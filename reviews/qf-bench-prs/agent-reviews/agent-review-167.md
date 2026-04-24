# Review: PR #167 - geometric-mean-reverting-jd
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Calibrates a geometric mean-reverting jump-diffusion model (OU + Poisson jumps in log-space) to FRED 10Y Treasury data. Computes conditional moments analytically, verifies with Monte Carlo, and produces forward rate curves.

### What I Did to Review This
- Read: instruction.md, test_outputs.py, solve.sh, trial results
- Checked OU calibration, jump detection, conditional moment formulas
- Reviewed model discrimination

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 4/5
- Difficulty calibration: 4/5
- Model discrimination: 3/5 — Only Opus passes
- Benchmark integrity: 4/5

### Findings

#### [MINOR] Good discrimination — Opus-only pass
Opus (1.0) passes all 34 tests. Haiku (0.0) fails on variance bounded by stationary, MC var accuracy, and summary MC accuracy — suggesting its conditional variance formula or MC implementation is wrong. Sonnet (0.0) fails on similar variance/MC tests. Only Opus gets the variance formulas right.

#### [MINOR] Correct financial framework
The OU calibration via OLS regression (X_{t+1} = a + b·X_t + ε, then invert to κ, θ, σ) is standard and correct. Jump detection via 3σ threshold on standardized residuals is a common approach. The conditional moment formulas including jump contributions are correct.

#### [MINOR] Stationary variance test is a good constraint
`test_variance_bounded_by_stationary` checks Var(X_τ) ≤ stationary_var + 0.01, which is mathematically correct for OU processes (variance is monotonically increasing to stationary). This catches errors in the variance formula.

#### [MINOR] Forward curve JD vs OU comparison
`test_jd_ou_close` checks that jump-diffusion and pure OU forward rates differ by < 10%, which is reasonable for a few jumps per year in interest rates.

#### [NIT] MC relative error tolerance
MC mean error < 5%, var error < 15% — reasonable for 10,000 paths with jumps.

### Summary
Well-designed task testing a non-trivial stochastic process (OU + jumps). Correct financial mathematics throughout. Good model discrimination where the variance formulas separate Opus from the others.

### Verdict
**建议 Merge** — Correct, well-calibrated, good discrimination on a genuinely difficult quantitative task.
