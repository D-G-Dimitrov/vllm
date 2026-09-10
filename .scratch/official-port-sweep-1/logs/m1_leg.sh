#!/usr/bin/env bash
# M1 differential leg: overlay ONE module (the tiering manager) into the image's installed vllm,
# once with the NEW version and once with the BASE (parent) version, and run the same probe against
# both. Both arms use OUR own file contents, so the stale image build cannot confound the result.
set -u
export PYTHONDONTWRITEBYTECODE=1
F=vllm/v1/kv_offload/tiering/manager.py
{
echo "===== M1 c35551f892 -> 9be6d2171 tiering shutdown ====="
PKG=$(python3 -c 'import os,vllm;print(os.path.dirname(vllm.__file__))')
REL=${F#vllm/}
echo "image package: $PKG"
echo "image vllm version: $(python3 -c 'import vllm;print(vllm.__version__)')"
echo
echo "----- ARM NEW (module from 9be6d2171) -----"
cp /m/w/$F "$PKG/$REL"
echo "  marker(new-code) count=$(grep -c shutdown_error "$PKG/$REL") (expect >=1)"
(cd /tmp && PYTHONPATH=/pl python3 /probe/m1_probe.py 2>&1 | grep -vE "RuntimeWarning|W[0-9]{4}|torch/utils|Failed to read commit hash")
echo
echo "----- ARM BASE (module from 9be6d2171^) -----"
cp /m/b/$F "$PKG/$REL"
echo "  marker(new-code) count=$(grep -c shutdown_error "$PKG/$REL") (expect 0)"
(cd /tmp && PYTHONPATH=/pl python3 /probe/m1_probe.py 2>&1 | grep -vE "RuntimeWarning|W[0-9]{4}|torch/utils|Failed to read commit hash")
echo "----- EVIDENCE-COMPLETE -----"
} >> /m/out/leg.txt 2>&1
echo "LEG_EXIT=$?" >> /m/out/leg.txt
