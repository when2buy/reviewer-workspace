# Review: PR #106 - etf-overlap-redemption-pressure
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/106](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/106)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Parse SPY and XLK daily holdings Excel files plus SPDR product data, compute fund-level metrics, build a curated universe (top 30 per fund), apply redemption scenarios, and produce pressure decomposition and rankings.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked trial results: H45=N/A, Opus46=N/A, S45=N/A (all Docker build failures)

### Scorecard
- Task contract / instruction: 4/5 — clear with explicit formulas and sort rules
- Verifier robustness: 5/5 — exact reference matching with recomputed identities
- Difficulty calibration: N/A — cannot assess
- Benchmark integrity: 3/5 — reference data contains full answers
- Data realism: 5/5 — real SPDR holdings and product data

### Findings

#### [CRITICAL] Docker build fails — base image mismatch
File: [`environment/Dockerfile`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/a8a93f4/tasks/etf-overlap-redemption-pressure/environment/Dockerfile)

Uses `FROM quantitative-finance-bench-sandbox:latest` but test environment has `finance-bench-sandbox:latest`. All trials failed.

#### [MINOR] Dockerfile installs openpyxl redundantly
File: [`environment/Dockerfile`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/a8a93f4/tasks/etf-overlap-redemption-pressure/environment/Dockerfile)

`RUN pip install --no-cache-dir pandas>=2.2 openpyxl>=3.1 numpy>=1.26` — if the base image already has pandas/numpy, this may conflict. The version constraints use `>=` which is unpinned.

#### [MINOR] Task is well-scoped for "medium" difficulty
The ETF overlap and redemption pressure analytics are standard portfolio analysis computations. The main challenge is parsing the SPDR Excel files correctly (dollar fields like "$653,201.93 M").


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-etf-overlap-redemption-pressure) | error reading | — | — |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-etf-overlap-redemption-pressure) | error reading | — | — |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-etf-overlap-redemption-pressure) | error reading | — | — |

### Summary
Well-designed ETF market-structure task with real holdings data. Clean specification and robust verifier. Cannot be evaluated due to Docker build failure.

### Verdict
**不建议 Merge**

Docker build fails for all models due to base image mismatch. Fix to `finance-bench-sandbox:latest`, pin dependency versions, and re-run trials.
