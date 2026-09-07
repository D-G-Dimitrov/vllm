# Pause snapshot — 2026-09-07, item 114 at its test gate

## Where the grind stands
- `mitaka/backport` tip on **origin** = **`8fc9c187e`** (item 113). 109 landed, 1 skipped, 207 pending.
- **`b2a06c9e4` (item 114, official `bd575a0d0b` AutoRound block-wise FP8) is committed LOCALLY on
  `jetson-222:~/dev/vllm` and NOT pushed.** It is 1 commit ahead of `8fc9c187e`, tree clean, `-x` trailer
  genuine (committed via `cherry-pick --continue`).
- Worker `1570db65-26e3-4595-9af2-91825355183c` was dispatched to run the test gate. **Check it first.**
  - Accept: fail-set identical to parent `8fc9c187e` + new upstream tests passing, **and** the fork's own
    `d1ba3782f9` INC/MTP tests green → `git fetch jetson-222:~/dev/vllm mitaka/backport && git merge --ff-only FETCH_HEAD
    && git push origin mitaka/backport`, tick `bd575a0d0b`, ledger-sync, then dispatch item 115 (`82936c409d`).
  - Reject: revert on jetson (`git reset --hard 8fc9c187e`), record why in `outcomes.log.md`, tick nothing,
    then dispatch item 115 anyway (the pick is not blocking the queue).

## Why 114 is the one item that must not be pushed on faith
AutoRound routing is **ungated**: `INCConfig.override_quantization_method` maps `quant_method == "auto-round"`
to `inc` for any such checkpoint — no flag, no platform check. `GLM-5.3-Flash-W4A16-AutoRound` is protected.
Conflict was resolved **OURS**; verified: my committed delta vs upstream's delta on `inc/inc.py` = 200 vs 201
changed lines, sole difference = upstream's deletion of one comment line; `_mtp_checkpoint_prefix` x3 and
`if name and self.extra_config` (line 353) intact. A **theirs** resolution would have raised `NameError: name
'name' is not defined` on the first `get_quant_method` for every INC checkpoint — it compiles, only runtime
catches it. Unproven risk the worker flagged: `_validate_mxfp_quantization` now dispatches on exact
`data_type == "mx_fp"`, so an existing **MXFP4** checkpoint violating `group_size==32` / `sym` /
`packing_format==auto_round:llm_compressor` / `backend==auto` now asserts where it previously loaded.

## Swap status (unchanged)
`swap/qwen-88` = **`337d3f5dd`** on origin, one commit on `6e5b0dfa1`, never merged. Item 88 stays `[ ]`.
Merge gate: (1) `test_get_kv_cache_config_mamba_hybrid_sharing_infeasible_no_indexer` resolved or proven
known-base, (2) meta-device build + key/shape coverage vs
`~/jetson-containers/data/models/huggingface/models--Qwen--Qwen3.8-Flash-Next-FP8`, (3) owner's go.
GPU numerics need the 4-node TP4 window (~200 GiB; 61 GiB/node) — that also takes down the agent's own endpoint,
so it must be scripted and agent-free. **Single-Jetson serving of Qwen3.8-Flash-Next is impossible** (FP8 needs
~200 GiB). Re-run the swap-collision check after every landing (`git show --name-only 337d3f5dd` vs the new commit).

## Queue rules — all three exclusion sources, or you re-dispatch the swap
Next actionable = first `[ ]` tracker line whose sha is in none of:
1. `swap-dependent.txt` (45 items depending on the swap)
2. **`e126687a9a`** — item 88 itself, NOT in that file (near-miss: a naive oldest-first rule picks the
   unvalidated model swap and a worker happily cherry-picks it). Now also a hard rule in `worker-brief.md`.
3. `skipped.txt` (currently `4c58a0c398`, marked `[~]` in the tracker, decision record in `outcomes.log.md`)

## Two defects found this session that will bite again
- **The 342-file overlap oracle is STALE.** `c01b50e390..3bec275739` freezes at Sep 2; fork commit `d1ba3782f9`
  is Sep 4 and caused item 114's conflict while the frozen set reported zero overlap. Use
  `fork-surface.sh <repo> <ref>` → **354 files**, includes `inc/inc.py`.
- **pi async capacity leaks and survives `pi` restart.** Dispatch says "capacity exhausted 2/2" while
  `view:fleet` shows no active runs. Root cause: a finished run's `process-terminal.json` stays `"pending"`, so
  its `session-active-async-capacity/<key>/slot-N/owner.json` is never released. Fix = `mv` that `slot-N` to a
  backup (done once: `/tmp/pi-capacity-backup-1786800194`-style dir). `stop` and `globalConcurrencyLimit` do NOT
  work. Companion bug: children can finish and never notify — poll `status` when one goes quiet. `toolBudget`
  counts **calls, not tokens** (a child used 884k tokens in 27 calls), so bound scope in prose instead.

## Standing rules
All git/docker over `ssh jetson-222` only; grind worktree `~/dev/vllm`, swap worktree `~/dev/vllm-swap88`
(one writer each, orchestrator is sole pusher). Every container: `-e CUDA_VISIBLE_DEVICES=""` **and**
`--runtime nvidia`; `:8000` is production (health 200 before/after). Never touch host `/dev/shm`. Halt only for
wtdcode-functional conflicts on DSV4 / qwen4_exp / glm5next, anything GPU-touching, or the swap merge.
**Owner granted standing autonomy: don't ask "go?" between items.** Verify → push → assert tip → collision-check
→ tick by re-reading the file from disk → ledger-sync → dispatch next, all in one turn.

## UPDATE: 114 RESOLVED AND PUSHED -- pause point is clean
`mitaka/backport` tip = **`b2a06c9e4`** everywhere (110 landed / 1 skipped / 206 pending).
Test gate passed (fail-set delta = a test the pick itself adds, CUDA-environmental). Next actionable = **item 115 `82936c409d`**.
Note the two land-chain defects above before resuming.
