# Review: PR #124 - pairs-cointegration-kalman
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/124](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/124)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Build a complete pairs trading pipeline: clean price data, run Engle-Granger cointegration on 6 pairs, estimate time-varying hedge ratio via scalar Kalman filter on PAIR_1, generate z-score trading signals, and backtest a mean-reversion strategy. Report performance metrics and half-life.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `solution/solve.sh`, `tests/test_outputs.py`, `tests/verifier.py`, `tests/reference_data/expected.json`, `tests/reference_data/checkpoints.json`
- Checked: oracle correctness, ADF implementation, Kalman filter equations, backtest logic, tolerance calibration
- Reviewed trial outputs: H45 FAILED, Opus46 FAILED, S45 FAILED — all three models fail

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 3/5 |
| Verifier robustness | 3/5 |
| Difficulty calibration | 2/5 |
| Model discrimination | 1/5 |
| Benchmark integrity | 4/5 |

### Findings

#### [CRITICAL] All three frontier models fail — task may be over-specified or have oracle issues
All trials (H45, Opus46, S45) produce FAILED results. The provided scores (H:0.38, O:0.79, S:0.71) suggest partial credit in some scoring system, but the strict verifier rejects all. When no model can achieve PERFECT, the task is not discriminating reasoning ability — it's testing whether agents can guess the exact implementation choices of the oracle.

#### [MAJOR] Oracle ADF implementation is non-standard
File: [`solution/solve.sh`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/161c50c/tasks/pairs-cointegration-kalman/solution/solve.sh)
The oracle implements ADF by hand using `linregress` on lagged residuals rather than using `statsmodels.tsa.stattools.adfuller`. The hand-rolled ADF computes standard errors differently (no lag augmentation, no constant term in the ADF regression beyond the coefficient). This produces ADF statistics that may differ substantially from what an agent using `statsmodels.adfuller` would get, causing cascading failures in the cointegration classification.

#### [MAJOR] Half-life formula produces unrealistic value
File: [`solution/solve.sh`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/161c50c/tasks/pairs-cointegration-kalman/solution/solve.sh), `tests/reference_data/expected.json`
The oracle computes half-life as `-log(2)/log(|lag1_autocorr|)` on the Kalman spread, yielding 0.39 days. A half-life < 1 day for a daily pairs trading signal is economically dubious and suggests the spread is nearly white noise. The tolerance (rtol=0.2, atol=5) is generous enough to accept values from 0 to ~5.4, but the reference value itself is suspicious.

#### [MAJOR] Backtest PnL uses spread change directly without normalization
File: [`solution/solve.sh`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/161c50c/tasks/pairs-cointegration-kalman/solution/solve.sh)
`pnl[t] = prev_pos * (-spread_change)` — this trades the raw Kalman innovation spread without normalizing for position sizing or notional. The annualized return of -18.2 and max drawdown of 2.44 (244%!) indicate the strategy is deeply unprofitable, which makes the task test whether agents can reproduce a failing strategy rather than build a correct one.

#### [MINOR] Expected max_drawdown > 1.0 (244%)
File: [`tests/reference_data/expected.json`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/161c50c/tasks/pairs-cointegration-kalman/tests/reference_data/expected.json)
`max_drawdown: 2.44` — a drawdown exceeding 100% implies the portfolio can go significantly negative. This is unusual for a pairs strategy benchmark and may confuse agents about the output convention.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-pairs-cointegration-kalman) | 0.383929 | 129s | 561,370in / 12,019out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-pairs-cointegration-kalman) | 0.785714 | 210s | 551,308in / 10,683out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-pairs-cointegration-kalman) | 0.714286 | 250s | 1,803,092in / 26,262out |


**Haiku key failures:**
```
FAIL: test_verification
E       AssertionError: Verification failed: WRONG
E       assert 'WRONG' == 'PERFECT'
E
E         - PERFECT
E         + WRONG
```


**Opus key failures:**
```
FAIL: test_verification
E       AssertionError: Verification failed: WRONG
E       assert 'WRONG' == 'PERFECT'
E
E         - PERFECT
E         + WRONG
```

### Summary
The task covers interesting quant territory (cointegration, Kalman filter, pairs trading) but has serious calibration issues. The non-standard ADF implementation creates a single correct path that all three frontier models fail to find. The oracle produces economically implausible results (half-life < 1 day, 244% drawdown, deeply negative returns). The task tests implementation mimicry rather than financial reasoning.

### Verdict
**不建议 Merge**

All frontier models fail. The oracle's hand-rolled ADF and economically implausible results make this task test oracle-guessing rather than quant competence. Recommend: (1) use `statsmodels.adfuller` in the oracle, (2) fix the backtest to produce reasonable economics, (3) re-run trials to confirm at least one model can pass.
