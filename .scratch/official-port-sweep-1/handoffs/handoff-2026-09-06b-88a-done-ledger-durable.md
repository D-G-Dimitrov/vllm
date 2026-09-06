# Handoff — session 2: 88a landed, ledger durable, grind resumed

**Generated:** 2026-09-06 (follows `handoff-2026-09-06-port-grind-and-swap.md`, now archived in-tree)
**Procedure:** skill `official-port-grind-loop`. **Swap detail:** `swap88b-plan.md` (read its
`88a RESOLUTION LOG` and `88c TEST FILES` sections — they are current).
**Live repo:** `/Users/mitaka/Projects/PyCharm/vllm-mitaka` (NOT the cwd `vllm-backport`).

## Corrections to the previous handoff (both matter)

1. **The agent's model server is NOT on jetson-222.** pi's `jetson` provider is
   `http://192.168.1.233:8000/v1`, a 4-Jetson cluster serving `Qwen/Qwen3.8-Flash-Next-FP8`. jetson-222's
   `:8000` is a separate production container. So worker deaths (cluster contention) and CPU-leg stalls
   (222 contention) are **independent** hazards — a narrow leg on 222 does not slow the agent.
2. **`test_nixl_desc_geometry.py` cannot prove anything here**: swap tree 196f/6p, parent tree
   200f/1p, both with `NIXL is not available`. Drop it from the "would prove 88b" list; add it to the
   NIXL/GPU validation list. Full analysis in `swap88b-plan.md`.

## State (re-verified from git this session, not from the doc)

| | |
|---|---|
| Tracker | **95 / 317** checked, 222 unchecked (45 deferred ⇒ 177 non-deferred pending) |
| `origin` = jetson = Mac | **`88e00426d`** — asserted three ways after each push |
| Landed this session | 97 `2a61f060d3`→`37d0e1eef`, 98 `c6c33f2b1f`→`88e00426d` |
| **Ledger durability** | **DONE.** `.scratch/` is now on `origin` as orphan branch **`mitaka/backport-ledger`** (deliberately not a descendant of `mitaka/backport`, so the ported branch stays PR-clean) + a tarball mirror `jetson-222:~/dev/scratch-ledger.tgz`. **Run `.scratch/official-port-sweep-1/ledger-sync.sh "msg"` after every push+bookkeep** — it rsyncs, commits, pushes, asserts the tip, mirrors, and asserts the sha. |
| Swap worktree | `jetson-222:~/dev/vllm-swap88`, `swap/qwen-88` @ base `e16d574bb`, **0 commits ahead**, 39 staged, **3 unmerged** |
| Production | `:8000` = 200 throughout; only `qwen38-flash-next` running; no stray containers |

## Lane A — the grind (worker dispatch is working again)

Children survive now that the cluster is idle. The standing rules moved into a **versioned brief**:
`.scratch/official-port-sweep-1/worker-brief.md`. Dispatch = `worker`, `async: true`, ~10-line task
pointing at that file + {item no., official sha, subject, file list, **base tip to assert**}. Orchestrator
verifies independently (commit count, per-file changed-line md5, silent-loss), pushes, bookkeeps, syncs.

Next items (strict oldest-first, skipping the 45 in `swap-dependent.txt`):
**99 `1b9539d37c`** [AutoRound][XPU] MXFP8 MoE → 100 `5bfd76372d` Renderer shutdown → 101 `399247cc88`
MiniCPM-o → 102 `28bf75c9a9` → 103 `699e180df4` → 104 `d8de4ae322`. First `CONFLICT` forecast is
**105 `eeb549a74d`** *Move engine/protocol.py out of the openai folder* (hot: `vllm/reasoning/hy_v4*`) —
run the five verify-before-escalating checks before writing any decision card.

Housekeeping item for whoever's patient: `~/dev/vllm/.git/AUTO_MERGE` is stale (predates both picks, is
not pick state — `unmerged=0`), plus untracked `.cargo-home/`, `i55_result.txt`. Untouched so far.

## Lane B — the swap: 88a DONE, 3 test files left

- **88a (9 `qwen4_exp` files)**: resolved and runtime-verified — nvidia+infra **16/16** imports,
  amd-only **6/6**, GPU hidden, inside `mitakad/vllm:…d4d703c`. Details and per-hunk justification in
  `swap88b-plan.md`. The two load-bearing findings: `amd/ple_layer.py` is official's file *provably*
  (every wtdcode line is the same logic re-expressed), and in `nvidia/ple_layer.py` **official's
  subclass-level `forward()` must NOT be taken** — it silently clobbers `PleOffloadLayer.forward`, which
  is what routes the GPU worker to the CPU-offload IPC buffer. Official's `forward` body was folded into
  `forward_impl` with an `is_offload_process()` branch.
- **Test files 4/7 done** (2 take-theirs, `test_kv_cache_utils` union + 6 re-applied tests, nixl all-theirs
  as a unit). Remaining: `tests/models/qwen4_exp/test_ple.py` (7 hunks, ours 140/theirs 55),
  `tests/models/qwen4_exp/test_config.py` (6 hunks, ours 331/theirs 38),
  `tests/v1/core/test_contiguous_kv_packing.py` (5 hunks incl. one **220 vs 222** showdown — this is the
  one likely to need a real decision, since ours rewrites the packing tests for our allocator and official
  rewrites them for its generic packer).
- **Then**: narrow CPU leg over what can actually run on this box (`test_kv_cache_utils`,
  `tests/models/qwen4_exp/*`, `test_contiguous_kv_packing`; **not** nixl) with a parent-tree base compare;
  rebase `swap/qwen-88` onto the moving tip; ONE `-x` commit; push as **branch only, never merge**;
  hand the user `gpu-validation-recipe.md`. Never call item 88 validated on CPU evidence.

## Re-grill candidate (do not bury this)

88b restored `_get_kv_cache_groups_uniform_groups` / `group_and_unify_kv_cache_specs` (L1) **and** took
official's `hf_config.model_type == "deepseek_v4"` eagle gate alongside our `spec.model_version`
predicate. The 5 restored `test_kv_cache_utils` tests exercise exactly that area. If any of them fails on
the CPU leg, that is Fork #3's stated "it forces changing a block-accounting predicate" trigger → STOP and
re-grill, do not delete or patch the test.

## Gates still with the user

1. Push `swap/qwen-88` to `origin` as a branch once it has a commit (nodes 2–5 need it to fetch; nothing
   merges into `mitaka/backport`). Recommended, not yet done.
2. GPU validation window (TP-only, 4 nodes) — held until the swap is resolution-complete + CPU-clean.
3. Whether the swap ever merges into `mitaka/backport`.

## Standing hazards

`+=` inside a heredoc through the shell tool gets mangled by the Hypa wrapper — write scripts to a file
and `scp` them instead. `git add` destroys stage 2/3 (compare against `git show <upstream>:<path>`, not
`:3:`). Silent-loss scans catch real deletions (5 tests here) — always run them, even on clean merges.
`PleOffloadLayer.__init_subclass__` wraps subclass `__init__`, so `co_varnames` probes read the wrapper.

## Dispatch reliability note (after the item-99 child died)

Item 99's `worker` child **terminated with no output** after ~178k tokens. It died before touching the
tree (`~/dev/vllm` verified still `88e00426d0`, 0 dirty, no sequencer), so nothing was salvageable and
nothing needed cleanup. Items 97 and 98 succeeded in the same window, so this is 2 successes / 1 death —
not yet the two-deaths trigger, but the pattern is that a `worker` runs as a **fork of this orchestrator's
context**, and by now that fork is enormous. Redispatch with **`context: fresh`** (the brief is a file, so
nothing is lost) and re-check `git log 88e00426d..HEAD | wc -l` before adopting any report.

**If a child lands a pick and this session has already ended:** the commit will sit unpushed on
`jetson-222:~/dev/vllm`. The next session must, before anything else: read
`git -C ~/dev/vllm log --oneline origin/mitaka/backport..HEAD`, verify faithfulness + silent-loss per
`worker-brief.md`, then `git fetch jetson-222:~/dev/vllm mitaka/backport` → `merge --ff-only` →
`git push -q origin mitaka/backport` → assert `ls-remote` == jetson tip → append the `outcomes.log.md`
entry → tick the tracker → `ledger-sync.sh`. An unpushed, unbookkept landing is the item-80 gap.

## PAUSED at user instruction (2026-09-06, after item 99) — resume only when told

Stop point, all verified: grind `96/317`, tip **`4529b9645`** == origin == jetson == Mac, no unpushed
commit, no in-flight sequencer in `~/dev/vllm`, no worker children left running, only the production
container up (`:8000` = 200), ledger pushed + mirrored.
**Swap worktree intentionally left mid-pick**: `swap/qwen-88` @ `e16d574bb`, 0 commits ahead, 39 staged,
**3 unmerged** (`test_ple.py`, `test_config.py`, `test_contiguous_kv_packing.py`). Do NOT `cherry-pick
--abort` — it cannot restore a `-n` pick cleanly (documented: leaves 40+ staged/unmerged entries).
On resume, grind item **100 `5bfd76372d`** "[Renderer] Shutdown the renderer properly (#52124)" with base
tip `4529b9645`, `context: fresh`, brief at `worker-brief.md`; swap resumes at those 3 test files.
