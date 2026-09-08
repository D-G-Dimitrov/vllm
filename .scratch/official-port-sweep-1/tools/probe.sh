#!/usr/bin/env bash
# usage: ssh jetson-222 'bash -s <sha>' < probe.sh   — read-only probe, touches nothing
SHA="$1"
cd ~/dev/vllm || exit 1
BASE=$(git rev-parse --short=9 HEAD)
echo "== start: HEAD=$BASE dirty=$(git status --porcelain | grep -v '^??' | wc -l | tr -d ' ')  probe_target=$SHA"
if git merge-base --is-ancestor "$SHA" HEAD 2>/dev/null; then
  echo "  !! $SHA IS ALREADY AN ANCESTOR OF HEAD — do not pick it (a 'DIVERGED' report below is just the landed pick)"
fi
echo "== upstream commit =="
git show --stat --format='%h %s%n  author %an | parents %p' "$SHA" | sed 's/^/  /'
echo "== per-file fork-locality vs this commit's parent =="
git show --name-only --format='' "$SHA" | sed '/^$/d' | sort -u > /tmp/pr_files.txt
while IFS= read -r f; do
  ours=$(git rev-parse "HEAD:$f" 2>/dev/null | cut -c1-9)
  uparent=$(git rev-parse "$SHA^:$f" 2>/dev/null | cut -c1-9)
  if [ -z "$ours" ]; then st=ABSENT_IN_FORK
  elif [ "$ours" = "$uparent" ]; then st="CLEAN(base==upstream_parent)"
  else st="DIVERGED fork=$ours up=$uparent  [$(git diff --numstat "$SHA^" HEAD -- "$f" | awk '{print "+"$1"-"$2}')]"
  fi
  echo "  $f -> $st"
done < /tmp/pr_files.txt
echo "== swap/qwen-88 collision =="
git show --name-only --format='' 337d3f5dd | sed '/^$/d' | sort -u > /tmp/pr_swap.txt
echo "  collisions: [$(comm -12 /tmp/pr_swap.txt /tmp/pr_files.txt | tr '\n' ' ')]"
echo "== full patch =="
git show --format='' "$SHA" | sed 's/^/  /'
