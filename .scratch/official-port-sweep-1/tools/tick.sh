#!/usr/bin/env bash
# Terse ledger bookkeeping for a minimum-gate landing.
# usage: tick.sh <up-sha10> <landing9> <title> <note>
set -uo pipefail
SCR=/Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/official-port-sweep-1
UP="$1"; NEW="$2"; TITLE="$3"; NOTE="${4:-}"
# Notes must never travel through argv: backticks in markdown get command-substituted by bash.
# Pass a file (prefixed with @) for any note containing code spans.
if [ "${NOTE:0:1}" = "@" ]; then
  NOTEFILE="${NOTE:1}"
  [ -s "$NOTEFILE" ] || { echo "!! note file $NOTEFILE missing/empty; refusing to write a blank note"; exit 1; }
  NOTE=$(cat "$NOTEFILE")
fi
case "$NOTE" in *'`'*) echo "!! note contains raw backticks and was passed as argv - use @file"; exit 1;; esac
cd "$SCR" || exit 1

grep -q "^### " outcomes.log.md || { echo "!! no ### entries found; refusing to number"; exit 1; }
N=$(grep -oE '^### [0-9]+' outcomes.log.md | awk '{if ($2+0 > m) m = $2+0} END {print m+1}')
[ "$N" -gt 1 ] || { echo "!! numbering probe yielded $N; refusing"; exit 1; }

{
  printf '\n'
  printf '### %s. `%s` -> `%s` — %s\n\n' "$N" "$UP" "$NEW" "$TITLE"
  printf '*Minimum gate (hybrid).* %s\n\n' "$NOTE"
  printf '`tip %s -> %s`.\n' "$(cd /Users/mitaka/Projects/PyCharm/vllm-mitaka && git rev-parse --short=9 "$NEW^")" "$NEW"
} >> outcomes.log.md

before=$(grep -c "^- \[ \] $UP " issues/03-pr-grind.md)
sed -i '' "s/^- \[ \] $UP /- [x] $UP /" issues/03-pr-grind.md
after=$(grep -c "^- \[x\] $UP " issues/03-pr-grind.md)
echo "entry=$N  ticked ${before}->${after}"
bash /tmp/audit.sh 2>/dev/null | head -1
bash ledger-sync.sh 2>&1 | tail -1
