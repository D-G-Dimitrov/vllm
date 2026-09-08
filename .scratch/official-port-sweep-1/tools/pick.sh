#!/usr/bin/env bash
# usage: ssh jetson-222 'bash -s <sha> <base9>' < pick.sh
# Generic: assert state -> pick (abort on conflict) -> faithfulness that is correct whether or not the file is fork-diverged.
SHA="$1"; BASE="$2"
cd ~/dev/vllm || exit 1
echo "== 0. start =="
H=$(git rev-parse --short=9 HEAD); D=$(git status --porcelain | grep -v '^??' | wc -l | tr -d ' ')
echo "  HEAD=$H dirty=$D unmerged=$(git ls-files -u|wc -l) seq=$(ls .git/sequencer 2>/dev/null|wc -l)  health_before=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)"
[ "$H" = "$BASE" ] && [ "$D" = "0" ] || { echo "  ABORT: state mismatch (HEAD=$H expected=$BASE, dirty=$D)"; exit 1; }
git merge-base --is-ancestor "$SHA" HEAD 2>/dev/null && { echo "  ABORT: $SHA already in history"; exit 1; }

echo "== 1. pick =="
git cherry-pick -x "$SHA" > /tmp/pick.log 2>&1; rc=$?
tail -3 /tmp/pick.log | sed 's/^/    /'
if [ "$rc" != "0" ]; then
  echo "  rc=$rc CONFLICT in: $(git diff --name-only --diff-filter=U | tr '\n' ' ')"
  grep -n -A8 "^<<<<<<<" $(git diff --name-only --diff-filter=U) 2>/dev/null | head -30 | cut -c1-135
  git cherry-pick --abort
  echo "  ABORTED clean: HEAD=$(git rev-parse --short=9 HEAD) dirty=$(git status --porcelain|grep -v '^??'|wc -l|tr -d ' ') unmerged=$(git ls-files -u|wc -l)"; exit 2
fi
NEW=$(git rev-parse --short=9 HEAD)
echo "  rc=0 HEAD=$NEW ahead=$(git rev-list --count $BASE..HEAD) dirty=$(git status --porcelain|grep -v '^??'|wc -l|tr -d ' ')"

echo "== 2. faithfulness =="
git show --name-only --format='' HEAD | sed '/^$/d' | sort > /tmp/f_ours.txt
git show --name-only --format='' "$SHA" | sed '/^$/d' | sort > /tmp/f_up.txt
if diff -q /tmp/f_ours.txt /tmp/f_up.txt >/dev/null; then echo "  file sets identical ($(wc -l < /tmp/f_up.txt|tr -d ' '))"; else echo "  !! FILE SET DIFF"; diff /tmp/f_ours.txt /tmp/f_up.txt; fi
while IFS= read -r f; do
  r1=$(git rev-parse "HEAD:$f" 2>/dev/null|cut -c1-9); r2=$(git rev-parse "$SHA:$f"|cut -c1-9)
  git diff "$BASE" HEAD -- "$f" | grep -E "^[+-]" | grep -vE "^(\+\+\+|---)" | sort > /tmp/d_o.txt
  git show "$SHA" -- "$f" | grep -E "^[+-]" | grep -vE "^(\+\+\+|---)" | sort > /tmp/d_u.txt
  dl=$(diff /tmp/d_o.txt /tmp/d_u.txt | grep -c '^[<>]')
  echo "  $(basename "$f"): blob $([ "$r1" = "$r2" ] && echo EQ || echo NE)  delta_vs_upstream $([ "$dl" = "0" ] && echo IDENTICAL || echo "DIFF($dl lines)")"
done < /tmp/f_up.txt
echo "  numstat ours: $(git show --numstat --format='' HEAD | awk '{printf "%s +%s/-%s  ",$3,$1,$2}')"
echo "  numstat up:   $(git show --numstat --format='' "$SHA" | awk '{printf "%s +%s/-%s  ",$3,$1,$2}')"
a=$(git show "$SHA"|git patch-id --stable|awk '{print $1}'); b=$(git show HEAD|git patch-id --stable|awk '{print $1}')
echo "  patch-id $([ "$a" = "$b" ] && echo "EQUAL ($a) [same changed-lines only; does NOT imply byte-identity -- trust blob EQ]" || echo "differs (expected if any file is fork-diverged)")"
echo "== 3. swap collision + state =="
git show --name-only --format='' 337d3f5dd | sed '/^$/d' | sort -u > /tmp/f_swap.txt
echo "  collisions: [$(comm -12 /tmp/f_swap.txt /tmp/f_ours.txt | tr '\n' ' ')]"
echo "  health_after=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health) HEAD=$(git rev-parse --short=9 HEAD) dirty=$(git status --porcelain|grep -v '^??'|wc -l|tr -d ' ') unmerged=$(git ls-files -u|wc -l) seq=$(ls .git/sequencer 2>/dev/null|wc -l)"
