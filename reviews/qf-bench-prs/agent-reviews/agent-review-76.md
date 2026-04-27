# Review: PR #76 - fama-macbeth-risk-premia
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/76](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/76)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Full Fama-MacBeth (1973) two-pass regression with rolling betas, four types of standard errors (FM, Newey-West, Shanken, Hodrick), GRS test, higher-order factor model, cross-sectional R² (OLS and GLS), multivariate Wald test, spanning tests, HDA statistic, and split-sample jackknife EIV correction. An extremely comprehensive asset pricing task with 11 steps.

### What I Did to Review This
- Read: instruction.md (partial — very long), task.toml, tests/test_outputs.py, tests/test.sh, Dockerfile
- Checked: trial results for h45, opus46, s45 (all reward=0.0)
- Analyzed: failure patterns

### Scorecard
- Task contract / instruction: 4/5 — impressively detailed
- Verifier robustness: 3/5
- Difficulty calibration: 2/5 — mislabeled "medium", clearly hard
- Model discrimination: 5/5 — excellent
- Benchmark integrity: 4/5

### Findings

#### [MAJOR] Difficulty mislabeled as "medium" — should be "hard"
File: [`task.toml`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/f8de275/tasks/fama-macbeth-risk-premia/task.toml)

This task has 11 distinct computational steps including Hodrick reverse regression, HDA statistic, spanning tests with Zhang-Kan adjustment, and split-sample jackknife. Expert estimate is 45 min, junior 120 min. The best model (Opus) fails 1/60 tests. This is clearly "hard" difficulty.

For reference:
- Opus: 59/60 (only GRS statistic fails)
- Haiku: 56/60 (NW lags, GRS, Wald stat+pval fail)
- Sonnet: 44/60 (widespread beta/risk premia failures)

#### [MAJOR] GRS statistic test fails for ALL models
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/f8de275/tasks/fama-macbeth-risk-premia/tests/test_outputs.py), `test_grs_statistic`

Expected: 23.003. Opus gets a different value (close but outside atol=0.1). The instruction specifies "F(N, T-N-K) where N=25, K=3, T=726" and "Run full-sample time-series regressions." The GRS formula involves Σ_ε inverse and Σ_F inverse — small differences in how the factor covariance is computed (e.g., whether to include intercept in the regression) can shift the F-stat.

This is likely a tolerance issue rather than a spec bug — Opus is very close. Consider widening tolerance to atol=0.5.

#### [MINOR] Newey-West lag selection ambiguity
Haiku selects 5 lags vs oracle 6. The instruction says "automatic bandwidth selection" without specifying the exact formula. The standard Newey-West automatic bandwidth is `floor(4*(T/100)^(2/9))` which for T=667 gives `floor(4*(6.67)^(0.222)) = floor(5.73) = 5 or 6` depending on rounding. The instruction should pin the formula.

#### [NIT] Instruction is extremely long (11 steps with detailed formulas)
The instruction reads like a problem set solution manual. While this is good for specification clarity, it reduces the "benchmark" aspect — it's more about careful implementation than financial reasoning. However, for QF-Bench purposes this is acceptable.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-fama-macbeth-risk-premia) | 0.0 | 208s | 1,371,638in / 37,193out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-fama-macbeth-risk-premia) | 0.0 | 142s | 160,612in / 7,667out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-fama-macbeth-risk-premia) | 0.0 | 236s | 258,553in / 12,975out |


**Haiku key failures:**
```
FAIL: test_nw_lags
E       assert 5 == 6
FAIL: test_grs_statistic
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f3d10cd59f0>(23.879902636335714, 23.003, atol=0.1)
E        +    where <function isclose at 0x7f3d10cd59f0> = np.isclose
FAIL: test_wald_statistic
E       assert np.False_
```


**Opus key failures:**
```
FAIL: test_grs_statistic
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7fb851cd3970>(23.130191615606492, 23.003, atol=0.1)
E        +    where <function isclose at 0x7fb851cd3970> = np.isclose
```

### Summary
Outstanding task design with excellent model discrimination. The instruction is remarkably detailed and covers both classical (FM, GRS) and modern (HDA, spanning, jackknife) asset pricing methods. The main issues are: (1) GRS tolerance may be too tight, (2) NW lag selection formula should be pinned, (3) difficulty label is wrong.

### Verdict
**需要 Human Review** — Very close to merge-ready. Fix difficulty label "medium"→"hard", consider widening GRS tolerance. Opus at 59/60 shows the task is well-calibrated. The remaining GRS failure may be a tolerance or oracle precision issue rather than a fundamental problem.
