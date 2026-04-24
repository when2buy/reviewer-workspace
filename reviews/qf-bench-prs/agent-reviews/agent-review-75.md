# Review: PR #75 - var-ebacktest-coverage
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/75](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/75)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
VaR and ES backtesting pipeline: compute historical, parametric, and EWMA VaR/ES forecasts, apply Kupiec and Christoffersen backtests, then implement the Wang-Wang-Ziegel (2022) e-backtest methodology for sequential risk monitoring.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, Dockerfile
- Checked: trial results for h45, opus46, s45 (all reward=0.0)
- Analyzed: failure patterns, especially e-backtest tests

### Scorecard
- Task contract / instruction: 2/5 — e-backtest formulas incomplete
- Verifier robustness: 3/5
- Difficulty calibration: 4/5
- Model discrimination: 3/5
- Benchmark integrity: 4/5

### Findings

#### [CRITICAL] E-backtest specification is incomplete — no actual formulas given
File: [`instruction.md`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/4a59bbb/tasks/var-ebacktest-coverage/instruction.md), Steps 7

The instruction says:
- "compute the backtest e-statistic for VaR" — but gives **no formula**
- "compute the backtest e-statistic for ES using both the ES and VaR forecasts" — **no formula**
- The e-process update rule is given (`M_t *= (1 - lambda + lambda*e_t)`) but the e-statistics `e_t` themselves are undefined

The test file hints at the formulas in docstrings:
- VaR: `e_t = (1/alpha)*I{L>VaR}`
- ES: `e_t = (L-VaR)+/[alpha*(ES-VaR)]`

But these formulas are in the **test file** (not visible to agents), not in the instruction. This means the task is unsolvable from the instruction alone — agents must guess the correct e-statistic formulas from the Wang et al. paper, which is niche and not widely known.

All three models fail the e-backtest tests. The classical VaR/ES and backtesting steps (Steps 1-6) are well-specified and most models pass those tests.

#### [MAJOR] E-process values span wildly different magnitudes across models
- Haiku: VaR e-process goes to infinity (overflow)
- Opus: log10(VaR e-process historical) misses by several orders
- Sonnet: log10 values are positive instead of negative

This confirms the e-statistic formula is the root cause — different models guess different formulas and get wildly different results.

#### [MINOR] Historical VaR quantile computation underspecified
The instruction says "Use the empirical distribution of returns in the rolling window" for historical VaR, but doesn't specify the interpolation method for the quantile (e.g., `np.percentile` with which interpolation mode). Opus gets different historical VaR values than Haiku/Sonnet.

#### [MINOR] Christoffersen test failures for some models
Haiku fails Christoffersen tests — likely due to transition probability edge cases (zero-count cells in the 2×2 transition matrix). The instruction doesn't specify how to handle degenerate transition matrices.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-var-ebacktest-coverage) | 0.0 | 200s | 1,785,952in / 29,998out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-var-ebacktest-coverage) | 0.0 | 199s | 279,246in / 11,131out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-var-ebacktest-coverage) | 0.0 | 207s | 1,226,083in / 30,848out |


**Haiku key failures:**
```
FAIL: test_es_parametric_day_500
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f4a5d774f70>(0.022180139303193246, 0.02013, atol=0.001)
E        +    where <function isclose at 0x7f4a5d774f70> = np.isclose
FAIL: test_christoffersen_historical_lr
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f4a5d774f70>(140.0533035197879, 8.037, atol=0.5)
E        +    where <function isclose at 0x7f4a5d774f70> = np.isclose
```


**Opus key failures:**
```
FAIL: test_var_historical_day_300
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f94e73130f0>(0.031471, 0.02881, atol=0.001)
E        +    where <function isclose at 0x7f94e73130f0> = np.isclose
FAIL: test_var_historical_day_500
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f94e73130f0>(0.028018, 0.02574, atol=0.001)
E        +    where <function isclose at 0x7f94e73130f0> = np.isclose
```

### Summary
Classical VaR/ES pipeline (Steps 1-6) is well-specified and models perform well on those tests. The e-backtest (Step 7) is fatally underspecified — the core e-statistic formulas are missing from the instruction. This makes the task unsolvable for the e-backtest portion.

### Verdict
**不建议 Merge** — E-backtest formulas missing from instruction.md. Add explicit formulas for VaR e-statistic and ES e-statistic (currently only in test docstrings). Once added, this would be a strong "hard" task.
