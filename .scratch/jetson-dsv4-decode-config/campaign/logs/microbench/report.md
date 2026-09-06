----------------------------------------------------------------------
## 2026-08-29 19:18:20  run=microbench-20260829191820  node=jetson-233
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  dry_run=0
regime=no-model kernel microbench  (random tensors; coverage mode)
kernels=shipped from /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/../../../benchmarks/kernels → /tmp/campaign/microbench/kernels (read-only mount)
    run=coverage rc=1  2026-08-29 19:18:46
----------------------------------------------------------------------
## 2026-08-29 19:26:56  run=microbench-20260829192656  node=jetson-233
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  dry_run=0
regime=no-model kernel microbench  (random tensors; coverage mode)
kernels=shipped from /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/../../../benchmarks/kernels → /tmp/campaign/microbench/kernels (read-only mount)
    run=coverage rc=0  2026-08-29 19:27:19
----------------------------------------------------------------------
## 2026-08-29 19:28:00  run=microbench-20260829192800  node=jetson-233
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  dry_run=0
regime=no-model kernel microbench  (random tensors; default mode)
kernels=shipped from /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/../../../benchmarks/kernels → /tmp/campaign/microbench/kernels (read-only mount)
    run=dsv4-indexer-logits rc=0  2026-08-29 19:30:00
    run=dsv4-indexer-paged rc=0  2026-08-29 19:30:54
    run=dsv4-sparse-decode rc=0  2026-08-29 19:32:57
    run=dsv4-dense-gemv rc=1  2026-08-29 19:33:40
    run=dsv4-moe-experts rc=0  2026-08-29 19:34:40
    run=marlin rc=1  2026-08-29 19:35:19
    run=mla-k-concat rc=0  2026-08-29 19:36:36
    run=concat-mla-q rc=1  2026-08-29 19:36:59
----------------------------------------------------------------------
## 2026-08-29 19:42:19  run=microbench-20260829194219  node=jetson-233
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  dry_run=0
regime=no-model kernel microbench  (random tensors; default mode)
kernels=shipped from /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/../../../benchmarks/kernels → /tmp/campaign/microbench/kernels (read-only mount)
    run=concat-mla-q rc=1  2026-08-29 19:42:42
----------------------------------------------------------------------
## 2026-08-29 20:01:34  run=microbench-20260829200134  node=jetson-233
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  dry_run=0
regime=no-model kernel microbench  (random tensors; default mode)
kernels=shipped from /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/../../../benchmarks/kernels → /tmp/campaign/microbench/kernels (read-only mount)
    run=concat-mla-q rc=1  2026-08-29 20:01:50
----------------------------------------------------------------------
## 2026-08-29 20:26:55  run=microbench-20260829202655  node=jetson-233
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  dry_run=0
regime=no-model kernel microbench  (random tensors; coverage mode)
kernels=shipped from /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/../../../benchmarks/kernels → /tmp/campaign/microbench/kernels (read-only mount)
    run=coverage rc=0  2026-08-29 20:27:20
----------------------------------------------------------------------
## 2026-08-29 20:27:35  run=microbench-20260829202735  node=jetson-233
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  dry_run=0
regime=no-model kernel microbench  (random tensors; default mode)
kernels=shipped from /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/../../../benchmarks/kernels → /tmp/campaign/microbench/kernels (read-only mount)
    run=dsv4-indexer-logits rc=0  2026-08-29 20:29:34
    run=dsv4-indexer-paged rc=0  2026-08-29 20:30:29
    run=dsv4-sparse-decode rc=0  2026-08-29 20:32:32
    run=dsv4-dense-gemv rc=1  2026-08-29 20:33:11
    run=dsv4-moe-experts rc=0  2026-08-29 20:34:12
    run=marlin rc=1  2026-08-29 20:34:52
    run=mla-k-concat rc=0  2026-08-29 20:36:08
    run=concat-mla-q rc=1  2026-08-29 20:36:31
----------------------------------------------------------------------
## 2026-08-29 20:37:54  run=microbench-20260829203754  node=jetson-233
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  dry_run=0
regime=no-model kernel microbench  (random tensors; default mode)
kernels=shipped from /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/../../../benchmarks/kernels → /tmp/campaign/microbench/kernels (read-only mount)
    run=concat-mla-q rc=0  2026-08-29 20:39:51
----------------------------------------------------------------------
## 2026-08-29 20:42:52  run=microbench-20260829204252  node=jetson-233
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  dry_run=0
regime=no-model kernel microbench  (random tensors; default mode)
kernels=shipped from /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/../../../benchmarks/kernels → /tmp/campaign/microbench/kernels (read-only mount)
    run=dsv4-indexer-logits rc=0  2026-08-29 20:44:50
    run=dsv4-indexer-paged rc=0  2026-08-29 20:45:45
    run=dsv4-sparse-decode rc=0  2026-08-29 20:47:44
    run=dsv4-dense-gemv rc=1  2026-08-29 20:48:24
    run=dsv4-moe-experts rc=0  2026-08-29 20:49:24
    run=marlin rc=1  2026-08-29 20:50:05
    run=mla-k-concat rc=0  2026-08-29 20:51:21
    run=concat-mla-q rc=0  2026-08-29 20:52:14
