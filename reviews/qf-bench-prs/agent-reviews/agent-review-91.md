# Review: PR #91 - polars-api-migration
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/91](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/91)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Migrate a Polars 0.x data processing pipeline to Polars 1.x API. Agent must update deprecated API calls, avoid anti-patterns (PolarsInefficientMapWarning, DeprecationWarning), and produce correct output across 25 pipeline steps.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, environment/Dockerfile
- Reviewed trial results: ALL THREE FAIL with Docker build error (wrong base image)

### Scorecard
- Task contract / instruction: 4/5 — Clear objective, good constraints (no hardcoding, warning checks)
- Verifier robustness: 4/5 — Tests check both output correctness and code quality (warning absence)
- Difficulty calibration: N/A — No trials completed
- Benchmark integrity: 3/5 — Test uses reference CSVs in /tests/references/ (hidden), plus code quality checks

### Findings

#### [CRITICAL] Dockerfile uses wrong base image — all trials fail to build
File: [`environment/Dockerfile`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/8e24f96/tasks/polars-api-migration/environment/Dockerfile)
Same issue as PR#89: uses `quantitative-finance-bench-sandbox:latest` instead of the correct base image. All three trials fail with Docker build errors.

#### [MINOR] Category "debug-migration" is unusual
File: [`task.toml`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/8e24f96/tasks/polars-api-migration/task.toml)
This is more of a software engineering task than a quantitative finance task. It tests Polars API knowledge rather than financial reasoning. May not fit the QF-Bench focus.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | error reading | — | — |
| Opus 4.6 | error reading | — | — |
| Sonnet 4.5 | error reading | — | — |

### Summary
Cannot be evaluated due to Docker build failure. The task concept (API migration) is more software engineering than quantitative finance. Needs correct base image.

### Verdict
**不建议 Merge**

Blocker: Dockerfile base image doesn't exist. Additionally, task may not fit QF-Bench scope (software engineering rather than quantitative finance).
