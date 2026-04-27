# Review: PR #165 - first-passage-time
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/165](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/165)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Computes analytical distributions of running maximum, running minimum, and first passage times for GBM using the reflection principle. Verifies against Monte Carlo simulation.

### What I Did to Review This
- Read: instruction.md, test_outputs.py, trial results
- Checked financial correctness of reflection principle tests
- Reviewed model discrimination

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 4/5
- Difficulty calibration: 4/5
- Model discrimination: 3/5 — Opus and Sonnet pass, Haiku fails narrowly
- Benchmark integrity: 4/5

### Findings

#### [MINOR] Good discrimination pattern
Opus (1.0) and Sonnet (1.0) pass all 31 tests. Haiku (0.0) fails only on `test_joint_mc_close` — the joint distribution of (X_T, M_T) MC verification. Haiku passed 30/31 tests, failing on the most complex joint distribution computation. This is a clean difficulty signal.

#### [MINOR] Strong structural tests
Tests include monotonicity (prob decreases with barrier height, increases with time), CDF in [0,1], MC-analytical comparison with 25-30% tolerance (appropriate for discrete monitoring bias), and pinned values (prob_hit_110_T1 ≈ 0.585, prob_hit_090_T1 with reasonable tolerance).

#### [MINOR] mu_rn consistency test
`test_mu_rn_consistent` checks μ_rn = r - D - σ²/2, which is the correct risk-neutral log-drift. Good mathematical check.

#### [NIT] MC tolerance of 30% is loose
The MC comparison allows 30% relative error for running extrema, which is appropriate given discrete vs. continuous monitoring bias, but could mask some implementation errors.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-first-passage-time) | 0.0 | 450s | 3,246,548in / 33,816out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-first-passage-time) | 1.0 | 142s | 203,220in / 6,269out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-first-passage-time) | 1.0 | 331s | 1,142,996in / 16,843out |


**Haiku key failures:**
```
E       assert 0.17157700932923622 < 0.03
E        +  where 0.17157700932923622 = abs((0.17986299067076375 - 0.35144))
```

### Summary
Clean task with correct financial mathematics. Good use of the reflection principle. Reasonable model discrimination — Haiku fails only on the hardest joint distribution test. Strong parity and monotonicity checks.

### Verdict
**建议 Merge** — Correct, well-calibrated, clean model discrimination.
