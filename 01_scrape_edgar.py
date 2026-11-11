#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
01_scrape_edgar.py
==================

Stage 1 of a Regression Discontinuity Design (RDD) pipeline around the
SEC Rule 14a-8(i)(12) shareholder-proposal RESUBMISSION thresholds.

What it does
------------
1. Finds Form 8-K filings that report Item 5.07 ("Submission of Matters to a
   Vote of Security Holders") and mention a shareholder / stockholder proposal
   (EDGAR full-text search), or, alternatively, all Item 5.07 8-Ks for a list
   of tickers (EDGAR submissions API).
2. Downloads each primary 8-K document while respecting SEC fair-access rules
   (declared User-Agent, <= 9 requests/second, back-off on 403/429/5xx).
3. Isolates the Item 5.07 section and parses the vote tables with fuzzy header
   matching (For / Against / Abstain / Broker Non-Votes), handling horizontal
   tables, transposed tables, split header tables and plain-paragraph results.
4. Computes the RDD running variable exactly as Rule 14a-8(i)(12) does:
       vote_share = Votes_For / (Votes_For + Votes_Against)
   (abstentions and broker non-votes are excluded, per SEC Staff Legal
   Bulletin No. 14). It is computed from the raw counts, never from the
   rounded percentages some filers print, because 14.95% and 15.04% both
   print as "15.0%".
5. Links proposals on the same subject at the same firm over time to build:
     * vote_number_5y : how many times this subject was voted on in the
                        5-year look-back (decides whether the 5%, 15% or 25%
                        threshold applies),
     * refiled_t1     : whether a substantially similar proposal reached the
                        ballot again at the next annual meeting (outcome).
6. Pulls baseline (pre-vote) firm covariates from the SEC XBRL "companyfacts"
   API: log total assets, leverage (liabilities / assets), ROA.
7. If fewer than --min-obs (default 50) valid observations are collected, or
   EDGAR blocks / cannot be reached, it writes a clearly labelled SYNTHETIC
   dataset (generate_synthetic_rdd_data) instead, so downstream scripts
   still run. Synthetic rows carry data_source == "SYNTHETIC" and synthetic
   identifiers; they must never be used for inference.

Regulatory notes that shape the design (read before running the RDD)
--------------------------------------------------------------------
* The rule is 14a-8(i)(12). After the 2020 amendments, a company MAY exclude
  a proposal that is substantially the same as one voted on within the
  preceding 5 calendar years if its most recent vote got:
      < 5%  when voted on once,
      < 15% when voted on twice,
      < 25% when voted on three or more times.
  So the 15% cutoff only applies to proposals on their SECOND vote in five
  years. Use `in_15pct_sample == True`, or pool all three cutoffs with the
  normalised running variable `run_var = vote_share - applicable_threshold`.
* The comparison is strict: 14.99% is below the bar; exactly 15.00% passes.
  `below_threshold` uses `vote_share < applicable_threshold`.
* Crossing the bar does not trigger an automatic board rejection. It makes
  the proposal *excludable* for three years: the company must still choose to
  exclude it, and the proponent must choose to resubmit. Treatment take-up is
  therefore imperfect (a fuzzy RD); `refiled_t1` measures "back on the
  ballot", which is the joint outcome.
* The 5/15/25 thresholds govern meetings held on or after 1 January 2022, so
  votes from 2021 onward determine eligibility under the 15% bar. From the
  2025-26 proxy season, SEC staff largely stopped responding to 14a-8
  no-action requests, and in September 2026 the SEC proposed rescinding
  Rule 14a-8 altogether. Default window: 2021-01-01 .. 2024-12-31 votes,
  which keeps the t+1 outcome inside the period of normal staff review.

Usage
-----
    python 01_scrape_edgar.py --user-agent "Your Name your.email@uni.edu"
    python 01_scrape_edgar.py --start-date 2021-01-01 --end-date 2024-12-31 --max-filings 0
    python 01_scrape_edgar.py --tickers AAPL MSFT XOM --no-history
    python 01_scrape_edgar.py --force-synthetic           # skip EDGAR entirely
    python 01_scrape_edgar.py --self-test                 # offline parser tests

Outputs
-------
    rdd_data.csv                 cleaned dataset (standard columns first)
    rdd_data_live_partial.csv    live rows kept aside if fallback triggered
    scraping_log.txt             skipped / unparseable filings and errors
    edgar_cache/                 raw HTTP cache (delete to force refresh)

Dependencies: requests, beautifulsoup4, pandas, numpy (lxml optional; the
script falls back to Python's built-in html.parser).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import os
import re
import sys
import threading
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment, NavigableString, Tag

try:  # lxml is faster and more forgiving; html.parser is always available.
    import lxml  # noqa: F401

    HTML_PARSER = "lxml"
except ImportError:  # pragma: no cover
    HTML_PARSER = "html.parser"


# =============================================================================
# 0. CONFIGURATION
# =============================================================================

# SEC requires a User-Agent of the form "Company/Name contact@email". Without it
# EDGAR answers 403 Forbidden. Override with --user-agent or $SEC_USER_AGENT and
# use a real address you monitor; SEC may contact you before blocking an IP.
DEFAULT_USER_AGENT = os.environ.get("SEC_USER_AGENT", "ResearchGroup admin@research.edu")

MAX_REQUESTS_PER_SECOND = 9.0  # SEC hard limit is 10/s across ALL sec.gov hosts.

EFTS_URL = "https://efts.sec.gov/LATEST/search-index"  # full-text search (lowercase LATEST; the
# "LatestSearch/rest/search-index" variant returns 403 and would silently trigger the synthetic fallback)
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
SUBMISSIONS_PAGE_URL = "https://data.sec.gov/submissions/{name}"
COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc_nodash}/{doc}"

# Phrases used to locate 8-Ks that contain a shareholder proposal vote.
SEARCH_PHRASES = ["shareholder proposal", "stockholder proposal", "shareowner proposal"]

# Rule 14a-8(i)(12) thresholds (post-2020 amendments), keyed by the number of
# times the subject was voted on in the preceding 5 calendar years.
RESUBMISSION_THRESHOLDS = {1: 0.05, 2: 0.15, 3: 0.25}
FOCAL_CUTOFF = 0.15

# Windows used to link "the same proposal" across meetings at one firm.
MIN_GAP_DAYS = 180            # anything closer is the same meeting / season
NEXT_MEETING_MAX_DAYS = 550   # t+1 annual meeting must fall within ~18 months
LOOKBACK_DAYS = 5 * 365 + 2   # "preceding five calendar years" (approximation)
TOPIC_SIMILARITY_MIN = float(os.environ.get("TOPIC_SIM_MIN", "0.5"))
# Jaccard similarity on topic keywords. Overridable so the sensitivity of the
# threshold assignment to this choice can be measured without editing code.

# Output schema: the 12 standard columns first, then audit / design columns.
STANDARD_COLUMNS = [
    "cik", "ticker", "filing_date", "proposal_desc", "votes_for", "votes_against",
    "votes_abstain", "vote_share", "log_assets", "leverage", "roa", "refiled_t1",
]
EXTRA_COLUMNS = [
    "company_name", "broker_non_votes", "vote_number_5y", "applicable_threshold",
    "run_var", "below_threshold", "in_15pct_sample", "history_complete",
    "accession_no", "source_url", "parse_method", "data_source",
]

VOTE_CATS = ("votes_for", "votes_against", "votes_abstain", "broker_non_votes")

LOG_FILE = "scraping_log.txt"
CHECKPOINT_EVERY = 100          # dump parsed rows to disk every N filings (crash safety)
CHECKPOINT_FILE = "rdd_data.partial.csv"
log = logging.getLogger("edgar_rdd")


def setup_logging(log_path: str, verbose: bool = False) -> None:
    """Detailed log to file (overwritten each run); concise log to terminal."""
    log.setLevel(logging.DEBUG)
    log.handlers.clear()
    fh = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s"))
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)
    ch.setFormatter(logging.Formatter("%(levelname)-7s %(message)s"))
    log.addHandler(fh)
    log.addHandler(ch)


# =============================================================================
# 1. SEC EDGAR REQUEST & COMPLIANCE ENGINE
# =============================================================================

class EdgarRequestError(RuntimeError):
    """A single request failed after all retries."""


class EdgarBlockedError(RuntimeError):
    """EDGAR is refusing us (403/429) or unreachable; abort live scraping."""


class RateLimiter:
    """Thread-safe limiter that spaces requests at least 1/max_rps seconds apart.

    One shared instance covers www.sec.gov, efts.sec.gov and data.sec.gov,
    because SEC applies its limit per client, not per host.
    """

    def __init__(self, max_per_second: float = MAX_REQUESTS_PER_SECOND):
        self.min_interval = 1.0 / max_per_second
        self._lock = threading.Lock()
        self._next_allowed = 0.0

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            if now < self._next_allowed:
                time.sleep(self._next_allowed - now)
                now = time.monotonic()
            self._next_allowed = now + self.min_interval


class EdgarClient:
    """requests.Session wrapper: SEC headers, rate limit, retries, disk cache."""

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        max_rps: float = MAX_REQUESTS_PER_SECOND,
        cache_dir: Optional[str] = "edgar_cache",
        timeout: float = 30.0,
        max_retries: int = 3,
        max_consecutive_failures: int = 3,
    ):
        if "@" not in user_agent:
            raise ValueError("SEC User-Agent must contain a contact e-mail, e.g. 'Name you@uni.edu'.")
        if user_agent == "ResearchGroup admin@research.edu":
            log.warning("Using the placeholder User-Agent. Pass --user-agent 'Your Name you@uni.edu' "
                        "(SEC asks for a real, monitored contact address).")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,                 # mandatory, prevents 403
            "Accept-Encoding": "gzip, deflate",       # requested by SEC
            "Accept": "application/json, text/html, */*",
        })
        self.limiter = RateLimiter(max_rps)
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_consecutive_failures = max_consecutive_failures
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._consecutive_failures = 0
        self.n_http_requests = 0
        self.n_cache_hits = 0

    # -- cache helpers ---------------------------------------------------------
    def _cache_path(self, url: str, params: Optional[dict]) -> Optional[Path]:
        if not self.cache_dir:
            return None
        key = url + "?" + json.dumps(params or {}, sort_keys=True)
        return self.cache_dir / (hashlib.sha1(key.encode()).hexdigest() + ".cache")

    # -- core GET --------------------------------------------------------------
    def get_text(self, url: str, params: Optional[dict] = None, use_cache: bool = True) -> str:
        cpath = self._cache_path(url, params) if use_cache else None
        if cpath and cpath.exists():
            self.n_cache_hits += 1
            return cpath.read_text(encoding="utf-8", errors="replace")

        last_err: Any = None
        for attempt in range(self.max_retries + 1):
            self.limiter.wait()
            self.n_http_requests += 1
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
            except requests.RequestException as exc:      # DNS, proxy, timeout ...
                last_err = exc
                time.sleep(min(2 ** attempt, 30))
                continue

            if resp.status_code == 200:
                self._consecutive_failures = 0
                text = resp.text
                if cpath:
                    cpath.write_text(text, encoding="utf-8")
                return text
            if resp.status_code == 404:
                self._consecutive_failures = 0
                raise EdgarRequestError(f"404 Not Found: {url}")
            last_err = f"HTTP {resp.status_code}"
            if resp.status_code in (403, 429):
                # 403 = missing/blocked User-Agent or IP; 429 = too many requests.
                # Honour Retry-After when present, otherwise back off exponentially.
                retry_after = resp.headers.get("Retry-After")
                wait = float(retry_after) if retry_after and retry_after.isdigit() else min(5 * 2 ** attempt, 60)
                log.warning("EDGAR returned %s for %s; sleeping %.0fs", resp.status_code, url, wait)
                time.sleep(wait)
                continue
            if 500 <= resp.status_code < 600:
                time.sleep(min(2 ** attempt, 30))
                continue
            break  # other 4xx: do not retry

        self._consecutive_failures += 1
        if self._consecutive_failures >= self.max_consecutive_failures:
            raise EdgarBlockedError(
                f"{self._consecutive_failures} consecutive failed requests "
                f"(last: {last_err}); EDGAR appears blocked or unreachable.")
        raise EdgarRequestError(f"GET failed for {url}: {last_err}")

    def get_json(self, url: str, params: Optional[dict] = None, use_cache: bool = True) -> Any:
        return json.loads(self.get_text(url, params=params, use_cache=use_cache))


# =============================================================================
# 1b. FILING DISCOVERY
# =============================================================================

@dataclass
class FilingRef:
    cik: str            # 10-digit, zero-padded
    company_name: str
    ticker: str
    filing_date: str    # YYYY-MM-DD
    accession_no: str   # 0000000000-YY-NNNNNN
    primary_doc: str

    @property
    def url(self) -> str:
        return ARCHIVE_URL.format(cik=int(self.cik), acc_nodash=self.accession_no.replace("-", ""),
                                  doc=self.primary_doc)


def load_ticker_map(client: EdgarClient) -> dict[str, tuple[str, str]]:
    """CIK (10-digit) -> (ticker, company title), from SEC's company_tickers.json."""
    try:
        data = client.get_json(TICKERS_URL)
    except EdgarRequestError as exc:
        log.warning("Could not load ticker map (%s); tickers will come from search results.", exc)
        return {}
    out: dict[str, tuple[str, str]] = {}
    for row in data.values():
        cik = f"{int(row['cik_str']):010d}"
        out.setdefault(cik, (row["ticker"], row["title"]))   # first listed = primary class
    return out


_DISPLAY_RE = re.compile(r"^(?P<name>.*?)\s*(?:\((?P<tick>[A-Z0-9.\-]+(?:,\s*[A-Z0-9.\-]+)*)\))?\s*\(CIK\s*\d+\)")


def _year_slices(start: date, end: date) -> list[tuple[date, date]]:
    """Split a date range into calendar-year chunks (EFTS caps a query at 10k hits)."""
    slices, cur = [], start
    while cur <= end:
        stop = min(date(cur.year, 12, 31), end)
        slices.append((cur, stop))
        cur = stop + timedelta(days=1)
    return slices


def discover_via_fulltext(client: EdgarClient, start: date, end: date, max_filings: int,
                          ticker_map: dict[str, tuple[str, str]]) -> list[FilingRef]:
    """EDGAR full-text search: 8-Ks with Item 5.07 that mention a shareholder proposal."""
    slices = _year_slices(start, end)
    per_slice = math.ceil(max_filings / len(slices)) if max_filings > 0 else None
    refs: dict[str, FilingRef] = {}

    for s, e in slices:
        n_slice = 0
        for phrase in SEARCH_PHRASES:
            offset = 0
            while True:
                params = {"q": f'"{phrase}"', "forms": "8-K", "dateRange": "custom",
                          "startdt": s.isoformat(), "enddt": e.isoformat(), "from": offset}
                try:
                    data = client.get_json(EFTS_URL, params=params)
                except EdgarRequestError as exc:
                    log.error("Full-text search failed (%s, %s..%s, from=%d): %s", phrase, s, e, offset, exc)
                    break
                hits = data.get("hits", {}).get("hits", [])
                if not hits:
                    break
                for h in hits:
                    src = h.get("_source", {})
                    if src.get("form") != "8-K" or "5.07" not in (src.get("items") or []):
                        continue
                    ftype = (src.get("file_type") or "8-K").upper()
                    if not ftype.startswith("8-K"):        # skip exhibit hits (EX-99 etc.)
                        continue
                    hid = h.get("_id", "")
                    adsh = src.get("adsh") or hid.split(":")[0]
                    if not adsh or adsh in refs or ":" not in hid:
                        continue
                    cik = f"{int((src.get('ciks') or ['0'])[0]):010d}"
                    m = _DISPLAY_RE.match((src.get("display_names") or [""])[0])
                    name = m.group("name").strip() if m else ""
                    tick = (m.group("tick") or "").split(",")[0].strip() if m else ""
                    if cik in ticker_map:
                        tick = tick or ticker_map[cik][0]
                        name = name or ticker_map[cik][1]
                    refs[adsh] = FilingRef(cik, name, tick, src.get("file_date", ""), adsh, hid.split(":", 1)[1])
                    n_slice += 1
                    if per_slice and n_slice >= per_slice:
                        break
                if per_slice and n_slice >= per_slice:
                    break
                offset += len(hits)
                total = data.get("hits", {}).get("total", {}).get("value", 0)
                if offset >= min(total, 10_000):
                    break
            if per_slice and n_slice >= per_slice:
                break
        log.info("Discovery %s..%s: %d Item 5.07 filings", s, e, n_slice)
    return list(refs.values())


def discover_via_tickers(client: EdgarClient, tickers: list[str], start: date, end: date,
                         max_filings: int, ticker_map: dict[str, tuple[str, str]]) -> list[FilingRef]:
    """Submissions API: every 8-K with Item 5.07 for the given tickers."""
    rev = {t.upper(): (cik, title) for cik, (t, title) in ticker_map.items()}
    refs: list[FilingRef] = []
    for t in tickers:
        if t.upper() not in rev:
            log.warning("Ticker %s not found in SEC ticker map; skipped.", t)
            continue
        cik, title = rev[t.upper()]
        try:
            sub = client.get_json(SUBMISSIONS_URL.format(cik=int(cik)), use_cache=False)
        except EdgarRequestError as exc:
            log.error("Submissions fetch failed for %s: %s", t, exc)
            continue
        blocks = [sub.get("filings", {}).get("recent", {})]
        for f in sub.get("filings", {}).get("files", []):          # older filings are paged
            if f.get("filingTo", "9999") >= start.isoformat():
                try:
                    blocks.append(client.get_json(SUBMISSIONS_PAGE_URL.format(name=f["name"])))
                except EdgarRequestError as exc:
                    log.warning("Older submissions page failed for %s: %s", t, exc)
        for blk in blocks:
            for i, form in enumerate(blk.get("form", [])):
                fdate = blk["filingDate"][i]
                items = (blk.get("items", [""] * (i + 1))[i] or "").split(",")
                if form == "8-K" and "5.07" in items and start.isoformat() <= fdate <= end.isoformat():
                    refs.append(FilingRef(cik, title, t.upper(), fdate, blk["accessionNumber"][i],
                                          blk["primaryDocument"][i]))
    refs.sort(key=lambda r: r.filing_date)
    return refs[:max_filings] if max_filings > 0 else refs


# =============================================================================
# 2. HTML PARSING & VARIABLE NORMALISATION
# =============================================================================

def _clean(s: str) -> str:
    """Normalise whitespace, non-breaking spaces and zero-width characters."""
    s = s.replace("\xa0", " ").replace("​", "").replace("﻿", "")
    return re.sub(r"\s+", " ", s).strip()


FOOTNOTE_RE = re.compile(r"\(\s*[a-z0-9]{1,2}\s*\)|[\*†‡§]+", re.I)
DASHES = {"-", "--", "—", "–", "——", "n/a", "na", "n.a.", "none", "nil", "*"}

# Fuzzy header mapping. Order matters: the more specific categories are tested
# first so "Votes Against" never falls through to the "for" rule.
_PREFIX = r"^(?:number\s+of\s+|total\s+)?(?:(?:shares|votes?)\s+)?(?:(?:cast|voted)\s+)?"
HEADER_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("broker_non_votes", re.compile(r"broker[\s\-]*non[\s\-]*votes?|^non[\s\-]*votes?$|^broker\s+non|unvoted|not\s+voted|^bnvs?$")),
    ("votes_abstain", re.compile(_PREFIX + r"(?:abstain(?:ed|ing|s)?|abstentions?)(?:\s+votes?)?$")),
    ("votes_against", re.compile(_PREFIX + r"(?:against|opposed|no|withh[eo]ld(?:ing)?)(?:\s+votes?)?$")),
    ("votes_for", re.compile(_PREFIX + r"(?:for|in\s+favou?r(?:\s+of)?|yes|affirmative)(?:\s+votes?)?$")),
]


def classify_header(cell: str) -> Optional[str]:
    """Map a header cell to a vote category, 'pct' (a percentage column) or None.

    'Withheld' is mapped to votes_against; it only appears in director
    elections, which are dropped later because they are not shareholder proposals.
    """
    t = FOOTNOTE_RE.sub("", _clean(cell).lower())
    t = re.sub(r"\(\s*(?:#|no\.|shares)\s*\)", "", t)
    t = re.sub(r"[\s:.\-–—#]+$", "", t).strip()
    if not t or len(t) > 40:
        return None
    if "%" in t or "percent" in t:
        return "pct"
    for cat, rx in HEADER_PATTERNS:
        if rx.search(t):
            return cat
    return None


_NUM_RE = re.compile(r"(\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?")


def parse_number(cell: str) -> tuple[Optional[str], Optional[float]]:
    """Classify a cell as ('num', value), ('pct', value), ('dash', None) or (None, None)."""
    t = FOOTNOTE_RE.sub("", _clean(cell)).strip().strip("$").strip()
    if t.lower() in DASHES:
        return "dash", None
    m = re.fullmatch(r"\(?\s*((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*%\s*\)?", t)
    if m:
        return "pct", float(m.group(1).replace(",", ""))
    if _NUM_RE.fullmatch(t):
        return "num", float(t.replace(",", ""))
    m = re.fullmatch(r"((?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*\(\s*\d+(?:\.\d+)?\s*%\s*\)", t)
    if m:                                     # "12,345,678 (95.1%)"
        return "num", float(m.group(1).replace(",", ""))
    return None, None


SP_RE = re.compile(
    r"\b(?:share|stock)\s*(?:holder|owner)s?['’]?s?\s+proposals?\b"
    r"|\bproposals?\s+(?:submitted|presented|made|sponsored)\s+by\s+(?:a\s+|certain\s+)?(?:share|stock)(?:holder|owner)s?"
    r"|\bproponents?\b",
    re.I,
)
ITEM_507_RE = re.compile(r"item\s*5\s*\.\s*07", re.I)
SECTION_END_RE = re.compile(r"^\s*(?:item\s*(?!5\s*\.\s*07)\d{1,2}\s*\.\s*\d{2}\b|signatures?\b|exhibit\s+index\b)", re.I)


def iter_blocks(node: Tag):
    """Yield ('text', str) and ('table', Tag) in document order.

    A tag that contains no table is emitted as one text block. A tag that does
    contain a table is descended into, so text before/after the table keeps its
    position. This survives the deeply nested <div>/<font> soup many filing
    agents produce.
    """
    for child in node.children:
        if isinstance(child, Comment):
            continue
        if isinstance(child, NavigableString):
            txt = _clean(str(child))
            if txt:
                yield "text", txt
            continue
        if not isinstance(child, Tag) or child.name in ("script", "style", "head", "title"):
            continue
        if child.name == "table":
            yield "table", child
        elif child.find("table") is not None:
            yield from iter_blocks(child)
        else:
            txt = _clean(child.get_text(" ", strip=True))
            if txt:
                yield "text", txt


def table_rows(table: Tag) -> list[list[str]]:
    """Return non-empty cell texts per row; glue stray '%' / ')' cells, drop '$' cells."""
    rows = []
    for tr in table.find_all("tr"):
        merged: list[str] = []
        for td in tr.find_all(["td", "th"], recursive=False):
            c = _clean(td.get_text(" ", strip=True))
            if not c or c == "$":
                continue
            if c in {"%", ")", "%)"} and merged:
                merged[-1] += c
                continue
            merged.append(c)
        if merged:
            rows.append(merged)
    return rows


def _context_description(context: list[str]) -> str:
    """Pick the most recent preceding paragraph that names a proposal."""
    for txt in reversed(context):
        if re.search(r"proposal", txt, re.I) and len(txt) > 15:
            return txt[:400]
    return context[-1][:400] if context else ""


def _make_obs(desc_row: str, context: list[str], values: dict, method: str) -> dict:
    ctx = _context_description(context)
    desc_row = _clean(desc_row)
    if len(desc_row.split()) >= 4:
        desc = desc_row
    elif desc_row:                       # e.g. "Proposal 5" -> enrich with paragraph
        desc = f"{desc_row} | {ctx}" if ctx else desc_row
    else:
        desc = ctx
    return {
        "proposal_desc": desc[:400],
        "votes_for": values.get("votes_for"),
        "votes_against": values.get("votes_against"),
        "votes_abstain": values.get("votes_abstain"),
        "broker_non_votes": values.get("broker_non_votes"),
        "is_shareholder_proposal": bool(SP_RE.search(desc)),
        "parse_method": method,
    }


def _header_cats(row: list[str]) -> Optional[list[str]]:
    """If the row is a vote-table header, return its numeric-column categories."""
    cats = [classify_header(c) for c in row]
    vote = {c for c in cats if c in VOTE_CATS}
    if "votes_for" in vote and "votes_against" in vote:
        return [c for c in cats if c in VOTE_CATS or c == "pct"]
    return None


def _align(header: list[str], tokens: list[tuple[str, Optional[float]]]) -> Optional[dict]:
    """Match numeric tokens of a data row to header categories, tolerating
    percentage columns, leading row numbers and a blank trailing BNV cell."""
    def attempt(h, t):
        if len(h) != len(t):
            return None
        out = {}
        for cat, (kind, val) in zip(h, t):
            if cat == "pct":
                continue
            if kind == "pct":
                return None
            out[cat] = val
        return out

    res = attempt(header, tokens)
    if res is not None:
        return res
    h2 = [c for c in header if c != "pct"]
    t2 = [x for x in tokens if x[0] != "pct"]
    while len(t2) > len(h2) and t2 and t2[0][0] == "num" and (t2[0][1] or 0) < 1000:
        t2 = t2[1:]                                   # drop "1", "2" row numbers
    res = attempt(h2, t2)
    if res is not None:
        return res
    if len(t2) == len(h2) - 1 and h2 and h2[-1] in ("broker_non_votes", "votes_abstain"):
        return attempt(h2, t2 + [("dash", None)])     # trailing cell left blank
    return None


def parse_vote_table(rows: list[list[str]], context: list[str],
                     carry_header: Optional[list[str]] = None) -> tuple[list[dict], Optional[list[str]]]:
    """Parse one table. Returns (observations, last header seen)."""
    obs: list[dict] = []
    has_header = any(_header_cats(r) for r in rows)

    # --- Layout A: transposed (labels down the first column) -----------------
    if not has_header:
        cat_rows: dict[str, list[Optional[float]]] = {}
        names_row: Optional[list[str]] = None
        for r in rows:
            cat = classify_header(r[0])
            if cat in VOTE_CATS:
                vals = [v for k, v in (parse_number(c) for c in r[1:]) if k in ("num", "dash")]
                if vals and cat not in cat_rows:
                    cat_rows[cat] = vals
            elif not cat_rows and all(parse_number(c)[0] is None for c in r):
                names_row = r            # possible column titles above the labels
        if "votes_for" in cat_rows and "votes_against" in cat_rows:
            k = len(cat_rows["votes_for"])
            if names_row and len(names_row) == k + 1:
                names_row = names_row[1:]
            for j in range(k):
                vals = {c: (v[j] if j < len(v) else None) for c, v in cat_rows.items()}
                desc = names_row[j] if names_row and len(names_row) == k else ""
                obs.append(_make_obs(desc, context, vals, "table_transposed"))
            return obs, carry_header

    # --- Layout B: horizontal (header row + one data row per proposal) -------
    header = None if has_header else carry_header
    for r in rows:
        hc = _header_cats(r)
        if hc:
            header = hc
            continue
        if header is None:
            continue
        tokens, text_cells = [], []
        for c in r:
            kind, val = parse_number(c)
            if kind is not None:
                tokens.append((kind, val))
            else:
                text_cells.append(c)          # description cell(s), wherever they sit
        if sum(1 for k, _ in tokens if k == "num") < 2:
            continue
        values = _align(header, tokens)
        if values is None:
            raise ValueError(f"column mismatch: header={header} row={r}")
        obs.append(_make_obs(" ".join(text_cells), context, values,
                             "table" if has_header else "table_carried_header"))
    return obs, header


_P_NUM = r"(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d{4,}(?:\.\d+)?)"
_P_LABEL = (r"(?P<label>votes?\s+(?:cast\s+)?for|for|in\s+favou?r|against|abstain(?:ed|ing|s)?"
            r"|abstentions?|broker[\s\-]+non[\s\-]*votes?)")
NUM_FIRST_RE = re.compile(_P_NUM + r"\s+(?:shares\s+|votes\s+)?(?:were\s+)?(?:voted\s+|cast\s+)?" + _P_LABEL + r"\b", re.I)
LABEL_FIRST_RE = re.compile(_P_LABEL + r"\s*(?:[:=\-–—]|was|were|of)?\s*" + _P_NUM, re.I)


def _label_cat(label: str) -> str:
    lab = label.lower()
    if "broker" in lab:
        return "broker_non_votes"
    if "abst" in lab:
        return "votes_abstain"
    if "against" in lab:
        return "votes_against"
    return "votes_for"


def parse_vote_paragraphs(section_text: str) -> list[dict]:
    """Fallback for results written as prose, e.g. 'The proposal received
    12,345,678 votes for, 45,678,901 votes against and 1,234 abstentions.'"""
    obs = []
    chunks = re.split(r"(?=\bproposal\s*(?:no\.?\s*)?\d{1,2}\b)", section_text, flags=re.I)
    for chunk in chunks:
        if not SP_RE.search(chunk):
            continue
        for rx in (NUM_FIRST_RE, LABEL_FIRST_RE):
            found: dict[str, float] = {}
            for m in rx.finditer(chunk):
                cat = _label_cat(m.group("label"))
                found.setdefault(cat, float(m.group("num").replace(",", "")))
            if "votes_for" in found and "votes_against" in found:
                first_sentence = re.split(r"(?<=[.;])\s", chunk.strip(), maxsplit=1)[0]
                obs.append({
                    "proposal_desc": _clean(first_sentence)[:400],
                    "votes_for": found.get("votes_for"),
                    "votes_against": found.get("votes_against"),
                    "votes_abstain": found.get("votes_abstain"),
                    "broker_non_votes": found.get("broker_non_votes"),
                    "is_shareholder_proposal": True,
                    "parse_method": "paragraph",
                })
                break
    return obs


def parse_item_507(html: str) -> tuple[list[dict], dict]:
    """Extract every proposal vote reported under Item 5.07 of one 8-K.

    Returns (observations, diagnostics). Each table is parsed inside its own
    try/except so a single malformed table never kills the filing.
    """
    soup = BeautifulSoup(html, HTML_PARSER)
    root = soup.body or soup
    diag = {"marker_found": False, "n_tables": 0, "table_errors": 0}

    in_section, done = False, False
    context: list[str] = []
    section_tables: list[tuple[Tag, list[str]]] = []
    all_tables: list[tuple[Tag, list[str]]] = []
    ctx_all: list[str] = []

    for kind, payload in iter_blocks(root):
        if kind == "text":
            ctx_all = (ctx_all + [payload])[-3:]
            if not in_section and not done and ITEM_507_RE.search(payload):
                in_section, diag["marker_found"] = True, True
                context = [payload]
            elif in_section and SECTION_END_RE.match(payload):
                in_section, done = False, True
            elif in_section:
                context = (context + [payload])[-3:]
            continue
        # table block
        all_tables.append((payload, list(ctx_all)))
        ctx_all = []
        ttxt = _clean(payload.get_text(" ", strip=True))
        if not in_section and not done and len(ttxt) < 300 and ITEM_507_RE.search(ttxt):
            in_section, diag["marker_found"] = True, True     # heading set inside a layout table
            context = [ttxt]
            continue
        if in_section and len(ttxt) < 300 and SECTION_END_RE.match(ttxt):
            in_section, done = False, True
            continue
        if in_section:
            section_tables.append((payload, list(context)))
            context = []

    tables = section_tables if diag["marker_found"] else all_tables
    diag["n_tables"] = len(tables)

    obs: list[dict] = []
    carry: Optional[list[str]] = None
    last_ctx: list[str] = []
    for tbl, ctx in tables:
        ctx = ctx or last_ctx          # header-only table followed by a numbers-only table
        last_ctx = ctx
        try:
            rows = table_rows(tbl)
            if not rows:
                continue
            found, carry = parse_vote_table(rows, ctx, carry)
            obs.extend(found)
        except Exception as exc:          # malformed table: log and keep going
            diag["table_errors"] += 1
            log.debug("Table parse error: %s", exc)

    # Prose fallback when tables yield no shareholder-proposal votes.
    if not any(o["is_shareholder_proposal"] for o in obs):
        full = _clean(soup.get_text(" "))
        m = ITEM_507_RE.search(full)
        section = full[m.start():] if m else full
        end = re.search(r"\bitem\s*(?!5\s*\.\s*07)\d{1,2}\s*\.\s*\d{2}\b|\bSIGNATURES?\b", section[20:])
        section = section[: end.start() + 20] if end else section
        try:
            obs.extend(parse_vote_paragraphs(section))
        except Exception as exc:
            log.debug("Paragraph parse error: %s", exc)
    return obs, diag


def compute_vote_share(votes_for: Any, votes_against: Any) -> float:
    """Rule 14a-8(i)(12) support: For / (For + Against). NaN if undefined."""
    try:
        f, a = float(votes_for), float(votes_against)
    except (TypeError, ValueError):
        return float("nan")
    if not (np.isfinite(f) and np.isfinite(a)) or f < 0 or a < 0 or f + a <= 0:
        return float("nan")
    return f / (f + a)


# =============================================================================
# 2b. RESUBMISSION HISTORY & OUTCOME (vote_number_5y, refiled_t1)
# =============================================================================

# Words carrying no topical signal, in two families:
#   1. structural  -- proposal vocabulary present in nearly every description
#   2. vote-result -- 8-K reporting language that leaks into proposal_desc when a
#      table cell is captured with its surrounding sentence, e.g.
#      "...was not approved as follows:". Left in, these words make unrelated
#      proposals look similar and inflate the apparent resubmission history.
# Content words such as "report" and "policy" are deliberately NOT stripped:
# they distinguish what is being asked for ("report on X" vs "adopt a policy on
# X"), and removing them was found to raise false-positive matches.
_TOPIC_STOP = set("""
a an the of on to for and or in by with from at as be is are its our their this that these
regarding requesting request requests relating related concerning re shareholder shareholders
stockholder stockholders shareowner shareowners proposal proposals vote voting votes voted
approve approval approved adopt adoption company companys item no non binding advisory
submitted presented entitled board directors
were was been being below above described description statement proxy follows following
based upon table set forth pursuant hereby further including include includes commission
sec annual meeting meetings cast record date abstain abstentions abstained brokers broker
against""".split())


def topic_tokens(desc: str) -> frozenset:
    """Content keywords of a proposal description, for 'substantially the same' matching."""
    return frozenset(w for w in re.findall(r"[a-z]{3,}", str(desc).lower()) if w not in _TOPIC_STOP)


def topic_similarity(a: frozenset, b: frozenset) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def add_resubmission_variables(df: pd.DataFrame, data_start: date, data_end: date) -> pd.DataFrame:
    """Link same-subject proposals at the same firm across meetings.

    vote_number_5y : 1 + prior votes on a similar subject within ~5 years.
    refiled_t1     : 1 if a similar proposal is voted on 6-18 months later,
                     0 if not, NaN if the t+1 window runs past the data end
                     (right-censored).
    history_complete : False if the 5-year look-back starts before the data
                     start, so vote_number_5y may be undercounted.

    Keyword matching is only an approximation of the SEC's "substantially the
    same subject matter" test; hand-check proposals near the cutoff.
    """
    df = df.copy()
    df["_date"] = pd.to_datetime(df["filing_date"])
    df["_tok"] = df["proposal_desc"].map(topic_tokens)
    df["vote_number_5y"] = 1
    df["refiled_t1"] = np.nan
    df["history_complete"] = False
    ts_start, ts_end = pd.Timestamp(data_start), pd.Timestamp(data_end)

    for _, g in df.groupby("cik"):
        for i in g.index:
            d, tok = df.at[i, "_date"], df.at[i, "_tok"]
            prior = g[(g["_date"] <= d - pd.Timedelta(days=MIN_GAP_DAYS)) &
                      (g["_date"] >= d - pd.Timedelta(days=LOOKBACK_DAYS))]
            n_prior = sum(topic_similarity(tok, t) >= TOPIC_SIMILARITY_MIN for t in prior["_tok"])
            df.at[i, "vote_number_5y"] = 1 + int(n_prior)
            df.at[i, "history_complete"] = bool(d - pd.Timedelta(days=LOOKBACK_DAYS) >= ts_start)
            nxt = g[(g["_date"] >= d + pd.Timedelta(days=MIN_GAP_DAYS)) &
                    (g["_date"] <= d + pd.Timedelta(days=NEXT_MEETING_MAX_DAYS))]
            if any(topic_similarity(tok, t) >= TOPIC_SIMILARITY_MIN for t in nxt["_tok"]):
                df.at[i, "refiled_t1"] = 1.0
            elif d + pd.Timedelta(days=NEXT_MEETING_MAX_DAYS) <= ts_end:
                df.at[i, "refiled_t1"] = 0.0
    return df.drop(columns=["_date", "_tok"])


def add_threshold_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Applicable (i)(12) threshold, normalised running variable, treatment side."""
    df = df.copy()
    n = df["vote_number_5y"].clip(lower=1, upper=3).astype(int)
    df["applicable_threshold"] = n.map(RESUBMISSION_THRESHOLDS)
    df["run_var"] = df["vote_share"] - df["applicable_threshold"]
    df["below_threshold"] = df["vote_share"] < df["applicable_threshold"]   # strict: 14.99% excludable, 15.00% not
    df["in_15pct_sample"] = df["vote_number_5y"] == 2
    return df


# =============================================================================
# 2c. BASELINE FIRM COVARIATES (SEC XBRL companyfacts)
# =============================================================================

ANNUAL_FORMS = {"10-K", "10-K/A", "10-KT", "20-F", "40-F"}


class CovariateFetcher:
    """log_assets, leverage, ROA from the latest annual report filed BEFORE the vote."""

    def __init__(self, client: EdgarClient):
        self.client = client
        self._facts: dict[str, Optional[dict]] = {}

    def _company_facts(self, cik: str) -> Optional[dict]:
        if cik not in self._facts:
            try:
                self._facts[cik] = self.client.get_json(COMPANYFACTS_URL.format(cik=int(cik)))
            except EdgarRequestError as exc:
                log.info("No XBRL company facts for CIK %s: %s", cik, exc)
                self._facts[cik] = None
        return self._facts[cik]

    @staticmethod
    def _latest(facts: dict, tags: list[str], asof: str, duration: bool) -> Optional[tuple[str, float]]:
        gaap = facts.get("facts", {}).get("us-gaap", {})
        for tag in tags:
            entries = gaap.get(tag, {}).get("units", {}).get("USD", [])
            best = None
            for e in entries:
                if e.get("form") not in ANNUAL_FORMS or e.get("filed", "9999") >= asof:
                    continue
                if duration:
                    if "start" not in e:
                        continue
                    span = (datetime.fromisoformat(e["end"]) - datetime.fromisoformat(e["start"])).days
                    if not 300 <= span <= 380:
                        continue
                elif "start" in e:
                    continue
                key = (e["end"], e.get("filed", ""))
                if best is None or key > best[0]:
                    best = (key, float(e["val"]))
            if best:
                return best[0][0], best[1]
        return None

    def get(self, cik: str, asof: str) -> dict:
        out = {"log_assets": np.nan, "leverage": np.nan, "roa": np.nan}
        facts = self._company_facts(cik)
        if not facts:
            return out
        try:
            assets = self._latest(facts, ["Assets"], asof, duration=False)
            if not assets or assets[1] <= 0:
                return out
            a_end, a_val = assets
            out["log_assets"] = math.log(a_val)
            liab = self._latest(facts, ["Liabilities"], asof, duration=False)
            if liab is None:   # many filers only tag L&SE and equity
                le = self._latest(facts, ["LiabilitiesAndStockholdersEquity"], asof, duration=False)
                eq = self._latest(facts, ["StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
                                          "StockholdersEquity"], asof, duration=False)
                if le and eq and le[0] == eq[0]:
                    liab = (le[0], le[1] - eq[1])
            if liab:
                out["leverage"] = liab[1] / a_val
            ni = self._latest(facts, ["NetIncomeLoss", "ProfitLoss"], asof, duration=True)
            if ni:
                out["roa"] = ni[1] / a_val
        except Exception as exc:
            log.info("Covariate computation failed for CIK %s: %s", cik, exc)
        return out


# =============================================================================
# 4. SYNTHETIC DATA FALLBACK
# =============================================================================

PROPOSAL_TOPICS = [
    "independent board chair", "report on political contributions", "report on lobbying expenditures",
    "right to act by written consent", "reduce special meeting ownership threshold",
    "simple majority vote", "climate transition plan", "greenhouse gas emissions targets",
    "racial equity audit", "gender pay gap report", "human rights impact assessment",
    "executive compensation clawback", "shareholder approval of severance packages",
    "report on plastic packaging", "child labor in supply chain", "deforestation risk report",
]


def generate_synthetic_rdd_data(n: int = 200, seed: int = 42, cutoff: float = FOCAL_CUTOFF,
                                true_effect_logit: float = 1.8) -> pd.DataFrame:
    """Mock shareholder-proposal votes centred on the 15% resubmission cutoff.

    Data-generating process (documented so the RDD stage can be validated):
      * vote_share ~ N(0.15, 0.06), clipped to [0.01, 0.60]; smooth density
        through the cutoff (no manipulation).
      * Covariates are smooth in vote_share (no jump), so balance tests pass:
          log_assets ~ N(22.5, 1.6) + 2*(v - 0.15)     (ln of total assets, USD)
          leverage   ~ Beta(2.5, 3.5)
          roa        ~ N(0.045, 0.06), clipped to [-0.30, 0.30]
      * refiled_t1 ~ Bernoulli(logistic(-1.2 + 3*(v - c) + 0.15*(log_assets - 22.5)
                                         + true_effect_logit * 1[v >= c]))
        i.e. P(back on ballot) jumps from ~0.23 to ~0.65 at the cutoff.
      * Vote counts are integers; vote_share is recomputed from them.
    All identifiers are fake (CIK 'SYN...', ticker 'SYNnnn').
    """
    rng = np.random.default_rng(seed)
    v = np.clip(rng.normal(cutoff, 0.06, n), 0.01, 0.60)

    total = np.round(np.exp(rng.normal(19.5, 1.0, n))).astype(np.int64)      # For + Against
    votes_for = np.round(v * total).astype(np.int64)
    votes_against = total - votes_for
    votes_abstain = np.round(total * rng.uniform(0.005, 0.03, n)).astype(np.int64)
    bnv = np.round(total * rng.uniform(0.04, 0.15, n)).astype(np.int64)
    share = votes_for / (votes_for + votes_against)

    log_assets = rng.normal(22.5, 1.6, n) + 2.0 * (share - cutoff)
    leverage = rng.beta(2.5, 3.5, n)
    roa = np.clip(rng.normal(0.045, 0.06, n), -0.30, 0.30)

    above = (share >= cutoff).astype(float)
    logit = -1.2 + 3.0 * (share - cutoff) + 0.15 * (log_assets - 22.5) + true_effect_logit * above
    refiled = rng.binomial(1, 1.0 / (1.0 + np.exp(-logit)))

    start = pd.Timestamp("2021-04-01")
    dates = [(start + pd.DateOffset(years=int(y)) + pd.Timedelta(days=int(d))).strftime("%Y-%m-%d")
             for y, d in zip(rng.integers(0, 4, n), rng.integers(0, 75, n))]
    topics = rng.choice(PROPOSAL_TOPICS, n)

    df = pd.DataFrame({
        "cik": [f"SYN{i:07d}" for i in range(1, n + 1)],
        "ticker": [f"SYN{i:03d}" for i in range(1, n + 1)],
        "filing_date": dates,
        "proposal_desc": [f"Shareholder proposal regarding {t}" for t in topics],
        "votes_for": votes_for, "votes_against": votes_against, "votes_abstain": votes_abstain,
        "vote_share": share, "log_assets": log_assets, "leverage": leverage, "roa": roa,
        "refiled_t1": refiled,
        "company_name": [f"Synthetic Corp {i:03d}" for i in range(1, n + 1)],
        "broker_non_votes": bnv,
        "vote_number_5y": 2,                       # all on their 2nd vote -> 15% bar applies
        "history_complete": True,
        "accession_no": "", "source_url": "", "parse_method": "synthetic",
        "data_source": "SYNTHETIC",
    })
    df = add_threshold_variables(df)
    log.info("Synthetic DGP: true jump in logit(P(refiled_t1)) at %.1f%% = %.2f", cutoff * 100, true_effect_logit)
    return df.sort_values("filing_date").reset_index(drop=True)


# =============================================================================
# 3 + 5. PIPELINE, ERROR HANDLING, OUTPUT
# =============================================================================

def _write_checkpoint(rows: list[dict], args, k: int, total: int) -> None:
    """Dump rows parsed so far to CHECKPOINT_FILE so a crash never loses the run.

    Deliberately swallows its own errors: a failed checkpoint write must never
    kill a long unattended scrape. The file is overwritten each time (not
    appended) because `rows` already holds the full history.
    """
    try:
        if not rows:
            return
        pd.DataFrame(rows).to_csv(CHECKPOINT_FILE, index=False)
        log.info("  checkpoint: %d rows from %d/%d filings -> %s",
                 len(rows), k, total, CHECKPOINT_FILE)
    except Exception as exc:                     # disk full, permissions, ...
        log.warning("  checkpoint write failed (continuing): %s", exc)


def scrape_live(args, stats: dict) -> pd.DataFrame:
    """Run discovery -> download -> parse -> link -> covariates. Raises EdgarBlockedError."""
    client = EdgarClient(args.user_agent, cache_dir=None if args.no_cache else args.cache_dir)
    stats["client"] = client

    analysis_start = date.fromisoformat(args.start_date)
    analysis_end = date.fromisoformat(args.end_date)
    # Widen the discovery window so the 5-year look-back and t+1 outcome are observable.
    disc_start = analysis_start - timedelta(days=LOOKBACK_DAYS) if args.history else analysis_start
    disc_end = min(analysis_end + timedelta(days=NEXT_MEETING_MAX_DAYS), date.today())

    ticker_map = load_ticker_map(client)
    if args.tickers:
        refs = discover_via_tickers(client, args.tickers, disc_start, disc_end, args.max_filings, ticker_map)
    else:
        refs = discover_via_fulltext(client, disc_start, disc_end, args.max_filings, ticker_map)
    stats["filings_found"] = len(refs)
    log.info("Discovered %d candidate 8-K filings (%s .. %s)", len(refs), disc_start, disc_end)
    if args.max_filings > 0:
        log.warning("--max-filings=%d caps discovery; vote_number_5y and refiled_t1 need complete "
                    "firm histories. Use --max-filings 0 for the production sample.", args.max_filings)

    rows: list[dict] = []
    for k, ref in enumerate(refs, 1):
        if k % 50 == 0:
            log.info("  ... %d/%d filings processed", k, len(refs))
        if k % CHECKPOINT_EVERY == 0:
            _write_checkpoint(rows, args, k, len(refs))
        try:
            html = client.get_text(ref.url)
            stats["filings_fetched"] += 1
        except EdgarRequestError as exc:
            stats["fetch_errors"] += 1
            log.warning("SKIP fetch | %s | %s | %s", ref.cik, ref.accession_no, exc)
            continue
        try:
            obs, diag = parse_item_507(html)
        except Exception as exc:
            stats["skipped"] += 1
            log.warning("SKIP parse-crash | %s | %s | %s | %s", ref.cik, ref.accession_no, ref.url, exc)
            continue
        if not diag["marker_found"]:
            log.info("NOTE no 'Item 5.07' heading found, parsed whole document | %s", ref.url)
        if not obs:
            stats["skipped"] += 1
            log.warning("SKIP no-vote-data | %s | %s | tables=%d errors=%d | %s", ref.cik,
                        ref.accession_no, diag["n_tables"], diag["table_errors"], ref.url)
            continue
        stats["parsed_ok"] += 1
        for o in obs:
            o.update(cik=ref.cik, ticker=ref.ticker, company_name=ref.company_name,
                     filing_date=ref.filing_date, accession_no=ref.accession_no, source_url=ref.url)
            rows.append(o)

    stats["proposals_parsed"] = len(rows)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if not args.all_proposals:
        df = df[df["is_shareholder_proposal"]]
    stats["shareholder_proposals"] = int(df["is_shareholder_proposal"].sum())

    # Validate and compute the running variable.
    df["vote_share"] = [compute_vote_share(f, a) for f, a in zip(df["votes_for"], df["votes_against"])]
    bad = df["vote_share"].isna()
    for _, r in df[bad].iterrows():
        log.warning("SKIP invalid-counts | %s | %s | for=%s against=%s | %.80s", r["cik"],
                    r["accession_no"], r["votes_for"], r["votes_against"], r["proposal_desc"])
    df = df[~bad].drop_duplicates(subset=["cik", "filing_date", "proposal_desc", "votes_for"])
    if df.empty:
        return df

    # History & outcome use the WIDE window; then restrict to the analysis window.
    if args.history:
        df = add_resubmission_variables(df, disc_start, disc_end)
    else:
        df["vote_number_5y"], df["refiled_t1"], df["history_complete"] = 1, np.nan, False
    df = add_threshold_variables(df)
    df = df[(df["filing_date"] >= analysis_start.isoformat()) & (df["filing_date"] <= analysis_end.isoformat())]

    # Baseline covariates (one companyfacts request per firm).
    cov = CovariateFetcher(client)
    cov_rows = [cov.get(c, d) for c, d in zip(df["cik"], df["filing_date"])]
    df = pd.concat([df.reset_index(drop=True), pd.DataFrame(cov_rows)], axis=1)
    df["data_source"] = "EDGAR"
    return df


def finalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    for c in STANDARD_COLUMNS + EXTRA_COLUMNS:
        if c not in df.columns:
            df[c] = np.nan
    out = df[STANDARD_COLUMNS + EXTRA_COLUMNS].copy()
    for c in ("votes_for", "votes_against", "votes_abstain", "broker_non_votes"):
        out[c] = pd.to_numeric(out[c], errors="coerce").round().astype("Int64")
    out["refiled_t1"] = pd.to_numeric(out["refiled_t1"], errors="coerce").astype("Int64")
    return out.sort_values(["filing_date", "cik"]).reset_index(drop=True)


def print_summary(stats: dict, df: pd.DataFrame, out_path: str) -> None:
    line = "=" * 66
    print(f"\n{line}\n EXECUTION SUMMARY\n{line}")
    print(f" Data source                     : {stats['data_source']}")
    print(f" Filings discovered (8-K, 5.07)  : {stats['filings_found']}")
    print(f" Filings fetched                 : {stats['filings_fetched']}")
    print(f" Filings parsed successfully     : {stats['parsed_ok']}")
    print(f" Filings skipped (no vote data)  : {stats['skipped']}")
    print(f" Fetch errors                    : {stats['fetch_errors']}")
    print(f" Proposal rows parsed (all)      : {stats['proposals_parsed']}")
    print(f" Shareholder-proposal rows       : {stats['shareholder_proposals']}")
    print(f" Valid live observations         : {stats['live_valid']}")
    if stats.get("client"):
        c = stats["client"]
        print(f" HTTP requests / cache hits      : {c.n_http_requests} / {c.n_cache_hits}")
    print(f" FINAL ROW COUNT                 : {len(df)}  ->  {out_path}")
    if len(df):
        vs = df["vote_share"]
        near = ((vs - FOCAL_CUTOFF).abs() <= 0.02).sum()
        print(f" Vote share mean / median        : {vs.mean():.3f} / {vs.median():.3f}")
        print(f" Obs within +/-2pp of 15%        : {near}")
        s15 = df[df["in_15pct_sample"] == True]  # noqa: E712
        print(f" 15%-bar sample (2nd vote in 5y) : {len(s15)}  "
              f"(below: {int((s15['vote_share'] < FOCAL_CUTOFF).sum())}, "
              f"at/above: {int((s15['vote_share'] >= FOCAL_CUTOFF).sum())})")
        if s15["refiled_t1"].notna().any():
            lo = s15.loc[s15["vote_share"] < FOCAL_CUTOFF, "refiled_t1"].astype(float).mean()
            hi = s15.loc[s15["vote_share"] >= FOCAL_CUTOFF, "refiled_t1"].astype(float).mean()
            print(f" Raw refiled_t1 rate below/above : {lo:.2f} / {hi:.2f}   (not an RD estimate)")
        print(f" Covariate coverage (log_assets) : {df['log_assets'].notna().mean():.0%}")
    if stats["data_source"] == "SYNTHETIC":
        print("\n !! SYNTHETIC DATA: for pipeline testing only, never for inference.")
    print(f" Log file                        : {LOG_FILE}\n{line}")


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Scrape 8-K Item 5.07 shareholder-proposal votes for a 14a-8(i)(12) RDD.")
    p.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="'Name email' declared to SEC (or $SEC_USER_AGENT)")
    p.add_argument("--start-date", default="2021-01-01", help="first vote (8-K filing) date in the analysis sample")
    p.add_argument("--end-date", default="2024-12-31", help="last vote date in the analysis sample")
    p.add_argument("--max-filings", type=int, default=400, help="cap on 8-Ks to download (0 = no cap)")
    p.add_argument("--tickers", nargs="*", help="restrict to these tickers (submissions API) instead of full-text search")
    p.add_argument("--no-history", dest="history", action="store_false",
                   help="skip the 5-year look-back / t+1 linkage (fewer requests, no refiled_t1)")
    p.add_argument("--all-proposals", action="store_true", help="keep management proposals too")
    p.add_argument("--min-obs", type=int, default=50, help="fallback to synthetic data below this many valid rows")
    p.add_argument("--n-synthetic", type=int, default=200)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--force-synthetic", action="store_true", help="skip EDGAR and write synthetic data")
    p.add_argument("--output", default="rdd_data.csv")
    p.add_argument("--cache-dir", default="edgar_cache")
    p.add_argument("--no-cache", action="store_true")
    p.add_argument("--self-test", action="store_true", help="run offline parser tests and exit")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    setup_logging(LOG_FILE, args.verbose)
    if args.self_test:
        return run_self_test()

    stats = {k: 0 for k in ("filings_found", "filings_fetched", "parsed_ok", "skipped", "fetch_errors",
                            "proposals_parsed", "shareholder_proposals", "live_valid")}
    stats.update(data_source="EDGAR", client=None)
    t0 = time.time()

    live = pd.DataFrame()
    if not args.force_synthetic:
        try:
            live = scrape_live(args, stats)
        except EdgarBlockedError as exc:
            log.error("Live scraping aborted: %s", exc)
        except Exception as exc:                     # never die without an output file
            log.exception("Unexpected failure during live scraping: %s", exc)
    valid = live.dropna(subset=["vote_share"]) if len(live) else live
    stats["live_valid"] = len(valid)

    if args.force_synthetic or len(valid) < args.min_obs:
        if not args.force_synthetic:
            log.warning("Only %d valid live observations (< %d): using SYNTHETIC fallback data.",
                        len(valid), args.min_obs)
        if len(valid):
            partial = "rdd_data_live_partial.csv"
            finalize_columns(valid).to_csv(partial, index=False)
            log.warning("Kept the %d real rows separately in %s (not mixed with synthetic rows).", len(valid), partial)
        final = generate_synthetic_rdd_data(n=args.n_synthetic, seed=args.seed)
        stats["data_source"] = "SYNTHETIC"
    else:
        final = valid

    final = finalize_columns(final)
    final.to_csv(args.output, index=False)
    print_summary(stats, final, args.output)
    log.info("Done in %.1fs", time.time() - t0)
    return 0


# =============================================================================
# 6. OFFLINE SELF-TEST (python 01_scrape_edgar.py --self-test)
# =============================================================================

_FIXTURES = {
    # One small table per proposal, description in the paragraph above.
    "per_proposal_tables": ("""<html><body>
      <p><b>Item 5.07 Submission of Matters to a Vote of Security Holders.</b></p>
      <p>Proposal 3 - Advisory vote to approve executive compensation.</p>
      <table><tr><td>For</td><td>Against</td><td>Abstain</td><td>Broker Non-Votes</td></tr>
             <tr><td>500,000,000</td><td>20,000,000</td><td>1,000,000</td><td>40,000,000</td></tr></table>
      <p>Proposal 5 - Shareholder proposal regarding an independent board chair.</p>
      <p>The votes were as follows:</p>
      <table><tr><td>Votes For</td><td></td><td>Votes Against</td><td>Abstentions</td><td>Broker Non-Votes</td></tr>
             <tr><td>74,500,000</td><td>&nbsp;</td><td>425,500,000</td><td>3,000,000</td><td>40,000,000</td></tr></table>
      <p>Item 9.01 Financial Statements and Exhibits.</p>
      <table><tr><td>For</td><td>Against</td></tr><tr><td>Stockholder proposal decoy</td><td>1,000</td><td>2,000</td></tr></table>
      </body></html>""", [(74_500_000, 425_500_000, 3_000_000, 40_000_000, 0.149)]),
    # Multi-row table, descriptions in column 1, % columns, footnotes, row numbers.
    "multi_row_with_pct": ("""<html><body><div><font>ITEM&nbsp;5.07</font> Submission of Matters</div>
      <table>
        <tr><td></td><td>Proposal</td><td>Votes For</td><td>% For</td><td>Votes Against(1)</td><td>% Against</td>
            <td>Abstentions</td><td>Broker Non-Votes</td></tr>
        <tr><td>1</td><td>Ratification of the appointment of auditors</td><td>900,000</td><td>95.0</td><td>%</td>
            <td>47,368</td><td>5.0%</td><td>1,000</td><td>&#8212;</td></tr>
        <tr><td>6</td><td>Stockholder Proposal Requesting a Report on Lobbying</td><td>150,000</td><td>15.0%</td>
            <td>850,000</td><td>85.0%</td><td>2,000</td><td>100,000</td></tr>
      </table><p>SIGNATURES</p></body></html>""", [(150_000, 850_000, 2_000, 100_000, 0.15)]),
    # Transposed table, labels down the first column.
    "transposed": ("""<html><body><table><tr><td>Item 5.07</td><td>Submission of Matters to a Vote</td></tr></table>
      <p>Proposal No. 4: Stockholder proposal requesting a climate transition plan.</p>
      <table><tr><td>In Favor</td><td>12,000,000</td></tr><tr><td>Opposed</td><td>88,000,000</td></tr>
             <tr><td>Abstentions</td><td>500,000</td></tr><tr><td>Broker Non-Votes</td><td>9,000,000</td></tr></table>
      </body></html>""", [(12_000_000, 88_000_000, 500_000, 9_000_000, 0.12)]),
    # Results written as prose only.
    "paragraph_only": ("""<html><body><p>Item 5.07. Submission of Matters to a Vote of Security Holders</p>
      <p>Proposal 4 - Shareholder proposal on simple majority vote. The proposal received 30,000,000 votes for,
      170,000,000 votes against, 1,500,000 abstentions and 12,000,000 broker non-votes and was not approved.</p>
      <p>Item 9.01 Exhibits</p></body></html>""", [(30_000_000, 170_000_000, 1_500_000, 12_000_000, 0.15)]),
    # Header in its own table, numbers in the next (split template).
    "split_header": ("""<html><body><p>Item 5.07 Submission of Matters to a Vote of Security Holders</p>
      <p>Proposal 7. Shareowner proposal regarding a racial equity audit.</p>
      <table><tr><td>For</td><td>Against</td><td>Abstain</td><td>Broker Non-Votes</td></tr></table>
      <table><tr><td>14,900,000</td><td>85,100,000</td><td>100</td><td>-</td></tr></table>
      </body></html>""", [(14_900_000, 85_100_000, 100, None, 0.149)]),
}


def run_self_test() -> int:
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

    print("Parser fixtures:")
    for name, (html, expected) in _FIXTURES.items():
        obs, diag = parse_item_507(html)
        sp = [o for o in obs if o["is_shareholder_proposal"]]
        got = [(o["votes_for"], o["votes_against"], o["votes_abstain"], o["broker_non_votes"]) for o in sp]
        exp = [tuple(None if x is None else float(x) for x in e[:4]) for e in expected]
        shares = [round(compute_vote_share(o["votes_for"], o["votes_against"]), 3) for o in sp]
        check(name, got == exp and shares == [e[4] for e in expected],
              f"-> {got} share={shares} method={[o['parse_method'] for o in sp]}")

    print("Header mapping:")
    for cell, cat in [("For", "votes_for"), ("In Favor", "votes_for"), ("Yes", "votes_for"),
                      ("Votes Cast For", "votes_for"), ("Against", "votes_against"), ("Opposed", "votes_against"),
                      ("No", "votes_against"), ("Votes Against", "votes_against"), ("Withheld", "votes_against"),
                      ("Abstain", "votes_abstain"), ("Abstentions", "votes_abstain"),
                      ("Broker Non-Votes", "broker_non_votes"), ("Unvoted", "broker_non_votes"),
                      ("% For", "pct"), ("Shareholder proposal regarding lobbying for climate", None)]:
        check(f"'{cell}'", classify_header(cell) == cat, f"-> {classify_header(cell)}")

    print("Threshold boundary (strict '<'):")
    t = add_threshold_variables(pd.DataFrame({"vote_share": [0.149, 0.1499999, 0.15, 0.151], "vote_number_5y": [2] * 4}))
    check("14.9% and 14.99999% excludable, 15.0% eligible", list(t["below_threshold"]) == [True, True, False, False])

    print("Resubmission linkage:")
    toy = pd.DataFrame({
        "cik": ["1"] * 4,
        "filing_date": ["2018-05-01", "2021-05-01", "2022-05-03", "2023-05-02"],
        "proposal_desc": ["Shareholder proposal regarding an independent board chair"] * 3
                         + ["Shareholder proposal regarding lobbying disclosure"],
        "vote_share": [0.2, 0.149, 0.30, 0.1],
    })
    linked = add_resubmission_variables(toy, date(2016, 1, 1), date(2024, 12, 31))
    check("vote_number_5y", list(linked["vote_number_5y"]) == [1, 2, 3, 1], f"-> {list(linked['vote_number_5y'])}")
    check("refiled_t1", list(linked["refiled_t1"]) == [0.0, 1.0, 0.0, 0.0], f"-> {list(linked['refiled_t1'])}")

    print("Synthetic generator:")
    syn = generate_synthetic_rdd_data(200, seed=1)
    check("200 rows, all synthetic", len(syn) == 200 and (syn["data_source"] == "SYNTHETIC").all())
    check("vote_share consistent with counts",
          np.allclose(syn["vote_share"], syn["votes_for"] / (syn["votes_for"] + syn["votes_against"])))
    check("centred near 15%", abs(syn["vote_share"].median() - 0.15) < 0.02, f"median={syn['vote_share'].median():.3f}")

    print("\nSELF-TEST", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())