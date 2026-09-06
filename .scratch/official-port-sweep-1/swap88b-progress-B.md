# swapB — swap lane: 3 no-flag files resolved + silent-loss scan + D1/D2

Scope held: worked **only** via ssh in `jetson-222:~/dev/vllm-swap88` (branch `swap/qwen-88`). Never `cd`'d, `git -C`'d,
read or wrote `~/dev/vllm` or `mitaka/backport`. **No commit, no push, no container run.**
Final: `HEAD=e16d574bb`, `commits_ahead=0`, `git ls-remote origin refs/heads/swap/qwen-88` empty, unmerged 25→**22**.
All 6 hard-flagged files verified still unmerged (untouched by this lane). Serving `:8000` health **200**.
One validation-image container was already running from the *other* lane — not mine, never touched.

## JOB 1 — 3 files resolved at hunk level (never `checkout --theirs`)

All three hunks had an **empty HEAD side** (pure official additions). Resolution was marker-exact, with the empty-ours
side *asserted* by the script rather than assumed (it aborts if ours-side is non-empty), so no wtdcode line could be dropped.

| file | hunk | action | result |
|---|---|---|---|
| `vllm/model_executor/models/config.py` | @877–887 | take official (+8) | PP>1 fail-fast for Qwen4Exp N-gram PLE |
| `vllm/config/compilation.py` | @771–774 | take official (+1) | registers `vllm::qwen4_exp_compute_ple_ngram_ids` |
| `vllm/platforms/interface.py` | @870–873 | take official (+1) | comment line only |

**Post-verify — diff of merged vs official stage-3 (`:3`), the strong form of the check:**

| file | lines only in merged | lines only in official |
|---|---|---|
| `models/config.py` | 0 | 0 → identical to official (correct: plan measured `A=0`, ours had nothing here) |
| `config/compilation.py` | **1** = `"vllm::sparse_attn_indexer_kpool",` | 0 → **UNION achieved** |
| `platforms/interface.py` | **15** = our `_get_indexer_block_alignment` classmethod + docstring | 0 → union, nothing official lost |

File-level take-theirs was correctly avoided: on `interface.py` it would have deleted the 15-line indexer block. Its
rounding site is confirmed live — `interface.py:927-929`:
`indexer_align = cls._get_indexer_block_alignment(vllm_config)` → `attn_block_size = indexer_align * cdiv(attn_block_size, indexer_align)`.
Residual conflict markers in all 3 files: **0**. All 3 `git add`ed; all other files left unmerged.

## JOB 2 — silent-loss scan, all 7 resolved files

"Ours" taken from `git show HEAD:FILE` (stage-2 is destroyed by `git add`; HEAD is equivalent here). Scan run
**before** staging. Compares def/class signatures *and* full non-blank line multisets.

```
CLEAN  vllm/model_executor/models/config.py            ours_lines_missing=0  official_added=8
CLEAN  vllm/config/compilation.py                      ours_lines_missing=0  official_added=1
CLEAN  vllm/platforms/interface.py                     ours_lines_missing=0  official_added=1
CLEAN  vllm/v1/core/single_type_kv_cache_manager.py    ours_lines_missing=0  official_added=0
CLEAN  tests/models/qwen4_exp/test_qsa_reference.py    ours_lines_missing=0  official_added=0
CLEAN  tests/v1/kv_connector/unit/test_tp_mapping.py   ours_lines_missing=0  official_added=0
CLEAN  tests/models/qwen4_exp/test_qsa_amd.py          ours_lines_missing=0  official_added=0
```

**No silent definition loss and no silently dropped wtdcode line in any of the 7.** This is the *clean* subset — the
landmines L1/L2 (`_get_kv_cache_groups_uniform_groups` + `round_up` in `kv_cache_utils.py`) and L3 (`_layer_specs`
semantics in `base_worker.py`) live in the 6 hard-flagged files, which this lane did not touch. They remain live for
the orchestrator.

## D1 — `mamba_utils.py` ~@991: **non-fatal** (adopt official's control flow; keep our invariant as a warning)

Evidence, strongest first:

1. **It is the same author's own later decision, not a deletion by someone else.** `git log -S"exposes"` on our HEAD
   attributes the `assert len(kv_caches) == len(mamba_spec.shapes)` to **`d4d0f73ef` "Support Qwen3.8-Flash-Next"
   (huanghaoyan.hhy, 2026-08-26)** — wtdcode's private build. Official **`e126687a9a` is the same person
   (Harry Huang / huanghaoyan.hhy), 2026-08-31, five days later**, upstreaming that work. The relaxation is deliberate.
2. **The real invariant did not disappear — official *added* a global enforcer.** Official's own diff adds
   `validate_mamba_state_copy_funcs()`, which asserts `len(state_copy_funcs) == len(mamba_spec.shapes)` for *every*
   mamba spec. It auto-merged cleanly and is live at `mamba_utils.py:707-718`. So coverage of spec↔copy-func mismatch
   is retained globally, without the per-layer fatal check.
3. **The two sides iterate different collections, and ours can hard-brick a model upstream supports.** Allocation is
   `for (shape, dtype) in zip(self.shapes, self.dtypes)` (`kv_cache_interface.py:924,935`) → tensor count is
   `min(len(shapes), len(dtypes))`. If a config ever yields a shorter `dtypes` tuple, `len(kv_caches) < len(shapes)` and
   ours' fatal `==` **crashes Qwen4Exp at engine load**, where official merely raises the `len(kv_caches) <
   len(state_copy_funcs)` ValueError at the point of use.
4. **Residual risk, stated honestly:** ours iterated `enumerate(kv_caches)` (all exposed states) while official
   iterates `enumerate(state_copy_funcs)` (only the first N). Under equality they are identical; if a layer ever
   exposes *more* tensors than copy-funcs, official silently under-copies mamba state. No allocation path in the tree
   produces extras (allocation is shapes/dtypes-driven), so this looks theoretical — but it is exactly the class of bug
   that shows up as wrong GLM/CSA output rather than a crash, so it belongs on the manual GPU checklist.

**Recommended resolution (matches the plan):** official's `if len(kv_caches) < len(state_copy_funcs): raise ValueError`
+ `for state_type_idx, copy_func in enumerate(state_copy_funcs)` as the control flow, **plus** our equality check
retained as `logger.warning`, not `assert`. Site @1371-1377: take theirs (duplicate of the same guard; the adjacent
`zip(kv_caches, state_copy_funcs)` truncation is the real hazard there).

## D2 — `base_worker.py` ~@1220 `block_stride`: **keep OURS' generic stride rule**

The divergence is narrower than the plan implied, and it converges upstream.

```python
# ours                                          # official (e126687a9a)
block_stride = (                                block_stride = physical_page_size
    physical_page_size                          if self._is_csa_linear and cache.ndim != 1:
    if cache.ndim == 1                              block_stride = cache.stride(0) * cache.element_size()
    else cache.stride(0) * cache.element_size()
)
```

Case analysis — they agree on `ndim==1` and on CSA-linear multi-dim; they differ **only** for a multi-dim, non-CSA
cache, where ours yields the true stride and official yields page size.

1. **`stride(0) * element_size()` is this codebase's canonical block-stride formula**, not an ad-hoc wtdcode
   invention: `_share_storage_and_block_stride()` at `base_worker.py:96-100` computes exactly that, as does `:133`.
2. **Layouts exist where the two differ, and the repo models them explicitly.** At the sweep cutoff the code tests
   `block_stride > physical_page_size and block_stride % physical_page_size == 0` and
   `cache.shape[0] * (block_stride // physical_page_size) == num_blocks` — i.e. packed multi-owner blocks where
   stride is a strict *multiple* of page size. Official's blanket default `physical_page_size` is wrong for those
   unless `_is_csa_linear` happens to be set; ours is right by construction and is a strict superset of official.
3. **Official converges toward ours.** `git log -S"block_stride" e126687a9a..d4d703caf9 -- <file>` returns exactly one
   later commit: **`98ed0856f` "[Model] add GLM-5.3-Flash support (#53906)"** — and that commit *adds* the
   `block_stride = cache.stride(0) * cache.element_size()` computation plus the packed-multiple predicate. So upstream
   ends up adopting ours' formula. The only other commit touching the file in that range, `41848caa6` (NIXL int32
   indices), does not touch this line.

**Flag for sequencing:** that one later commit is **item 315, the GLM-5.3-Flash swap** — so this exact region gets
re-touched there. Do not over-engineer it at 88: keep ours now, and at 315 take official's GLM version of the region,
which by then agrees with ours. Ours' choice is also the one that cannot regress GLM when 315 lands.

## State handed back

`swap/qwen-88` @ `e16d574bb`, pick still in progress, **22 files unmerged** (6 hard-flagged shared-infra + 9
`qwen4_exp/*` 88a files + 7 test files), 45 staged, no commit, no push, no GPU/container use, other lane untouched.

```json
{
  "resolved": [
    "vllm/model_executor/models/config.py: took official @877-887 (+8, ours side empty, verified identical to official)",
    "vllm/config/compilation.py: took official @771-774 (+1), UNION verified - sparse_attn_indexer_kpool still present, merged = official + 1 line",
    "vllm/platforms/interface.py: took official comment @870-873 (+1), merged = official + our intact 15-line _get_indexer_block_alignment block, rounding live at L927-929"
  ],
  "silent_loss": [],
  "D1": "non-fatal: adopt official's ValueError floor + enumerate(state_copy_funcs); retain our kv_caches==shapes check as logger.warning. Evidence: ours came from wtdcode d4d0f73ef (huanghaoyan.hhy, 2026-08-26) and the SAME author upstreamed the relaxed form in e126687a9a (2026-08-31); official ADDS validate_mamba_state_copy_funcs which enforces copy_funcs==shapes globally (auto-merged, live at mamba_utils.py:707); allocation is zip(shapes,dtypes) so a shorter dtypes tuple makes our fatal == crash Qwen4Exp at load. Residual: official iterates only the first N states, so a layer exposing extras would silently under-copy - put GLM/CSA mamba state correctness on the GPU checklist.",
  "D2": "keep ours (generic stride(0)*element_size). It is the codebase's canonical formula (base_worker.py:98,:133); the repo explicitly models block_stride as a strict multiple of physical_page_size for packed multi-owner blocks, where official's blanket physical_page_size default is wrong unless _is_csa_linear is set; ours is a strict superset (identical for ndim==1 and CSA-linear, differs only for multi-dim non-CSA). Official later converges on ours: the only commit in e126687a9a..d4d703caf9 touching block_stride is 98ed0856f = item 315 GLM-5.3-Flash, which adds exactly this stride-based computation - so re-take official's version of the region at 315.",
  "unmerged_remaining": 22,
  "committed": false,
  "pushed": false,
  "escalated": false,
  "escalation_reason": null
}
```
