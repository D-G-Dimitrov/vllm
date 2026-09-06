# Jetson-222 dev environment setup

Type: task
Status: resolved

## Question

Prepare jetson-222 (`192.168.1.222`) as the per-PR work/test box for the sweep, and record a repeatable recipe that every grind session will copy:

1. Clone `https://github.com/D-G-Dimitrov/vllm.git` under `~/dev` on jetson-222; checkout `mitaka/backport` and verify it matches the pushed tip (`d1ba3782f9` at charting).
2. Verify the clone contains the cherry-pick source objects: official commits `c01b50e390..d4d703caf9` (fork `main` is synced with official main, so this should hold; add `https://github.com/vllm-project/vllm.git` as a remote only if objects are missing).
3. Verify PUSH access to `D-G-Dimitrov/vllm` from jetson-222 (SSH key or token). If push is not possible from jetson-222, record the fallback: push from the Mac after tests pass on jetson-222.
4. Test-runner sanity: establish how unit tests run there (venv? uv? docker?), run a small subset including at least one GPU-capable test, and record the exact commands as the recipe.
5. Check disk/CPU headroom; confirm the vision vLLM serving on :8001 is undisturbed.
6. **GPU isolation**: identify which GPU serves the :8001 vision vLLM; the test recipe MUST pin `CUDA_VISIBLE_DEVICES` away from that GPU for all grind test runs.

The Answer must contain the final working recipe (clone path, branch, test command(s), push path, CUDA_VISIBLE_DEVICES pin) — grind **workers** follow it verbatim. The recipe is written for a fresh worker with no prior context: every command must be copy-pasteable.

## Answer

Resolved 2026-09-04. All steps verified live on jetson-222.

- **SSH path**: alias `jetson-222` → `mitaka@192.168.1.222`, key `id_pi_ssh`, BatchMode works first try.
- **Clone**: `~/dev/vllm`, branch `mitaka/backport`, tip `d1ba3782f` verified (= `d1ba3782f9`).
- **Objects**: 5/5 present (c01b50e390, d4d703caf9, e126687a9a, 98ed0856f3, 3bec275739) — no extra remote needed.
- **Push**: NOT possible from jetson-222 (no HTTPS creds, no GitHub SSH key). **Refined push flow (orchestrator decision): worker cherry-picks + tests on jetson-222 → orchestrator, from the Mac, runs `git fetch jetson-222:dev/vllm mitaka/backport` (Mac's existing key authenticates; no creds needed on jetson) → `git merge --ff-only FETCH_HEAD` on local `mitaka/backport` → `git push origin mitaka/backport`.** Test-before-push preserved; GitHub history append-only.
- **Inventory**: 1× Orin GPU (index 0) — the vision vLLM serve runs on it, **listening on :8000 (not :8001 as charted)**; 274 GB disk free; 24 Gi RAM available; 12 cores; Python 3.12.3, no host venvs. Key docker image: `mitakad/vllm:0.29.0.dev0-r39.2.tegra-aarch64-cp312-cu132-24.04-commit.d4d703c` with prebuilt vLLM in `/opt/venv`.

### THE RECIPE (fresh worker tests one PR on jetson-222)

```bash
ssh jetson-222
cd ~/dev/vllm
git fetch origin && git checkout mitaka/backport
git reset --hard origin/mitaka/backport   # jetson local branch always mirrors pushed state before a new pick
# ... cherry-pick -x <official-sha>; if conflicts: record + git cherry-pick --abort + report ...

# CPU-only test run (CUDA_VISIBLE_DEVICES="" keeps the serving GPU untouched);
# working-tree Python code + prebuilt *.so extensions copied from the image:
docker run --rm --runtime nvidia --network host \
  -v ~/dev/vllm:/workspace -w /workspace \
  -e CUDA_VISIBLE_DEVICES="" \
  mitakad/vllm:0.29.0.dev0-r39.2.tegra-aarch64-cp312-cu132-24.04-commit.d4d703c bash -c '
set -e
source /opt/venv/bin/activate
cd /opt/venv/lib/python3.12/site-packages \
  && find vllm -maxdepth 3 \( -name "*.so" -o -name "*.so.*" \) -type f \
     -exec cp -a --parents {} /workspace/ \;
cd /workspace
pip install -q pytest tblib -i https://pypi.org/simple   # container devpi index has no pytest
pytest <PR-relevant test files> -x -q
'
# after tests pass: orchestrator fetches from jetson-222 and pushes (see Push above)
# if tests fail: on jetson-222 `git reset --hard origin/mitaka/backport` (discard pick), report
```

**Proof**: `tests/v1/core/test_scheduler.py -x -q -k block` → `4 passed, 149 deselected` (31.7s); `tests/test_config.py -x -q` → `115 passed, 1 failed` (the failure is an HF-hub download OSError inside the container — environment artifact, not code).

### Notes / caveats
- **Single GPU**: all test runs are CPU-only (`CUDA_VISIBLE_DEVICES=""`). No GPU test headroom without user OK + memory caps.
- **C++/CUDA caveat**: prebuilt extensions come from the d4d703caf image (133 commits behind tip). Python-level tests are meaningful; a cherry-pick touching C++/CUDA/CMake needs an image rebuild before its tests say anything.
- The vision vLLM serve was confirmed alive and undisturbed after every check (listens on :8000).
