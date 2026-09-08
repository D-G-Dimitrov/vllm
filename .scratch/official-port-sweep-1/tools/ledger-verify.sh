#!/usr/bin/env bash
# Assert ONE ledger entry exists in all three durable copies: the Mac source tree, the
# mitaka/backport-ledger branch on origin, and the jetson tarball mirror.
#
# Why this exists: on 2026-09-08 item 141's `tick.sh` printed `entry=141 ticked 1->1` and
# `ledger: mirrored ... (c5c58d93077f)`, yet outcomes.log.md and the tracker were later found
# reverted to the *previous* item's content AND mtime, no ledger commit existed, and the jetson
# tarball was still the previous item's sha. A bookkeeping step that reports success while
# writing nothing is worse than one that fails, because the audit then "confirms" a tick that
# is not there. Every landing must therefore end with this check.
#
# usage: ledger-verify.sh <up-sha10> <entry-number>
set -uo pipefail

UP=$(printf '%s' "${1:?usage: ledger-verify.sh <up10> <entryN>}" | cut -c1-10)
N="${2:?usage: ledger-verify.sh <up10> <entryN>}"
SRC=/Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/official-port-sweep-1
LTX=/Users/mitaka/Projects/PyCharm/vllm-ledger
BR=mitaka/backport-ledger
HDR="### ${N}. \`${UP}\`"
rc=0

grep -qF -- "$HDR" "$SRC/outcomes.log.md" \
  && echo "  src-entry : OK" || { echo "  src-entry : MISSING '$HDR'"; rc=1; }
grep -qF -- "- [x] $UP " "$SRC/issues/03-pr-grind.md" \
  && echo "  src-tick  : OK" || { echo "  src-tick  : MISSING"; rc=1; }

git -C "$LTX" fetch -q origin "$BR" 2>/dev/null
git -C "$LTX" show "FETCH_HEAD:.scratch/official-port-sweep-1/outcomes.log.md" 2>/dev/null \
  | grep -qF -- "$HDR" && echo "  origin    : OK" || { echo "  origin    : MISSING (no ledger commit carries the entry)"; rc=1; }

ssh -o ConnectTimeout=10 jetson-222 \
  'tar xzOf ~/dev/scratch-ledger.tgz .scratch/official-port-sweep-1/outcomes.log.md 2>/dev/null' \
  | grep -qF -- "$HDR" && echo "  jetson    : OK" || { echo "  jetson    : MISSING (mirror is stale or corrupt)"; rc=1; }

if [ "$rc" = "0" ]; then
  echo "ledger-verify: entry $N ($UP) confirmed in SRC + origin + jetson mirror"
else
  echo "ledger-verify: FAILED - the landing is safe in git, but the LEDGER is not durable for this entry; repair before the next item"
fi
exit "$rc"
