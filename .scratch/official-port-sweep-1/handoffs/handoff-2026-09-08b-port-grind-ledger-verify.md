# Handoff — official→`mitaka/backport` port grind (sweep-1), session 2026-09-08b

**Mode:** orchestrator-direct, HYBRID depth · **Status:** healthy; 4 items landed; **grind paused for owner eyes on §4**
Supersedes `/tmp/handoff-2026-09-08-port-grind-hybrid.md` (its §1–§6 facts still hold; the tooling section below replaces its §3).

## 1. Ground truth (re-derive, do not trust this doc)

```
Mac push clone  /Users/mitaka/Projects/PyCharm/vllm-mitaka   mitaka/backport   tip e049f5d03 (== origin)
jetson work box jetson-222:~/dev/vllm                        tip e049f5d03, dirty 0, unmerged 0, 2 worktrees
ledger branch   mitaka/backport-ledger  origin tip 9612acd2f; SRC == ledger == jetson tgz (5285b4b8ad67 both sides)
ledger counts   checked 137 / unchecked 179 / skipped 1 = 317   (verify: bash /tmp/audit.sh)
swap worktree   jetson-222:~/dev/vllm-swap88 = 337d3f5dd   (untouched)
production      :8000 = 200 (probed before/after every item and every container run)
next actionable 446c769482 [Distributed] Add opt-in FlashInfer PCIe IPC all-reduce backend (#53576)
```

**Landmine #1 (unchanged):** agent cwd `/Users/mitaka/Projects/PyCharm/vllm-backport` is a **different repo**
(origin `wtdcode/vllm-backport`, detached at tag `v0.11.3`). All pushes happen from `vllm-mitaka`.

**Landmine #2 (new, cost me a false alarm this session):** `git -C "$VAR"` with `$VAR` **empty** does not error —
it runs in the agent cwd and returns the *other* repo's HEAD/reflog/remotes. Two of my diagnostics reported
"the push clone was swapped / origin lost the ledger branch", which was entirely false. Always pass the absolute
path literally to `git -C`, and treat an empty `branch --show-current` as "wrong repo", not "broken repo".

## 2. Landed this session (138–141; per-item detail in `outcomes.log.md`, do not re-derive)

| # | upstream | landing | tier |
|---|---|---|---|
| 138 | `907b1a7f22` ROCm CI image-pull | `9ccd9694b` | minimum gate |
| 139 | `882ca8d696` FlashInfer cutedsl W4A16 linear | `7c4ad3d08` | **full depth** (measured dispatch differential) |
| 140 | `923949e6e3` preemption histogram metric | `2c4b66ba7` | minimum gate |
| 141 | `188716ace7` MADV_POPULATE_WRITE fallback | `e049f5d03` | **full depth** (real CPU leg) |

## 3. Tooling — `.scratch/official-port-sweep-1/tools/` (all changes verified by isolated tests, not by reading)

* `tick.sh` **normalises shas** (10/9) and refuses unless the tracker match is **exactly 1 before** the entry is
  written. Observed failure: a 40-char sha made the tick sed match nothing and it printed `ticked 0->0`, exit 0 —
  item 138 landed UNCHECKED with a confident ledger entry (repaired by hand).
* `tick.sh`'s backtick guard now applies to the **argv path only**; file notes are the sanctioned channel and
  legitimately contain code spans. The old guard would abort *after* `land.sh` pushed.
* `tick.sh` accepts `TIER="Full depth (hybrid): …"` so non-minimum-gate entries are not mislabelled.
* `fast.sh` finally honours the documented `@notefile` (it previously wrote the literal `@/tmp/note.md` as the entry).
* **NEW `ledger-verify.sh <up10> <entryN>`**, called by `tick.sh`: asserts the entry exists in SRC, on the ledger
  branch, and inside the jetson tarball. Rationale in §4 of this file's namesake event:
  item 141's first tick printed `entry=141 ticked 1->1` and a mirror sha, yet both files were later found reverted
  to the *previous* item's content **and mtime**, with no ledger commit and the mirror unchanged. Cause **not
  identified** (no shadow writer, no branch swap, tools edits and `logs/` writes persisted; only those two data
  files rolled back, which is the signature of a mtime-preserving restore). Code was never at risk — all four
  landings pushed and asserted three ways. Detection is now in-line; prevention is not.
* Persistent CPU test deps for legs: `jetson-222:~/dev/pytest-libs` (mount `-v ~/dev/pytest-libs:/pl`,
  `PYTHONPATH=/pl`; installed once via `pip install --target /pl --index-url https://pypi.org/simple`).

## 4. Owner-decision items (nothing blocks; these need a human call, not a "go?")

1. **Item 139 is inert on Jetson but NOT on SM 100 — and the fork has SM 100 boxes.** Measured (not inferred):
   with the pick applied, `init_nvfp4_linear_kernel` selects `MarlinNvFp4LinearKernel` at simulated cc 87 for both
   `use_a16` values (identical to the parent tree), and `FlashInferCuteDslNvFp4W4A16LinearKernel` at cc 100 — and
   the runtime image's FlashInfer really does export `mm_bf16_fp4`/`prepare_bf16_fp4_weights`
   (`has_flashinfer_bf16_fp4() → True`), so nothing would stop it there. Re-open **before serving any
   NVFP4/`W4A16_NVFP4` checkpoint on SM 100/103/12x**: the GEMM changes (numerics change; `--linear-backend`
   overrides). Revert = `git revert 7c4ad3d08`. Full table in `outcomes.log.md` §139, raw evidence
   `logs/i139-nvfp4-dispatch-diff.txt`.
2. **Item 141 killed a class of risk cheaply:** L4T `6.8.12-1021-tegra` accepts `madvise(23)` while CPython's
   `mmap` doesn't expose the constant, so the EC fallback is dead code here. No action; recorded so the next agent
   doesn't re-derive it.
3. **Next item is not a minimum-gate item.** `446c769482` (FlashInfer PCIe IPC all-reduce, opt-in) touches 4
   fork-diverged files: `vllm/envs.py` (+327/-2 fork delta), `device_communicators/cuda_communicator.py`
   (+31/-0), `model_executor/warmup/kernel_warmup.py` (+8/-0), and `parallel_state.py` is clean — plus
   `flashinfer_pcie_ipc_all_reduce.py` is a **new file upstream** that already exists in the fork tree
   (probe reports `fork=HEAD:vllm`), i.e. the fork carries its own version of that module. Expect a genuine
   collision needing the resolve-and-note gate or a stop-and-ask, and read the fork's existing copy first.

## 5. Procedure reminders that earned their keep tonight

* **A differential leg must prove which tree it loaded, per leg.** `PYTHONPATH` loses to `sys.path[0]` (the
  script's dir) and, under pytest, to the rootdir that holds `conftest.py`. Both traps fired tonight; both looked
  like clean passes. Print `vllm.__file__` / read the pytest warning path, and copy the new test file *into* the
  base tree for the mismatched-pair leg. Skill Verification 19.
* **`blob NE` on a fork-diverged file → prove gap invariance** (`diff` of the fork-vs-upstream gap before vs
  after; only hunk header line numbers may differ). Skill Verification 20. Strip diff prefixes with
  `sed 's/^+//'`, never `${l#+ }` (that produced false "LOST" lines on `+@functools.cache`).
* Minimum gate still means **read the diff** — 138 and 140 were only cleared because the hunks were read.
* Never `sleep >30s` inside a shell call here; the tool caps at 30 s (the command dies, the remote work continues).

## 6. Suggested skills

* **`official-port-grind-loop`** (bumped to v5 this session) — **call first**; Verification is now 1–23 and holds
  every gotcha above, including the two new probe-identity rules.
* `resolving-merge-conflicts` — for `446c769482` (§4.3) and the forecast-model mega-conflicts ahead.
* `jetson-network-check` — only if `jetson-222` is unreachable at start.
* Do **not** re-enable worker dispatch without `fix-subagent-launch-after-pi-update` +
  `enforce-subagent-fanout-concurrency`; orchestrator-direct is working and workers are not the bottleneck.

## 7. Artifacts (referenced, not duplicated here)

* `outcomes.log.md` §138–§141 — per-item records (139 and 141 carry the measurement tables)
* `logs/i139-nvfp4-dispatch-diff.txt`, `logs/i141-ec-madvise-cpu-leg.txt` — raw leg output
* `issues/03-pr-grind.md` — queue (file order = queue order); `blocked.md` — empty
* `swap-dependent.txt`, `skipped.txt`, `heat-map-raw.txt`, `worker-brief.md`, `ledger-sync.sh`, `tools/`
* `.scratch/official-port-sweep-1/handoffs/` — this file's predecessors

No credentials, keys, or PII in this document. Internal addresses (devpi, jetson IP) are infrastructure metadata.
