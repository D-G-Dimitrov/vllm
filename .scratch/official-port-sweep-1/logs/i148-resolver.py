#!/usr/bin/env python3
"""Resolve the single conflict from picking 4ac452ad98 into the fork's gpu_worker.py.

Shape of the conflict: the fork inserted whole PLE-offload methods immediately before
`def _get_sleep_mode_backend(...)`, and upstream rewrote exactly that def line into a
`sleep_mode_backend` property. Git therefore could not tell "insert before" from "rewrite".

Resolution = verbatim union: keep every fork line, drop the ONE base line upstream deletes
(the old `def _get_sleep_mode_backend`), and take upstream's replacement lines. No upstream
hunk dropped; no fork-authored line lost. Refuses to do anything if the block does not match
this exact expected shape.
"""
import sys

P = "vllm/v1/worker/gpu_worker.py"
OLD_DEF = '    def _get_sleep_mode_backend(self) -> "SleepModeBackend":'
WANT_UP = ['    @property', '    def sleep_mode_backend(self) -> "SleepModeBackend":']

lines = open(P).read().split("\n")
starts = [i for i, l in enumerate(lines) if l.startswith("<<<<<<< ")]
mids = [i for i, l in enumerate(lines) if l == "======="]
ends = [i for i, l in enumerate(lines) if l.startswith(">>>>>>> ")]
if not (len(starts) == len(mids) == len(ends) == 1):
    sys.exit(f"ABORT: expected exactly 1 conflict block, got {len(starts)}/{len(mids)}/{len(ends)}")
s, m, e = starts[0], mids[0], ends[0]
head, up = lines[s + 1 : m], lines[m + 1 : e]

if head[-1] != OLD_DEF:
    sys.exit(f"ABORT: HEAD side does not end with the old def line:\n{head[-1]!r}")
if up != WANT_UP:
    sys.exit(f"ABORT: upstream side is not the expected property pair:\n{up!r}")
if not any("_has_ple_layers" in l for l in head):
    sys.exit("ABORT: HEAD side does not contain the fork's PLE methods -- wrong conflict")

merged = lines[:s] + head[:-1] + up + lines[e + 1 :]   # exclude the marker lines themselves
out = "\n".join(merged)
bad = [l for l in merged if l.startswith("<<<<<<<") or l.startswith(">>>>>>>") or l == "======="]
if bad:
    sys.exit(f"ABORT: {len(bad)} conflict marker line(s) survived, e.g. {bad[0][:40]!r}")

open(P, "w").write(out)
kept = out.count("    def _has_ple_layers") + out.count("    def _validate_ple_offload_config")
print("resolved: 1 hunk (verbatim union)")
print(f"  fork PLE methods present: {kept} (expect 2)")
print(f"  old def removed: {OLD_DEF not in out}")
print(f"  new property present: {'def sleep_mode_backend' in out}")
import ast
try:
    ast.parse(out)
    print("  ast.parse: OK")
except SyntaxError as ex:
    sys.exit(f"ABORT: resolved file is not valid Python: {ex}")
