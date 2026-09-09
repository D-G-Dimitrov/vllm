#!/usr/bin/env bash
# Generic production-module differential leg.
#   mounts: /w = new tree, /b = base tree, /pl = pytest libs, /out = world-writable evidence dir
#   env:    F=repo-relative module path to overlay (vllm/...)   T=repo-relative test path
#           MARK=grep pattern present only in the NEW module     OUT=name of the log file
# Why overlay instead of mounting the tree: worktrees have no build artifacts, so `import vllm` only works
# against the image's installed package. Copying ONE module in makes the code under test exact while
# everything around it stays the built package. --import-mode=importlib keeps the repo's unbuilt tree off
# sys.path even when the test module uses relative imports.
set -u
export PYTHONDONTWRITEBYTECODE=1
PKG=$(python3 -c 'import os,vllm;print(os.path.dirname(vllm.__file__))')
REL=${F#vllm/}
run_tests() {
  ( cd / && PYTHONPATH=/pl python3 -m pytest "$1" --rootdir="$2" --import-mode=importlib \
      -rA -q --noconftest -p no:cacheprovider 2>&1 \
      | grep -E "^(PASSED|FAILED|ERROR)|passed|failed|error" | tail -24 )
}
{
echo "===== ${ITEM:-item ?}  module under test: $F   tests: $T ====="
echo "vllm package: $PKG ($(python3 -c 'import vllm;print(vllm.__version__)'))   marker pattern: $MARK"
echo
echo "----- LEG A  NEW module + NEW tests -----"
cp "/w/$F" "$PKG/$REL"; mc=$(grep -c "$MARK" "$PKG/$REL"); echo "  marker count=$mc (expect >=1 = new code)"
run_tests "/w/$T" /w
echo
echo "----- LEG B  BASE module + NEW tests (new tests should fail here if they pin the fix) -----"
cp "/b/$F" "$PKG/$REL"; mc=$(grep -c "$MARK" "$PKG/$REL"); echo "  marker count=$mc (expect 0 = base code)"
run_tests "/w/$T" /w
echo
echo "----- LEG C  BASE module + BASE tests (pre-existing health) -----"
run_tests "/b/$T" /b
echo "----- EVIDENCE-COMPLETE -----"
} >> "/out/${OUT:-leg.log}" 2>&1
