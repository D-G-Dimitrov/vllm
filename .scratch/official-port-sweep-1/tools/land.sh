#!/usr/bin/env bash
# Reusable atomic land chain: guard -> fetch -> ff-only -> push -> 3-way tip assert.
# Usage: bash /tmp/land.sh <expected_new_sha_9> <expected_base_sha_9>
set -uo pipefail
EXPECT=${1:?usage: land.sh <new9> <base9>}
BASE=${2:?usage: land.sh <new9> <base9>}
cd /Users/mitaka/Projects/PyCharm/vllm-mitaka || exit 1

echo "== 0. guards =="
D=$(git status --porcelain | grep -v '^??' | wc -l | tr -d ' ')
echo "  mac_tracked_dirty=$D  mac_HEAD=$(git rev-parse --short=9 HEAD)"
[ "$D" = "0" ] || { echo "ABORT: Mac worktree dirty (pr/efix invariant) -- investigate, do not merge over it"; git status --porcelain | grep -v '^??' | head; exit 1; }
[ "$(git rev-parse --short=9 HEAD)" = "$BASE" ] || { echo "ABORT: Mac not at expected base $BASE"; exit 1; }
# the second writer is a human editor; warn rather than block
pgrep -x 'pycharm' >/dev/null 2>&1 && echo "  WARNING: a JetBrains IDE process is running -- it can mutate this worktree via autosave"

echo "== 1. fetch from jetson =="
git fetch -q jetson-222:~/dev/vllm mitaka/backport || { echo "ABORT: fetch failed"; exit 1; }
echo "  FETCH_HEAD=$(git rev-parse --short=9 FETCH_HEAD)"
[ "$(git rev-parse --short=9 FETCH_HEAD)" = "$EXPECT" ] || { echo "ABORT: jetson tip $(git rev-parse --short=9 FETCH_HEAD) != expected $EXPECT"; exit 1; }

echo "== 2. ff-only merge =="
git merge --ff-only FETCH_HEAD || { echo "ABORT: not a fast-forward -- shadow-writer reconcile required, halt grind"; exit 1; }
NEW=$(git rev-parse HEAD)
echo "  mac_HEAD=$NEW"

echo "== 3. push =="
git push -q origin mitaka/backport; echo "  push_exit=$?"

echo "== 4. three-way tip assert (exact refname, non-empty) =="
ORIG=$(git ls-remote --heads origin refs/heads/mitaka/backport | awk '$2=="refs/heads/mitaka/backport"{print $1}')
[ -n "$ORIG" ] || { echo "ASSERT FAIL: empty ls-remote read from origin"; exit 1; }
JET=$(ssh jetson-222 'cd ~/dev/vllm && git rev-parse HEAD')
[ -n "$JET" ] || { echo "ASSERT FAIL: empty read from jetson"; exit 1; }
echo "  local =$NEW"
echo "  origin=$ORIG"
echo "  jetson=$JET"
[ "${NEW:0:9}" = "$EXPECT" ] || { echo "ASSERT FAIL: landed ${NEW:0:9} != expected $EXPECT"; exit 1; }
[ "$ORIG" = "$NEW" ] && [ "$JET" = "$NEW" ] || { echo "ASSERT FAIL: tips disagree"; exit 1; }
echo "ALL THREE TIPS AGREE: ${NEW:0:9}"
git log --format='  %h %s' -1
