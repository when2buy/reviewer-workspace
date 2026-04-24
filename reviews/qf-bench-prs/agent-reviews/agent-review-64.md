# Review: PR #64 - cta-ewma-cvar
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/64](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/64)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
CTA (Commodity Trading Advisor) strategy backtest: adjust prices for corporate actions, resample to monthly, compute EWMA signals with a 1-month skip, build a vol-targeted portfolio, and compute risk metrics including Cornish-Fisher Modified VaR and Newey-West HAC t-statistic.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, Dockerfile
- Checked: trial results for h45, opus46, s45 (all reward=0.0)
- Analyzed: failure patterns across all three models

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 2/5 — likely oracle bug
- Difficulty calibration: 3/5
- Benchmark integrity: 4/5
- Data realism: 4/5

### Findings

#### [CRITICAL] Oracle value for `num_valid_obs` appears wrong — all 3 models agree on 58, oracle says 57
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/2231e93/tasks/cta-ewma-cvar/tests/test_outputs.py) line 44

All three models (Haiku, Opus, Sonnet) produce `num_valid_obs = 58` and the test hardcodes 57 with an exact-match assertion (`assert load_r()["num_valid_obs"] == 57`). When three independent model implementations converge on the same value and disagree with the oracle, the oracle is likely wrong.

The discrepancy is probably a fencepost error in the month-end resampling or the `estimation_window_days` filtering. The broader tolerance test `test_num_monthly_obs` (50 ≤ n ≤ 65) passes for all models, confirming they're in the right ballpark.

This single test failure causes all three models to score 0.0, which is a pure verifier bug — the task would otherwise be well-calibrated (15/16 tests pass for all models).

**Fix:** Verify the oracle solution's resampling logic and update the expected value to 58, or widen the tolerance.

#### [MINOR] Test has both exact and range check for same quantity
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/2231e93/tasks/cta-ewma-cvar/tests/test_outputs.py)

`test_num_valid_obs` does exact equality (==57) while `test_num_monthly_obs` does range (50-65). The exact check is fragile and redundant given the range check already exists.

#### [MINOR] Solution file is empty
File: [`solution/solve.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/2231e93/tasks/cta-ewma-cvar/solution/solve.py)

The solution file is empty (0 bytes). While this prevents answer leakage, it also means there's no oracle implementation to audit for correctness.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-cta-ewma-cvar) | 0.0 | 246s | 1,530,408in / 21,147out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-cta-ewma-cvar) | 0.0 | 112s | 210,242in / 4,340out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-cta-ewma-cvar) | 0.0 | 144s | 325,419in / 6,879out |


**Haiku key failures:**
```
FAIL: test_num_valid_obs
E       assert 58 == 57
```


**Opus key failures:**
```
FAIL: test_num_valid_obs
E       assert 58 == 57
```

### Summary
The task is well-designed — detailed instruction, multi-step pipeline, good test coverage across intermediates and final metrics, proper canary strings. However, a likely oracle bug in `num_valid_obs` (57 vs the unanimous model answer of 58) causes 0% pass rate across all models. This is a single-line fix.

### Verdict
**不建议 Merge** — oracle bug in `num_valid_obs` causes false 0% pass rate. Fix the expected value (likely 57→58) and this becomes a strong task.
