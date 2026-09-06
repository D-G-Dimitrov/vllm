# Continuation plan — grind + item-88 swap (2026-09-06, post-handoff)

Derived from **ground truth**, not from the handoff (per skill Verification #3 / handoff rule 7).
Handoff: `/var/folders/.../handoff-2026-09-06-port-grind-and-swap.md`. Procedure: skill
`official-port-grind-loop`. Plan is a *proposal* — the §6 gates are the user's to call.

## 1. Verified state (all re-measured this session)

| check | result |
|---|---|
| `ls-remote origin` / jetson `~/dev/vllm` / Mac tip | **`eef9f770c3` all three** — in sync, 0 unclean |
| Tracker | 93 checked / 224 unchecked / 317 total; checked∩unchecked = 0 |
| Ledger audit (`comm -23 checked outcomes`) | **empty** — every landed item has an `outcomes.log.md` entry |
| Deferred pending (∩ `swap-dependent.txt`) | 45 → **179 non-deferred pending** |
| Swap worktree `~/dev/vllm-swap88` | branch `swap/qwen-88`, HEAD `e16d574bb` = base, **0 commits ahead**, **16 unmerged** (9 model + 7 test), 27 staged-resolved, pick state = `MERGE_MSG`+`AUTO_MERGE`, no `CHERRY_PICK_HEAD` (expected for `-n`) |
| Production | `:8000/health` = **200**; no stray container (`swapnarrow` gone) |
| **NEW — jetson load** | `0.00` → `0.12` over the session; **serving is idle** |
| **NEW — child liveness** | a `scout` child completed a trivial ssh probe cleanly → the two-deaths trigger for orchestrator-direct mode **has cleared**; worker dispatch is viable again |

## 2. New measurement: 88a is smaller and more mechanical than the ticket assumed

Per-file stage-2 (ours) vs stage-3 (official) divergence on the 9 conflicted `qwen4_exp/**` files:

| file | ours-only | theirs-only | resolution class |
|---|---|---|---|
| `amd/model.py` | **0** | 17 | **lossless-take-THEIRS** (ours ⊆ official, order-preserving) |
| `common/ple.py` | **0** | 25 | **lossless-take-THEIRS** |
| `config.py` | 8 | **0** | **lossless-take-OURS** (official adds nothing) |
| `nvidia/model_state.py` | 4 | 9 | hunk-level union |
| `nvidia/model.py` | 5 | 19 | hunk-level union |
| `amd/mtp.py` | 18 | 10 | hunk-level union |
| `nvidia/mtp.py` | 23 | 11 | hunk-level union |
| `amd/ple_layer.py` | 83 | 112 | hunk-level union |
| `nvidia/ple_layer.py` | 174 | 188 | hunk-level union (largest, do last) |

Ticket 04 said "take official's implementation, re-apply ~315 lines". Measured, that is **3 take-side
files + 6 unions**, none of them more than 188+174 divergent lines. The prohibition on
`checkout --theirs` (skill Pitfall, and 88b's rule) is about **shared-infra** files; here it is permitted
*only* after re-proving containment with `comm -23 <(sort :2) <(sort :3)` empty, same test as 88b STEP 2.

Test-file surface (for Phase 2): `test_gpu_autoregressive_speculator` 1/3 and `test_gpu_model_runner_v2`
1/6 are near-trivial; then `test_nixl_desc_geometry` 20/56, `test_ple` 129/44, `test_config` 323/30,
`test_kv_cache_utils` 605/63, `test_contiguous_kv_packing` 209/204.

## 3. New measurement: continuing the grind costs the swap almost nothing

6 commits have landed on `mitaka/backport` since the swap's base `e16d574bb`. Their file intersection with
the swap's surface is **3 files** — `vllm/config/vllm.py`, `deepseek_v32/attention.py`,
`v1/kv_offload/base.py` — **none of them** in the 16 conflicted or 10 resolved sets. So the deferral list
is working as designed: grinding now does **not** create re-resolution debt for the swap, and the swap can
be replayed onto a much later tip almost for free. This is the justification for running both lanes at once.

## 4. Sequencing (recommended)

Two lanes, **one writer per worktree**, orchestrator sole pusher and sole `.scratch/` writer:

- **Lane B — orchestrator-direct, `~/dev/vllm-swap88`**: 88a, then the 7 test files. Chosen because 88a is
  the judgment-heavy work whose rules (hunk-level union, D1/D2, never pick a side on allocator predicates)
  are already loaded here; a fresh child would need to re-absorb ~700 lines of plan to do it safely.
- **Lane A — ONE sequential `worker` child, `~/dev/vllm`**: grind items **97 → 104** (all `OK`-forecast;
  first `CONFLICT` forecast is item 105 `eeb549a74d` *Move engine/protocol.py out openai folder*). Child
  picks + validates CPU-only and **reports; it never pushes**. Orchestrator pushes + bookkeeps each landing
  atomically (skill step 4) between its own swap steps. Sequential only — never two children in `~/dev/vllm`.
- Never a `cd`/`git -C` across the two trees.

## 5. Phases

### Phase 0 — ledger durability (do first; it is the only single-copy artifact)
`.scratch/` is **untracked and not gitignored** → the ledger, tracker, `swap-dependent.txt` and every plan
exist on one Mac only. Nothing else in this plan matters if that disk goes. Recommendation in §6.1.

### Phase 1 — 88a (orchestrator, swap worktree)
1. Re-assert preconditions from git, not from this doc: HEAD `e16d574bb`, 16 unmerged, 0 commits ahead,
   `MERGE_MSG` present. Abort criteria: anything else → stop and re-derive.
2. The 3 take-side files (2 theirs, 1 ours) **after** re-proving containment per file.
3. The 6 unions smallest→largest. Per file, unchanged discipline: read both sides; hunk-by-hunk with the
   governing rule *preserve wtdcode augmentation **and** add official's changes*; assert-before-write in a
   python heredoc (the assertions gate the write); `compile(open(f).read(), f, "exec")` (never `py_compile`);
   symbol-**NAME** silent-loss scan with the before-side from `git show HEAD:FILE`; stage; move on.
4. **Runtime-import gate**: the 9 `qwen4_exp` modules **+** the 10 already-resolved 88b modules, inside
   `mitakad/vllm:…d4d703c`, `PYTHONPATH` on the worktree, `CUDA_VISIBLE_DEVICES=""`. Target **19/19**.
   `:8000/health` before and after.

### Phase 2 — test files, then the CPU leg once (not twice)
5. Resolve the 7 test files last (ticket 05 step 5) — they must describe what 88a+88b actually settled on.
   Rule for collisions: a test encoding **our** allocator's expectation is never deleted; a test encoding
   official's new planner expectation that *fails* is a **re-grill signal, not a delete candidate**
   (that is Fork #3's stated revisit trigger).
6. **Now** run the narrow CPU leg — the 4 suites that would actually prove 88b
   (`test_kv_cache_utils`, `test_contiguous_kv_packing`, `test_nixl_desc_geometry`,
   `tests/models/qwen4_exp/*`) exist and import only after step 5. Guards: no mooncake/flexkv/moriio,
   Ray disabled, `docker run -d` with output into the mounted repo, poll on `docker stats` CPU **+ log
   mtime**, `:8000/health` before/after, and any failure is judged **only** as an identical fail-set vs a
   parent-tree base compare at `e16d574bb`. Known-base families in the skill and `map.md` are never escalated.
7. **Rebase `swap/qwen-88` onto the then-current `mitaka/backport` tip** (append-only protects
   `mitaka/backport`, not the quarantined branch) so the evidence and the GPU run apply to the tree that
   will actually merge. Expect the 3 §3 files only.
8. Commit as **ONE** commit with the `-x` upstream line → `git push origin swap/qwen-88` **branch only, never
   merge**. Bookkeep: item 88 stays **unchecked**; record the swap state in `map.md` + ticket 05.

### Phase 3 — grind resumes continuously
Items 97→, strict oldest-first, skipping the 45 deferred. Item 105 `eeb549a74d` (CONFLICT forecast,
`vllm/reasoning/hy_v4*` hot) gets the full step-3b five-check verification **before** any decision card.

### Phase 4 — item 315 (GLM-5.3-Flash) probe, jointly planned
Fresh branch `swap/glm-315` + worktree, same probe→measure→resolve pattern. D2's evidence (upstream
converges on our `block_stride` at 315) is why 88 and 315 are one plan, not two.

### Phase 5 — nodes + GPU window (user)
Seed nodes 2–5 by `git fetch` + worktree from `origin/swap/qwen-88` (4× fetch, no image rebuild), then the
TP-only 4-node eval of Qwen3.8-Flash-Next-FP8 and GLM-5.3-Flash-W4A16 per `gpu-validation-recipe.md`.
**Item 88 is never reported validated on CPU evidence.**

## 6. Gates — the user's to decide, not mine

1. **Ledger durability.** Recommend: commit `.scratch/official-port-sweep-1/` to a dedicated branch
   (e.g. `mitaka/backport-ledger`) pushed to `origin` so it is off-Mac, and keep it out of
   `mitaka/backport` so the ported branch stays clean for PRs. Alternative: tarball mirror to
   `jetson-222:~/dev/`. Do both cheaply?
2. **Lane allocation.** Recommend §4 (orchestrator on the swap + one sequential grind child). Alternative:
   orchestrator-direct on both, sequentially (slower, zero delegation risk).
3. **CPU leg placement.** Recommend once, after the test files resolve (Phase 2 step 6) — not a rerun now.
4. **Push `swap/qwen-88` to `origin`** as a branch once it has a commit (needed before nodes 2–5 can fetch).
5. **GPU window / node seeding** — per ticket 05, not to be requested before the swap is
   resolution-complete + CPU-clean.

## 7. Standing hazards carried forward

- The model **serving this session is `Qwen/Qwen3.8-Flash-Next-FP8` on jetson-222** — the same family the
  swap targets. Any test leg that competes with it degrades the agent *and* production. Keep legs narrow.
- GPU watch list (no CPU signal, real behavior deltas accepted deliberately): item 95's non-dcp-gated
  padding-row Q-norm; `has_mamba_layers` via `iter_layer_specs`; `ple_groups` per-layer selection;
  `mamba_utils` invariant fatal→warning (D1); `block_stride` kept as ours (D2); nixl `_layer_specs`
  leaf-vs-wrapper (L3); `mamba_utils` `zip()` truncation.
- Never put an imperative action in a `steer` derived from a status snapshot; observation + question only.
- Push = fetch jetson → `merge --ff-only` → push → **assert `ls-remote` == jetson tip**; then bookkeep.
