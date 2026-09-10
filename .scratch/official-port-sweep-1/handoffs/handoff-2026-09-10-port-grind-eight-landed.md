# Handoff — official→mitaka/backport grind (sweep-1), 2026-09-10 second session

**Written at a clean boundary: `state-check.sh` CLEAN, nothing in flight.** Supersedes
`handoff-2026-09-09-port-grind-batched-recon.md`. Durable copy lives at
`.scratch/official-port-sweep-1/handoffs/` and rides `origin/mitaka/backport-ledger` + the jetson tarball.

## Ground truth (re-derive from git before acting — this table is already one landing stale)

| | |
|---|---|
| `origin/mitaka/backport` = Mac = jetson | `b6ba8c780` |
| Ledger counts | `checked=159 unchecked=157 skipped=1 sum=317` |
| `mitaka/backport` vs `upstream/main` | **292 ahead, 427 behind** |
| Production endpoint | `jetson-222:8000` → 200 (container `a9a7acb9bee3`, image `vllm/vllm-openai:qwen38-flash-next`) — untouched all session |
| Landed this session | entries **156–163** (`c35551f892`, `8f03625b3d`, `504bb8b0c3`, `754d5e1f65`, `92ccd2c306`, `9e905f7450`, `40824284bc`, `55aa766dc8`) |
| Leg image used | `mitakad/vllm:0.29.0.dev0-r39.2.tegra-aarch64-cp312-cu132-24.04-commit.d4d703c` (build is ~284 commits behind tip → always overlay OUR file versions, never trust the image's own copy) |

Push **only** from `/Users/mitaka/Projects/PyCharm/vllm-mitaka`. Never from `vllm-backport`.

## Next four actionable (tracker file order)

1. `1f1f628859` [Feat][MM Hashing] include `media_io_kwargs` in multi-modal hashes (#54241) — forecast OK
2. `25efcfa788` [Attention] Enable adaptive verification for `FLASHINFER_MLA_SPARSE_DSV4` — **DSV4 by name: expect fork-diverged, expect full depth, do not minimum-gate on the subject line**
3. `0d4ad47981` [Kernel] Add B12X causal paged attention backend (#52017) — kernel item, no runtime leg under the never-touch-GPU rule (skill 16)
4. `339e16cbb6` [Bugfix] Support MCP SDK 2.x tool input schemas (#53870)

## What changed about how to run this (operational, learned the hard way)

- **Recon children failed 2/2 this session.** One was *misdiagnosed* dead by me and was actually alive (see below); the second genuinely failed: `exitCode 1` after 36.6 min / 667k tokens with `windowPeak` only 36k, so **context size was not the cause** and `context: fresh` did not protect it. Both died after doing real work, mid-analysis, leaving no report. → **Default to ORCHESTRATOR-DIRECT for now** (skill step 2 sanction after 2+ deaths). Parent-side recon on the Mac clone is cheap: it holds every upstream sha, so `git show <sha> -- <path>`, blob comparisons and `git rev-parse HEAD:<path>` all work read-only with no jetson contention.
- **Never declare a child dead from indirect signals.** I killed a live run this session because `children.list` showed 0 model requests and a `find` for its fork jsonl used the wrong filename pattern. The correct liveness test is `subagent action:"status"` (turn/token/tool counts, `Updated` timestamp) plus the run dir's `events.jsonl` (`wc -l`, last `turn_start`/`toolResult`). Saved as a `failure` memory.
- **Consequence of that mistake, and the rule:** I then picked onto the shared branch and removed the child's live worktree, making *me* the "unknown concurrent writer". Children stay in disposable worktrees off a fixed tip; **the parent must not pick onto `mitaka/backport` while recon is in flight**, and must stop a child before taking over its work.
- **Never cherry-pick while a leg is reading `/w`.** `~/dev/vllm` is the branch worktree, so a pick swaps files under a running pytest. Serialize: leg → pick → leg.
- **Overlay legs: one container per arm.** Once a module is copied into the image's site-packages it stays for the container's life, and a re-copy does not re-import. Two arms = two containers.
- **`git archive` inside a container fails** with `detected dubious ownership in repository at '/w'` → `tar: does not look like a tar archive` → a vacuous `collected 0 items` that reads like a result. Prepare any base tree on the **host** before mounting. Failed attempts leave root-owned `.so`; clear with a container (`docker run --rm --entrypoint bash -v ~/dev:/x <img> -c 'rm -rf /x/MN1/b2'`), then host `rmdir`.
- **A wrong file path can hide a real risk.** My `git show -- <path>` for `8f03625b3d` used `schemes/` instead of `compressed_tensors_moe/` and returned empty, nearly causing me to skip the one file with a GPU-path change. Re-derive paths from `git show --name-status <sha>` every time.

## Two findings worth keeping in mind beyond their entries

- **157 (Zen Int8 MoE)** put `from ...experts.cpu_moe import ZenCPUExpertsInt8` inside `process_weights_after_loading`, which runs on the **GPU** path for every compressed-tensors W8A8 INT8 MoE load. Measured inert here (import OK on `NvmlCudaPlatform`, `_supports_current_device=False`), but it is the pattern to watch: an "[CPU][AMD]" subject can carry a GPU-path hunk.
- **160 (INC selection)** proved the inverse also matters: the fork has its **own** code inside `INCConfig.get_quant_method` (`_mtp_checkpoint_prefix`, fork commit `d1ba3782f9`, for MTP draft loading) and a fork-authored test for it. Upstream's new tests and the fork's MTP test all pass together on the merged tree (12 passed); the BASE arm fails exactly the two intended cases. Full evidence in entry 160 and `logs/i160-N1-leg-*.txt`.

## Still needs a human, not a round (unchanged, still open)

1. **The unidentified concurrent cherry-picker is NOT root-caused** — and note this session adds no new evidence for it either way, because the one suspicious reflog event I investigated turned out to be **me**. Do not treat it as explained. `ACK-REFLOG` remains absent, so a foreign reflog head fails closed.
2. **Item 139's SM100 caveat** (`882ca8d696`, cutedsl W4A16): inert on Jetson, can change numerics on SM100+. Revisit before serving NVFP4 there.
3. **Ledger durability is still structurally weak**: `.scratch/official-port-sweep-1` is untracked files inside the push clone; three copies exist, nothing auto-restores. Owner's call.
4. **Memory store reports 100% capacity** (38,682/16,384 chars) — writes still succeed but it is over budget; consolidate before it degrades retrieval.
5. **Rebase pressure**: 292 ahead / 427 behind `upstream/main` (measured this session). The handoff before this one said 284/427; the +8 is exactly this session's landings.
