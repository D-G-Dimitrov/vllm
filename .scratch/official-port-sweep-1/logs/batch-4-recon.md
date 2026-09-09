# Code Context — batch-4 recon (A/B/C/D), picks run only in disposable worktrees ~/dev/rw{A,B,C,D} on jetson-222

All four task-supplied subjects matched `git log -1 --format=%s` except A, whose PR number differs.

---

ITEM A 8905633687 "[Bugfix][Frontend] Preserve token offset origins after left text pre-trimming (#54692)"
(subject text matches; the task brief omitted the PR number — no other discrepancy)
pick: clean (in disposable worktree ~/dev/rwA, commit 0e19b034e)
files: `tests/renderers/test_token_offsets.py` +58/-0   blob: EQ
       `vllm/renderers/base.py` +29/-0                 blob: EQ
       `vllm/renderers/params.py` +25/-0               blob: EQ
q1 runtime: YES. Both `vllm/` files execute in the API-server frontend process on every request that tokenizes a string prompt. The two new call sites sit inside `BaseRenderer.tokenize_prompt` / `tokenize_prompt_async` (`vllm/renderers/base.py:547,552` and `:587,592`), i.e. the hot path of every `/v1/completions` + `/v1/chat/completions` request. Guarded by an early `if char_offset == 0: return prompt` (`vllm/renderers/base.py:476-477`) so cost for all non-affected traffic is one attribute lookup + one int compare.
q2 fork-relevance: reachable, NOT platform-gated — no `is_cuda()`/`is_xpu()`/`is_rocm()`/capability guard anywhere on the changed path. Effective only when all three hold: `return_token_offsets=True` (request field, `vllm/entrypoints/openai/completion/protocol.py:182`, `chat_completion/protocol.py:429`, default None→False), `truncate_prompt_tokens is not None`, and `truncation_side == "left"`. Fork does not diverge in either changed file (`git diff --stat da87294a4 8905633687 -- vllm/renderers` → base.py +29, params.py +25 = the commit itself, nothing else). Fork DOES diverge in a nearby consumer: `vllm/entrypoints/scale_out/token_in_token_out/serving.py` has fork-local `self._preflight()` replacing the inline `engine_client.errored` check — not touched by this commit, no conflict.
q3 executability: YES, partially. `tests/renderers/test_token_offsets.py::TestTruncationKeepsOffsetsAligned::test_text_pretrim_preserves_source_offsets` and `::test_async_left_text_pretrim_preserves_source_offsets` use the in-file fake `_OffsetTokenizer` (tests/renderers/test_token_offsets.py:57-70) — no HF download, no GPU, pure Python + torch CPU. Selectable with `-k pretrim`. Caveat: the rest of that file uses the `fast_tokenizer` fixture = `AutoTokenizer.from_pretrained("openai-community/gpt2")` (line 22) and jetson-222 host has no `~/.cache/huggingface/hub`, so those need network and must be deselected. Also no torch in the host python (`/usr/bin/python3 -c 'import torch'` → ModuleNotFoundError), so it only runs inside the existing container.
q4 blast radius: two NEW private symbols, no existing signature changed. `_apply_prompt_char_offset` is a `BaseRenderer` staticmethod used only in base.py; `_get_text_truncation_offset` is a `TokenizeParams` method used only in base.py (verified: repo-wide grep returns defs + the 4 call sites only). No callers outside the changed files. No new config field, no new env var; `TokenizeParams` dataclass fields unchanged (`return_token_offsets` default False, `truncation_side` default None).
evidence:
- vllm/renderers/params.py:384-407 — new offset helper mirrors the existing pre-trim at params.py:376-379 (`text = text[-max_input_chars:]`), same formula `max_input_tokens * tokenizer.max_chars_per_token`; drift risk is two copies of one bound.
- vllm/utils/../renderers/base.py:481-489 — the `(0, 0)` special-token passthrough is what keeps fast-tokenizer special tokens at origin; `prompt_token_offsets` consumers are `vllm/entrypoints/scale_out/render/serving.py:157,228` and `vllm/inputs/engine.py:43` / `vllm/inputs/llm.py:118`.
- New tests fail pre-pick with off-by-36 offsets: `_OffsetTokenizer.max_chars_per_token=1` + `max_total_tokens=16` pre-trims `"0123456789"*4` to 16 chars, so the assertion expects `(36,37)…(39,40)` and base yields `(12,13)…(15,16)`.

---

ITEM B ce7391712b "[Bugfix][Security] Bound embedding densification before to_dense() (#54632)"
(subject matches exactly)
pick: clean (in disposable worktree ~/dev/rwB, commit 09ba7873d) — git reported "Auto-merging vllm/envs.py", zero conflicts
files: `docs/usage/security.md` +1/-0                      blob: EQ
       `tests/renderers/test_sparse_tensor_validation.py` +143/-1  blob: EQ
       `vllm/envs.py` +12/-0                               blob: **NE** (only NE in the batch)
       `vllm/multimodal/media/audio.py` +6/-3              blob: EQ
       `vllm/multimodal/media/image.py` +6/-3              blob: EQ
       `vllm/multimodal/media/video.py` +6/-3              blob: EQ
       `vllm/renderers/embed_utils.py` +5/-7               blob: EQ
       `vllm/utils/sparse_utils.py` +47/-1                 blob: EQ
q1 runtime: YES, and on the request path of any server that accepts embeds. `safe_to_dense()` replaces 6 bare `tensor.to_dense()` calls: `vllm/renderers/embed_utils.py:36` (`prompt_embeds`), `vllm/multimodal/media/image.py:141,162`, `audio.py:354,362`, `video.py:221,242`. `safe_load_prompt_embeds` is called from `vllm/renderers/base.py:377,396` and `vllm/entrypoints/chat_utils.py:1034,1228`. New env var read per call: `envs.VLLM_MAX_EMBED_DECODE_BYTES`.
q2 fork-relevance: reachable in THIS fork, NOT platform-gated. No `is_cuda/is_xpu/is_rocm`/capability guard on any changed line; the media IO classes are registered unconditionally in `vllm/multimodal/media/connector.py:614,625,639,650,664,675`. Fork divergence is confined to `vllm/envs.py` (post-pick HEAD vs upstream: +2/-327) — the fork carries ~327 upstream-absent env lines (VLLM_MHC_*, VLLM_INDEXER_*, VLLM_SPARSE_*, VLLM_PLE_*, VLLM_DSPARK_*, VLLM_MAX_SIZE_MB_CUSTOM_ALL_REDUCE …) plus the new var; the three hunks landed at unrelated line numbers (fork envs.py:85 / :1052-1053 / :2664 vs upstream :85 / :1022-1023 / :2339). That is why this file is NE — additive, not semantic. All other 7 files byte-identical to upstream.
q3 executability: YES for the discriminating unit class. `tests/renderers/test_sparse_tensor_validation.py::TestEmbeddingDecodeSizeLimit` (added at lines 409-541) is pure CPU torch: it builds `torch.sparse_coo_tensor([[0],[0]], [1.0], (1024,1024))`, monkeypatches `VLLM_MAX_EMBED_DECODE_BYTES=4096`, and asserts `VLLMValidationError`. Those tests do NOT use the `model_config` fixture, so no HF/network. Note the file's own comment (lines 411-418) explains they deliberately avoid the 4 TiB `BOMB_SHAPE` so a regressed guard cannot OOM the runner. Everything else in that file (`model_config` fixture, lines 30-42) constructs a real `ModelConfig(model="facebook/opt-125m")` and needs HF access. Host has no torch, so run inside the existing container.
q4 blast radius: NEW function `safe_to_dense(tensor: object, *, parameter: str)` — keyword-only `parameter`, all 10 call sites are inside the changed files (verified repo-wide). `safe_load_prompt_embeds` signature unchanged; it LOSES its inline `isinstance(tensor, torch.Tensor)` check, which moves into `safe_to_dense` — the 3 media IO paths gain that check for the first time (previously a non-tensor payload raised `AttributeError` → HTTP 500 instead of 4xx). NEW ENV VAR `VLLM_MAX_EMBED_DECODE_BYTES`, DEFAULT `2147483648` (2 GiB), `0` disables. No new pydantic/config field.
evidence:
- vllm/envs.py (fork post-pick):2664 — the new var is added to `compile_factors()`, whose only consumers are `vllm/compilation/backends.py:1031` and `vllm/compilation/caching.py:577`. Adding a key changes the compiled-artifact/env hash for every fork user, i.e. a one-time compile-cache invalidation on upgrade.
- vllm/utils/sparse_utils.py:38-73 — the guard is `tensor.numel() * tensor.element_size()` measured on the *declared* shape before `to_dense()`, so it also applies to plain dense payloads, not only sparse ones (default 2 GiB ⇒ a legitimate >2 GiB dense `prompt_embeds` upload now 4xx's where it previously densified).
- vllm/utils/mem_constants.py:12 `MiB_bytes = 1 << 20` — the new import resolves at fork base, no missing-symbol risk.

---

ITEM C 5414b4e694 "[XPU][TEST] Add entrypoints test in Intel GPU CI (#53980)"
(subject matches exactly)
pick: clean (in disposable worktree ~/dev/rwC, commit 992f39f5e)
files: `.buildkite/intel_jobs/entrypoints_intel.yaml` +185/-0 (new file)   blob: EQ
q1 runtime: NO. Single new Buildkite YAML, no `vllm/` or `tests/` code touched. Nothing in a running server executes it.
q2 fork-relevance: dead weight in this fork. Not platform-gated in code — it is an Intel-GPU CI job definition. It IS live in upstream's pipeline: `.buildkite/ci_config_intel.yaml:2-3` lists `job_dirs: [".buildkite/intel_jobs"]`, and that dir already holds 15 sibling `*_intel.yaml` files at fork base, so this file would be picked up by Intel's Buildkite org. The fork's own CI is `.github/workflows/{docker-publish.yml,pr-title.yml}` only; no workflow consumes `.buildkite/`. Requires Intel BMG agents (`device: intel_gpu`, `agent_tags.label: production`) which the fork does not have.
q3 executability: NO. Every one of the 7 jobs shells out to `bash .buildkite/scripts/hardware_ci/run-intel-test.sh`, which runs the test suite inside the Intel XPU docker container (script header, lines 1-6) and needs an `intel_gpu` device. The jobs run full offline/online entrypoint suites (`entrypoints/llm/test_generate.py`, `entrypoints/serve`, `entrypoints/scale_out`, `tool_use`, `openai/responses`, `openai/correctness`) against real served models — no GPU on this box, no model downloads. There is no test file that discriminates a YAML-only change.
q4 blast radius: no function signatures, no config fields, no env vars in the repo sense. Per-job `env:` block sets `REGISTRY`, `REPO`, `VLLM_TEST_DEVICE: "xpu"` — scoped to those Buildkite jobs only.
evidence:
- `.buildkite/intel_jobs/entrypoints_intel.yaml:2-3` `depends_on: [image-build-xpu]` — that key exists at `.buildkite/hardware_tests/intel_xpu_ci/test-intel.yaml:7`, so the DAG reference resolves.
- Every referenced path exists at fork base: `tests/entrypoints/unit_tests`, `tests/entrypoints/weight_transfer`, `tests/entrypoints/llm/test_generate.py`, `tests/entrypoints/llm/offline_mode`, `tests/entrypoints/openai/correctness/`, `.buildkite/scripts/hardware_ci/run-intel-test.sh` (all verified present).
- No Buildkite `key:` collision: `entrypoints-unit-tests-intel`, `entrypoints-integration-llm-intel`, `openai-api-correctness-intel` etc. appear in no other `.buildkite/**` file at fork base.
- Minor internal inconsistency worth noting: line ~81 runs `PYTHONPATH=/workspace/vllm pytest … entrypoints/serve/dev/rpc` while `.buildkite/scripts/hardware_ci/run-intel-test.sh:20` sets `export PYTHONPATH=".."`; the two spellings of the workspace path differ.

---

ITEM D 4707679cd2 "[Bugfix][MiniCPM-V] Route video_embeds to the shared vision parser (#54633)"
(subject matches exactly)
pick: clean (in disposable worktree ~/dev/rwD, commit 54cbf9439)
files: `tests/model_executor/test_minicpmv.py` +56/-0 (new)   blob: EQ
       `vllm/model_executor/models/minicpmv.py` +17/-1        blob: EQ
       `vllm/model_executor/models/minicpmv4_6.py` +2/-7      blob: EQ
q1 runtime: YES for MiniCPM-V/MiniCPMO serving only. Changes `MiniCPMVBaseModel._parse_and_validate_multimodal_inputs` (`vllm/model_executor/models/minicpmv.py:1294-1295`), called from `embed_multimodal` on every multimodal forward, and `MiniCPMV4_6ForConditionalGeneration.embed_multimodal` (`minicpmv4_6.py:1209`). No change for any non-MiniCPM model.
q2 fork-relevance: reachable — both models are registered at fork base: `vllm/model_executor/models/registry.py:503` `"MiniCPMV": ("minicpmv", "MiniCPMV")` and `:504-506` `"MiniCPMV4_6ForConditionalGeneration"`. NOT platform-gated — `grep is_xpu()/is_rocm()/is_cuda()/has_device_capability` in both changed model files returns only `minicpmv.py:1244 self.resampler.to(current_platform.device_type)`, unrelated. Fork does not diverge in the 3 changed files (all EQ). Neighbouring fork divergence in `registry.py` is Glm5Next entries only; in `models/` overall it is config.py, deepseek_mtp/v2, interfaces.py, qwen2_moe, qwen3_5_mtp, qwen3_dspark, qwen3_next — none MiniCPM.
q3 executability: YES. `tests/model_executor/test_minicpmv.py` is CPU-only and network-free: it builds instances with `object.__new__(MiniCPMV2_6)` / `object.__new__(MiniCPMV4_6ForConditionalGeneration)` (lines 12-22), stubs `_process_vision_input`, and asserts on `torch.arange(32).reshape(1,4,8)`. No ModelConfig, no checkpoint, no device. Only cost is importing `minicpmv4_6` → `qwen3_5`. Marker `skip_global_cleanup` is registered (`pyproject.toml:106`, honoured `tests/conftest.py:273`). `tests/model_executor/` already exists in the fork and is wired into `model_executor_intel.yaml:23` only (Intel CI), not GitHub CI.
q4 blast radius: NEW module-level dict `_VIDEO_TO_IMAGE_KWARGS` (minicpmv.py:472) and NEW helper `_image_kwargs_from_video` (minicpmv.py:480). Only external importer is `minicpmv4_6.py:62` — already in the changed set. No existing signature changes, no new config field or env var. Indirect blast radius via inheritance: `MiniCPMVBaseModel` subclasses `MiniCPMV2_0/2_5/2_6/4_0/4_5/MiniCPMV` (minicpmv.py:1405,1496,1588,1692,1791,1909) and `MiniCPMOBaseModel._parse_and_validate_multimodal_inputs` calls `super()` (`minicpmo.py:900-901`), with `MiniCPMO2_6/MiniCPMO4_5/MiniCPMO` mixing in `MiniCPMV2_6`/`MiniCPMV4_5` (minicpmo.py:935,947,970) — so MiniCPMO behaviour changes too, though no MiniCPMO test is added.
evidence:
- The semantic delta is ONLY in minicpmv.py: the old expression was `{k.removeprefix("video_"): v for k, v in kwargs.items()}` over ALL kwargs, so on a mixed image+video request `video_pixel_values`→`pixel_values` and the real `pixel_values` collide in one dict (last wins), and `tgt_sizes`/`image_embeds` leak into the video branch. The new allowlist `_VIDEO_TO_IMAGE_KWARGS` (minicpmv.py:472-485) drops that collision. `minicpmv4_6.py` old code already filtered `k.startswith("video_")`, so its change is a behaviour-preserving dedupe.
- Field set the allowlist must cover, at minicpmv.py:488-497 `_minicpmv_field_config`: exactly `video_pixel_values`, `video_image_sizes`, `video_tgt_sizes`, `video_embeds` — 1:1 with the 4 map entries, and `grep -rn 'removeprefix("video_")'` post-pick returns nothing, so no leftover un-prefixed pass-through.
- `_parse_and_validate_vision_input` (minicpmv.py:1247-1273) returns `MiniCPMVImageEmbeddingInputs` whenever `image_embeds` is set, ignoring `pixel_values` — the reason `video_embeds` alone previously fell through to `modalities["videos"] = None`-adjacent paths; guarded by the new `test_video_embeds_reach_the_vision_parser` and `test_image_and_video_embeds_stay_in_their_own_modality`.

---

worktrees_left: 2  vllm_head: da87294a4  dirty: 0  health: 200

## Start Here
For decision-making, the only items with any runtime exposure are A (`vllm/renderers/base.py:547,587`) and B (`vllm/utils/sparse_utils.py:38` + `vllm/envs.py` compile_factors at :2664). D is model-scoped to MiniCPM-V/MiniCPMO. C is CI-only and inert in this fork.

Note on `dirty`: `git status --porcelain` on jetson-222 reports one pre-existing untracked directory, `?? .cargo-home/`, which was present before this recon and was not created or removed by it. Tracked-file modifications = 0; no cherry-pick or index state left behind (no `.git/sequencer`).
