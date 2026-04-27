# Review: PR #61 - Pairs Trading Cointegration
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/61](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/61)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Build a complete pairs trading pipeline for XOM/CVX: OLS hedge ratio, Engle-Granger ADF test, rolling z-score signals, backtest with transaction costs, and performance metrics.

### What I Did to Review This
- Read: instruction.md, task.toml, solution/solve.py, test_outputs.py, test.sh, Dockerfile
- Reviewed trial failures for all three models
- Analyzed failure patterns to determine if task or agent is at fault

### Trial Results
| Model | Reward | Key Failures |
|-------|--------|-------------|
| Haiku 4.5 | 0.0 | total_return, ann_vol, max_drawdown, xom_shares sign |
| Opus 4.6 | 0.0 | max_drawdown sign (negative vs positive) |
| Sonnet 4.5 | 0.0 | xom_shares sign |

### Scorecard
- Task contract / instruction: 3/5
- Verifier robustness: 2/5
- Difficulty calibration: N/A (all fail)
- Model discrimination: 1/5
- Benchmark integrity: 3/5

### Findings

#### [CRITICAL] test_trades_csv_xom_shares_consistent has a sign ambiguity bug
The test asserts `xom_shares == 1000` for all entries. But for `enter_short` trades, the agent reasonably reports `xom_shares = -1000` (negative = short). The instruction says "Short spread = sell 1000 shares XOM" — whether xom_shares should be +1000 (unsigned count) or -1000 (signed position) is ambiguous. Both Haiku and Sonnet fail on this test. The instruction should clarify whether trade records use signed or unsigned share counts.

#### [CRITICAL] max_drawdown sign convention ambiguity
Opus 4.6 reports `max_drawdown = -0.029025` (negative convention, meaning peak-to-trough loss) while the expected value is `+0.029076` (positive convention). The instruction defines max_drawdown as "maximum peak-to-trough drawdown of equity curve" which conventionally is positive. The agent's value is numerically close but wrong sign. This is a specification clarity issue — the instruction should explicitly state "max_drawdown is always non-negative."

#### [MAJOR] All three models fail — 0% pass rate
When all frontier models fail, the question is whether the task is too hard or the verifier is too strict. In this case, Opus gets 21/22 tests right (only max_drawdown sign), and Sonnet gets 21/22 (only xom_shares sign). These are specification ambiguities, not fundamental capability failures.

#### [MINOR] Hardcoded expected values in verifier
The test pins exact values like `num_trades=38`, `total_return=-0.003271`, `hit_rate=0.526316` etc. These are correct given the reference solution but make the task fragile to minor implementation differences (e.g., tie-breaking in signal evaluation, floating point accumulation order).

#### [MINOR] Complex multi-step task is good for benchmarking
The pipeline (data cleaning → OLS → ADF → z-score → backtest → metrics) is a realistic quant workflow. The complexity is appropriate.

### Summary
Ambitious and realistic pairs trading task, but two specification ambiguities cause all models to fail: (1) signed vs unsigned share counts in trades.csv, and (2) max_drawdown sign convention. These are verifier bugs, not model capability issues. Opus nearly passes (1 test off) and Sonnet is close too.

### Verdict
**不建议 Merge**

Two verifier issues need fixing:
1. `test_trades_csv_xom_shares_consistent` should check `abs(xom_shares) == 1000` or instruction must specify unsigned
2. `test_results_metric[max_drawdown]` should accept both positive and negative convention, or instruction must explicitly specify positive

After these fixes, Opus and Sonnet would likely pass, giving good discrimination.
