# Model strategy: official-native vs wtdcode Qwen3.8-Flash-Next & GLM-5.3-Flash

Type: research
Status: resolved
Blocked by: 02

## Question

The grind's two mega-conflicts are official's native model-support PRs colliding with wtdcode's own implementations: `[Model] Support Qwen3.8-Flash-Next` (e126687a9a, #53896 — grind item 126) and `[Model] add GLM-5.3-Flash support` (98ed0856f3, #53906 — item 353), 31 conflicted files each. User-verified facts: **Qwen3.8-Flash-Next works on official vLLM**; **GLM-5.3-Flash does NOT work on official vLLM but works on the wtdcode backport**.

Investigate the diffs between the official-native and wtdcode implementations of both models (static analysis, no runtime) and produce a per-model collision strategy for the grind: take-official (+ what to port from wtdcode), keep-wtdcode (skip official's), or hybrid — with the concrete wtdcode-only commits/files each option must carry.

## Answer

Resolved 2026-09-04 via static comparative analysis (full report: [model-compare.md](../model-compare.md); artifact also at /tmp/glm-qwen-compare.md).

**Both models: TAKE_OFFICIAL_PORT_FIXES.**

- **GLM-5.3-Flash** — official fails for concrete, fixable reasons (ranked): (1) no SM80 compute path for the kpool sparse indexer (wtdcode's `fp8_sm80.py` 177 LOC + `mqa_logits_triton.py` 673 LOC + uint8 fp8 stores are absent); (2) AutoRound W4A16 MTP draft quant resolution KeyError (fixed by user commit d1ba3782f9 `_mtp_checkpoint_prefix`); (3) kpool tail slot mapping OOB under cudagraph decode (wtdcode 1e6fd4f62e); (4) draft attn metadata built without positions (wtdcode 611e908e63); (5) missing JIT sparse warmup + int64 KV-offset fix. Port effort: ~7 commits, ~1,100–1,300 LOC. Official's tree is the superset (in-tree KDA kernels, ROCm AIter, FlashInfer SM90, mhc.py, kv_cache_interface).
- **Qwen3.8-Flash-Next** — official's model files are runtime-validated and byte-identical where they overlap; wtdcode adds the PLE **CPU offload** stack (ple_offload_layer.py, ple_offload connector/worker, VLLM_PLE_CPU_OFFLOAD wiring), PLE layer integration (~520-line ple_layer.py diff), PP>1 with PLE offload + MTP relay (4d1acaf058), bf16-MTP compressed-tensors draft loading (c1dda6409c), and FP8 PLE fixes (c92e9d6042). Port effort: ~10 commits, ~1,700–1,900 LOC — mandatory, or the Jetson PP/PLE profiles break.
- **Interaction**: both ports land on overlapping infra (`config/speculative.py`, `warmup/kernel_warmup.py`, `gpu_model_runner.py`/`gpu_worker.py`, `scheduler.py`, `kv_cache_interface.py`) — sequence them and re-evaluate wtdcode 3bec275739 against official's newer planner at item 126/353 time.
