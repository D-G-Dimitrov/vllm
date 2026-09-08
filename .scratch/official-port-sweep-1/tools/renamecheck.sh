#!/usr/bin/env bash
# renamecheck.sh <new9> <base9> — verify a pick that landed at a fork-side relocated path.
# Run ON jetson inside ~/dev/vllm. Renders a verdict ONLY if assertions actually ran.
set -uo pipefail
cd ~/dev/vllm || exit 1
NEW="$1"; BASE="$2"

UP=$(git log -1 --format='%b' "$NEW" | grep -oE 'cherry picked from commit [0-9a-f]{8,}' | awk '{print $5}')
case "${UP:-}" in
  *[!0-9a-f]*|"") echo "FATAL: trailer sha extraction yielded '${UP:-<empty>}'; refusing"; exit 1 ;;
esac
[ "${#UP}" -ge 8 ] || { echo "FATAL: trailer sha '${UP}' too short; refusing"; exit 1; }
git cat-file -e "$UP^{commit}" 2>/dev/null || { echo "FATAL: '$UP' is not a commit; refusing"; exit 1; }
echo "  upstream=$UP  base=$BASE  new=$NEW"

UPPATHS=$(git show --name-only --format='' "$UP" | sed '/^$/d')
OURPATHS=$(git show --name-only --format='' "$NEW" | sed '/^$/d')
NU=$(printf '%s\n' "$UPPATHS" | grep -c .)
NO=$(printf '%s\n' "$OURPATHS" | grep -c .)
[ "$NU" -ge 1 ] || { echo "FATAL: upstream touched no paths - nothing to assert; refusing to render a verdict"; exit 1; }
echo "  [1] file count upstream=$NU ours=$NO $([ "$NU" = "$NO" ] && echo OK || echo FAIL)"
[ "$NU" = "$NO" ] || exit 1

fail=0
checked=0
while IFS= read -r up; do
  [ -n "$up" ] || continue
  checked=$((checked + 1))
  if git cat-file -e "$NEW:$up" 2>/dev/null; then
    echo "  [2] $up STILL present at upstream path -> not a clean relocation; inspect manually"; fail=1; continue
  fi
  ours=$(git show --name-only --format='' "$NEW" | sed -n '1p')
  git cat-file -e "$NEW:$ours" 2>/dev/null || { echo "  [2] our target '$ours' missing"; fail=1; continue; }
  ob=$(git rev-parse "$BASE:$ours" 2>/dev/null | cut -c1-9); ub=$(git rev-parse "$UP^:$up" 2>/dev/null | cut -c1-9)
  git diff "$BASE" "$NEW" -- "$ours" | grep -E "^[+-]" | grep -vE "^(\+\+\+|---)" | sort > /tmp/rc_o.txt
  git show "$UP" -- "$up"          | grep -E "^[+-]" | grep -vE "^(\+\+\+|---)" | sort > /tmp/rc_u.txt
  d=$(diff /tmp/rc_o.txt /tmp/rc_u.txt | grep -c '^[<>]')
  rb1=$(git rev-parse "$NEW:$ours" | cut -c1-9); rb2=$(git rev-parse "$UP:$up" | cut -c1-9)
  echo "  [3] $up  ->  $ours"
  echo "      base blob ours=$ob up=$ub $([ "$ob" = "$ub" ] && echo MATCH || echo MISMATCH)"
  echo "      delta diff lines=$d $([ "$d" = "0" ] && echo "(identical)" || echo FAIL)"
  echo "      result blob ours=$rb1 up=$rb2 $([ "$rb1" = "$rb2" ] && echo MATCH || echo MISMATCH)"
  [ "$ob" = "$ub" ] || fail=1
  [ "$d" = "0" ] || fail=1
  [ "$rb1" = "$rb2" ] || fail=1
done < <(printf '%s\n' "$UPPATHS")

echo "  [4] assertions executed on $checked path(s); state: dirty=$(git status --porcelain|grep -v '^??'|wc -l|tr -d ' ') unmerged=$(git ls-files -u|wc -l) seq=$(ls .git/sequencer 2>/dev/null|wc -l) health=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
[ "$checked" -ge 1 ] || { echo "  VERDICT: NO ASSERTIONS RAN - no verdict"; exit 1; }
echo "  VERDICT: $([ "$fail" = "0" ] && echo 'RELOCATION FAITHFUL (safe to land)' || echo 'DO NOT LAND - assertions failed')"
exit "$fail"
