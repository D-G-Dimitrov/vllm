#!/usr/bin/env bash
# fast.sh <up-sha10> "<title>" "<note>"  — hybrid minimum-gate pipeline:
# pick on jetson -> require clean + blob-identity (or verified rename) -> land -> terse ledger entry.
# Stops without touching the branch on ANY of: conflict, file-set diff, or a non-EQ blob.
set -uo pipefail
UP="$1"; TITLE="${2:-}"; NOTE="${3:-}"
cd /Users/mitaka/Projects/PyCharm/vllm-mitaka || exit 1
BASE=$(git rev-parse --short=9 HEAD)

OUT=$(ssh jetson-222 "bash -s $UP $BASE" < /tmp/pick.sh 2>&1 | grep -viE "pi-lens|tree-sitter|read_symbol|^\s*(→|·)|^✗|^✓")
echo "$OUT" | sed -n '3,20p'

echo "$OUT" | grep -q "rc=0" || { echo ">> STOP: pick did not complete cleanly (conflict or error). No landing."; exit 2; }
echo "$OUT" | grep -q "FILE SET DIFF" && { echo ">> STOP: file-set diff (check for fork-side rename before landing)."; exit 3; }
NE=$(echo "$OUT" | grep -c ": blob NE")
[ "$NE" = "0" ] || { echo ">> STOP: $NE file(s) not byte-identical to upstream - needs human-grade review, not minimum gate."; exit 4; }
echo "$OUT" | grep -q "delta_vs_upstream IDENTICAL" || { echo ">> STOP: no delta-identity evidence."; exit 5; }
echo "$OUT" | grep -q "collisions: \[ *\]" || { echo ">> STOP: swap collision present."; exit 6; }
NEW=$(echo "$OUT" | sed -n 's/.*rc=0 HEAD=\([0-9a-f]\{9\}\).*/\1/p' | head -1)
[ -n "$NEW" ] || { echo ">> STOP: could not parse new sha."; exit 7; }

echo ">> gates passed."
# Hybrid rule: minimum gate != no reading. Hot-path files get a human/orchestrator diff read BEFORE landing.
HOT=$(echo "$OUT" | grep -oE '^  [a-zA-Z0-9_./-]+\.(py|cu|cuh|cpp|rs|h): blob' | awk '{print $1}' | grep -E '^(vllm/(model_executor/layers/|v1/(attention|worker|engine)/)|csrc/|vllm/sampling_params\.py|vllm/config/)' || true)
if [ -n "$HOT" ] && [ "${FORCE:-0}" != "1" ]; then
  echo ">> STOP (needs-read): this pick touches hot-path code and must be diff-read before landing:"
  echo "$HOT" | sed 's/^/     /'
  echo "   pick is committed on jetson at $NEW (unpushed, tree clean)."
  echo "   after reading: bash /tmp/land.sh $NEW $BASE && bash /tmp/tick.sh $UP $NEW \"<title>\" \"<note>\""
  echo "   to discard:    ssh jetson-222 'cd ~/dev/vllm && git reset --hard $BASE'"
  echo "   or FORCE=1 to land unread (not the default)."
  exit 9
fi
if [ -z "$TITLE" ]; then
  TITLE=$(ssh jetson-222 "cd ~/dev/vllm && git show -s --format='%s' $UP" 2>/dev/null)
fi
[ -n "$TITLE" ] || { echo '>> STOP: could not derive a commit title; refusing to write a placeholder ledger entry.'; exit 10; }
[ -n "$NOTE" ] || NOTE='Minimum-gate landing under the hybrid rule: no leg attempted (not executable on this box and/or not fork-relevant).'
echo "   title: $TITLE"
echo ">> landing $NEW on $BASE"
bash /tmp/land.sh "$NEW" "$BASE" 2>&1 | tail -3 || { echo ">> STOP: land failed"; exit 8; }
# Notes travel by FILE, never argv: backticks in markdown are command-substituted by bash.
NOTEF=/tmp/note.$(date +%s).md
printf '%s\n' "$NOTE" > "$NOTEF"
bash /tmp/tick.sh "$UP" "$NEW" "${TITLE:-$UP}" "@$NOTEF"; trc=$?
rm -f "$NOTEF"
[ "$trc" = "0" ] || echo "!! tick.sh rc=$trc - item is LANDED but the ledger entry may be incomplete; repair before continuing"
