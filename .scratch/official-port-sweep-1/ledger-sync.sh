#!/usr/bin/env bash
# Mirror the sweep ledger off the Mac. Orchestrator is the ONLY caller (sole .scratch writer).
#
# Why: `.scratch/` in the Mac clone is untracked and holds the sole record of what has been
# ported and why (outcomes.log.md, the tracker, swap-dependent.txt, the swap plans). Origin
# carries the commits but none of the reasoning. This pushes it to the orphan branch
# `mitaka/backport-ledger` (deliberately NOT a descendant of mitaka/backport, so the ported
# branch stays clean for PRs) and drops a second copy on jetson-222, independent of GitHub.
#
# Usage: .scratch/official-port-sweep-1/ledger-sync.sh ["commit message"]
# Run it after every push+bookkeep pair, and before any handoff.
set -euo pipefail

SRC=/Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch
LTX=/Users/mitaka/Projects/PyCharm/vllm-ledger
BR=mitaka/backport-ledger
MSG="${1:-ledger: sync $(date -u +%Y-%m-%dT%H:%M:%SZ)}"
JE=jetson-222
TGZ=/tmp/scratch-ledger.tgz

# a linked worktree's .git is a FILE, not a directory — probe it with git, not with -d
git -C "$LTX" rev-parse --git-dir >/dev/null 2>&1 \
  || { echo "MISSING worktree $LTX — recreate with: git -C /Users/mitaka/Projects/PyCharm/vllm-mitaka worktree add $LTX $BR"; exit 1; }
[ "$(git -C "$LTX" branch --show-current)" = "$BR" ] \
  || { echo "WRONG BRANCH in $LTX: $(git -C "$LTX" branch --show-current)"; exit 1; }

# 1. source -> ledger worktree (handoffs live in the source tree, so --delete is safe)
rsync -a --delete --exclude='__pycache__' --exclude='*.pyc' "$SRC/" "$LTX/.scratch/"

# 2. commit + push, then ASSERT origin matches (a silent no-op push is the known failure mode)
cd "$LTX"
git add -A
if git diff --cached --quiet; then
  echo "ledger: no changes"
else
  git -c commit.gpgsign=false commit -q -m "$MSG"
  git push -q origin "$BR"
  LOCAL=$(git rev-parse HEAD)
  REMOTE=$(git ls-remote origin "$BR" | cut -f1)
  [ "$LOCAL" = "$REMOTE" ] || { echo "LEDGER PUSH ASSERT FAILED local=$LOCAL remote=$REMOTE"; exit 1; }
  echo "ledger: pushed $BR -> ${LOCAL:0:9}"
fi

# 3. second copy on the work box, independent of GitHub
tar czf "$TGZ" --exclude='__pycache__' --exclude='*.pyc' -C "$(dirname "$SRC")" "$(basename "$SRC")"
L_SHA=$(shasum -a 256 "$TGZ" | awk '{print $1}')
scp -q "$TGZ" "$JE:~/dev/scratch-ledger.tgz.new"
ssh "$JE" 'mv -f ~/dev/scratch-ledger.tgz.new ~/dev/scratch-ledger.tgz && sha256sum ~/dev/scratch-ledger.tgz' \
  | awk '{print $1}' > /tmp/ledger-remote-sha
R_SHA=$(cat /tmp/ledger-remote-sha)
[ "$L_SHA" = "$R_SHA" ] || { echo "LEDGER MIRROR SHA MISMATCH local=$L_SHA remote=$R_SHA"; exit 1; }
echo "ledger: mirrored to $JE:~/dev/scratch-ledger.tgz (${L_SHA:0:12})"
