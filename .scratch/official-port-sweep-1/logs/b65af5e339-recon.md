# Code Context — recon of b65af5e339 (target for `.scratch/official-port-sweep-1/logs/b65af5e339-recon.md`)

upstream: b65af5e3396e161a64db6352241acf3afbdcd958 "[CI][ROCm] Expand weight loading test coverage on AMD and cap its KV cache (#54037)" (author stefankoncarevic, 2026-09-01; task-supplied subject "[CI][ROCm] Add AMD coverage for weight loading in a dedicated job" not found in fetched history — see concerns)

pick: da87294a4 (jetson, `-x`, ahead=1 of d1dc60334)  conflicts: 0 []
- pick.sh: file sets identical (3); delta_vs_upstream IDENTICAL per file; patch-id EQUAL d418f43eb0f2ef591427528667ac5821565c67cf; collisions with 337d3f5dd: []

files:
- `.buildkite/test_areas/weight_loading.yaml` +3/-3  (MODIFIES an existing job's `mirror.amd` block — not a new yaml, not a new job: label `:amd: (MI300)`→`(MI355)`, `device: mi300_2`→`mi355_2`, `timeout_in_minutes: 35`→`40`)
- `tests/weight_loading/models-amd.txt` +14/-0  (14 added model configs: 3 gptq, 9 compressed-tensors, 1 awq, 1 fp8)
- `tests/weight_loading/test_weight_loading.py` +4/-0  (new import `from vllm.utils.mem_constants import GiB_bytes`; adds `kv_cache_memory_bytes=2 * GiB_bytes` to the `vllm_runner(...)` call)

blob: weight_loading.yaml=EQ  models-amd.txt=EQ  test_weight_loading.py=EQ (base had pre-commit state ⇒ not already present)

runtime_executed: no
- All 3 files are CI-only / test-data. Tree-wide grep for `test_weight_loading|models-amd|weight_loading` (excluding `tests/weight_loading/`) returns only: `.buildkite/test_areas/weight_loading.yaml`, `.buildkite/test-amd.yaml` (unreferenced legacy file), `.buildkite/scripts/hardware_ci/run-tpu-v1-test-part2.sh` (a *different* file, `tests/v1/tpu/test_spmd_model_weight_loading.py`), an unrelated comment in `tests/kernels/quantization/test_rocm_compressed_tensors_w4a16.py:20`, and a class docstring in `vllm/model_executor/parameter.py:206`. No `vllm/` module imports either test module; nothing imports `tests/*`.
- Direction of dependency is tests→vllm only. New symbol resolves at base: `vllm/utils/mem_constants.py:18 GiB_bytes = 1 << 30`; engine arg exists at base `vllm/config/cache.py:232`, `vllm/engine/arg_utils.py:542`, `vllm/entrypoints/llm.py` (5 hits). No missing-symbol risk.

lock_changes: NONE — zero lockfile/requirements churn in this commit. Repo has no lockfile at all (`git ls-files | grep -i lock` → only "block"-substring false positives; no `uv.lock`, no `constraints*.txt`). Task premise "bump torch 2.11 -> 2.13 in a lockfile" is not this commit.

torch_pins: fork requirements/cuda.txt=`7:torch==2.13.0` (`8:torchaudio==2.11.0`, `10:torchvision==0.28.0`, `11:torchcodec >= 0.14`)  changed_by_this=no  rocm=absent (no torch line in `requirements/rocm.txt`)  pyproject.toml=`10:"torch == 2.13.0"`
- `git diff d1dc60334 b65af5e339 -- requirements/cuda.txt requirements/rocm.txt pyproject.toml` → **empty**: fork pins are byte-identical to upstream at this commit, no independent fork torch pin.

ci_paths_referenced:
- `.buildkite/test_areas/`: exists
- `.buildkite/test_areas/weight_loading.yaml`: exists (pre-existing)
- `/vllm-workspace/tests` → `tests/`: exists
- `weight_loading/run_model_weight_loading_test.sh` → `tests/weight_loading/run_model_weight_loading_test.sh`: exists
- `weight_loading/models.txt` → `tests/weight_loading/models.txt`: exists
- `weight_loading/models-amd.txt` → `tests/weight_loading/models-amd.txt`: exists
- `depends_on: image-build` → key at `.buildkite/image_build/image_build.yaml:4`: exists
- `depends_on: image-build-amd` → key at `.buildkite/hardware_tests/amd.yaml:64`: exists
- `device: mi355_2`: no in-repo device registry to validate (device/agent_pool names live in the Buildkite org). `mi355_1` is used by 6 other `test_areas/*.yaml`; `mi355_2` previously appears only as `agent_pool:` in the unreferenced `.buildkite/test-amd.yaml`; post-pick `device: mi355_2` is unique to weight_loading.yaml
- `device: mi300_2` (removed value): also only in `test-amd.yaml` outside this file

lands_in_dir: `.buildkite/test_areas/`  fork_ci_runs_here: no
- `.buildkite/ci_config.yaml` (`name: vllm_ci`) lists `job_dirs: [.buildkite/image_build, .buildkite/test_areas, .buildkite/hardware_tests]`, so the file is in a live job dir *for upstream's Buildkite org*, which requires AMD MI355 agents the fork does not have.
- `.buildkite/ci_config_rocm.yaml` (`vllm_rocm_ci`) uses only `.buildkite/hardware_tests` — it never globs `test_areas`.
- The fork's own GitHub CI is only `.github/workflows/{docker-publish.yml,pr-title.yml}` (+ `matchers/`, `scripts/`); no workflow consumes `.buildkite/`. `.buildkite/test-amd.yaml` (which also runs `models-amd.txt` at lines 3069 and 3949) is referenced by nothing in the repo.

concerns:
1. Premise mismatch — the task's believed subject and the "torch 2.11 → 2.13 lockfile bump" content do not match this sha. Verified content of b65af5e339 = CI device/timeout swap + AMD test-model list + a KV-cache cap in the test. `git log --all --grep='dedicated job'`/`'Add AMD coverage'` → no matches in fetched history. Sweep list line 206 of `issues/03-pr-grind.md` and heat-map line 164 agree on this sha+subject, so the misattribution is in the brief, not the list. (Likely source of the "2.11" impression: `torchaudio==2.11.0` already in cuda.txt.)
2. The `.py` change is **not AMD-gated**: `kv_cache_memory_bytes=2 * GiB_bytes` applies to every runner of `test_weight_loading.py`, including the NVIDIA (L4, `tensor_parallel_size=2`) job that drives `models.txt` (19 configs incl. `casperhansen/mixtral-instruct-awq`, `awq_marlin` mixtral, `neuralmagic/Meta-Llama-3-8B-Instruct-FP8-KV`) and any local/manual run.
3. Zero runtime benefit for the wtdcode fork: no fork CI runs either job; the only in-repo consumer of `models-amd.txt` needs AMD MI355 hardware. Untestable on jetson-222 (needs 2 GPUs + HF model downloads).
4. env-impact: none — `requirements/`, `pyproject.toml`, `setup.py`, `cmake/` untouched ⇒ no image/wheel rebuild implied.
5. Added AMD rows omit the optional 4th `MIN_CAPABILITY` field, so `MIN_CAPABILITY` defaults to `"80"` and the gate is `current_platform.has_device_capability(80)` on ROCm (upstream presumably validated on MI355).
6. Heat-map recorded `env=no` / `HOT:` (no hot files) for this sha — consistent with what landed.

jetson_state: head=da87294a4 dirty=0 health=200 (commit left in place, unmerged=0, sequencer empty; Mac untouched)

## Start Here
If the parent wants more: `.buildkite/test_areas/weight_loading.yaml` (22 lines total) plus `tests/weight_loading/test_weight_loading.py` are the whole change surface; nothing in `vllm/` is involved.
