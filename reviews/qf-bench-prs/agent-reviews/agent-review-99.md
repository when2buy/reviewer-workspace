# Review: PR #99 - 13f-amendment-aware-crowding
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/99](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/99)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Reconstruct effective long-share portfolios from SEC Form 13F filings with amendment resolution (RESTATEMENT vs NEW HOLDINGS), then compute concentration (HHI), turnover, pairwise overlap, and crowded securities analytics.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `solution/solve.py`, `environment/Dockerfile`
- Checked trial results: H45=N/A, Opus46=N/A, S45=N/A (all Docker build failures)
- Verified reference data exists in `tests/reference_data/`

### Scorecard
- Task contract / instruction: 4/5 — thorough but very long specification
- Verifier robustness: 4/5 — reference-based comparison with semantic tolerance
- Difficulty calibration: N/A — cannot assess, no successful runs
- Benchmark integrity: 3/5 — reference data in tests/ dir may leak answers
- Data realism: 5/5 — real SEC 13F data

### Findings

#### [CRITICAL] Docker build fails — base image mismatch
File: [`environment/Dockerfile`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/75d5f1a/tasks/13f-amendment-aware-crowding/environment/Dockerfile)

Uses `FROM quantitative-finance-bench-sandbox:latest` but the test environment only has `finance-bench-sandbox:latest`. All three model trials failed at the Docker compose stage. The task cannot be evaluated.

**Fix:** Change base image to `finance-bench-sandbox:latest` or ensure the `quantitative-finance-bench-sandbox` image is available.

#### [MAJOR] Verifier relies heavily on exact reference matching
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/75d5f1a/tasks/13f-amendment-aware-crowding/tests/test_outputs.py)

The test loads reference CSVs from `tests/reference_data/` and does `pd.testing.assert_frame_equal` or close numeric comparisons. This is robust for correctness but means the verifier contains the full canonical answer. Under Harbor assumptions tests are not visible to agents, so this is acceptable, but the reference data is extensive (8 files).

#### [MAJOR] Task is very complex — 8 output files, detailed amendment logic
File: [`instruction.md`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/75d5f1a/tasks/13f-amendment-aware-crowding/instruction.md)

The specification is ~200 lines covering amendment resolution, cleaning audit, portfolio analytics, and cross-sectional overlap. The expert time estimate of 75 min seems optimistic for a task requiring correct SEC filing parsing, amendment ordering, and multiple analytics. This might be better classified as "hard."

#### [MINOR] solve.py is partial — only loads and prepares data
The oracle solution is truncated at the data preparation stage.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | error reading | — | — |
| Opus 4.6 | error reading | — | — |
| Sonnet 4.5 | error reading | — | — |

### Summary
The task is well-conceived and tests a real quant workflow (13F amendment-aware portfolio reconstruction). However, it cannot be evaluated because the Docker base image doesn't exist in the test environment. Fix the base image and re-run trials before merge.

### Verdict
**不建议 Merge**

Docker build fails for all three models due to base image mismatch (`quantitative-finance-bench-sandbox` vs `finance-bench-sandbox`). Cannot assess difficulty calibration or model discrimination without working trials.
