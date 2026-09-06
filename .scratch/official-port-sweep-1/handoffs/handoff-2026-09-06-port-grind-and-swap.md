# Handoff — official→mitaka/backport port grind + Qwen/GLM model swap

**Generated:** 2026-09-06 ~20:25 local (jetson-222 clock ~19:2x–20:2x, runs ahead — never infer staleness from it)
**Prior handoff (still valid background):** `/tmp/vllm-backport-handoff-2026-09-05.md`
**Read first, in this order:**
1. Skill `official-port-grind-loop` (global) — execution modes, briefs, gate, push path, hazards. **It is the authoritative procedure.**
2. `.scratch/official-port-sweep-1/swap88b-plan.md` — swap plan + full RESOLUTION LOG + orchestrator D1/D2 decisions + the 88b review verdict.
3. `.scratch/official-port-sweep-1/gpu-validation-recipe.md` — deferred GPU work, TP-only, node inventory.
4. `.scratch/official-port-sweep-1/issues/03-pr-grind.md` (tracker), `outcomes.log.md` (ledger, last entry = 95), `issues/05-model-swap-qwen-glm.md` (swap ticket), `swap-dependent.txt` (45 deferred SHAs).

All paths above are relative to **`/Users/mitaka/Projects/PyCharm/vllm-mitaka`** (Mac orchestrator clone). Note the cwd in the session prompt is `…/PyCharm/vllm-backport` — a **different** directory; the live repo for this work is **`vllm-mitaka`**.

---

## Mission (standing order — do not re-ask for permission between rounds)

Port all **317** official PRs in `c01b50e390..d4d703caf9` into `mitaka/backport`, **strictly oldest-first**, each individually `git cherry-pick -x`'d or skipped with a recorded reason. Grind continuously; halt **only** for a decision that changes default-path behavior for the three protected families: **DSV4 (`deepseek_v4`), `qwen4_exp` (Qwen3.8-Flash-Next), GLM-5.3-Flash (`glm5next`)**. File-touch is *not* a stop condition.

## State right now

| | |
|---|---|
| Tracker | **93 / 317 checked**, 224 unchecked, **179 non-deferred pending** |
| `origin` = jetson = Mac | **`eef9f770c`** (item 95) — in sync |
| Next pending | item 88 `e126687a9a` (**the swap itself**), then `2a61f060d3`, `c6c33f2b1f`, `1b9539d37c`, `5bfd76372d`, `399247cc88` |
| Swap tree | `jetson-222:~/dev/vllm-swap88`, branch `swap/qwen-88`, **HEAD `e16d574bb`, 0 commits ahead, 16 files unmerged** (cherry-pick `-n` in flight — **do not abort**) |
| Running on jetson | container `swapnarrow` = CPU test leg over 13 targeted suites → `/tmp/swapout/narrow.log` (look for `NARROW_DONE` + summary). Production `qwen38-flash-next` on **:8000** is sacred. |

**Tracker parse is asymmetric** (bit me twice): checked `- [x]` → `awk '{print $3}'`; unchecked `- [ ]` → `awk '{print $4}'` (the bracket splits). Audit by **set membership**, never line count: `comm -23 <(checked) <(outcomes SHAs)` must be empty.

## Lane A — the grind (orchestrator-direct for now)

Per item: pick on jetson → validate → **push** → bookkeep. Details in the skill; the non-negotiables:

- **Push path.** Picks exist only on jetson, which **cannot push** (HTTPS origin, no creds). Mac is a mirror, so a naive Mac push **silently no-ops with exit 0**. Correct: `git fetch jetson-222:~/dev/vllm mitaka/backport` → `git merge --ff-only FETCH_HEAD` → `git push -q origin mitaka/backport` → **assert `ls-remote` == jetson tip**.
- **Bookkeeping is atomic with the push**: append entry to `outcomes.log.md` **and** tick the tracker line.
- **Faithfulness.** Commit-level `patch-id` is neither sufficient nor always applicable — a contextual UNION legitimately mismatches (item 92). The discriminating test is **per-file sorted `+`/`-` line-set equality** vs the upstream commit.
- **Silent-loss scan is mandatory on every resolved file**, including clean auto-merges (git applies incoming deletions with no marker): compare `^(def|class)` **names** in `git show HEAD:FILE` vs the working file.
- Known-base CPU failure families are listed in the skill — never escalate those; accept only an **identical fail-set vs the item's parent**.

**Dispatch mode:** subagent children are being **terminated by the runner** (model server contending with production). Two deaths in one window is the documented trigger → **work orchestrator-direct** until serving load drops. Async children write nothing until they finish, so `status view=transcript` shows empty while they work; a dropped completion notification is recoverable from `async-subagent-results/<runId>.json`.

## Lane B — the model swap (item 88, ratified A′)

`e126687a9a` = official Qwen3.8-Flash-Next = **88a** (9 `qwen4_exp/**` model files) + **88b** (shared KV infra). Item **315** `98ed0856f3` (GLM-5.3-Flash) must be planned **jointly** — upstream converges on *our* `block_stride` rule there, so resolving D2 any other way would force unwinding later. 45 items are deferred (`swap-dependent.txt`) until the swap merges; item 88 stays unchecked while quarantined.

**88b is DONE** — 10 files resolved, staged, silent-loss clean, **10/10 runtime-import clean** inside `mitakad/vllm:…d4d703c` with `PYTHONPATH` on the worktree. Two git-stolen blocks were restored (`_get_kv_cache_groups_uniform_groups`, 87 lines; the `round_up` import). Decisions **D1** (mamba fatal assert → official's bounded loop + warning; same author revised his own code) and **D2** (keep our generic `block_stride`) are in the plan file. Review verdict: **conditional pass** — the alias-inversion check is clean (nothing defines `prefix_cacheable` except the delegating base; `CircularBufferSpec` and `KpoolTailSpec` both override the **canonical** predicate to `False`).

### Immediate next actions

1. **Decide the CPU-coverage question, don't blindly rerun it.** The targeted CPU leg was attempted **twice and abandoned both times**: it stalls after ~40 tests with a run of `E` marks, and the first attempt was found to have spawned **Ray inside the container** while your model was serving. `/tmp/swapout/narrow.log` (13 suites) and `/tmp/swapout/new.log` (36 suites) are on jetson if you want the tails, but neither reached a summary. The container is removed and `:8000` is healthy. **Do not run broad CPU suites on jetson-222 while it serves.** Evidence for 88b currently rests on the **10/10 runtime-import gate** + the silent-loss scans + the predicate override-map review, which is real but is *not* test coverage — and the 4 conflicted suites that would actually prove it (`test_kv_cache_utils`, `test_contiguous_kv_packing`, `test_nixl_desc_geometry`, plus `tests/models/qwen4_exp/*`) are exactly the ones **88a** unblocks. So: resolve the test files first (step 3), then run CPU coverage either when serving is idle or on a seeded second node.
2. **88a**: resolve the 9 `vllm/models/qwen4_exp/**` files on `swap/qwen-88`. These are the actual model implementation — expect the ~315 lines of wtdcode augmentation to need **re-applying on top of** official's implementation, not choosing a side. Same discipline: conflict-by-conflict, read both sides, assert-before-write in a python heredoc, silent-loss scan, runtime-import gate.
3. Then the **7 test files**, exactly: `tests/models/qwen4_exp/test_config.py`, `tests/models/qwen4_exp/test_ple.py`, `tests/v1/core/test_contiguous_kv_packing.py`, `tests/v1/core/test_kv_cache_utils.py`, `tests/v1/kv_connector/unit/test_nixl_desc_geometry.py`, `tests/v1/worker/test_gpu_autoregressive_speculator.py`, `tests/v1/worker/test_gpu_model_runner_v2.py`. (4 of these are the suites that would actually *prove* 88b — `test_kv_cache_utils`, `test_contiguous_kv_packing`, `test_nixl_desc_geometry` — so resolving them lets the CPU leg be rerun at full coverage.)
4. **Commit the whole swap as ONE commit** (the plan is one PR = one commit; 0 commits are ahead so far, so this stays a single commit) with the `-x` upstream line, then `git push origin swap/qwen-88` **as a branch only — never merge to `mitaka/backport`.**
5. Hand the user `gpu-validation-recipe.md`. **Do not report item 88 as validated on CPU evidence.**
6. Then resume the grind: item 88 stays unchecked; pick `2a61f060d3` next (`2a61f060d3` is XPU → likely trivial/escalate-free), and skip everything in `swap-dependent.txt`.
7. Repeat probe → resolve → review for item **315** on a fresh `swap/glm-315` branch, planned jointly with 88.

## Hard constraints (violating these caused real damage before)

- **All git/docker on `ssh jetson-222 'cd ~/dev/vllm && …'`. Never local git/docker. Never touch the GPU** (`-e CUDA_VISIBLE_DEVICES=""` always). Production serving on **:8000 ONLY** (`:8001` has no listener). Check `curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health` before and after any container.
- **One writer per worktree.** Never `cd`+git in `~/dev/vllm-swap88` from a grind brief or vice versa.
- **TP only, never PP** (user constraint). **No image rebuild needed** — code ships by bind mount + `PYTHONPATH=/work` + copying the 8 `.so` from the host image.
- Append-only history: never rebase. Orchestrator is the **sole pusher** and sole `.scratch/` writer.
- Do **not** seed the other 4 Jetsons yet — `swap/qwen-88` has no commit, so there is nothing to fetch. Node inventory + `.so` bundle (`jetson-222:~/dev/vllm-so-d4d703c.tgz`, 338M, sha256 `3b2abe7e…`) are in the GPU recipe.

## Harness traps that cost time this session

- **Never put an imperative action in a `steer` based on a status snapshot** — a nested child's commits land in a result blob the parent cannot see, so "you have not committed yet" can be false, and a child that acts on it can break an invariant. Correct steer = observation + question, forbid mutating ops. (A worker correctly pushed back on exactly this.)
- Broad CPU test sets can spawn **Ray** inside the container and stall 10+ min while contending with production. Narrow the set to suites that import what you changed; drop mooncake/flexkv/moriio.
- Slow vs hung = `docker stats` CPU **+ log mtime**, not the progress bar.
- Container-created `__pycache__` is root-owned → non-sudo `rm` **silently no-ops** while looking successful; use `sudo -n rm -rf`.
- `git cherry-pick --abort` can fail mid `-n` leaving unmerged state with **no `CHERRY_PICK_HEAD`** → recover with `git reset --hard HEAD`.
- Invariant checks must be phrased as **"no NEW occurrence vs HEAD"**, not "zero occurrences" — HEAD often already contains the shape you're guarding against.
- Use `compile(open(f).read(), f, "exec")`, not `py_compile` (`__pycache__` Errno 13 mimics a syntax error). Stage runner scripts and **verify non-empty in a separate command**; `docker run -d` + redirect into a mounted dir (a backgrounded `docker run` dies with the ssh session).

## Open items for the user (do not decide unilaterally)

- **`.scratch/` is UNTRACKED** (`git status` shows `?? .scratch/`), so the ledger — `outcomes.log.md`, the tracker, `swap-dependent.txt`, this handoff's referenced plans — exists **only on this Mac**, in no remote and on no Jetson. It is the sole record of what has actually been ported and why. Consider committing it (or mirroring it) before the sweep gets much further; `origin` carries the commits but none of the reasoning.
- GPU validation window (deferred by user until swap is CPU-complete + oracle-passed).
- Whether the swap merges into `mitaka/backport` at all — currently quarantined by design.
- Item 95 landed with **zero CPU coverage** (all 67 tests skip behind CUDA fp8/SM89+); its non-dcp-gated padding-row Q-norm change is on the GPU watch list.

## Suggested skills

- **`official-port-grind-loop`** (global) — invoke before touching either lane; it is the procedure.
- **`subagent-driven-development`** / **`dispatching-parallel-agents`** (superpowers) — only when resuming delegation; re-verify children are surviving first.
- **`verification-before-completion`** — this task's failure mode is *asserting* validation that didn't happen (items 83–86 were voided that way).
- **`diagnosing-bugs`** / **`systematic-debugging`** — for conflict semantics when blame coverage is required.
- **Context7 MCP** (per `AGENTS.md`) — for upstream/doc questions such as how official intends `participates_in_prefix_caching` vs `prefix_cacheable` to coexist with out-of-tree connectors. Use this before web search for library/API questions. **`research`** only for broader multi-source investigation.
- **`handoff`** — refresh this doc at lane boundaries; it drifts fast.

## Durable facts worth keeping (already partly in memory)

Async children can be terminated while the TUI still shows a stale `Async runs 1/2 · 0 tokens` with an empty fleet; a completed child's notification can be dropped but its result is at `async-subagent-results/<runId>.json`. `prefix_cacheable` was **deleted from the official tree at the cutoff** (`d4d703caf9`) — only the delegating base property remains, plus a docstring begging downstream to switch to the canonical predicate.
