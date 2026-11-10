#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Overnight Stage-1 scrape for the 14a-8(i)(12) RDD paper.
#
# Start:   ./run_overnight.sh
# Watch:   tail -f scrape_*.log
# Stop:    kill $(cat scrape.pid)
# Resume:  just run it again. Downloaded HTML is cached in edgar_cache/, so a
#          restart re-parses from disk instead of re-hitting SEC.
#
# Why these flags:
#   --max-filings 0   no cap. vote_number_5y (5-year look-back) and refiled_t1
#                     (t+1 outcome) both need COMPLETE firm histories; capping
#                     truncates them and silently biases the running variable.
#   --min-obs 0       disables the synthetic fallback. If SEC blocks us we get
#                     an empty CSV plus a loud log, NOT 200 fake rows that look
#                     real. Never let mock data reach the R stage by accident.
#   (history on)      the 5-year look-back + t+1 linkage is the whole point.
# ---------------------------------------------------------------------------
set -euo pipefail

cd "$(dirname "$0")"

# SEC requires a real, monitored contact address in the User-Agent header.
# Without it EDGAR answers 403 and may block the IP.
export SEC_USER_AGENT="${SEC_USER_AGENT:?Set SEC_USER_AGENT first, e.g. export SEC_USER_AGENT='Jokubas Narvydas you@example.com'}"

. .venv/bin/activate

STAMP="$(date +%Y%m%d_%H%M)"
LOG="scrape_${STAMP}.log"

# systemd-inhibit: block lid-close suspend while the scrape runs. Without it,
# closing the laptop lid pauses the process until the machine wakes again.
# The lock is released automatically when python exits.
setsid nohup systemd-inhibit \
    --what=handle-lid-switch:sleep:idle \
    --mode=block \
    --why="SEC EDGAR 14a-8 scrape in progress" \
    python -u 01_scrape_edgar.py \
    --start-date 2021-01-01 \
    --end-date   2024-12-31 \
    --max-filings 0 \
    --min-obs 0 \
    --output rdd_data.csv \
    > "$LOG" 2>&1 &

echo $! > scrape.pid

echo "started  pid $(cat scrape.pid)"
echo "log      $LOG"
echo "cache    edgar_cache/"
echo
echo "follow progress:  tail -f $LOG"
echo "stop it:          kill \$(cat scrape.pid)"
