#!/usr/bin/env bash
# Terse ledger bookkeeping for a minimum-gate landing.
# usage: tick.sh <up-sha10> <landing9> <title> <note>
set -uo pipefail
SCR=${SCR:-/Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/official-port-sweep-1}
TDIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)   # sibling tools live beside this script
UP="$1"; NEW="$2"; TITLE="$3"; NOTE="${4:-}"
# Tracker lines carry 10-char shas and entries show 9-char landings. A full sha (straight from
# git log / heat-map-raw) made the tick sed match NOTHING, so the item landed UNCHECKED while the
# entry reported success (observed on 907b1a7f22 -> 9ccd9694b). Normalise instead of trusting caller.
UP=$(printf '%s' "$UP" | cut -c1-10)
NEW=$(printf '%s' "$NEW" | cut -c1-9)
case "$UP" in *[!0-9a-f]*|"") echo "!! sha '$UP' is not hex"; exit 1;; esac
case "$NEW" in *[!0-9a-f]*|"") echo "!! sha '$NEW' is not hex"; exit 1;; esac
# Notes must never travel through argv: backticks in markdown get command-substituted by bash.
# Pass a file (prefixed with @) for any note containing code spans. The guard applies to the
# argv path ONLY -- a file-sourced note is the sanctioned channel and legitimately contains
# code spans; refusing it there would abort AFTER land.sh has already pushed (landed, unticked).
if [ "${NOTE:0:1}" = "@" ]; then
  NOTEFILE="${NOTE:1}"
  [ -s "$NOTEFILE" ] || { echo "!! note file $NOTEFILE missing/empty; refusing to write a blank note"; exit 1; }
  NOTE=$(cat "$NOTEFILE")
else
  case "$NOTE" in *'`'*) echo "!! note contains raw backticks and was passed as argv - use @$NOTE"; exit 1;; esac
fi
cd "$SCR" || exit 1

grep -q "^### " outcomes.log.md || { echo "!! no ### entries found; refusing to number"; exit 1; }
N=$(grep -oE '^### [0-9]+' outcomes.log.md | awk '{if ($2+0 > m) m = $2+0} END {print m+1}')
[ "$N" -gt 1 ] || { echo "!! numbering probe yielded $N; refusing"; exit 1; }

# Counted BEFORE the append so an unmatched sha cannot leave a confident-looking entry behind
# for an item that stays unchecked (the exact state the audit would then miss).
before=$(grep -c "^- \[ \] $UP " issues/03-pr-grind.md)
[ "$before" = "1" ] || { echo "!! ASSERT: '$UP' matched $before unchecked tracker lines (expected exactly 1) - refusing to write entry $N for an item that cannot be ticked"; exit 1; }

{
  printf '\n'
  printf '### %s. `%s` -> `%s` — %s\n\n' "$N" "$UP" "$NEW" "$TITLE"
  printf '*Minimum gate (hybrid).* %s\n\n' "$NOTE"
  printf '`tip %s -> %s`.\n' "$(cd /Users/mitaka/Projects/PyCharm/vllm-mitaka && git rev-parse --short=9 "$NEW^")" "$NEW"
} >> outcomes.log.md

sed -i '' "s/^- \[ \] $UP /- [x] $UP /" issues/03-pr-grind.md
after=$(grep -c "^- \[x\] $UP " issues/03-pr-grind.md)
[ "$after" = "1" ] || { echo "!! ASSERT: after sed, '$UP' is checked $after times (expected 1) - tracker hand-edit needed"; exit 1; }
echo "entry=$N  ticked ${before}->${after}"
bash "$TDIR/audit.sh" 2>/dev/null | head -1
bash ledger-sync.sh 2>&1 | tail -1
