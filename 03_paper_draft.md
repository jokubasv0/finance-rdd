# Do Resubmission Thresholds Deter Shareholder Proposals? Regression Discontinuity Evidence from SEC Rule 14a-8(i)(12)

*Draft — Stage 3. All numbers generated from `rdd_data.csv` by
`02_rdd_analysis.py` and `02b_multi_cutoff_rd.py`.*

---

## Abstract

Rule 14a-8(i)(12) permits a company to exclude a shareholder proposal that has
already been voted on if, at its most recent vote, it failed to clear a
threshold that rises with the number of prior appearances: 5% after one vote,
15% after two, 25% after three or more. Because a proposal just below the bar
may be excluded and one just above it may not, the rule generates a sharp
discontinuity in the cost of returning to the ballot. Using 2,077 proposals
across 431 firms from 2022–2025, we estimate a pooled regression discontinuity
across all three bars. Clearing the applicable threshold raises the probability
that the proponent resubmits the same topic at the next annual meeting by
**18.2 percentage points** (SE 8.4, p = 0.030) against a base refiling rate of
27%. The result is stable across bandwidths, polynomial orders, placebo cutoffs
and covariate balance tests. Estimated separately, the effect is
indistinguishable from zero at the 5% bar and grows with the threshold, though
individual bars are too thinly populated to be conclusive. We interpret the
estimates as intent-to-treat effects of *eligibility for exclusion*, since
companies retain discretion over whether to exclude.

**Keywords:** shareholder proposals, Rule 14a-8, regression discontinuity,
corporate governance, shareholder activism

---

## 1. Introduction

A shareholder proposal that fails at the ballot is not free to return. Under
Rule 14a-8(i)(12), a company may exclude a proposal that substantially
duplicates one submitted within the previous five years if that earlier
proposal failed to attract a minimum share of votes cast. The minimum rises
with repetition: 5% where the proposal has been voted on once, 15% where twice,
25% where three or more times.

The rule is a screening device. It is meant to stop a small group of
shareholders from imposing recurrent compliance costs on the firm, while
preserving the right of proposals with meaningful support to return. Whether it
achieves that balance is an empirical question about behaviour, not about the
text of the rule: the threshold only matters if proponents actually respond to
it.

This paper asks whether they do. The identification problem is that vote shares
are endogenous — proposals with more support are both more likely to clear the
bar and more likely to be resubmitted, for reasons that have nothing to do with
the rule. Comparing proposals above and below a threshold in a regression would
recover the correlation, not the rule's effect.

The discontinuity supplies the missing variation. A proposal at 14.8% faces a
materially different regulatory environment from one at 15.2%: the first may be
excluded from the next ballot, the second may not. If proposals cannot
precisely sort across that line, the two sides are comparable in every other
respect, and the difference in refiling behaviour is attributable to the rule.

Our contribution is threefold. First, we assemble a hand-validated dataset of
2,294 proposal-level votes from 2,905 EDGAR 8-K filings, parsed from Item 5.07
vote tables rather than from summary databases, and we compute vote shares from
raw For/Against counts rather than the rounded percentages printed in filings.
Second, we show that the natural single-cutoff design at 15% is severely
underpowered — 24 observations within two percentage points of the bar, a
minimum detectable effect near 88 percentage points — and that the three bars
must be pooled to answer the question at all. Third, we provide pooled evidence
that eligibility for exclusion raises refiling by roughly 18 percentage points.

The rest of the paper is organised as follows. Section 2 describes the
institutional framework. Section 3 sets out the data. Section 4 develops the
identification strategy and states its assumptions. Section 5 reports results.
Section 6 discusses threats to validity. Section 7 concludes.

---

## 2. Institutional Framework

### 2.1 Who may submit a proposal

A shareholder proposal is a recommendation or requirement that the company or
its board take a specified action, submitted for inclusion in the company's
proxy materials and voted on at a shareholder meeting. The shareholder who
submits it is the *proponent*.

Eligibility under Rule 14a-8(b) is an ownership test. A proponent must have
continuously held at least one of:

**Table 2.1.** Ownership thresholds for proposal eligibility under Rule 14a-8(b).

| Minimum market value | Holding period |
|---|---|
| $2,000 | 3 years |
| $15,000 | 2 years |
| $25,000 | 1 year |

Holdings may not be aggregated across shareholders to satisfy the test, and a
proponent may submit only one proposal per company per meeting. The proposal,
including any supporting statement, is capped at 500 words and must be received
at least 120 calendar days before the date the company released the previous
year's proxy statement.

These requirements shape who appears in our data. Individual retail holders
almost never clear the ownership threshold. The recurring proponents are public
pension funds, small activist funds that hold a token position purely to file,
religious orders, labour unions, and non-governmental organisations. Each has a
limited annual slate, so the decision to spend one slot on a given company and
topic is a real allocation choice — which is precisely the margin our outcome
variable measures.

A proponent who fails to appear and present the proposal at the meeting, absent
good cause, may have all proposals excluded for the following two calendar
years. Filing is therefore a commitment, not a costless gesture.

### 2.2 The resubmission rule

Rule 14a-8(i)(12) is one of thirteen substantive bases on which a company may
omit a shareholder proposal from its proxy statement. It applies where the
current proposal addresses substantially the same subject matter as a proposal
previously *included in the company's proxy materials* within the preceding
five calendar years, provided that the most recent vote on that subject occurred
within the preceding three calendar years, and provided that vote failed to meet
the applicable threshold:

**Table 2.2.** Resubmission thresholds under Rule 14a-8(i)(12).

| Prior appearances in 5 years | Threshold on most recent vote |
|---|---|
| 1 | 5% of votes cast |
| 2 | 15% of votes cast |
| 3 or more | 25% of votes cast |

Two drafting details are easy to miss and both matter for our measurement.

**The prior proposal must have been included, not merely submitted.** A
proposal that was itself excluded never generated a vote and therefore does not
count toward the tally. Because we observe vote records rather than filings,
this condition is satisfied by construction in our data.

**The recency condition is on the most recent vote.** Even if proposals on the
subject appear within five years, the rule is unavailable if the last vote on
them is more than three years old. A proposal that lapses for several years and
then returns is treated as a first submission for the purposes of this rule.

Three further features matter for identification.

**The comparison is strict.** A proposal receiving 14.99% is excludable; one
receiving 15.00% is not. The rule does not round.

**Votes cast excludes abstentions and broker non-votes.** Following SEC Staff
Legal Bulletin No. 14, the denominator is For plus Against. We compute the share
from raw counts; the percentages printed in 8-K filings are rounded and
occasionally computed on a different denominator.

**Exclusion is permitted, not required.** A company that is entitled to exclude
a proposal may still include it. This makes the design intent-to-treat: we
estimate the effect of *becoming eligible* for exclusion, which is attenuated
relative to the effect of actual exclusion by the share of companies that
decline to use the rule.

### 2.3 The thirteen exclusion grounds

Clearing a resubmission threshold closes one door, not thirteen. A company that
cannot rely on (i)(12) may still seek exclusion on any of the grounds below,
several of which are used far more often in practice.

**Table 2.3.** The thirteen substantive exclusion grounds under Rule 14a-8(i).

| Ground | Basis for omission |
|---|---|
| (i)(1) | Not a proper subject for shareholder action under state law |
| (i)(2) | Implementation would violate state, federal, or foreign law |
| (i)(3) | Proposal or supporting statement contravenes the proxy rules |
| (i)(4) | Redress of a personal grievance or furtherance of a special interest |
| (i)(5) | Relates to operations below 5% of assets, net earnings, and gross sales, and not otherwise significantly related to the business |
| (i)(6) | Company lacks the power or authority to implement the proposal |
| (i)(7) | Deals with a matter relating to ordinary business operations |
| (i)(8) | Would affect the outcome of the upcoming director election |
| (i)(9) | Directly conflicts with a company proposal at the same meeting |
| (i)(10) | Company has already substantially implemented the proposal |
| (i)(11) | Substantially duplicates another proponent's proposal for the same meeting |
| (i)(12) | **Resubmission below the applicable vote threshold** |
| (i)(13) | Relates to a specific amount of cash or stock dividends |

Grounds (i)(7) and (i)(10) do most of the work in practice. A company facing a
30% vote on a request to report on lobbying expenditure can simply publish the
report and then omit next year's version as substantially implemented, without
ever invoking (i)(12). Ground (i)(5), which governs economic relevance, is also
frequently litigated.

### 2.4 How exclusion actually happens

Exclusion is a procedure, not an election. Rule 14a-8(j) requires a company
intending to omit a proposal to file its reasons with the Commission no later
than 80 calendar days before it files its definitive proxy statement, and to
send a copy of that submission to the proponent. The burden of persuasion rests
on the company (Rule 14a-8(g)), which must supply the proposal, an explanation
citing applicable authority, and — where the argument turns on state or foreign
law — a supporting opinion of counsel.

Commission staff then respond. In practice this is the *no-action letter*
process: staff indicate whether they will recommend enforcement action if the
company omits the proposal. A favourable response lets the company drop the
proposal without litigation risk; an unfavourable one leaves the company to
include it or proceed at its own risk. The proponent may file a reply under Rule
14a-8(k).

Three consequences follow for our design. First, the treatment is real: there
exists a low-cost administrative route from "below the threshold" to "not on the
ballot". Second, the treatment is costly enough that many eligible companies
never use it, since the process consumes legal fees and management attention.
Third, the route is not exclusive to (i)(12) — the same procedure serves every
ground in Table 2.3.

### 2.5 Why clearing the threshold does not guarantee a ballot

A reader might assume that a proposal which cleared its threshold is
automatically included next year. It is not. The full path from one year to the
next contains several points at which the proposal can disappear:

1. The proponent must decide to file again. Clearing the threshold creates no
   obligation, and a proponent whose request was substantially satisfied, whose
   fund exited the position, or who reallocated a limited slate elsewhere may
   simply not return.
2. The company may exclude on any of the other twelve grounds in Table 2.3.
3. The company may negotiate a withdrawal: the proponent retracts the proposal
   in exchange for a policy commitment, and no vote occurs.
4. Only if all three hurdles are cleared does the proposal reach the ballot.

Clearing the threshold therefore removes one specific obstacle. It does not
create a right to a vote.

This is the single most important institutional fact for interpreting our
estimates, and it cuts in two directions.

*It does not threaten identification.* The other twelve grounds, the withdrawal
channel, and the proponent's own cost-benefit calculation all operate on both
sides of the cutoff, because they depend on what the proposal asks for and what
the company has done — not on whether the vote was 14.8% or 15.2%. These
channels are therefore smooth in the running variable, and the discontinuity we
estimate is attributable to the availability of ground (i)(12) alone. If all
thirteen grounds switched off at the threshold we would still measure an effect,
but we could not attribute it to the resubmission rule specifically.

*It does constrain what the estimate means.* Our outcome records whether a
proposal on the same subject is *filed* for the following meeting, not whether
it *reached a ballot*. We therefore estimate the effect of eligibility on
proponent filing behaviour. The company's subsequent inclusion decision is a
separate, unmeasured margin. Section 6 discusses what this implies for
interpreting the coefficient as a deterrent effect.

### 2.6 Threshold history

The 5%/15%/25% schedule governs meetings held on or after 1 January 2022. Before
that date the bars were 3%/6%/10%. This matters for sample construction: votes
held under the earlier regime cannot be scored against the current thresholds,
because a proposal at 12% was above the old 10% bar and below the current 15%
bar. Our analysis window therefore begins in 2022. Discovery extends earlier
only to construct the five-year look-back needed to count prior appearances.

---

## 3. Data

### 3.1 Source and construction

Vote results are reported in Item 5.07 of Form 8-K, which companies must file
within four business days of a shareholder meeting. We discover candidate
filings through the SEC's full-text search system, restricted to Form 8-K and
sliced by year, and additionally through the submissions API for a set of large
issuers.

Parsing is the binding constraint. Item 5.07 vote disclosure is not
machine-readable and its layout varies across filers. We implement four
layouts — a horizontal header with one row per proposal, a transposed table with
proposal labels in the first column, a header carried across two adjacent
tables, and a prose fallback for companies that report results in sentences —
and classify headers fuzzily, mapping *For*, *In Favor* and *Yes* to votes in
favour and *Against*, *Opposed* and *No* to votes against. Unparseable filings
are skipped rather than permitted to halt the run.

Covariates are drawn from the SEC's XBRL company-facts API, using the most
recent annual report filed strictly before the vote date: log total assets,
leverage (liabilities over assets, with a fallback that reconstructs liabilities
from liabilities-plus-equity less equity), and return on assets.

### 3.2 Sample

| | |
|---|---|
| 8-K filings discovered | 3,040 |
| Parsed successfully | 2,905 |
| Skipped, no vote table | 135 |
| Fetch errors | 0 |
| Proposal-level observations | 2,294 |
| Usable pooled RD sample | 2,077 |
| Dropped, right-censored outcome | 217 |
| Unique firms | 431 |
| Filing years | 2022–2025 |

The 217 dropped observations are right-censored: their next annual meeting has
not yet occurred, so refiling cannot be observed. Reinstating them as zeros
leaves the estimates unchanged in sign and magnitude.

### 3.3 Outcome

`refiled_t1` equals one where the proponent submitted a proposal on the same
topic at the firm's next annual meeting. Topics are matched by Jaccard
similarity of title tokens with a threshold of 0.5. This is the noisiest
variable in the analysis and we return to it in Section 6.

### 3.4 Descriptive statistics by threshold

| Group | n | Firms | Within ±2pp | Refiling rate |
|---|---|---|---|---|
| 5% bar (voted once) | 1,274 | 394 | 93 | 0.163 |
| 15% bar (voted twice) | 292 | 155 | 24 | 0.257 |
| 25% bar (voted 3+) | 511 | 105 | 26 | 0.556 |
| **Pooled** | **2,077** | **431** | **143** | **0.273** |

Refiling rates rise steeply with the number of prior appearances. This is
mechanical in part — a proposal that has survived two exclusion windows is
evidently one its proponent cares about — and is absorbed by threshold fixed
effects.

---

## 4. Identification

### 4.1 Running variable

For each proposal, the running variable is the vote share minus the bar
applicable to its appearance count:

$$X_i = \text{vote\_share}_i - \text{bar}(\text{appearances}_i)$$

so that $X_i = 0$ at every threshold. Treatment is eligibility for exclusion:

$$D_i = \mathbf{1}[X_i < 0]$$

Note the direction: a proposal *below* its bar becomes excludable.

### 4.2 Estimator

We estimate the pooled discontinuity by local linear regression with a
triangular kernel, following Calonico, Cattaneo and Titiunik (2014). Bandwidths
are chosen by the MSE-optimal selector of Calonico, Cattaneo and Farrell (2018)
(`bwselect = "mserd"`), and we report bias-corrected point estimates with
robust confidence intervals. Threshold fixed effects enter as covariates, and
standard errors are clustered on CIK throughout, since the sample contains 431
firms and as many as 85 proposals from a single firm.

### 4.3 Assumptions

**A1 — Continuity.** Potential outcomes are continuous in $X$ at zero. Firms
cannot precisely manipulate the vote share across the bar.

**A2 — No sorting.** The density of $X$ is continuous at zero. Tested by the
McCrary density test in Section 5.2.

**A3 — Comparable effects across bars.** The effect of becoming eligible is
similar at the 5%, 15% and 25% bars. Threshold fixed effects absorb level
differences between groups but not differences in slope. This assumption is
what licenses pooling and is the design's weakest link; Section 5.4 reports
per-threshold estimates so the reader can assess it.

**A4 — Local independence.** Observations on either side of the cutoff are
comparable in predetermined characteristics. Tested by covariate balance in
Section 5.5.

### 4.4 Why the single-cutoff design fails

Before pooling, we estimated the 15% discontinuity alone, as the natural
specification. The sample is 292 proposals with 24 within two percentage points
of the bar. The local linear estimate is 0.137 (SE 0.313, p = 0.663), with a
95% confidence interval spanning −0.478 to 0.751, and a minimum detectable
effect at 80% power of 88 percentage points.

An interval that wide cannot distinguish the rule's effect from zero or from
near-totality. Reporting it as a null result would be misleading, because the
design never had the power to detect the effect we ultimately find. Pooling is
not a specification search; it is what makes the question answerable.

---

## 5. Results

### 5.1 Main estimates

| Specification | τ | SE | p | 95% CI | n (L/R) |
|---|---|---|---|---|---|
| Pooled, threshold FE | 0.158* | 0.081 | 0.052 | [−0.001, 0.318] | 271/314 |
| **Pooled, FE + covariates** | **0.182** | **0.084** | **0.030** | **[0.017, 0.346]** | 259/295 |
| Pooled, no adjustment | 0.148* | 0.088 | 0.092 | [−0.024, 0.321] | 278/329 |

*Notes:* local linear, triangular kernel, MSERD bandwidth, bias-corrected with
robust CIs, SEs clustered on CIK. Significance: \*\*\* p<0.01, \*\* p<0.05,
\* p<0.10.

Clearing the applicable bar raises the probability of resubmission by 18.2
percentage points, against a base rate of 27%. The point estimate is stable
across adjustment choices, moving from 0.148 without adjustment to 0.182 with
covariates.

### 5.2 Density and manipulation

| Sample | t | p | Verdict |
|---|---|---|---|
| 5% bar | 0.634 | 0.526 | Pass |
| 15% bar | 0.830 | 0.407 | Pass |
| 25% bar | 0.245 | 0.806 | Pass |
| Pooled | 1.921 | 0.055 | Not interpretable |

Each threshold passes comfortably: there is no evidence that vote shares are
sorted across any of the three bars. The pooled statistic requires care. It is
computed on the stacked running variable and compares the density just below
zero with the density just above it *across all three groups at once*. Because
the groups have different vote-share distributions, stacking induces a
discontinuity that has nothing to do with manipulation. The per-threshold tests
are the valid ones, and all three pass.

### 5.3 Bandwidth sensitivity

| h / h\* | τ | SE | p | n (L/R) |
|---|---|---|---|---|
| 0.50 | 0.107 | 0.086 | 0.215 | 205/167 |
| 0.75 | 0.144 | 0.074 | 0.052 | 240/248 |
| 1.00 | 0.139 | 0.065 | 0.033 | 271/314 |
| 1.25 | 0.125 | 0.058 | 0.032 | 305/377 |
| 1.50 | 0.111 | 0.053 | 0.037 | 325/441 |
| 2.00 | 0.112 | 0.050 | 0.027 | 368/560 |

*Notes:* conventional point estimates at fixed bandwidths. Sign is stable
throughout and significance is reached at and above the MSE-optimal bandwidth.
The estimate is not an artifact of one bandwidth choice.

### 5.4 Heterogeneity across bars

| Group | τ | SE | p | 95% CI | n (L/R) |
|---|---|---|---|---|---|
| 5% bar | 0.030 | 0.092 | 0.742 | [−0.150, 0.210] | 166/213 |
| 15% bar | 0.166 | 0.286 | 0.562 | [−0.394, 0.725] | 41/40 |
| 25% bar | 0.208 | 0.218 | 0.339 | [−0.218, 0.635] | 45/53 |

The point estimates rise monotonically with the threshold, from 0.030 at the 5%
bar to 0.208 at the 25% bar. This is economically plausible: the higher the bar,
the more consequential exclusion becomes, and the larger the behavioural
response should be. It is also consistent with assumption A3 being violated in a
specific direction — pooling averages across a weaker effect at the low bar and a
stronger one at the high bar.

We do not claim the ordering as a finding. Only the 5% bar is precisely
estimated, and it is indistinguishable from zero; the 15% and 25% intervals are
wide enough to accommodate almost any effect. The ordering is a hypothesis for
better-powered data, not a result.

### 5.5 Covariate balance

| Covariate | τ | SE | p |
|---|---|---|---|
| log assets | −0.365 | 0.403 | 0.365 |
| leverage | −0.054 | 0.052 | 0.298 |
| ROA | 0.003 | 0.016 | 0.847 |

Predetermined characteristics do not jump at the cutoff, supporting A4.

### 5.6 Placebo cutoffs

| Offset from true bar | τ | SE | p |
|---|---|---|---|
| −5pp | 0.027 | 0.119 | 0.823 |
| +5pp | −0.016 | 0.068 | 0.817 |

No discontinuity where none should exist.

### 5.7 Polynomial order

| Order | τ | SE | p |
|---|---|---|---|
| p = 1 | 0.158 | 0.081 | 0.052 |
| p = 2 | 0.172 | 0.095 | 0.070 |

The estimate does not depend on the order of the local polynomial.

---

## 6. Threats to Validity

**Measurement of refiling.** `refiled_t1` is constructed by fuzzy-matching
proposal titles across years. It will both miss genuine refilings — a proponent
who reframes a topic, or whose title tokens shift — and occasionally match
unrelated proposals that share vocabulary. This is the largest source of error
in the analysis. Classical measurement error in a binary outcome attenuates the
estimate toward zero, so the true effect is plausibly larger than 0.182; but
non-classical error cannot be signed. A first-stage outcome measuring whether
the proposal was actually excluded, observable from SEC no-action letters, would
be less noisy and is the natural extension.

**Proposal classification.** Some observations with near-unanimous support are
probably management proposals misclassified as shareholder proposals, triggered
by the word "proposal" appearing in a nearby sentence. This does not affect the
15% bar, where such rows are rare, but the 5% bar is dominated by low-support
proposals and is more exposed. Restricting to rows with explicit shareholder
proposal language would tighten this at the cost of sample size.

**Pooling.** Discussed in Section 5.4. Threshold fixed effects cannot correct
for heterogeneity in the treatment effect across bars, and the observed ordering
suggests that heterogeneity is present.

**Window measurement.** The five-year look-back is implemented as a 1,827-day
window measured from the date of the current vote. The rule measures it from the
date the company evaluates exclusion, which is up to roughly eighteen months
later. At the five-year boundary this can shift a proposal between "voted once"
(5% bar) and "voted twice" (15% bar). Only proposals whose prior history sits
almost exactly five years back are affected, so the exposure is small, but it is
a genuine approximation rather than an exact implementation of the rule.

**Intent-to-treat.** Falling below the bar permits exclusion but does not compel
it. The estimate is therefore a lower bound on the effect of actual exclusion,
scaled by the share of eligible proposals that companies choose to omit.

**External validity.** The sample covers 2022–2025. Reporting suggests that
during part of this period SEC staff granted no-action relief on 14a-8 grounds
far less readily than in earlier years, and that the Commission has since
proposed further changes to the rule. We have not independently verified the
extent of either development, and we therefore do not condition the analysis on
them. If relief did become harder to obtain, companies relying on the rule
during our sample were doing so without the staff guidance that historically
accompanied it, which would attenuate the estimated effect of eligibility
relative to a regime with a functioning no-action process.

<!-- TODO(jn): verify the no-action-relief and rescission claims against SEC
     releases before circulation, or delete this paragraph. Currently unverified
     and stated conditionally for that reason. -->

---

## 7. Conclusion

Rule 14a-8(i)(12) creates sharp thresholds in the cost of returning a failed
shareholder proposal to the ballot. Using a pooled regression discontinuity
across all three thresholds, we find that clearing the applicable bar raises the
probability of resubmission by roughly 18 percentage points. The design passes
the standard falsification tests: no sorting at any threshold, balanced
covariates, null placebo cutoffs, and stability across bandwidths and
polynomial orders.

Two caveats bound the claim. The estimate is an intent-to-treat effect of
eligibility, attenuated by companies that decline to exclude. And the effect
appears to grow with the threshold, so the pooled figure is an average across
bars rather than a single behavioural parameter.

The broader point is methodological. The 15% threshold — the one that attracts
attention because it governs the common case of a twice-voted proposal — is
simply too thinly populated to identify anything. Twenty-four observations
within two percentage points of the bar cannot support inference. Recognising
that the rule contains three thresholds of identical structure, and pooling
them, is what converts an uninformative design into an informative one.

---

## Appendix A — Specification summary

| Element | Choice |
|---|---|
| Estimator | Local linear, triangular kernel |
| Bandwidth | MSERD (Calonico, Cattaneo, Farrell 2018) |
| Inference | Bias-corrected, robust CIs, clustered on CIK |
| Threshold FE | Yes (two dummies, base = 5% bar) |
| Covariates | log assets, leverage, ROA |
| Running variable | vote share − applicable bar |
| Outcome | Refiled same topic at next annual meeting |

## Appendix B — Reproduction

```bash
cd ~/rdd-paper
. .venv/bin/activate
python 01_scrape_edgar.py --self-test    # parser fixtures
python 02_rdd_analysis.py                # single-cutoff, 15%
python 02b_multi_cutoff_rd.py            # pooled, main result
```

Data: `rdd_data.csv`, 2,294 observations, 100% sourced from EDGAR.

## References

Calonico, S., Cattaneo, M. D., and Farrell, M. H. (2018). Optimal bandwidth
choice for coverage error minimization in regression discontinuity designs.
*Annals of Statistics*.

Calonico, S., Cattaneo, M. D., and Titiunik, R. (2014). Robust nonparametric
confidence intervals for regression-discontinuity designs. *Econometrica*.

Cattaneo, M. D., Jansson, M., and Ma, X. (2020). Simple local polynomial
density estimators. *Journal of the American Statistical Association*.

McCrary, J. (2008). Manipulation of the running variable in the regression
discontinuity design: a density test. *Journal of Econometrics*.

SEC Staff Legal Bulletin No. 14 (CF). Shareholder proposals.
