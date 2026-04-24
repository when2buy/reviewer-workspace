# Review: PR #164 - dupire-local-vol
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Extracts the Dupire local volatility surface from SPY option market prices using SVI smoothing. Involves implied vol extraction, SVI calibration per expiry, and Dupire formula application with numerical derivatives.

### What I Did to Review This
- Read: instruction.md, test_outputs.py (first 100 lines), trial results
- Checked financial correctness of Dupire formula
- Reviewed model discrimination

### Scorecard
- Task contract / instruction: 3/5
- Verifier robustness: 2/5
- Difficulty calibration: 2/5 — All models fail (0/0/0)
- Model discrimination: 1/5 — No discrimination
- Benchmark integrity: 3/5

### Findings

#### [CRITICAL] All three models score 0.0 — task is likely too hard or underspecified
- Haiku: 5 failures (n_expiries, n_options_filtered, expiry_dates_list, local_vol positivity, ATM consistency)
- Opus: 5 failures — **all file existence tests fail** (calibration.json doesn't exist). Opus couldn't even produce output files.
- Sonnet: 5 failures (n_options_filtered, SVI a_positive, local_vol ATM consistency, summary values)

When even Opus can't produce the basic output files, either the task specification is ambiguous, the data pipeline is too fragile, or there's a hidden dependency that trips all models.

#### [MAJOR] Complex data pipeline with fragile filtering
The task requires filtering options by volume > 10, selecting OTM only, converting puts via parity, then fitting SVI per expiry. Multiple steps where agents can diverge from the oracle's expectations. The `spy_options.csv` data format isn't shown in the instruction — agents must infer column names.

#### [MAJOR] Verifier tests pin exact counts (n_expiries between 4-6, n_options_filtered > 0)
These tests are highly sensitive to the exact data filtering pipeline. Different reasonable approaches to filtering could yield different expiry counts.

#### [MINOR] SVI calibration is inherently fragile
SVI fitting with scipy.optimize.minimize can converge to different local minima depending on initialization. The test `test_svi_a_positive` assumes a > 0 which may not hold for all valid SVI fits.

### Summary
All three models fail, including Opus failing to even produce output files. The task combines data engineering (options filtering), numerical optimization (SVI), and PDE computation (Dupire) in a way that is too fragile for a benchmark. The complex multi-step pipeline has too many points of failure.

### Verdict
**不建议 Merge** — Zero model pass rate indicates the task is either underspecified or too fragile. Even Opus cannot produce basic outputs. Needs significant simplification or clearer specification of data format and filtering expectations.
