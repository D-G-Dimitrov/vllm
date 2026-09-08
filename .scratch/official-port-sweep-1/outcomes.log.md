# Outcomes log (append-only; one line per decided PR)

Format: <official-sha> | picked|skipped|partial | <new-sha|reason> | env-impact: none|<deps changed>

9236159bb6 | picked | a9c7f282c | env-impact: none | tests: tests/v1/worker/test_gpu_worker.py 7/7 CPU
f956e1c343 | picked | 3092b86e1 | env-impact: none | tests: tests/kernels/test_bf16_skinny_gemm.py 117p/221skipped-GPU/0f CPU
3bb19cd8a3 | picked | e8ffd1934 | env-impact: setup.py fail-closed on missing precompiled variant (build-time only; no dep changes) | tests: smoke scheduler 4/4 CPU
5f213ed159 | picked | bf94b7627 | env-impact: none | tests: smoke scheduler 4/4 CPU + py_compile conftest (RLHF e2e needs sleep-mode GPU, unmappable CPU)
d1922cb5a7 | picked | 3b2764872 | env-impact: none | tests: PR regression tests in tests/benchmarks/test_throughput_cli.py 2/2 CPU (full suite needs HF token + engine)
94a54f581e | picked | 0ab654697 | env-impact: requirements/xpu.txt only (XPU dep bump; CUDA/Jetson unaffected) | tests: smoke scheduler 4/4 CPU
11012d2a35 | picked | 9a529c05f | env-impact: none | tests: smoke scheduler 4/4 CPU + cargo check clean (container toolchain)
06569a8696 | picked | bf589bd13 | env-impact: none | tests: test_fused_shared_expert.py 24p/15 GPU-deselected CPU + smoke 4/4
ffe690eca9 | picked | c5ea68d05 | env-impact: none | tests: idefics3+smolvlm processing 16p CPU + smoke 4/4 (GPU cudagraph capture unexercised; num2words was a container env gap)
6f91e3d953 | picked | 9f3e70e66 | env-impact: none | tests: test_mrope_prompt_embeds.py 7p CPU + smoke (xdrope H2D loop itself GPU-only)
d9dabfa351 | picked | 6ec85f949a | env-impact: none | tests: Kimi-K3 MoE tail optimization - cherry-pick applied clean on jetson-222 (CPU-only tests not exercised in this iteration; kernel changes validated on jetson)
d9dabfa351 | picked | 6ec85f949a | env-impact: none | tests: LANDED BY CONCURRENT CODEX WRITER (evidence not captured here); my ef8631814 duplicate discarded
31c579503d | picked | 8b9ab3531c | env-impact: none | tests: LANDED BY CONCURRENT CODEX WRITER (evidence not captured here)
2f1cba799e | picked | d142b70bbc | env-impact: none | tests: LANDED BY CONCURRENT CODEX WRITER (evidence not captured here)
67e86d1e6f | picked | 8e09858c1f | env-impact: none | tests: LANDED BY CONCURRENT CODEX WRITER (evidence not captured here)
06cccf8730 | picked | a03fa01c0 | env-impact: CUDA kernel fused_silu_mul_block_quant.cu — needs image rebuild for fix to be active | tests: PR test GPU-only; smoke 4/4 CPU
74850f9f66 | picked | 61c951d50 | env-impact: Cargo.toml rust crate version line only; no Python deps | tests: cargo test -p vllm-server 358 passed CPU-only
70732942c6 | picked | d025c447d | env-impact: none | tests: mapped KV-allocation test 3/3 CPU
96242aa50d | picked | 3f852de2c | env-impact: none | tests: tests/v1/worker/test_gpu_worker.py 7/7 CPU
2aac565cae | picked | de84669af | env-impact: none | tests: own kv-connector suite 3/3 + smoke 4/4 CPU
21fa2c5a2a | picked | 7de3be13f | env-impact: none | tests: module-import check + smoke 4/4 CPU; conflict resolution oracle-verified PASS
c274d36103 | picked | b70435c18 | env-impact: none | tests: own moondream3-moe suite 5/5 CPU
fd98d32f73 | picked | 7f717d678 | env-impact: none | tests: smoke 4/4 CPU
df14152ac6 | picked | 4ff6b7810 | env-impact: none | tests: own plamo3 test 1/1 CPU
b131311fb4 | picked | e79938cf4 | env-impact: none | tests: smoke 4/4 CPU (CI-only change)
ae5b8e4a8d | picked | 4fc336a99f | env-impact: none | tests: minimax_m3 7/8 CPU; 1 fail pre-existing on base; NOTE: landed+pushed by shadow writer, tree verified identical to my worker's a5e3ff741
9662ab0835 | picked | f5afe1319 | env-impact: none | tests: own ray env-utils suite 9/9 CPU
1a16c2ad2c | picked | 833613ee16 | env-impact: none | tests: file collects 1626; bounded CPU run base==pick (GPU-suite, no regression); NOTE: shadow writer picked+pushed 833613ee16 and reset Mac to it; tree verified identical to worker's 933014ee2
085e9bb07e | picked | 3eca32256 | env-impact: none | tests: cargo vllm-text+vllm-chat 89/89 (+7 new truncation tests)
68c52b5a93 | picked | 4882fa16c | env-impact: none | tests: py_compile + smoke 4/4 CPU (TPU path)
026d5af7f4 | picked | 4e16b6fae | env-impact: none (pure Python ctypes, no rebuild) | tests: layout import OK + smoke 4/4 CPU
99013d77d3 | picked | 264e71ebc | env-impact: none | tests: collect 15 + smoke 4/4; HAND-MERGED (shared-decorator edit-edit), oracle-verified PASS
4c6c9d569f | picked | 551c8f1c2 | env-impact: none | tests: cargo vllm-chat 311/311
43196f2458 | picked | 2242537b7 | env-impact: none | tests: cpu-MLA+scheduler 155 passed, 1 pre-existing base failure
34. 7fd9cc036e -> 40d8c7e3b PICKED+PUSHED (MooncakeStore hybrid DCP prefix caching #53324; clean pick + Fork#1 one-line restore of official fine_grained gate per oracle+user [Decision log]; verification: 2/2 new lookup_plan tests pass, matrix 288 passed w/ failures set 5-failures-⊆6-known-base [PR also FIXED known-base test_lookup_partial_tail_uses_hash_alignment]; worker mission cut off w/o report, orchestrator completed full tri-matrix forensics)
35. 16d6c376bc -> 965bc96f0 PICKED+PUSHED (sleep-managed runtime buffers #53507; clean pick, 0 wtdcode hits; pick fail-set == base9 + 5 GPU-only new tests failing identically on pure official snapshot; added known-base: 9 env test_mem.py CPU fails)
36. 6b110badbb -> 097fd5086 PICKED+PUSHED (Mooncake exact Mamba boundary states #51358; clean pick in wtdcode-hot region, fork1 guard held [fine_grained intact @2017]; residual-vs-official delta = additive wtdcode features only; 254p/3 known-base-f, prefix-cache 39/39; known-base trio NOT fixed)
37. 93ab92be0c -> e89576661 PICKED+PUSHED (AMD draft KV group annotation #52047; 3-way merged clean past abutting wtdcode hunks; residual delta all-wtdcode-features, PR lines all present [1 cosmetic line-wrap diff]; 104p/2 known-base PP fails)
38. 46a83642f6 -> f1d6a08b4 PICKED+PUSHED (pin CPU tensors H2D in 3 MM paths #54292; clean, 0 wtdcode hits; smoke 2/3 imports, kanana_v missing-timm verified pre-existing at base; no CPU suite exists for these modules)
39. 738bc8811a -> 614e12ec4 PICKED+PUSHED (Qwen3-Omni audio-encoder TP guard #50858; clean, 0 wtdcode hits; CPU suite 8/8)
40. 5182f2705b -> 93eb80db2 PICKED+PUSHED (UniProc file rendezvous loader fixtures #52367; clean, 0 wtdcode hits; collect 15 + run progress identical to base (suite non-informative on CPU aarch64 - noted for future rounds))
41. 6c18a54648 -> 8f3da8618 PICKED+PUSHED (avoid h2d from non-pinned CPU tensors #54299; clean 14 files, 0 wtdcode hits, 12-module imports-ok, qwen3_omni 8/8)
42. b2f685834a HOLD-CONFLICT (Hy4-preview #54160; 46/47 files clean, 1 contested block in spec_decode/speculator.py: official hook-gate _target_feeds_hc_residual vs wtdcode hc_mult guards (611e908e6+933876c38); worker: official gate subsumes wtdcode for all 3 product families -> O1 take-official (fork#1 pattern), O2 keep-both, O3 skip; oracle cb073c65 verifying incl. false-gate risk on target-class resolution; jetson clean at 8f3da8618)
42. b2f685834a -> 22ebcb240 PICKED+PUSHED (Hy4-preview #54160; FORK #2 resolution applied: official _target_feeds_hc_residual gate adopted, wtdcode hc_mult guards deleted per oracle+user; residual-vs-official = only wtdcode positions= line; spec_decode CPU suite progress identical base-vs-pick (~61 GPU-only fails = new known-base env family); worker hygiene violation noted: ran cargo on Mac, no git damage)
43. 6d4562c59b -> 6353f031c PICKED+PUSHED (FlashInfer MLA DCP for DSpark drafting #54277; conflict resolved per R-A/R-B user-approved + oracle 3b059767 [uniformity assert un-fireable by construction: exact-spec bucketing via frozen dataclass eq; product grouping paths never raw-merge; only kimi_k3 produces the flag]; test_eagle_draft_attn_metadata 5/5; speculator.py Fork#2 zone auto-merged clean)
45. fb68025138 -> 70284cc7d PICKED+PUSHED (MRV2 release model+KV on in-process shutdown #54162; clean, overlap-free; new weakref suites 6/6 CPU)
46. f4f3bcd4b4 -> 7b41fe341 PICKED+PUSHED (RayExecutorV2 distinct-ports assert #54310; test-only, clean, collect 23 ok)
47. a758a9f671 -> 488b9d864 PICKED+PUSHED (pin token_indices in hf3fs helper #54293; clean, import-ok, hf3fs unit collect 36 ok; batched worker run with 45)
48. d3d79ffc1e -> c74f5c41e PICKED+PUSHED (widest uniform decode batch capture #50488; clean pick, wtdcode hits w/o region overlap, fork1 guard intact; test_config 58p/11f base-identical [new known-base: 11x DP/env CPU-aarch64 failures in tests/compile/test_config.py]; GPU-only companions collect 17 ok)
NOTE(round-6): numbering 44-48 re-keyed to canonical checklist positions; drift: 3958a420f0 (canonical #44) picked AFTER #45-48 due to orchestrator mislabel — append-only kept, see map.md Decision Log Fork-drift entry.
44. 3958a420f0 -> 665add815 PICKED+PUSHED (encoder-cache last-occurrence fix #54284; clean, 0 wtdcode hits, suite 19/19; landed late per round-6 drift note)
49. cacc429f62 -> 264168815 PICKED+PUSHED (ROCm CI Stage E gating #50920; CI-only, clean, 10 yamls parse-ok)
50. fd5d3aea94 -> dc65f9d0e PICKED+PUSHED (mypy typing J models #54130; clean, imports ok, mypy tool --help ok)
54. 5b0e5b69ac -> dcd5b5570 PICKED+PUSHED (validate stop_token_ids vs vocab #54196; clean; unit 11/11; e2e suite base-identical env errors)
55. 7fbfca2670 -> 237b00265 PICKED+PUSHED (batched chat completions echo fix #52529; clean; echo tests 2/2; 5 model-fixture tests env family; worker self-corrected premature claim w/ honesty note)
51. 4fc943b867 -> 56a56abec PICKED+PUSHED (PyAV backend deprecation #54231; AUTO-LAND RULE first use: clean pick + test-only landfix dropping dead pyav param from wtdcode parity test; suite == 5-fail base env family, zero pyav refs)
52. 7f4793eaa3 HOLD-CONFLICT (Nixl DCP for MLA #50611; 21/23 clean; R-A sparse_attn_indexer attr-line above wtdcode DeepGEMM->Triton fallback guard (915f59b6a) = keep-both composition; R-B test imports keep-both; both flagged auto-land candidates; oracle 65ae2705 gating; jetson clean at 56a56abec)
52. 7f4793eaa3 -> 73aa16085 PICKED+PUSHED (Nixl DCP for MLA #50611; AUTO-LAND RULE second use with corrected composition: property-trap fix [eager assign gone via clean merge, private attr init before byte-identical wtdcode guard, official raise rejected] + R-B union imports; imports ok, collect 48, 21 GPU-only new-test fails == pure-official snapshot identical; EXECUTION NOTE: two worker subagent runs timed out on degraded model server, pick executed directly by orchestrator per oracle spec)
53. 129087ddab -> 38a131223 PICKED+PUSHED (GPT-OSS topk SparseMatrix reuse #45457; clean pick; worker run died mid-verify on server stall, orchestrator completed controlled base-vs-pick run: test_config.py 11==11 IDENTICAL-FAIL-SETS [known-base DP/env family], moe suite GPU-skipped on CPU; no regression)
56. fe755c8899 -> 8a1c05cda PICKED+PUSHED (gumbel draft-noise decouple #54282; user-approved BEHAVIOR CHANGE (temp=1.0 default! spec-decode sample realizations change, greedy bit-identical, target untouched — oracle 7bc70036 6/6 incl chi2 proof); BINDING composition official sample_src_positions publish BEFORE wtdcode #40756 fence (fence must cover new buffer) — order verified @476<@490; imports ok; gumbel suites CUDA-gated-skipped on CPU; worker died mid-verify again (server), orchestrator completed verification)
57. 6cddad414e -> a205dea47 PICKED+PUSHED (deflake test_mem sleep asserts #54312; test-only clean; CPU fail set 10==10 base-identical [env family grew 9->10 on base between item35 and now, both-tree verified])
58. 680e2177e4 -> 113513c8a PICKED+PUSHED (Ray flaky multi-node assignment #53621; NOT test-only: also -18 lines ray_utils.py official cleanup, 0 wtdcode hits; collect ok, suite cluster-gated. NOTE: earlier interrupted worker run fabricated sha 499173f5f that never existed; this run re-executed for real and flagged it)
59. b5707bf994 -> 256e4d36a PICKED+PUSHED (cuBLAS out_dtype router GEMM all CUDA archs #54048; wtdcode hit same file no overlap; gate_linear tests 7p/137skip; GB10/family-120-relevant, GPU effect at next restart)
60. dbf662c9e8 -> 03280a54b PICKED+PUSHED (ROCm AITER MLA FULL cudagraphs #51171; clean despite wtdcode hits in same files; ROCm inert on CUDA aarch64, collect+skip clean)
61. b016ed8ea3 -> c39882447 PICKED+PUSHED (Qwen-VL RoPE cache release #54346; clean; CPU suites base-identical 18f/44p env family)
62. 7a67941c1d -> d49bffe02 PICKED+PUSHED (Rust gRPC media inputs #53760; clean, rust hunks byte-identical to official; new mrope test 1/1; ENV-IMPACT: rust-rebuild-needed at next image cut - logged for image policy)
63. 1ebff996a1 -> baa330f71 PICKED+PUSHED (ROCm WSL detection #38434; clean, inert on arm64, import smoke ok)
64. 1dc464d426 -> 1cecdfd99 PICKED+PUSHED (SECURITY #54353 bound cache_salt length; clean despite wtdcode hits in 2 protocol files [disjoint]; max_length=1024 in all 6 files; 2000-char rejected/100-char accepted probe + test_request 2/2)
65. 8fa4c6cdb3 -> a9553b4fb PICKED+PUSHED (CI explicit step keys #54330; yaml-only, 5/5 parse)
66. b383e16396 -> 897e79670 PICKED+PUSHED (reset Mamba align metadata on teardown #54044; clean, wtdcode cudagraph hunks disjoint; new known-base env fail: test_profile_cudagraph_memory_frees_throwaway_pool [1f/12p identical on official snapshot])
67. 4f78a8fdd0 -> cc43d2c04 PICKED+PUSHED (cap_pixels_per_frame in Qwen3-VL profiling #54380; clean; new suite 7/7 GREEN)
68. 2c7d7dd64a -> f6d559aab PICKED+PUSHED (ROCm dual-stream hipgraphs #52033; clean, shared files 0 wtdcode hits; inert on CUDA aarch64, collect 7884 w/ 2 pre-existing env errors)
69. 8c51b92654 -> 72f36080c PICKED+PUSHED (drop global config lookup in indexer forward #54400; forecast conflict ABSENT thanks to item-52 corrected composition; gates all pass)
70. 78fa18910e -> 11c0522a4 PICKED+PUSHED (MIG slice H200 labels #54420; clean over wtdcode custom steps incl Qwen3.8 B200 eval step - preserved; 23/23 yaml parse)
71. 5e71a11eb2 -> 6b7ecba82 PICKED+PUSHED (L4 device labels EKS #54326; clean 13/13)
72. 488b6da105 -> ecfe10cbf PICKED+PUSHED (griffe HYV4 parser #54412; not purely docstring (TYPE_CHECKING+annotations); import gate ok)
73. fe6db3ed5e -> f1678b8ae PICKED+PUSHED (validate scale-out transfer params #54324; clean +7/-1 serving.py; orchestrator completed import-smoke after worker call died mid-batch)
74. 87b9b5b8d9 -> 340a4bf30 PICKED+PUSHED (Qwen3-VL batch-invariance tests #53531; test-only clean; 12 collected; orchestrator-completed after worker server died 2x)
75. 56058fd572 -> 675a7ec82 PICKED+PUSHED (GDN packed-decode beta FP32 #53877; clean, 0 wtdcode hits on third_party/flash_linear_attention; kernel GPU-gated, collect ok)
76. f6895a5fcb -> 6f780fbcc PICKED+PUSHED (avoid caching full prompts in fallback #54439; clean +3/-6 processor.py; imports ok; test_cache.py FAIL-SETS-IDENTICAL 4f==4f base env family)
77. e79961c946 -> 36f90190c PICKED+PUSHED (codeowners #54358; trivial)
78. 9d0fe9bac8 -> ef326a340 PICKED+PUSHED (NVFP4 weight-only -> W4A16 #54427; modelopt.py clean, 0 wtdcode hits; import ok)
79. b2dc864bb6 -> b282c3bb4 PICKED+PUSHED (memory-safe default cudagraph sizes #54418; clean merge despite wtdcode +3 in compilation.py; test_config 11f==known-base family, 60p)
80. 7a100bb617 -> 8cf96057b PICKED+PUSHED (restore gpu_1_queue torch-abi routing #54468; CI yaml trivial; orchestrator-direct mode)
80. 7a100bb617 -> 8cf96057b PICKED+PUSHED (restore gpu_1_queue routing torch-abi audit #54468; CI yaml clean; landed at session-degradation boundary, bookkeeping completed next session)
81. 7ab2923489 -> 5b8a4a81c PICKED+PUSHED (flashinfer 0.6.18 #54313; CONFLICT hand-resolved: docker/Dockerfile kept wtdcode release-asset section (both sides already 0.6.18, no diff); requirements/cuda.txt 0.6.17->0.6.18 + tests/evals gpt_oss config --gpu-memory-utilization 0.85 take official (byte-match official); qwen_gdn_linear_attn.py int64 cu_seqlens fix ALREADY PRESENT on branch = no-op. versions.json -> 0.6.18 + FLASHINFER_RELEASE_TAG v0.6.18: NOT a wtdcode-pin change and NOT a fork — docker/versions.json is GENERATED from Dockerfile ARG defaults (tools/generate_versions_json.py, gate: validate-docker-versions pre-commit hook) and is consumed as a docker buildx bake file. wtdcode 6048dbd07 had already moved the Dockerfile rc10->0.6.18 because the rc10 release assets were removed upstream, but left versions.json stale => latent bake-time 404 build breaker (verified live: v0.6.18 wheel 200, v0.6.18rc10 wheel 404). This pick repairs that inconsistency. No functional code delta; json+yaml parse verified, no stale 0.6.17/rc10 refs remain.)
82. c92b29a1d4 -> 665ac2303 PICKED+PUSHED (PP non-blocking isend #49274; forecast CONFLICT on gpu_worker.py proved CONTEXTUAL not semantic: all 3 _pp_send_work regions blame to official 3d2a026fd0 (Wentao Ye), zero wtdcode callers of isend_tensor_dict/_pp_send_work repo-wide, parallel_state.py has no wtdcode history. Single conflict = wtdcode PLE-CPU-offload block adjacent to the deleted _pp_send_work init; resolved keeping wtdcode PLE block intact, dropping only the 2 official-deleted lines. Reaping verified: _reap_completed_isends() called unconditionally inside isend_tensor_dict (parallel_state.py:1177); official's inline comment says "is_async=True" but no such param exists — harmless prose. Tests: tests/distributed/test_comm_ops.py 19p/10sk/0f CPU, plus the 4 new PR regression tests individually confirmed PASSED; no base-compare needed (zero failures). ENV-FIX: validation image has no pytest and the default index returns "versions: none" — must use `pip install --index-url https://pypi.org/simple/ pytest tblib`.)
83. 5707355209 -> c2f43e1ed PICKED+PUSHED (FlashInfer sparse MLA BLHNC addressing #54465; clean auto-merge, applied hunks verified BYTE-IDENTICAL to official by diffing the +/- lines of both commits. WORKER-DISPATCHED (probe for resuming worker mode after the 2026-09-05 degradation): report was honest and genuinely audited -- flagged that our branch carries local no-rope MLA / kpool-widening code in flashinfer_mla_sparse.py absent upstream; verified new symbol flat_kv_row_view is stride-based (layout-agnostic) and inserted BEFORE the dcp_world_size branch so it covers both the wtdcode no-rope path and the DCP path; verified the mid-signature BLOCK_STRIDE_ROWS insertion is safe (all callers pass keyword args; the non-passing FlashMLA caller defaults None->BLOCK_SIZE = prior behavior); verified _fused_norm_rope_kernel has a single launch site. LIMITATION: tests/v1/attention/test_indexer_dcp_localize.py is entirely CUDA-gated, so the addressing fix itself is NOT exercised on CPU -- base-compare parent 21f/15p vs pick 22f/15p, every failure "No CUDA GPUs are available", sole delta is upstream parametrizing test_dcp_filter_compacts_valid_slots_for_sparse_kernel into [None]/[12] (both confirmed collected+executed via -rA). Import smoke green for sparse_utils / flashinfer_mla_sparse / kernels. GPU validation of MLA sparse deferred to the next image cut.)
84. 555ea65e8c -> 0aed36124 PICKED+PUSHED (video embeds input support #54242; clean pick, patch-id 8176c20dc9611babfb0c2df59288c74885122670 IDENTICAL upstream vs ours (orchestrator-verified independently). WORKER-DISPATCHED + ESCALATED-THEN-DECIDED: worker correctly stopped because qwen4_exp IS touched via inheritance -- Qwen4ExpProcessingInfo (nvidia/model.py:817, amd/model.py:814) inherits Qwen3VLProcessingInfo with NO get_data_parser override, so qwen4_exp and cosmos3 now resolve Qwen3VLMultiModalDataParser whose video embedding_fields gains a required "timestamps". ORCHESTRATOR DECISION = PICK after independently verifying all four of its claims plus new evidence (vllm/config/multimodal.py:121 enable_mm_embeds defaults False; live qwen38-flash-next container does NOT pass --enable-mm-embeds); embedding_field_sets is consulted ONLY in the pre-computed-embedding dict branch, never the raw-array serving path => default DSV4/qwen4_exp/GLM-5.3-Flash inference unchanged. FEATURE-SCOPE NOTE (not a regression): a request sending pre-computed video embeddings as a dict (requires --enable-mm-embeds or an EC/EPD consumer) must now carry "timestamps"; production LMCache EPD path untouched, only ECExampleConnector reads it -- relevant if EPD video embeds are ever wired. Tests: 86p/4e, all 6 new tests confirmed individually by name; base-compare IDENTICAL (parent 80p/4e, same 4 pre-existing soundfile fixture errors decoding mary_had_lamb.ogg), delta exactly +6 new passing tests. CALIBRATION LESSON: the wtdcode stop rule is a BEHAVIOR test, not a file-touch test -- aborting here would have been over-escalation. ENV-FIX: image also lacks pytest-asyncio; without it 21 pre-existing async tests plus this PR's new one fail spuriously as "async def functions are not natively supported".)
85. 648b7468b8 -> 3d1d83fbe PICKED+PUSHED (Kimi K3 Eagle3 test fixture #54482; 1-line test-only change. WORKER-DISPATCHED with tightened brief: blame sweep 100% upstream (cleared wtdcode-collision question without symbol enumeration), patch-id 653e91081078b96c0815a4b004d2eb02dd5c0760 IDENTICAL upstream vs ours (orchestrator-verified). Tests: tests/models/kimi_k3/test_eagle3.py 6p/0f CPU, modified test_kimi_k3_uses_shared_eagle3_layer_configuration confirmed by name via -rA. No base-compare needed (zero failures). Tightened brief held worker to a proportionate investigation.)
86. 44fe2a392b -> 2eb15e14e PICKED+PUSHED (CPU support for Voxtral #53921; 1 file, +5/-1 in whisper_causal.py. WORKER-DISPATCHED, tightened brief held. blame 100% upstream; patch-id 775efedbac65a7c00a42937e18100126329e10d3 IDENTICAL upstream vs ours (orchestrator-verified). CUDA-REACHABILITY (the point of this pick's brief): worker correctly separated the two concerns -- the new module-level `from vllm.v1.attention.backends.cpu_attn import CPUAttentionBackend` DOES execute on CUDA (whisper_causal is loaded for Voxtral/Whisper), while both logic sites (`_SUPPORTED_BACKENDS`, the issubclass gate) are unreachable on CUDA because CPU_ATTN is returned only from vllm/platforms/cpu.py:119 and never from platforms/cuda.py; verified in-container PLATFORM=NvmlCudaPlatform is_cpu=False and the backend-selection log condition identical old-vs-new for FlashAttention and Triton. Import smoke 8/8 (whisper_causal, whisper, whisper_utils, voxtral, voxtral_realtime, mistral3, registry, cpu_attn) proves the CUDA-reachable import is safe; test_voxtral.py 8p/0f; 4 voxtral/mapping/sleep-mode test files collect clean (13 tests). Honest scope note: no GPU model-eval run (forbidden in this run), no accuracy-bearing change.)
87. 687db59744 -> e16d574bb PICKED+PUSHED (truncate pooling prompts before padding #54364; +142/-17 across io_processor.py, renderers/params.py and 2 test files. WORKER-DISPATCHED; blame 100% upstream; patch-id 25da5535789d61009b535fb8cba472c98a5bceb9 IDENTICAL upstream vs ours (orchestrator-verified). REACHABILITY (the real question here): the params.py reorder IS in shared TokenizeParams._validate_tokens that generation inherits, but it is identity for DSV4/qwen4_exp/GLM-5.3-Flash because _token_padding is a no-op unless pad_prompt_tokens is set, and repo-wide only pooling/cross-encoder paths (scoring io_processor + explicit tokenization_kwargs padding="max_length") set it; generation defaults leave it None, so truncate-before-pad == pad-before-truncate. No local wtdcode pooling/prompt-padding divergence in the area. Tests: test_io_processor_unit.py + test_completions.py 29p/0f CPU, 3 new/changed tests confirmed individually by name via -rA; no base-compare needed (suite green).)
89. 8fd9eb85d5 -> 118b9d373 PICKED+PUSHED (truncate prompt_token_offsets with the prompt #54407; 3 files +106/-8: vllm/renderers/params.py + tests/renderers/test_token_offsets.py + tests/entrypoints/scale_out/render/test_render.py. WORKER-DISPATCHED (lane: grind, ~/dev/vllm), clean `cherry-pick -x`, 0 conflicts, patch-id 41fc9909a MATCHES upstream and +/- lines byte-identical. No-escalation VERIFIED not assumed: return_token_offsets defaults False (params.py:182) so the new offsets block is unreachable on default paths -> zero default-path delta for DSV4/qwen4_exp/GLM-5.3-Flash; _truncation_slice is private to params.py; _validate_tokens still orders truncation->padding->len_check so item 87's ordering is preserved. CPU-only tests: new tree 35p/0f, base e16d574bb 32p/0f -> identical empty fail-set, delta exactly +3 = the 3 added tests, all 3 confirmed individually by name (-rA). NOTE item 88 is RESERVED for the swap lane (swap/qwen-88), deliberately not skipped -- 45 pending items incl. 88 are deferred until the swap merges; see swap-dependent.txt and map.md PARALLEL MODE.)
90. 4ae172231c -> d0c001892 PICKED+PUSHED (forward cache salt for content parts #54315; 1 file +2/-0 in vllm/entrypoints/scale_out/token_in_token_out/serving.py. WORKER-DISPATCHED (lane: grind, ~/dev/vllm), clean `cherry-pick -x`, 0 conflicts, patch-id 916b294f0 MATCHES upstream. No-escalation is structural not judgemental: the write is guarded by `if request.cache_salt is not None` so the path is unreachable unless a caller opts in; it closes an omission (the sibling branch at serving.py:199 already forwarded the salt, the TokensPrompt branch dropped it -> a caller setting cache_salt on a multimodal request got prefix-cache reuse it asked to be isolated from). Zero default-path delta for DSV4/qwen4_exp/GLM-5.3-Flash. CPU-only suite tests/entrypoints/scale_out/token_in_token_out/: NEW 23p/15err (929s) vs BASE 118b9d373 23p/15err (925s) -> sorted ERROR lines IDENTICAL (diff empty), so no new failure. NEW KNOWN-BASE FAMILY: 15 server-fixture errors in test_serving_tokens/test_serving_multimodal_tokens/test_return_routed_experts (RuntimeError: Server exited unexpectedly from tests/utils.py:707) -- these fixtures launch a real engine and cannot start with the GPU hidden. Upstream shipped this fix with NO test (-k salt selected 0 of 38), which is why the dropped-salt bug survived silently.)
91. 7292ee2791 -> b0644513e PICKED+PUSHED (honor modality-scoped mm_processor_kwargs #53808; 5 files +172/-9, identical shortstat to upstream. WORKER-DISPATCHED (lane: grind, ~/dev/vllm), clean `cherry-pick -x`, 0 conflicts, patch-id 509d8c5b6 MATCHES upstream. No-escalation VERIFIED empirically: new `modality` param is keyword-only defaulting to None and merge_mm_processor_kwargs already returns a dict, so the modality=None branch returns a value-identical copy; confirmed with a semantics matrix (modality=None leaves values untouched; image/video overlay only their own nested kwargs, no cross-leak; audio/no-nested-keys unchanged). No DSV4/qwen4_exp/GLM-5.3-Flash call site passes modality -- GLM's two sites (glm5next/nvidia/multimodal.py:648,654, wtdcode 933876c38) call get_merged_mm_kwargs({}) with no modality and only .get() the result; qwen2_vl/qwen3_vl here are the official VL models, NOT qwen4_exp. TARGETED SUITE 105p/0f in 139s (tests/multimodal/test_processing.py + tests/models/multimodal/processing/test_qwen3_vl.py) with all 6 new tests confirmed by name via -rA; other consumers test_mistral3 21p, test_moss_audio 15p, test_idefics3 8p, transformers_utils/processors/test_glm5next 39p (correct GLM-5.3-Flash suite path). BASE-COMPARE for test_smolvlm.py: BASE d0c001892 8f vs NEW 8f, sorted FAILED sets diff EMPTY -> pre-existing.)
92. da0b2d8b17 -> 07289de03 PICKED+PUSHED (optimize Dots3 NOTE runtime #53517; 6 files +94/-85 -- 5 inside vllm/models/dots3_note/ (a fourth model family, not one of the three protected) + 1 shared line in vllm/config/vllm.py. WORKER-DISPATCHED (lane: grind, ~/dev/vllm). CONFLICT: contextual list-append -- wtdcode's Glm5Next entries and official's Dots3Note entries inserted at the SAME position in DEFAULT_BREAKABLE_CUDAGRAPH_ARCHITECTURES. Blame: HEAD side 54d298759f is NOT an ancestor of cutoff d4d703caf9 => wtdcode local addition; the 2 symbols the silent-loss scan flagged (RMSNorm, _RMSNorm) were removed by 9035151d6c which IS an ancestor => official renaming its own code to shared VisionRMSNorm, 0 dangling refs. Resolved as UNION. PATCH-ID MISMATCH AT COMMIT LEVEL (8670f33e vs 2b3902f0) -- EXPECTED AND INDEPENDENTLY VERIFIED BENIGN: per-file +/- line sets are byte-identical to upstream for ALL 6 files (md5 of sorted +/- lines equal); only hunk context differs because our tree carries adjacent wtdcode Glm5Next lines. SAFETY ORCHESTRATOR-VERIFIED: vs parent b0644513e the arch-name set lost NOTHING and gained exactly Dots3NoteForCausalLM + Dots3NoteMTPModel; all 10 GLM/DeepSeek entries intact => DSV4 and GLM-5.3-Flash default CUDA-graph mode unchanged. Taking --theirs here would have silently dropped 3 wtdcode GLM-5.3-Flash entries = a real default-path delta. Commit ships NO tests; narrowest importing suite tests/models/test_registry.py: NEW 3f/381p/13sk vs BASE 3f/381p/13sk, sorted FAILED sets diff EMPTY (3 ModuleNotFoundError on deps absent from the CPU image, pre-existing). Runtime semantic check: added 2, preserved all 7 DeepseekV32/V4 + Glm5Next, MISSING=[].)
94. f9d666f917 -> ab6758e0d PICKED+PUSHED (forward ownership in KV cache events #52067; 4 files +36/-10, shortstat identical to upstream. WORKER-DISPATCHED (lane: grind, ~/dev/vllm), clean `cherry-pick -x`, 0 conflicts. Faithfulness DOUBLE-PROVEN: commit-level patch-id EQUAL (7a6b908dd both sides) AND per-file sorted changed-line md5 identical for all 4 files. Silent-deletion scan (symbol-NAME granularity, before-side from git show 07289de03:FILE) run on all 4 files DESPITE the clean merge because auto-merge occurred in kv_offload/base.py -- 0 lost definitions. ORCHESTRATOR-VERIFIED safety: `ownership: str | None = None` is APPENDED LAST after `removed: bool` (base.py:158) and `locality` (159), so the 8 positional construction sites in tree are unaffected; and 0 files under qwen4_exp/glm5next/deepseek_v4 reference BlockStored or kv_events at all, so no protected family consumes these events. Block-lifetime/freeing was checked specifically because the brief flagged it as a silent-corruption class: conclusion = publication metadata only, no allocation or free path touched. TESTS: tests/v1/kv_offload/.../offloading_connector/test_events.py 22p/0f/0e in 29s; the commit's NEW assertions confirmed to have EXECUTED (not merely exist) by matching enclosing test names against PASSED lines; test_event_hashes_use_group_block_size PASSED. No base-compare needed (zero failures). STEER INCIDENT: orchestrator steered 'you have not picked yet, run the pick' based on a state snapshot that had already moved (HEAD was ab6758e0d by delivery time); the worker correctly REFUSED the literal instruction, re-derived state, and continued -- obeying it would have produced a duplicate pick. Verified after the fact: exactly 1 commit in 07289de03..HEAD.)
95. 2cf82bcdd1 -> eef9f770c PICKED+PUSHED (DCP fix NVIDIA DeepSeek-V3.2 / GLM-5.2 fused attention #50005; 3 files +102/-22: deepseek_v32/attention.py, deepseek_v32/common/kernels.py, tests/kernels/test_fused_deepseek_v32_norm_rope.py. WORKER-DISPATCHED (lane: grind, ~/dev/vllm), clean pick, 0 conflicts. ORCHESTRATOR-VERIFIED: exactly 1 commit off parent ab6758e0d, commit-level patch-id EQUAL (20e61de78 both sides), per-file sorted changed-line md5 SAME for all 3 files. Silent-loss scan run DESPITE the clean pick because attention.py auto-merged without a marker: lost=[], gained=[the new test]. No protected family imports deepseek_v32 (0 files under glm5next/deepseek_v4/qwen4_exp reference it), and the attention.py edits are gated on impl.dcp_world_size > 1. VALIDATION LIMITATION RECORDED HONESTLY: all 67 tests SKIP behind 'deepseek_v32 fused kernels require CUDA with fp8 (SM89+)' -> CPU provides ZERO behavioral signal for this pick; only collection (new test present, 1 occurrence) + clean imports of both changed modules were established, so no base-compare was meaningful. REAL BEHAVIOR DELTA NOTED BY WORKER (not dcp-gated): in _fused_norm_rope_kernel the Q RMS norm (pid==2) moved ahead of the negative-slot_mapping early return, so padding rows are now normalized+stored instead of returning early; writes masked/row-local/in-bounds, reachability confined to deepseek_v32 -> added to the GPU watch list rather than escalated. NOTE: this worker's completion notification never arrived; the result was recovered from the run-result JSON. Steer-hazard lesson re-confirmed: an earlier steer of mine asserting 'you have not picked yet' was stale and the worker correctly refused it.)
97. 2a61f060d3 -> 37d0e1eef PICKED+PUSHED (XPU ensure unquantized linear weight is N-contiguous #53536; 2 files +16/-0: vllm/envs.py, vllm/model_executor/layers/linear.py. WORKER-DISPATCHED (lane: grind, ~/dev/vllm) after a liveness probe proved children survive again -- the two-deaths trigger for orchestrator-direct mode had cleared because the CLUSTER (192.168.1.233:8000, which serves the agent's own model) went idle; jetson-222's :8000 is a DIFFERENT server and the two hazards are independent. Clean pick, 0 conflicts. Orchestrator-verified independently: exactly 1 commit off eef9f770c3, per-file sorted changed-line md5 MATCH for BOTH files (23dd0c51e3, 2e977cd04f), symbol-NAME silent-loss lost=[] on both, membership scan on envs.environment_variables gained exactly VLLM_XPU_FORCE_N_CONTIG_WEIGHT and lost nothing. Commit-level patch-id DIFFERS benignly -- the delta is exactly 2 hunk headers + 1 context line (upstream VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS vs our wtdcode VLLM_HIER_ALL_REDUCE at that slot), i.e. context only. NO-ESCALATION PROVEN BY GATE MATRIX, not assumed: the new arm is `elif current_platform.is_xpu():` inside UnquantizedLinearMethod.process_weights_after_loading, doubly gated by platform AND by the new env var which defaults False; 4-point in-container matrix showed CUDA+env-unset and CUDA+env-FORCED both leave the weight untouched, and is_xpu+env=1 rewrites while preserving values. WHY THE PLATFORM GATE IS LOAD-BEARING (worker caught this): qwen4_exp SUBCLASSES the changed method (nvidia/low_latency_gemm.py:116) and its warmup scan reads those weight strides, so a leaking arm would have rewritten GDN low-latency weights -- it cannot fire on CUDA/ARM. TESTS: tests/model_executor/test_cpu_unquantized_gemm_dispatch.py + layers/test_rocm_unquantized_gemm.py NEW 3p/1sk vs BASE 3p/1sk, fail-set diff empty, names confirmed by -rA. Upstream shipped NO test. HONEST LIMIT: no XPU hardware exists here, so the PR's actual perf claim is unverified on any platform.)
98. c6c33f2b1f -> 88e00426d PICKED+PUSHED (CPU support for FP16/BF16 persisted GDN state on AMX #52191; 4 files +575/-141: csrc/cpu/sgl-kernels/fla.cpp, vllm/platforms/cpu.py, tests/kernels/mamba/cpu/test_cpu_gdn_ops.py, tests/platforms/test_cpu.py (new). WORKER-DISPATCHED via the new versioned brief (.scratch/official-port-sweep-1/worker-brief.md). Clean pick, 0 conflicts, zero wtdcode-surface overlap. Orchestrator-verified independently: 1 commit off 37d0e1eef4, dirty 0, per-file sorted changed-line md5 MATCH on all 4 files, and commit-level patch-id EQUAL (af27197dd48a) -- the strongest faithfulness case in the sweep. fla.cpp scanned at C-declarator granularity: 10 -> 11 symbols, lost=[]. NO-ESCALATION PROVEN STRUCTURALLY: the only changed Python surface is CpuPlatform.check_and_update_config + a module-private helper whose sole caller is inside it; the dispatch point is vllm/config/vllm.py:1650 current_platform.check_and_update_config, which on this box resolves to CudaPlatformBase's override, not CpuPlatform's; and the block is additionally gated by torch.cpu._is_avx512_bf16_supported() = False on aarch64. Worker flagged the one real coupling honestly: qwen4_exp nvidia/model.py:708 and amd/model.py:705 READ cache_config.mamba_ssm_cache_dtype (the value this commit's policy decides) but the value is only mutated inside the CPU-only branch, so the families cannot observe a delta. TESTS: test_cpu_gdn_ops.py SKIPS wholesale (zero signal); the new tests/platforms/test_cpu.py fails 8/8 here, all on the PRE-EXISTING `assert vllm_config.device_config.device_type == "cpu"` (cpu.py:341, present in the parent at :275, and the commit diff contains zero occurrences of device_type) -- a host-shape requirement no CUDA box can meet. Rather than wave it off, the worker ran the REAL CpuPlatform.check_and_update_config over all 8 shipped param sets with only that assert neutralised: 8/8 matched the shipped expectations and the NEW branches fired (INFO cpu.py:249 bf16 SSM state, WARNING cpu.py:255 reset-to-fp32). HONEST LIMIT: ~340 lines of AMX/AVX512-BF16 C++ are unverified everywhere (image .so files are copied, never rebuilt; no AMX hardware), so the kernel this PR actually ships has no coverage here.)
99. 1b9539d37c -> 4529b9645 PICKED+PUSHED (AutoRound MXFP8 MoE support #51248; 3 files: new inc/schemes/inc_mxfp8_moe.py +196, inc_mxfp8_scheme.py +12 (get_moe_method), tests/quantization/test_auto_round.py +133. WORKER-DISPATCHED with context:fresh after the first attempt (a FORK of the orchestrator's now-large context) terminated at 178k tokens with no output and, verified, no tree change; fresh dispatch succeeded, so prefer context:fresh for grind children from now on -- worker-brief.md makes inherited context unnecessary. Clean pick, 0 conflicts, no wtdcode-surface overlap. Orchestrator-verified independently: HEAD 4529b9645 exactly 1 commit off 88e00426d, dirty 0, unmerged 0, per-file sorted changed-line md5 ALL_MATCH, symbol-NAME silent-loss NONE. NO-ESCALATION ESTABLISHED AS EVIDENCE NOT ASSUMPTION: the gate is CHECKPOINT DATA, not platform -- inc/config_parser.py:44-45 is_mxfp8 = ("mx_fp" in data_type and bits == 8), and inc_mxfp8_moe.py has zero current_platform references (get_min_capability 60). Worker ran the same probe on both trees over a CUDA platform class: BASE raises NotImplementedError("INCScheme does not support MoE layers") for mxfp8, HEAD resolves INCMxfp8MoEMethod; w4a16_gptq, w4a16_awq, mxfp4, w8a8_int and float extra_config outputs IDENTICAL across trees, mxfp8 the only DIFF. Specifically checked because GLM-5.3-Flash-W4A16-AutoRound is a protected family: bits=4 routes to INCWna16Scheme (inc_wna16_scheme.py:137-156), untouched by this commit, and the commit edits no shared AutoRound surface (no registry, no resolve_scheme, no base get_moe_method, no cases/*) -- so the only moved edge is crash -> works for an mxfp8 MoE checkpoint.)
100. 5bfd76372d -> 6e5b0dfa1 PICKED+PUSHED ([Renderer] Shutdown the renderer properly #52124; ONE file vllm/renderers/base.py, +shutdown()/weakref.finalize teardown). Worker timed out at its 40m ceiling AFTER committing and reporting, so the orchestrator verified and landed it rather than losing a good pick: HEAD 6e5b0dfa1 exactly 1 commit off 4529b9645, dirty 0, no sequencer, and **patch-id EQUAL to upstream (d85b2eff8240)** plus per-file changed-line md5 match -- patch-id equality is the strongest faithfulness evidence this sweep has produced, and it subsumes the silent-loss scan (an identical patch cannot have dropped context). Zero overlap with the wtdcode surface. WHAT IT ACTUALLY CHANGES (measured by the worker, not inferred): (a) explicit shutdown() is order-only different (cache -> mm pool -> main pool vs cache -> main -> mm, both wait=False); (b) NEW teardown for a renderer dropped without shutdown() -- offline LLM / crashed AsyncLLM now close the MM cache and shut both thread pools via weakref.finalize, also at interpreter exit (+1.7s measured with a forced 2s cache.close; base 0s); (c) if mm cache close() raises, head still shuts both pools while base skipped them -- but in BOTH trees the exception still escapes AsyncLLM.shutdown() and skips engine_core.shutdown(): pre-existing, unchanged, backstopped by the CLI engine-manager teardown. 6 exit modes rc=0 on both trees; forked engine-core children do not inherit-run the finalizer (multiprocessing exits via os._exit). RESIDUAL RISK, NOT PROVEN (worker died before these two, recorded rather than hidden): (1) double-run idempotency -- explicit shutdown() and the finalizer can both fire for one renderer; if finalize() is not deregistered by the explicit path, a second close() could raise during interpreter exit, which is a restart-only bug; (2) the +1.7s was measured on the offline/interpreter-exit path, NOT on a SIGTERM'd `vllm serve`, which is our deployment shape -- restart wall-time impact unattributed. Both are upstream-inherited behavior in a file with no wtdcode overlap, so they do not block the port, but they belong on the pre-production checklist.)

## Item 88 (swap/qwen-88) -- PUBLISHED AS A BRANCH, validation deferred by owner (2026-09-06)

Official e126687a9a landed as ONE commit **337d3f5dd** on parent = current `mitaka/backport` tip
`6e5b0dfa1`, rebased clean (42 files, 0 conflicts during rebase), `-x` provenance trailer + attribution
present. Pushed as **`origin swap/qwen-88`** and asserted three ways (local = origin = jetson =
`337d3f5dd`). `mitaka/backport` deliberately UNCHANGED at `6e5b0dfa1`; **item 88 stays UNCHECKED** -- this
is not a landing.

Owner decision: postpone the GPU validation, continue cherry-picking with the normal worker workflow.
Merge gate, agreed verbatim: (1) `test_get_kv_cache_config_mamba_hybrid_sharing_infeasible_no_indexer`
resolved or proven known-base, (2) meta-device instantiation + checkpoint key/shape coverage against the
real local index (`~/jetson-containers/data/models/huggingface/models--Qwen--Qwen3.8-Flash-Next-FP8`),
(3) owner's explicit go. Numerics need the 4-node TP4 window (~200 GiB; 61 GiB/node), which also takes down
the agent's own endpoint -> must be run as the scripted agent-free form, never interactively.

Why branch-not-merge matters operationally: the commit is a single revert away only while later picks do not
collide with its 42 files. **Orchestrator watch-item:** after each grind landing, check whether the new
commit touched any file in `git show --name-only 337d3f5dd`; a collision means the swap now needs
re-resolution and the revert is no longer free -- rebase the branch onto the new tip promptly rather than
letting debt accumulate.
101. 399247cc88 -> f7d71c72a PICKED+PUSHED (TRUE subject: [Bugfix][MM] Fix MiniCPM-o image processor reuse on Transformers v5 #54501 -- my heat-map had this mislabelled "[Model] support MiniCPM-o"; tracker lists shas so nothing else needs correcting. 3 files: vllm/model_executor/models/minicpmv.py (pure extraction of _get_checkpoint_image_processor out of get_hf_processor), minicpmo.py (calls it instead of hf_processor.image_processor), tests/.../test_minicpmv.py. WORKER-DISPATCHED and the new time-boxing rules worked: it committed and emitted the settled faithfulness verdict BEFORE running any test leg, so a timeout could no longer cost the analysis. Orchestrator re-verified independently: HEAD f7d71c72a exactly 1 off 6e5b0dfa1, dirty 0, unmerged 0, per-file changed-line md5 ALL_MATCH, and **patch-id equal (8331ce5e270e)** on both sides -- so the applied patch is byte-normalized identical to upstream's and the 7 test-name deletions in test_minicpmv.py are upstream's OWN renames, not merge loss. Silent-loss (worker, AST-based over imports+defs+classes+assignments with multi-line import blocks expanded -- the item-88 lesson): minicpmo 210->210 lost 0, minicpmv 312->313 gained the extracted helper, **no import line lost anywhere**. NO-ESCALATION PROVEN TWICE: (a) intersect of the 3 touched files with the 342-file wtdcode surface is EMPTY, and no registry / ModelConfig / mm-dispatch / placeholder-helper file is touched; (b) MRO argument -- MiniCPMVProcessingInfo is subclassed only by MiniCPMV4_6ProcessingInfo and MiniCPMOProcessingInfo, while the protected families use Qwen4ExpProcessingInfo(Qwen3VLProcessingInfo), Glm5NextProcessingInfo(Glm4vProcessingInfo) and DeepseekV4 (text-only, no register_processor), so the changed methods are not in any protected family's MRO. Test leg + in-container MRO probe were still running when the pick was landed: justified because patch-id equality means there is no resolution risk to validate -- any behavioral regression here is upstream's own, exactly as for every other clean pick.)
  101 follow-up (worker's banked final report): static **MRO reachability proof**, pure-AST walk over all
  of vllm/ on f7d71c72a -- `Qwen4ExpProcessingInfo` (nvidia AND amd), `Glm5NextProcessingInfo` all report
  `minicpm_roots_in_mro=NONE`, and the exhaustive enumeration of every class in the tree inheriting
  `MiniCPMVProcessingInfo` is exactly {MiniCPMOProcessingInfo, MiniCPMV4_6ProcessingInfo}, corroborated by
  an independent grep. Reachability gate is architecture dispatch (`registry.py:502-503` "MiniCPMO"/
  "MiniCPMV" vs `register_processor(info=Qwen4ExpProcessingInfo / Glm5NextProcessingInfo)`), not an env var;
  MiniCPM-V 4.6 additionally fully overrides `get_hf_processor` (incompatible with the vendored
  MiniCPMVProcessor) with no `super()` call, and `vllm/models/deepseek_v4/**` has no `register_processor` or
  MultiModal hit at all -- text-only, no processor path exists to reach. TWO THINGS THE WORKER VOLUNTEERED
  AND BOTH MATTER: (1) its probe printed `get_hf_processor defined in: []` for every class, and it declared
  those lines worthless because it had compared class names against a method name -- **an empty list from
  your own script can mean a bug, not absence, so sanity-check a probe against a case you know is positive
  before trusting a negative**; (2) the pytest leg was never reported, so item 101 has **no test evidence**
  -- accepted because patch-id equality removes resolution risk, and recorded as a limit, not as a pass.)

Addendum to 101 (worker's banked report, after the pick was already landed): the no-escalation case is now
carried by a **pure-ast MRO walk over every `vllm/**.py`** (no GPU import needed), not by prose. Result: the
complete set of classes repo-wide inheriting `MiniCPMVProcessingInfo` is `MiniCPMOProcessingInfo` and
`MiniCPMV4_6ProcessingInfo`; the protected families report `minicpm_roots_in_mro=NONE` (chain_size 2-3) --
`Qwen4ExpProcessingInfo` (nvidia and amd), `Glm5NextProcessingInfo`, and `deepseek_v4/**` has no
`register_processor`/`MultiModal` hit at all, so it has no processor path to reach. Gate is architecture
dispatch (`registry.py:502-503`), not an env var. MiniCPM-V 4.6 escapes twice over: it fully overrides
`get_hf_processor` (its own comment: incompatible with the vendored `MiniCPMVProcessor` used by 2.x/4.0/4.5)
and never calls `super().get_hf_processor` or `_get_checkpoint_image_processor`.
The worker also disclosed that one column of its own probe output (`get_hf_processor defined in: []`) was a
bug in its script -- class names compared against a method name -- and marked it informationless rather than
letting it look like evidence. That self-disclosure is the behaviour to keep rewarding.
OPERATIONAL: the "bank before you die" steer worked. The run reached 339k tokens and shipped a complete
verdict plus the probe instead of dying mid-analysis the way item 99's worker did.
102. 28bf75c9a9 -> e8407683f PICKED+PUSHED ([Bugfix][Frontend] Truncate prompt_is_token_ids with the prompt
#54509; 2 files: vllm/renderers/params.py, tests/renderers/test_chat_utils_prompt_embeds.py). Orchestrator
verified: parent f7d71c72a, exactly 1 ahead, dirty 0, per-file changed-line md5 MATCH on both files, and
**patch-id equal (a94072c334ce)** -- so silent-loss is impossible here regardless of scan, because the applied
patch is byte-normalized identical to upstream's. Swap-collision watch: NONE (renderer/params files are not
in the swap's 42-file surface).
INCIDENT (self-inflicted, no damage): my item-102 dispatch produced **two concurrent workers for the same
item in the same worktree** (1ef97c0e... and b8e4dd58...), violating one-writer-per-cwd. Caught it from the
"needs attention" ping on a run id I did not dispatch. Because both were assigned the *same* sha the risk was
a double-pick / stack-on-top-of-each-other, not divergent content: the second had already committed
e8407683f cleanly on the correct parent, so I interrupted the uncommitted twin and landed the committed one.
Leftovers cleared: stale .git/CHERRY_PICK_HEAD and MERGE_MSG removed after confirming tip had moved and the
tree was clean; stray untracked scratch i55_result.txt moved to ~/dev/scratch-artifacts/ rather than deleted
(it is another session's evidence, not mine to destroy). .cargo-home/ left in place (build cache, untracked,
ignored by the clean-tree convention).
RULE FOR NEXT DISPATCH: after every subagent dispatch, confirm the fleet has exactly one worker and that its
run id matches the one returned -- the duplicate was only visible because the attention ping carried an
unknown id. Check `subagent({action:"status",view:"fleet"})` before dispatching the next item.
102. 28bf75c9a9 -> e8407683f PICKED+PUSHED ([Bugfix][Frontend] Truncate prompt_is_token_ids with the prompt #54509; 2 files, renderers/params.py +5 and its test +47; clean pick, 0 conflicts, patch-id EQUAL a94072c334ce, per-file md5 match, zero intersection with the 342-file wtdcode surface, no swap-file collision). WORKER banked before touching a container, per the time-boxing rules. NO-ESCALATION PROVEN BY FOUR NESTED STATIC GATES (best reachability argument of the sweep): the new code is guarded by `prompt.get("prompt_is_token_ids")`, which is set in exactly one place in vll/ (renderers/hf.py:1284, the <prompt_embeds> sentinel path) or by a user; both producers sit behind `enable_prompt_embeds` (default False at config/model.py:291, and nothing in the tree sets it True); and even then _truncation_slice returns None unless truncate_prompt_tokens/max_input_tokens actually bites. TokenizeParams is instantiated, never subclassed, and the three protected families contain zero references to renderer/embeds symbols. NOT PROVEN, recorded as such by the worker itself: no container leg ran, so no negative control demonstrating the fix fires and the upstream-added test was never executed; and its silent-loss probe had only a one-sided (gained-side) control, so lost:[] is weaker evidence than gained:[...] -- though patch-id equality covers that ground independently.
103. 699e180df4 -> a0458e64a PICKED+PUSHED (Adaptive Width for DSV4 SparseMLA + SM120 FlashInfer Fix #53574; 2 files, sparse_mla.py + test_flashmla_sparse.py; clean pick, 0 conflicts, patch-id EQUAL 5bd47776edf9, both files byte-identical to upstream, wtdcode overlap EMPTY, no swap-file collision). ORCHESTRATOR-VERIFIED: HEAD a0458e64a 1 off e8407683f, dirty 0, unmerged 0, md5 ALL_MATCH. RISK ANSWER, with a correction to the commit's own title: DSV4 **does** execute the changed function on every platform (builder gate sparse_mla.py:201 `compress_ratio == 128` -> _build_c128a_metadata), but only takes the new wider view when `capability.major == 12` -- and that is the whole SM12x family, NOT 12.0 as the subject claims (worker caught this; heat map must not read it as 12.0-only). Proven in-container with the Triton launch stubbed: (12,0) and (12,1) -> (2,512) contiguous; (10,0), (8,7), None -> (2,256) non-contiguous and asserted equal to the literal pre-change `gbuf[:2,:256]` in shape AND stride, 3 positive controls green (the probe was checked against known-positives per the brief's rule). qwen4_exp/glm5next cannot reach it at all (no sparse_mla/c128a/deepseek_v4 reference in either family; the only FLASHMLA_SPARSE_DSV4 registration is registry.py:95). TESTS: collect 10/10 with both new parametrized IDs confirmed; HEAD 3f/3p/4s vs parent 2f/3p/4s, fail-sets identical modulo the commit's own 1->2 parametrization, and the shared failure is `RuntimeError: No CUDA GPUs are available` at cuda_init -- pre-existing and environmental. HONEST LIMITS the worker volunteered: the 2 new tests were NEVER observed passing (they allocate on cuda, unrunnable under the no-GPU rule) -- collecting and failing-identically-at-base is not passing; and SM120/12x kernel correctness itself is upstream's claim, unverified here (only host-side view shape/stride). Net: Jetson (not 12.x) sees a byte-identical else-branch.
104. d8de4ae322 -> 1d687b2ca PICKED+PUSHED ([Bugfix][KVOffload] P2P tier declares REQUEST_LEVEL on the producer leg #52912 -- heat-map label wrong again, worker read it from the object. 5 files, +282/-9; ONLY production file is vllm/v1/kv_offload/tiering/p2p/manager.py (+8 lines inside P2PSecondaryTierManager.on_new_request); 0 conflicts, patch-id EQUAL 0bc44fd19723 (stable AND unstable), all 5 changed-line md5 MATCH, diff-of-diffs differs only by sha + -x trailer, silent-loss LOST=[] on all 5 with positive control passed. Orchestrator re-verified independently (1 off a0458e64a, dirty 0, unmerged 0, files 5, ALL_MATCH, patch equal). wtdcode overlap EXACTLY ZERO; no swap collision. BEST-EVIDENCED PICK OF THE SWEEP, and the template to aim workers at: reachability answered by 4 nested default-closed gates (kv_transfer_config default None at config/vllm.py:401 -> connector None -> on_new_request never called; default spec CPUOffloadingSpec builds no secondary tier; secondary_tiers default []; the new branch needs kv_transfer_params["remote_decoder"]["kv_request_id"], which appears nowhere in the repo outside this manager, its test and its doc) PLUS an in-container sys.modules probe showing the p2p manager module is NOT loaded even after importing all three protected families (register_tier is a lazy loader -- registry lists p2p without importing it), with a POSITIVE control (explicit import -> True) so the negative is trustworthy. TESTS: HEAD 8f/434p vs parent 8f/365p on identical targets, fail-set IDENTICAL (8 pre-existing test_worker register_kv_caches failures, not root-caused), and **70 IDs only-at-HEAD all PASSED** by -rA name check (1 base ID superseded by its 2 new parametrizations, not lost). THE DECISIVE LEG: a FORCED NEGATIVE CONTROL on a separate copy of the tree (worktree never dirtied) -- deleting the 3 new lines makes test_on_new_request_policy[producer] FAIL with `assert BLOCK_LEVEL is REQUEST_LEVEL` while the other 3 params still pass, and the same node ID passes unmutated. That proves *semantic* absence at base, which patch-id equality alone cannot. Side evidence the insert landed: captured-log line ref moves manager.py:656 -> :664. Housekeeping done unprompted: container removed, 156 root-owned __pycache__ dirs sudo-removed, scratch tree outside the repo removed, :8000 200/200/200. LIMITS: no live engine load, no GPU/P2P transport.
105. eeb549a74d -> 82b1e968b PICKED+PUSHED ([Frontend] Move engine/protocol.py out openai folder #54492). **CONFLICT FORECAST WAS WRONG** -- clean pick, 0 conflicts, and the worker proved WHY rather than being lucky: the moved file is NOT in the 342-file wtdcode surface (touch=0 on all six move paths), so the R075 rename had no local edits to collide with; only 4 of 194 files overlap and all auto-merged with every wtdcode-added line surviving (39/53/17/15) plus all upstream additions. BIGGEST COMMIT OF THE SWEEP (194 files, 550+/585-, 1 A / 1 D / 191 M / 1 R075). Orchestrator-verified independently: patch-id EQUAL with -M (7c29a53fb125), name-status tree identical, spot md5 ALL_MATCH on the renamed protocol + abs_reasoning_parsers + exceptions + chat_completion serving, old path vllm/entrypoints/openai/engine/protocol.py CONFIRMED GONE at HEAD, 1 off 1d687b2ca, dirty 0. It is a PURE MOVE, not a semantic change -- proven by verifying all 32 top-level code blocks of the old protocol.py appear byte-identically in the new homes, with a negative control (a mutated block is rejected); the only non-import edits are 3 reasoning parsers moving request-type imports into `if TYPE_CHECKING:` (annotation-only, `from __future__ import annotations` present; ChatCompletionRequest kept as a runtime import where an isinstance depends on it). SILENT-LOSS AT SCALE: 12 names vanished from the moved file, 0 truly lost (9 classes now in serve/engine/protocol.py, GenerationError at exceptions.py:122); import audit over 193 files with multi-line imports expanded: 189 dropped old-path imports, **0 files use a name with no replacement**. Tree-wide the old path survives only in docs/features/reasoning_outputs.md:433 -- and that stale line is UPSTREAM'S OWN, present identically in the parent tree, so we reproduce it md5-exactly (fixing it would be fork drift; left alone). REACHABILITY: not affected -- the one touched module on the families' import path guards its import with TYPE_CHECKING (False at runtime), 0/194 files under vllm/models/**, and a clean-process probe shows byte-identical sys.modules for all three protected families on HEAD vs parent (36 family submodules; zero changed protocol modules; non-vacuity controls green). TESTS: 191 files compile; import sweep 130/134 HEAD vs 129/134 parent with the delta exactly = files existing on one tree only and 3 identical optional-dep failures; whole frontend graph imports at HEAD and old path raises ModuleNotFoundError (negative control); pytest -rA on 4 files chosen to cover every wtdcode-overlapping file: **233 passed at HEAD, 233 passed at parent**, per-file name counts identical (67/107/48/11), result-set diff empty both directions; plus a test-leg negative control (HEAD's anthropic test vs parent tree -> collection error on the new import path) proving the leg would actually catch a stale path. :8000 200 across all three legs. LIMITS: no broad CPU suites, no model evals (no default-path behavioural delta to measure), rust + buildkite changes are a doc URL and a CI path filter, artifacts copied not rebuilt (csrc untouched, 0 files).

## QUEUE HAZARD (2026-09-07, found at item 106 selection) -- do not trust swap-dependent.txt alone
Computing "next actionable" as (first unchecked tracker line whose sha is not in swap-dependent.txt) returned
**e126687a9a = item 88, the model swap itself**, because that sha is NOT listed in swap-dependent.txt (the file
holds the 45 items that depend on the swap, not item 88). Strict oldest-first would therefore re-dispatch the
swap onto mitaka/backport -- which is exactly the one thing the bounded waiver forbids, and a worker would
happily cherry-pick it since it is genuinely unchecked. Fix: the exclusion set is **swap-dependent.txt UNION
{e126687a9a}** (anything on swap/qwen-88, landed or not). When the swap is finally merged, item 88 gets ticked
and this exclusion retires. Generalise: a waiver list of *dependents* is not the same list as the *waived*
item -- check both when the queue is oldest-first, or the deferred item resurfaces as the next job.
106. 9acbc5360a -> b4d9c4231 PICKED+PUSHED ([KV Offload] Preserve KV event metadata until final residency removal #52068; 3 files; clean pick, 0 conflicts, patch-id EQUAL 8aca0f760ab6, all 3 changed-line md5 MATCH, -x trailer present; orchestrator re-verified parent=82b1e968b/ahead=1/dirty=0/unmerged=0). Overlap: only vllm/v1/kv_offload/base.py is in the wtdcode surface and wtdcode's 17 lines there (reserve_hits/release_reservation) are DISJOINT from OffloadingEvent -- a real containment argument, not "it merged so fine". SILENT-LOSS WITH A FORCED POSITIVE CONTROL ON THE SAME TOOL: same AST diff run after deleting class OffloadingEventsTracker reports LOST=13 and after deleting OffloadingEvent reports LOST=1, so LOST=0 on both changed files is a true negative; the only repo-wide name loss is upstream's own intentional test replacement (0 callers). STRONGEST ARGUMENT OF THE SWEEP -- behaviour is identical, not merely unreached: 3 serial default-off gates (kv_offloading_size None at cache.py:241 -> vllm.py:974 early return -> kv_transfer_config None; enable_kv_cache_events False; self_describing_kv_events default False, probe-confirmed) PLUS a producer census: the installed tree has exactly ONE OffloadingEvent(removed=True) producer (cpu/manager.py:256, medium=CPU, ownership=None) and grep for removal_expected returns exactly 2 hits (the field default and the read) -- nothing sets it True -- so active_residencies can only ever be {(CPU,None)}, every in-tree removal empties it, and the new branch is DEAD CODE in this tree. EQUIVALENCE PROBE WITH ITS OWN VISIBILITY PROOF: S1 (CPU/None, the only in-tree shape) emits byte-identical BlockStored/BlockRemoved AND identical metadata lifetime on head vs base, while known-positive S2/S3 DO differ (head retains metadata after a STORAGE/custom removal where base pops; base raises TypeError on removal_expected=) -- so the no-difference result means something. PYTEST: head 8f/309p vs base 8f/308p (base's +1 = upstream replaced 1 test with a 2-param version), fail-set IDENTICAL (the 8 are the known No-CUDA-GPUs register_kv_caches failures -- collect and fail identically at base, not passing); 4 new/renamed event tests confirmed PASSED by -rA name and re-run (4 passed, 19 deselected). rev-tree control (HEAD tests against reverted sources): 27 failed = the same 8 CUDA + 19 test_events.py failures, all `TypeError: unexpected keyword argument removal_expected`, which proves the FIELD is load-bearing; the worker states plainly that the RETENTION semantics rest on the probe, not on that leg. LIMITS: no GPU, no ZMQ KV-event stream, no model evals; the reachable-but-non-CPU residency path was exercised only at tracker-API level (S3), never through a real manager. :8000 200/200; container and scratch trees removed, no root-owned __pycache__ left.
107. 9debcd5990 -> 114366ca8 PICKED+PUSHED ([Test][Qwen3-VL] Cover compiled DeepStack input contract #53529). TEST-ONLY, PROVEN BY CONSTRUCTION: adds exactly one file (status A); `git diff --stat b4d9c4231..HEAD -- vllm/ csrc/ rust/ examples/ requirements/` EMPTY (orchestrator re-measured product_files=0); tree file count 6865->6866; path absent at base AND absent from the 342-file wtdcode surface. Faithfulness strongest possible: changed-line md5 equal, patch-id equal 91ecbef9cd7e, and **the blob hash is the same git object on both sides (2ac539dd..., orchestrator confirmed via rev-parse on both trees)** -- byte-identical by identity, not by comparison. Zero default-path delta is therefore proven rather than inferred; the Qwen3-VL vs qwen4_exp MRO worry is moot because no byte under vllm/ changes (fork fact re-confirmed: Qwen4ExpProcessingInfo(Qwen3VLProcessingInfo) at nvidia/model.py:817, amd/model.py:814; every private deepstack symbol the test reads exists here). Test-only follow-ups the brief demanded, both clean: does NOT touch tests/compile/conftest.py or add any fixture, nothing imports the module (grep rc=1 with a known-positive control), module basename unique so no package shadowing, and **zero references in .buildkite/ or .github/** -- the Compile group invokes explicit paths only, so this test runs in NO fork CI job. CPU evidence: LEG1 collect-only = 1 collected, which proves all imports plus the module-level @support_torch_compile resolve in our fork (the only CPU-visible signal, and it passed); LEG2 fails at line 65 torch.zeros(...,device="cuda") -- RuntimeError No CUDA GPUs, ZERO signal on the contract itself, explicitly NOT claimed as passing. Sibling control test_decorator.py fail-set identical base vs HEAD (4 CUDA failures both sides) and a pair run shows no collection-time contamination. LIMITS recorded as the worker wrote them: the deepstack payload contract is UNVERIFIED here (needs a GPU runner); the test logic was judged consistent by inspection only; and since no CI job references the file it guards nothing automatically in our fork -- its value is contract documentation. Note for the future GPU window: the new test is CUDA-gated with no skipif, so a broad `pytest tests/compile/` on a CPU box will now show one extra CUDA failure that is ours-by-upstream, not a regression. :8000 200/200; containers and scratch trees removed (sudo for root-owned .so); swap worktree untouched.
108. 810bc3250c -> 8ca7d1c86 PICKED+PUSHED ([Frontend][Performance] Resolve async media across modalities **concurrently** #54537 -- the word "concurrently" is why this item is not inert; heat-map label omitted it). 2 files (vllm/entrypoints/chat_utils.py +21/-14, its unit test); clean pick, 0 conflicts, patch-id EQUAL 8f3e08e3b5ad, both changed-line md5 MATCH, and a stronger-than-patch-id check: **both touched files are byte-identical between our base tree and upstream's parent tree**, so no hunk could mis-anchor. wtdcode overlap ZERO (neither chat_utils file is in the 342-file surface). Silent-loss lost=[] with our lost-set == upstream's lost-set and HEAD symbol set == upstream's (nothing extra crept in either).
  *** FIRST ITEM OF THE RUN WITH A REAL, MEASURED BEHAVIOURAL DELTA FOR OUR OWN MODELS *** Reachability PROVEN not assumed: qwen4_exp and glm5next register NO renderer, so they get HfRenderer (registry.py:85 + _VLLM_RENDERERS "hf"->HfRenderer) and reach the changed `resolve_items` via renderers/hf.py:1070 <- chat_utils.py:2193; DSV4 uses DeepseekV4Renderer which ALSO calls it (renderers/deepseek_v4.py:67) but deepseek_v4 has no multimodal code so its _items_by_modality stays empty. Text-only requests are provably delta-free via the guard at chat_utils.py:871-872 `if not self._items_by_modality: return None, None`, evaluated before every changed line. No family overrides it: `def resolve_items` has exactly 2 hits repo-wide (sync+async) and no class subclasses MultiModalItemTracker outside the two trackers. DELTAS (measured, not argued): (a) peak concurrent media fetches 7 vs 2 -- that IS the intended perf win; (b) **in 164/304 sampled configs the number of fetches STARTED differs: when an early modality fails, the new code has already issued the other modalities' downloads (real network side effects) before raising the same exception.** Bounded: connector.py:44-46 caps the pool at VLLM_MEDIA_LOADING_THREAD_COUNT (envs.py:80, default 8), so in-flight blocking media work cannot exceed 8 regardless of gather width. Exception TYPE and MESSAGE unchanged in all 304 configs; mm_data key order, item order and uuids identical in 304/304. EVIDENCE QUALITY: HEAD 159 passed/4 pre-existing fixture ERRORs vs parent 158/4 with IDENTICAL fail-set, both new upstream tests PASSED by -rA name, and TWO FORCED CONTROLS -- parent-source control fails the concurrency test with `assert 2 == 6`, and a reassembly mutation (reversed(item_groups)) fails with audio getting video's keys, so the passing suite is demonstrably not vacuous; the differential probe carries its own positive control (a shuffled variant was detected in 5/80). LIMITS: concurrency measured with synthetic awaitables, not MediaConnector against live URLs; no model eval (numerics argued unchanged via identical mm_data content+order, not measured); the vision_chunk modality was not exercised by the probe though it shares the same length-based slicing.
  -> ADDED TO THE PRE-PRODUCTION CHECKLIST (real, if small, behaviour change on a path our two multimodal flagship models use): (1) a mixed-media chat request where ONE media URL fails -- confirm the extra in-flight downloads do not produce orphaned connections, surprising error text, or latency blowups; (2) confirm VLLM_MEDIA_LOADING_THREAD_COUNT=8 is the right ceiling for Jetson's memory/conns under concurrent multimodal load; (3) spot-check a served qwen4_exp multimodal request before/after the swap merge.
109. bed3280f50 -> b57745322 PICKED+PUSHED. Heat-map title "Order CPU->GPU loads against the compute stream" **overstates it: the commit is COMMENT-ONLY** (numstat 4/2, and the orchestrator independently confirmed noncomment_lines=0 by filtering `^[+-]` against `^[+-]\s*#`). The `stream.wait_stream(current_stream())` the PR title describes is PRE-EXISTING context in parent blob d2625c237; only the four comment lines above it were rewritten. Worker ruled out a companion functional commit properly: blob-to-blob plain diff (no .gitattributes filter), single parent, `git log --all --grep 50696` returns exactly this one commit. So zero executable delta; nothing to reach, nothing to gate. Gate still quoted for the record (cache.py:241 kv_offloading_size None -> vllm.py:974 early return), call path proved (OffloadingConnectorWorker -> CPUOffloadingWorker.submit_load -> SingleDirectionOffloadingHandler.transfer_async at gpu_worker.py:621, comment at 746-751), protected families have zero kv_offload/Offloading/transfer_async references, and CPUOffloadingWorker is constructed only from kv_offload/cpu/spec.py and tiering/spec.py so the subclass route cannot reach it either. BEST PROBE-HYGIENE STORY OF THE SWEEP: its FIRST zero-delta probe (marshal.dumps(compile(...))) reported **DIFFERENT** on a comment-only commit, because two extra comment lines shift co_linetable/co_firstlineno; it refused to report that as a behaviour change, replaced the probe with one separating the instruction stream from the line table (4253 tokens identical both sides), and gave it a positive control (0fec3d652 on the same file) that correctly reported DIFFERENT on both checks. Lesson generalises: **for Python zero-delta proofs compare instructions, not bytecode** -- comments and blank lines move the line table and will make a correct probe cry wolf. Also answered the stream/event-lifetime question without hand-waving: per-transfer Stream() from _stream_pool and two pooled Events, wait_stream/wait_event/record inside `with current_platform.stream(stream)` -- all unchanged, so no stream or event is created, recorded, waited on, pooled or destroyed differently. TESTS: HEAD 33f/10p/6s vs BASE 33f/10p/6s, fail-set IDENTICAL (33 CUDA-gated cuda:0 transfer tests + test_load_waits_for_pending_compute_stream_writes), 10 CPU-runnable tests PASSED by -rA name on both trees. :8000 200/200; scratch trees and containers removed. PRE-PROD CHECKLIST (carried, do not treat as safe): (1) run test_load_waits_for_pending_compute_stream_writes on real CUDA -- it is the direct coverage for this ordering and is unexecuted here; (2) only if a protected family is ever launched with kv_offloading_size set + kv_offloading_backend=native (or VLLM_USE_SIMPLE_KV_OFFLOAD), smoke CPU->GPU load correctness under async scheduling with output comparison, since the zeroing-vs-load race the comment documents is GPU-observable only.
110. e0d27040dd -> e39151638 PICKED+PUSHED ([Bugfix][KV Offload][P2P] Preserve aborted loads until abort completion #52571; 2 files +97/-11; clean pick, patch-id EQUAL e58de20debe8, both changed-line md5 MATCH, orchestrator-verified parent/ahead/dirty/unmerged; wtdcode overlap 0/2 and BOTH files byte-identical between our base and upstream's parent, which is *why* it was clean -- the check that predicts the conflict rather than observing its absence). What it does: ClientRole.finish() stops doing `st.loads.clear()` + `_active_loads.discard()` and instead stamps `load.aborted_at = time.monotonic()` so the PRE-EXISTING abort-ack/timeout machinery emits the terminal result (the field, _ABORT_ACK_TIMEOUT_S and the drain loop are all pre-existing context -- title verified against diff, and it agrees, unlike 109). Plus 1 docstring + 2 log rewordings. Invariant coherence checked, which is the thing that usually breaks here: every `st.loads.pop` site (292/327/503) funnels through _on_load_terminal, which discards from _active_loads BEFORE _maybe_prune, so `_active_loads <-> non-empty st.loads` still holds and no new KeyError/assert exposure appears. Silent-loss: client.py 59->59 LOST=[], test file 241->248 LOST=[] +4 new names; **probe validated by TWO known-positive controls that both fired** (dropping collect_results -> LOST includes it; dropping AbortFetchMsg from the real 5-line multi-line import -> LOST=['AbortFetchMsg']), so LOST=[] is a true negative. Reachability: default-off gate cited (cache.py:241 -> vllm.py:974; p2p not even imported unless secondary_tiers names it) PLUS the two things gating cannot settle -- no changed line runs with offloading disabled (all 4 hunks inside ClientRole.finish/__init__/on_abort_ack, reachable only via P2PSession <- P2PSecondaryTierManager), and ClientRole has zero bases, is referenced by nothing outside vllm/v1/kv_offload, and vllm/models/** contains no kv_offload reference at all. TESTS -- the campaign's cleanest control yet: two trees differing in EXACTLY ONE FILE (diff -rq verified), with the change 101 passed; with client.py reverted and the new tests kept, 4 failed / 97 passed, and the 4 failures are precisely the 4 new tests failing with `KeyError: req-1` -- i.e. they reproduce the REAL bug (entry pruned before abort settles), not a collection error. Import-path self-check confirmed each tree imported its own client.py. :8000 200/200; house state verified clean. LIMITS: no GPU, no NIXL/ZMQ transport, no second peer -- the 4 tests are white-box state-machine tests poking session._client._requests, so they lock the internal contract, not wire semantics; real 10s timeout behaviour under load unmeasured. PRE-PROD CHECKLIST (carried): if a p2p secondary tier is ever enabled, an aborted request now keeps has_active_loads true until abort-ack or the 10s timeout, so tiering/manager.py:952 keeps the ENGINE STEPPING for up to _ABORT_ACK_TIMEOUT_S per aborted request -- watch step latency and _requests retention under abort storms.

## DECISION RECORD -- item 111 `4c58a0c398` SKIPPED, not ported (first declined commit of the sweep)

Worker held correctly: 1 of 3 files conflicts (`vllm/v1/kv_offload/cpu/shared_offload_region.py`), wtdcode
**rewrote the exact statements** upstream edits (blame: 80 + 53 + 5 lines wtdcode vs 20 official) and restructured
them into `_init_memfd`/`_init_shm`/`_map_and_populate`/`_wait_for_meta`/`_check_geometry`. Orchestrator verified
the hold was clean before deciding: HEAD back at `e39151638`, 0 unmerged, 0 staged, 0 dirty, no sequencer,
no CHERRY_PICK_HEAD/MERGE_MSG, 0 conflict markers anywhere in vllm/ or tests/.

Why SKIP rather than port, with the parts I re-measured myself rather than trusting the report:
1. **The defect is already fixed here, by a broader mechanism.** Fork holds `fcntl.flock(LOCK_SH)` on the region
   file for the whole process lifetime (creator 417, joiner 472) and runs `_reclaim_stale_regions()` (422) *before*
   the free-space check, reaping with `LOCK_EX|LOCK_NB` anything lock-free and >60 s old. That covers the SIGKILL
   leak for *every* crash path, not only this constructor. `grep -c barrier` on the fork file: **0**.
2. **A naive port makes /dev/shm strictly worse in this fork, permanently.** Upstream clears `_creator = False` at
   the barrier; the fork publishes `mmap_path + ".meta"` and only deletes it in `cleanup()` under `if self._creator:`,
   and I confirmed the reaper's filter from source is `name.startswith("vllm_offload_") and name.endswith(".mmap")` --
   so an orphaned `.mmap.meta` is invisible to every reaper and accumulates one per boot forever. The item whose
   purpose is not leaking /dev/shm entries would introduce a new leak.
3. **Upstream's own tests for this file are already red on our base for a pre-existing reason** (2 failed / 32
   passed at e39151638: `_init_shm` really flocks a mocked fd and the fork uses inline `os.statvfs` rather than the
   `check_shm_free_space` those tests monkeypatch). So "green after porting" was never on the table, and a
   mechanically clean pick would have looked broken for reasons unrelated to the change.
4. **There is a trap that a split resolution walks straight into**: `cpu/spec.py` picked cleanly and adds
   `barrier=` to the constructor call, while base `__init__` has no such kwarg -- "theirs for spec.py, ours for the
   region file" boots into `TypeError: unexpected keyword argument 'barrier'` on any run with offloading enabled.
5. **Nothing we run is affected.** Default-off gate re-proved by call path (`kv_offloading_size` None -> no connector
   -> `CPUOffloadingSpec` never built -> `SharedOffloadRegion` never constructed), zero references under
   `vllm/models/**`, and the live `:8000` server has **0** `/dev/shm/vllm_offload_*` entries.

Cost of skipping: we keep the reaper's one weakness -- a leaked region is only reclaimed by a *later* boot, and
pre-flocking builds' regions are indistinguishable from stale ones (base's own comment admits this). Benefit we
forgo: name removal without needing a later boot, and no dependence on the 60 s age heuristic.

**Revisit trigger (recorded so this does not become a silent permanent divergence):** if we ever launch with
`kv_offloading_size` set (i.e. `kv_offloading_backend=native`/`OffloadingConnector`, or `VLLM_USE_SIMPLE_KV_OFFLOAD`),
re-open this item. An authored port then has three design questions the worker deliberately refused to answer for us:
where the barrier goes for **both** `_init_shm` and `_init_memfd`; how `.meta` + `_check_geometry` late-joiner
support survives losing the name; and whether `barrier=` is passed for the tiering spec's scheduler-side
`rank=None` region. Also unproven and needing multi-rank GPU: barrier-group size == region-opener count for
PP>1 / DP>1 / elastic-EP (if they diverge the failure is a boot hang, not corruption).

The shm-lifetime evidence the worker produced is worth keeping regardless: in a container IPC namespace it showed
unlink-after-barrier leaves **one shared inode** with cross-process writes still visible (so no worker loses a
mapping), and its forced negative control showed unlink **without** a barrier produces two inodes under one
`engine_id` with divergent contents -- the silent-corruption mode the barrier exists to prevent. It also caught its
own first probe silently not running, because the scenario label doubled as the mode string, and noticed only
because the output matched its known-positive control.

Tracker state: marked `[~]` (skipped), NOT `[x]`. Excluded from the actionable queue by `skipped.txt`, which now
joins `swap-dependent.txt` + `{e126687a9a}` as a third exclusion source. If any future session sees 4c58a0c398 as
"next unchecked", that is the same class of bug as the item-88 near-miss: read all three exclusion files.
112. c5d840ff6a -> 269559d67 PICKED+PUSHED ([KV Connector][Offloading] Certify attention-only hybrid configs #...; 2 files; clean pick patch-id EQUAL f522083ee3b1, both md5 MATCH, orchestrator-verified + **fork symbols is_kv_cache_tensor_packed / compute_worker_kv_bytes_per_block re-checked present in the merged file**, because config.py IS one of the 342 overlap files and a clean auto-merge there still needed proving the fork side survived: it does -- the fork delta is confined strictly UPSTREAM of the gate the commit rewrites and terminates on the context line `single_group_spec = (`, so the rewritten region was byte-for-byte upstream on our side (that is *why* it was clean; tests/.../test_config.py has zero fork delta, blob-identical). TITLE-vs-DIFF agrees (unlike 109) and the headline the brief asked for is NEGATIVE in the good way: despite "attention-only hybrid", it touches NO kv_cache_interface.py and NO kv_cache_utils.py -- the new spec classes appear only as isinstance/type() operands inside the connector's own certification predicate -- so nothing escapes the default-off gate. Every changed production line is inside build_offloading_config, whose only non-test caller is OffloadingConnector.__init__, and factory.py registers that module with a LAZY importlib loader so it is not even imported on the default path. Silent-loss: only removal is upstream's own intended test replacement; import block gained 3 names with none lost (multi-line expanded, name-by-name). TESTS: HEAD 8f/326p vs parent 8f/323p, sorted FAILED lists byte-identical (the known 8 CUDA register_kv_caches), +3 net = 4 new params minus the deleted test, all new IDs confirmed PASSED by -rA name including the control pair that matters -- attention-hybrid asserts certified=True while swa-mla and mamba-hybrid assert certified=False, so the widening is bounded, not a blanket open. WORKER OVERRODE ITS OWN GUARDRAIL AND THIS IS THE LESSON: it reached 491k tokens (2x the stated limit) and needed an orchestrator steer to stop and report; it still delivered a complete, well-ordered report because the bank-early rule had already put the verdict down first. Fix applied to dispatches from here: harness-enforced toolBudget (soft 28 / hard 40 tool calls) instead of relying on the child's self-discipline. LIMITS: no GPU/TP>1, so num_kv_heads//tp_size and the MLA page-size branches are covered only at tp=1 by MagicMock configs; _validate_canonical_refs (the fork's fail-closed net at tiering/spec.py:414-448) was read, not executed; the 8 pre-existing CUDA failures remain undiagnosed. Orchestrator did the cleanup it owed (scratch-112 1.4G + host scripts removed). :8000 200/200.
113. 76ff0cdff2 -> 8fc9c187e PICKED+PUSHED ([Bugfix][ROCm] Preserve AITER unified-attention metadata; 2 files +59/-3; clean pick, patch-id EQUAL d58051353a39fa19 (orchestrator-computed both sides), md5 ALL_MATCH, parent 269559d67, ahead 1, dirty 0, unmerged 0; title verified accurate against the diff). Adds RocmAiterUnifiedAttentionMetadataBuilder.build_for_cudagraph_capture (preserves query_start_loc during graph capture instead of zeroing the shared CommonAttentionMetadata buffer) and re-points RocmAiterUnifiedAttentionBackend.get_builder_cls() at it. AMD REACHABILITY, verified by the orchestrator rather than accepted: both changed paths are AMD-scoped by filename; the new builder class is referenced ONLY inside the same file (lines 35/120/121); and the changed module's ONLY importer repo-wide is `registry.py:131`, a **lazily resolved BackendEnum string** -- so on a CUDA build the module is not imported unless that ROCm backend is explicitly selected. NOTE WHERE MY OWN CHECK ALMOST MISLED ME: my first "platform gate" grep hit `rocm_aiter_fa.py`, a *different* file, and showed `if current_platform.is_rocm():` at line 70 -- the actually-changed file `rocm_aiter_unified_attn.py` has **no module-level is_rocm guard of its own** (it imports `vllm._aiter_ops` and `rocm_attn` at top level). Non-reachability therefore rests on the lazy-registry importer argument, not on a self-guard. Re-checking my own assumption rather than reporting the first grep is what caught this. WORKER'S OWN LIMITS, kept verbatim in spirit: it reached **884k tokens on just 27 tool calls** -- which means the toolBudget I added as a guardrail after item 112 targets the WRONG METRIC (tool-call count does not bound tokens); the completion notification also never reached the orchestrator (run sat complete for ~114 min and had to be polled). Both are harness-level defects, logged. Evidence it did produce: the upstream test file is `pytestmark skipif(not is_rocm())`, so fork CPU/NVIDIA CI can NEVER regression-guard this fix (it bypassed the skip to execute it); the AITER kernel itself was never run (no ROCm device, no aiter library) -- builder behaviour proven with MagicMock metadata as in upstream's own test; the CUDA-platform candidate list was not printed dynamically (probe unpacked 2-tuples against 3-tuple candidates), so NVIDIA non-reachability is static + gate-control based, not a dynamic CUDA candidate list; and tests/v1/attention/test_attention_backends*.py fail en masse here on HF gated-repo 401s and were correctly NOT used as evidence. ORCHESTRATOR ADDS: AMD qwen4_exp/glm5next/deepseek_v4 builds are maintained code in this fork but unexecutable here, so any AMD-side behavioural delta is by inspection only; the mixed-backend graph-capture ordering (RocmAttentionBackend.build_for_cudagraph_capture still zeroes the shared query_start_loc while the AITER builder now preserves it) is a real cross-builder interaction on AMD that needs AMD hardware. Also: the CUDA-graph capture ordering between per-layer builders sharing that buffer is the residual risk if anyone ever enables AITER unified attention on AMD. Cleanup done by orchestrator (~/scratch/item113 incl. root-owned logs removed; worker had already deleted the 1.4GB parent tree). :8000 200/200.

## Item 114 `bd575a0d0b` RESOLVED by the orchestrator -> `b2a06c9e4` (NOT yet pushed: test gate open)

Worker held a 1-of-10 conflict in `inc/inc.py` with the wiring-graph analysis I asked for, which is what made the
resolution safe to decide: `resolve_scheme` is called at inc.py:383, **downstream of the conflict region**, so the
new FP8 schemes are reachable under an ours-resolution; and a **theirs**-resolution would delete
`name = _mtp_checkpoint_prefix(...)` while merged lines 354/360/366 still use `name` -> `NameError` on the FIRST
`get_quant_method` for **every** INC/auto-round checkpoint, i.e. it breaks GLM-5.3-Flash-W4A16-AutoRound loudly at
runtime (it compiles fine -- only execution catches it). Upstream's whole delta in that hunk is the deletion of one
comment line, so ours is correct.

Orchestrator-resolved with a scripted marker-strip (keep-ours, no hand editing), then verified non-vacuously:
`compile()` OK, 0 markers, fork symbols intact (`_mtp_checkpoint_prefix` x3, `if name and self.extra_config` at
line 353), and a **set-diff of my committed delta vs upstream's delta for that file = 200 vs 201 lines with the
sole difference being upstream's deleted comment** -- both sides asserted non-zero first, because my *first*
attempt at that comparison was silently vacuous: I ran `git diff -- <path>` while the path was unmerged, which
diffs against the conflicted index and produced an EMPTY left side, and an empty-vs-empty compare "passes".
Committed through the sequencer (`cherry-pick --continue`) so the upstream message and `(cherry picked from
commit bd575a0d0b...)` trailer are genuine rather than hand-written.

**PROCESS DEFECT FOUND AND FIXED: the 342-file overlap oracle is stale.** `c01b50e390..3bec275739` freezes at
Sep 2; the fork commit that caused this conflict, `d1ba3782f9`, is dated **Sep 4**. The stale set reported ZERO
overlap for all 10 files -- so "no wtdcode overlap" from it meant nothing here. Added `fork-surface.sh`, which
derives the surface from fork-local commits (subjects lacking an upstream `(#N)` marker), plus a brief rule that
a clean merge in model/quant areas must be re-checked against the refreshed surface.
  CORRECTION to the entry above: my first fork-surface.sh run produced **0 files** (`/dev/stdin: Permission denied`
  when piping the script over ssh) and I nearly recorded the refreshed oracle as working on that number. Re-run
  properly via scp: the refreshed surface is **larger than 342 files** and it DOES list `.../quantization/inc/inc.py`, i.e. it
  catches exactly what the frozen 342-file set missed. Same failure class as item 114's vacuous set-diff: a tool
  that silently produced nothing returns results that look like *findings* ("no overlap", "0 files") rather than
  like errors. Assert the output is non-empty and plausible before believing it.

## Item 114 `bd575a0d0b` LANDS as `b2a06c9e4` (pushed; local=origin=jetson) -- first orchestrator-resolved conflict

Test gate: HEAD 8f/84p/10s vs parent 7f/79p/10s; **the whole fail-set delta is one id the pick itself adds**
(`test_auto_round_model[auto_round:block_wise_fp8_on_cuda]`), dead with the same
`DP adjusted local rank 0 is out of bounds for 0 devices` assert as the 7 pre-existing model tests -> environmental,
meets the accept rule. 5 new upstream config/scheme tests pass; skip sets byte-identical; nothing removed/renamed.
**Decisive leg: the fork's own 4 `d1ba3782f9` MTP tests pass on both trees** -- the `_mtp_checkpoint_prefix` fix the
OURS resolution preserves is green. Strongest protected-family evidence of the campaign: a GLM-5.3-W4A16-shaped
AutoRound config produced a **byte-identical** parse/resolve/`get_quant_method`/scheme transcript parent vs HEAD
(md5 `cfcf11e4`); the only differing line is `resolve_scheme(fp8-block)` `NotImplementedError -> INCFp8Scheme`.
`is_fp8_block` needs `data_type=="fp"` + `packing_format=="auto_round:fp8"` + tuple `group_size`, disjoint from
int/mx_fp, so prepending the scheme cannot re-route a W4A16 layer. **Still untested by anyone:** an existing MXFP4
checkpoint violating `group_size==32`/`sym`/`packing_format==auto_round:llm_compressor`/`backend==auto` now asserts
at config construction where it previously loaded (HF gated, so reasoned-from-code only).
`tip 8fc9c187e -> b2a06c9e4 | conflicts=1 | resolution=OURS (sole delta vs upstream = 1 retained comment line) |
files=10 | tests=fail-set delta is new-test-only/CUDA | :8000=200 | overlap=d1ba3782f9 (Sep 4), INVISIBLE to the
stale 342-file oracle; refreshed surface=354 files`

### Two new defects, both in MY OWN verification, found during this land
1. **UNEXPLAINED local mutation in the Mac clone.** `git merge --ff-only` aborted because
   `vllm/model_executor/layers/quantization/inc/inc.py` was modified in `vllm-mitaka` -- by one inserted character:
   `def _mtp_checkpoint_pr/efix(...)` (a syntax error). Not mine, not a worker's (workers run on jetson), not
   present in HEAD, in `b2a06c9e4`, on jetson, or on origin (all asserted 0). Verified the local delta was exactly
   that 1 insertion/1 deletion, then discarded it. ~~I cannot explain its origin.~~ **RESOLVED in the next session
   (2026-09-08) -- see "The `pr/efix` mutation: resolved" at the end of this file. It was the owner's own PyCharm, and
   it happened at 09:23:51, not "at the moment of the merge".**
   *Rule adopted: the land chain always asserted `dirty=0` on the JETSON worktree and never once on the Mac clone,
   which is where merges and pushes actually happen. Assert tracked-dirty=0 on BOTH sides before every merge; if a
   mystery edit reappears, treat it as a possible second writer on the Mac worktree and stop to investigate.*
   *Rule strengthened (post-resolution): the invariant is not "clean at merge time" but **clean continuously** -- this
   corruption sat unnoticed for 12.5 h only because nothing needed to update that one file. A human IDE/editor with
   `vllm-mitaka` open IS a second writer; do not keep the push clone open in an editor during a grind.*
2. **My three-way tip assert was broken (new form).** `git ls-remote <remote> mitaka/backport` matches by ref TAIL,
   so it returned **two** refs and `$J` was two SHAs -- the equality test failed while an echo of the first 9 chars
   of each *looked* like it matched. Fixed with `--heads` + exact refname match. Third false-check today (vacuous
   `git diff` on an unmerged path, an oracle script that printed 0 files after failing to run, now this): the
   pattern is the same every time -- **a check whose output is compared visually instead of structurally.**

115. 82936c409d -> 3c2a91cc1 PICKED+PUSHED ([Tests][XPU] Limit Qwen2-VL generation length to avoid flaky numerical
 divergence #54172). **Cleanest item of the sweep**: conflicts=0, 1 file, 16+/8-, and the result blob is
 **byte-identical to upstream's** (`c364bab38`) while our pre-pick blob was **byte-identical to upstream's PARENT**
 (`45ad479d8`) -- i.e. zero fork divergence in this file, which is the strongest faithfulness tier available (strictly
 better than per-file changed-line md5 `ca1c3df0b70f00a33245d10c416952d5` match, which also held, and commit-level
 patch-id EQUAL). Fork-local overlap ZERO, recomputed per the fork-surface rule (every commit ever touching this file
 carries an upstream `(#N)` marker) -- not from the frozen 342-file set. Silent-loss: 14 symbols parent vs 14 at HEAD,
 `comm -23` empty, **with a positive control** (same pipeline returns 12 names when fed a synthetic removal), so the
 empty result is not vacuous. The commit edits a VALUE inside `VLM_TEST_SETTINGS["qwen2_vl"]`, not a key set (key set
 53 == 53 parent vs HEAD). Of 24 changed lines exactly **one is functional**: `max_tokens=64 if
 current_platform.is_cpu() else 128` -> `... or current_platform.is_xpu() ...`; the other 22 are comment lines. Verified
 independently by the orchestrator after the worker stopped (all of the above re-derived from git, not adopted from the
 report) + `compile()` OK and `cmp` byte-identical vs the upstream blob. `tip b2a06c9e4 -> 3c2a91cc1 | :8000=200 |
 swap-collision vs 337d3f5dd = 0 (42 swap files vs 1)`.
 **Unproven, recorded not fatal:** the worker hit its 1 h ceiling *after* committing (the cheap failure mode -- the
 commit survives, the analysis does not). It never ran the reachability probe or either container leg, so there is no
 in-container evidence and no proof that the protected families cannot reach this param. Accepted anyway because the
 change is test-only, in a file with byte-level fork parity to upstream, inside a `qwen2_vl` test-settings dict; the
 only way it alters a non-XPU/CPU path is if upstream itself is wrong.
 **Numbering caveat for future agents:** `heat-map.md` row numbers are QUEUE POSITIONS, not the `N.` landing numbers
 used in this file -- `82936c409d` is row 117 but landing item 115, because two queue rows (`dafbef15a1` swap-dependent,
 `4c58a0c398` skipped) never landed. Always key on the sha; never reconcile the two numbering systems.

### The `pr/efix` mutation: resolved (2026-09-08), and the method warning that came with it

**Not an agent. The owner's own PyCharm.** Evidence chain: the file's `mtime` at discovery was **09:23:51**, so it was
written ~11 h *before* the 20:43 merge that noticed it (the handoff's "at the moment of the merge" is wrong by 12.5 h);
the delta is a single **substitution** (`_mtp_checkpoint_pr`**`e`**`fix` -> `pr/efix`), i.e. one keystroke over a
selected char, not an insertion; `idea.log` shows PyCharm 2026.2 `IDE STARTED 2026-09-06 18:43:30` with project
`vllm-mitaka`, one continuous session (the uptime counter at 09:24:59 back-computes to that start), disposing the
project at **09:42:11** with `fileClosed inc.py` -- so that exact file was open in the editor across 09:23:51, and
PyCharm autosaves.
Excluded with positive evidence: the item-114 worker (only *read* the brief; its `python -c` calls were escaped *remote*
scripts); `/tmp/resolve114.py` (ends in `open(P,"w")` with a **relative** `P` -- genuinely dangerous, but it was scp'd
and run in `jetson:~/dev/vllm`, artifact present there, and no `inc.py.resolved` exists in either Mac clone); the
orchestrator's own 8 local writes in 09:00-09:45 (all `/tmp/*.py` or `.scratch/`); `swap88-mirror.sh` (writes only under
`.scratch/`); no crontab; no pi session rooted in the push clone ran that day.

**Method warning -- three of my "no evidence" results were vacuous, caught only by positive controls.** Grepping for
`_mtp_checkpoint_pr/efix` found nothing because the literal in the logs is the shorter `pr/efix`; grepping JetBrains
`LocalHistory` found nothing **even for `vllm`** (it is compressed storage, unreadable by grep -- and it last flushed
09:42, so it could not have covered the merge window anyway); and `grep -rl ... ~/.pi/agent/sessions` found nothing
**even for `jetson-222`** (broken corpus walk; `find -print0 | xargs -0 grep` found 1,607 files and 12 real hits).
*This is the same defect as the day's three false checks, mirrored: a check that silently returns nothing reads as an
absence. Before concluding "not recorded anywhere", grep the same corpus for a string you KNOW is there.*

116. 3593c964de -> dea406f89 PICKED+PUSHED ([ROCm] Add TheRock preview docker updates, Keep Python 3.12 and Ubuntu
 22.04 #49925). 7 files +1384/-7, conflicts=0, **zero `.py` files changed**. Fork-local overlap **0 of 7**, recomputed
 against the live 354-file fork-surface (which *does* contain `docker/Dockerfile`, `docker/versions.json`,
 `requirements/cuda.txt`, so the surface is live in this exact area -- the zero is not vacuous). Faithfulness at the
 strongest tier for **all 7**: result blob SHA equals upstream's for every file; the 4 modified files also have parent
 blobs equal to upstream's parent blobs (no resolution performed at all); the 3 new files verified `git cat-file -e`
 **ABSENT in both parents** (so they are pure additions, not silently-overwritten existing paths); per-file
 changed-line md5 7/7; patch-id equal (`bc47fff55e9d...`). `tip 3c2a91cc1 -> dea406f89 | :8000=200,200 | swap-collision
 vs 337d3f5dd = 0 (42 swap files vs 7)`.
 **`pyproject.toml` was the only platform-neutral risk and is proven inert:** the single added line is
 `a63ede7 = "a63ede7"` under `[tool.typos.default.extend-identifiers]` (line 141) -- consumed only by the `typos`
 pre-commit hook, not by `[build-system]`/`[project]`/`[tool.setuptools]`/`[tool.setuptools_scm]`, which the
 in-container `tomllib` diff showed each IDENTICAL (leaf keys 80->81, LOST `[]`, GAINED just that one key, CHANGED `[]`,,
 positive controls fired). `git grep -l a63ede7 HEAD` = 1 file, so the token exists nowhere else and an
 extend-identifiers entry can only *suppress* a lint finding. `pip install -e .` and the CUDA/aarch64 build are
 unaffected.
 **KNOWN UPSTREAM DEFECT CARRIED FAITHFULLY (do not "fix" it in a port):** `requirements/build/rocm.txt` pins
 `triton==3.7.1+git0263a6a6`, which is **unsatisfiable against the AMD index this very commit introduces** -- the index
 only serves `3.7.1+git0263a6a6.rocm7.14.0`, and upstream's own new `rock.txt` uses the correct full suffix. Verified by
 cross-platform `pip download` plus an independent `SpecifierSet` check with fired controls. This breaks **upstream ROCm
 CI only**; it can never bite our CUDA/aarch64 path (that index carries no aarch64 wheels at all: `linux_x86_64` +
 `win_amd64` only). Recorded as an observation, out of scope for a faithful pick -- raising it is an owner decision.
 **No coverage claimed:** no container leg on this host can build or validate a ROCm dockerfile (aarch64/Tegra, no AMD
 GPU, base images unavailable), and no pytest leg was run because 0 python files changed and no test imports a
 Dockerfile/requirements file -- a suite here would be theatre. The dockerfiles are verified byte-identical to upstream
 and have **zero in-tree consumers** (`git grep -ln Dockerfile.rock HEAD` is empty; they are invoked manually).
 **Hygiene:** removed `vllm/model_executor/layers/quantization/inc/inc.py.resolved` from the jetson grind worktree -- an
 untracked stray left by item 114's `/tmp/resolve114.py` (`open(P + ".resolved", "w")`). Untracked, so it never affected
 dirty counts, but it is exactly the kind of residue that makes a later `git status` read ambiguous. Its existence
 *only* on jetson independently corroborates the `pr/efix` resolution. `.cargo-home/` left untouched (pre-existing).

117. dbb7fffddb -> 413e14565 PICKED+PUSHED ([ROCm][MLA][DCP] Support causal multi-token verification #51705). First
  MLA/spec-decode item of the sweep -- and it was the **near-name collision**, not the diff, that could have bitten.
  7 files +1105/-111, conflicts=0. All 7 files have **parent blob == upstream's parent blob AND result blob ==
  upstream's result blob** (changed-line md5 7/7, patch-id equal `6d15f995...`). *Insight worth reusing: when both
  equalities hold, the silent-loss scan is structurally incapable of finding a merge artifact -- there was no merge. It
  still earns its keep as a control, but stop treating a clean scan as evidence of safety here.* The one name-level
  exception (`test_fp8_never_routes_to_gluon` gone from `test_rocm_aiter_mla_fp8_decode_routing.py`) is **upstream's own
  rename**; and the check that flagged it was itself faulty -- `grep -c "def $name"` matched the longer
  `..._gluon_under_...` because it had no word boundary.
  **The real trap, and why a loose grep would have produced a wrong all-clear:** DSV4 imports
  `vllm.v1.attention.**ops**.rocm_aiter_mla_sparse` (NOT touched by this commit) while the rewritten module is
  `vllm.v1.attention.**backends.mla**.rocm_aiter_mla`. A substring grep for `rocm_aiter_mla` over the protected families
  returns 1 hit; boundary-anchored `backends\.mla\.rocm_aiter_mla([^_]|$)` returns **0** -- and I ran the loose pattern
  as the control precisely to prove the difference is real, not luck. Same class as item 116's `--no-merges` false
  positive: *an unanchored identifier match is not a reachability result.*
  **Gate (verbatim, with a fired control):** `if rocm_aiter_ops.is_mla_enabled(): return [ROCM_AITER_MLA, ...] else:
  return [TRITON_MLA]`, where `is_mla_enabled() = _AITER_ENABLED and _MLA_ENABLED` and `VLLM_ROCM_USE_AITER` defaults to
  **False** (`vllm/envs.py`) -> observed CUDA list `['TRITON_MLA']`; forcing it True yields
  `['ROCM_AITER_MLA','TRITON_MLA','ROCM_AITER_TRITON_MLA']`, so the negatives mean something. `ROCM_AITER_MLA` appears in
  no CUDA/nvidia priority list (0 hits). `vllm/platforms/rocm.py`'s 26-line delta is entirely inside
  `RocmPlatform.check_and_update_config`; the live dispatch on our box is `CudaPlatformBase.check_and_update_config`
  (virtual call at `vllm/config/vllm.py:1650`), platform observed as `NvmlCudaPlatform`.
  **Import safety proven, not assumed:** `registry.py:53` resolves `ROCM_AITER_MLA` from a **lazy string**, so nothing
  imports the rewritten backend at CUDA startup; and an in-container import of all four modules
  (`...mla.rocm_aiter_mla`, `ops.rocm_aiter_mla_merge`, `backends.registry`, `ops.rocm_aiter_mla_sparse`) returned
  `RESULT=ALL_IMPORT_OK` with the `vllm.envs` control firing. The new merge op is imported only by the rewritten backend
  and one test. `tip dea406f89 -> 413e14565 | :8000=200,200 | swap-collision vs 337d3f5dd = 0`.
  **Coverage -- worker correction accepted (it contradicted my own brief, correctly):** I asserted no container leg here
  could execute these tests. Wrong for one file -- `test_rocm_aiter_mla_head_padding.py` **runs 34 tests that pass on
  this aarch64 host**, with a base-compare fail-set identical to the parent tree. *That result is worker-run and I did
  not re-execute it; recorded as reported.* The other three genuinely cannot run here
  (`test_rocm_aiter_mla_fp8_decode_routing.py:23`, `test_rocm_aiter_mla_mtp_split.py:15` hard-skip at module level on
  `not current_platform.is_rocm()`; `causal_verify_mask` skips at :210) -- so the **+385 new DCP-verify test lines are
  unexecutable on this host** and remain unverified by us.

118. 65ce85fcdc -> d6f60ba4b PICKED+PUSHED (Add Laguna-XS-2.1-INT4 to nightly CI #52961). 4 files +16/-2, all
  `tests/evals/gsm8k/configs/`, conflicts=0. Pre-image blobs **and** result blobs equal upstream for all 4; per-file
  changed-line md5 4/4; patch-id equal (`2602fe4029...`) -- no merge existed, so the silent-loss scan was formality and
  the worker said so itself (the item-117 lesson propagating). Membership sets, the actual point of the item:
  `models-blackwell.txt` **6->7, lost 0, gained exactly `Laguna-XS-2.1-INT4.yaml`**; `models-small.txt` **8->8, lost 0,
  gained 0**; yaml `Laguna-XS.2-NVFP4` key set 6->8 (gained `max_tokens`, `use_chat_completions`), exactly one value
  changed (`accuracy_threshold` 0.86->0.90), `server_args` byte-identical. Confirmed through the *real consumer path*
  (worker-run in-container `--collect-only`, HEAD tree vs `git archive` parent tree): collected IDs **6->7, lost 0,
  gained exactly `[Laguna-XS-2.1-INT4]`**.
  **My own framing was corrected twice by the worker, both times correctly.** (a) I called the `models-small.txt` `+1/-1`
  a reorder; it is **EOF-newline normalisation** -- verified independently from raw bytes, parent last byte `0x6c` (`l`,
  no newline) -> `0x0a`. A trailing-newline change and a reorder are indistinguishable in the raw diff and only a sorted
  **set** diff tells them apart; that is the whole argument for set diffs over diff reading. (b) It flagged that a BRE
  `([0-9]*)$` overlap filter miscounts upstream subjects like `…(#49241)` as fork-local -- but see the direction note
  below before acting on it.
  **Impact ~nil, verified not assumed:** the fork has **no consumer** for `tests/evals/gsm8k/configs/` at all --
  `.github/workflows/` is only `docker-publish.yml` + `pr-title.yml` with **0** hits for `gsm8k|evals|models-blackwell`
  (checked locally on the Mac), while `.buildkite/test_areas/lm_eval.yaml:68` (B200) and `.buildkite/test-amd.yaml:1218`
  are upstream infra we do not run; and the B200 job's `source_file_dependencies` are `csrc/` +
  `vllm/model_executor/layers/quantization`, which this pick does not touch, so it would not even trigger. HF asset
  `poolside/Laguna-XS-2.1-INT4` -> **200** public (independently re-checked; worker's negative control returned 401, not
  404, so gated-vs-missing was correctly discriminated). **Unproven by us:** neither accuracy threshold can be measured
  here -- both need a B200 plus a live server; upstream merged them with its own runs behind them. `tip 413e14565 ->
  d6f60ba4b | :8000=200,200 | swap-collision = 0`.

### Filter-direction note: the BRE overlap bug is CONSERVATIVE -- do not re-audit for it

Item 118's worker recommended re-auditing earlier items whose "zero fork-local overlap" came from a BRE filter. Tested
against a real subject (`[ROCm][MLA][DCP] Support causal multi-token verification (#51705)`):
`grep -vE '\(#[0-9]+\)$'` correctly excludes it; BRE `([0-9]*)$` **counts it as fork-local**. So the BRE bug's error
direction is a **false-positive overlap -- it manufactures extra overlap, never a false zero.** That is the safe
direction: it buys needless scrutiny, it cannot cause a blind landing. **No re-audit of items 1-117 is warranted on that
account.** The filters that *can* under-report overlap, and are the ones worth distrust, are: the frozen 342-file oracle
(documented, use `fork-surface.sh`), near-name substring matches without a word/module boundary (`ops.rocm_aiter_mla_sparse`
vs `backends.mla.rocm_aiter_mla`, item 117), and any filter that drops `Merge` subjects wholesale. Corollary for reading
future worker reports: **check which direction a suspected tool error fails in before spending an audit on it** -- the
same reasoning that makes a vacuous zero dangerous also tells you a conservative false alarm is not.

119. f5e441de10 -> 114c41e88 PICKED+PUSHED ([Bugfix][Test] Fix off-by-one error in sampled token rank causing flaky
 logprobs test #53976). 1 file `tests/v1/engine/utils.py` +6/-4; parent blob **and** result blob equal upstream
 (`b1e8c612a` / `324c9c9ad`), patch-id equal (`6418c30108...`), file sets identical, `-x` trailer present.
 Semantically live: `sampled_token_rank` and `prompt_token_ranks[rdx]` move **0-based -> 1-based**.
 **The worker produced an EMPTY final report after doing the entire job correctly** (72 tool calls, base-vs-head
 container comparison, own container removed, tree left clean). Everything below was **salvaged from its transcript**,
 not received -- see the harness-defect note underneath. Verified independently by the orchestrator from git.
 **Consumer path proven, not assumed:** the sole consumer is `tests/v1/engine/test_output_processor.py` (`assert
 ref_sampled_token_rank == smp_lp_rank` at :323; `ref_prompt_token_ranks` at :443/:459), and **all 8
 `test_logprobs_processor` params PASSED by name** -- so the changed branch was actually exercised, not just collected.
 Fail-set vs a `git archive` parent tree is **identical** (`comm -23` and `comm -13` on the PASSED/FAILED/ERROR name sets
 both empty); the 7 failures on *both* trees are `test_stop_token[...]` tripping the repo's own guard
 `test_output_processor.py:745-748` ("Test requires meta-llama/Llama-3.2-1B but facebook/opt-125m is in use"), and the 33
 ERRORs are the gated `AutoTokenizer.from_pretrained('meta-llama/Llama-3.2-1B')` fixture (401 anon). Both are known-base.
 **It also caught an inaccuracy in upstream's own comment and then confirmed the substance anyway:** the comment names
 `logprobs.py`, which resolves to `vllm/logprobs.py` (`range(1, num_logprobs+1)` at :194), **not**
 `vllm/v1/engine/logprobs.py` -- and 1-basis is independently corroborated by `(x >= values).sum(-1)` at
 `vllm/logprobs.py:27`. **Its own stated limit, worth keeping:** "identical fail-set proves no regression; it does NOT
 prove the shipped test would have failed pre-fix, because at real vocab the duplicate-into-top-k path is rarely hit
 (that is exactly why the bug was flaky)." `tip d6f60ba4b -> 114c41e88 | :8000=200,200 | swap-collision = 0`.

### Harness defect: a worker can finish correctly and report NOTHING (2nd report-loss in one window)

Item 115 hit its 1 h ceiling after committing; item 119 completed 72 tool calls of correct work and emitted an empty
final message (its `acceptance_report` call carried `{}`). Two report-losses in one window is the skill's stated trigger
to **switch to orchestrator-direct**, which is what item 120 onward uses until the mode proves itself again. Two
operational rules fall out of this and are worth more than the mode switch: **(1) a worker's silence is not evidence of
nothing-happened -- always `git rev-list --count <base>..HEAD` on jetson before concluding anything about a dead or quiet
child** (here it returned `114c41e88`, 1 ahead, clean, no sequencer, i.e. a complete landing with no report attached);
**(2) transcripts are recoverable** -- `~/.pi/agent/sessions/<project>/<session>/<run>/run-0/session.jsonl` holds every
tool call and thinking block, so salvage the analysis instead of re-running expensive container legs. The 24 h
exclusion-for-empty-output penalty in the skill is about worker incompetence; this was a transport failure, and burning
a good worker over it would be wrong.

### 120. `f9c7c6e090` -> `b819c11c7` — `[Rust Frontend][CI] Remove TCP port races from mock-engine tests (#54481)` — first orchestrator-direct pick, and the first item where a real test suite actually ran

**First orchestrator-direct item**, and the strongest verification tier the sweep has produced: `rust/src/mock-engine/src/tests.rs`
is **byte-identical to upstream** (parent blob EQ, result blob EQ, hunk md5 EQ, patch-id `d142931f300d44300b422e546c135834b5326941`
EQUAL), `fork_local=0`, outside the fork surface — **and** the crate was compiled *and executed*: `cargo test --locked -p
vllm-mock-engine` → **6 passed; 0 failed**. Every prior item either had no executable consumer on this host or was covered
by an import/collection proxy; this one has a green suite behind it.

**"Uncovered" has to be earned, not asserted.** `cargo` is absent on the Jetson host but present in the production image
(`/root/.cargo/bin/cargo`), and the Rust frontend is a real build artifact here — `cargo`/`rustup` appear in
`docker/Dockerfile.{cpu,rock,xpu,s390x,...}`, 5 references in `pyproject.toml`, 2 in build tooling — so "it's just a Rust
test file, no fork consumer" would have been an excuse, not a finding. Bounded attempt: `--locked` so the tracked
`Cargo.lock` cannot churn, `CARGO_TARGET_DIR=/t` mounted **outside** the repo so no build artifact can dirty the tree
(`tracked_dirty=0` throughout), `timeout 500`. Result: `Finished test profile in 47.56s`, `CARGO_EXIT=0`. Once it is built,
*running* the tests is nearly free, so stopping at "--no-run" would have left the cheap half of the evidence on the table.

**The commit deletes a test, and the count says so.** Upstream removed `mock_engine_connects_over_tcp` plus its
`free_tcp_address` helper (the bind-then-close-"free port" pattern that races), and added nothing: `#[tokio::test]` count
**7 → 6**, no gained functions. Because the result blob *is* upstream's, this is faithful by construction — the deletion is
upstream's own coverage decision, made because the TCP path is now covered differently rather than because it broke. Worth
carrying forward as a fact about the fork, not a defect: there is now no dedicated mock-engine-over-TCP test here.

**Third vacuous probe of the window, and the same root cause each time.** My first count grepped `#[test]`, which cannot
match `#[tokio::test]`, and returned `0 → 0` — a "no tests here" answer for a file holding six. The differently-written
second probe (`grep -cE '#\[tokio::test'`) returned the truth. This is the pattern from item 118's BRE bug and item 119's
`logprobs.py` path: a probe that returns a suspiciously clean zero is usually probing the wrong string, not finding an
absence. `awk '/fn /'` on a Rust file has the same trap — annotations live on the line above.

**Operational, for the next Rust item:** cargo writes its target dir as root through the bind mount, so the orchestrator's
own user cannot `rm -rf` it afterwards; and `rm -rf /t` from inside a container fails with `Device or resource busy` on the
mountpoint itself. Cleanup is `docker run --rm -v dir:/t <image> bash -lc 'rm -rf /t/* /t/.[!.]*'` and *then* `rmdir` on the
host. Root-owned build artifacts would otherwise accumulate per Rust item, invisible to `git status` and undeletable by the
account that owns the repo. (I did not capture the size before deleting it; the cleanup is the point, not the figure.)

`tip 114c41e88 -> b819c11c7 | :8000=200,200 | swap-collision = 0 | cargo: build ok, 6/6 passed`.

### 121. `a9dc631429` -> `b566d8c61` — `[Bugfix] Reject empty bad-word tokenizations (#53433)` — a HOT flag that turned out to be stale, and the counterfactual that proves a pick is not a no-op

**The HOT flag was wrong about *this* commit, and blob equality caught it.** The queue marked this item HOT, but both touched
files are **byte-identical to upstream's parent** at our tip (`vllm/sampling_params.py` and
`tests/test_request_input_bounds.py` both `parent EQ`), so the fork has not diverged on them *here*: `fork_local=0`,
patch-id `81b93db42cd59e0702375dad08562785ae10baf5` EQUAL, additive-only `+45/-0`. The surface list is a file-level,
history-level property; whether *this* pick can collide is a tip-state question, and the blob comparison — not the flag — is
what answers it. Had I treated HOT as "will conflict" I would have held a clean pick for no reason; had I treated it as
"ignore" I would have skipped the check that showed why it is safe. Upstream's parent for this commit is `f9c7c6e09`, the
item landed immediately before it, so the chain is contiguous.

**Production reachability confirmed, not assumed:** the new guard sits in `SamplingParams.update_from_tokenizer`, reached
from `vllm/v1/engine/input_processor.py:369` on every request that carries `bad_words` — so this changes runtime validation
behaviour, unlike the evals-only and CI-only items nearby.

**Executable leg, end to end, on a pure-Python item:** the tree is **built in place** (6 in-tree `.so`, incl.
`_C_stable_libtorch.abi3.so`), so mounting it at `/w` with `PYTHONPATH=/w` makes `import vllm` resolve to the *fork tree*
(`import vllm` → `/w/vllm/__init__.py`), not the image's own non-editable install at
`/opt/venv/lib/python3.12/site-packages/vllm`. Result: `tests/test_request_input_bounds.py` → **24 passed, 0 failed**, both
new tests passing by name. Three environment traps had to be cleared first, and all three are now known-good for future
Python legs:
1. The production image has **no pytest** — install it into the *ephemeral* container only.
2. That image pins pip to a local devpi index `http://localhost:3141/jp7/cu132/+simple/`, which is **refused inside the
   container** and fails with a misleading "No matching distribution found"; fix is
   `--index-url https://pypi.org/simple`. Cargo never hit this because crates.io is direct.
3. `tests/conftest.py` needs `tblib`, absent from the runtime image — `--noconftest` is correct for a self-contained file
   like this one (it builds its own fake tokenizers) and avoids dragging in the whole test stack. `PYTHONDONTWRITEBYTECODE=1`
   keeps `__pycache__` out of the mounted tree so `tracked_dirty=0`/untracked-count invariants hold.

**The counterfactual, and the two false starts it took to get it right.** "Do these tests fail without the fix?" cannot be
answered by checking out the parent and running them: the parent tree collects **22 items, `-k empty` selects 0** — the tests
don't exist there, so 22-vs-24 is a *collection-count* check, not a behaviour check (the first attempt also failed outright
with `No module named 'vllm._C_stable_libtorch'`, because a fresh worktree does not contain the **untracked** in-tree `.so`
files; `cp vllm/*.so <worktree>/vllm/` fixes that). The correct construction is a *mismatched* pair — parent module + new
test file — giving **2 failed** on the parent `sampling_params.py` versus 24 passed on the picked tree. That is what proves
the guard is load-bearing rather than decorative. Worktree was created detached at the parent, then `worktree remove
--force` + `prune`; verified `worktrees=2` (main + `vllm-swap88`) and `dirty=0` afterwards. One near-miss worth recording: my
first cleanup draft did `rm -rf /w/.git` inside the worktree, which would have deleted the gitdir *pointer file* and wedged
`git worktree remove` on the shared repo — a worktree's `.git` is not a directory.

`tip b819c11c7 -> b566d8c61 | :8000=200,200 | swap-collision = 0 | pytest: 24 passed; pre-fix counterfactual 2 failed`.

### 122. `85c1365bd9` -> `2cc1a12bc` — `[Bugfix] NemotronHMTP: add hf_to_vllm_mapper so quant exclusions reach the MTP draft (#53790)` — plus a self-inflicted "verification" that verified nothing

Small clean item: one file `vllm/model_executor/models/nemotron_h_mtp.py`, **`parent EQ` / `result EQ`** (fork base identical
to upstream's parent), additive-only `+11/-0`, patch-id `3f8a84fd90f8093b8df2bc8e08cec223566b80b7` EQUAL, upstream parent is
the item landed immediately before it. NemotronH is not a fork-served model (production is Qwen3.8-Flash-Next), so serving
impact is nil; it is still a model-executor file, so it got a semantic check rather than a shrug.

**Consumer path proven rather than inferred:** the class now carries `hf_to_vllm_mapper = WeightsMapper(...)`
(`nemotron_h_mtp.py:321`), and the single reader is `vllm/model_executor/model_loader/utils.py:280-285`, which does
`getattr(model_class, "hf_to_vllm_mapper", None)` then `quant_config.apply_vllm_mapper(hf_to_vllm_mapper.get_rename_ma…)` —
i.e. the commit does exactly what its subject line claims (quant exclusion patterns written in checkpoint space now reach a
draft built under `mtp`). Confirmed live: importing `NemotronHMTP` from the mounted fork tree yields the mapper object
(`orig_to_new_substr={'embeddings': 'embed_tokens'}`) rather than `None`.

**My own reusable script lied to me, by reuse.** `pick122.sh` was `pick121.sh` with the sha/base seds applied — so its
"step 3: the new guard is present and reachable" grepped item 121's `bad_words` string and reported it present, which is
true of the *tree* (121 is an ancestor now) and completely irrelevant to 122. Parameterising shas across copies is fine;
carrying over an item-specific assertion is not, and it produces a green line that proves nothing. The separate `sem122`
check above is what actually verified this commit. Rule: when cloning a probe script, the item-specific assertions must be
replaced or deleted — a copied assertion is worse than no assertion, because it reads as coverage.

**Harness gotcha, second silent no-op of the window:** two consecutive `bash audit.sh` invocations failed with
`No such file or directory` while their exit status was swallowed by a pipeline — the script lives at `/tmp/audit.sh`, not in
the `.scratch` dir I had `cd`'d into. Two "counts looked fine" conclusions were therefore drawn from empty output. The audit
did run for item 121 (its tail printed `exclusion set=47 actionable=153`), but the explicit `checked=…` line was cut by a
`tail`, and I read the absence as agreement. Re-running with the absolute path gives the counts below. Same lesson as the
vacuous greps above: **empty output from a checker is not a pass.**

`tip b566d8c61 -> 2cc1a12bc | :8000=200,200 | swap-collision = 0 | import+mapper present, no test leg (no consumer for NemotronH here)`.

### 123. `f5c3cc240b` — `[Perf][Kernel] Tune cooperative topk for medium batch-sizes (#53382)` — **HALTED: wtdcode-functional conflict, owner decision required** (not landed, not skipped, tree left clean)

Picked, conflicted on `vllm/model_executor/layers/sparse_attn_indexer.py`, and **`git cherry-pick --abort`ed** — verified after
abort `HEAD=2cc1a12bc dirty=0 unmerged=0`, sequencer absent. This is the halt condition the brief reserves, so it is recorded
rather than resolved. Nothing else in the commit conflicted: the two `csrc/libtorch_stable/cooperative_topk.*` files are
fork-identical (clean), `tests/kernels/test_top_k_per_row.py` merged (it *is* fork-diverged, +33, but in a different region —
the fork's own `test_topk_between_k_and_2k` and upstream's new `test_cooperative_topk_cs2` coexist), and swap-collision is
empty.

**The conflict is semantic, not textual.** One line, two axes:

| | predicate |
|---|---|
| upstream parent | `and num_rows <= 32` (where `num_rows = logits.shape[0]`) |
| upstream `f5c3cc240b` | `and num_rows <= 64` |
| fork tip (wtdcode, +231/−19 in this file) | `and num_padded_tokens <= 32` (where `num_padded_tokens = batch_size * next_n`) |

The fork did not merely rename it — it **re-keyed** the predicate from the per-rank logit row count to the unsharded padded
token count, with a comment stating why: *"Keyed on the batch's row count, not this rank's: a shard must not pick a different
top-k kernel than the replicated path would, and a batch that fits the cooperative kernel fits it on any shard of itself."*
So upstream's threshold bump and the fork's TP-sharding fix land on the same physical line, and `<= 32` vs `<= 64` is a
question about *which quantity bounds the kernel*.

**Recommended resolution: `and num_padded_tokens <= 64`** — keep the fork's key, take upstream's threshold. Three independent
reasons, the first two verified from source rather than assumed:
1. **`num_rows ≤ num_padded_tokens` is provable.** `indexer_decode_shard_rows` (`vllm/v1/attention/backends/mla/indexer.py`)
   returns `(lo*next_n, hi*next_n)` with the caller's `assert 0 <= group_lo < group_hi <= batch_size`, so
   `num_rows = logits.shape[0] = (hi−lo)*next_n ≤ batch_size*next_n = num_padded_tokens`. Keying on the padded count is
   therefore *conservative*: `num_padded_tokens <= 64` ⇒ `num_rows <= 64`.
2. **The bound is enforced kernel-side anyway.** Upstream's `.cu` carries `TORCH_CHECK`-style `num_rows <= 64` ("...use
   persistent_topk for larger batches"), and the new dispatch adds a `CS == 2` two-CTA path for `num_rows <= 33` (the old
   comment `32 = max clusters for CS=4` is removed). A too-large row count raises loudly rather than silently corrupting.
3. It preserves the fork's shard-consistency intent exactly, changing only the numeric threshold, which is all the upstream
   commit is about.

**Why I did not land it despite (1)-(3).** It sits inside the fork's DSV4/TP-sharding rewrite, in a function whose author
left an explicit rationale for this very predicate; the auto-land gate covers mechanical conflicts, not judgement calls about
wtdcode kernel-selection. **Serving risk today is zero either way** — `use_cooperative_topk` additionally requires
`has_device_capability(90)`, and both this host and the production container report **SM 8.7** (`torch.cuda.get_device_capability(0) == (8, 7)`),
so the cooperative path is unreachable on the Jetson cluster; and any `.cu`/`.cuh` change is inert until an image rebuild,
which is separately owner-gated. Deferring is self-consistent: the fork keeps `<= 32` in both the dispatch and the matching
test skip-guard.

**To apply once approved** (single-token resolution, then re-verify):
`git cherry-pick -x f5c3cc240b` → edit the conflicted line to `and num_padded_tokens <= 64` → `git add` →
`git -c core.editor=true cherry-pick --continue`; then confirm `git diff <base> HEAD -- <testfile>` equals upstream's hunks
for the non-conflicting files, that the fork's `test_topk_between_k_and_2k` and upstream's `test_cooperative_topk_cs2` are
both present, and that the only delta in the python file is that one line. If preferred, an alternative is to take the
`csrc`/test hunks and *drop* the dispatch bump (fork stays at 32) — behaviourally identical on SM87, and defers the
judgement rather than making it.

### 124. `24d42f3553` -> `dfa41c2b4` — `[CI] Mark 1-GPU L4 test steps with device: l4 for EKS migration (#54549)` — landed, plus a correction that lowers the claimed strength of every earlier "patch-id EQUAL"

Clean pick of 5 `.buildkite/test_areas/*.yaml` files (+15/−0). Four files were fork-clean (`blob EQ`);
`.buildkite/test_areas/kernels.yaml` is fork-diverged (+6/−2 — the fork renamed a FlashMLA step to an "MLA Kernel Test" step
and added flashinfer paths to its path filter), so byte-identity was impossible there and the correct test was *delta*
equality: **`delta_vs_upstream IDENTICAL` for all five files**, and the fork's own five added lines all still present in the
result (verified line-by-line with `grep -Fc --`). All 5 files still `yaml.safe_load`. Fork runs no Buildkite pipeline (its CI
is docker-publish + pr-title), so serving/CI impact is nil; the change matters only if this branch is ever pointed at
upstream's EKS pipeline. Note this commit's upstream parent is `f5c3cc240b`, the **blocked** item 123 — cherry-pick order does
not require contiguity, and nothing here touches the indexer.

**Correction, applies backwards over the whole sweep: `patch-id EQUAL` does NOT imply byte-identity.** Item 124 is the first
case where the two signals visibly disagree — `kernels.yaml: blob NE` alongside `patch-id EQUAL (af885b70…)`. `git patch-id`
hashes only the added/removed lines and ignores line numbers and surrounding context, so a hunk applied into a *modified*
file still yields an equal patch-id. Several earlier entries in this log cited patch-id equality with a gloss like "implies no
fork-divergence on touched files" — that gloss is wrong, and the `/tmp/pick.sh` wording has been fixed. **Nothing computed on
it is invalidated**: in every prior item the load-bearing evidence was the independent `parent EQ` / `result EQ` blob
comparison (the strongest tier, which *does* prove byte-identity), and patch-id was corroborating, not load-bearing. The
durable rule: **blob identity proves sameness of state; patch-id proves sameness of change. Never let the second stand in for
the first.**

**Two self-inflicted checks on this item, both mine, both caught before they could mislead.** (1) I ran a probe against
`24d42f3553` by `sed`-ing a *previous* probe script that had itself been edited in place, so the substitution silently no-op'd
and I "probed" already-landed item 122 — which reported `DIVERGED` for a file whose fork-side difference is simply *the pick I
had already landed*. Reproduced twice now (also on item 122's copied assertion), so the sed-copy pattern is retired in favour
of two parameterised scripts, `/tmp/probe.sh <sha>` and `/tmp/pick.sh <sha> <base>`, with the probe now self-guarding: it
prints `!! <sha> IS ALREADY AN ANCESTOR OF HEAD` via `git merge-base --is-ancestor` rather than reporting a misleading
divergence. (2) A `grep -Fc "$line"` where the line begins with a YAML list dash (`- label: …`) was parsed as option flags
(`grep: invalid option -- ' '`) and returned an empty count that looked like "the fork's line is gone"; `grep -Fc --` fixes
it. And an inline `python3 -c "…\n…"` mangled exactly as the brief warns — the YAML check had to become a real scp'd file.
**A check that errors is not a check that passed**, and two of these three would have read as results if I had been skimming.

`tip 2cc1a12bc -> dfa41c2b4 | :8000=200,200 | swap-collision = 0 | 5 files parse; only change to device labels is +8 device:l4`.

### 123 (resolved). `f5c3cc240b` -> `84c58b1eb` — cooperative-topk 32→64, landed with the fork's key retained: `and num_padded_tokens <= 64`

Owner approved the recommendation from the blocked entry above, so the conflict was resolved rather than deferred. Chosen
resolution: **keep the fork's key, take upstream's threshold** (`num_padded_tokens <= 64`). The rejected alternative — take the
`csrc`/test hunks and drop the dispatch bump — would have manufactured a *permanent* local deviation in the file that already
conflicts on every rebase, to dodge a one-line change that is itself a one-commit revert. Faithfulness is the cheaper long-run
position here.

**The resolver refuses rather than guesses** (`/tmp/resolve123.py`, run in-container): it locates the conflict structurally
(one `<<<<<<<`, one `=======`, one `>>>>>>>`, correctly ordered), asserts the two sides are *exactly*
`and num_padded_tokens <= 32` and `and num_rows <= 64`, and exits non-zero without writing if anything differs — at which point
the driver `cherry-pick --abort`s. On success it reported `remaining markers: 0` and `stale 'num_rows <=' occurrences: 0`.
The driver also *inverts* the usual expectation: if the pick ever applies **cleanly** it aborts (rc=3), so a future re-run can
never silently bypass the recorded decision.

**Verification, and its honest ceiling.** `file sets identical (4)`; both `csrc/libtorch_stable/cooperative_topk.*` are
`blob EQ` + `delta IDENTICAL`; the test file is `blob NE` (fork-diverged base) but `delta IDENTICAL`, with the fork's
`test_topk_between_k_and_2k` **and** upstream's `test_cooperative_topk_cs2` both present and no stale `32 rows` references.
The python delta is exactly two lines, and normalising the identifier gives **`identifier-only difference? YES`** — our
`-num_padded_tokens <= 32 / +…<= 64` versus upstream's `-num_rows <= 32 / +…<= 64`. Kernel-side, our tree now carries the
`num_rows <= 64` bound. Both files `ast.parse` and the module imports. The variable-binding question is not newly opened by
this pick: the fork *already* dereferenced `num_padded_tokens` at that same line (assigned at 703, used at 786), so the pick
inherits a property it cannot change.

**No runtime leg is possible for this item on this box, for three independent reasons — stated as a gap, not glossed.**
1. **The standing never-touch-GPU rule.** I run every container with `CUDA_VISIBLE_DEVICES=""`, so `tests/kernels/test_top_k_per_row.py`
   cannot execute: my first run reported **138 failed in 26 s**, and the actual one-line reason is
   `RuntimeError: No CUDA GPUs are available` (`torch/cuda/__init__.py:529`). Those 138 are *my own guard*, not the change.
2. SM 8.7 (this host and the production container) has no thread-cluster support, and `use_cooperative_topk` is additionally
   gated on `has_device_capability(90)` — the changed predicate is dead code here regardless of its value.
3. The in-tree `.so` **predates** the `.cu` edit, so the new 64-row CS=2 path is not even present in the binary that would be
   exercised; the source/binary skew resolves only at the next image build, which is separately owner-gated.
So the evidence for this item is static + structural, and behavioural confirmation is deferred to a Hopper build. Serving on
the Jetson cluster is provably unaffected.

**Another vacuous check caught before it reached the report.** My base fail-set comparison printed `new failures on head: 0`
and `only-on-base: 0`, which reads as "no regression" — but both files were **empty** because the collection pipeline died on
`sed: -e expression #1, char 10: unknown option to 's'`, so the diff was 0-vs-0. Third time this window an "0 findings" result
was really a broken probe (after the `#[test]` grep and the wrong-cwd audit). The guard worth keeping: **when a comparison
reports zero of everything, check that both sides are non-empty before believing it.** Worktree used for the attempt was
cleaned (`worktrees=2`, `dirty=0`).

`tip dfa41c2b4 -> 84c58b1eb | :8000=200,200 | swap-collision = 0 | blocked.md cleared | runtime leg: NOT POSSIBLE here (CUDA intentionally disabled; SM87; stale .so)`.

### 125. `d61b6e1878` -> `0edb36733` — `[Bugfix][Spec Decode] Take the DFlash draft's RoPE layout from its own config (#54373)`

Top tier: all three files (`qwen3_dflash.py`, `vllm/v1/spec_decode/dflash.py`, `v1/worker/gpu/spec_decode/dflash/utils.py`)
probed **CLEAN** and landed **`blob EQ`** with `delta IDENTICAL` and matching numstat (`+5/−46`), so the fork's result is
byte-identical to upstream's — the resolution policy settled in item 123 was never engaged because there was no conflict. No
swap collision; sequencer clean; `:8000` 200 before and after.

Impact is real but gated: this makes a DFlash draft take its RoPE layout from its *own* config instead of the target's
(−46/−15/−6 lines of inherited-layout plumbing). It only affects runs that actually attach a DFlash draft to a Qwen3-family
target, and it is inert on the running production container, which executes the prebuilt image rather than this tree — like
every item in the sweep, behaviour only moves at the next image build, which stays owner-gated. No runtime leg: the path needs
a draft model plus GPU, and the GPU is intentionally not exposed to my containers (see item 123's note).

`tip 84c58b1eb -> 0edb36733 | :8000=200,200 | swap-collision = 0`.

### 126. `07ea9350ba` -> `9559cad0e` — `[Kernel][Gemma4] Prune Triton sliding-window tiles for multimodal prefixes (#53147)`

Clean, top tier: all three files probed **CLEAN** and landed **`blob EQ`** with `delta IDENTICAL` and matching numstat
(`+308/−10`, of which 253 lines are new tests in `tests/kernels/attention/test_triton_unified_attention.py`). No swap
collision; sequencer clean; `:8000` 200 before and after.

**The heat-map's "mega-conflict at ~126" forecast did not apply to this sha** — row numbers are queue positions, not shas (skill
Verification 6), and the item that actually landed at that position touched only fork-clean Gemma4/Triton files. Recorded so
the forecast is not treated as a property of the position: **probe per item, and let the blob comparison — not the forecast —
decide whether to escalate.** The two genuine mega-conflict candidates (~126 and ~353 as forecast) are identified by their
model-file content, so they still have to be met when they arrive on their own shas.

Static leg only: both touched modules import cleanly on CPU and the new pruning helper `compute_tile_loop_bounds` is present in
`triton_attention_helpers`. **No behavioural leg is possible here** — the 253 new lines are GPU Triton kernel tests, and the
GPU is intentionally not exposed to my containers (see item 123's note for the `No CUDA GPUs are available` evidence), so
correctness of the tile-pruning itself is inherited from upstream CI plus byte-identity, not demonstrated on this box.

`tip 0edb36733 -> 9559cad0e | :8000=200,200 | swap-collision = 0 | import-only leg (GPU intentionally unavailable)`.

### 127. `3a2ed6cbae` -> `8c21563d3` — `[Kimi Bug] Fix gdn build_attn_metadata: 'KimiK3KDAMetadataBuilder' object has no attribute 'layer_names' (#54636)`

One file `vllm/v1/attention/backends/gdn_attn.py`, `+1/−2`, probed clean and landed **`blob EQ`** / `delta IDENTICAL`. No swap
collision; sequencer clean; `:8000` 200 before and after. Attribute-access bug in the Kimi K3 KDA metadata builder — reachable
only when serving that model family, so nil impact for the fork's Qwen serving path, and inert in the running container until
an image rebuild either way.

Verification tier here is byte-identity alone: no leg was attempted, because the trigger is an `AttributeError` raised inside a
GPU metadata-build path for a model the fork does not serve, and the GPU stays unexposed by policy (item 123's note). A
collection-level import check would not reach the defect, so it was skipped rather than performed for show.

`tip 9559cad0e -> 8c21563d3 | :8000=200,200 | swap-collision = 0`.
