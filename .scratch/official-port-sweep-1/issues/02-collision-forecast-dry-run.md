# Collision forecast dry-run (throwaway)

Type: task
Status: resolved

## Question

Produce the grind's **collision heat-map**: for each of the 317 official PRs (oldest-first), will `git cherry-pick` apply cleanly onto `mitaka/backport`, and if not, which files conflict (and which of those are wtdcode-patched)? Also pre-tag dependency-impact PRs. Measurement only — `mitaka/backport` is never modified.

Method (ratified 2026-09-04, replaces the earlier rebase-replay idea, which measured a different operation than cherry-picking): a scripted **cumulative cherry-pick dry-run** on a throwaway branch — the exact operation the grind performs.

Procedure (run on the Mac in `~/Projects/PyCharm/vllm-mitaka`, pure git, no builds):

1. `git worktree add /tmp/sweep-forecast -b forecast/throwaway mitaka/backport`.
2. For each commit in `git rev-list --reverse c01b50e390..d4d703caf9`: attempt `git cherry-pick -x <sha>`.
   - Clean → keep it committed (later commits are tested on top of applied predecessors, mirroring the real grind).
   - Conflict → record: official sha + subject, conflicted files, which of them are in the wtdcode surface (`git diff --name-only c01b50e390 3bec275739`), then `git cherry-pick --abort` (prior picks persist) and continue.
   - Note: skipping conflicted commits approximates hand-merging; later conflicts may differ slightly from the real grind — acceptable for triage.
3. Produce the heat-map: per-PR outcome (clean / conflict + files / blocked-by-<earlier-skipped-sha>), ranked worst-offender wtdcode areas, count of hot PRs needing the semantic already-present review, and an `env-impact` tag on every PR touching `requirements/`, `pyproject.toml`, `setup.py`, `cmake/`.
4. Discard everything: remove the worktree and the branch; verify `git status` clean and no stray branches.

The Answer must contain the full heat-map — the grind ticket's per-PR collision review cites it.

## Answer

Resolved 2026-09-04 via the scripted cumulative cherry-pick dry-run (one bash loop, ~317 picks, pure git).

**Counts: OK=272 CONFLICT=45 EMPTY=0 · wtdcode-hot conflicts: 37 · env-impact PRs: 12.**

Full heat-map: [heat-map.md](../heat-map.md) (summary + 317-row grind table + worst offenders + env list); raw outcomes: [heat-map-raw.txt](../heat-map-raw.txt).

Key findings:
- **The two mega-conflicts are the two target models**: official's native `[Model] Support Qwen3.8-Flash-Next` (e126687a9a, #53896 — grind item 126) and `[Model] add GLM-5.3-Flash support` (98ed0856f3, #53906 — item 353) each conflict with **31 files** against wtdcode's own implementations. This is the conflict-resolution-playbook decision in the map's fog, now concrete; the user should rule on it before item 126.
- Top conflict magnet: `vllm/model_executor/warmup/kernel_warmup.py` (6 PRs); then `tests/models/qwen4_exp/test_ple.py` (4, incl. the cutoff PR d4d703caf9 itself); `vllm/config/vllm.py`, nixl base_worker, `sparse_attn_indexer.py`, `kv_cache_interface.py`, `gpu_worker.py` (3 each).
- **Env-impact: 12 PRs** — incl. Flashinfer → 0.6.18 (#54313) and Transformers → 5.16.1 (#53905); each needs an image/wheel rebuild decision when landed.
- EMPTY=0: nothing resolved as already-applied in the cumulative sweep — consistent with the oracle's warning that wtdcode's equivalents are re-implementations, only catchable by the semantic check.
