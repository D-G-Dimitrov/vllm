# Model swap: Qwen3.8-Flash-Next (item 88) + GLM-5.3-Flash (item 315)

Label: wayfinder:task
Type: task (HITL for the swap decisions, AFK for mechanical steps)
Ratified: 2026-09-06, option A′ — see map.md Decision log "MODEL-SWAP RATIFICATION / Fork #3"

## Question

How do we land official's Qwen3.8-Flash-Next (#53896, grind item 88) and GLM-5.3-Flash (#53906, grind item 315) implementations onto a tree that already carries wtdcode's versions of both — while preserving every line of wtdcode logic the product families depend on, and without breaking the other 45 pending items that touch the same file surface?

Oldest-first is **waived for these two items only**. Everything else in the sweep stays strictly oldest-first.

## Measured shape of item 88

Probe: branch off `e16d574bb`, `git cherry-pick -x -n e126687a9a`, measure, abort, delete branch.
Never move `mitaka/backport`. Repeat this probe pattern for item 315.

- 49 files merge clean, **29 conflict**.
- **Lossless-take-OURS (4)** — official content fully contained in ours, conflict is spurious:
  - `vllm/v1/core/single_type_kv_cache_manager.py` (2,094 official lines, 0 absent from ours; holds wtdcode's whole `KpoolTailManager` subclass)
  - `tests/models/qwen4_exp/test_qsa_reference.py`
  - `tests/v1/kv_connector/unit/test_tp_mapping.py`
  - `tests/models/qwen4_exp/test_qsa_amd.py`
- **88a — qwen4_exp model files (~315 wtdcode-only lines to preserve)**: `nvidia/ple_layer.py` 174, `amd/ple_layer.py` 83, `nvidia/mtp.py` 23, `amd/mtp.py` 18, `config.py` 8, `nvidia/model.py` 5, `nvidia/model_state.py` 4, `common/ple.py` (official adds 25), `amd/model.py` (official adds 17).
- **88b — shared KV/infra (high blast radius, affects DSV4 + GLM too)**: `kv_cache_utils.py` **918 ours-only** / 237 official-only, `gpu/model_runner.py` 148/14, `kv_cache_interface.py` 74/18, `single_type_kv_cache_manager.py` 135/0, `kv_cache_coordinator.py` 10/2, `platforms/interface.py` 15/1, `mamba_utils.py` 11/7, `model_executor/models/config.py` 0/8, `config/compilation.py` 1/1, `nixl/base_worker.py` 22/43.
- Test-file conflicts follow from the above: `test_kv_cache_utils` 605/63, `test_contiguous_kv_packing` 209/204, `qwen4_exp/test_config` 323/30, `test_ple` 129/44, plus nixl/tp_mapping/speculator/gpu_model_runner_v2.

## Procedure

1. **Land the lossless-ours 4 first** — mechanical, zero risk, shrinks the conflict set before any judgment work.
2. **88b before 88a.** Reconcile the shared KV/allocator surface first, because 88a's model files call into it. Rule for every hunk: **preserve** wtdcode's allocator predicates and block-accounting paths and *add* official's planner changes alongside. Never resolve 88b by choosing a side.
3. Fresh **oracle** pass over 88b as a whole (not per hunk) — it must return an unconditional pass on "zero behavior delta for DSV4 / qwen4_exp / GLM-5.3-Flash", per the auto-land gate. If it cannot, halt and present a card.
4. Then **88a**: take official's qwen4_exp implementation, re-apply the ~315 lines of wtdcode augmentation.
5. Resolve the test files last, against whatever 88a+88b settled on.
6. Commit as a contiguous range, push, bookkeep item 88 with the swap recorded (not as a plain pick).
7. Then items 176, 222, 230, 233, 310 should apply as ordinary picks — verify they do; that is the empirical proof the swap was shaped correctly.
8. Repeat the probe → 88b-style → swap pattern for item 315 (GLM), reusing this ticket. Their shared surface is `speculative.py`, `warmup/kernel_warmup.py`, `gpu_model_runner.py` / `gpu/model_runner.py` / `gpu_worker.py` — reconcile once, deliberately.

## Blocking / gates

- **GPU model-eval window is not scheduled.** Required before item 88 may be called validated: Qwen3.8-Flash-Next-FP8 and GLM-5.3-Flash-W4A16. The only GPU runs the sacred :8000/:8001 serving. CPU-only suites are necessary but NOT sufficient here.
- Stop conditions: any change to a wtdcode allocator predicate rather than preservation of it; any oracle conditional/fail on 88b; any fail-set that differs from the parent tree.

## Answer

(pending)

## USER CONSTRAINTS (2026-09-06) — change the validation surface

- **TP only, across all 4 nodes. NEVER PP.** PP is not acceptable operationally (costs more RAM than TP)
  and is broken in both official and the backport. Consequences:
  - The `pp_handler.broadcast` vs `propose` ordering hard flag in `gpu/model_runner.py` is **moot for
    validation** (ours' post-`propose` placement was kept and verified anyway, for upstream faithfulness).
  - Official's new fail-fast for Qwen4Exp N-gram PLE at `pipeline_parallel_size > 1`
    (`model_executor/models/config.py`) is **inert** in this deployment.
  - Validation must instead concentrate on TP-reachable paths: `slot_mapping_enabled` (CUDA illegal access
    on GLM kpool tail), KV group/block sizing, `tp_replicated` Mamba uniformity, kpool-tail prefix caching,
    PLE offload and MTP/spec-decode in TP.
- **Both protected models require all 4 nodes in TP** - so a validation run is a 4-node affair, and the branch
  must be present on all four (4x `git fetch` + worktree, not 4 image builds).
- **No image exists from github.com/D-G-Dimitrov/vllm and none is needed.** Host images present on jetson-222:
  `mitakad/vllm:0.29.0.dev0-...commit.d4d703c` (official @ cutoff, the sweep's CPU reference image),
  `mitakad/vllm:0.29.0rc2-...pre-release`, and wtdcode-backport images `0.11.3 / 0.11.1 / 0.10.0.wtdcode`.
  Production serving uses `vllm/vllm-openai:qwen38-flash-next`. Code is delivered by bind mount +
  `PYTHONPATH=/work` + the 8 `.so` copied from the host image - proven to import the resolved 88b files.
  Recipe: [../gpu-validation-recipe.md](../gpu-validation-recipe.md) (NOT YET DUE).
- **GPU validation is deferred by the user until the swap is resolution-complete + oracle-passed on CPU.**
  Do not ask for a window before then.
