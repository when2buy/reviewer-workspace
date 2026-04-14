---
name: qfbench-review
description: Review QF-Bench or QuantitativeFinance-Bench pull requests, task diffs, benchmark task folders, and review drafts. Use when reviewing a QF-Bench PR, a new benchmark task, verifier/tests/instruction quality, difficulty calibration, anti-cheat integrity, skill leakage, or when rewriting review comments for this project into the house style.
---

# QFBench Review

Review QF-Bench like a benchmark reviewer, not a generic code reviewer.

Prioritize benchmark correctness and integrity over style. A task can have clean code and still be a bad benchmark item.

## Read these references first

Read both before writing the review:
- `references/qfbench-review-checklist.md`
- `references/review-template.md`

If the PR changes repository guidance or task standards, also read:
- `/home/node/.openclaw/workspace-reviewer/repo/docs/task_review_guideline.md`

## Core review posture

Judge the PR on these axes first:
1. Task correctness and specification quality
2. Benchmark integrity and anti-cheat resistance
3. Difficulty calibration and model discrimination
4. Oracle/verifier robustness and determinism
5. Data realism and provenance
6. Review hygiene and PR scope
7. Code quality and maintainability

Do not stop at “tests pass”. In this project, passing tests can still hide:
- under-specified instructions
- pinned-answer verifiers
- solution leakage through skills or tests
- difficulty inflation
- benchmark contamination risks

## What to do during review

1. Explain the PR in plain language first.
   - Assume the reader may not know the financial method.
   - State what the task is trying to make an agent do.
   - State why it matters for the benchmark.

2. Include a "What I did to review this" section.
   - List files inspected.
   - List commands or runs performed.
   - Note any hand-checks, recomputation, or comparisons.
   - If you used sub-agents, say which ones and for what.

3. Prefer execution over speculation when feasible.
   - Run the oracle or verifier when access and time allow.
   - Check whether reward-writing logic is robust.
   - Inspect whether tests recompute from inputs or just pin constants.

4. Review at the benchmark level, not just the file level.
   - Does the instruction fully specify the contract?
   - Do tests verify the right thing?
   - Can an agent game the task without doing the intended work?
   - Does the claimed difficulty match the evidence?

5. Be explicit about severity.
   - `[CRITICAL]` blocks merge.
   - `[MAJOR]` should be fixed unless there is a strong reason not to.
   - `[MINOR]` is worthwhile but non-blocking.
   - `[NIT]` is optional.

## QFBench-specific red flags

Treat these as deep-review triggers:
- `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `solution/solve.*`, `environment/Dockerfile`
- any task skill under `environment/skills/*/SKILL.md`
- exact expected-value dicts covering large fractions of the final answer
- hidden canonical conventions not stated in the instruction
- brittle `set -euo pipefail` plus post-hoc `$?` reward writing
- PRs that bundle multiple unrelated tasks
- evidence that only weak models fail while strong models all pass easily
- tasks labeled hard with weak failure evidence
- synthetic or toy datasets
- instructions that mention skills or prescribe the solution path

## Required review output shape

Follow the template in `references/review-template.md`.

The review should usually contain:
- title / PR identifier
- plain-language explanation of the PR
- what you did to review it
- scorecard across benchmark dimensions
- findings with severity labels
- concise summary
- final verdict: `APPROVE`, `REQUEST CHANGES`, or `NEEDS DISCUSSION`

## Tone

Be direct and concrete.
Do not pad.
Do not praise weak benchmark work just because the idea is interesting.
If something is good, say so briefly.
If something is risky, explain why and what should change.

## Delivery notes

If posting to GitHub, write in English.
If reviewing in chat, English is still preferred unless explicitly asked otherwise.

When the review is based on actual execution, say that clearly. It materially increases credibility.
