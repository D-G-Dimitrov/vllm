# Collision Forecast Heat Map

Cumulative `git cherry-pick -x` dry-run of `c01b50e390..d4d703caf9`
(317 official commits) onto `mitaka/backport`, throwaway worktree.

## Summary counts

- Total commits: **317**
- OK (clean pick): **272**
- CONFLICT: **45**
- EMPTY (possibly already applied): **0**
- Conflicts involving >=1 wtdcode-hot file: **37**
- Env-impact PRs (requirements/, cmake/, pyproject.toml, setup.py): **12**

## Per-PR table (grind order)

| # | outcome | sha | subject | env | conflicted files |
|---|---------|-----|---------|-----|------------------|
| 1 | OK | 9236159bb | [ROCm][CI] Keep startup profiling from aborting when free memory grows (#53591) | no |  |
| 2 | OK | f956e1c34 | [Kimi-K3][Bugfix] Fix low-latency GEMM fallback initialization (#54167) | no |  |
| 3 | OK | 3bb19cd8a | [Bugfix][CI/Build] Fail closed when selected precompiled CUDA variant is unavailable (#52545) | yes |  |
| 4 | OK | 5f213ed15 | [ROCm][CI] Warm up the RLHF dev server before the pause/resume timing checks (#53594) | no |  |
| 5 | OK | d1922cb5a | [Bugfix] Restore multimodal support on the plain "vllm" throughput backend (#52168) | no |  |
| 6 | OK | 94a54f581 | [XPU]bump up vllm_xpu_kernels to 0.1.14.1 (#54203) | yes |  |
| 7 | OK | 11012d2a3 | [Rust Frontend] Reduce copy in auxiliary frame resolution (#54148) | no |  |
| 8 | OK | 06569a869 | [ROCm][Quantization][MOE] Enable fused shared experts for block-quantized FP8 (#53097) | no |  |
| 9 | OK | ffe690eca | [MM][CG] Support ViT full CUDA graph for Idefics3 and SmolVLM (#47625) | no |  |
| 10 | OK | 6f91e3d95 | [Perf] Split xdrope_positions H2D copy into per-row transfers (#53412) | no |  |
| 11 | OK | d9dabfa35 | [Kimi-K3][Kernel] Optimize the low-M fused latent MoE tail (#54168) | no |  |
| 12 | OK | 31c579503 | update quark docs to include online quantization (#52736) | no |  |
| 13 | OK | 2f1cba799 | [ROCm] remove VLLM_ROCM_USE_AITER_FP4_ASM_GEMM environment variable; make w4a4 use the preshuffle triton+asm by default (#53141) | no |  |
| 14 | OK | 67e86d1e6 | [BugFix] Bind RayExecutorV2 TCPStore before publishing its port (#50969) | no |  |
| 15 | OK | 06cccf873 | [Bugfix] Fix int32 token offset overflow in fused SiLU block quant (#53409) | no |  |
| 16 | OK | 74850f9f6 | [Rust Frontend] Optimize SSE streaming hot path (#51321) | no |  |
| 17 | CONFLICT | 21fa2c5a2 | [Mypy] Fix mypy typing for model interfaces and H/I models (#54079) | no | vllm/model_executor/models/interfaces.py |
| 18 | OK | 70732942c | [Bugfix][ROCm] Pre-allocate `wvSplitKrc` static workspaces before KV init (#54247) | no |  |
| 19 | OK | 96242aa50 | [Bugfix][MRV2] Release layer-bound KV cache memory in shutdown() (#54246) | no |  |
| 20 | OK | 2aac565ca | [Core][KV Connector] Start async KV loads after the forward launch when no sync loads are scheduled (#53333) | no |  |
| 21 | OK | c274d3610 | [Bugfix] Keep the Moondream3 MoE all-reduce out of the fused-path try (#54152) | no |  |
| 22 | OK | fd98d32f7 | [ROCm][CI] Fix test_ray_v2_executor (#54249) | no |  |
| 23 | OK | df14152ac | [Model] Support speculative decoding method for PLaMo3 (#54239) | no |  |
| 24 | OK | b131311fb | [CI/Build] Add advisory PR title format check (#54263) | no |  |
| 25 | OK | ae5b8e4a8 | [ROCm][PERF] Enable AITER PA gluon decode for MiniMax-M3 MTP and dense layers (#52849) | no |  |
| 26 | OK | 9662ab083 | [Bugfix] Set breakable graph env before Ray actor import (#53293) | no |  |
| 27 | OK | 1a16c2ad2 | [CI][Test] Deflake the rms_norm scaling-property assertions (#54271) | no |  |
| 28 | OK | 085e9bb07 | [Rust Frontend] Add support for `truncate_prompt_tokens` and `truncation_side` (#48584) | no |  |
| 29 | OK | 68c52b5a9 | fix: improve token_ids_cpu swap to copy only valid indices (#36255) | no |  |
| 30 | OK | 026d5af7f | [Bugfix] Fix ncclCommQueryProperties heap overflow with NCCL >= 2.31 (#53008) | no |  |
| 31 | CONFLICT | 99013d77d | [Bugfix][Distributed] Gate cross-node MNNVL custom all-reduce by group capability (#53253) | no | tests/distributed/test_custom_all_reduce.py |
| 32 | OK | 4c6c9d569 | [Rust Frontend] Take the raw buffer in mm tensor lowering when possible (#53528) | no |  |
| 33 | OK | 43196f245 | [Perf][MLA Sparse] Pin req_id_per_token before non_blocking H2D on XPU and ROCm (#54295) | no |  |
| 34 | OK | 7fd9cc036 | [KV Connector] Support MooncakeStore with hybrid DCP prefix caching (#53324) | no |  |
| 35 | OK | 16d6c376b | [Bugfix][Models] Register sleep-managed runtime buffers (#53507) | no |  |
| 36 | OK | 6b110badb | [Bugfix][Mooncake] Save exact Mamba boundary states (#51358) | no |  |
| 37 | OK | 93ab92be0 | [Bugfix][AMD] Annotate draft KV cache groups on the hybrid grouping path (#52047) | no |  |
| 38 | OK | 46a83642f | [Perf] Pin CPU tensors before non_blocking H2D in three MM paths (#54292) | no |  |
| 39 | OK | 738bc8811 | [BugFix] Disable TP for Qwen3-Omni audio encoder when heads % TP != 0 (#50858) | no |  |
| 40 | OK | 5182f2705 | [CI/Build] Use file rendezvous for UniProc loader fixtures (#52367) | no |  |
| 41 | OK | 6c18a5464 | [Perf] Avoid h2d copies from non-pinned CPU tensors (#54299) | no |  |
| 42 | CONFLICT | b2f685834 | [Hy4] support Hy4-preview model (#54160) | no | vllm/v1/worker/gpu/spec_decode/speculator.py |
| 43 | CONFLICT | 6d4562c59 | [Attention][DCP] Enable FlashInfer MLA for DSpark drafting (#54277) | no | tests/v1/spec_decode/test_eagle_draft_attn_metadata.py, vllm/v1/kv_cache_interface.py |
| 44 | OK | 3958a420f | [Bugfix][V1] Keep an encoder cache entry until its last occurrence is freed (#54284) | no |  |
| 45 | OK | fb6802513 | [Bugfix][MRV2] Release model and KV cache on in-process engine shutdown (#54162) | no |  |
| 46 | OK | f4f3bcd4b | [Test] Assert co-located RayExecutorV2 stores publish distinct ports (#54310) | no |  |
| 47 | OK | a758a9f67 | [Perf][KV Connector] Pin token_indices before non_blocking H2D in hf3fs helper (#54293) | no |  |
| 48 | OK | d3d79ffc1 | [Bugfix][Spec Decode] Capture the widest uniform decode batch by default (#50488) | no |  |
| 49 | OK | cacc429f6 | [ROCm][CI] Stage E gating (#50920) | no |  |
| 50 | CONFLICT | fd5d3aea9 | [Mypy] Fix typing for J models (#54130) | no | tools/pre_commit/mypy.py |
| 51 | OK | 4fc943b86 | [Multimodal] Deprecate PyAV video decoder backend (#54231) | no |  |
| 52 | CONFLICT | 7f4793eaa | [Nixl][PD] DCP support for MLA models   (#50611) | no | tests/v1/worker/test_gpu_model_runner.py, vllm/model_executor/layers/sparse_attn_indexer.py |
| 53 | OK | 129087dda | [Perf] Reuse topk SparseMatrix routing metadata in GPT-OSS MoE forward (#45457) | no |  |
| 54 | OK | 5b0e5b69a | [Bugfix][Frontend] Validate stop_token_ids against vocab size (#54196) | no |  |
| 55 | OK | 7fbfca267 | [Bugfix][Frontend] Only echo the assistant turn in batched chat completions (#52529) | no |  |
| 56 | CONFLICT | fe755c889 | [Bugfix][Model Runner V2][Spec Decode] Decouple the draft's gumbel noise stream from the target's (#54282) | no | vllm/v1/worker/gpu/spec_decode/autoregressive/speculator.py |
| 57 | OK | 6cddad414 | [CI][Test] Deflake test_mem.py sleep-mode asserts via allocator bookeeping (#54312) | no |  |
| 58 | OK | 680e2177e | [CI][Ray] Fix flaky multi-node assignment test after placement-group teardown (#53621) | no |  |
| 59 | OK | b5707bf99 | [Bugfix][MoE] Enable cuBLAS out_dtype router GEMM on all CUDA archs (fixes family-120/GB10) (#54048) | no |  |
| 60 | OK | dbf662c9e | [ROCm][MLA] Reach FULL cudagraphs for AITER MLA speculative decoding (#51171) | no |  |
| 61 | OK | b016ed8ea | [Bugfix][Multimodal] Release Qwen2.5-VL and Qwen3-VL RoPE caches with the model (#54346) | no |  |
| 62 | OK | 7a67941c1 | [Rust Frontend][gRPC] Add audio and video media inputs (#53760) | no |  |
| 63 | OK | 1ebff996a | [Fix] Improve ROCm detection in WSL environments (#38434) | no |  |
| 64 | OK | 1dc464d42 | [Bugfix] Bound cache_salt length to prevent DoS via scheduler CPU exhaustion (#54353) | no |  |
| 65 | OK | 8fa4c6cdb | [CI] Add explicit step keys to 18 hardware test steps (#54330) | no |  |
| 66 | OK | b383e1639 | [Bugfix] Reset cached Mamba align metadata on profiling teardown (#54044) | no |  |
| 67 | OK | 4f78a8fdd | [Model] Honor cap_pixels_per_frame in Qwen3-VL memory profiling (#54380) | no |  |
| 68 | OK | 2c7d7dd64 | [Perf][ROCm] Dual-stream decode with hipgraphs (#52033) | no |  |
| 69 | CONFLICT | 8c51b9265 | [Bugfix] Avoid global config lookup in sparse indexer forward (#54400) | no | vllm/model_executor/layers/sparse_attn_indexer.py |
| 70 | OK | 78fa18910 | ci: add MIG slice size to H200 job labels (#54420) | no |  |
| 71 | OK | 5e71a11eb | [CI] Mark L4 GPU test steps with device: l4 for EKS migration (#54326) | no |  |
| 72 | CONFLICT | 488b6da10 | [Doc] Fix griffe warnings in HYV4 tool parser (#54412) | no | vllm/tool_parsers/hy_v4_tool_parser.py |
| 73 | OK | fe6db3ed5 | [Bugfix] Validate scale-out transfer params (#54324) | no |  |
| 74 | OK | 87b9b5b8d | [Test][VLM] Add batch-invariance tests for Qwen3-VL (#53531) | no |  |
| 75 | OK | 56058fd57 | [Bugfix][Kernel] Keep packed GDN decode beta in FP32 (#53877) | no |  |
| 76 | OK | f6895a5fc | [Bugfix][Multimodal] Avoid caching full prompts in fallback (#54439) | no |  |
| 77 | OK | e79961c94 | [codeowners] Add jperezdealgaba to security file ownership (#54358) | no |  |
| 78 | OK | 9d0fe9bac | [Bugfix][Quantization][MoE] Route weight only NVFP4 checkpoints through W4A16 (#54427) | no |  |
| 79 | OK | b2dc864bb | [Bugfix][Spec Decode] Keep default CUDA graph sizes memory-safe (#54418) | no |  |
| 80 | OK | 7a100bb61 | [CI] Restore gpu_1_queue routing for torch-abi audit (#54468) | no |  |
| 81 | CONFLICT | 7ab292348 | [Flashinfer] Upgrade Flashinfer version to 0.6.18 (#54313) | yes | docker/Dockerfile, docker/versions.json |
| 82 | CONFLICT | c92b29a1d | [Bugfix] Make metadata send non-blocking in GroupCoordinator.isend_tensor_dict (#49274) | no | vllm/v1/worker/gpu_worker.py |
| 83 | OK | 570735520 | [Bugfix][MLA] Fix BLHNC addressing for FlashInfer sparse MLA (#54465) | no |  |
| 84 | OK | 555ea65e8 | [Frontend] Add video embeds input support (#54242) | no |  |
| 85 | OK | 648b7468b | [CI/Build] Fix Kimi K3 Eagle3 test fixture (#54482) | no |  |
| 86 | OK | 44fe2a392 | [CPU] add CPU support for Voxtral (#53921) | no |  |
| 87 | OK | 687db5974 | [Bugfix][Frontend] Truncate pooling prompts before padding them (#54364) | no |  |
| 88 | CONFLICT | e126687a9 | [Model] Support Qwen3.8-Flash-Next (#53896) | no | tests/distributed/test_custom_all_reduce.py, tests/models/qwen4_exp/test_config.py, tests/models/qwen4_exp/test_ple.py, tests/models/qwen4_exp/test_qsa_amd.py, tests/models/qwen4_exp/test_qsa_reference.py, tests/v1/core/test_contiguous_kv_packing.py, tests/v1/core/test_kv_cache_utils.py, tests/v1/kv_connector/unit/test_nixl_desc_geometry.py, tests/v1/kv_connector/unit/test_tp_mapping.py, tests/v1/worker/test_gpu_autoregressive_speculator.py, tests/v1/worker/test_gpu_model_runner_v2.py, vllm/config/compilation.py, vllm/distributed/kv_transfer/kv_connector/v1/nixl/base_worker.py, vllm/model_executor/models/config.py, vllm/model_executor/models/interfaces.py, vllm/models/qwen4_exp/amd/model.py, vllm/models/qwen4_exp/amd/mtp.py, vllm/models/qwen4_exp/amd/ple_layer.py, vllm/models/qwen4_exp/common/ple.py, vllm/models/qwen4_exp/config.py, vllm/models/qwen4_exp/nvidia/model.py, vllm/models/qwen4_exp/nvidia/model_state.py, vllm/models/qwen4_exp/nvidia/mtp.py, vllm/models/qwen4_exp/nvidia/ple_layer.py, vllm/platforms/interface.py, vllm/v1/core/kv_cache_coordinator.py, vllm/v1/core/kv_cache_utils.py, vllm/v1/core/single_type_kv_cache_manager.py, vllm/v1/kv_cache_interface.py, vllm/v1/worker/gpu/model_runner.py, vllm/v1/worker/mamba_utils.py |
| 89 | OK | 8fd9eb85d | [Bugfix][Frontend] Truncate prompt_token_offsets with the prompt (#54407) | no |  |
| 90 | OK | 4ae172231 | [Frontend] Forward cache salt for content parts (#54315) | no |  |
| 91 | OK | 7292ee279 | [Bugfix][Multimodal] Honor modality-scoped mm_processor_kwargs (#53808) | no |  |
| 92 | CONFLICT | da0b2d8b1 | [Performance] Optimize Dots3 NOTE runtime (#53517) | no | vllm/config/vllm.py |
| 93 | CONFLICT | 8e92248f7 | [Kernel] Retire the DSv3 router GEMM CUDA kernel  (#54040) | no | vllm/model_executor/layers/fused_moe/router/gate_linear.py |
| 94 | OK | f9d666f91 | [KV Offload] Forward ownership in KV cache events (#52067) | no |  |
| 95 | OK | 2cf82bcdd | [Bugfix][DCP] Fix NVIDIA DeepSeek-V3.2 / GLM-5.2 fused attention (#50005) | no |  |
| 96 | OK | fdbf2ddbd | [Bugfix][CPU] Fix several bugs (#54042) | no |  |
| 97 | OK | 2a61f060d | [XPU] Ensure unquantized linear weight is N-contiguous (#53536) | no |  |
| 98 | OK | c6c33f2b1 | [CPU] Support FP16/BF16 persisted GDN state on AMX (#52191) | no |  |
| 99 | OK | 1b9539d37 | [Quantization][Autoround][XPU] Support AutoRound MXFP8 MoE models (#51248) | no |  |
| 100 | OK | 5bfd76372 | [Renderer] Shutdown the renderer properly.  (#52124) | no |  |
| 101 | OK | 399247cc8 | [Bugfix][MM] Fix MiniCPM-o image processor reuse on Transformers v5 (#54501) | no |  |
| 102 | OK | 28bf75c9a | [Bugfix][Frontend] Truncate prompt_is_token_ids with the prompt (#54509) | no |  |
| 103 | OK | 699e180df | [Bugfix][SM120] DSv4: pass contiguous C128A decode topk indices on SM120 (#53574) | no |  |
| 104 | OK | d8de4ae32 | [Bugfix][KVOffload] P2P tier declares REQUEST_LEVEL on the producer leg (#52912) | no |  |
| 105 | CONFLICT | eeb549a74 | [Frontend] Move engine/protocol.py out openai folder (#54492) | no | vllm/reasoning/hy_v4_reasoning_parser.py, vllm/tool_parsers/hy_v4_tool_parser.py |
| 106 | OK | 9acbc5360 | [KV Offload] Preserve KV event metadata until final residency removal (#52068) | no |  |
| 107 | OK | 9debcd599 | [Test][Qwen3-VL] Cover compiled DeepStack input contract (#53529) | no |  |
| 108 | OK | 810bc3250 | [Frontend][Performance] Resolve async media across modalities concurrently (#54537) | no |  |
| 109 | OK | bed3280f5 | [KV offload] Order CPU->GPU loads against the compute stream (#50696) | no |  |
| 110 | OK | e2c8eeac4 | [kernel] Fused embedding kernel  (#53677) | no |  |
| 111 | OK | e0d27040d | [Bugfix][KV Offload][P2P] Preserve aborted loads until abort completion (#52571) | no |  |
| 112 | CONFLICT | 4c58a0c39 | [Bugfix][KV Offload] Unlink /dev/shm region after all workers map it (barrier variant of #51317) (#52596) | no | vllm/v1/kv_offload/cpu/shared_offload_region.py |
| 113 | OK | c5d840ff6 | [KV Connector][Offloading] Certify attention-only hybrids in the canonical portability gate (#51689) | no |  |
| 114 | OK | 76ff0cdff | [Bugfix][ROCm] Preserve AITER unified-attention metadata during graph replay (#53821) | no |  |
| 115 | CONFLICT | dafbef15a | [Core] Add `max_num_queued_reqs` and `max_num_queued_tokens` for queue size management (#49445) | no | tests/entrypoints/openai/chat_completion/test_serving_chat.py, vllm/exceptions.py |
| 116 | CONFLICT | bd575a0d0 | [AutoRound] Support AutoRound Format Block-Wise FP8 in vLLM (#47434) | no | vllm/model_executor/layers/quantization/inc/inc.py |
| 117 | OK | 82936c409 | [Tests][XPU] Limit Qwen2-VL generation length to avoid flaky numerical divergence (#54172) | no |  |
| 118 | OK | 3593c964d | [ROCm] Add TheRock preview docker updates, Keep Python 3.12 and Ubuntu 22.04 (#49925) | yes |  |
| 119 | OK | e9dd6d483 | [CI] Exclude kv_transfer changes from broad spec-decode/kernels/multimodal triggers (#54365) | no |  |
| 120 | OK | 39e276eae | [Structured Output] Let terminal grammars stop under min_tokens (II) (#54218) | no |  |
| 121 | OK | dbb7fffdd | [ROCm][MLA][DCP] Support causal multi-token verification (#51705) | no |  |
| 122 | OK | 2ba984a5d | [ROCm][DSpark][DCP] Serve prefix cache hits under DCP for Kimi-K3 (#53598) | no |  |
| 123 | OK | 65ce85fcd | Add Laguna-XS-2.1-INT4 to nightly CI (#52961) | no |  |
| 124 | OK | f5e441de1 | [Bugfix][Test] Fix off-by-one error in sampled token rank causing flaky logprobs test (#53976) | no |  |
| 125 | OK | f9c7c6e09 | [Rust Frontend][CI] Remove TCP port races from mock-engine tests (#54481) | no |  |
| 126 | OK | a9dc63142 | [Bugfix] Reject empty bad-word tokenizations (#53433) | no |  |
| 127 | OK | 85c1365bd | [Bugfix] NemotronHMTP: add hf_to_vllm_mapper so quant exclusions reach the MTP draft (#53790) | no |  |
| 128 | CONFLICT | f5c3cc240 | [Perf][Kernel] Tune cooperative topk for medium batch-sizes (#53382) | no | vllm/model_executor/layers/sparse_attn_indexer.py |
| 129 | OK | 24d42f355 | [CI] Mark 1-GPU L4 test steps with device: l4 for EKS migration (#54549) | no |  |
| 130 | OK | d61b6e187 | [Bugfix][Spec Decode] Take the DFlash draft's RoPE layout from its own config (#54373) | no |  |
| 131 | OK | 07ea9350b | [Kernel][Gemma4] Prune Triton sliding-window tiles for multimodal prefixes (#53147) | no |  |
| 132 | OK | d6d665854 | [Kimi-K3][Perf] Make native CUDA AttnRes the SM100 default (#54261) | no |  |
| 133 | OK | 3a2ed6cba | [Kimi Bug] Fix gdn build_attn_metadata `'KimiK3KDAMetadataBuilder' object has no attribute 'layer_names'` (#54636) | no |  |
| 134 | OK | 91752b7a3 | [K3 Bug] Fix Kimi-K3 RecoverSSM startup failure `'MambaAttentionBackendEnum.GDN_ATTN declares 4 states, but provides 2 state copy funcs'` (#54634) | no |  |
| 135 | OK | b05acd2ae | [XPU] [CI] Add retry for v1/sample in Intel GPU CI (#53669) | no |  |
| 136 | CONFLICT | 6bafc049a | [Bugfix][PP] Never drop a decoding request from the sampled-token broadcast (#54436) | no | tests/v1/worker/test_pp_utils.py |
| 137 | OK | 89df6fcb8 | [CI] Broaden structured-output issue auto-labeling (#54645) | no |  |
| 138 | OK | d4329ba53 | [Bugfix][Rust Frontend] Fix adjacent DeepSeek V4 user content rendering (#53281) | no |  |
| 139 | OK | e29af0a2a | [XPU] bump up auto-round-lib to 0.15.0 (#54515) | yes |  |
| 140 | OK | 8600db5df | [CI] Build CPU image against torch nightly for TORCH_NIGHTLY runs (#48750) | no |  |
| 141 | OK | 4c21d4173 | [XPU] Route activation CustomOps to SYCL kernels (#53734) | no |  |
| 142 | OK | 58dace61f | [Kernel] Make prefix-prefill tiling independent of the KV page size (#54194) | no |  |
| 143 | OK | 22df3a34e | [Perf][Rust Frontend] Count the tokenizer vocabulary once at construction (#54449) | no |  |
| 144 | OK | 45aed9b0c | [CI] Broaden tool-calling issue auto-labeling (#54650) | no |  |
| 145 | OK | 225aec480 | [Rust Frontend] Migrate to new tekken crate (#53056) | no |  |
| 146 | CONFLICT | c28feab98 | [Core][MRV2] Freeze gc during V2 CG capture; skip per-descriptor cleanup (#54646) | no | vllm/v1/worker/gpu/model_runner.py |
| 147 | OK | 907b1a7f2 | [CI][ROCm] Avoid redundant image pulls during smoke validation (#54408) | no |  |
| 148 | OK | 882ca8d69 | [Kernel] add Flashinfer cutedsl w4a16 linear (#53014) | no |  |
| 149 | OK | 923949e6e | [Feat] Add request-level preemption count histogram metric (#49984) | no |  |
| 150 | OK | 188716ace | [Bugfix][EC Connector] Fall back when MADV_POPULATE_WRITE is unsupported (#53190) | no |  |
| 151 | CONFLICT | e16b5e518 | [1/N][warmup][DSv4] Migrate generic MLA metadata and indexing kernels (#50175) | no | vllm/model_executor/warmup/kernel_warmup.py, vllm/model_executor/warmup/sparse_mla_triton_warmup.py, vllm/models/deepseek_v4/attention.py, vllm/v1/attention/backends/mla/indexer.py, vllm/v1/attention/backends/mla/sparse_utils.py |
| 152 | CONFLICT | 446c76948 | [Distributed] Add opt-in FlashInfer PCIe IPC all-reduce backend (#53576) | no | vllm/distributed/device_communicators/cuda_communicator.py |
| 153 | OK | dc9114b20 | [ROCm][MoE] Split AITER CK and Triton MXFP4 W4A16 into separate backends (#50622) | no |  |
| 154 | OK | ce2e343be | [ROCm] Keep GLM-5.2 on MRV1 and disable default breakable cudagraph (#53155) | no |  |
| 155 | CONFLICT | 7c5dc571c | [Attention][DSA] Enable W4A16 DSA (#51724) | yes | tests/v1/attention/test_sparse_mla_backends.py |
| 156 | OK | 40b2f6206 | [ROCm][CI] Stabilize the sqrt-softplus top-k tie oracle (#54403) | no |  |
| 157 | OK | 30dd1a795 | [DecodeBenchConnector] Fix HMA cache-group mapping (#54647) | no |  |
| 158 | OK | ff0c3cb03 | [Bugfix][Frontend] Truncate the assistant tokens mask with the prompt (#54539) | no |  |
| 159 | OK | ec32f669b | [Feature][MM_UUIDs] Allow empty video URLs when using multi-modal UUIDs (#54220) | no |  |
| 160 | CONFLICT | 4ac452ad9 | [Core] Release NCCL communicator memory in sleep mode (#51485) | no | vllm/v1/worker/gpu_worker.py |
| 161 | OK | fa99a6fea | [Bugfix][Security] Bound the validation-error response body (#54684) | no |  |
| 162 | OK | d0e695a91 | [Distributed] Support pre-shared ncclUniqueId rendezvous for weight transfer (#53784) | no |  |
| 163 | OK | 63988f3c2 | [Quantization][Refactor][1/N] Adopt `QuantKey` in `QuarkConfig` and methods, relying on `weight_quant_key`, `act_quant_key` for quant method dispatch (#52958) | no |  |
| 164 | OK | b65af5e33 | [CI][ROCm] Expand weight loading test coverage on AMD and cap its KV cache (#54037) | no |  |
| 165 | OK | 890563368 | [Bugfix][Frontend] Preserve token offset origins after left text pre-trimming (#54692) | no |  |
| 166 | OK | ce7391712 | [Bugfix][Security] Bound embedding densification before to_dense() (#54632) | no |  |
| 167 | OK | 5414b4e69 | [XPU][TEST] Add entrypoints test in Intel GPU CI (#53980) | no |  |
| 168 | OK | 4707679cd | [Bugfix][MiniCPM-V] Route video_embeds to the shared vision parser (#54633) | no |  |
| 169 | OK | c35551f89 | [Bugfix][KV Offload] Isolate tiering shutdown failures (#52290) | no |  |
| 170 | OK | 8f03625b3 | [CPU][Zen] Route Int8 MoE inference through zentorch on AMD (#44834) | no |  |
| 171 | OK | 504bb8b0c | [CI] Add repository-local OTel tracing helpers (#52851) | no |  |
| 172 | OK | 754d5e1f6 | [CI/Build] Fix entrypoints coverage (#54750) | no |  |
| 173 | OK | 92ccd2c30 | [Bugifx][INC] Fix INC quantization method selection for non-quantized layers (#47237) | no |  |
| 174 | OK | 9e905f745 | [Bugfix] Account for client queue time in serve benchmarks (#54136) | no |  |
| 175 | OK | 481839ad9 | [Feature][Spec] Support disabling trailing prefix-cache block dropping (#53388) | no |  |
| 176 | OK | 191cecd51 | [Kernel][Qwen] Add Hopper LL-GEMM tuning table for Qwen4Exp (#54560) | no |  |
| 177 | OK | 40824284b | [Doc] Document FP8 GEMM kernel selection and Blackwell support (#49936) | no |  |
| 178 | OK | 55aa766dc | [Bugfix][Model] Fix GraniteMoeHybrid per-expert quantized weight loading (#54052) | no |  |
| 179 | OK | 1f1f62885 | [Feat][MM Hashing]  include media_io_kwargs in multi-modal hashes (#54241) | no |  |
| 180 | OK | 25efcfa78 | [Attention] Enable adaptive verification for FLASHINFER_MLA_SPARSE_DSV4 (#52724) | no |  |
| 181 | CONFLICT | adebc41b7 | [Mamba] Add FlashInfer ReplaySSM backend (#52506) | no | vllm/model_executor/warmup/kernel_warmup.py |
| 182 | CONFLICT | 0d4ad4798 | [Kernel] Add B12X causal paged attention backend (#52017) | yes | vllm/v1/attention/backends/registry.py |
| 183 | OK | 339e16cbb | [Bugfix] Support MCP SDK 2.x tool input schemas (#53870) | yes |  |
| 184 | OK | d9eb4e344 | [Bugfix] Reject tokenless chat and audio streams (#54708) | no |  |
| 185 | OK | 76f3249fb | [Mypy] Fix typing for M models (#54262) | no |  |
| 186 | OK | a232e29e9 | [Bugfix] Gate sm_100-only kernel tests on the capability family, not >= (#54306) | no |  |
| 187 | OK | 82b7d49a6 | [MoE] Generalize masked activation for padded layouts (#51217) | no |  |
| 188 | OK | f1e5fdd7f | [Transformers backend] Replace vocab embeddings in `recursive_replace` (#54760) | no |  |
| 189 | OK | cdefd9d49 | [Bugfix] Support Sentence Transformers 5.4+ serialized configs (#54533) | no |  |
| 190 | OK | 514c7314a | [Perf][Kernel] Initialize NVFP4 padding in quant kernel (#53568) | no |  |
| 191 | CONFLICT | 2fe5cef35 | [Fix] Fix FSE compatibility detection for Quark-produced models (#54573) | no | tests/model_executor/layers/test_fused_shared_expert.py |
| 192 | OK | c866ba9d1 | [KV Connector] Support heterogeneous TP sharing in Mooncake Store Connector (#53129) | no |  |
| 193 | OK | 2f0103966 | [Misc] Share Buildkite CI failure skill across agents (#54806) | no |  |
| 194 | CONFLICT | e7cf4730d | [Bugfix] Drop incomplete tool-call markup in non-streaming to match streaming (#47562) | no | vllm/parser/engine/streaming_parser_engine.py |
| 195 | OK | d1c15e589 | [CI] Speed up quantization test group (#53291) | no |  |
| 196 | OK | 0ad5652a5 | [Bugfix][Frontend] Restore the chat template content format mismatch warning (#54622) | no |  |
| 197 | OK | d98bb2a87 | [Bugfix][Frontend] Honor skip_decoder_start_token in async encoder-decoder rendering (#54799) | no |  |
| 198 | OK | 6c58595c2 | [Feature] Avoid flashinfer autotune each time when vllm source change (#54794) | no |  |
| 199 | OK | c0adee923 | [ROCm][CI] Add ROCm misc ops and env tests (#53279) | no |  |
| 200 | OK | aa71f9bcc | [Bugfix] Log platform plugin detection failures (#52285) | no |  |
| 201 | OK | ab54f5bd8 | [Chore] Remove redundant `_pack_topk_ids_weights_kernel` in TrtLLM NvFP4 MoE (#46872) | no |  |
| 202 | OK | 3439bad37 | [Rust Frontend] Bound recursive argument parsers (#54303) | no |  |
| 203 | OK | 73723b707 | [ROCm][MoE] Fix gfx950 block scale swizzle for AITER Triton MXFP4 W4A16 (#54773) | no |  |
| 204 | OK | 55178f2d0 | [Bugfix][Profiler] Fix API server crash on double /stop_profile (#51678) | no |  |
| 205 | OK | 7cb9a88f5 | [Bugfix][Mooncake] Offload producer partial tails on request finish (#52832) | no |  |
| 206 | CONFLICT | 5cc32fbdf | [Bugfix][KV Connector] Fix Mooncake physical-block transfer length (#54272) | no | vllm/distributed/kv_transfer/kv_connector/v1/mooncake/mooncake_connector.py |
| 207 | OK | dc5cf437c | [Rust Frontend] Enable Qwen4-exp multimodal support (#54813) | no |  |
| 208 | OK | 4bf06be98 | [CI] Disable CUDA graphs for GLM PCP evals (#54745) | no |  |
| 209 | OK | 7a977c069 | [ModelOpt] Redesign the LinearMethod classes using the generic QuantKey-driven method (#49381) | no |  |
| 210 | OK | 16f16876f | [CI] Read the CRCR report token from a Buildkite secret (#54605) | no |  |
| 211 | OK | 18c53727c | [Bugfix][KV Connector] Fix DecodeBench DCP block selection (#54679) | no |  |
| 212 | OK | ce6a283c0 | [Bugfix] Restore `weight_dtype` in `QuarkW8A8Fp8MoEMethod` to fix GPT-OSS FP8 MoE weight loading (#54824) | no |  |
| 213 | OK | fc72fc39a | [Kimi Bug] Fix `cannot access local variable 'active_non_spec_mask_cpu'` (#54781) | no |  |
| 214 | OK | a56e74afd | [CI] Remove MRV2-specific tests (#54823) | no |  |
| 215 | OK | 259a209bf | [Kimi-K3][Perf] Prefetch ll_bf16 router weights for M=1 (#53524) | no |  |
| 216 | OK | b911fe85c | [Rust Frontend] Attribute decoded text to tokens (#52910) | no |  |
| 217 | OK | e90b608c4 | [CI] Split nightly MTP acceptance tests (#52353) | no |  |
| 218 | OK | 96031b862 | [CI] Shard distributed model jobs above the 24h P90 threshold (#54752) | no |  |
| 219 | OK | 3b6c0bdae | [CI] Shard long kernel test groups (#54754) | no |  |
| 220 | OK | e01d4acbb | [ROCm][CI] Handle tied experts in softplus sqrt top-k test (#52679) | no |  |
| 221 | OK | 80389cfed | [CI/Build] Gate PR title check on ready PRs & use slim runners (#54827) | no |  |
| 222 | CONFLICT | 003e34341 | [Qwen3.8-Flash-Next] Separate prefill and decode paths for QSA indexer (#54513) | no | tests/models/qwen4_exp/test_qsa_reference.py, vllm/model_executor/warmup/kernel_warmup.py |
| 223 | OK | 46c8a161f | [Bugfix] Handle padded routes in CUTLASS MoE permutations (#54747) | no |  |
| 224 | OK | dbf1a044e | [Bugfix] Fix ColQwen3.5 pooler projector initialization (#54847) | no |  |
| 225 | OK | 12b9573c9 | [Bugfix][KV Offloading] Fix eager SimpleCPUOffload cache registration and final flush (#53532) | no |  |
| 226 | CONFLICT | 3ba9907a1 | [Kimi-K3] Overlap low-M TP8 KDA projections (#54697) | no | vllm/model_executor/warmup/kernel_warmup.py |
| 227 | OK | a566ea7e8 | [Perf] Avoid more h2d copies from non-pinned tensors (#54660) | no |  |
| 228 | OK | 1d8d7a396 | [Bugfix] Fix RoPE construction for deepseek-v4 sparse SWA layers (#54815) | no |  |
| 229 | OK | ee3c00bbf | [Performance] Register Triton W4A16 GEMM as a custom op (#51453) | no |  |
| 230 | CONFLICT | 1e300895a | [Qwen4] validate FP8 PLE weight scale after loading (#54722) | no | tests/models/qwen4_exp/test_ple.py |
| 231 | CONFLICT | 396c5a563 | [Bugfix] Lazy-import FlashInfer PCIe IPC all-reduce in kernel_warmup (#54869) | no | vllm/model_executor/warmup/kernel_warmup.py |
| 232 | OK | 05201d8ec | [CI] Shard basic model initialization tests (#54753) | no |  |
| 233 | CONFLICT | f870b9297 | [Qwen3.8-Flash-Next] Fuse Qwen4Exp PLE kernels (#54517) | no | tests/models/qwen4_exp/test_ple.py, vllm/models/qwen4_exp/nvidia/ple_layer.py |
| 234 | OK | 73029d424 | [CI][ROCm] Calibrate AMD test timeouts from nightly runtimes (#54695) | no |  |
| 235 | OK | ad76610c4 | [XPU][CI] Move heavy jobs to nightly test in Intel GPU CI (#54863) | no |  |
| 236 | OK | 56b549537 | [ROCm][AMD][Installation] Add mooncake build to rocm base image (#52650) | no |  |
| 237 | OK | aae36577f | [XPU][UT] skip fp8_per_channel test on XPU (#54861) | no |  |
| 238 | OK | 3976eada8 | [CI] Use PR head label for Buildkite branch to avoid main collision (#54895) | no |  |
| 239 | CONFLICT | 300f68832 | [Bugfix] Implicitly close DeepSeek DSML parameters (#54838) | no | vllm/parser/deepseek_v32.py |
| 240 | OK | c00091e02 | [Frontend] Gate scale-out endpoints behind opt-in flag (#54579) | no |  |
| 241 | OK | f4e613614 | [Kimi-K3] Bump FlashKDA to fix unstable inverse (#54859) | yes |  |
| 242 | OK | 798b557e0 | [Frontend] Add site-packages support for reasoning/tool parser plugins (#45241) | no |  |
| 243 | OK | df09c7673 | [KV Connector][Offloading] Look through UniformTypeKVCacheSpecs in the canonical portability gate (#51690) | no |  |
| 244 | OK | 1b4b2a18b | [CI] Shard H100 MoE refactor integration tests (#52352) | no |  |
| 245 | OK | 62588e059 | [CI] Batch the swap_blocks verification instead of copying block by block (#54558) | no |  |
| 246 | OK | 878ec4bfe | [CI] Shard entrypoints API-server tests (#52344) | no |  |
| 247 | OK | c23e15be9 | [CI][Fix] Resolved the Ascend NPU test build image fail and add file dependencies (#50504) | no |  |
| 248 | OK | b2558f8da | [Bugfix] Fix launch render hanging on shutdown (#54913) | no |  |
| 249 | OK | f5711fa13 | [CI] Shard LoRA TP distributed tests (#52350) | no |  |
| 250 | OK | 01eeb798b | [CI][AMD] Preserve diagnostics for unwritable checkouts (#53437) | no |  |
| 251 | OK | 8052102c2 | [Bugfix] Fix cross-batch buffer race corrupting DiskBackend loads (#51667) | no |  |
| 252 | CONFLICT | e52407ef4 | [ROCm][CI] Add MTP and other spec-decode acceptance coverage (#53399) | no | vllm/v1/spec_decode/gemma4.py |
| 253 | OK | c6005000d | [CI][ROCm] Prefetch safetensors weights in AMD CI (#54898) | no |  |
| 254 | OK | 87deddc7a | [CI][Spec Decode] Add MTP placeholder-token regression coverage (#54893) | no |  |
| 255 | OK | 584e8f0dd | [Model] Fix GLM-OCR MTP weight loading (#49869) | no |  |
| 256 | OK | 1c26e57d3 | [Bugfix] Raise for unavailable piecewise CUDA graphs (#54782) | no |  |
| 257 | OK | b205750fe | [Bugfix][ROCm][Build] fix profiler hang due to queue interposition bug (#54171) | no |  |
| 258 | OK | 76ba32160 | [CI] Shard CPU jobs above the 24h P90 threshold (#54751) | no |  |
| 259 | OK | 314053177 | Include chat template fallbacks in package_data (#53762) | yes |  |
| 260 | CONFLICT | f81eb4193 | [Bugfix] `adjust_dcp_kv_cache_interleave_size` for NixlConnector only (#54803) | no | tests/test_config.py, vllm/config/vllm.py, vllm/distributed/kv_transfer/kv_transfer_state.py |
| 261 | OK | 2a4e3cc3d | [Bugfix][KV Offload] Ensure tracker progress for oversized offers (#54759) | no |  |
| 262 | OK | 7894394b0 | [Online quantization] Add targeted online quantization configuration based on user patterns (#51285) | no |  |
| 263 | OK | ffe3bb3c7 | [Hardware][XPU] Register matmul and linear batch-invariant kernels for XPU (#49209) | no |  |
| 264 | OK | 35faf957d | [Bugfix][KV Offload] Ignore stale async lookup results (#54872) | no |  |
| 265 | OK | ba6c60e98 | [Bugfix][KV Offload] Scale UniformTypeKVCacheSpecs groups by DCP (#50883) | no |  |
| 266 | OK | 872084fb7 | [CI] Add Kimi-K3-pruned75-DSpark-TP4 gsm8k eval (#54817) | no |  |
| 267 | OK | c6bca6e58 | [Bugfix][Multimodal] Scope cache hash kwargs by modality (#54918) | no |  |
| 268 | CONFLICT | 41848caa6 | [NIXL] Use int32 array for indices to avoid intermediate conversion (#51952) | no | vllm/distributed/kv_transfer/kv_connector/v1/nixl/base_worker.py |
| 269 | OK | 3b45d053b | [Bugfix][Model] Fix CohereASR streaming audio-token estimate (unit + subsampling) (#53829) | no |  |
| 270 | OK | d539de1c5 | [Docs] Add missing return annotations flagged by griffe (#54980) | no |  |
| 271 | OK | 605c3ddcb | [BUILD] Bump cutlass to v4.7.1 (#54190) | no |  |
| 272 | OK | 488e6fd53 | [CI] Revert flaky `test_quark_int8_w8a8_moe` (#54991) | no |  |
| 273 | CONFLICT | 1356635d8 | [New model][Multimodal] Add DeepSeek-V4-Flash-Vision-Exp support (#54566) | no | tests/models/test_registry.py, tests/tokenizers_/test_deepseek_v4.py, vllm/models/deepseek_v4/attention.py, vllm/v1/attention/backends/mla/sparse_swa.py |
| 274 | OK | bf7a14d30 | [CI][ROCm] Add DSpark evals (#54852) | no |  |
| 275 | OK | 2691c6cc5 | [Bugfix][CI] Set cudagraph_mode=FULL for the Ernie4.5-VL ViT cudagraph test (#54957) | no |  |
| 276 | CONFLICT | 3e9d364ff | [CI/Build][ROCm] Guard the two CUDA-only tests in test_bf16_skinny_gemm (#54984) | no | tests/kernels/test_bf16_skinny_gemm.py |
| 277 | OK | 9b38e3ad5 | [CI][MoE] Moe kernels test cleanup (#54954) | no |  |
| 278 | OK | 1945a9457 | [Bugfix][Tests] Stabilize B12X linear kernel checks (#54996) | no |  |
| 279 | OK | 0e3ac4907 | [ROCm][CI] Fix false multi-node detection on native CI (#54989) | no |  |
| 280 | OK | a56654d6d | [K3 Perf] Enable DSV3 GEMM for inner-contiguous and row-strided tensors, 12%~81% kernel performance improvement (#54565) | no |  |
| 281 | OK | 60857baa5 | [Bugfix][Rust Frontend][Renderer] Align DeepSeek V4 historical developer message handling (#54854) | no |  |
| 282 | OK | e3e124100 | [ROCm][CI] Extend Multimodal Processor Shard timeout on AMD CI (#55011) | no |  |
| 283 | OK | 963054ed5 | [CI] Exclude nightly-dev tags from nightly DockerHub cleanup (#55023) | no |  |
| 284 | OK | a0d3e5c16 | [XPU] Add fused GemmaRMSNorm path for eager execution (#53678) | no |  |
| 285 | OK | 6c6376a09 | [CI] Remove deleted nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16 and its arch aliases (#55026) | no |  |
| 286 | OK | cf3263d57 | [Agents] Add Triton kernel-writing skill (#55019) | no |  |
| 287 | OK | 443febe72 | [Agents] Expose Triton kernel-writing skill to Claude (#55028) | no |  |
| 288 | OK | ad127d9a0 | [Perf][Rust Frontend] Coalesce decoded chunks per engine update (#55012) | no |  |
| 289 | OK | 0e14198a6 | [Skills] Add kernel benchmark sanity references (#54995) | no |  |
| 290 | OK | 5e4e927b5 | [CI] Force HTTP/1.1 for runtime Git installs (#55044) | no |  |
| 291 | OK | e47356c63 | [ROCm][Installation] Add mooncake package to image using public wheels (#55002) | yes |  |
| 292 | OK | 5d09eb2cf | [Bugfix][MoE] Preserve unquantized weight storage on ROCm (#46009) | no |  |
| 293 | CONFLICT | 27a94d1ce | [CI] Fix DeepSeek-V4 registry platform guard (#55042) | no | tests/models/test_registry.py |
| 294 | OK | 3f1af35e0 | [Bugfix][Multimodal] Handle prefix-covered items in SHM worker cache (#54994) | no |  |
| 295 | OK | ee17d0d86 | Use server-generated keys for late-interaction query caches (#51445) | no |  |
| 296 | CONFLICT | 859dd3951 | [Bugfix][Core] Wait for the previous PP tensor sends before the next forward pass (#54962) | no | vllm/v1/worker/gpu_worker.py |
| 297 | OK | 092334c82 | [Bugfix] Wait for offload keys before storing chunks (#52923) | no |  |
| 298 | OK | 1f76efaa2 | [Model] Add K2-Horizon model support (#55063) | no |  |
| 299 | OK | 096d8e8ce | [ROCm][CI] Add MiniMax reduce RMS kernel coverage (#55057) | no |  |
| 300 | OK | e6eb9074e | [CI] Bump Transformers version to 5.16.1 (#53905) | yes |  |
| 301 | OK | 4cc0cb6f7 | [CI][AMD] Avoid expandable segments in LoRA TP tests (#55094) | no |  |
| 302 | OK | c21751c90 | [Kernel] Warm up Qwen GDN gated RMSNorm (#54251) | no |  |
| 303 | OK | 0d3ede3e3 | [Bugfix][Model] Enable torch.compile for StableLM (#54969) | no |  |
| 304 | OK | facd9a74a | [Model Runner V2][Spec Decode] Skip DP sync for all speculator uniform decodes (#54856) | no |  |
| 305 | OK | ee0a4c46a | [Bugfix] Account for PCP in multi-node world size validation (#55111) | no |  |
| 306 | OK | 758c79e1c | [Bugfix] Retain vocab embeddings during replacement (#55083) | no |  |
| 307 | OK | 848ab131b | [Perf] Accumulate Conformer attention scores with baddbmm (#55062) | no |  |
| 308 | OK | bb363db9a | feat: Add support for reasoning_token_count to reasoning parser (#54982) | no |  |
| 309 | OK | bf95f58d1 | [Core] Triton kernel for small-batch top-p only masking (#54651) | no |  |
| 310 | OK | edc0fb7e0 | Optimize PLE MTP metadata transfers (#55054) | no |  |
| 311 | OK | 31e9c1368 | [Bugfix][KV Connector] Safely fill circular buffers in DecodeBench (#54879) | no |  |
| 312 | OK | e55b93f29 | [Core] Deprecate "all" mamba cache mode (#55041) | no |  |
| 313 | OK | 4ae622828 | [Bugfix][KV Connector] Populate SimpleCPUOffload BlockStored metadata (#54325) | no |  |
| 314 | OK | da8ec2826 | [Bugfix][KV Offload] Do not let a recurrent group's unhashed block truncate the load boundary (#52807) | no |  |
| 315 | CONFLICT | 98ed0856f | [Model] add GLM-5.3-Flash support (#53906) | no | tests/kernels/attention/test_flashinfer_mla_decode.py, tests/kernels/mamba/test_gdn_prefill_flashinfer.py, tests/kernels/test_mhc_kernels.py, tests/multimodal/test_video.py, tests/transformers_utils/processors/test_glm5next.py, tests/v1/attention/test_kpool_tail_slot_mapping.py, tests/v1/attention/test_sparse_mla_backends.py, tests/v1/core/test_kv_cache_utils.py, vllm/config/vllm.py, vllm/distributed/kv_transfer/kv_connector/v1/mooncake/mooncake_connector.py, vllm/distributed/kv_transfer/kv_connector/v1/mooncake/store/coordinator.py, vllm/distributed/kv_transfer/kv_connector/v1/mooncake/store/worker.py, vllm/distributed/kv_transfer/kv_connector/v1/nixl/base_worker.py, vllm/model_executor/layers/sparse_attn_indexer_kpool.py, vllm/model_executor/warmup/kernel_warmup.py, vllm/models/glm5next/nvidia/kda.py, vllm/models/glm5next/nvidia/model.py, vllm/models/glm5next/nvidia/ops/kpool_compress.py, vllm/platforms/cuda.py, vllm/transformers_utils/processors/glm5next.py, vllm/v1/attention/backends/mla/indexer.py, vllm/v1/attention/backends/mla/rocm_aiter_mla_sparse.py, vllm/v1/attention/backends/mla/sparse_utils.py, vllm/v1/attention/ops/rocm_aiter_mla_sparse.py, vllm/v1/core/kv_cache_coordinator.py, vllm/v1/core/kv_cache_utils.py, vllm/v1/core/single_type_kv_cache_manager.py, vllm/v1/engine/core.py, vllm/v1/kv_cache_interface.py, vllm/v1/worker/gpu/model_states/mamba_hybrid.py, vllm/v1/worker/utils.py |
| 316 | OK | d410fc12f | [Kernel] Enable Kimi-K3 SiTU on the CuteDSL MoE backend and the SM107 low-latency GEMM plan (#54606) | no |  |
| 317 | CONFLICT | d4d703caf | [Bugfix][Model] Fix FP8 PLE loading in mixed ModelOpt checkpoints (#54882) | no | tests/models/qwen4_exp/test_ple.py |

## Worst offenders (wtdcode conflict magnets, top 15)

| file | distinct conflicting PRs | PR shas |
|------|--------------------------|---------|
| vllm/model_executor/warmup/kernel_warmup.py | 6 | 003e34341, 396c5a563, 3ba9907a1, 98ed0856f, adebc41b7, e16b5e518 |
| tests/models/qwen4_exp/test_ple.py | 4 | 1e300895a, d4d703caf, e126687a9, f870b9297 |
| vllm/config/vllm.py | 3 | 98ed0856f, da0b2d8b1, f81eb4193 |
| vllm/distributed/kv_transfer/kv_connector/v1/nixl/base_worker.py | 3 | 41848caa6, 98ed0856f, e126687a9 |
| vllm/model_executor/layers/sparse_attn_indexer.py | 3 | 7f4793eaa, 8c51b9265, f5c3cc240 |
| vllm/v1/kv_cache_interface.py | 3 | 6d4562c59, 98ed0856f, e126687a9 |
| vllm/v1/worker/gpu_worker.py | 3 | 4ac452ad9, 859dd3951, c92b29a1d |
| tests/distributed/test_custom_all_reduce.py | 2 | 99013d77d, e126687a9 |
| tests/models/qwen4_exp/test_qsa_reference.py | 2 | 003e34341, e126687a9 |
| tests/v1/attention/test_sparse_mla_backends.py | 2 | 7c5dc571c, 98ed0856f |
| tests/v1/core/test_kv_cache_utils.py | 2 | 98ed0856f, e126687a9 |
| vllm/distributed/kv_transfer/kv_connector/v1/mooncake/mooncake_connector.py | 2 | 5cc32fbdf, 98ed0856f |
| vllm/model_executor/models/interfaces.py | 2 | 21fa2c5a2, e126687a9 |
| vllm/models/deepseek_v4/attention.py | 2 | 1356635d8, e16b5e518 |
| vllm/models/qwen4_exp/nvidia/ple_layer.py | 2 | e126687a9, f870b9297 |

## Conflict-heaviest PRs (top 10 by conflicted-file count)

| sha | subject | conflicted files |
|-----|---------|------------------|
| e126687a9 | [Model] Support Qwen3.8-Flash-Next (#53896) | 31: tests/distributed/test_custom_all_reduce.py, tests/models/qwen4_exp/test_config.py, tests/models/qwen4_exp/test_ple.py, tests/models/qwen4_exp/test_qsa_amd.py, tests/models/qwen4_exp/test_qsa_reference.py, tests/v1/core/test_contiguous_kv_packing.py, tests/v1/core/test_kv_cache_utils.py, tests/v1/kv_connector/unit/test_nixl_desc_geometry.py, tests/v1/kv_connector/unit/test_tp_mapping.py, tests/v1/worker/test_gpu_autoregressive_speculator.py, tests/v1/worker/test_gpu_model_runner_v2.py, vllm/config/compilation.py, vllm/distributed/kv_transfer/kv_connector/v1/nixl/base_worker.py, vllm/model_executor/models/config.py, vllm/model_executor/models/interfaces.py, vllm/models/qwen4_exp/amd/model.py, vllm/models/qwen4_exp/amd/mtp.py, vllm/models/qwen4_exp/amd/ple_layer.py, vllm/models/qwen4_exp/common/ple.py, vllm/models/qwen4_exp/config.py, vllm/models/qwen4_exp/nvidia/model.py, vllm/models/qwen4_exp/nvidia/model_state.py, vllm/models/qwen4_exp/nvidia/mtp.py, vllm/models/qwen4_exp/nvidia/ple_layer.py, vllm/platforms/interface.py, vllm/v1/core/kv_cache_coordinator.py, vllm/v1/core/kv_cache_utils.py, vllm/v1/core/single_type_kv_cache_manager.py, vllm/v1/kv_cache_interface.py, vllm/v1/worker/gpu/model_runner.py, vllm/v1/worker/mamba_utils.py |
| 98ed0856f | [Model] add GLM-5.3-Flash support (#53906) | 31: tests/kernels/attention/test_flashinfer_mla_decode.py, tests/kernels/mamba/test_gdn_prefill_flashinfer.py, tests/kernels/test_mhc_kernels.py, tests/multimodal/test_video.py, tests/transformers_utils/processors/test_glm5next.py, tests/v1/attention/test_kpool_tail_slot_mapping.py, tests/v1/attention/test_sparse_mla_backends.py, tests/v1/core/test_kv_cache_utils.py, vllm/config/vllm.py, vllm/distributed/kv_transfer/kv_connector/v1/mooncake/mooncake_connector.py, vllm/distributed/kv_transfer/kv_connector/v1/mooncake/store/coordinator.py, vllm/distributed/kv_transfer/kv_connector/v1/mooncake/store/worker.py, vllm/distributed/kv_transfer/kv_connector/v1/nixl/base_worker.py, vllm/model_executor/layers/sparse_attn_indexer_kpool.py, vllm/model_executor/warmup/kernel_warmup.py, vllm/models/glm5next/nvidia/kda.py, vllm/models/glm5next/nvidia/model.py, vllm/models/glm5next/nvidia/ops/kpool_compress.py, vllm/platforms/cuda.py, vllm/transformers_utils/processors/glm5next.py, vllm/v1/attention/backends/mla/indexer.py, vllm/v1/attention/backends/mla/rocm_aiter_mla_sparse.py, vllm/v1/attention/backends/mla/sparse_utils.py, vllm/v1/attention/ops/rocm_aiter_mla_sparse.py, vllm/v1/core/kv_cache_coordinator.py, vllm/v1/core/kv_cache_utils.py, vllm/v1/core/single_type_kv_cache_manager.py, vllm/v1/engine/core.py, vllm/v1/kv_cache_interface.py, vllm/v1/worker/gpu/model_states/mamba_hybrid.py, vllm/v1/worker/utils.py |
| e16b5e518 | [1/N][warmup][DSv4] Migrate generic MLA metadata and indexing kernels (#50175) | 5: vllm/model_executor/warmup/kernel_warmup.py, vllm/model_executor/warmup/sparse_mla_triton_warmup.py, vllm/models/deepseek_v4/attention.py, vllm/v1/attention/backends/mla/indexer.py, vllm/v1/attention/backends/mla/sparse_utils.py |
| 1356635d8 | [New model][Multimodal] Add DeepSeek-V4-Flash-Vision-Exp support (#54566) | 4: tests/models/test_registry.py, tests/tokenizers_/test_deepseek_v4.py, vllm/models/deepseek_v4/attention.py, vllm/v1/attention/backends/mla/sparse_swa.py |
| f81eb4193 | [Bugfix] `adjust_dcp_kv_cache_interleave_size` for NixlConnector only (#54803) | 3: tests/test_config.py, vllm/config/vllm.py, vllm/distributed/kv_transfer/kv_transfer_state.py |
| 6d4562c59 | [Attention][DCP] Enable FlashInfer MLA for DSpark drafting (#54277) | 2: tests/v1/spec_decode/test_eagle_draft_attn_metadata.py, vllm/v1/kv_cache_interface.py |
| 7f4793eaa | [Nixl][PD] DCP support for MLA models   (#50611) | 2: tests/v1/worker/test_gpu_model_runner.py, vllm/model_executor/layers/sparse_attn_indexer.py |
| 7ab292348 | [Flashinfer] Upgrade Flashinfer version to 0.6.18 (#54313) | 2: docker/Dockerfile, docker/versions.json |
| eeb549a74 | [Frontend] Move engine/protocol.py out openai folder (#54492) | 2: vllm/reasoning/hy_v4_reasoning_parser.py, vllm/tool_parsers/hy_v4_tool_parser.py |
| dafbef15a | [Core] Add `max_num_queued_reqs` and `max_num_queued_tokens` for queue size management (#49445) | 2: tests/entrypoints/openai/chat_completion/test_serving_chat.py, vllm/exceptions.py |

## Env-impact PRs

- `3bb19cd8a` [Bugfix][CI/Build] Fail closed when selected precompiled CUDA variant is unavailable (#52545)
- `94a54f581` [XPU]bump up vllm_xpu_kernels to 0.1.14.1 (#54203)
- `7ab292348` [Flashinfer] Upgrade Flashinfer version to 0.6.18 (#54313)
- `3593c964d` [ROCm] Add TheRock preview docker updates, Keep Python 3.12 and Ubuntu 22.04 (#49925)
- `e29af0a2a` [XPU] bump up auto-round-lib to 0.15.0 (#54515)
- `7c5dc571c` [Attention][DSA] Enable W4A16 DSA (#51724)
- `0d4ad4798` [Kernel] Add B12X causal paged attention backend (#52017)
- `339e16cbb` [Bugfix] Support MCP SDK 2.x tool input schemas (#53870)
- `f4e613614` [Kimi-K3] Bump FlashKDA to fix unstable inverse (#54859)
- `314053177` Include chat template fallbacks in package_data (#53762)
- `e47356c63` [ROCm][Installation] Add mooncake package to image using public wheels (#55002)
- `e6eb9074e` [CI] Bump Transformers version to 5.16.1 (#53905)

