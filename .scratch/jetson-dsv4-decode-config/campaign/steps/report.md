----------------------------------------------------------------------
## 2026-08-28 07:54:41  step=00-preflight  profile=(current serving — snapshot)  pre-campaign snapshot + dataset build
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MAXN
    --- 2026-08-28 07:54:43 pre-campaign snapshot ---
    image_pinned=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5
    --- node jetson-233 (10.10.10.4, head) ---
    containers: 
    nvpmodel : NV Power Mode: MAXN
    --- node jetson-234 (10.10.10.1, 1) ---
    containers: 
    nvpmodel : NV Power Mode: MAXN
    --- node jetson-223 (10.10.10.2, 2) ---
    containers: 
    nvpmodel : NV Power Mode: MAXN
    --- node jetson-232 (10.10.10.3, 3) ---
    containers: 
    nvpmodel : NV Power Mode: MAXN
    NOTE: no live container at preflight time — Task 4/5 will fall back to 01-baseline facts
    data: sharegpt=   10787B  long131k=  555206B
----------------------------------------------------------------------
## 2026-08-28 08:25:12  step=00-preflight  profile=(current serving — snapshot)  pre-campaign snapshot + dataset build
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MAXN
    --- 2026-08-28 08:25:15 pre-campaign snapshot ---
    image_pinned=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5
    --- node jetson-233 (10.10.10.4, head) ---
    containers: 
    nvpmodel : NV Power Mode: MAXN
    --- node jetson-234 (10.10.10.1, 1) ---
    containers: 
    nvpmodel : NV Power Mode: MAXN
    --- node jetson-223 (10.10.10.2, 2) ---
    containers: 
    nvpmodel : NV Power Mode: MAXN
    --- node jetson-232 (10.10.10.3, 3) ---
    containers: 
    nvpmodel : NV Power Mode: MAXN
    NOTE: no live container at preflight time — Task 4/5 will fall back to 01-baseline facts
    data: sharegpt=   10787B  long131k=  555206B
    IDENTITY_SAMPLE_ERROR: <urlopen error [Errno 111] Connection refused>
    NOTE: identity-baseline-bf16.json capture failed — deferred to a step with a live server
    verdict=ok
----------------------------------------------------------------------
## 2026-08-28 08:42:29  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MAXN
----------------------------------------------------------------------
## 2026-08-28 08:58:04  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MAXN
----------------------------------------------------------------------
## 2026-08-28 09:01:53  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MAXN
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=
    --- last 40 lines: logs/01-baseline/head.log ---
        -e \
        MKL_NUM_THREADS=4 \
        -e \
        RAY_CGRAPH_get_timeout=600 \
        -e \
        RAY_CGRAPH_submit_timeout=600 \
        -e \
        RAY_DEDUP_LOGS=0 \
        -e \
        RAY_DISABLE_IMPORT_WARNING=1 \
        -e \
        VLLM_USE_FLASHINFER_SAMPLER=1 \
        -e \
        VLLM_MARLIN_USE_ATOMIC_ADD=1 \
        -e \
        VLLM_FLOAT32_MATMUL_PRECISION=high \
        --ulimit \
        memlock=-1 \
        --ulimit \
        stack=67108864 \
        "vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5" \
        -c ""
    
    ==========================================
    DEBUG: Ray Start Command
    ==========================================
    ray start \
        -e \
        RAY_NODE_IP_ADDRESS=10.10.10.4 \
        -e \
        RAY_OVERRIDE_NODE_IP_ADDRESS=10.10.10.4 \
        -v \
        --block \
        --num-gpus 1 \
        --head \
        --port=6379 \
        --node-ip-address 10.10.10.4 \
    cannot attach stdin to a TTY-enabled container because stdin is not a terminal
    Error response from daemon: No such container: jetson-cluster-node-20260828090158
    Error response from daemon: No such container: jetson-cluster-node-20260828090158
    --- last 40 lines: logs/01-baseline/worker-10.10.10.1.log ---
        OMP_NUM_THREADS=4 \
        -e \
        MKL_NUM_THREADS=4 \
        -e \
        RAY_CGRAPH_get_timeout=600 \
        -e \
        RAY_CGRAPH_submit_timeout=600 \
        -e \
        RAY_DEDUP_LOGS=0 \
        -e \
        RAY_DISABLE_IMPORT_WARNING=1 \
        -e \
        VLLM_USE_FLASHINFER_SAMPLER=1 \
        -e \
        VLLM_MARLIN_USE_ATOMIC_ADD=1 \
        -e \
        VLLM_FLOAT32_MATMUL_PRECISION=high \
        --ulimit \
        memlock=-1 \
        --ulimit \
        stack=67108864 \
        "vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5" \
        -c ""
    
    ==========================================
    DEBUG: Ray Start Command
    ==========================================
    ray start \
        -e \
        RAY_NODE_IP_ADDRESS=10.10.10.1 \
        -e \
        RAY_OVERRIDE_NODE_IP_ADDRESS=10.10.10.1 \
        -v \
        --block \
        --num-gpus 1 \
        --address 10.10.10.4:6379 \
        --node-ip-address 10.10.10.1 \
    cannot attach stdin to a TTY-enabled container because stdin is not a terminal
    Error response from daemon: No such container: jetson-cluster-node-20260828090211
    Error response from daemon: No such container: jetson-cluster-node-20260828090211
    --- last 40 lines: logs/01-baseline/worker-10.10.10.2.log ---
        OMP_NUM_THREADS=4 \
        -e \
        MKL_NUM_THREADS=4 \
        -e \
        RAY_CGRAPH_get_timeout=600 \
        -e \
        RAY_CGRAPH_submit_timeout=600 \
        -e \
        RAY_DEDUP_LOGS=0 \
        -e \
        RAY_DISABLE_IMPORT_WARNING=1 \
        -e \
        VLLM_USE_FLASHINFER_SAMPLER=1 \
        -e \
        VLLM_MARLIN_USE_ATOMIC_ADD=1 \
        -e \
        VLLM_FLOAT32_MATMUL_PRECISION=high \
        --ulimit \
        memlock=-1 \
        --ulimit \
        stack=67108864 \
        "vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5" \
        -c ""
    
    ==========================================
    DEBUG: Ray Start Command
    ==========================================
    ray start \
        -e \
        RAY_NODE_IP_ADDRESS=10.10.10.2 \
        -e \
        RAY_OVERRIDE_NODE_IP_ADDRESS=10.10.10.2 \
        -v \
        --block \
        --num-gpus 1 \
        --address 10.10.10.4:6379 \
        --node-ip-address 10.10.10.2 \
    cannot attach stdin to a TTY-enabled container because stdin is not a terminal
    Error response from daemon: No such container: jetson-cluster-node-20260828090211
    Error response from daemon: No such container: jetson-cluster-node-20260828090211
    --- last 40 lines: logs/01-baseline/worker-10.10.10.3.log ---
        OMP_NUM_THREADS=4 \
        -e \
        MKL_NUM_THREADS=4 \
        -e \
        RAY_CGRAPH_get_timeout=600 \
        -e \
        RAY_CGRAPH_submit_timeout=600 \
        -e \
        RAY_DEDUP_LOGS=0 \
        -e \
        RAY_DISABLE_IMPORT_WARNING=1 \
        -e \
        VLLM_USE_FLASHINFER_SAMPLER=1 \
        -e \
        VLLM_MARLIN_USE_ATOMIC_ADD=1 \
        -e \
        VLLM_FLOAT32_MATMUL_PRECISION=high \
        --ulimit \
        memlock=-1 \
        --ulimit \
        stack=67108864 \
        "vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5" \
        -c ""
    
    ==========================================
    DEBUG: Ray Start Command
    ==========================================
    ray start \
        -e \
        RAY_NODE_IP_ADDRESS=10.10.10.3 \
        -e \
        RAY_OVERRIDE_NODE_IP_ADDRESS=10.10.10.3 \
        -v \
        --block \
        --num-gpus 1 \
        --address 10.10.10.4:6379 \
        --node-ip-address 10.10.10.3 \
    cannot attach stdin to a TTY-enabled container because stdin is not a terminal
    Error response from daemon: No such container: jetson-cluster-node-20260828090212
    Error response from daemon: No such container: jetson-cluster-node-20260828090212
    verdict=startup-failed
----------------------------------------------------------------------
## 2026-08-28 09:10:30  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MAXN
----------------------------------------------------------------------
## 2026-08-28 09:13:43  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MAXN
----------------------------------------------------------------------
## 2026-08-28 09:17:53  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=
    ready_seconds=90
    ------- startup facts -------
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=
    verdict=baseline-pinned
----------------------------------------------------------------------
## 2026-08-28 09:18:32  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MAXN
----------------------------------------------------------------------
## 2026-08-28 10:05:24  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=
    ready_seconds=90
    ------- startup facts -------
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=
    verdict=baseline-pinned
----------------------------------------------------------------------
## 2026-08-28 10:55:56  step=00b-container-only  profile=container-only (no vLLM)  Option 2 — launch containers only, no vLLM serve
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MODE_50W
----------------------------------------------------------------------
## 2026-08-28 10:56:23  step=00b-container-only  profile=container-only (no vLLM)  Option 2 — launch containers only, no vLLM serve
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    container_jetson-233=NONE
    container_jetson-234=NONE
    container_jetson-223=NONE
    container_jetson-232=NONE
    verdict=containers-up-0of4
    verdict=CONTAINERS NOT ALL UP: 0/4 — capture node logs, diagnose
----------------------------------------------------------------------
## 2026-08-28 11:09:35  step=00b-container-only  profile=container-only (no vLLM)  Option 2 — launch containers only, no vLLM serve
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MODE_50W
----------------------------------------------------------------------
## 2026-08-28 11:10:03  step=00b-container-only  profile=container-only (no vLLM)  Option 2 — launch containers only, no vLLM serve
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MODE_50W
----------------------------------------------------------------------
## 2026-08-28 14:24:12  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=
    ready_seconds=90
    ------- startup facts -------
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=
    verdict=baseline-pinned
----------------------------------------------------------------------
## 2026-08-28 14:24:28  step=02-fp16  profile=ds4-x4-fp16  Task 3 — fp16 circuit-dtype A/B (sm_87 half-rate bf16 hypothesis)
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    dtype_check=NOT-CONFIRMED — verify manually
    -> tokens DIVERGE: record, do NOT auto-adopt (human call on accuracy)
    verdict=fp16-arm-measured
----------------------------------------------------------------------
## 2026-08-28 14:25:03  step=06-adopt  profile=ds4-x4-fp16-kv96  Task 6 — combined-winner verification (dtype x KV x schedule)
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    verdict=adopt-measured
----------------------------------------------------------------------
## 2026-08-28 15:15:24  step=01-baseline  profile=ds4-x4  test
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
regime=32768 context  num_seqs=4  (QUICK override active when != 262k)
power_head=NV Power Mode: MODE_50W
    SMOKE: SKIPPED (QUICK context=32768 — 131k prompt does not fit)
----------------------------------------------------------------------
## 2026-08-28 17:11:47  step=00b-container-only  profile=container-only (no vLLM)  Option 2 — launch containers only, no vLLM serve
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
----------------------------------------------------------------------
## 2026-08-28 17:11:51  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
----------------------------------------------------------------------
## 2026-08-28 17:12:06  step=02-fp16  profile=ds4-x4-fp16  Task 3 — fp16 circuit-dtype A/B (sm_87 half-rate bf16 hypothesis)
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
----------------------------------------------------------------------
## 2026-08-28 17:12:22  step=03-kv96  profile=ds4-x4-kv96  Task 4 — KV cache 9.5833g A/B (known-good ceiling)
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=
----------------------------------------------------------------------
## 2026-08-28 17:12:37  step=04-btmp  profile=ds4-x4-btmp  Task 5 — batched-token GUARD test (DO-NOT-SET warning)
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    baseline_kv=0  baseline_concurrency=0
----------------------------------------------------------------------
## 2026-08-28 17:12:52  step=05-restore  profile=ds4-x4  restore pre-campaign serving
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
----------------------------------------------------------------------
## 2026-08-28 17:13:07  step=00-preflight  profile=(current serving — snapshot)  pre-campaign snapshot + dataset build
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    --- 2026-08-28 17:13:09 pre-campaign snapshot ---
    image_pinned=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5
    --- node jetson-233 (10.10.10.4, head) ---
    containers: 
    nvpmodel : 
    --- node jetson-234 (10.10.10.1, 1) ---
    containers: 
    nvpmodel : 
    --- node jetson-223 (10.10.10.2, 2) ---
    containers: 
    nvpmodel : 
    --- node jetson-232 (10.10.10.3, 3) ---
    containers: 
    nvpmodel : 
    data: sharegpt=   10787B  long131k=  555206B
    verdict=ok
----------------------------------------------------------------------
## 2026-08-28 21:22:50  step=00-preflight  profile=(current serving — snapshot)  pre-campaign snapshot + dataset build
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=NV Power Mode: MODE_50W
    --- 2026-08-28 21:22:51 pre-campaign snapshot ---
    image_pinned=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5
    --- node jetson-233 (10.10.10.4, head) ---
    containers: 
    nvpmodel : NV Power Mode: MODE_50W
    --- node jetson-234 (10.10.10.1, 1) ---
    containers: 
    nvpmodel : NV Power Mode: MODE_50W
    --- node jetson-223 (10.10.10.2, 2) ---
    containers: 
    nvpmodel : NV Power Mode: MODE_50W
    --- node jetson-232 (10.10.10.3, 3) ---
    containers: 
    nvpmodel : NV Power Mode: MODE_50W
    NOTE: no live container at preflight time — Task 4/5 will fall back to 01-baseline facts
    data: sharegpt=   10787B  long131k=  555206B
    IDENTITY_SAMPLE_ERROR: <urlopen error [Errno 111] Connection refused>
    NOTE: identity-baseline-bf16.json capture failed — deferred to a step with a live server
    verdict=ok
----------------------------------------------------------------------
## 2026-08-28 21:24:21  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=NV Power Mode: MODE_50W
----------------------------------------------------------------------
## 2026-08-28 21:24:38  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=NV Power Mode: MODE_50W
----------------------------------------------------------------------
## 2026-08-28 22:21:54  step=02-fp16  profile=ds4-x4-fp16  Task 3 — fp16 circuit-dtype A/B (sm_87 half-rate bf16 hypothesis)
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=NV Power Mode: MODE_50W
----------------------------------------------------------------------
## 2026-08-28 22:33:14  step=05-restore  profile=ds4-x4  restore pre-campaign serving
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=NV Power Mode: MODE_50W
----------------------------------------------------------------------
## 2026-08-28 22:21:54  step=02-fp16  profile=ds4-x4-fp16  Task 3 — fp16 circuit-dtype A/B
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=NV Power Mode: MODE_50W
    dtype_check=float16-launched (args show dtype: float16; EngineCore dtype=torch.float16)
    STARTUP FAILED — the failure itself is the fp16-arm result (recorded, no bench ran)
    error: RuntimeError: Engine core initialization failed.
           WorkerProc exception in determine_available_memory() -> model_runner.profile_run()
           (multiproc_executor.py:1044, gpu_worker.py:477)
    root cause: fp16 weights (unquantized compute path) + fp8_ds_mla KV cache (8.17g)
           exceed sm_87 GPU memory at 50W during memory profiling.
           The bf16 arm boots because deepseek_v4_fp8 quant keeps weights fp8/fp4.
    verdict=STARTUP-FAILED — fp16 ARM REFUTED (cannot boot on this hardware/budget)
    NOTE: 3x worker containers (234/223/232) left up after head death; cleaned before restore.
----------------------------------------------------------------------
## 2026-08-29 09:38:55  step=03-kv96  profile=ds4-x4-kv96  Task 4 — KV cache 9.5833g A/B (known-good ceiling)
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    kv_delta_target=923492  this_kv=0  this_conc=0
    verdict=kv96-measured
----------------------------------------------------------------------
## 2026-08-29 10:43:41  step=07-opt  profile=ds4-x4-opt  promotion serve A/B — microbench winner on ds4-x4-opt
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=
    containers= |  |  |  | 
    ready_seconds=90
    ------- startup facts -------
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    baseline_kv=  this_kv=0  baseline_conc=  this_conc=0
    NOTE: KV/conc differ from baseline — lever not memory-neutral
    IDENTITY opt-bf16: SKIPPED (missing /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/steps/logs/01-baseline/identity-baseline-bf16.json or /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/steps/logs/07-opt/identity-opt-bf16.json)
    verdict=opt-measured
----------------------------------------------------------------------
## 2026-08-29 15:45:31  step=07-opt  profile=ds4-x4-opt  promotion serve A/B — microbench winner on ds4-x4-opt
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=
    containers= |  |  |  | 
    ready_seconds=90
    ------- startup facts -------
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    baseline_kv=  this_kv=0  baseline_conc=  this_conc=0
    NOTE: KV/conc differ from baseline — lever not memory-neutral
    IDENTITY opt-bf16: SKIPPED (missing /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/steps/logs/01-baseline/identity-baseline-bf16.json or /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/steps/logs/07-opt/identity-opt-bf16.json)
    verdict=identity-unproven
----------------------------------------------------------------------
## 2026-08-29 15:48:07  step=07-opt  profile=ds4-x4-opt  promotion serve A/B — microbench winner on ds4-x4-opt
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=
    containers= |  |  |  | 
    ready_seconds=90
    ------- startup facts -------
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    NOTE: baseline facts empty — memory-neutrality unverifiable
    IDENTITY opt-bf16: SKIPPED (missing /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/steps/logs/01-baseline/identity-baseline-bf16.json or /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/steps/logs/07-opt/identity-opt-bf16.json)
    verdict=identity-unproven
----------------------------------------------------------------------
## 2026-08-29 15:50:47  step=07-opt  profile=ds4-x4-opt  promotion serve A/B — microbench winner on ds4-x4-opt
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=
    containers= |  |  |  | 
    ready_seconds=90
    ------- startup facts -------
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    NOTE: baseline facts empty — memory-neutrality unverifiable
    verdict=opt-measured
----------------------------------------------------------------------
## 2026-08-29 15:51:02  step=03-kv96  profile=ds4-x4-kv96  Task 4 — KV cache 9.5833g A/B (known-good ceiling)
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    kv_delta_target=923492  this_kv=0  this_conc=0
    verdict=kv96-measured
----------------------------------------------------------------------
## 2026-08-29 16:08:20  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    containers= |  |  |  | 
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    ready_seconds=90
    verdict=baseline-pinned
----------------------------------------------------------------------
## 2026-08-29 16:08:35  step=02-fp16  profile=ds4-x4-fp16  Task 3 — fp16 circuit-dtype A/B (sm_87 half-rate bf16 hypothesis)
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    ready_seconds=90
    dtype_check=NOT-CONFIRMED — verify manually
    -> identity UNVERIFIED (missing/unparseable ref or arm) — no comparison recorded
    verdict=fp16-arm-measured
----------------------------------------------------------------------
## 2026-08-29 16:08:51  step=03-kv96  profile=ds4-x4-kv96  Task 4 — KV cache 9.5833g A/B (known-good ceiling)
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    ready_seconds=90
    kv_delta_target=923492  this_kv=0  this_conc=0
    verdict=kv96-measured
----------------------------------------------------------------------
## 2026-08-29 16:09:06  step=05-restore  profile=ds4-x4  restore pre-campaign serving
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    ready_seconds=90
    verdict=restored
----------------------------------------------------------------------
## 2026-08-29 16:09:21  step=04-btmp  profile=ds4-x4-btmp  Task 5 — batched-token GUARD test (DO-NOT-SET warning)
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    baseline_kv=787,108  baseline_concurrency=3.00
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    this: kv=0  concurrency=0  max_num_scheduled_tokens=0
    recorded_verdict=rejected (startup failed) — DO-NOT-SET warning verified by failure
    verdict=btmp-guard-verdict
----------------------------------------------------------------------
## 2026-08-29 16:09:36  step=07-opt  profile=ds4-x4-opt  promotion serve A/B — microbench winner on ds4-x4-opt
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    ready_seconds=90
    baseline_kv=787,108  this_kv=0  baseline_conc=3.00  this_conc=0
    NOTE: KV/conc differ from baseline — lever not memory-neutral
    verdict=opt-measured
----------------------------------------------------------------------
## 2026-08-29 16:10:15  step=06-adopt  profile=ds4-x4-fp16-kv96  Task 6 — combined-winner verification (dtype x KV x schedule)
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    ready_seconds=90
    verdict=adopt-measured
----------------------------------------------------------------------
## 2026-08-29 16:10:30  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
regime=262k context  num_seqs=profile  (QUICK override active when != 262k)
power_head=
    containers= |  |  |  | 
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    ready_seconds=90
    verdict=baseline-pinned
----------------------------------------------------------------------
## 2026-08-29 16:16:42  step=00-preflight  profile=(current serving — snapshot)  pre-campaign snapshot + dataset build
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    --- 2026-08-29 16:16:43 pre-campaign snapshot ---
    image_pinned=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5
    --- node jetson-233 (10.10.10.4, head) ---
    containers: 
    nvpmodel : 
    --- node jetson-234 (10.10.10.1, 1) ---
    containers: 
    nvpmodel : 
    --- node jetson-223 (10.10.10.2, 2) ---
    containers: 
    nvpmodel : 
    --- node jetson-232 (10.10.10.3, 3) ---
    containers: 
    nvpmodel : 
    data: sharegpt=   10787B  long131k=  555206B
    verdict=ok
----------------------------------------------------------------------
## 2026-08-29 16:16:44  step=00b-container-only  profile=container-only (no vLLM)  Option 2 — launch containers only, no vLLM serve
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    container_jetson-233=NONE
    container_jetson-234=NONE
    container_jetson-223=NONE
    container_jetson-232=NONE
    verdict=containers-up-0of4
    verdict=CONTAINERS NOT ALL UP: 0/4 — capture node logs, diagnose
----------------------------------------------------------------------
## 2026-08-29 16:16:48  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    containers= |  |  |  | 
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    ready_seconds=90
    verdict=baseline-pinned
----------------------------------------------------------------------
## 2026-08-29 16:17:03  step=02-fp16  profile=ds4-x4-fp16  Task 3 — fp16 circuit-dtype A/B (sm_87 half-rate bf16 hypothesis)
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    ready_seconds=90
    dtype_check=NOT-CONFIRMED — verify manually
    -> identity UNVERIFIED (missing/unparseable ref or arm) — no comparison recorded
    verdict=fp16-arm-measured
----------------------------------------------------------------------
## 2026-08-29 16:17:18  step=03-kv96  profile=ds4-x4-kv96  Task 4 — KV cache 9.5833g A/B (known-good ceiling)
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    ready_seconds=90
    kv_delta_target=923492  this_kv=0  this_conc=0
    verdict=kv96-measured
----------------------------------------------------------------------
## 2026-08-29 16:17:33  step=04-btmp  profile=ds4-x4-btmp  Task 5 — batched-token GUARD test (DO-NOT-SET warning)
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    baseline_kv=787,108  baseline_concurrency=3.00
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    this: kv=0  concurrency=0  max_num_scheduled_tokens=0
    recorded_verdict=rejected (startup failed) — DO-NOT-SET warning verified by failure
    verdict=btmp-guard-verdict
----------------------------------------------------------------------
## 2026-08-29 16:17:48  step=05-restore  profile=ds4-x4  restore pre-campaign serving
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    ready_seconds=90
    verdict=restored
----------------------------------------------------------------------
## 2026-08-29 16:18:03  step=06-adopt  profile=x  Task 6 — combined-winner verification (dtype x KV x schedule)
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    ready_seconds=90
    verdict=adopt-measured
----------------------------------------------------------------------
## 2026-08-29 16:18:19  step=07-opt  profile=ds4-x4-opt  promotion serve A/B — microbench winner on ds4-x4-opt
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    ready_seconds=90
    baseline_kv=787,108  this_kv=0  baseline_conc=3.00  this_conc=0
    NOTE: KV/conc differ from baseline — lever not memory-neutral
    verdict=opt-measured
----------------------------------------------------------------------
## 2026-08-29 16:35:04  step=07-opt  profile=ds4-x4-opt  promotion serve A/B — microbench winner on ds4-x4-opt
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    ready_seconds=90
    baseline_kv=787,108  this_kv=0  baseline_conc=3.00  this_conc=0
    NOTE: KV/conc differ from baseline — lever not memory-neutral
    verdict=opt-measured
----------------------------------------------------------------------
## 2026-08-29 17:22:19  step=07-opt  profile=ds4-x4-opt  promotion serve A/B — microbench winner on ds4-x4-opt
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    ready_seconds=90
    baseline_kv=787,108  this_kv=0  baseline_conc=3.00  this_conc=0
    NOTE: KV/conc differ from baseline — lever not memory-neutral
    verdict=opt-measured
----------------------------------------------------------------------
## 2026-08-30 12:46:53  step=07-opt  profile=ds4-x4-opt  promotion serve A/B — microbench winner on ds4-x4-opt
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    containers= |  |  |  | 
    model_dtype=
    marlin_line=
    scheduled=
    kv_tokens_line=
    concurrency_line=
    error_lines=LOG_MISSING
    ready_seconds=90
    baseline_kv=787,108  this_kv=0  baseline_conc=3.00  this_conc=0
    NOTE: KV/conc differ from baseline — lever not memory-neutral
    verdict=opt-measured
----------------------------------------------------------------------
## 2026-08-30 12:52:47  step=07-opt  profile=ds4-x4-opt  promotion serve A/B — microbench winner on ds4-x4-opt
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MODE_50W
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 993,278
    concurrency_line=Maximum concurrency for 393,216 tokens per request: 2.53x
    error_lines=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 993,278
    concurrency_line=Maximum concurrency for 393,216 tokens per request: 2.53x
    error_lines=
    --- last 40 lines: logs/07-opt/head.log ---
    (APIServer pid=1) INFO:     127.0.0.1:60114 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:50252 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:52712 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:41784 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:37876 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:48308 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:55506 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:40156 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:53116 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:55396 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:55032 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:41964 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:51254 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:55414 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:46750 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:51248 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:58950 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:56438 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:36850 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:40828 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:60574 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:40110 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:46310 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:48638 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:53118 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:44398 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:53634 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:56722 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:43810 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:49034 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:56906 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:42556 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:39634 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:42508 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:36922 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:37928 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:60978 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:41076 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:47752 - "GET /health HTTP/1.1" 200 OK
    (APIServer pid=1) INFO:     127.0.0.1:50832 - "GET /health HTTP/1.1" 200 OK
    --- last 40 lines: logs/07-opt/worker-10.10.10.1.log ---
    (Worker_TP1_EP1 pid=237) INFO 08-30 09:57:44 [mxfp4.py:1730] Using MoEPrepareAndFinalizeNoDPEPModular
    (Worker_TP1_EP1 pid=237) INFO 08-30 09:57:44 [mxfp4.py:1731] Using MarlinExperts
    (Worker_TP1_EP1 pid=237) INFO 08-30 09:57:56 [eagle3_utils.py:28] Using Eagle3 auxiliary layers from config: (41, 42, 43)
    (Worker_TP1_EP1 pid=237) WARNING 08-30 09:57:56 [vllm.py:1237] VLLM_USE_BREAKABLE_CUDAGRAPH is set, disabling vLLM's torch.compile pipeline. Equivalent to -cc.mode=none.
    (Worker_TP1_EP1 pid=237) WARNING 08-30 09:57:56 [vllm.py:1247] Inductor compilation was disabled by user settings, optimizations settings that are only active during inductor compilation will be ignored.
    (Worker_TP1_EP1 pid=237) INFO 08-30 09:57:56 [kernel.py:306] Final IR op priority after setting platform defaults: IrOpPriorityConfig(rms_norm=['vllm_c', 'native'], fused_add_rms_norm=['vllm_c', 'native'])
    (Worker_TP1_EP1 pid=237) WARNING 08-30 09:57:56 [vllm.py:1757] max_num_scheduled_tokens is set to 2032 based on the speculative decoding settings. This may lead to suboptimal performance. Consider increasing max_num_batched_tokens to accommodate the additional draft token slots, or decrease num_speculative_tokens or max_num_seqs.
    (Worker_TP1_EP1 pid=237) WARNING 08-30 09:57:56 [vllm.py:2267] Model Runner V2 does not yet support the thinking_token_budget request parameter. Set VLLM_USE_V2_MODEL_RUNNER=0 if this is required.
    (Worker_TP1_EP1 pid=237) INFO 08-30 09:57:57 [weight_utils.py:867] Filesystem type for checkpoints: EXT4. Checkpoint size: 155.43 GiB. Available RAM: 11.06 GiB.
    (Worker_TP1_EP1 pid=237) INFO 08-30 09:57:57 [weight_utils.py:897] Auto-prefetch is disabled because the filesystem (EXT4) is not a recognized network FS (NFS/Lustre) and the checkpoint size (155.43 GiB) exceeds 90% of available RAM (11.06 GiB).
    (Worker_TP1_EP1 pid=237) INFO 08-30 09:58:34 [dspark.py:508] DSpark draft model loaded: 96 params
    (Worker_TP1_EP1 pid=237) INFO 08-30 09:58:34 [default_loader.py:430] Loading weights took 36.84 seconds
    (Worker_TP1_EP1 pid=237) INFO 08-30 09:58:36 [model_runner.py:381] Model loading took 40.65 GiB and 160.437595 seconds
    (Worker_TP1_EP1 pid=237) 2026-08-30 09:58:47  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `mhc_pre_big_fuse_broadcast_with_norm_tilelang` with `out_idx=None`
    (Worker_TP1_EP1 pid=237) 2026-08-30 09:59:10  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `mhc_pre_big_fuse_broadcast_with_norm_tilelang`
    (Worker_TP1_EP1 pid=237) INFO 08-30 09:59:12 [marlin_utils.py:589] You are running Marlin kernel with bf16 on GPUs before SM90. You can consider change to fp16 to achieve better performance if possible.
    (Worker_TP1_EP1 pid=237) 2026-08-30 09:59:12  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `mhc_post_tilelang` with `out_idx=None`
    [09:59:13] : Warning: T.vectorized loop over `i_hci` with extent 4 is lowered as a serial loop because TileLang could not find a valid vectorization plan. Scalar accumulator updates inside the loop are a common cause; move reductions to T.unroll or T.serial if this is intended.
    (Worker_TP1_EP1 pid=237) 2026-08-30 09:59:16  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `mhc_post_tilelang`
    (Worker_TP1_EP1 pid=237) 2026-08-30 09:59:18  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `mhc_pre_big_fuse_with_norm_tilelang` with `out_idx=None`
    (Worker_TP1_EP1 pid=237) 2026-08-30 09:59:40  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `mhc_pre_big_fuse_with_norm_tilelang`
    (Worker_TP1_EP1 pid=237) 2026-08-30 09:59:46  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `hc_head_fuse_tilelang` with `out_idx=None`
    (Worker_TP1_EP1 pid=237) 2026-08-30 09:59:54  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `hc_head_fuse_tilelang`
    (Worker_TP1_EP1 pid=237) 2026-08-30 09:59:56  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `hc_prenorm_gemm_tilelang` with `out_idx=None`
    (Worker_TP1_EP1 pid=237) 2026-08-30 09:59:59  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `hc_prenorm_gemm_tilelang`
    (Worker_TP1_EP1 pid=237) INFO 08-30 10:00:03 [gpu_worker.py:491] Initial free memory 55.61 GiB, reserved 7.61 GiB memory for KV Cache as specified by kv_cache_memory_bytes config and skipped memory profiling. This does not respect the gpu_memory_utilization config. Only use kv_cache_memory_bytes config when you want manual control of KV cache memory size. If OOM'ed, check the difference of initial free memory between the current run and the previous run where kv_cache_memory_bytes is suggested and update it correspondingly.
    (Worker_TP1_EP1 pid=237) INFO 08-30 10:00:03 [indexer.py:761] DSA indexer decode path: use_flattening=True (next_n=6, use_fp4_indexer_cache=False)
    (Worker_TP1_EP1 pid=237) INFO 08-30 10:00:03 [kernel.py:306] Final IR op priority after setting platform defaults: IrOpPriorityConfig(rms_norm=['vllm_c', 'native'], fused_add_rms_norm=['vllm_c', 'native'])
    (Worker_TP1_EP1 pid=237) INFO 08-30 10:00:14 [flashinfer_sparse_mla_warmup.py:233] Warming up DeepSeek V4 sparse MLA attention for mixed tokens=16.
    (Worker_TP1_EP1 pid=237) 2026-08-30 10:00:17  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `hc_prenorm_gemm_tilelang` with `out_idx=None`
    (Worker_TP1_EP1 pid=237) 2026-08-30 10:00:20  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `hc_prenorm_gemm_tilelang`
    (Worker_TP1_EP1 pid=237) 2026-08-30 10:00:24  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `mhc_fused_tilelang` with `out_idx=None`
    (Worker_TP1_EP1 pid=237) 2026-08-30 10:00:28  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `mhc_fused_tilelang`
    (Worker_TP1_EP1 pid=237) 2026-08-30 10:00:29  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `mhc_pre_big_fuse_with_norm_tilelang` with `out_idx=None`
    (Worker_TP1_EP1 pid=237) 2026-08-30 10:00:52  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `mhc_pre_big_fuse_with_norm_tilelang`
    (Worker_TP1_EP1 pid=237) INFO 08-30 10:01:19 [breakable_cudagraph.py:288] Breakable CUDA graph enabled
    (Worker_TP1_EP1 pid=237) INFO 08-30 10:01:39 [sparse_attn_indexer.py:719] Indexer decode-sharding INACTIVE for this batch shape (below VLLM_INDEXER_DECODE_SHARD_MIN_REQS, or ineligible).
    (Worker_TP1_EP1 pid=237) INFO 08-30 10:01:45 [speculator.py:137] Capturing model for DSpark speculator...
    (Worker_TP1_EP1 pid=237) INFO 08-30 10:01:45 [model_runner.py:843] Graph capturing finished in 27 secs, took 0.14 GiB
    (Worker_TP1_EP1 pid=237) INFO 08-30 10:05:08 [jit_monitor.py:79] Kernel JIT monitor activated; monitored JIT compilations during inference will use mode=warn.
    --- last 40 lines: logs/07-opt/worker-10.10.10.2.log ---
    (Worker_TP2_EP2 pid=237) INFO 08-30 09:57:46 [mxfp4.py:1730] Using MoEPrepareAndFinalizeNoDPEPModular
    (Worker_TP2_EP2 pid=237) INFO 08-30 09:57:46 [mxfp4.py:1731] Using MarlinExperts
    (Worker_TP2_EP2 pid=237) INFO 08-30 09:57:57 [eagle3_utils.py:28] Using Eagle3 auxiliary layers from config: (41, 42, 43)
    (Worker_TP2_EP2 pid=237) WARNING 08-30 09:57:57 [vllm.py:1237] VLLM_USE_BREAKABLE_CUDAGRAPH is set, disabling vLLM's torch.compile pipeline. Equivalent to -cc.mode=none.
    (Worker_TP2_EP2 pid=237) WARNING 08-30 09:57:57 [vllm.py:1247] Inductor compilation was disabled by user settings, optimizations settings that are only active during inductor compilation will be ignored.
    (Worker_TP2_EP2 pid=237) INFO 08-30 09:57:57 [kernel.py:306] Final IR op priority after setting platform defaults: IrOpPriorityConfig(rms_norm=['vllm_c', 'native'], fused_add_rms_norm=['vllm_c', 'native'])
    (Worker_TP2_EP2 pid=237) WARNING 08-30 09:57:57 [vllm.py:1757] max_num_scheduled_tokens is set to 2032 based on the speculative decoding settings. This may lead to suboptimal performance. Consider increasing max_num_batched_tokens to accommodate the additional draft token slots, or decrease num_speculative_tokens or max_num_seqs.
    (Worker_TP2_EP2 pid=237) WARNING 08-30 09:57:57 [vllm.py:2267] Model Runner V2 does not yet support the thinking_token_budget request parameter. Set VLLM_USE_V2_MODEL_RUNNER=0 if this is required.
    (Worker_TP2_EP2 pid=237) INFO 08-30 09:57:59 [weight_utils.py:867] Filesystem type for checkpoints: EXT4. Checkpoint size: 155.43 GiB. Available RAM: 10.13 GiB.
    (Worker_TP2_EP2 pid=237) INFO 08-30 09:57:59 [weight_utils.py:897] Auto-prefetch is disabled because the filesystem (EXT4) is not a recognized network FS (NFS/Lustre) and the checkpoint size (155.43 GiB) exceeds 90% of available RAM (10.13 GiB).
    (Worker_TP2_EP2 pid=237) INFO 08-30 09:58:36 [dspark.py:508] DSpark draft model loaded: 96 params
    (Worker_TP2_EP2 pid=237) INFO 08-30 09:58:36 [default_loader.py:430] Loading weights took 37.46 seconds
    (Worker_TP2_EP2 pid=237) INFO 08-30 09:58:38 [model_runner.py:381] Model loading took 40.65 GiB and 162.234487 seconds
    (Worker_TP2_EP2 pid=237) 2026-08-30 09:58:48  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `mhc_pre_big_fuse_broadcast_with_norm_tilelang` with `out_idx=None`
    (Worker_TP2_EP2 pid=237) 2026-08-30 09:59:10  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `mhc_pre_big_fuse_broadcast_with_norm_tilelang`
    (Worker_TP2_EP2 pid=237) INFO 08-30 09:59:12 [marlin_utils.py:589] You are running Marlin kernel with bf16 on GPUs before SM90. You can consider change to fp16 to achieve better performance if possible.
    (Worker_TP2_EP2 pid=237) 2026-08-30 09:59:12  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `mhc_post_tilelang` with `out_idx=None`
    [09:59:13] : Warning: T.vectorized loop over `i_hci` with extent 4 is lowered as a serial loop because TileLang could not find a valid vectorization plan. Scalar accumulator updates inside the loop are a common cause; move reductions to T.unroll or T.serial if this is intended.
    (Worker_TP2_EP2 pid=237) 2026-08-30 09:59:16  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `mhc_post_tilelang`
    (Worker_TP2_EP2 pid=237) 2026-08-30 09:59:18  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `mhc_pre_big_fuse_with_norm_tilelang` with `out_idx=None`
    (Worker_TP2_EP2 pid=237) 2026-08-30 09:59:40  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `mhc_pre_big_fuse_with_norm_tilelang`
    (Worker_TP2_EP2 pid=237) 2026-08-30 09:59:46  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `hc_head_fuse_tilelang` with `out_idx=None`
    (Worker_TP2_EP2 pid=237) 2026-08-30 09:59:54  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `hc_head_fuse_tilelang`
    (Worker_TP2_EP2 pid=237) 2026-08-30 09:59:56  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `hc_prenorm_gemm_tilelang` with `out_idx=None`
    (Worker_TP2_EP2 pid=237) 2026-08-30 09:59:59  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `hc_prenorm_gemm_tilelang`
    (Worker_TP2_EP2 pid=237) INFO 08-30 10:00:03 [gpu_worker.py:491] Initial free memory 55.58 GiB, reserved 7.61 GiB memory for KV Cache as specified by kv_cache_memory_bytes config and skipped memory profiling. This does not respect the gpu_memory_utilization config. Only use kv_cache_memory_bytes config when you want manual control of KV cache memory size. If OOM'ed, check the difference of initial free memory between the current run and the previous run where kv_cache_memory_bytes is suggested and update it correspondingly.
    (Worker_TP2_EP2 pid=237) INFO 08-30 10:00:03 [indexer.py:761] DSA indexer decode path: use_flattening=True (next_n=6, use_fp4_indexer_cache=False)
    (Worker_TP2_EP2 pid=237) INFO 08-30 10:00:03 [kernel.py:306] Final IR op priority after setting platform defaults: IrOpPriorityConfig(rms_norm=['vllm_c', 'native'], fused_add_rms_norm=['vllm_c', 'native'])
    (Worker_TP2_EP2 pid=237) INFO 08-30 10:00:14 [flashinfer_sparse_mla_warmup.py:233] Warming up DeepSeek V4 sparse MLA attention for mixed tokens=16.
    (Worker_TP2_EP2 pid=237) 2026-08-30 10:00:17  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `hc_prenorm_gemm_tilelang` with `out_idx=None`
    (Worker_TP2_EP2 pid=237) 2026-08-30 10:00:20  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `hc_prenorm_gemm_tilelang`
    (Worker_TP2_EP2 pid=237) 2026-08-30 10:00:24  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `mhc_fused_tilelang` with `out_idx=None`
    (Worker_TP2_EP2 pid=237) 2026-08-30 10:00:28  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `mhc_fused_tilelang`
    (Worker_TP2_EP2 pid=237) 2026-08-30 10:00:29  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `mhc_pre_big_fuse_with_norm_tilelang` with `out_idx=None`
    (Worker_TP2_EP2 pid=237) 2026-08-30 10:00:52  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `mhc_pre_big_fuse_with_norm_tilelang`
    (Worker_TP2_EP2 pid=237) INFO 08-30 10:01:19 [breakable_cudagraph.py:288] Breakable CUDA graph enabled
    (Worker_TP2_EP2 pid=237) INFO 08-30 10:01:39 [sparse_attn_indexer.py:719] Indexer decode-sharding INACTIVE for this batch shape (below VLLM_INDEXER_DECODE_SHARD_MIN_REQS, or ineligible).
    (Worker_TP2_EP2 pid=237) INFO 08-30 10:01:45 [speculator.py:137] Capturing model for DSpark speculator...
    (Worker_TP2_EP2 pid=237) INFO 08-30 10:01:45 [model_runner.py:843] Graph capturing finished in 27 secs, took 0.12 GiB
    (Worker_TP2_EP2 pid=237) INFO 08-30 10:05:08 [jit_monitor.py:79] Kernel JIT monitor activated; monitored JIT compilations during inference will use mode=warn.
    --- last 40 lines: logs/07-opt/worker-10.10.10.3.log ---
    (Worker_TP3_EP3 pid=237) INFO 08-30 09:57:46 [mxfp4.py:1730] Using MoEPrepareAndFinalizeNoDPEPModular
    (Worker_TP3_EP3 pid=237) INFO 08-30 09:57:46 [mxfp4.py:1731] Using MarlinExperts
    (Worker_TP3_EP3 pid=237) INFO 08-30 09:57:57 [eagle3_utils.py:28] Using Eagle3 auxiliary layers from config: (41, 42, 43)
    (Worker_TP3_EP3 pid=237) WARNING 08-30 09:57:57 [vllm.py:1237] VLLM_USE_BREAKABLE_CUDAGRAPH is set, disabling vLLM's torch.compile pipeline. Equivalent to -cc.mode=none.
    (Worker_TP3_EP3 pid=237) WARNING 08-30 09:57:57 [vllm.py:1247] Inductor compilation was disabled by user settings, optimizations settings that are only active during inductor compilation will be ignored.
    (Worker_TP3_EP3 pid=237) INFO 08-30 09:57:57 [kernel.py:306] Final IR op priority after setting platform defaults: IrOpPriorityConfig(rms_norm=['vllm_c', 'native'], fused_add_rms_norm=['vllm_c', 'native'])
    (Worker_TP3_EP3 pid=237) WARNING 08-30 09:57:57 [vllm.py:1757] max_num_scheduled_tokens is set to 2032 based on the speculative decoding settings. This may lead to suboptimal performance. Consider increasing max_num_batched_tokens to accommodate the additional draft token slots, or decrease num_speculative_tokens or max_num_seqs.
    (Worker_TP3_EP3 pid=237) WARNING 08-30 09:57:57 [vllm.py:2267] Model Runner V2 does not yet support the thinking_token_budget request parameter. Set VLLM_USE_V2_MODEL_RUNNER=0 if this is required.
    (Worker_TP3_EP3 pid=237) INFO 08-30 09:57:58 [weight_utils.py:867] Filesystem type for checkpoints: EXT4. Checkpoint size: 155.43 GiB. Available RAM: 10.37 GiB.
    (Worker_TP3_EP3 pid=237) INFO 08-30 09:57:58 [weight_utils.py:897] Auto-prefetch is disabled because the filesystem (EXT4) is not a recognized network FS (NFS/Lustre) and the checkpoint size (155.43 GiB) exceeds 90% of available RAM (10.37 GiB).
    (Worker_TP3_EP3 pid=237) INFO 08-30 09:58:36 [dspark.py:508] DSpark draft model loaded: 96 params
    (Worker_TP3_EP3 pid=237) INFO 08-30 09:58:36 [default_loader.py:430] Loading weights took 37.25 seconds
    (Worker_TP3_EP3 pid=237) INFO 08-30 09:58:38 [model_runner.py:381] Model loading took 40.65 GiB and 161.929922 seconds
    (Worker_TP3_EP3 pid=237) 2026-08-30 09:58:47  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `mhc_pre_big_fuse_broadcast_with_norm_tilelang` with `out_idx=None`
    (Worker_TP3_EP3 pid=237) 2026-08-30 09:59:10  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `mhc_pre_big_fuse_broadcast_with_norm_tilelang`
    (Worker_TP3_EP3 pid=237) INFO 08-30 09:59:12 [marlin_utils.py:589] You are running Marlin kernel with bf16 on GPUs before SM90. You can consider change to fp16 to achieve better performance if possible.
    (Worker_TP3_EP3 pid=237) 2026-08-30 09:59:13  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `mhc_post_tilelang` with `out_idx=None`
    [09:59:14] : Warning: T.vectorized loop over `i_hci` with extent 4 is lowered as a serial loop because TileLang could not find a valid vectorization plan. Scalar accumulator updates inside the loop are a common cause; move reductions to T.unroll or T.serial if this is intended.
    (Worker_TP3_EP3 pid=237) 2026-08-30 09:59:17  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `mhc_post_tilelang`
    (Worker_TP3_EP3 pid=237) 2026-08-30 09:59:18  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `mhc_pre_big_fuse_with_norm_tilelang` with `out_idx=None`
    (Worker_TP3_EP3 pid=237) 2026-08-30 09:59:41  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `mhc_pre_big_fuse_with_norm_tilelang`
    (Worker_TP3_EP3 pid=237) 2026-08-30 09:59:46  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `hc_head_fuse_tilelang` with `out_idx=None`
    (Worker_TP3_EP3 pid=237) 2026-08-30 09:59:54  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `hc_head_fuse_tilelang`
    (Worker_TP3_EP3 pid=237) 2026-08-30 09:59:56  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `hc_prenorm_gemm_tilelang` with `out_idx=None`
    (Worker_TP3_EP3 pid=237) 2026-08-30 10:00:00  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `hc_prenorm_gemm_tilelang`
    (Worker_TP3_EP3 pid=237) INFO 08-30 10:00:03 [gpu_worker.py:491] Initial free memory 55.86 GiB, reserved 7.61 GiB memory for KV Cache as specified by kv_cache_memory_bytes config and skipped memory profiling. This does not respect the gpu_memory_utilization config. Only use kv_cache_memory_bytes config when you want manual control of KV cache memory size. If OOM'ed, check the difference of initial free memory between the current run and the previous run where kv_cache_memory_bytes is suggested and update it correspondingly.
    (Worker_TP3_EP3 pid=237) INFO 08-30 10:00:03 [indexer.py:761] DSA indexer decode path: use_flattening=True (next_n=6, use_fp4_indexer_cache=False)
    (Worker_TP3_EP3 pid=237) INFO 08-30 10:00:03 [kernel.py:306] Final IR op priority after setting platform defaults: IrOpPriorityConfig(rms_norm=['vllm_c', 'native'], fused_add_rms_norm=['vllm_c', 'native'])
    (Worker_TP3_EP3 pid=237) INFO 08-30 10:00:14 [flashinfer_sparse_mla_warmup.py:233] Warming up DeepSeek V4 sparse MLA attention for mixed tokens=16.
    (Worker_TP3_EP3 pid=237) 2026-08-30 10:00:17  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `hc_prenorm_gemm_tilelang` with `out_idx=None`
    (Worker_TP3_EP3 pid=237) 2026-08-30 10:00:20  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `hc_prenorm_gemm_tilelang`
    (Worker_TP3_EP3 pid=237) 2026-08-30 10:00:24  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `mhc_fused_tilelang` with `out_idx=None`
    (Worker_TP3_EP3 pid=237) 2026-08-30 10:00:28  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `mhc_fused_tilelang`
    (Worker_TP3_EP3 pid=237) 2026-08-30 10:00:29  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:129): TileLang begins to compile kernel `mhc_pre_big_fuse_with_norm_tilelang` with `out_idx=None`
    (Worker_TP3_EP3 pid=237) 2026-08-30 10:00:53  [TileLang:tilelang.jit.kernel:INFO] (kernel.py:137): TileLang completes to compile kernel `mhc_pre_big_fuse_with_norm_tilelang`
    (Worker_TP3_EP3 pid=237) INFO 08-30 10:01:19 [breakable_cudagraph.py:288] Breakable CUDA graph enabled
    (Worker_TP3_EP3 pid=237) INFO 08-30 10:01:39 [sparse_attn_indexer.py:719] Indexer decode-sharding INACTIVE for this batch shape (below VLLM_INDEXER_DECODE_SHARD_MIN_REQS, or ineligible).
    (Worker_TP3_EP3 pid=237) INFO 08-30 10:01:45 [speculator.py:137] Capturing model for DSpark speculator...
    (Worker_TP3_EP3 pid=237) INFO 08-30 10:01:45 [model_runner.py:843] Graph capturing finished in 27 secs, took 0.22 GiB
    (Worker_TP3_EP3 pid=237) INFO 08-30 10:05:08 [jit_monitor.py:79] Kernel JIT monitor activated; monitored JIT compilations during inference will use mode=warn.
    verdict=startup-failed
----------------------------------------------------------------------
## 2026-08-30 13:49:55  step=07-opt  profile=ds4-x4-opt  promotion serve A/B — microbench winner on ds4-x4-opt
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MODE_50W
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    containers=jetson-cluster-node-20260830135048	Up 12 minutes | jetson-cluster-node-20260830135102	Up 12 minutes | jetson-cluster-node-20260830135105	Up 12 minutes | jetson-cluster-node-20260830135107	Up 12 minutes | 
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 993,278
    concurrency_line=Maximum concurrency for 393,216 tokens per request: 2.53x
    error_lines=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 993,278
    concurrency_line=Maximum concurrency for 393,216 tokens per request: 2.53x
    error_lines=
    ready_seconds=713
    baseline_kv=787,108  this_kv=993,278  baseline_conc=3.00  this_conc=2.53
    NOTE: KV/conc differ from baseline — lever not memory-neutral
    NOTE: identity-opt-bf16.json capture failed — deferred to a step with a live server
    IDENTITY opt-bf16: SKIPPED (missing /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/steps/logs/01-baseline/identity-baseline-bf16.json or /Users/mitaka/Projects/PyCharm/vllm-mitaka/.scratch/jetson-dsv4-decode-config/campaign/steps/logs/07-opt/identity-opt-bf16.json)
    verdict=identity-unproven
----------------------------------------------------------------------
## 2026-08-30 15:37:34  step=07-opt  profile=ds4-x4-opt  promotion serve A/B — microbench winner on ds4-x4-opt
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MODE_50W
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    containers=jetson-cluster-node-20260830153828	Up 12 minutes | jetson-cluster-node-20260830153843	Up 12 minutes | jetson-cluster-node-20260830153845	Up 12 minutes | jetson-cluster-node-20260830153848	Up 12 minutes | 
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 993,278
    concurrency_line=Maximum concurrency for 393,216 tokens per request: 2.53x
    error_lines=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 993,278
    concurrency_line=Maximum concurrency for 393,216 tokens per request: 2.53x
    error_lines=
    ready_seconds=713
    baseline_kv=787,108  this_kv=993,278  baseline_conc=3.00  this_conc=2.53
    NOTE: KV/conc differ from baseline — lever not memory-neutral
    IDENTITY_SAMPLE_OK len=2805 reasoning=16619 first60='When one long reasoning-style request arrives, the sequence '
    IDENTITY opt-bf16: DIFFERS
    content: len a=0 b=2805 first divergence at char 0
      A[0:] ''
      B[0:] 'When one long reasoning-style request arrives, the sequence is:\n\n1. **Prefix cache lookup**  \n   - The prompt is tokeniz'
    reasoning: len a=46013 b=16619 first divergence at char 109
      A[109:] ' four-node Jetson Orin cluster serving MoE model with tensor and expert parallelism. Explain exact sequence steps when one user request with long reasoning-style prompt arrives: pr'
      B[109:] ' four-node Jetson Orin cluster serving MoE model with tensor/expert parallelism. Need exact sequence steps when one user request with long reasoning-style prompt arrives: prefix ca'
    verdict=identity-differs
----------------------------------------------------------------------
## 2026-08-30 17:20:19  step=07-opt  profile=ds4-x4-opt  promotion serve A/B — microbench winner on ds4-x4-opt
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    containers= |  |  |  | 
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    ready_seconds=90
    baseline_kv=787,108  this_kv=787,108  baseline_conc=3.00  this_conc=3.00
    verdict=opt-measured
----------------------------------------------------------------------
## 2026-08-30 19:24:23  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=1
power_head=
    containers= |  |  |  | 
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2016
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    ready_seconds=90
    verdict=baseline-pinned
----------------------------------------------------------------------
## 2026-08-30 19:27:56  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MODE_50W
----------------------------------------------------------------------
## 2026-08-30 19:28:18  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MODE_50W
    containers=jetson-cluster-node-20260830192829	Up 12 minutes | jetson-cluster-node-20260830192844	Up 12 minutes | jetson-cluster-node-20260830192847	Up 12 minutes | jetson-cluster-node-20260830192850	Up 12 minutes | 
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 993,278
    concurrency_line=Maximum concurrency for 393,216 tokens per request: 2.53x
    error_lines=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 993,278
    concurrency_line=Maximum concurrency for 393,216 tokens per request: 2.53x
    error_lines=
    ready_seconds=724
----------------------------------------------------------------------
## 2026-08-30 19:49:45  step=01-baseline  profile=ds4-x4  Task 2 — pinned bf16 reference baseline
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MODE_50W
    containers=jetson-cluster-node-20260830195033	Up 12 minutes | jetson-cluster-node-20260830195048	Up 12 minutes | jetson-cluster-node-20260830195051	Up 12 minutes | jetson-cluster-node-20260830195054	Up 12 minutes | 
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    ready_seconds=723
    IDENTITY_SAMPLE_OK len=2805 reasoning=16619 first60='When one long reasoning-style request arrives, the sequence '
----------------------------------------------------------------------
## 2026-08-30 20:48:45  step=07-opt  profile=ds4-x4-opt  promotion serve A/B — microbench winner on ds4-x4-opt
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MODE_50W
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    containers=jetson-cluster-node-20260830204942	Up 12 minutes | jetson-cluster-node-20260830204957	Up 12 minutes | jetson-cluster-node-20260830205000	Up 12 minutes | jetson-cluster-node-20260830205003	Up 12 minutes | 
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 787,108
    concurrency_line=Maximum concurrency for 262,144 tokens per request: 3.00x
    error_lines=
    ready_seconds=725
    baseline_kv=787,108  this_kv=787,108  baseline_conc=3.00  this_conc=3.00
    IDENTITY_SAMPLE_OK len=2805 reasoning=16619 first60='When one long reasoning-style request arrives, the sequence '
    IDENTITY opt-bf16: EQUAL (content 2805 chars + reasoning trace 16619 chars) — numerics-preserving
----------------------------------------------------------------------
## 2026-08-30 21:24:38  step=05-restore  profile=ds4-x4  restore pre-campaign serving
image=vllm:0.27.1-r39.2.tegra-aarch64-cp312-cu132-24.04-wtdcode.dsv4.v5  master=10.10.10.4  dry_run=0
power_head=NV Power Mode: MODE_50W
    containers=jetson-cluster-node-20260830212524	Up 12 minutes | jetson-cluster-node-20260830212539	Up 12 minutes | jetson-cluster-node-20260830212541	Up 12 minutes | jetson-cluster-node-20260830212544	Up 12 minutes | 
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 993,278
    concurrency_line=Maximum concurrency for 393,216 tokens per request: 2.53x
    error_lines=
    model_dtype=dtype=torch.bfloat16
    marlin_line=You are running Marlin kernel with bf16
    scheduled=max_num_scheduled_tokens is set to 2032
    kv_tokens_line=GPU KV cache size: 993,278
    concurrency_line=Maximum concurrency for 393,216 tokens per request: 2.53x
    error_lines=
    ready_seconds=726
    verdict=restored
