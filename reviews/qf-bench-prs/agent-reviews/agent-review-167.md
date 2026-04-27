# Review: PR #167 - geometric-mean-reverting-jd
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/167](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/167)
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


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-geometric-mean-reverting-jd) | 0.0 | 85s | 222,469in / 5,846out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-geometric-mean-reverting-jd) | 1.0 | 98s | 147,277in / 3,970out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-geometric-mean-reverting-jd) | 0.0 | 108s | 111,419in / 5,348out |


**Haiku key failures:**
```
E       assert np.False_
E        +  where np.False_ = all()
E        +    where all = 0    0.043029\n1    0.080839\n2    0.144116\n3    0.237715\n4    0.415628\nName: Var_X, dtype: float64 <= (0.23621084091434857 + 0.01).all
E               AssertionError: tau=2.0: relerr=0.1727
E               assert np.float64(0.1727003327464178) < 0.1
E       assert 0.40785278123735247 < 0.15
```


**Sonnet key failures:**
```
E       assert np.False_
E        +  where np.False_ = all()
E        +    where all = 0    0.043236\n1    0.081244\n2    0.144895\n3    0.239185\n4    0.418991\nName: Var_X, dtype: float64 <= (0.319391205907997 + 0.01).all
E               AssertionError: tau=1.0: relerr=0.1029
E               assert np.float64(0.10292102597661826) < 0.1
E       assert 0.414408825878002 < 0.15
```

### Summary
Well-designed task testing a non-trivial stochastic process (OU + jumps). Correct financial mathematics throughout. Good model discrimination where the variance formulas separate Opus from the others.

### Verdict
**建议 Merge** — Correct, well-calibrated, good discrimination on a genuinely difficult quantitative task.
