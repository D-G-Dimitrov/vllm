# GLM-5.3-Flash vs Qwen3.8-Flash-Next — cherry-pick collision analysis

Repos: `/Users/mitaka/Projects/PyCharm/vllm-mitaka` (branches `mitaka/official` @ e862c2f45b, `mitaka/backport` @ d1ba3782f9 = wtdcode fork tip 3bec27573 + 2 user commits) and `/Users/mitaka/Projects/PyCharm/vllm-backport` (wtdcode clone, HEAD detached at v0.11.3).
Official PRs: `98ed0856f3` (GLM-5.3-Flash, #53906, merged 2026-09-03) and `e126687a9a` (Qwen3.8-Flash-Next, #53896, merged 2026-08-31). wtdcode's initial ports predate the merges: `933876c388` (GLM, 2026-08-26) and `d4d0f73ef1` (Qwen, 2026-08-26); fork base `c01b50e390`.
Runtime facts: Qwen3.8-Flash-Next works on official; GLM-5.3-Flash does NOT work on official but works on wtdcode's backport. User runs wtdcode/GLM-5.3-Flash-AWQ-W4A16 (AutoRound AWQ W4A16) with MTP-3 on 4x A100-80GB (sm80) per wtdcode README, and Qwen/Qwen3.8-Flash-Next-FP8 on the Jetson cluster with PP/PLE profiles.

## 1. File footprint

### Official PR 98ed0856f3 (GLM-5.3-Flash) — 94 files, `vllm/` subset highlights
- Model: `vllm/models/glm5next/**` (nvidia + amd trees incl. `ops/third_party/kda/{fused_recurrent,kernels}.py`, `mtp.py`, `multimodal.py`), `vllm/models/registry.py`
- Config/processor: `vllm/transformers_utils/configs/glm5_next.py`, `processors/glm5next.py`, `config.py`, `model_arch_config_convertor.py`
- Indexer/sparse-MLA: `vllm/model_executor/layers/sparse_attn_indexer_kpool.py`, `vllm/v1/attention/backends/mla/{indexer,flashinfer_mla_sparse,flashinfer_mla_sparse_sm90,sparse_utils,rocm_aiter_mla,rocm_aiter_mla_sparse}.py`, `vllm/v1/attention/ops/rocm_aiter_mla_sparse.py`, `vllm/model_executor/layers/attention/mla_attention.py`
- Infra: `vllm/model_executor/layers/mhc.py`, `vllm/v1/kv_cache_interface.py`, `vllm/v1/core/{kv_cache_utils,kv_cache_coordinator,single_type_kv_cache_manager}.py`, `vllm/model_executor/warmup/{kernel_warmup,spec_decode_rejection_warmup}.py`, `vllm/config/{speculative,vllm}.py`, `vllm/utils/{deep_gemm,flashinfer}.py`, `vllm/v1/worker/gpu_model_runner.py`, `vllm/v1/worker/gpu/model_runner.py`, `vllm/v1/spec_decode/llm_base_proposer.py`
- NOTE: official PR does NOT add `vllm/v1/attention/ops/fp8_sm80.py` or `vllm/v1/attention/ops/mqa_logits_triton.py` (both absent at e862c2f45b).

### Official PR e126687a9a (Qwen3.8-Flash-Next) — 124 files
- Model: `vllm/models/qwen4_exp/**` (common/nvidia/amd: `model.py`, `model_state.py`, `mtp.py`, `ple_layer.py`, `hyperconnection.py`, `indexer_qsa.py`, `qsa.py`, `ops/{qsa,qsa_pre_indexer,hc}.py`, `low_latency_gemm.py`, `config.py`)
- Infra: `vllm/model_executor/models/{qwen3_next,qwen2_moe,interfaces}.py`, `vllm/model_executor/layers/quantization/{fp8.py,utils/config_utils.py,utils/flashinfer_utils.py}`, `vllm/v1/kv_cache_interface.py`, `vllm/v1/core/kv_cache_utils.py`, `vllm/v1/worker/{gpu_model_runner.py,gpu/model_runner.py,mamba_utils.py}`, warmup incl. `qwen4_exp_qsa_warmup`, tests/evals (`tests/evals/qwen4_exp/`).
- Official does NOT have `vllm/model_executor/layers/ple_offload_layer.py` or `vllm/v1/ple_offload/` (MISSING at e862c2f45b).

### wtdcode GLM commits (c01b50e390..mitaka/backport, `vllm/models/glm5next*` et al.)
933876c388 feat: add GLM-5.3-Flash support · 54d298759f merge main · 724f07381c [ROCm] GLM-5.3-Flash on AMD (#5) · 0f82208cb1 Fix GLM-5.3-Flash CI regressions · 3a5698636d sm8x: encode kpool fp8 writes without native fp8 converts · 878631b607 Harden GLM-5.3 FlashInfer integration (port of upstream PR iteration) · 1e6fd4f62e don't inherit main slot mapping for padded kpool tail slots · 36c83fdc92 triton_mla_sparse int64 KV row offsets + hardening · 35fb863a93 strip debugging · 82088a5bd0 merge pr-53906-new (resync with official PR) · 611e908e63 fix MTP and repo ID startup · 3b890f43ed PP via mHC multi-stream hand-off. User-side: d1ba3782f9 (inc: resolve MTP draft modules against checkpoint layer namespace), 3341564b5a (guard fp8_sm80/ple_offload imports), 3bec275739 (scheduler hybrid-allocator KV recovery, shared infra).

### wtdcode Qwen commits (c01b50e390..mitaka/backport, `vllm/models/qwen4_exp` + PLE stack)
d4d0f73ef1 Support Qwen3.8-Flash-Next · d7f50c5290 fix qsa interface · c92e9d6042 fix weight loader mappings · 060089f507 fix qsa kv-cache layout · ea5b4577ec fix PLE profile warmup · 93a769a97b PLE-Offload · d2fda37e28 accept qwen_sparse_attention layer_type alias · c1dda6409c keep MTP draft unquantized for compressed-tensors bf16-MTP · 4d1acaf058 PP for Qwen3.8-Flash-Next with PLE CPU offload + native MTP (+ user 3341564b5a). 26 commits match ple|qsa|qwen4.

## 2. GLM-5.3-Flash — per-file diff notes (official 98ed0856f3/e862c2f45b vs wtdcode d1ba3782f9)

Model files are near-identical (wtdcode resynced via merge `pr-53906-new`):
- `nvidia/model.py` (124 diff lines): (a) wtdcode drops official's `is_kda_layer = not is_mtp_layer and config.is_kda_layer(layer_idx)` guard → draft layer type is config-driven (only observable if the MTP layer idx is inside `layer_types` and typed `linear_attention`; MTP draft layers normally index past `layer_types`, so likely inert); (b) wtdcode adds `make_empty_intermediate_tensors` carrying the full mHC multi-stream state `[tokens, n, hidden]` and materializes deferred `hc_post` at PP boundaries (DSV4 pattern) — official explicitly gates PP off ("Glm5NextForCausalLM does not implement make_empty_intermediate_tensors ... pipeline parallelism is gated off").
- `nvidia/kda.py` (39): official conditionally imports `chunk_kda_with_fused_gate`/`fused_recurrent_kda` from in-tree `models/glm5next/{amd,nvidia}/ops/third_party/kda/`; wtdcode imports them from `vllm.third_party.flash_linear_attention.ops.kda` and lacks the in-tree third_party KDA kernels entirely.
- `nvidia/ops/kpool_compress.py` (187): wtdcode adds `NATIVE_FP8` constexpr + `_encode_e4m3fn_u8`/uint8-view stores (`vllm/v1/attention/ops/fp8_sm80.py`, 177 LOC, absent in official) because "Triton refuses every fp8e4nv convert below SM89" (3a5698636d). Official stores fp8 values natively → SM80/SM86 Triton compile failure.
- `sparse_attn_indexer_kpool.py` (283 diff vs tip): wtdcode has Triton fallback `fp8_paged_mqa_logits_triton`/`fp8_mqa_logits_triton` (`vllm/v1/attention/ops/mqa_logits_triton.py`, 673 LOC, absent in official); official's decode path is ROCm aiter XOR `vllm.utils.deep_gemm.fp8_fp4_paged_mqa_logits` only — no NVIDIA-consumer/Ampere path. wtdcode also int64-promotes KV row offsets (36c83fdc92) and env-gated debug bounds checks (35fb863a93 strips them).
- `indexer.py` (878 diff, mostly base drift): substantive — official `compute_kpool_tail_slot_mapping` still does `out = slot_mapping.clone()`/`out.copy_(slot_mapping)` at e862c2f45b; wtdcode's 1e6fd4f62e fills the padded tail region with -1. Commit message documents the exact official failure: padded cudagraph batches slice `tail_meta.slot_mapping[num_decode_tokens:num_tokens]` and hand main-granularity block ids to `_kpool_tail_seed_kernel` (no upper-bound check) → OOB write; "eager passed every length up to 26k while the first cudagraph replay faulted".
- `v1/worker/gpu/spec_decode/speculator.py`: wtdcode (611e908e63) passes `positions=self.input_buffers.positions[:num_tokens_padded]` into draft attention metadata; official at e862c2f45b builds draft attn metadata without `positions` (only kv_cache_config/causal/seq_lens_cpu_upper_bound).
- `quantization/inc/inc.py`: official has no MTP prefix mapping; user's d1ba3782f9 adds `_mtp_checkpoint_prefix` (maps `model.layers.<i>.mtp_block.*` onto declared `block_name_to_quantize` namespace e.g. `model.language_model.layers.*`), else "every draft module unquantized → loading its quantized weights raises KeyError (w2_qweight missing)".
- `warmup/kernel_warmup.py` (69 diff, base drift) + wtdcode-only `warmup/sparse_mla_triton_warmup.py` (112 LOC, absent in official) — JIT warmup for the Triton sparse-MLA/kpool kernels.
- Infra files (`kv_cache_utils.py` 1137, `gpu_model_runner.py` 612, `config/vllm.py` 434, nixl/mooncake 666/1374, rocm_aiter_mla* ~1000/1131): dominated by fork-base drift (wtdcode forked older official main), not GLM-specific deltas.

## 3. GLM-5.3-Flash — ranked hypotheses for official's runtime failure

1. **No SM80/Ampere compute path for the kpool sparse indexer.** Official decode logits = ROCm aiter XOR DeepGEMM `fp8_fp4_paged_mqa_logits`; kpool FP8 Triton kernels store native fp8e4nv ("Triton refuses every fp8e4nv convert below SM89"). User runs 4x A100 (sm80) → official cannot compile/run the indexer at all. Evidence: official `vllm/model_executor/layers/sparse_attn_indexer_kpool.py` decode branch + `vllm/utils/deep_gemm.py:fp8_fp4_paged_mqa_logits`; wtdcode commits 3a5698636d, `vllm/v1/attention/ops/fp8_sm80.py` (177 LOC) and `vllm/v1/attention/ops/mqa_logits_triton.py` (673 LOC) — both files MISSING at e862c2f45b; wtdcode README "Verified with MTP-3 on 4x A100-80GB (sm80)".
2. **AutoRound/AWQ W4A16 checkpoint: MTP draft quantization resolution fails.** Draft modules built at `model.layers.<i>.mtp_block.*` vs checkpoint namespace `model.language_model.layers.*` → all draft modules marked unquantized → KeyError (w2_qweight) on load. Evidence: user commit d1ba3782f9 (`_mtp_checkpoint_prefix` in `vllm/model_executor/layers/quantization/inc/inc.py`, absent in official); checkpoint is wtdcode/GLM-5.3-Flash-AWQ-W4A16.
3. **kpool tail slot mapping OOB under cudagraph decode.** Official `compute_kpool_tail_slot_mapping` still clones the main slot_mapping; padded (cudagraph) batches pass stale main-granularity block ids to the tail-seed kernel → OOB write, eager passes but first replay faults. Evidence: official `vllm/v1/attention/backends/mla/indexer.py:558-580` at e862c2f45b (`out = slot_mapping.clone()`), wtdcode fix 1e6fd4f62e with detailed failure post-mortem.
4. **MTP draft attention metadata built without token positions.** Official `DraftModelSpeculator` attn-metadata builder omits `positions`; wtdcode's 611e908e63 passes them in ("Pass token positions into draft attention metadata") — GLM draft attention (KDA/MLA + RoPE) computes wrong/misaligned positions without it. Evidence: official `vllm/v1/worker/gpu/spec_decode/speculator.py:327-331`; wtdcode commit 611e908e63.
5. **Missing JIT warmup + minor hardening.** Official lacks `sparse_mla_triton_warmup.py` and wtdcode's FlashInfer/kpool hardening (878631b607 partially ported from upstream; 36c83fdc92 int64 KV row offsets for >4.2M-row KV views i.e. ~1M-context). Lower probability of hard startup failure, but contributes to instability/long-context corruption. Evidence: warmup file MISSING at e862c2f45b; `vllm/v1/attention/ops/triton_mla_sparse_kernel.py` int32 offsets in official.

## 4. GLM-5.3-Flash — strategy & effort

**Recommendation: TAKE_OFFICIAL_PORT_FIXES.** Official's implementation is the superset (in-tree third_party KDA kernels, ROCm AIter sparse, FlashInfer SM90 sparse, mhc.py, kv_cache_interface integration) and wtdcode's deltas are small, well-scoped fixes that can be re-applied as ~7 commits onto official's tree; keeping wtdcode would strand the model on a stale base (no fp8_sm80/mqa Triton files upstream to lean on later, plus 115 divergent fork commits).

Port-effort estimate: ~7 commits, ~1,100–1,300 LOC —
- fp8_sm80.py (177) + kpool_compress NATIVE_FP8 (~80) [3a5698636d]
- mqa_logits_triton.py (673) + indexer decode fallback wiring (~30) [wtdcode-only files]
- inc.py `_mtp_checkpoint_prefix` (~40 + 86 tests) [d1ba3782f9]
- kpool tail slot -1 fill (~30 net across indexer.py/kpool_compress/sparse_attn_indexer_kpool) [1e6fd4f62e, debug hunks dropped]
- speculator positions (~3) [611e908e63]
- sparse_mla_triton_warmup.py (112) + kernel_warmup wiring (~5)
- triton_mla_sparse int64 offsets (~25) [36c83fdc92]
- optional: PP mHC hand-off (56) [3b890f43ed] — only if GLM PP is wanted (user runs TP4, not PP).

## 5. Qwen3.8-Flash-Next — what wtdcode adds over official

Official's implementation works; the QSA/core model files are byte-identical between the two trees (0-diff on `qsa.py`, `ops/qsa*.py`, `hyperconnection.py`, `indexer_qsa.py`, `low_latency_gemm.py`, `config.py` etc.). wtdcode-only additions:
- **PLE CPU offload stack** (official has GPU-resident PLE only): `vllm/model_executor/layers/ple_offload_layer.py` (268 LOC, `PleOffloadLayer`, `is_offload_process`), `vllm/v1/ple_offload/connector.py` (446) + `vllm/v1/ple_offload/worker.py` (672) offload subprocess, `VLLM_PLE_CPU_OFFLOAD` env wired in `vllm/config/parallel.py` (IPC path), `multiproc_executor.py`, `weight_utils.py`, `fix_functionalization.py` — commits 93a769a97b, ea5b4577ec ("fix PLE profile warmup").
- **Qwen4Exp PLE layer integration**: `models/qwen4_exp/nvidia/ple_layer.py` (521-line diff; `Qwen4ExpNGramEmbedding(PleOffloadLayer)` with offload-process forward path, `_offload_weight_scale` handling) + `amd/ple_layer.py` (256-line diff).
- **PP > 1 with PLE CPU offload + native MTP relay**: 4d1acaf058 — stage-local `_has_ple_layers()` in gpu_worker, n-gram buffers on first PP rank only (gpu_model_runner, model_state), skip `hyper_connection_mixer.` checkpoint columns on non-last stages, MTP head on target's last PP rank accepts relayed `hidden_states` (validated TP2xPP2 / TP1xPP4 with MTP-3 on 4x CMP 170HX).
- **MTP draft unquantized for compressed-tensors bf16-MTP checkpoints** (c1dda6409c): extends ct `.ignore` regex list with draft layer indices in `models/qwen4_exp/nvidia/mtp.py` `_make_draft_vllm_config` — needed for AWQ W4A16 exports whose quantization_config ignores `re:.*mtp\..*`.
- **FP8 PLE fixes**: `quantization/fp8.py` `_needs_block_scale_refine` (+ ~124-line diff), `quantization/utils/config_utils.py` (~105-line diff), weight-loader mapping fixes (c92e9d6042).
- **Draft PP config**: `use_qwen4_exp_mtp()` + draft `pipeline_parallel_size=1` (draft runs only on last stage) in `config/speculative.py`.
- User-side: 3341564b5a guards optional accelerator imports in `ple_offload_layer.py`/`fp8_sm80.py` (Jetson/CPU-safe imports); 3bec275739 scheduler hybrid-allocator KV recovery (shared infra).

Taking official's Qwen implementation as-is would LOSE: PLE CPU offload (required by the Jetson PP/PLE profiles — PLE layers would have to stay GPU-resident), PP>1 + MTP-3 under PLE offload, and compressed-tensors/AWQ bf16-MTP draft loading.

**Recommendation: TAKE_OFFICIAL_PORT_FIXES.** Official base is validated at runtime and model files are identical anyway; only the PLE-offload/PP/MTP augmentation stack (~10 commits, ~1,700–1,900 LOC: ple_offload_layer 268 + v1/ple_offload 1,118 + ple_layer integration ~250 + mtp/model_state/gpu_worker/gpu_model_runner gating ~90 + fp8.py/config_utils ~200 + speculative.py ~30) must be re-applied. KEEP_WTD_SKIP_OFFICIAL is viable only if the Jetson PP/PLE profiles must run immediately with zero porting, at the cost of the whole 115-commit fork drift.

## 6. Cross-model risk / interaction

The two choices interact through shared infra; both being TAKE_OFFICIAL_PORT_FIXES, the fix sets must be sequenced and rebased together:
- `vllm/config/speculative.py`: Qwen needs `use_qwen4_exp_mtp` + draft PP=1; GLM needs draft metadata positions — same file, and official's newer `disable_eagle_block_drop`/`hy_v4_mtp` hunks must be preserved.
- `vllm/model_executor/warmup/kernel_warmup.py`: GLM adds `sparse_mla_triton_warmup`; official already carries `qwen4_exp_qsa_warmup` + `replayssm` hooks that wtdcode's older base lacks — merge both, don't drop official's.
- `vllm/v1/worker/gpu_model_runner.py` / `gpu/model_runner.py` / `gpu_worker.py`: touched by both (Qwen PLE/PP gating, GLM kpool paths) — highest-conflict files.
- `vllm/v1/attention/ops/fp8_sm80.py`: introduced for GLM kpool but also imported by wtdcode's deepseek_v4 ampere paths and guarded by user commit 3341564b5a (which also guards `ple_offload_layer.py` — Jetson-relevant for Qwen).
- `vllm/v1/core/sched/scheduler.py` (3bec275739 hybrid-allocator KV recovery) and `vllm/v1/kv_cache_interface.py`/`kv_cache_utils.py`: both models are hybrid-architecture (KDA+MLA / CSA+linear+PLE); official's newer planner versions must be kept, with wtdcode's recovery patch re-evaluated against them.
- `quantization/inc/inc.py`: GLM AutoRound fix; if the Jetson cluster also serves AutoRound checkpoints, it benefits Qwen too.

## 7. Effort summary table

| Model | Strategy | Commits | ~LOC |
|---|---|---|---|
| GLM-5.3-Flash | TAKE_OFFICIAL_PORT_FIXES | ~7 (+1 optional PP) | 1,100–1,300 |
| GLM-5.3-Flash | KEEP_WTD_SKIP_OFFICIAL | 0 | 0 (but stays on drifted base, misses official hardening) |
| Qwen3.8-Flash-Next | TAKE_OFFICIAL_PORT_FIXES | ~10 | 1,700–1,900 |
| Qwen3.8-Flash-Next | KEEP_WTD_SKIP_OFFICIAL | 0 | 0 (loses nothing today, but forfeits official fused-shared-expert + newer planner) |
