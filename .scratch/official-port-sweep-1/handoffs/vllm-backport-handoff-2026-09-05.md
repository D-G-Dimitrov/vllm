# Handoff — official→mitaka/backport PR grind (sweep-1)
Date: 2026-09-05 ~22:15 local. Written because the orchestrator session degraded (token pressure + a garbled reply). Verify ground truth before acting — this doc may lag the repo by minutes.

## Mission (unchanged)
Port all **317 official vLLM PRs** (git range `c01b50e390..d4d703caf9`, strictly oldest-first) into `mitaka/backport`. Each PR individually PICKED (`git cherry-pick -x`) or SKIPPED with recorded reason. Append-only (never rebase). Push after every landed PR. Batch = 10; **standing order: grind continuously, no "go" between rounds**; halt only for user decisions (behavior-changing forks) — auto-land rule below excepted.

## STATE RIGHT NOW — clean, nothing in flight (updated after handoff write)
- **80/317 decided+pushed.** origin == jetson == `8cf96057b` (item 80, `7a100bb617` CI yaml). Tree clean, NO sequencer/cherry-pick in progress (the previously in-flight item-81 attempt was aborted per user decision; redo it fresh).
- Item 81 redo note: `7ab2923489` (Flashinfer 0.6.18 #54313) conflicted in `docker/Dockerfile` + `docker/versions.json` (wtdcode pins vs official flashinfer bump). Expected: take official flashinfer version; keep wtdcode pins/image tags where disjoint. Wtdcode-FUNCTIONAL pin change → abort + decision card.
- Queue strict order from 81: 82 `c92b29a1d4` (isend non-blocking #49274, +282, CONFLICT forecast — `vllm/distributed/*` wtdcode-hot; packet+oracle if wtdcode lines involved) → 83 `5707355209` (FlashInfer sparse MLA BLHNC fix, OK forecast) → 84+ from `issues/03-pr-grind.md` first unchecked (skip 80/81/82/83 as handled).

## Canonical artifacts (do not duplicate; read them)
- Repo (orchestrator, GitHub creds): `/Users/mitaka/Projects/PyCharm/vllm-mitaka`
- State dir: `.scratch/official-port-sweep-1/` — `map.md` (Decision log incl. FORK #1/#2 + revisit triggers + auto-land rule), `issues/03-pr-grind.md` (checklist `- [ ] <sha> <title>`, NO numeric prefix), `outcomes.log.md` (numbered entries), `heat-map-raw.txt` (forecasts `STATUS|40char-sha|title`).
- Fork decision log + auto-land rule live in `map.md` — the ONLY source of truth for those.

## Environment facts
- **All repo/docker commands run on jetson via `ssh jetson-222 '...'`** (mitaka@192.168.1.222, repo `~/dev/vllm`, branch `mitaka/backport`). NEVER local git/docker on Mac except the orchestrator push flow below.
- GPU serving :8000/:8001 on 222 **SACRED** (also user's container `qwen38-flash-next` `vllm/vllm-openai:qwen38-flash-next`, Up since ~19:00 — do not stop). Validation containers always `--rm -e CUDA_VISIBLE_DEVICES=""`.
- **Worker/oracle degradation**: model server serving pi subagents shares the Jetson stack; since ~user restarted qwen38-flash-next, subagent calls die/truncate repeatedly (3+ in one batch; one fabricated a sha `499173f5f` that never existed — always verify). **Workaround in effect: orchestrator (me/next agent) performs picks+validation directly via ssh** — works fine, keep doing that while degradation persists; keep `subagent {agent: oracle}` for behavior-delta reviews when it recovers, and reconcile any worker output against `git log` on jetson before trusting it.
- Shell tool caps ~30s: pass `timeoutMs`, launch containers `nohup ... > /tmp/x.log 2>&1 &` then poll with short ssh greps.
- Docker validation recipe: image `mitakad/vllm:0.29.0.dev0-r39.2.tegra-aarch64-cp312-cu132-24.04-commit.d4d703c`, `--runtime nvidia --network host -v ~/dev/vllm:/workspace -w /workspace -e CUDA_VISIBLE_DEVICES=""`; inner: `source /opt/venv/bin/activate`; copy `.so`s from site-packages into /workspace; `pip install -q pytest tblib`.
- Base-compare for any test failure: `git archive <parent> | tar -x -C /tmp/x` + copy `vllm/version.py` in, mount `/tmp/x:/base`, run same suite; `sudo rm -rf` after (containers write root-owned files).
- Known-base CPU failure families (NOT regressions; fail-set must be IDENTICAL vs parent): test_mem 10f env family; test_config 11f; mooncake store_sending_thread trio; 2 wtdcode PP tests; video pynvvideocodec×4 + parity[torchcodec]; multimodal test_cache 4f (shm); ~61 GPU-only spec_decode; misc model-download/fixture gaps. Record new families in outcomes.

## Push flow (orchestrator-side, Mac)
```
cd /Users/mitaka/Projects/PyCharm/vllm-mitaka
git ls-remote origin refs/heads/mitaka/backport | cut -c1-9   # expected tip
git fetch -q jetson-222:dev/vllm mitaka/backport && git merge --ff-only FETCH_HEAD
git push -q origin mitaka/backport && git ls-remote origin refs/heads/mitaka/backport
```
Then append `outcomes.log.md` entry `<n>. <official9> -> <new9> PICKED+PUSHED (area #PR; notes/tests)` and tick checklist `- [ ]`→`- [x]` for that sha.

## Decision rules (short form; full text in map.md)
- Trivial conflict outside wtdcode code → hand-merge + document. Conflict touching wtdcode-functional lines → abort, packet, fresh oracle review, A/B/C card **with explicit recommendation** to user.
- **Auto-land rule (ON)**: wtdcode conflict may land without halt iff composition is mechanical AND fresh oracle returns UNCONDITIONAL PASS (zero behavior delta for DSV4/qwen4_exp/GLM-5.3-Flash). Behavior-changing forks ALWAYS halt (e.g. #56 gumbel did halt, user approved; default `temperature=1.0` means spec-decode samples shift — landed, fork noted).
- Every behavior fork → map.md Decision-log entry (basis, revisit trigger, rollback).
- Model mega-conflicts ahead: ~item 126 Qwen `e126687a9a`, ~353 GLM `98ed0856f3` — need user ratification before 126.

## Open items to raise with user (when convenient, not blocking)
1. Shadow writer `D-G-Dimitrov` pushed nothing since item 27; Q2 card (branch protection) recommended but user hasn't acted. Any content divergence on origin ⇒ halt & investigate.
2. Their qwen38-flash-next container correlates with subagent-server degradation (explained to user; they chose to keep it — orchestrator-direct mode mitigates).
3. Item 62 (`d49bffe02`) flagged `rust-rebuild-needed` — Rust frontend binaries in the image refresh at next image cut; note for image policy.

## Suggested skills
- `official-port-grind-loop` — now a USER skill at `~/.pi/agent/skills/mitaka-skills/official-port-grind-loop/SKILL.md` (moved from project scope 2026-09-06; old project copy deleted). **Who uses it: the ORCHESTRATOR/continuation agent, not the human, not the dispatched workers.** The human doesn't invoke it; workers get their briefs inline (task text), never the skill. The orchestrator agent should READ it first (worker brief template, reconcile, reporting contract) and follow it to run rounds.
- `enforce-subagent-fanout-concurrency` (global) — if/when resuming parallel worker dispatch.
- `pi-subagents` — workflow syntax for oracle/worker re-dispatch after server recovery.
- `diagnosing-bugs` / `systematic-debugging` — if a real regression (non-base-identical fail) appears.

## Verification checklist for the fresh agent
1. `ssh jetson-222 'cd ~/dev/vllm && git status && git log --oneline -3'` + `git ls-remote origin mitaka/backport` → expect both `8cf96057b`, clean tree.
2. Redo item 81 fresh (conflict expectations above), then 82 (expect conflict packet), 83, onward oldest-first; verify origin tip after every push.
3. Read `official-port-grind-loop` (user skill v3) — it now encodes orchestrator-direct mode and the auto-land gate.
