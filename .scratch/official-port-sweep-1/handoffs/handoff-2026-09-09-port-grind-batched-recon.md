# Handoff — official→mitaka/backport grind (sweep-1), batched-recon era

**Written:** 2026-09-09, end of session. **State verified clean at write time** — `state-check.sh` CLEAN.
Supersedes `handoff-2026-09-08b-port-grind-ledger-verify.md`. **Durable copy:**
`.scratch/official-port-sweep-1/handoffs/handoff-2026-09-09-port-grind-batched-recon.md`, which rides
`origin/mitaka/backport-ledger` and the jetson tarball; the `/tmp` copy is disposable (macOS wipes it on reboot).

## Ground truth (re-derive before acting; do not trust this doc for shas after one landing)

| | |
|---|---|
| `origin/mitaka/backport` = Mac = jetson | `aeb5deca9` |
| `origin/mitaka/backport-ledger` | `9692e9c38` |
| Ledger counts | `checked=151 unchecked=165 skipped=1 sum=317` |
| Production endpoint | `jetson-222:8000` → 200 (container `a9a7acb9bee3`, **do not stop**, no Mac mount) |
| Items landed this session | 142–155 (entries have full per-item evidence; do not re-derive here) |

Push **only** from `/Users/mitaka/Projects/PyCharm/vllm-mitaka`. The agent cwd `…/vllm-backport` is a different
repo and a known landmine.

## Next steps

1. `bash /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/official-port-sweep-1/tools/state-check.sh` — obey rc.
2. Next four actionable (`tools/audit.sh`): `c35551f892` (KV-offload tiering shutdown), `8f03625b3d` (Zen Int8 MoE),
   `504bb8b0c3` (repo-local OTel CI helpers), `754d5e1f65` (entrypoints coverage).
3. Run the round as batched recon — the procedure that now works end to end is **skill item 30** of
   `official-port-grind-loop`; items 28–29 hold the two failure modes it replaced. Do not re-derive them.
4. **Rebase pressure is bigger than it looks.** Measured this session: `mitaka/backport` is **284 ahead but 427 behind
   `upstream/main`**, and the unmerged queue spans commit dates **2026-06-29 → 2026-09-04** (138 raw `git cherry` `+`
   commits; `audit.sh` calls 123 of them actionable after exclusions). Consider an epoch rebase with the owner after
   ~20 more items rather than grinding indefinitely against a moving base.
   Note the ref names: `origin` = the fork, `upstream` = `vllm-project/vllm`, base is **`upstream/main`** — there is no
   `official` ref despite the `.scratch/official-port-sweep-1` directory name.

## Unresolved (needs a human, not a round)

- **Unknown concurrent writer — NOT root-caused.** Two bare `git cherry-pick`s appeared on the Mac mid-item
  (`10:31:47` + `19:38:16`), each tree-identical to my own pick but without the `-x` trailer. Mitigation is
  detection, not prevention: `state-check.sh` + the `ACK-REFLOG` escape hatch. **`ACK-REFLOG` was deleted this
  session** once normal landings superseded it, so a foreign reflog head now fails closed again — if it reappears,
  write the exact adopted sha into `.scratch/official-port-sweep-1/ACK-REFLOG` only after proving tree equality,
  and delete it as soon as a normal landing supersedes it.
- **Item 139 (`882ca8d696`, cutedsl W4A16) open caveat.** Inert on Jetson, but FlashInfer symbols genuinely exist on
  SM100+, so it can change numerics there. Revisit before serving NVFP4 on SM100+.
- **Ledger durability is still structurally weak.** `.scratch/official-port-sweep-1` lives *inside the push clone* as
  untracked files, so a deletion is invisible to git (this actually happened and cost recovery time). Three copies
  exist (Mac SRC, ledger branch, jetson tarball) but nothing auto-restores. Making `~/Projects/PyCharm/vllm-ledger`
  the primary, or adding SRC-restore to `state-check.sh`, is the owner's call and is worth making before another
  incident.

## Environment facts that repeatedly cost time

- Children run on the **same small local model** as the parent → `context: fork` is unusable (skill 28). Use
  `context: fresh` + `scout` + self-contained brief; parent keeps every write and every leg.
- CPU legs: worktrees are unbuilt, so overlay only the changed modules into the image's installed package, one
  container **per item** (overlays persist within a container), and grep a marker proving the overlay landed
  (skill 30 c/d). Stop chasing image-vs-tip skew after two hops once it reaches fork-diverged code.
- `land.sh <pick> <base>` asserts **jetson tip == pick**, so a stacked set lands in one fast-forward call; then
  `tick.sh` each sha in queue order.
- Shell tool sometimes joins multi-line commands with a space — keep every command on one line.
- The compacted session summary is **not** ground truth. It fabricated a commit subject and a torch-lockfile premise
  once (entry 151 records the correction), and this session's own draft handoff carried a fabricated "~440 ahead /
  ~4 years deep" until measured (corrected above, with the real ref name). **Anything numeric or naming a ref in a
  handoff must be re-derived from `git` before it is written down.**

## Suggested skills

1. **`official-port-grind-loop`** (project) — read in full, then **items 28–30** specifically; they are this
   session's net output. `/Users/mitaka/.pi/agent/skills/mitaka-skills/official-port-grind-loop/SKILL.md`
2. **`enforce-subagent-fanout-concurrency`** — keep fan-out ≤ 2 against the Jetson vLLM server.
3. **`diagnosing-bugs`** — for any leg that fails to discriminate; distinguish harness fault from product fault
   before believing a result (this session had three harness faults in a row that looked like product results).

## Artifact map

| What | Where |
|---|---|
| Ledger SRC (authoritative) | `vllm-mitaka/.scratch/official-port-sweep-1/ledger/` |
| Tools (`state-check` `pick` `land` `tick` `ledger-verify` `ledger-sync` `audit` `leg-*`) | `.scratch/official-port-sweep-1/tools/` |
| Per-item evidence logs (`i14x-*`, `batch-ABD-leg.txt`, `*-recon.md`) | `.scratch/official-port-sweep-1/logs/` |
| Item queue / heat-map | `.scratch/official-port-sweep-1/issues/03-pr-grind.md` |
| Jetson mirror | `jetson-222:~/dev/scratch-ledger.tgz` |

All of the above is on `origin/mitaka/backport-ledger` too — if SRC looks wrong, compare before writing.
