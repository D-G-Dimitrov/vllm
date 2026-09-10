#!/usr/bin/env bash
# usage: run once per arm in its OWN container (an overlaid module stays in the image's
# site-packages for the rest of the container's life -- skill 30c, so never reuse one).
# /a holds a single-file tree: /a/vllm/model_executor/layers/quantization/inc/inc.py
set -u
export PYTHONDONTWRITEBYTECODE=1
F=vllm/model_executor/layers/quantization/inc/inc.py
{
echo "===== ARM=$ARM ====="
PKG=$(python3 -c 'import os,vllm;print(os.path.dirname(vllm.__file__))')
cp "/a/$F" "$PKG/${F#vllm/}"
echo "  marker return_None_in_file=$(grep -c 'return None' "$PKG/$F" 2>/dev/null || echo ERR)  (proves WHICH version the container is running)"
(cd /tmp && PYTHONPATH=/pl python3 /p/n1_probe.py 2>&1 | grep -vE "RuntimeWarning|W[0-9]{4}|torch/utils|Failed to read commit hash|from .version import")
echo "ARM_DONE"
} >> /o/leg.txt 2>&1
