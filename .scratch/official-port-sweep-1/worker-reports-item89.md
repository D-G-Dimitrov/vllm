# Grind item 89 — official `8fd9eb85d5` (#54407)

**Decision: PICKED** → new sha `118b9d373` on `mitaka/backport`. Not pushed (per brief).

## Result

| Field | Value |
|---|---|
| pr_sha | `8fd9eb85d5a3d8f36cacb2b5d570a7a51c8200d8` |
| decision | PICKED |
| new_sha | `118b9d373` |
| conflict_class | none — clean `git cherry-pick -x`, 0 conflicted files |
| blame_coverage | n/a (no conflicts); semantic checks run anyway — see below |
| patch_id_match | **true** — `41fc9909a3a2e40d6ec9c6c1c676670c07d15997` both sides |
| tests | new tree **35 passed / 0 failed**; all 3 new tests pass individually by name |
| base_compare | parent `e16d574bb` **32 passed / 0 failed** → fail-sets identical (both empty); delta = exactly +3 = the 3 tests this PR adds |
| env_impact | none; GPU never exposed; production `:8000` healthy throughout |
| escalated | false |

Gate at dispatch: tip `e16d574bb`, modified 0, branch `mitaka/backport`, no sequencer. Pass.

## What the PR does

Refactors `TokenizeParams._token_truncation` into a reusable `_truncation_slice()` and applies **the same slice** to `prompt_token_offsets`, which was previously left un-truncated while `prompt_token_ids` was truncated — breaking the documented equal-length invariant between the two lists whenever an explicit `truncation_side` disabled tokenizer-level truncation.

## Why no escalation (verified, not assumed)

This lands in shared tokenize code reached by the general render path, so the stop rule was tested properly:

- `_truncation_slice` / `_token_truncation` are **private to `vllm/renderers/params.py`** — no callers outside the file.
- `apply_post_tokenization` callers: `vllm/renderers/base.py:536,572` (all models) and `vllm/entrypoints/pooling/scoring/io_processor.py:547` (item 87's scoring path).
- The new block is gated on `prompt.get("prompt_token_offsets") is not None`, and `return_token_offsets: bool = **False**` (params.py:182). Off by default ⇒ block unreachable on default paths ⇒ **zero default-path delta for DSV4, qwen4_exp or GLM-5.3-Flash.**
- `_token_truncation` is behaviour-preserving: it returns `tokens` unchanged when `_truncation_slice` returns `None`, matching the old inline early-returns.
- `vllm/renderers/params.py` is **not** a generated artifact — no generator in `tools/` references it.
- Composes correctly with item 87 (`e16d574bb`), which landed the same region an hour earlier: `_validate_tokens` still runs `(_token_truncation, _token_padding, _token_len_check)` in that order, so truncate-before-padding is preserved and offsets are never double-truncated.
- No external version/URL claims, so checks (4)/(5) had nothing to bite on.

## Commands run

```
ssh jetson-222 'cd ~/dev/vllm && git rev-parse --short=9 HEAD'                    # e16d574bb (gate)
ssh jetson-222 'cd ~/dev/vllm && git cherry-pick -x 8fd9eb85d5'                    # clean, -> 118b9d373
ssh jetson-222 'cd ~/dev/vllm && git show 8fd9eb85d5 | git patch-id --stable'      # 41fc9909a...
ssh jetson-222 'cd ~/dev/vllm && git diff e16d574bb..HEAD | git patch-id --stable' # 41fc9909a... (match)
# diff of the +/- lines upstream vs ours: byte-identical
# CPU-only container (CUDA_VISIBLE_DEVICES=""), image ...d4d703c:
python -m pytest tests/renderers/test_token_offsets.py tests/entrypoints/scale_out/render/test_render.py -rA -q   # 35 passed
python -m pytest ".../TestTruncationKeepsOffsetsAligned" -rA -q                     # 2 passed (left, right)
python -m pytest ".../test_completion_render_truncated_token_offsets" -rA -q        # 1 passed
# base leg, same two files from `git archive e16d574bb`:             32 passed / 0 failed
```

Per-test confirmation (new tree, `-rA`, by name):
`TestTruncationKeepsOffsetsAligned::test_explicit_truncation_side_truncates_offsets[left]` PASSED
`...[right]` PASSED
`test_render.py::test_completion_render_truncated_token_offsets` PASSED

## Recipe fix discovered (will recur — worth folding into the grind skill)

The documented base-compare step copies `vllm/*.so`, which is **insufficient**: the tree has **8 `.so` files, 2 of them nested** in `vllm/vllm_flash_attn/`. Copying only the 6 top-level ones made the base leg die with a spurious
`ImportError: vllm.vllm_flash_attn requires the CUDA flash attention extensions` collection error — which looks exactly like a real regression but is a harness artifact. Correct approach:

```bash
find vllm -name "*.so" | while read f; do mkdir -p "/tmp/baseNN/$(dirname "$f")"; cp "$f" "/tmp/baseNN/$f"; done
```

Also: `vllm/_version.py` **does not exist** in this repo (only `vllm/version.py`); the brief's instruction to copy it silently no-ops and yields a benign "No module named vllm._version" warning.

## Cleanup / safety verified

- Repo: tip `118b9d373`, modified **0**, untracked only the 2 pre-existing entries (`.cargo-home/`, `i55_result.txt`).
- No `CHERRY_PICK_HEAD`, no `.git/sequencer`; runner scripts, `.i89_base.tar` and stray logs removed (0 `i89` leftovers).
- Second lane untouched: `~/dev/vllm-swap88` still at `e16d574bb` on `swap/qwen-88` with its own in-flight state; never `cd`-ed into or written.
- Nothing pushed; nothing under `.scratch/` modified.
- GPU never exposed (`-e CUDA_VISIBLE_DEVICES=""` on every run); all containers `--rm` and gone.
- Serving: `:8000` health **200** (single `vllm serve`, NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4, host-network container, started 07:30 with `restarts=0`, ~6h before this task). `:8001` has **no listener on host or inside the container** — it is not a live endpoint, so there was nothing to disturb; the handoff note's "`:8000`/`:8001`" is stale.

## Residual risks

- None functional. The 2 touched test files pass fully on CPU; but note `test_completion_render_truncated_token_offsets` spins a real OpenAI server via `RemoteOpenAIServer`, so it is heavier than a unit test and was the slow part (~26s).
- Item 89 is the **third** consecutive PR in `renderers/params.py` (87, 89) plus scoring `io_processor` — expect future items in this cluster to conflict contextually; resolution rule that worked here is "keep truncate→pad ordering, add parallel-sequence handling alongside".
- Neither `89` nor its neighbour appears in `swap-dependent.txt`, so this pick is independent of the `swap/qwen-88` lane — confirmed by the clean apply.

## Recommended next step

Push `118b9d373` and bookkeep item 89 (outcomes entry + checklist tick), then continue oldest-first on `~/dev/vllm` with the next non-deferred pending item (`4ae172231c`, skipping `8e92248f79` and `fdbf2ddbd2` which are swap-deferred).

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Exactly one commit added to mitaka/backport via `git cherry-pick -x 8fd9eb85d5` -> 118b9d373, touching only the upstream PR's 3 files (vllm/renderers/params.py + 2 test files). No push, no .scratch/ edits, no work in the second lane's worktree. patch-id identical to upstream (41fc9909a3a2e40d6ec9c6c1c676670c07d15997) and +/- lines byte-identical, proving no scope widening."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "Gate (tip e16d574bb, mod=0), patch-id proof both directions, per-test -rA confirmation of all 3 new tests by name, new tree 35 passed/0 failed, base tree e16d574bb 32 passed/0 failed => identical empty fail-set with delta exactly +3 = the added tests. Cleanup and no-sequencer verified; GPU never exposed; production :8000 health 200."
    }
  ],
  "changedFiles": [
    "vllm/renderers/params.py",
    "tests/renderers/test_token_offsets.py",
    "tests/entrypoints/scale_out/render/test_render.py"
  ],
  "testsAddedOrUpdated": [
    "tests/renderers/test_token_offsets.py",
    "tests/entrypoints/scale_out/render/test_render.py"
  ],
  "commandsRun": [
    {
      "command": "ssh jetson-222 'cd ~/dev/vllm && git rev-parse --short=9 HEAD; git status --porcelain | grep -v ^?? | wc -l'",
      "result": "passed",
      "summary": "Gate: tip e16d574bb, modified 0, branch mitaka/backport, no CHERRY_PICK_HEAD"
    },
    {
      "command": "ssh jetson-222 'cd ~/dev/vllm && git cherry-pick -x 8fd9eb85d5'",
      "result": "passed",
      "summary": "Clean apply, 0 conflicts, new sha 118b9d373, 3 files changed 106 insertions 8 deletions"
    },
    {
      "command": "ssh jetson-222 'cd ~/dev/vllm && git show 8fd9eb85d5 | git patch-id --stable; git diff e16d574bb..HEAD | git patch-id --stable'",
      "result": "passed",
      "summary": "Both 41fc9909a3a2e40d6ec9c6c1c676670c07d15997; +/- lines byte-identical; (cherry picked from) trailer present"
    },
    {
      "command": "docker run --rm --runtime nvidia --network host -e CUDA_VISIBLE_DEVICES=\"\" -v ~/dev/vllm:/workspace -w /workspace <image d4d703c> bash /workspace/.i89_run.sh",
      "result": "passed",
      "summary": "CPU-only: 35 passed / 0 failed on the 2 touched files; 3 new tests also pass individually by name"
    },
    {
      "command": "docker run ... bash /workspace/.i89_base.sh  (base tree git archive e16d574bb + all 8 .so copied recursively)",
      "result": "passed",
      "summary": "Base leg 32 passed / 0 failed -> identical empty fail-set vs new tree, delta exactly +3 new tests"
    },
    {
      "command": "ssh jetson-222 'cd ~/dev/vllm && rm -f .i89_run.sh .i89_base.sh .i89_base.tar && git status --porcelain'",
      "result": "passed",
      "summary": "Tree clean (mod=0), only 2 pre-existing untracked entries, no sequencer residue, swap worktree untouched at e16d574bb"
    },
    {
      "command": "curl -s -o /dev/null -w %{http_code} http://localhost:8000/health",
      "result": "passed",
      "summary": "Production serving :8000 returned 200 before and after; container restarts=0, started ~6h before task"
    }
  ],
  "validationOutput": [
    "NEW TREE (HEAD 118b9d373): 35 passed, 15 warnings in 82.24s — 0 failed, 0 errors",
    "BASE TREE (e16d574bb): 32 passed, 15 warnings in 79.35s — 0 failed, 0 errors; fail-sets identical (both empty), +3 delta equals the tests added by this PR",
    "PASSED tests/renderers/test_token_offsets.py::TestTruncationKeepsOffsetsAligned::test_explicit_truncation_side_truncates_offsets[left]",
    "PASSED tests/renderers/test_token_offsets.py::TestTruncationKeepsOffsetsAligned::test_explicit_truncation_side_truncates_offsets[right]",
    "PASSED tests/entrypoints/scale_out/render/test_render.py::test_completion_render_truncated_token_offsets",
    "Semantic gate: return_token_offsets defaults False (vllm/renderers/params.py:182) so the new offsets-truncation block is unreachable on default paths -> zero default-path delta for DSV4 / qwen4_exp / GLM-5.3-Flash; _truncation_slice has no callers outside params.py; _validate_tokens still orders truncation -> padding -> len_check (item 87 ordering preserved)",
    "Cleanup verified: mod=0, untracked=2 (both pre-existing), CHERRY_PICK_HEAD/sequencer absent, 0 i89 leftovers, ~/dev/vllm-swap88 still e16d574bb"
  ],
  "residualRisks": [
    "Recipe defect found and worked around, not yet fixed in the grind skill: base-compare must copy .so files RECURSIVELY (8 total, 2 nested in vllm/vllm_flash_attn/). Copying only vllm/*.so produced a spurious 'ImportError: vllm.vllm_flash_attn requires the CUDA flash attention extensions' collection error that mimics a real regression.",
    "vllm/_version.py does not exist in this repo (only vllm/version.py); copying it is a silent no-op yielding a benign 'No module named vllm._version' warning.",
    "test_completion_render_truncated_token_offsets launches a real server via RemoteOpenAIServer (~26s), so this file is heavier than a unit test in future runs.",
    "The renderers/params.py cluster is now touched by consecutive items (87, 89); later items here will conflict contextually. Working rule: preserve truncate->pad ordering and add parallel-sequence handling alongside.",
    "Nothing was pushed and no bookkeeping was written, per brief; item 89 is still unchecked in the tracker and the orchestrator must push + record it.",
    "Handoff context claiming serving on ':8000/:8001' is stale: only :8000 has a listener (host-network container, restarts=0, predating this task). :8001 has no listener on host or inside the qwen38-flash-next container."
  ],
  "noStagedFiles": true,
  "diffSummary": "Cherry-pick of upstream #54407 onto mitaka/backport: extracts TokenizeParams._truncation_slice() as the single source of truth for the truncation slice and applies it to prompt_token_offsets in apply_post_tokenization, keeping offsets aligned with truncated prompt_token_ids; _token_truncation becomes a thin wrapper (behaviour-preserving). Plus 2 upstream tests (3 new cases).",
  "reviewFindings": [
    "no blockers"
  ],
  "manualNotes": "PICKED, not pushed (per brief). new_sha 118b9d373, parent e16d574bb, patch-id matches upstream exactly. Orchestrator should push and write the outcomes entry + checklist tick for item 89. Also please fold the recursive .so copy fix into the official-port-grind-loop skill base-compare step, and correct the serving-endpoint note in the handoff doc."
}
```
