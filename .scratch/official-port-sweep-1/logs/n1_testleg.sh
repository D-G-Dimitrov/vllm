#!/usr/bin/env bash
# N1 leg: run upstream's NEW regression tests by name against (a) the picked tip tree and
# (b) the PARENT tree carrying the new test file (the mismatched pair -- running new tests on
# the parent tree alone proves nothing because they do not exist there).
# Expect: NEW arm all pass; BASE arm FAILS on the unknown-layer cases (base returns
# UnquantizedLinearMethod where upstream now returns None). That is the discriminator.
set -u
export PYTHONDONTWRITEBYTECODE=1
export CUDA_VISIBLE_DEVICES=""
NEW=3952a84d5
SEL="get_quant_method"
OUT=/m/out/leg.txt
{
echo "===== N1 92ccd2c306 -> $NEW : INC get_quant_method regression tests ====="

echo "----- ARM NEW (tip tree, /w) -----"
(cd /w && PYTHONPATH=/w:/pl python3 -m pytest tests/quantization/test_auto_round.py -rA -k "$SEL" -p no:cacheprovider 2>&1 | grep -vE "RuntimeWarning|W[0-9]{4}|torch/utils|Failed to read commit hash|^\s*$" | tail -30)

echo
echo "----- ARM BASE (parent module + the NEW test file) -----"
rm -rf /m/b2 && mkdir -p /m/b2
(cd /w && git archive $NEW^ | tar -x -C /m/b2) || echo "  ABORT: git archive failed"
cp /w/tests/quantization/test_auto_round.py /m/b2/tests/quantization/test_auto_round.py
( cd /w && find vllm -name '*.so' -print0 | xargs -0 -I{} cp --parents {} /m/b2/ )
echo "  .so copied: $(find /m/b2/vllm -name '*.so' | wc -l | tr -d ' ') (expect 8, 2 nested in vllm/vllm_flash_attn)"
echo "  tree marker (must be BASE: expect 0): return_None=$(grep -c "return None" /m/b2/vllm/model_executor/layers/quantization/inc/inc.py)"
echo "  test file present in BASE tree (copied in): $(grep -c 'def test_inc_get_quant_method' /m/b2/tests/quantization/test_auto_round.py)"
(cd /m/b2 && PYTHONPATH=/m/b2:/pl python3 -m pytest tests/quantization/test_auto_round.py -rA -k "$SEL" -p no:cacheprovider 2>&1 | grep -vE "RuntimeWarning|W[0-9]{4}|torch/utils|Failed to read commit hash|^\s*$" | tail -30)
echo "----- EVIDENCE-COMPLETE -----"
} >> $OUT 2>&1
