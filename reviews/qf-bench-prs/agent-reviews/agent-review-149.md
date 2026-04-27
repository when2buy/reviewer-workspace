# Review: PR #149 - liquidity-var-backtest
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/149](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/149)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
A "medium" risk-management task: build a comprehensive risk report for a rates/FX portfolio including historical VaR, EWMA parametric VaR, liquidity add-ons, stress testing, rolling backtest, component VaR, filtered historical simulation, rates PCA, and coverage diagnostics. Uses real FRED data.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`
- Checked trial results and stdout for all models
- Reviewed expected values in test file

### Trial Results
| Model | Reward |
|-------|--------|
| Haiku 4.5 | ERROR (RewardFileNotFoundError) |
| Opus 4.6 | ERROR (RewardFileNotFoundError) |
| Sonnet 4.5 | ERROR (RewardFileNotFoundError) |

### Scorecard
- Task contract / instruction: 5/5 — Extremely comprehensive, explicit formulas for every calculation
- Verifier robustness: 3/5 — All expected values hardcoded in test_outputs.py with rtol=1e-6
- Difficulty calibration: N/A — Cannot assess; verifier broken
- Benchmark integrity: 3/5 — Massive amount of expected values in test file (all numeric results, liquidity breakdown, backtest values, stress results, component VaR, FHS values, PCA values) — effectively the full answer

### Findings

#### [CRITICAL] Verifier broken — RewardFileNotFoundError for all models
Opus46 stdout shows: `bash: line 1: /tests/test.sh: cannot execute: required file not found`. The test.sh exists in the task but may not be properly copied into the Docker image, or has a shebang/encoding issue.

Looking at test.sh — it doesn't have `mkdir -p /logs/verifier` before writing the reward file. Compare with working tasks (PR#137, #139, etc.) which do `mkdir -p /logs/verifier`. This task's test.sh is missing that, and the reward file path is just `/logs/verifier/reward.txt` without ensuring the directory exists.

Wait — actually the test.sh doesn't even have the reward writing logic properly. The `if [ $? -eq 0 ]` block exists but the directory may not. More importantly, the "cannot execute" error suggests the file itself isn't being found at `/tests/test.sh`.

#### [MAJOR] Test file contains complete expected output
`test_outputs.py` has ~200 lines of hardcoded expected values covering every single output metric. This is essentially the full answer key. While agents shouldn't access `/tests/`, the sheer volume of pinned values means any solution must match to rtol=1e-6, which is extremely tight.

#### [MAJOR] Task scope is enormous for "medium"
The instruction requires: data cleaning, historical VaR, ES, EWMA parametric VaR, liquidity add-ons (6 factors), stress testing (4 scenarios), rolling backtest with Kupiec/Christoffersen tests, component VaR, filtered historical simulation, rates PCA attribution, and diagnostics. This is more like a "hard" task.

#### [MINOR] Good financial content
Proper EWMA covariance update, liquidity horizon scaling, Kupiec POF test, Christoffersen independence test, PCA on rates — all standard risk management methodology, well-specified.

### Summary
Comprehensive risk management task with excellent financial content. However, the verifier is broken (cannot execute test.sh), and the task scope seems too large for "medium." The amount of hardcoded expected values in the test file is a concern.

### Verdict
**不建议 Merge** — Verifier broken; all trials error out. Fix the test infrastructure, verify difficulty label, and re-run.
