# Handoff — grind STOPPED 2026-09-10 (superseded by fork rebase)

## Why it stopped

Owner instruction: stop after the in-flight item. Reason given — `wtdcode/vllm-backport` master was rebased onto official vLLM main — verified from refs, not taken on faith:

```
c866ba9d11 in vllm-backport/master: YES      2f01039666 in vllm-backport/master: YES
e7cf4730d6 in vllm-backport/master: YES      0d4ad47981 in vllm-backport/master: YES
mitaka/backport vs vllm-backport/master: ahead=170 behind=661
```

Four of four sampled official commits that this grind was cherry-picking are already ancestors of the rebased fork master. The tracker's remaining 148 unchecked items target `mitaka/backport`, a branch the rebased master now supersedes. **Do not resume the sweep against `vllm-backport/master`** — it would re-land commits the fork already contains.

## Ref state at stop

| ref | tip |
| --- | --- |
| Mac `refs/heads/mitaka/backport` | `6b7d3d68c` |
| `origin/mitaka/backport` | `6b7d3d68c` |
| jetson push clone `~/dev/vllm` (branch `mitaka/backport`) | `855be75bd` — **one commit ahead, unpushed** (see below) |
| Mac working tree | on branch `mitaka/official` @ `e6cb56337`, NOT on `mitaka/backport` |

The Mac worktree was moved out from under the grind by a separate session: reflog shows `master` rebased onto `vllm-backport/master`, then `mitaka/official` rebased onto `upstream/main`. Nothing was switched back — that session owns the checkout. `land.sh` guard 0 correctly refused to land into a worktree that isn't at the expected base.

Production untouched throughout: `:8000` returned 200 before and after every pick; the serving container was never restarted.

## Ledger state

`checked=168 unchecked=148 skipped=1 sum=317`. Last ticked and ledger-verified: **entry 172** (`2f01039666` → `6b7d3d68c`).

The ledger is **untracked in git** (`.gitignore` doesn't cover it, but no branch tree contains it — `git show <ref>:.scratch/.../outcomes.log.md` is empty for HEAD, `mitaka/backport`, `origin/mitaka/backport` and `master`). It exists only as working-tree files plus the per-tick mirror `jetson-222:~/dev/scratch-ledger.tgz`. That is why the rebase cost nothing — and why a clean checkout or `git clean -fdx` in this worktree would destroy the only copy. Back it up before anyone cleans the tree.

## Entry 173 — resolved, verified, NOT landed

`e7cf4730d6` `[Bugfix] Drop incomplete tool-call markup in non-streaming to match streaming (#47562)`. Conflicted in `vllm/parser/engine/streaming_parser_engine.py` (one region, both sides appending independent `__init__` fields), resolved as a union, committed on the jetson clone only as `855be75bd` with the `-x` trailer.

Verification already done (details in the leg logs, `logs/i173-N1-leg-{newarm,basearm}.txt`):

- Per-file faithfulness: 4 files blob EQ, the 2 fork-diverged files delta-IDENTICAL.
- Fork integrity: 161 fork lines in `streaming_parser_engine.py` present verbatim (missing=0), gap-invariance with zero non-header body lines, `allowed_tool_names`/`suppress_tool_calls` still in `__init__` by ast.
- Composition: upstream's new `skip_reasoning_parsing` bypass sits in `_on_terminal` before the `skip_tool_parsing` branch and calls the fork-extended `_emit_for_state`; it cannot reach the fork's tool-name filtering because `_compute_reasoning_markup_terminals` admits only markers whose transitions stay inside CONTENT/REASONING.
- Leg (CPU, mock tokenizer, overlay trees verified by `diff -rq` to differ in exactly the 4 changed files): NEW 7 failed / 379 passed vs BASE 18 failed / 368 passed → **11 named tests fixed, 0 regressions**, including `test_think_block_passes_through_both_paths[qwen3_coder]` (the production tool parser) and `[deepseek_v4]`.
- Not inert: `qwen3_coder` → `Qwen3EngineToolParser` and `nemotron_v3` is engine-based, so `DelegatingParser._engine_based` is True on :8000 — non-streaming truncated tool-call markup now drops like streaming does, and streaming deferred-content ordering changes.

Saved as `handoffs/entry173-e7cf4730d6-resolved.patch` (531 lines) so the resolution survives regardless of what happens to the jetson clone.

Owner decision needed on `855be75bd`, not taken here because it is moot given the rebase and would have required touching another session's checkout:

- **drop it** — `ssh jetson-222 'cd ~/dev/vllm && git reset --hard 6b7d3d68c'` (restores three-way tip agreement), or
- **land it** without switching the Mac worktree — fetch the object, fast-forward the uncommitted branch ref, push: `git -C /Users/mitaka/Projects/PyCharm/vllm-mitaka fetch origin mitaka/backport` then `git -C /Users/mitaka/Projects/PyCharm/vllm-mitaka branch -f mitaka/backport 855be75bd` (legal only while `mitaka/backport` is not checked out) then `git -C /Users/mitaka/Projects/PyCharm/vllm-mitaka push origin mitaka/backport`, and finally `tick.sh e7cf4730d6 855be75bd ...` — the note text is in `/tmp/n173.md` (transient; the patch file and leg logs carry the substance).

## Separate fork bug found (not fixed, out of scope for a backport)

`tests/parser/engine/test_deepseek_v4.py:1086` asserts on `p.parser_engine_config...` while line 1085 binds `parser` → `NameError: name 'p' is not defined`. Seven `TestThinkingModeConfig::test_parser_thinking_mode_matches_tokenizer_default` params fail on any tree (present in both arms of the differential). The line is also a redundant duplicate of the assertion above it and hardcodes `"REASONING"`, so it would fail the CONTENT params even after the typo is fixed. Belongs to a fork-authored fix.

## Cleanup

Removed from jetson `~/dev`: `mc171/`, `p173/`, and all `i171-*`, `i173-*`, `p173-*`, `mcprobe` scripts. Remaining there: `vllm/` (push clone, at `855be75bd`), `scratch-ledger.tgz` (ledger mirror), `pytest-libs/`, `entry173-e7cf4730d6-resolved.patch`.
