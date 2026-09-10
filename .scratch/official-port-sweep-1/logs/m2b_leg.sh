#!/usr/bin/env bash
# M2 gate question: does the new function-local `from ...experts.cpu_moe import ZenCPUExpertsInt8`
# inside process_weights_after_loading work on a CUDA-platform (Jetson-like) build?
# Runs against the REAL tip tree (~/dev/vllm is built in place), not the stale image package.
set -u
export PYTHONDONTWRITEBYTECODE=1
export CUDA_VISIBLE_DEVICES=""
{
echo "===== M2 8f03625b3d -> aeb034d72 : cpu_moe importability on CUDA platform ====="
echo "--- tree identity (must be /w, the picked tip) ---"
(cd /tmp && PYTHONPATH=/w python3 -c 'import vllm,sys;print("VLLM_FILE",vllm.__file__);print("PLATFORM");from vllm.platforms import current_platform;print("platform_name",current_platform.__class__.__name__)' 2>&1 | grep -vE "RuntimeWarning|Failed to read commit hash")
echo
echo "--- CHECK 1: module-scope import of cpu_moe + the new symbol (this is what the new test file and the scheme hunk both need) ---"
(cd /tmp && PYTHONPATH=/w python3 -c '
from vllm.model_executor.layers.fused_moe.experts.cpu_moe import ZenCPUExpertsInt8, ArmCPUExpertsInt8, CPUExpertsInt8
print("CHECK1_IMPORT_OK", ZenCPUExpertsInt8.__name__, ArmCPUExpertsInt8.__name__, CPUExpertsInt8.__name__)
print("CHECK1_supports_current_device =", ZenCPUExpertsInt8._supports_current_device())
' 2>&1 | grep -vE "RuntimeWarning|Failed to read commit hash" | tail -15)
echo
echo "--- CHECK 2: the scheme module that now imports cpu_moe inside process_weights_after_loading ---"
(cd /tmp && PYTHONPATH=/w python3 -c '
import inspect
from vllm.model_executor.layers.quantization.compressed_tensors.compressed_tensors_moe.compressed_tensors_moe_w8a8_int8 import CompressedTensorsW8A8Int8MoEMethod as M
src = inspect.getsource(M.process_weights_after_loading)
print("CHECK2_OK imports_cpu_moe_internally =", "cpu_moe" in src, " has_bias_gate_in_create =", "has_bias" in inspect.getsource(M.create_weights))
' 2>&1 | grep -vE "RuntimeWarning|Failed to read commit hash" | tail -8)
echo
echo "--- CHECK 3: can pytest COLLECT the new test file on this (non-CPU) platform? import runs before the module skip ---"
(cd /w && PYTHONPATH=/w:/pl python3 -m pytest tests/kernels/moe/test_zen_cpu_int8_moe.py --collect-only -q 2>&1 | tail -8)
echo "===== EVIDENCE-COMPLETE ====="
} >> /m/out/leg.txt 2>&1
echo "LEG_EXIT=$?" >> /m/out/leg.txt
