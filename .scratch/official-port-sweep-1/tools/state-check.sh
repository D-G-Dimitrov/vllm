#!/usr/bin/env bash
# Start-of-round ground truth. Run BEFORE the first pick of a session and after any pause.
# Exists because on 2026-09-09 the ledger SRC directory was deleted mid-session and nothing in the
# pipeline noticed until an unrelated `scp` failed. Every check is an assert, not a print.
set -uo pipefail
cd / || exit 1   # own cwd must be neutral: the second-writer check below would otherwise match THIS script
MAC=${MAC:-/Users/mitaka/Projects/PyCharm/vllm-mitaka}
SCR=$MAC/.scratch/official-port-sweep-1
LTX=${LTX:-/Users/mitaka/Projects/PyCharm/vllm-ledger}
rc=0
ok() { echo "  ok    $*"; }
no() { echo "  FAIL  $*"; rc=1; }

# 1. ledger source exists and is readable (it is UNTRACKED -- git will never report its loss)
[ -s "$SCR/outcomes.log.md" ] && ok "SRC outcomes.log.md present ($(wc -l < "$SCR/outcomes.log.md" | tr -d ' ') lines)" \
  || { no "SRC outcomes.log.md MISSING/empty -- restore with: rsync -a $LTX/.scratch/ $MAC/.scratch/"; }
[ -s "$SCR/issues/03-pr-grind.md" ] && ok "SRC tracker present" || no "SRC tracker MISSING"

# 2. SRC agrees with the durable ledger copy (uncommitted delta is expected only right after a tick)
if [ -s "$SCR/outcomes.log.md" ]; then
  d=$(diff -rq "$LTX/.scratch/official-port-sweep-1" "$SCR" 2>&1 | grep -vc 'handoffs' || true)
  [ "$d" = "0" ] && ok "SRC == ledger worktree (byte-identical)" || no "SRC differs from ledger in $d path(s) -- diff before writing"
fi

# 3. counts
T=$SCR/issues/03-pr-grind.md
c=$(grep -c '^- \[x\]' "$T" 2>/dev/null || true); u=$(grep -c '^- \[ \]' "$T" 2>/dev/null || true)
s=$(grep -c '^- \[~\]' "$T" 2>/dev/null || true); sum=$((c + u + s))
[ "$sum" = "317" ] && ok "counts $c/$u/$s sum=317" || no "counts $c/$u/$s sum=$sum (expected 317)"

# 4. the three tips, each read non-empty and exactly
o=$(git -C "$MAC" ls-remote --heads origin refs/heads/mitaka/backport | awk '$2=="refs/heads/mitaka/backport"{print $1}')
m=$(git -C "$MAC" rev-parse HEAD)
j=$(ssh -o ConnectTimeout=10 jetson-222 'cd ~/dev/vllm && git rev-parse HEAD' 2>/dev/null)
[ -n "$o" ] || no "empty ls-remote read from origin"
[ -n "$j" ] || no "empty read from jetson"
if [ -n "$o" ] && [ "$o" = "$m" ] && [ "$o" = "$j" ]; then ok "tips agree local=origin=jetson ${o:0:9}"; else
  no "tips DISAGREE local=${m:0:9} origin=${o:0:9} jetson=${j:0:9}"; fi

# 5. nobody moved the Mac branch behind our back (the 10:32:44 cherry-pick case)
last=$(git -C "$MAC" reflog -1 --format='%gs')
case "$last" in
  merge*|*"Fast-forward"*) ok "Mac reflog head is ours: ${last:0:60}" ;;
  *) # A foreign reflog head is only tolerable if a human/agent explicitly vouched for THIS commit:
     # write the full sha of the adopted commit into $SCR/ACK-REFLOG. Never weaken this check instead.
     ack=$(tr -d ' \n' < "$SCR/ACK-REFLOG" 2>/dev/null)
     if [ -n "$ack" ] && [ "$ack" = "$(git -C "$MAC" rev-parse HEAD)" ]; then
       ok "Mac reflog head is foreign but ACKNOWLEDGED: ${last:0:55} (ACK-REFLOG matches HEAD; delete it once a landing supersedes)"
     else
       no "Mac reflog head is NOT a merge: '$last' -- a second writer moved the branch; halt and reconcile (or, if adoption is intended, write the exact adopted sha into $SCR/ACK-REFLOG)"
     fi ;;
esac
dirty=$(git -C "$MAC" status --porcelain | grep -vc '^??' || true)
[ "$dirty" = "0" ] && ok "Mac tracked-dirty=0" || no "Mac tracked-dirty=$dirty (second writer?)"

# 6. is anything sitting INSIDE the push clone? (a count of pi processes is noise; a cwd in this
#    repo is the actual second-writer signal -- this is the check that settles the 2026-09-09 event)
anc=""; ap=$$
while :; do pp=$(ps -o ppid= -p "$ap" 2>/dev/null | tr -d ' '); [ -z "$pp" ] && break; anc="$anc $pp"; [ "$pp" = "1" ] && break; ap=$pp; done
occ=$(cd / && lsof -d cwd 2>/dev/null | awk -v r="$MAC" -v ANC=" $anc " '$NF==r && ($1=="node"||$1=="pi"||$1 ~ /zsh$/||$1=="bash"||$1=="fish"||$1=="git") { if (index(ANC," "$2" ")==0) print $1"/"$2 }' | sort -u | tr '\n' ' ')
# no legit session runs with the push clone as cwd (agents sit in vllm-backport), so any holder is foreign
[ -z "$occ" ] && ok "no process cwd inside the push clone" || no "processes hold a cwd in $MAC: $occ -- identify them before landing"
echo "        (info) pi processes: $(ps -eo pid,lstart,command | grep -cE '[p]i[[:space:]]*$' || true)"

# 7. jetson work box state
read -r jd ju <<<"$(ssh -o ConnectTimeout=10 jetson-222 'cd ~/dev/vllm && echo "$(git status --porcelain | grep -vc "^??") $(git ls-files -u | wc -l)"' 2>/dev/null)"
[ "${jd:-x}" = "0" ] && [ "${ju:-x}" = "0" ] && ok "jetson dirty=0 unmerged=0" || no "jetson dirty=${jd:?} unmerged=${ju:?} or unreadable"
h=$(ssh -o ConnectTimeout=10 jetson-222 'curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health' 2>/dev/null)
[ "$h" = "200" ] && ok "production :8000 = 200" || no "production :8000 = ${h:-no-response}"

[ "$rc" = "0" ] && echo "state-check: CLEAN -- safe to pick" || echo "state-check: NOT CLEAN -- reconcile before touching the branch"
exit "$rc"
