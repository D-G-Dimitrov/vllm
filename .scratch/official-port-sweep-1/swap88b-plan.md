# swap88 RECONCILIATION PLAN — official e126687a9a (#53896) shared infra

Scope: `jetson-222:~/dev/vllm-swap88` only, branch `swap/qwen-88`. `~/dev/vllm` / `mitaka/backport` never read, never `git -C`'d, never cd'd.
HEAD before and after: `e16d574bb`. No commit, no push, no content edits to shared-infra files.

## STATE

- `git rev-parse --short=9 HEAD` → `e16d574bb`, tree clean before pick. ✔
- `git cherry-pick -x -n e126687a9a` → **exit 1, 29 conflicts** (as predicted). ✔
- Pick **LEFT IN PROGRESS**: 25 files still unmerged after STEP 2, `MERGE_MSG` present, HEAD unchanged.
  Note: git 2.43 does **not** write `CHERRY_PICK_HEAD` for `-n`; sequencer dir is absent. Resume/abort state lives in the
  index (unmerged entries) + `MERGE_MSG`. `git cherry-pick --abort` will NOT work here — clean up with
  `git checkout -f HEAD -- <paths> ; git reset --hard HEAD` style if ever needed.
- `git worktree list` confirms `/home/mitaka/dev/vllm [mitaka/backport]` is a *linked worktree of the same object DB*.
  Object-level writes from this pick are shared but additive (blob/tree only); no ref of `mitaka/backport` was touched.

## STEP 2 — containment re-verified, then resolved `--ours` (all 4 lossless)

| file | official_lines (`:3`) | ours (`:2`) | absent | verdict |
|---|---|---|---|---|
| `vllm/v1/core/single_type_kv_cache_manager.py` | 2094 | 2229 | **0** | resolved ours ✔ |
| `tests/models/qwen4_exp/test_qsa_reference.py` | 973 | 1004 | **0** | resolved ours ✔ (add/add, stages 2+3) |
| `tests/v1/kv_connector/unit/test_tp_mapping.py` | 315 | 331 | **0** | resolved ours ✔ |
| `tests/models/qwen4_exp/test_qsa_amd.py` | 297 | 309 | **0** | resolved ours ✔ (add/add, stages 2+3) |

`absent=0` for all four → containment holds, resolution permitted.
Post-check: 0 conflict markers, 0 unmerged index entries, all 4 staged.

**Structural bonus (stronger than line-multiset containment):** ours' stage-2 blob for
`single_type_kv_cache_manager.py` already contains *all* of official's additions — `CircularBufferSpec`
import (L22), the narrowed `_record_new_block_ids` predicate (L91-94, `and not isinstance(..., CircularBufferSpec)`),
`class CircularBufferManager(FullAttentionManager)` (L1119) and its registry entry (L2177-2179). So
`checkout --ours` dropped **nothing** official; the conflict existed only because official's new
`CircularBufferManager` was inserted where our `KpoolTailManager` sits. Our whole `KpoolTailManager`
subclass (GLM-5.3-Flash, 126 lines) is preserved. `KpoolTailSpec(SlidingWindowSpec)` and `CircularBufferSpec(AttentionSpec)`
are disjoint classes, so official's zeroing-predicate narrowing does not touch the kpool tail path.

## STEP 3 — per-file plan (metrics: `A`=ours-only lines vs official, `C`=official lines truly absent from ours, `LOST`=ours lines already silently gone from the working tree)

| file | A / C / LOST | official INTENT in this file | wtdcode-only (what official lacks) | INTERACT? | resolution (hunk-level) | HARD FLAG |
|---|---|---|---|---|---|---|
| `vllm/v1/core/kv_cache_utils.py` | 918 / 187 / **85** | Generalize `resolve_kv_cache_block_sizes` for hybrid-Mamba prefix caching (nested-spec iteration, `prefix_alignments` from `tokens_per_state`, `has_partial_mamba_group` → `cache_hit_alignment`); **replace** DSV4-only `group_and_unify_kv_cache_specs`+`_get_kv_cache_groups_uniform_groups` with generic `_get_packed_kv_cache_groups` (block-outermost contiguous packing); gate DSV4 eagle fallback on `hf_config.model_type=="deepseek_v4"` (`_is_deepseek_v4_eagle`); widen `_annotate_eagle_groups` to `iter_layer_specs` | whole GLM-5.3-Next path `_get_kv_cache_groups_glm5_next` (L1157) + `_glm5_next_tensor_layout`; whole CSA+linear path `_CSALinear*`, `_classify_csa_linear_specs`, `_get_csa_linear_cache_tuples`, `_get_csa_linear_mamba_group_count` (L2137), `_get_kv_cache_groups_csa_linear` (L2165), `_get_csa_linear_tensor_layout`; `_pp_balanced_mamba_group_count` (L1128); `group_and_unify_kv_cache_specs` + `_get_kv_cache_groups_uniform_groups`; `participates_in_prefix_caching` filter in `hashing_sizes`; DSV4 detect via `spec.model_version=="deepseek_v4"`; CSA tensor layout w/ explicit `num_blocks`/byte-offset math | **YES** — same functions, same hunks | **UNION, all 4 hunks:** `@731-738` **ours** (`participates_in_prefix_caching`); `@743-780` **ours' message text + official's new body** (`prefix_alignments`/`has_partial_mamba_group`/`cache_hit_alignment` — official's side is 32 lines, ours' is 5); `@1969-2351` **ours** (official side empty = pure deletion of our CSA/linear + DSV4 grouping block); `@2663-2690` **ours' 3 dispatch branches + official's comment**. Keep official's `_get_packed_kv_cache_groups` call at L2700 *after* our branches. **+ landmines L1/L2 below** | **YES** — official deletes DSV4 tuple packing, GLM5 grouping, CSA/linear group counts and PP-balanced mamba group count; and replaces our `spec.model_version` DSV4 predicate with a model-type gate |
| `vllm/v1/worker/gpu/model_runner.py` | 148 / 5 / 0 | Exclude only `CircularBufferSpec` from generic slot mapping; **move** `pp_handler.broadcast` before `propose`; collapse our PP-aware drafter gate into a flat `ValueError("... with pipeline parallel is not supported")`; drop `model_state.supports_mm_inputs` from the speculator gate | `KpoolTailSpec` in `slot_mapping_enabled` (CUDA-illegal-access guard for GLM-5.3-Flash); PLE offload lifecycle ×6 (`_setup_ple_offload`, `prepare_forward`, `release_outputs`×2, `signal_dummy_outputs`, `close`); `_pp_aux_hidden_state_layers` + `get_pp_indices` last-stage validation; `pp_handler.broadcast_draft` relay + `req_states.draft_tokens` scatter; `num_blocks=self.kv_cache_config.num_blocks` arg | **YES** at both hunks + the PP region | `@71-74` **ours** (`KpoolTailSpec` import); `@641-652` **ours** (`not isinstance(layer_spec, (CircularBufferSpec, KpoolTailSpec))` — union of both spec types). PP region: auto-merge already kept our post-`propose` placement; **verified no duplicate broadcast** (merged has exactly our 2 calls at L2083/L2097; official's pre-`propose` insert did not land) | **YES** — `slot_mapping_enabled` is a block-addressing predicate (wrong value = CUDA illegal access, not a clean failure); PP broadcast ordering is NCCL order-matching critical (official's placement + our relay deadlocks) |
| `vllm/v1/kv_cache_interface.py` | 74 / 13 / 0 | Rename `participates_in_prefix_caching` → `prefix_cacheable`; delete `KpoolTailSpec`; drop `storage_block_size` (storage-vs-kernel block view) and its uniformity key; replace `get_page_sizes`/`get_num_layer_tuples` with `get_max_layers_per_page_size`; add `tp_replicated` to Mamba uniformity; `has_mamba` via `iter_layer_specs`; drop `max_worker_kv_bytes_per_block` | `participates_in_prefix_caching` as canonical + `prefix_cacheable` as **deprecated alias** (docstring: out-of-tree connectors `getattr(spec,"prefix_cacheable",True)`, dropping it re-enables GLM kpool tail / DSV4 compressor ring as serveable prefix KV); `class KpoolTailSpec` (L881: 1-block/request, `participates_in_prefix_caching=False`); `storage_block_size` (L572/591/596/619); `real_page_size_bytes` (L446/928); `max_worker_kv_bytes_per_block` (L1301); `get_page_sizes`/`get_num_layer_tuples` (L1136/1139) | **YES** — the rename *is* the collision | **UNION, all 5 hunks:** `@154-177` **ours** (keeps canonical name **and** alias → official's new `.prefix_cacheable` call sites at kv_cache_utils L758 keep working through the alias; do **not** let official's `return True` at L173-177 co-define a second, unconditional `prefix_cacheable`); `@806-810` **ours**; `@1067-1075` **ours** (equivalent semantics); `@1134-1144` **UNION BOTH** — our `get_page_sizes`+`get_num_layer_tuples` **and** official's `get_max_layers_per_page_size`; `@1347-1361` theirs (equivalent `iter_layer_specs` form) | **YES** — take-theirs deletes `KpoolTailSpec` + `storage_block_size` + `max_worker_kv_bytes_per_block` and flips the prefix-cacheability predicate that gates whether scratch groups may be served as shared KV |
| `vllm/v1/core/single_type_kv_cache_manager.py` | 135 / **0** / 0 | Add `CircularBufferManager` + narrow `_record_new_block_ids` | `KpoolTailManager` (whole subclass) | no (already a subset) | **RESOLVED ours in STEP 2** — provably lossless; official's additions already present in our blob | no (ours preserves both managers) |
| `.../nixl/base_worker.py` | 22 / 43 / **12** | Track CSA scratch regions explicitly (`_scratch_region_indices`, populated L1301-1308, sorted L1307+) because a scratch page shares the address of the page it overlays; **unwrap `UniformTypeKVCacheSpecs` into per-layer specs** (`self._layer_specs`) for every connector predicate; SSM detect via `_is_ssm_spec(get_representative_spec_type(...))`; exempt CSA from `hnc_contiguous` and from `packed_storage` | `_is_csa_linear`-derived region selection via `np.flatnonzero(self._region_is_mla)`; group-level `_layer_specs` (wrapper-valued); **generic stride-based `block_stride`** (`physical_page_size if cache.ndim==1 else cache.stride(0)*element_size`); `_region_is_mla` + `_is_mla_region` (L302, still live) | **YES** — official keeps `self._is_csa_linear` (it was rebased on our CSA work) and edits the same predicates | `@159-169` **theirs** (`_scratch_region_indices` supersedes our `_region_is_mla` derivation); `@376-385` **theirs** (per-layer unwrap is a superset, keeps `tp_replicated`); `@643-649` **theirs** (pure add); `@1157-1160` **theirs** (pure add); `@1301-1308` **theirs** (pure add); **`@1220-1232` `block_stride` → OURS** (our rule is the superset: it already yields `stride(0)*element_size` for the CSA case official special-cases, and stays correct for any other packed/overlaid layout; official hardcodes `physical_page_size` otherwise) | **YES** — official's `block_stride` rewrite changes PD descriptor stride/page accounting for packed layouts (silent wrong-offset transfer, not a crash); and `_layer_specs` semantics changed silently (see L3) |
| `vllm/platforms/interface.py` | 15 / 1 / 0 | Support models with several Mamba state layouts: `max(spec.page_size_bytes for spec in model_cls.get_mamba_specs_from_config(...))` with the old `MambaSpec(...)` path as `else` | `_get_indexer_block_alignment` classmethod (L767) + its `attn_block_size` rounding at L930 (CUDA kpool paged-MQA indexer: `block_size` must be a multiple of `index_kpool * min(PAGED_MQA_PAGE_SIZES)`); `cache_dtype_str=cache_config.cache_dtype` pass-through | **NO** — share a file only; the single hunk is a bare comment line (our `get_mamba_specs_from_config` block auto-merged around it) | `@870-873` **theirs** (take official's comment line only). Net file = union; our indexer hook + `indexer_align` rounding are already intact (silent-loss = 0) | **YES if anyone resolves this file at file level to theirs** — that deletes the indexer block-size alignment (block accounting for GLM kpool). Not triggered by the hunk-level recommendation |
| `vllm/v1/worker/mamba_utils.py` | 11 / 7 / 0 | Make state copy robust: `if len(kv_caches) < len(state_copy_funcs): raise ValueError` then iterate `enumerate(state_copy_funcs)` indexing `kv_caches[i]`; delete both shape-equality asserts | `assert len(kv_caches) == len(mamba_spec.shapes)` at **two** sites — our guard that a layer's exposed states match its cache spec (catches CSA/multi-layout page-size mismatches) | **YES** — same loop body, and official's relaxation may be *required* by Qwen4Exp's multi-layout states | `@991-1006` **UNION, official's control flow as the hard error** + our invariant retained non-fatally (do **not** keep a fatal `==` assert here — if Qwen4Exp legitimately exposes more tensors than `mamba_spec.shapes`, ours crashes the new model at load). `@1371-1377` **theirs** (our assert here duplicates the one above; the adjacent `zip(kv_caches, state_copy_funcs)` truncation is the real risk) | **YES** — this is a mamba state-copy (block data movement) guard; official *removes* it in both places |
| `vllm/v1/core/kv_cache_coordinator.py` | 10 / 2 / 0 | Same rename inside the block-size divisibility loop and the fine-grained prefix-hit loop | `participates_in_prefix_caching` + the comment explaining why GLM-5.3-Flash kpool tail groups are skipped in hit lookup ("their blocks are per-request scratch, never shareable… their slot in the per-group hit tuple stays empty") | **Naming only** — identical semantics *iff* the interface union keeps our canonical name | `@609-613` **ours**; `@685-694` **ours** (both hunks: keep our predicate name + comments) | **YES** — this is the group-count / prefix-hit-lookup path. If the interface alias or the canonical name is lost, kpool tail and DSV4 ring groups silently re-enter prefix hit lookup → wrong cache hits served, no crash |
| `vllm/model_executor/models/config.py` | 0 / 8 / 0 | Fail fast for Qwen4Exp N-gram PLE with `pipeline_parallel_size > 1` (non-first ranks don't get raw `input_ids`) | nothing (A=0 — ours fully contained in official) | **NO new constraint**: we already raise the identical error at `vllm/models/qwen4_exp/nvidia/model_state.py:47-50`; official only moves it earlier, before weight loading | `@877-887` **theirs** (pure addition) | no |
| `vllm/config/compilation.py` | 1 / 1 / 0 | Register `vllm::qwen4_exp_compute_ple_ngram_ids` in the custom-op name list | `vllm::sparse_attn_indexer_kpool` (survived outside the markers) | **NO** — adjacent list entries | `@771-774` **theirs** (pure addition; result is the union of both op names) | no |

## HIDDEN LANDMINES (already applied by the auto-merge, no conflict markers — resolving the visible hunks is NOT enough)

Def-level scan (`comm` on `def`/`class` names: stage2 vs merged tree) + line-level scan over all 10 files found exactly three issues;
no official definition was silently lost anywhere.

- **L1 — silently deleted wtdcode function (DSV4 breaks loudly at dispatch).** `def _get_kv_cache_groups_uniform_groups`
  exists in stage2 `kv_cache_utils.py:2345-2431` and is **gone** from the merged tree, because base had it, official deleted it,
  and ours didn't touch those lines → git took the deletion silently. Its **caller survives** on ours' side of hunk
  `@2663-2690` (`kv_cache_utils.py:2669`). Any DSV4 model → `NameError`.
  *Action:* restore stage2 lines **2345-2431** verbatim when resolving hunk 3/4. 85 ours lines vanished in this file, all in this body.
- **L2 — silently removed import needed by the restored function.** Merged `kv_cache_utils.py:19` is official's
  `from vllm.utils.math_utils import cdiv`; ours had `cdiv, round_up`, and the restored body uses `round_up` (stage2:2382).
  *Action:* re-add `round_up` to that import. (`KpoolTailSpec` L28, `SlidingWindowMLASpec` L36, `defaultdict` L9 survived.)
- **L3 — silent semantic change to nixl connector predicates (needs a test, no marker).** `_layer_specs` was auto-merged to
  official's per-layer unwrapped form (our group-level dict lines are among the 12 vanished base_worker lines). Every
  connector predicate downstream (`_is_full_attention`, `_is_mamba`, `tp_replicated` region grouping, `_is_csa_linear` at L367)
  now evaluates **leaf** specs instead of `UniformTypeKVCacheSpecs` wrappers — more precise, but a behavior change for exactly the
  DSV4/GLM/CSA wrapped groups. *Action:* run the nixl/connector unit suites before trusting it.

Also verified clean: `model_runner.py` PP broadcast was **not** duplicated by the merge (2 calls = ours' post-`propose`
broadcast + `broadcast_draft`); `iter_layer_specs` is available in ours' `kv_cache_interface` (official's rewrites depend on it);
`get_num_layer_tuples` is still required by `tests/v1/core/test_kv_cache_utils.py:2275`, independent of L1.

## Governing-rule check

No recommendation picks a side where the two sides are orthogonal: every file with real interaction (kv_cache_utils,
kv_cache_interface, model_runner, base_worker, mamba_utils, coordinator) is **union at hunk granularity**, and in each case the
wtdcode allocator predicate / block-accounting path is retained verbatim (`participates_in_prefix_caching`, `KpoolTailSpec`,
`KpoolTailManager`, `storage_block_size`, `max_worker_kv_bytes_per_block`, `slot_mapping_enabled`, `block_stride`,
CSA-linear + GLM5 + PP-balanced group counts). The two "take theirs" cases with real content (`models/config.py`,
`compilation.py`) are pure additions, and `platforms/interface.py`'s single hunk is a comment.

**Do not** run `git checkout --theirs` on any of the 9 remaining shared-infra files, and do not use `--strategy-option`
resolves: file-level take-theirs on `kv_cache_interface.py` / `kv_cache_utils.py` / `model_runner.py` is what deletes the
hybrid allocator, KV-recovery (`max_worker_kv_bytes_per_block`) and CSA/PP group-count logic — a quiet break of DSV4 and
GLM-5.3-Flash, not a test failure.

## Open decisions for the orchestrator (not blockers for this analysis)

1. `mamba_utils.py @991`: keep our `len(kv_caches)==len(mamba_spec.shapes)` invariant fatally, or only non-fatally? Decidable by
   inspecting a Qwen4Exp `MambaSpec.shapes` vs its exposed states (official removed the assert, which hints it fires for Qwen).
2. `base_worker.py @1220` `block_stride`: recommendation is ours' generic stride rule. If official's `physical_page_size`
   general case was deliberate (e.g. an hnc-layout fix), that is the one line in this set where "preserve ours" may need
   upstream justification rather than default precedence.

```json
{
  "containment": {
    "vllm/v1/core/single_type_kv_cache_manager.py": {"official_lines": 2094, "ours_lines": 2229, "absent": 0, "resolved": true},
    "tests/models/qwen4_exp/test_qsa_reference.py": {"official_lines": 973, "ours_lines": 1004, "absent": 0, "resolved": true},
    "tests/v1/kv_connector/unit/test_tp_mapping.py": {"official_lines": 315, "ours_lines": 331, "absent": 0, "resolved": true},
    "tests/models/qwen4_exp/test_qsa_amd.py": {"official_lines": 297, "ours_lines": 309, "absent": 0, "resolved": true}
  },
  "plan": [
    {
      "file": "vllm/v1/core/kv_cache_utils.py",
      "official_intent": "Generalize resolve_kv_cache_block_sizes for hybrid-Mamba prefix caching (nested specs, tokens_per_state alignments, partial-mamba cache_hit_alignment); replace DSV4-only group_and_unify/_get_kv_cache_groups_uniform_groups with generic _get_packed_kv_cache_groups; gate DSV4 eagle fallback on hf model_type; widen _annotate_eagle_groups via iter_layer_specs",
      "wtdcode_only": "_get_kv_cache_groups_glm5_next + _glm5_next_tensor_layout; full CSA+linear subsystem (_CSALinearCacheTuple/_TensorLayout/_Roles, _classify_csa_linear_specs, _get_csa_linear_cache_tuples, _get_csa_linear_mamba_group_count, _get_kv_cache_groups_csa_linear, _get_csa_linear_tensor_layout); _pp_balanced_mamba_group_count; group_and_unify_kv_cache_specs + _get_kv_cache_groups_uniform_groups; participates_in_prefix_caching filter in hashing_sizes; DSV4 detect via spec.model_version",
      "interacts": "yes - same functions and same hunks (block-size/hash-size selection and group counting)",
      "resolution": "union: hunk@731 ours (participates_in_prefix_caching); hunk@743 ours' error text + official's new prefix_alignments/has_partial_mamba_group/cache_hit_alignment body; hunk@1969 ours (official side empty = deletion of our CSA/linear+DSV4 block); hunk@2663 ours' three dispatch branches + official's comment; keep official _get_packed_kv_cache_groups call after our branches; PLUS restore stage2 kv_cache_utils.py:2345-2431 (_get_kv_cache_groups_uniform_groups) and re-add round_up to the math_utils import",
      "hard_flag": true,
      "hard_flag_reason": "official deletes DSV4 tuple packing, GLM5 grouping, CSA+linear group counts and PP-balanced mamba group count, and swaps our model_version DSV4 predicate for a model-type gate; _get_kv_cache_groups_uniform_groups was ALREADY silently deleted by the auto-merge while its caller survives"
    },
    {
      "file": "vllm/v1/worker/gpu/model_runner.py",
      "official_intent": "Exclude only CircularBufferSpec from generic slot mapping; move pp_handler.broadcast before propose; collapse PP-aware drafter support into a flat ValueError; drop model_state.supports_mm_inputs from the speculator mm gate",
      "wtdcode_only": "KpoolTailSpec in slot_mapping_enabled (GLM-5.3-Flash CUDA illegal-access guard); PLE offload connector lifecycle x6; _pp_aux_hidden_state_layers + get_pp_indices last-stage validation; pp_handler.broadcast_draft relay + req_states.draft_tokens scatter; num_blocks=kv_cache_config.num_blocks argument",
      "interacts": "yes - both hunks touch spec-type predicates; official's broadcast move collides with our NCCL-ordered broadcast+broadcast_draft sequence",
      "resolution": "ours for hunk@71-74 (KpoolTailSpec import) and hunk@641-652 (slot_mapping_enabled covers both CircularBufferSpec and KpoolTailSpec); PP region already resolved to ours' post-propose placement - verified no duplicated broadcast (merged L2083 broadcast + L2097 broadcast_draft only)",
      "hard_flag": true,
      "hard_flag_reason": "slot_mapping_enabled is a block-addressing predicate (failure mode is CUDA illegal memory access); official's broadcast placement would deadlock our draft relay under NCCL strict order matching; taking theirs also reverts working PP spec-decode to a hard error"
    },
    {
      "file": "vllm/v1/kv_cache_interface.py",
      "official_intent": "Rename participates_in_prefix_caching to prefix_cacheable; delete KpoolTailSpec; drop storage_block_size field + uniformity key; replace get_page_sizes/get_num_layer_tuples with get_max_layers_per_page_size for the new packing planner; add tp_replicated to Mamba uniformity; has_mamba via iter_layer_specs; drop max_worker_kv_bytes_per_block",
      "wtdcode_only": "participates_in_prefix_caching as canonical plus prefix_cacheable deprecated-alias (connector-safety docstring for GLM kpool tail and DSV4 compressor ring); class KpoolTailSpec (1 block/req, participates=False); storage_block_size; real_page_size_bytes; max_worker_kv_bytes_per_block (KV-recovery/shared-offload sizing, consumed by engine/core.py:339 and offloading/config.py:123); get_page_sizes + get_num_layer_tuples",
      "interacts": "yes - the prefix-cacheable rename is the central semantic collision and every other file's predicate depends on how it resolves",
      "resolution": "union all 5 hunks: @154 ours (keep canonical + alias so official's new .prefix_cacheable call sites resolve correctly; ensure official's unconditional return True at @173-177 does not double-define); @806 ours; @1067 ours (equivalent); @1134 UNION BOTH helper sets (our get_num_layer_tuples is needed by the restored uniform_groups and by tests/v1/core/test_kv_cache_utils.py:2275, official's get_max_layers_per_page_size by _get_packed_kv_cache_groups); @1347 theirs (equivalent iter_layer_specs form)",
      "hard_flag": true,
      "hard_flag_reason": "take-theirs deletes KpoolTailSpec (import error in single_type manager, model_runner, kv_cache_utils, glm5next attention, mooncake connector), storage_block_size (block-size accounting view) and max_worker_kv_bytes_per_block (KV-recovery layout sizing), and redefines the predicate that stops scratch groups being served as prefix KV"
    },
    {
      "file": "vllm/v1/core/single_type_kv_cache_manager.py",
      "official_intent": "Add CircularBufferManager (ring 1-block-per-request) and exclude CircularBufferSpec from new-block-id recording for zeroing",
      "wtdcode_only": "KpoolTailManager (entire GLM-5.3-Flash subclass: never skip, never prune, never prefix-cache, fixed 1 block/req)",
      "interacts": "no - official's additions are already present in our stage-2 blob; the conflict is purely positional adjacency",
      "resolution": "ours (resolved and staged in STEP 2, absent=0, structurally lossless)",
      "hard_flag": false
    },
    {
      "file": "vllm/distributed/kv_transfer/kv_connector/v1/nixl/base_worker.py",
      "official_intent": "Track CSA scratch regions explicitly (_scratch_region_indices init/populate/sort) because a scratch page shares the overlaid page address; unwrap UniformTypeKVCacheSpecs into per-layer _layer_specs for all connector predicates; SSM detection via _is_ssm_spec(get_representative_spec_type(...)); exempt CSA-linear from hnc_contiguous and packed_storage",
      "wtdcode_only": "_is_csa_linear-derived scratch region selection via np.flatnonzero(self._region_is_mla); group-valued _layer_specs; generic stride-based block_stride; _region_is_mla + _is_mla_region (still live at L302)",
      "interacts": "yes - official was rebased on our CSA work (stage3 references self._is_csa_linear) and edits the same predicates",
      "resolution": "theirs for @159-169, @376-385, @643-649, @1157-1160, @1301-1308; OURS for @1220-1232 block_stride (our rule already returns stride(0)*element_size for official's CSA case and stays correct for other packed layouts)",
      "hard_flag": true,
      "hard_flag_reason": "official's block_stride rewrite changes per-block descriptor stride for packed layouts (silent wrong-offset PD transfer); plus L3: _layer_specs semantics changed silently from group-level to per-layer, altering _is_mamba/_is_full_attention/tp_replicated decisions for DSV4/GLM/CSA wrapped groups"
    },
    {
      "file": "vllm/platforms/interface.py",
      "official_intent": "Support models with multiple Mamba state layouts via model_cls.get_mamba_specs_from_config (max page size), keeping the legacy MambaSpec path as else-branch",
      "wtdcode_only": "_get_indexer_block_alignment classmethod and its attn_block_size rounding (CUDA kpool paged-MQA indexer constraint); cache_dtype_str pass-through",
      "interacts": "no - the two edits share only the file; the sole conflict hunk is a bare comment line",
      "resolution": "theirs for the single hunk @870-873 (comment only); net file is union, our indexer hook and indexer_align rounding already survived the auto-merge (silent-loss 0)",
      "hard_flag": true,
      "hard_flag_reason": "conditional: a file-level take-theirs here would delete _get_indexer_block_alignment and its attn_block_size rounding, i.e. modify block-size computation for the GLM kpool indexer; not triggered by the recommended hunk-level resolution"
    },
    {
      "file": "vllm/v1/worker/mamba_utils.py",
      "official_intent": "Make mamba state copy robust: raise only when len(kv_caches) < len(state_copy_funcs) and iterate state_copy_funcs indexing kv_caches; delete both len(kv_caches)==len(mamba_spec.shapes) asserts",
      "wtdcode_only": "the two equality asserts tying exposed state tensors to the cache spec's declared shapes (catches CSA / multi-layout page-size mismatch)",
      "interacts": "yes - same loop body; official's relaxation may be required for Qwen4Exp's multi-layout states",
      "resolution": "union at @991-1006 (official's >= check and iteration as the control flow, our invariant retained non-fatally) and theirs at @1371-1377; explicitly do NOT keep a fatal == assert at @991 as it could break Qwen4Exp at load",
      "hard_flag": true,
      "hard_flag_reason": "this is the mamba state-copy (block data movement) guard; official removes it at both sites, so a naive take-theirs modifies rather than preserves a wtdcode invariant - the union form is the only resolution that keeps the guard without risking the new model"
    },
    {
      "file": "vllm/v1/core/kv_cache_coordinator.py",
      "official_intent": "Apply the prefix_cacheable rename in the block-size divisibility loop and in the fine-grained prefix-hit lookup skip",
      "wtdcode_only": "participates_in_prefix_caching plus the comment explaining why GLM-5.3-Flash kpool tail groups must not take part in hit lookup",
      "interacts": "naming only - semantics are identical provided the interface union retains our canonical name and alias",
      "resolution": "ours for both hunks @609-613 and @685-694",
      "hard_flag": true,
      "hard_flag_reason": "group-count and prefix-hit-lookup path: if either predicate name is lost, kpool tail and DSV4 ring groups silently re-enter prefix cache hit lookup and get served as shared KV, with no crash"
    },
    {
      "file": "vllm/model_executor/models/config.py",
      "official_intent": "Fail fast for Qwen4Exp N-gram PLE when pipeline_parallel_size > 1, before weights are loaded",
      "wtdcode_only": "none (0 ours-only lines)",
      "interacts": "no new constraint - we already raise the identical error at vllm/models/qwen4_exp/nvidia/model_state.py:47-50; official only moves the check earlier",
      "resolution": "theirs (hunk @877-887, pure addition)",
      "hard_flag": false
    },
    {
      "file": "vllm/config/compilation.py",
      "official_intent": "Register custom op vllm::qwen4_exp_compute_ple_ngram_ids in the compile-time op name list",
      "wtdcode_only": "vllm::sparse_attn_indexer_kpool (survived outside the markers)",
      "interacts": "no - adjacent list entries only",
      "resolution": "theirs (hunk @771-774, pure addition; result is the union of both op names)",
      "hard_flag": false
    }
  ],
  "landmines": [
    "L1: _get_kv_cache_groups_uniform_groups (stage2 vllm/v1/core/kv_cache_utils.py:2345-2431) was silently deleted by the auto-merge with no conflict marker, while its caller survives at merged kv_cache_utils.py:2669 -> NameError for DSV4; must be restored manually",
    "L2: merged kv_cache_utils.py:19 lost round_up from the vllm.utils.math_utils import (official's line); the restored function needs it (stage2:2382) -> re-add, no conflict marker present",
    "L3: nixl base_worker _layer_specs silently changed from group-valued to per-layer unwrapped; connector predicates (_is_full_attention, _is_mamba, tp_replicated grouping, _is_csa_linear) now see leaf specs for DSV4/GLM/CSA wrapped groups - no marker, needs connector unit tests"
  ],
  "pick_left_in_progress": true,
  "pick_state": {
    "head": "e16d574bb",
    "branch": "swap/qwen-88",
    "conflicts_initial": 29,
    "conflicts_remaining": 25,
    "resolved_by_this_pass": 4,
    "cherry_pick_head_file": false,
    "sequencer_dir": false,
    "merge_msg_file": true,
    "note": "git 2.43 with -n records pick state only in the index + MERGE_MSG; 'git cherry-pick --abort' is not usable, reset manually if abandoned"
  },
  "escalated": false,
  "escalation_reason": null,
  "decisions_needed": [
    "mamba_utils.py @991: whether our len(kv_caches)==len(mamba_spec.shapes) invariant can stay fatal, or must be downgraded for Qwen4Exp multi-layout MambaSpec.shapes",
    "base_worker.py @1220: confirm official's physical_page_size general case for block_stride is not a deliberate hnc-layout fix that should outrank our stride-based rule"
  ]
}
```

## ORCHESTRATOR DECISIONS on the two open questions (2026-09-06, from swapB evidence)

- **D1 `mamba_utils.py` ~@991 -> NON-FATAL.** Adopt official's control flow; retain our
  `len(kv_caches) == len(mamba_spec.shapes)` invariant as a warning, not an assert. Decisive evidence: that assert was
  written by wtdcode's own author (`d4d0f73ef` "Support Qwen3.8-Flash-Next", huanghaoyan.hhy, 2026-08-26) and official
  `e126687a9a` is the *same author* five days later removing it - i.e. a self-revision, not a foreign deletion. A fatal
  assert here would crash Qwen4Exp at load if it legitimately exposes more tensors than `mamba_spec.shapes`.
- **D2 `nixl/base_worker.py` ~@1220 `block_stride` -> KEEP OURS' generic stride rule.** (1) `stride(0)*element_size()`
  is this codebase's canonical formula (`base_worker.py:96-100`, `:133`), not a wtdcode invention; (2) the repo models
  packed multi-owner blocks where `block_stride` is a strict *multiple* of page size, so official's blanket
  `physical_page_size` default is wrong for those unless `_is_csa_linear` happens to be set - ours is a strict superset;
  (3) upstream CONVERGES on ours: the only later commit in `e126687a9a..d4d703caf9` touching that line is `98ed0856f`
  = **item 315, the GLM-5.3-Flash swap**, which adds ours' formula. SEQUENCING NOTE: this is direct evidence for the
  ratified joint planning of the two swaps - the same region is rewritten by the GLM swap, so resolving it once,
  deliberately, is required rather than optional.

## RESOLUTION LOG (orchestrator, swap/qwen-88)

- [x] 4 provably-lossless-ours files (containment proven, absent=0) - scout STEP 2
- [x] `model_executor/models/config.py`, `config/compilation.py`, `platforms/interface.py` - hunk-level, union verified - scout swapB JOB 1
- [x] **`vllm/v1/core/kv_cache_utils.py`** - RESOLVED by orchestrator via guarded script (assertions gate the write):
      hunk1 ours (`participates_in_prefix_caching`); hunk2 ours' error text + official's new body
      (`prefix_alignments`/`has_partial_mamba_group`/`cache_hit_alignment`); hunk3 ours (380 lines - official's side was an
      empty deletion of our CSA/linear + DSV4 grouping block); hunk4 ours' 3 dispatch branches + official's comment.
      **L1 restored** `_get_kv_cache_groups_uniform_groups` (87 lines) before `def _annotate_eagle_groups(`;
      **L2 restored** `round_up` in the `vllm.utils.math_utils` import. Verified: py_compile OK, silent-loss scan clean
      (no def/class from HEAD missing), dispatch order = uniform(2740) -> glm5_next(2748) -> csa_linear(2750) ->
      official `_get_packed_kv_cache_groups`(2769). 3324 lines (was 3255).
      CROSS-FILE DEPENDENCY: this file now calls `spec.prefix_cacheable` (official's new body). It resolves only because
      the `kv_cache_interface.py` resolution keeps BOTH the canonical `participates_in_prefix_caching` AND the
      `prefix_cacheable` alias - must re-verify when interface is resolved.
- [ ] hard-flag remaining: `kv_cache_interface.py`, `gpu/model_runner.py`, `nixl/base_worker.py` (D2=ours),
      `mamba_utils.py` (D1=non-fatal), `kv_cache_coordinator.py` (both hunks ours)
- [ ] 88a qwen4_exp model files (9) + remaining test files (6)
- [x] **`kv_cache_coordinator.py`** - both hunks OURS (canonical predicate + our GLM kpool-tail rationale comment).
      Verified: compiles, symbol-name silent-loss clean, canonical ref count == HEAD (2).
      NOTE: a check that banned `prefix_cacheable` outright was WRONG and was corrected - HEAD itself already mixes
      both names (line 655 predates the pick). The right test is "no NEW alias adoption", measured against HEAD counts.
- [x] **`mamba_utils.py`** - D1 applied: official's `if len(kv_caches) < len(state_copy_funcs): raise ValueError` +
      official's bounded `enumerate(state_copy_funcs)` loop ADOPTED, our `len(kv_caches)==len(mamba_spec.shapes)`
      invariant downgraded from fatal assert to `logger.warning`. Confirmed strictly safer than ours: ours iterated
      `enumerate(kv_caches)` while line 1025 indexes `state_copy_funcs[state_type_idx]`, so ours could IndexError when a
      layer exposed MORE states than the spec declared - exactly the Qwen4Exp case. Hunk 2 (@1371) = theirs (assert
      dropped; residual `zip(kv_caches, state_copy_funcs)` truncation noted for GPU validation). Compiles, silent-loss clean.
- CROSS-FILE DEPENDENCY NOW SATISFIED: HEAD already defines `prefix_cacheable` as a deprecated alias at
  `kv_cache_interface.py:159` with a docstring warning that dropping it would let GLM-5.3-Flash kpool tail and DSV4
  compressor-ring scratch groups default back to cacheable. So official's new `.prefix_cacheable` call sites already
  resolve - but ONLY while the interface hunk @154-177 keeps BOTH names. Taking theirs there deletes the alias.
- [ ] hard-flag remaining (3): `kv_cache_interface.py` (alias + KpoolTailSpec), `gpu/model_runner.py`
      (slot_mapping_enabled, PP broadcast), `nixl/base_worker.py` (D2=ours, L3 _layer_specs semantics)
- [x] **`kv_cache_interface.py`** - 5 hunks: ours, ours, ours, **UNION**, theirs. Compiles; name-level silent-loss clean;
      `KpoolTailSpec`, `storage_block_size`, `max_worker_kv_bytes_per_block`, `real_page_size_bytes` all confirmed intact
      BEFORE and AFTER resolution (the pre-check showed git had NOT silently deleted them here, unlike kv_cache_utils).
      Hunk @154 kept canonical `participates_in_prefix_caching` AND the deprecated `prefix_cacheable` alias **with its
      warning docstring**; asserted exactly 1 definition of `prefix_cacheable` so official's unconditional `return True`
      could not co-define a second one and shadow the delegating alias.
      Hunk @1134 was the trap: ours' `get_num_layer_tuples` and official's new `get_max_layers_per_page_size` SHARE a
      single body located AFTER the conflict marker, so a plain textual union yields a method with no body. Resolved by
      materialising the shared body once per method. Caller check: `get_max_layers_per_page_size` has 3 callers (official's,
      now satisfied), `get_num_layer_tuples` has 2 (ours', preserved), `get_page_sizes` now has 0 callers -> dead but kept
      deliberately (removing it is out of scope and riskier than keeping it).
      Hunk @1347 took official's `iter_layer_specs` form for `has_mamba_layers` (strictly more thorough than ours'
      first_spec unwrap). NOTE for GPU validation: this can return True where ours returned False for a mixed uniform
      group - a behavior delta in mamba-path gating, judged an improvement but unverified at runtime.
- [x] **`nixl/base_worker.py`** - 6 hunks: theirs x5, **OURS for block_stride (D2)**. Asserted before applying: ours'
      hunk1 carried `_region_is_mla`+`_is_csa_linear`, official's carries `_scratch_region_indices`; hunk2 ours matched only a
      bare `MambaSpec` group while official matches per-layer via `iter_layer_specs` (ours would raise
      "CSA-linear NIXL requires exactly one PLE cache owner" for a wrapped group); hunk5 verified as the exact D2 pair.
      Verified after: compiles, name-level silent-loss clean, generic `stride(0)*element_size()` rule retained, and
      `_region_is_mla` still defined (not orphaned by taking official elsewhere).
      A check of mine was wrong again here: it demanded zero occurrences of `block_stride = physical_page_size`, but HEAD
      already has one at another site. Correct invariant is **no NEW adoption**, measured against HEAD's count.
- [x] **RUNTIME IMPORT GATE PASSED (88b complete)** - all 10 resolved shared-infra modules imported inside
      `mitakad/vllm:...d4d703c` with `PYTHONPATH` pointed at the swap worktree: kv_cache_utils (with L1 restored),
      kv_cache_interface (KpoolTailSpec + both predicate names live), single_type_kv_cache_manager (KpoolTailManager),
      kv_cache_coordinator, mamba_utils, gpu/model_runner, nixl/base_worker, models/config, config/compilation,
      platforms/interface. **10/10 import clean.** This is much stronger evidence than `compile()`.
- REMAINING for the swap: 9 `qwen4_exp/**` model files (88a) + 7 test files. 16 files still unmerged, 0 commits ahead.

## 88b REVIEW VERDICT — orchestrator-direct (2026-09-06)

Both review children (oracle + cpu-test leg) were **terminated** with no output - two child deaths in one window
triggers the documented switch to orchestrator-direct. Verdict produced by direct tracing instead.

**Verdict: CONDITIONAL PASS for CPU purposes.** No blocker found in the resolved 10; the conditions are runtime,
not static, and are exactly what the GPU window must cover.

Evidence gathered:
1. **Silent-loss scan** (def/class NAMES, HEAD vs working file) on all 10: clean everywhere except the two
   landmines in `kv_cache_utils.py` that were then restored (L1 `_get_kv_cache_groups_uniform_groups` 87 lines,
   L2 `round_up` import). Re-verified after restore: L1 is importable at runtime.
2. **Runtime import gate: 10/10 modules import** inside `mitakad/vllm:...d4d703c` with `PYTHONPATH` on the swap
   worktree, GPU hidden.
3. **Predicate override map** (the sharpest risk - a subclass overriding the *alias* would invert semantics):
   `KVCacheSpec.participates_in_prefix_caching` -> True (base);
   `KVCacheSpec.prefix_cacheable` -> the ONLY alias definition in the tree, delegates to canonical;
   `CircularBufferSpec` (DSV4 compressor ring) -> canonical **False**;
   `KpoolTailSpec` (GLM-5.3-Flash kpool tail) -> canonical **False**;
   `UniformTypeKVCacheSpecs` -> all(canonical).
   No subclass anywhere defines `prefix_cacheable`, so official's 3 alias call sites resolve through the
   delegating base property and correctly observe False for both scratch specs. Call-site split: 10 canonical / 3 alias.
4. **Dispatch order** in `kv_cache_utils`: uniform(2740) -> glm5_next(2748) -> csa_linear(2750) -> official
   `_get_packed_kv_cache_groups`(2769). Ours wins ties, as intended.
5. **PP topology** in `model_runner`: 1 `pp_handler.broadcast` + 1 `broadcast_draft`, broadcast still AFTER
   `propose` (2052 -> 2076), byte-identical ordering to HEAD. Moot for this deployment (TP-only) but faithful.

**Residual deltas accepted deliberately, all on the GPU list:**
- `has_mamba_layers` now via `iter_layer_specs` - can return True where ours returned False for a mixed uniform group.
- `base_worker.py` `ple_groups` selection now per-layer (ours matched only a bare MambaSpec and would raise
  "CSA-linear NIXL requires exactly one PLE cache owner" for a wrapped group).
- `mamba_utils` invariant downgraded fatal -> warning (D1; official's bounded loop is strictly safer).
- `block_stride` kept as ours' generic rule (D2; upstream adopts ours at item 315).
- `nixl/base_worker.py` `_layer_specs` leaf-vs-wrapper semantics (L3) - only exercised by the NIXL connector path.

- [x] **CPU coverage attempt ABANDONED twice (env, not code)** - ran 36-suite then 13-suite CPU legs against the swap worktree (mounted :ro); both stalled after ~40 tests, and the first was found running Ray inside the container (ray::DashboardAgent/log_monitor/dashboard.py) while production served. Killed both; :8000 = 200 before and after; container removed. Evidence for 88b therefore rests on the 10/10 runtime-import gate + silent-loss scans + the predicate override-map review, NOT on test coverage - and the suites that would prove it are 4 of the 7 still-conflicted test files, so they get rerun AFTER 88a. Handoff: `.scratch/official-port-sweep-1/handoffs/handoff-2026-09-06-port-grind-and-swap.md` (now archived in the ledger, not a temp dir).

## 88a RESOLUTION LOG (orchestrator-direct, 2026-09-06) — 9/9 model files DONE

Measured divergence first (stage2 vs stage3, per file) — this **shrank** ticket 05's "re-apply ~315 lines":
2 files provably lossless-take-THEIRS (`ours-only=0`, order-preserving containment re-proven with
`comm -23 <(sort :2) <(sort :3)`: `amd/model.py`, `common/ple.py`), 1 lossless-take-OURS (`config.py`,
`theirs-only=0`), 6 hunk-level unions. The `never --theirs` rule is about shared-infra files; here it was
permitted only after that containment proof.

- [x] `amd/model.py`, `common/ple.py` — take theirs (containment proven, `ours-only=0`).
- [x] `config.py` — take ours (official adds nothing).
- [x] `nvidia/model_state.py`, `nvidia/model.py` — **all hunks theirs; files are byte-identical to
      official's blob**. Justification for dropping the 4+5 wtdcode-only lines: all of them are the
      PP>1 path (`uses_ngram_embedding and get_pp_group().is_first_rank`; the `skip_substrs.append
      ("hyper_connection_mixer.")` branch). Official's PP fail-fast already landed in 88b at
      `model_executor/models/config.py:879-884` (gated on `ple_layer_ids`), so `is_first_rank` is True
      whenever execution reaches it, and `ignore_unexpected_prefixes` (models/utils.py:230) is
      equivalent when `hyper_connection_mixer is not None` (PP=1). Verified the dropped import had no
      other use. Same-author-later-revision pattern as D1.
- [x] `amd/mtp.py`, `nvidia/mtp.py` — unions: took official's fused-shared-expert plumbing (import,
      `Qwen4ExpSparseMoeBlock`, `is_fused_shared_expert_enabled`, `enabled=` arg — convention already
      matches the ported `qwen3_next.py:745`, and `maybe_fuse_shared_experts` already accepts
      `enabled` at models/utils.py:479) and **kept both wtdcode augmentations**: the compressed-tensors
      MTP ignore-list extension (AWQ W4A16 exports that leave the draft in bf16 — product-relevant) and
      nvidia's `is_first_rank or hidden_states is not None` draft-PP relaxation. Diff vs official blob =
      exactly those preserved lines, nothing else.
- [x] `amd/ple_layer.py` — 8 hunks → all theirs except wtdcode's `# TODO: need double-check`. Every
      wtdcode-only line here was the *same logic* official re-expressed: module-level hash helpers →
      classmethods (formula compared line by line), inline vocab layout → `_make_vocab_layout`, and
      `copy_ple_embedding_shard_(...)` → `PLEVocabParallelEmbedding.weight_loader`, which **calls that
      same helper with the same `shard_indices` bounds** (read it). So this file is official's, provably.
- [x] `nvidia/ple_layer.py` — the real work, 22 hunks. Official restructured the PLE entry point
      (`compute_ngram_ids` + a new graph-excluded custom op `vllm::qwen4_exp_compute_ple_ngram_ids`)
      where wtdcode has `forward_impl` under its `PleOffloadLayer` CPU-offload base.
      **Trap: official's subclass-level `forward()` would silently clobber `PleOffloadLayer.forward`,**
      which is what routes the GPU worker to the IPC semaphore — take-theirs there disables PLE CPU
      offload with no error at all. Resolution: keep wtdcode's base class + official's classmethods, take
      official's `compute_ngram_ids` (with wtdcode's offload-only buffer narrowing kept inside it), and
      fold official's `forward` body into `forward_impl`, branching on `is_offload_process()` — direct
      call in the CPU subprocess (no forward context to resolve `layer_name`, and it never captures a
      CUDA Graph), the custom op on the GPU path. Kept wtdcode's `get_offload_output_dtype` and the
      `output_buffer` IPC fast path; took official's `layer_name` param and
      `with torch.device(PleOffloadLayer.get_target_device())` construction context together.
      Note `PleOffloadLayer.__init_subclass__` replaces `__init__` with a `functools.wraps` wrapper, so a
      `co_varnames` probe reads the wrapper, not the real signature — check signatures textually.
- [x] **RUNTIME IMPORT GATE for 88a PASSED**: nvidia+shared-infra **16/16**, amd-only **6/6**, GPU hidden,
      inside `mitakad/vllm:…d4d703c` with `PYTHONPATH` on the worktree. Importing nvidia and amd variants
      in ONE process fails by design (both register `vllm::qwen4_exp_grouped_gemma_rmsnorm` /
      `qwen4_exp_ple_short_conv`) — pre-existing two-variant layout, not a resolution defect; test each
      variant in its own process.
      Structural checks: nvidia class base=`PleOffloadLayer`, has `compute_ngram_ids` AND `forward_impl`,
      **`forward` NOT overridden**, `get_offload_output_dtype` present, custom op registered, L1
      `_get_kv_cache_groups_uniform_groups` callable alongside official's `_get_packed_kv_cache_groups`,
      `prefix_cacheable` alias present, `KpoolTailSpec`/`CircularBufferSpec` intact. amd class keeps
      official's `forward` (no offload there) and registers no op — the op is nvidia-only, while
      `config/compilation.py` lists its name unconditionally (harmless: that list is a name allow-list).
- Symbol-NAME silent-loss scan vs HEAD clean on all 9.

Remaining for the swap: 7 test files (still unmerged), then the narrow CPU leg, rebase onto the moving
tip, one `-x` commit, and push as a branch only.

## 88c TEST FILES (4 of 7 resolved, 2026-09-06 session 2)

- [x] `test_gpu_autoregressive_speculator.py`, `test_gpu_model_runner_v2.py` — 1 hunk each, take theirs,
      both files byte-identical to official's blob. The speculator one monkeypatches
      `_target_feeds_hc_residual`, i.e. it *follows* Fork #2's gate; taking ours there would have kept a
      test of a guard we already deleted.
- [x] `tests/v1/core/test_kv_cache_utils.py` — only ONE 1-line conflict (the `vllm.config` import; resolved
      as a UNION, ours needs `KVTransferConfig`, official adds `CacheConfig`). The 605/63 line divergence
      merged silently and that is exactly where the damage was: **the auto-merge deleted 5 wtdcode tests**
      (`test_group_and_unify_kv_cache_specs_*` x3, `test_deepseek_v4_annotation_requires_model_version`,
      `test_deepseek_v4_draft_group_annotated_on_group_and_unify_path`) — the tests that cover the very
      functions 88b restored via L1 — and dropped **one official test**
      (`test_mixed_precision_kv_cache_with_uniform_type_specs`) into a region our tree had modified.
      Both sides re-applied; defs now 110 ours + 4 official-only = 114, LOST_FROM_OURS and
      MISSING_OFFICIAL both empty. NOTE: whether those 5 restored tests still PASS is unresolved and is a
      real re-grill candidate, because 88b also took official's `hf_config.model_type=="deepseek_v4"`
      eagle gate alongside our `spec.model_version` predicate.
- [x] `tests/v1/kv_connector/unit/test_nixl_desc_geometry.py` — all 7 hunks theirs, deliberately as a UNIT:
      official rewrote the fixture around `tensor_regions` and its helpers arrive in the ours-empty hunks,
      so any mix would reference undefined variables. Consistency check: our resolved interface uses
      `tokens_per_state` (official's rename) and `compress_ratio` appears nowhere, so the fixture matches
      the code we shipped.

### The NIXL suite cannot validate anything on jetson-222 (corrects an assumption in the handoff)
Ran it: swap tree **196 failed / 6 passed**; parent tree `e16d574bb` **200 failed / 1 passed**, both with
`NIXL is not available` / `NIXL agent config is not available` in the log. The dominant failure is
`assert block_stride % physical_page_size`-family arithmetic in `register_kv_caches`, and that assert
exists in BOTH trees (1 occurrence each in ours' parent and official's blob), so it is not an auto-merge
chimera and not introduced by the swap. Conclusion: **`test_nixl_desc_geometry.py` is NOT usable as 88b
evidence in this image** — the handoff's "these 4 suites would prove 88b" list must drop it (or gain a
NIXL-capable runner). The swap tree is strictly better than base here, which is reassuring but proves
nothing. Add to the GPU/NIXL validation list.

## 88d LAST 3 TEST FILES RESOLVED (2026-09-06 session 3) — pick is now conflict-free

Tooling rebuilt (jetson `/tmp` had been wiped): `/tmp/sw.py` (`dump` / `show` / `apply <i><O|T|U>[,...]` /
`check`) refuses to write unless block-count matches the spec, zero markers remain, **and `compile()`
passes**, then diffs def/class NAMES against stage-2 (ours) and stage-3-or-upstream (theirs). `/tmp/postcheck.py`
adds what `compile()` cannot: an AST pass proving every module-private helper a kept test *calls* still
exists — the failure mode when a union keeps official's test whose fixture our side reshaped. All 7 swap
test files pass both: `LOST_FROM_OURS=none`, `MISSING_THEIRS=none`, `undefined local-helper references: none`.

- **`test_ple.py` → T,T,T,O,O,U,O** (21 defs = parent 18 + 3 official-only). #1–#3 are one coherent
  official addition (`from functools import partial` + helper `_set_test_embedding_weight_loader` + its two
  call sites); verified safe because the shared `_make_ngram_embedding_for_load_test` body builds
  `weight=nn.Parameter(...)`, and `weight.weight_loader = ...` on a Parameter is standard vLLM
  (`VocabParallelEmbedding`). #4/#5/#7 are wtdcode's **PLE CPU-offload** tests (`forward_impl(...,
  output_buffer=...)`, `is_offload_process`, fp8 `output_buffer.data_ptr()`) — these are the executable
  specification of the very mechanism Fork #3 preserved, so they are not optional. #6 is a **union**, not a
  fight: ours tests the offload buffer path, official's tests the new `qwen4_exp_compute_ple_ngram_ids`
  custom op via `get_forward_context` — different functions, no name collision.
- **`test_config.py` → all-ours, then official's two extras folded in by hand.** This file is not two
  versions of one suite: our tree has 19 tests, official's blob has 5. Two real findings: (a) our
  `test_qwen4_exp_mtp_override_exposes_index_share_flag` **is** official's
  `test_qwen4_exp_mtp_override_sets_draft_config` with 4 asserts missing — same parametrize, same body,
  official adds `model_type`/`architectures`/`hc_mult == 2`/`n_predict == 1`. Adopted **official's name**
  (future official picks to this file will match it) and its asserts. A naive union here would have emitted
  two consecutive `def(` lines — `compile()` would have caught it, which is why the gate exists. (b) added
  official's `test_qwen4_exp_rejects_pipeline_parallel_only_with_ple` verbatim: **it is the guard the whole
  88a decision on `model_state.py`/`model.py` rested on** (we dropped wtdcode's PP conjuncts because
  official's *conditional* refusal, gated on `ple_layer_ids`, lands first). Verified runnable here — our
  `_text_config(**kwargs)` already defaults `ple_layer_ids=[1]`, so both params resolve.
- **`test_contiguous_kv_packing.py` → U,U,O,O,U** (44 defs). #5's 220-vs-222 "showdown" is **not** a
  showdown: our side adds `TestCSALinearPacking` + `_placements_by_layer`, official's adds
  `TestCSALinearGrouping` — disjoint names, so union. The actual conflict is the shared fixture
  `_make_csa_linear_specs` (#3/#4): ours is a **strict superset** of official's — same defaults, plus
  keyword-only `main_kv_indices`/`mamba_indices`/`include_replicated` normalized to
  `list(range(num_mamba))`/`list(range(num_tuples))` and `include_replicated=True`, so official's class
  calling it with defaults gets byte-identical specs. Took ours; postcheck proves official's class calls no
  helper our version dropped. #1/#2 unions are import-list members both suites need
  (`_max_memory_usage_bytes_from_groups` + `_get_packed_kv_cache_groups`, `SlidingWindowSpec` + `SlidingWindowMLASpec`).

State: `swap/qwen-88` **0 unmerged, 0 conflict markers, 42 files staged, 0 commits ahead**. Two containers
now running the CPU leg + the mandatory parent-tree compare over `tests/models/qwen4_exp/`,
`test_contiguous_kv_packing.py`, `test_kv_cache_utils.py` (`swap88leg` vs `base88leg`, GPU hidden, prod 200).
