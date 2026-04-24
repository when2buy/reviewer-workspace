# Review: PR #46 - ou-pairs-trading
Reviewer: Grim 🔍 | Date: 2026-04-23

### What This PR Does
Agent fits an Ornstein-Uhlenbeck process to a pairs spread time series via OLS, estimates OU parameters (theta, mu, sigma, half-life), computes z-scores, and runs a mean-reversion trading strategy with Sharpe ratio and max drawdown.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py, test.sh, solution/solve.py
- Noted: No Dockerfile, no trial results
- Checked OU estimation correctness, test coverage

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 3/5
- Difficulty calibration: N/A (no trials)
- Benchmark integrity / anti-cheating: 3/5
- Financial correctness: 4/5

### Findings

#### [CRITICAL] Missing Dockerfile
No environment/Dockerfile. Task cannot be run. No trial data.

#### [MAJOR] Tests are structural only — no pinned values
Tests check theta > 0, half_life consistency with theta, num_trades > 0, max_drawdown <= 0. All are structural/sanity checks. An agent could produce wildly wrong OU parameters and still pass as long as they're self-consistent. No oracle pinning of expected parameter ranges from the synthetic data.

#### [MAJOR] max_drawdown sign convention ambiguous
Instruction says "compute maximum drawdown" but doesn't specify sign convention. Test requires `max_drawdown <= 0`. Solution computes `drawdown.min()` which is negative. This is a common source of confusion — instruction should be explicit.

#### [MINOR] Solution OU estimation is correct
OLS on dX = a + b*X_lag is the standard discrete OU estimation. Annualization via dt=1/252 is correct. Half-life formula is consistent.

#### [MINOR] Synthetic data — acceptable for OU but reduces realism
Instruction says "already generated as synthetic OU process data." This is fine for parameter estimation testing but limits the benchmark's real-world relevance.

### Summary
Sound quant task with correct OU methodology and reasonable trading strategy. Blocked by missing Dockerfile. Tests lack oracle pinning — they verify internal consistency but not correctness against known-good values.

### Verdict
**不建议 Merge**

Missing Dockerfile is a blocker. Additionally, tests need oracle-pinned parameter ranges to be meaningful as a benchmark.
