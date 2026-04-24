# Review: PR #48 - CIR Calibration
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/48](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/48)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Calibrate a Cox-Ingersoll-Ross (CIR) interest rate model to historical short rate data using OLS regression, check the Feller condition, and compute analytical zero-coupon bond prices.

### What I Did to Review This
- Read: instruction.md, task.toml, solution/solve.py, test_outputs.py, test.sh
- Checked environment directory (no Dockerfile found)
- Checked trial results (no result.json for any model)
- Verified CIR OLS discretization and ZCB formula correctness

### Trial Results
| Model | Reward |
|-------|--------|
| Haiku 4.5 | N/A (no results) |
| Opus 4.6 | N/A (no results) |
| Sonnet 4.5 | N/A (no results) |

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 3/5
- Difficulty calibration: N/A (no trial data)
- Model discrimination: N/A
- Benchmark integrity: 3/5
- Financial correctness: 4/5

### Findings

#### [CRITICAL] No Dockerfile — environment directory contains only data
The `environment/` directory has a `data/` subfolder with `short_rates.csv` but no Dockerfile. This means the task cannot build its sandbox environment. All three trials produced no results, likely because the environment build failed.

#### [CRITICAL] No trial results available
All three model trials have no result.json, making it impossible to assess difficulty calibration or model discrimination.

#### [MAJOR] Solution provided but not verified
solve.py exists and implements the OLS approach correctly (dividing by sqrt(r_t) to get the regression form). The CIR ZCB formula implementation looks correct. However, without trial runs, this is unverified.

#### [MINOR] Tests are property-based only — no reference comparison
Tests check: positive parameters, ZCB in (0,1), strictly decreasing ZCB prices, Feller condition consistency, positive forward rates. No exact value comparison. This is appropriate for a calibration task where exact values depend on data, but makes the verifier lenient.

#### [MINOR] OLS sigma estimation uses ddof=2
solve.py uses `np.std(residuals, ddof=2)` which is unconventional. Standard practice would be ddof=0 or ddof=1 for residual std. This may not matter much with 500 data points but is technically incorrect (ddof should correspond to number of estimated parameters, which is 2, so ddof=2 is actually the correct choice for unbiased residual variance).

#### [NIT] test.sh sources `$HOME/.local/bin/env` instead of adding to PATH
Different pattern from other tasks but functionally equivalent.

### Summary
Financially sound CIR calibration task with correct OLS discretization approach. However, the missing Dockerfile is a blocker — the task cannot run. No trial data exists to validate.

### Verdict
**不建议 Merge**

Missing Dockerfile prevents environment build. No trial data available. Must add Dockerfile and re-run trials before merge.
