#!/usr/bin/env bash
# Reusable post-landing audit: counts, set-membership, and next actionable in TRACKER FILE ORDER.
# Usage: bash /tmp/audit.sh [N]
set -u
cd /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/official-port-sweep-1 || exit 1
T=issues/03-pr-grind.md
N=${1:-4}

grep '^- \[x\]' "$T" | awk '{print substr($3,1,10)}' | sort -u > /tmp/a_chk.txt
grep '^- \[ \]' "$T" | awk '{print substr($4,1,10)}' | sort -u > /tmp/a_unchk.txt
grep '^- \[ \]' "$T" | awk '{print substr($4,1,10)}'          > /tmp/a_unchk_ordered.txt
grep '^- \[~\]' "$T" | awk '{print substr($3,1,10)}' | sort -u > /tmp/a_skip.txt
grep -oE '\b[0-9a-f]{9,40}\b' outcomes.log.md | cut -c1-10 | sort -u > /tmp/a_out.txt

for f in /tmp/a_chk.txt /tmp/a_unchk.txt /tmp/a_out.txt; do
  [ -s "$f" ] || { echo "ASSERT FAIL: $f empty -- audit would be vacuous"; exit 1; }
done
SUM=$(( $(wc -l < /tmp/a_chk.txt) + $(wc -l < /tmp/a_unchk.txt) + $(wc -l < /tmp/a_skip.txt) ))
echo "checked=$(wc -l < /tmp/a_chk.txt | tr -d ' ') unchecked=$(wc -l < /tmp/a_unchk.txt | tr -d ' ') skipped=$(wc -l < /tmp/a_skip.txt | tr -d ' ') sum=$SUM (expect 317)"
[ "$SUM" = "317" ] || echo "ASSERT FAIL: sum != 317"
BAD=$(grep -vcE '^[0-9a-f]{10}$' /tmp/a_unchk.txt || true)
[ "$BAD" = "0" ] || { echo "ASSERT FAIL: $BAD unchecked shas malformed (field-number trap: checked lines use \$3, unchecked \$4)"; exit 1; }

echo "checked-shas missing an outcomes.log.md record: $(comm -23 /tmp/a_chk.txt /tmp/a_out.txt | wc -l | tr -d ' ')"
comm -23 /tmp/a_chk.txt /tmp/a_out.txt | head -5 | sed 's/^/    /'
echo "checked/unchecked overlap (must be 0): $(comm -12 /tmp/a_chk.txt /tmp/a_unchk.txt | wc -l | tr -d ' ')"

grep -vE '^\s*#' skipped.txt | grep -oE '\b[0-9a-f]{7,40}\b' | cut -c1-10 > /tmp/a_sk.txt
cut -c1-10 swap-dependent.txt | grep -E '^[0-9a-f]{10}$' > /tmp/a_sw.txt
{ cat /tmp/a_sk.txt /tmp/a_sw.txt; printf 'e126687a9a\n'; } | sort -u > /tmp/a_ex.txt
grep -vxFf /tmp/a_ex.txt /tmp/a_unchk_ordered.txt > /tmp/a_act.txt
[ -s /tmp/a_act.txt ] || { echo "ASSERT FAIL: actionable empty"; exit 1; }
echo "exclusion set=$(wc -l < /tmp/a_ex.txt | tr -d ' ') actionable=$(wc -l < /tmp/a_act.txt | tr -d ' ') (FILE ORDER, not sorted)"
echo "landmine e126687a9a excluded: $(grep -qxF e126687a9a /tmp/a_ex.txt && echo YES || echo 'NO - REGRESSION')"
echo "next $N actionable:"
head -"$N" /tmp/a_act.txt | while read -r s; do echo "    $(grep -m1 "^- \[ \] $s" "$T" | cut -c1-92)"; done
echo "forecast for next one: $(grep -E "\|$(head -1 /tmp/a_act.txt)" heat-map-raw.txt | cut -c1-120)"
