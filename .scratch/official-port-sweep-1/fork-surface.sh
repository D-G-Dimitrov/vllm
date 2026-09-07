#!/bin/bash
# Refreshed wtdcode/fork overlap oracle. The old one (git diff --name-only c01b50e390 3bec275739) is
# STALE: it freezes at Sep 2 while fork commits keep landing (d1ba3782f9, Sep 4, touched inc/inc.py and
# was MISSED by the stale oracle on item 114). Recompute per-run from the branch itself.
# Fork-local commits are the ones whose subject carries no upstream PR marker "(#1234)".
cd "${1:-/Users/mitaka/Projects/PyCharm/vllm-mitaka}" || exit 1
git log --format="%H%x09%s" c01b50e390.."$2" 2>/dev/null \
  | grep -vE '\(#[0-9]+\)$' | cut -f1 \
  | while read -r c; do git show --name-only --format= "$c"; done \
  | grep . | sort -u
