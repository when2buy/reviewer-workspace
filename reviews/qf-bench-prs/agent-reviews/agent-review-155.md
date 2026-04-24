# Review: PR #155 - barrier-gbm-analytics
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/155](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/155)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Compute analytical distributions for running max/min and first passage times of GBM. Verify against Monte Carlo simulation. Input is SPY daily OHLCV.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked: financial correctness, verifier robustness, trial failure modes
- Reviewed: trial results for h45, opus46, s45

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 4 |
| Verifier robustness | 2 |
| Difficulty calibration | 3 |
| Model discrimination | 2 |
| Benchmark integrity / anti-cheating | 4 |

### Findings

#### [CRITICAL] Verifier bug in `test_mean_fpt_down` — TypeError on all strong models
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/47112b5/tasks/barrier-gbm-analytics/tests/test_outputs.py)

Opus fails 1/24 with `TypeError: '<' not supported between instances of 'float' and 'str'` in `test_mean_fpt_down`. Sonnet fails the same test with `TypeError: '<' not supported between instances of 'float' and 'NoneType'`. 

The mean first passage time for a downward barrier with positive drift (SPY has μ≈0.20) is **infinite** — the expected time to hit a level below S₀ when the drift is upward is infinite (or undefined). Agents correctly output `"inf"`, `null`, or similar, but the test tries to do a `<` comparison against a float, causing a TypeError.

This is a verifier bug: the test must handle the mathematical reality that `E[T_b] = ∞` for certain barrier/drift combinations. The verifier should accept `inf`, `null`, `"Inf"`, `NaN`, or similar representations.

#### [MAJOR] All models score 0 despite Opus/Sonnet being substantively correct
Opus passes 23/24 (only fails the fpt_down bug above). Sonnet passes 22/24 (also fails drift_range by a hair). Both are penalized to reward=0 due to a single verifier bug. This makes the task non-functional as a discriminator.

#### [MINOR] Haiku fails substantively (10/24 failures)
Haiku's failures are real — wrong CDF values, wrong MC results. This is genuine discrimination, but it's masked by the verifier bug giving everyone reward=0.

#### [MINOR] Dockerfile copies `data/` directory instead of specific file
The Dockerfile uses `COPY data/ /app/data/` but the instruction references `/app/spy_daily.csv`. This works if the data directory contains spy_daily.csv, but the path in the Dockerfile doesn't match the instruction's data path. Agents would need to find the data at `/app/data/spy_daily.csv` rather than `/app/spy_daily.csv`.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 358s | 2,517,966in / 28,128out |
| Opus 4.6 | 0.0 | 198s | 520,497in / 9,402out |
| Sonnet 4.5 | 0.0 | 533s | 1,934,552in / 27,509out |


**Haiku key failures:**
```
E       AssertionError: max CDF at 1.10: 0.0858170210646019
E       assert 0.1 < np.float64(0.0858170210646019)
E       AssertionError: min CDF at 0.90: 0.1269336413925213
E       assert 0.13 < np.float64(0.1269336413925213)
E       AssertionError: Some MC errors exceed 0.020: [0.047992978935398, 0.0869237820639337, 0.0260085501332349, 0.0091563586074786, 0.4176034587410434, 0.9990731198670784]
E       assert np.False_
E        +  where np.False_ = all()
E        +    where all = 0    0.047993\n1    0.086924\n2    0.026009\n3    0.009156\n4    0.417603\n5    0.999073\nName: abs_error, dtype: float64 < 0.02.all
```


**Opus key failures:**
```
E       TypeError: '<' not supported between instances of 'float' and 'str'
```

### Summary
The task is conceptually sound — running extremes and first passage times are important barrier option analytics. However, a **verifier bug** in `test_mean_fpt_down` causes all models to fail (reward=0), making the task non-functional. The bug is that the test doesn't handle infinite mean FPT for downward barriers with positive drift.

### Verdict
**不建议 Merge**

Blocker: verifier bug in `test_mean_fpt_down` gives all models reward=0 despite Opus/Sonnet being substantively correct. Fix: handle infinite/null mean FPT values in the test. Also verify data path consistency between Dockerfile and instruction.
