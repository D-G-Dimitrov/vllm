#!/usr/bin/env python3
"""Resolve the single known conflict of 446c769482 in cuda_communicator.py.

Refuses (exit != 0, cherry-pick aborted) unless the conflict is EXACTLY the one
mechanical import-block intersection this session predicted. Nothing is
hand-written: the resolution is the verbatim union of both sides.
"""
import subprocess
import sys

SHA = "446c76948"
BASE = "e049f5d03"
F = "vllm/distributed/device_communicators/cuda_communicator.py"

OURS_IMPORT = (
    "        from vllm.distributed.device_communicators.hier_all_reduce import (\n"
    "            HierarchicalAllReduce,\n"
)
THEIRS_IMPORT = (
    "        from vllm.distributed.device_communicators"
    ".flashinfer_pcie_ipc_all_reduce import (  # noqa: E501\n"
    "            FlashInferPcieIpcAllReduce,\n"
)
# upstream first, then fork: 'f' < 'h' keeps the block sorted (isort/ruff).
RESOLUTION = THEIRS_IMPORT + "        )\n" + OURS_IMPORT


def sh(*a, check=True):
    p = subprocess.run(a, capture_output=True, text=True)
    if check and p.returncode != 0:
        die(f"{' '.join(a)} -> rc={p.returncode}\n{p.stdout}\n{p.stderr}")
    return p.stdout.strip()


def die(msg):
    print(f"!! REFUSE: {msg}")
    subprocess.run(["git", "cherry-pick", "--abort"], capture_output=True)
    print(
        "   state after abort: HEAD=%s dirty=%s unmerged=%s"
        % (
            sh("git", "rev-parse", "--short=9", "HEAD"),
            sh("sh", "-c", "git status --porcelain | grep -vc '^??' || true"),
            sh("sh", "-c", "git ls-files -u | wc -l"),
        )
    )
    sys.exit(1)


sh("git", "rev-parse", "--verify", "HEAD")
if sh("git", "rev-parse", "--short=9", "HEAD") != BASE:
    die(f"HEAD is not the expected base {BASE}")
dirty = sh("sh", "-c", "git status --porcelain | grep -vc '^??' || true")
if dirty != "0":
    die(f"worktree dirty ({dirty}) before pick")

rc = subprocess.run(
    ["git", "cherry-pick", "-x", SHA], capture_output=True, text=True
).returncode
# The recorded decision is only valid for a CONFLICTING pick. If git ever applies
# this cleanly (e.g. after another landing changes the base), the note is wrong.
if rc == 0:
    die("pick applied CLEANLY - the recorded conflict no longer exists; re-review")
if rc != 1:
    die(f"cherry-pick rc={rc}, not a conflict")

conflicted = [x for x in sh("git", "diff", "--name-only", "--diff-filter=U").split() if x]
if conflicted != [F]:
    die(f"unexpected conflict set: {conflicted}")

# Stages must be read BEFORE `git add` destroys them.
base_s = sh("git", "show", f":1:{F}")
ours_s = sh("git", "show", f":2:{F}")
theirs_s = sh("git", "show", f":3:{F}")

raw = open(F).read()
marker = f"<<<<<<< HEAD\n{OURS_IMPORT}=======\n{THEIRS_IMPORT}>>>>>>> {SHA}"
if raw.count("<<<<<<<") != 1 or raw.count("=======") < 1 or raw.count(">>>>>>>") != 1:
    die(f"expected exactly one conflict block, found {raw.count('<<<<<<<')}")
start = raw.index("<<<<<<< HEAD\n")
end = raw.index("\n", raw.index(">>>>>>>")) + 1
block = raw[start:end]
if not block.startswith(marker):
    die(
        "conflict block is NOT the predicted mechanical import intersection.\n"
        "--- actual ---\n" + block
    )
if not raw[end:].startswith("        )\n"):
    die(
        "the line following the conflict is not the shared closing paren;\n"
        "--- block ---\n" + block + "\n--- after ---\n" + raw[end:end + 40]
    )

resolved = raw[:start] + RESOLUTION + raw[end:]
for m in ("<<<<<<<", ">>>>>>>", "======="):
    if m in resolved:
        die(f"{m!r} marker survived resolution")
open(F, "w").write(resolved)

# Faithfulness of the union: every line either side added over the merge base
# must still be present, and nothing else may have been invented.
def added(ours, base):
    b = set(base.splitlines())
    return [l for l in ours.splitlines() if l not in b]


for side, text in (("ours", ours_s), ("theirs", theirs_s)):
    for line in added(text, base_s):
        if line not in resolved.splitlines():
            die(f"{side}-added line lost by resolution: {line!r}")

subprocess.run(["git", "add", "--", F], check=True)
if sh("sh", "-c", "git ls-files -u | wc -l") != "0":
    die("unmerged entries remain after add")
sh("git", "-c", "core.editor=true", "cherry-pick", "--continue")

new = sh("git", "rev-parse", "--short=9", "HEAD")
print(f"resolved HEAD={new} ahead={sh('git','rev-list','--count',BASE+'..HEAD')}")
if sh("sh", "-c", "git status --porcelain | grep -vc '^??' || true") != "0":
    die("worktree dirty after continue")
print(f"health_after={sh('curl','-s','-o','/dev/null','-w','%{http_code}','http://localhost:8000/health')}")
print(open(F).read().split("from vllm.distributed.device_communicators.flashinfer_all_reduce")[1][:420])
