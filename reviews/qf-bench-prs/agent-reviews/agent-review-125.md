# Review: PR #125 - bl-regime-hmm
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/125](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/125)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Fit a 2-state Gaussian HMM via Baum-Welch on market-cap-weighted portfolio returns, identify bull/bear regimes, compute regime-conditional covariance, run Black-Litterman portfolio optimization with views, and report performance metrics.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `solution/solve.sh`, `tests/reference_data/expected.json`, `tests/reference_data/checkpoints.json`
- Checked: HMM implementation, BL math, view conversion, tolerance calibration
- Reviewed trial outputs: H45 FAILED, Opus46 FAILED, S45 FAILED

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 4/5 |
| Verifier robustness | 3/5 |
| Difficulty calibration | 2/5 |
| Model discrimination | 1/5 |
| Benchmark integrity | 4/5 |

### Findings

#### [CRITICAL] All three frontier models fail
Trial results: H45 FAILED, Opus46 FAILED, S45 FAILED. The provided scores (H:0.5, O:0.92, S:0.58) suggest partial credit elsewhere, but the strict PERFECT verifier rejects all. This indicates the task is too tightly specified for current models.

#### [MAJOR] Hand-rolled Baum-Welch creates implementation-sensitive checkpoints
File: [`solution/solve.sh`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/460473d/tasks/bl-regime-hmm/solution/solve.sh)
The oracle implements Baum-Welch from scratch in ~60 lines of Python rather than using `hmmlearn`. The HMM iteration count (checkpoint `hmm_iterations: 25`, atol=5) and internal parameters (`hmm_mu_bull`, `hmm_sigma_bear`) are sensitive to the exact EM implementation, numerical stability choices, and convergence criterion. An agent using `hmmlearn.GaussianHMM` will likely get different iteration counts and slightly different parameters, even if the final regime classification is correct.

#### [MAJOR] Checkpoint tolerances on HMM internals are tight
File: [`tests/reference_data/checkpoints.json`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/460473d/tasks/bl-regime-hmm/tests/reference_data/checkpoints.json)
`hmm_mu_bull` has atol=5e-5, `hmm_sigma_bear` has atol=5e-4, `regime_prob_bull` has rtol=0.05/atol=0.02. These are tight for an EM algorithm that can converge to different local optima depending on implementation. The `n_bull_days` checkpoint (atol=5) further constrains the exact smoothing output.

#### [POSITIVE] Instruction is very detailed
The instruction explicitly specifies initialization (first-half/second-half split), convergence criterion, hard assignment threshold (0.5), gross-exposure normalization, and view conversion. This is commendable specificity — the problem is that the checkpoints demand matching the oracle's exact numerics.

#### [MINOR] BL view conversion: annual to daily
File: [`solution/solve.sh`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/460473d/tasks/bl-regime-hmm/solution/solve.sh)
`Q[vi] = v["return"] / 252` and `omega_diag[vi] = v["confidence"]**2 / 252`. The variance division by 252 (not 252²) is a specific convention choice. The instruction says "convert annual values to the daily frequency" without specifying whether to convert the variance or the standard deviation. This is a common source of agent error.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-bl-regime-hmm) | 0.5 | 390s | 1,323,476in / 16,061out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-bl-regime-hmm) | 0.916667 | 89s | 121,849in / 3,601out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-bl-regime-hmm) | 0.583333 | 114s | 107,631in / 5,398out |


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
E       AssertionError: Verification failed: IMPERFECT
E       assert 'IMPERFECT' == 'PERFECT'
E
E         - PERFECT
E         + IMPERFECT
E         ? ++
```

### Summary
Ambitious multi-domain task (HMM + BL + portfolio optimization) with excellent instruction detail. However, all three frontier models fail, and the tight checkpoints on HMM internals create an implementation-matching problem rather than a financial reasoning test. The HMM convergence path is implementation-sensitive.

### Verdict
**不建议 Merge**

All frontier models fail. The tight HMM checkpoints make this an implementation-matching exercise. Recommend: (1) relax HMM internal checkpoints significantly (or remove them and only check final outputs), (2) accept `hmmlearn`-based solutions, (3) re-run trials after relaxation.
