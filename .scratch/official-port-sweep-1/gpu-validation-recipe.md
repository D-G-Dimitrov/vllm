# GPU validation recipe — Qwen3.8-Flash-Next + GLM-5.3-Flash swap

**Status: NOT YET DUE.** Prepared in advance so the hand-off is one paste. Do not run until the
orchestrator says the swap is resolution-complete and oracle-passed on CPU. Everything here is on
`jetson-222` (and the other 3 TP members); the orchestrator never runs the GPU.

## Standing facts (from the user, 2026-09-06)

- **TP only, across all 4 nodes. PP is never used and is not acceptable** — it costs more RAM than TP
  on this cluster, and PP is broken in both official and the backport. Any command or config that
  implies `pipeline_parallel_size > 1` is out of scope for validation.
- No Docker image has ever been built from `github.com/D-G-Dimitrov/vllm` (any branch/tag), and none is
  needed. Existing images are built from official vLLM and from wtdcode's backport.
- The code under test reaches the container by **bind mount**, never by rebuilding an image.

## Why no rebuild / no editable install

The image supplies only the runtime: torch, CUDA, python deps, and the 8 compiled extensions.
`PYTHONPATH=/work` puts the mounted source in front of site-packages, so the container executes our
branch's Python. Proven on 2026-09-06: the swap worktree's `kv_cache_utils.py`, `kv_cache_interface.py`,
`kv_cache_coordinator.py`, `mamba_utils.py` and `gpu/model_runner.py` all imported inside
`mitakad/vllm:0.29.0.dev0-r39.2.tegra-aarch64-cp312-cu132-24.04-commit.d4d703c`, and
`KpoolTailSpec`, `KpoolTailManager` and the restored `_get_kv_cache_groups_uniform_groups` were all live.

A rebuild is needed only if we touch C++/CUDA. This sweep does not.

## Node inventory (probed 2026-09-06, ssh from the Mac)

| host | internal ip | `~/dev` free | fork repo | `d4d703c` image | GPUs |
|---|---|---|---|---|---|
| jetson-222 | 192.168.1.222 | 260G | **yes** (origin of record) | yes `12bb167c429a` | 1 |
| jetson-234 | 10.10.10.1 | 76G | no | yes `12bb167c429a` | 1 |
| jetson-223 | 10.10.10.2 | 65G | no | yes `12bb167c429a` | 1 |
| jetson-232 | 10.10.10.3 | 141G | no | yes `12bb167c429a` | 1 |
| jetson-233 | 10.10.10.4 | 165G | no | yes `12bb167c429a` | 1 |
| jetson-221 | 192.168.1.221 | - | - | - | ssh **timed out** |

Each node has exactly **1 GPU**, so TP4 is genuinely multi-node (4x 10.10.10.x). The same
`d4d703c` image id is present on all of them, so the `.so` can come from the local image on any node.

**Pre-bundled for one-shot distribution** (built on jetson-222, no image needed on the target):
`jetson-222:~/dev/vllm-so-d4d703c.tgz` - 338M, 8 members, sha256 `3b2abe7ee71880fc...`.
`scp jetson-222:~/dev/vllm-so-d4d703c.tgz <node>:~/dev/ && tar xzf ~/dev/vllm-so-d4d703c.tgz -C <worktree>`

**Do NOT pre-seed the nodes yet** (user approved doing it, but it is premature): `swap/qwen-88` is still
at `e16d574bb` with every resolution uncommitted, so there is nothing to distribute. Clone + worktree +
`.so` on the 4 TP nodes is a ~5 minute task to run once the swap is committed and pushed.

## Step 0 — once per node (all 4), ~1 minute each

```bash
cd ~/dev/vllm                       # or any clone of the fork
git fetch origin mitaka/backport    # after the swap merges; before that: swap/qwen-88
git worktree add ~/dev/vllm-swap swap/qwen-88

# supply the compiled extensions the source tree does not carry (they are gitignored)
IMG=mitakad/vllm:0.29.0.dev0-r39.2.tegra-aarch64-cp312-cu132-24.04-commit.d4d703c
docker run --rm -e CUDA_VISIBLE_DEVICES="" -v ~/dev/vllm-swap:/work "$IMG" bash -lc '
  SP=/opt/venv/lib/python3.12/site-packages/vllm
  for f in $(cd $SP && find . -name "*.so"); do mkdir -p /work/vllm/$(dirname $f); cp $SP/$f /work/vllm/$f; done
  find /work/vllm -name "*.so" | wc -l'          # must print 8
```

The `.so` are untracked, so `git status` stays clean afterwards. **The `.so` must come from an image
whose native build matches the tree's expectations** — the `d4d703c` image has been the reference for
every CPU validation in this sweep, so keep using it unless there is a reason not to.

## Step 1 — the A/B that makes the result meaningful

Run the SAME image twice so the only variable is the Python layer:

- **baseline:** mount `~/dev/vllm` at the pre-swap tip (the last `mitaka/backport` commit before the swap)
- **candidate:** mount `~/dev/vllm-swap` (`swap/qwen-88`, or post-merge `mitaka/backport`)

Same mount recipe, same `.so`, same serve command, same prompts. Diff the outputs.

```bash
docker run --rm --runtime nvidia --network host -e CUDA_VISIBLE_DEVICES="" \
  -v ~/dev/vllm-swap:/work -w / -e PYTHONPATH=/work <IMAGE> \
  vllm serve <model> --tensor-parallel-size 4 --pipeline-parallel-size 1
```

Keep `-e CUDA_VISIBLE_DEVICES=""` for every non-serving container. Never run the swap while the
production `:8000` container needs the GPU; that endpoint is sacred.

## Step 2 — what to actually look at (TP-only focus)

Ranked by "breaks silently rather than crashing":

1. **GLM kpool-tail prefix caching.** `kv_cache_interface.py` now keeps BOTH `participates_in_prefix_caching`
   and the `prefix_cacheable` alias. If that alias were lost, kpool-tail and DSV4 compressor-ring scratch
   groups would default back to *cacheable* and a connector could serve per-request scratch as shared prefix
   KV — **wrong answers, no error.** Check: identical greedy outputs across repeat runs, and no cross-request
   output contamination with prefix caching on.
2. **`slot_mapping_enabled` in `gpu/model_runner.py`.** Our resolution excludes BOTH `CircularBufferSpec` and
   `KpoolTailSpec`. If `KpoolTailSpec` were missing, GLM-5.3-Flash reads far beyond its 1-block table row
   (`pos 130559 // 4 = 32639` vs stride 32) → CUDA illegal memory access. This is TP-reachable.
3. **KV cache group / block sizing.** `kv_cache_utils.py` now runs our DSV4/GLM5/CSA-linear group builders
   first and official's new `_get_packed_kv_cache_groups` after. Compare the printed `KV cache config`
   (group count, block sizes, tensor layouts) between baseline and candidate — it should be identical for
   both production models.
4. **`tp_replicated` in Mamba KV uniformity** (new from official in `kv_cache_interface.py`) and
   `has_mamba_layers` now using `iter_layer_specs`, which can return True where ours returned False for a
   mixed uniform group. TP-relevant by definition; watch for a changed mamba group count.
5. **PLE offload lifecycle and MTP / spec-decode drafts** in TP mode. 15 `ple_offload` references verified
   still present in `model_runner.py`; confirm the offload path is actually exercised, not silently skipped.

## Explicitly OUT of scope for validation

Everything PP: `pp_handler.broadcast` ordering vs `propose` (we kept ours' post-`propose` placement and
verified it, but it will never run here), and official's new fail-fast for Qwen4Exp N-gram PLE at
`pipeline_parallel_size > 1` in `model_executor/models/config.py`. Both kept for upstream faithfulness only.

## Residual risks this recipe does NOT cover

- `nixl/base_worker.py` `_layer_specs` silently changed from group-level wrappers to leaf specs (landmine L3).
  Only exercised by the NIXL connector path; needs its own suite or a PD-disaggregated run.
- `block_stride` (D2: we keep ours' generic stride rule). Upstream adopts ours' formula later at item 315,
  so the final joint-swap resolution is the one to validate, not this interim one.

## Added to the GPU watch list from the grind lane

- **item 95 (`eef9f770c`, #50005)**: in `deepseek_v32` `_fused_norm_rope_kernel`, the Q RMS norm (`pid == 2`)
  now runs **ahead of** the negative-`slot_mapping` early return, so padding rows are normalised and stored
  instead of returning early. Writes are masked, row-local and in-bounds, and reachability is confined to
  `deepseek_v32` - but it is **not dcp-gated**, and **every one of its 67 tests skips on CPU** behind a
  CUDA fp8/SM89+ guard, so it has zero CPU coverage. DeepSeek-V3.2 is not a protected family, so this is a
  "notice while you are already running the GPU" item, not a blocker.
