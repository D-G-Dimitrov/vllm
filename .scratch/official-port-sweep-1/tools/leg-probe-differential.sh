#!/usr/bin/env bash
# Generic PROBE leg: run one version-agnostic probe script against the NEW then the BASE version of a
# single module, overlaid into the image's installed vllm package (worktrees have no build artifacts).
#   env: ITEM  F=repo-relative module (vllm/...)  PROBE=probe basename (mount at /probe/)  MARK=new-only pattern  OUT=log name
# NOTE: the probe MUST live outside the repo tree -- python3 puts the script dir on sys.path[0], which
# would shadow the image vllm with the unbuilt worktree and fail on vllm._C_stable_libtorch.
set -u
export PYTHONDONTWRITEBYTECODE=1
PKG=$(python3 -c 'import os,vllm;print(os.path.dirname(vllm.__file__))')
REL=${F#vllm/}
{
echo "===== $ITEM ====="
echo "module overlaid: $F    probe: $PROBE    vllm: $(python3 -c 'import vllm;print(vllm.__version__)')"
echo
echo "----- PROBE against NEW module -----"
cp "/w/$F" "$PKG/$REL"; mc=$(grep -c "$MARK" "$PKG/$REL"); echo "  marker count=$mc (expect >=1 = new code)"
(cd /tmp && PYTHONPATH=/pl python3 "/probe/$PROBE" 2>&1 | grep -vE "RuntimeWarning|W0[0-9]{3}|torch/utils")
echo
echo "----- PROBE against BASE module (this is the differential) -----"
cp "/b/$F" "$PKG/$REL"; mc=$(grep -c "$MARK" "$PKG/$REL"); echo "  marker count=$mc (expect 0 = base code)"
(cd /tmp && PYTHONPATH=/pl python3 "/probe/$PROBE" 2>&1 | grep -vE "RuntimeWarning|W0[0-9]{3}|torch/utils")
echo "----- EVIDENCE-COMPLETE -----"
} >> "/out/$OUT" 2>&1
