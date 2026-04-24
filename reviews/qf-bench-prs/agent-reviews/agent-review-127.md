# Review: PR #127 - crypto-funding-rate-basis-carry
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/127](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/127)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Analyze BTCUSDT perpetual funding rate economics: descriptive stats, autocorrelation, ADF test, regime analysis (bear/recovery split), OU process fitting, and Monte Carlo basis carry simulation. Produces 6 output files.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `solution/solve.py`, `solution/solve.sh`
- Checked: OU fitting convention, MC simulation, test pinned values, trial results
- Reviewed trial outputs: H45 32/63 failed, Opus46 26/63 failed, S45 16/63 failed — **all models fail significantly**

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 3/5 |
| Verifier robustness | 2/5 |
| Difficulty calibration | 1/5 |
| Model discrimination | 2/5 |
| Benchmark integrity | 2/5 |

### Findings

#### [CRITICAL] All models score 0.0 — massive test failure rates
H45: 32 failed / 63 total. Opus46: 26 failed. S45: 16 failed / 63 total. The provided scores are (H:0.0, O:0.0, S:0.0). The strict 0/1 verifier means even one failure → reward 0, but the sheer number of failures indicates fundamental specification problems.

#### [CRITICAL] Test pins exact numeric values with very tight tolerances
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/c2fca48/tasks/crypto-funding-rate-basis-carry/tests/test_outputs.py)
Tests pin values like `mean=5.493e-05` (atol=1e-06), `skewness=-3.20` (atol=0.2), `kurtosis=60.4` (atol=5.0). The `num_observations == 2190` check is exact. Any data filtering difference (e.g., handling of the date range boundaries, timezone interpretation of Unix timestamps) will cascade into different observation counts and different statistics.

#### [CRITICAL] MC simulation results are unpinnable across implementations
The MC stats tests check simulated basis carry returns which depend on the exact OU simulation path. Even with a fixed seed, differences in the random number generator call sequence, array shape handling, or simulation loop will produce different MC outputs.

#### [MAJOR] Verifier uses individual pytest tests, not generic verifier
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/c2fca48/tasks/crypto-funding-rate-basis-carry/tests/test_outputs.py)
Unlike the GinkgoGao PRs which use the generic multi-phase verifier with tolerance-based checking, this PR has ~63 individual pytest tests with hard-coded expected values. This is much more brittle — a different verifier architecture than the benchmark standard.

#### [MAJOR] `num_observations` sensitivity
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/c2fca48/tasks/crypto-funding-rate-basis-carry/tests/test_outputs.py)
`assert r["num_observations"] == 2190` — exact match. The instruction says filter to date range `[analysis_start, analysis_end]`. Boundary handling of Unix ms timestamps vs UTC date strings could easily produce 2188 or 2191 observations. The trial output shows `assert 2188 == 2190` for H45.

#### [MINOR] OU fitting convention is over-specified
The instruction explicitly specifies "plug-in Euler" convention vs "exact-discretization AR(1)". This is good for reproducibility but unusual — most quant practitioners would use the AR(1) form. The instruction calls it out clearly, which is fine.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-crypto-funding-rate-basis-carry) | 0.0 | 135s | 723,158in / 10,341out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-crypto-funding-rate-basis-carry) | 0.0 | 151s | 268,365in / 8,145out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-crypto-funding-rate-basis-carry) | 0.0 | 195s | 327,728in / 10,961out |


**Haiku key failures:**
```
FAIL: test_symbol_and_obs
E       assert 2188 == 2190
FAIL: test_descriptive_stat
E       AssertionError: mean=0.5467306672760512, expected ~5.493e-05
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7fbab356a970>(0.5467306672760512, 5.493e-05, atol=1e-06)
E        +    where <function isclose at 0x7fbab356a970> = np.isclose
FAIL: test_descriptive_stat
```


**Opus key failures:**
```
FAIL: test_descriptive_stat
E       AssertionError: mean=0.5493441552511417, expected ~5.493e-05
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7fed1d3ad2b0>(0.5493441552511417, 5.493e-05, atol=1e-06)
E        +    where <function isclose at 0x7fed1d3ad2b0> = np.isclose
FAIL: test_descriptive_stat
E       AssertionError: std=0.7690209162381608, expected ~7.69e-05
E       assert np.False_
```

### Summary
This task has a well-thought-out financial concept (crypto funding rate analysis + OU fitting + MC carry simulation), but the verification is fundamentally broken. All three models score 0.0 with massive test failure counts. The hard-pinned numeric values and exact observation count checks make the task impossibly brittle. Needs a complete verifier overhaul.

### Verdict
**不建议 Merge**

All models score 0.0 with 16-32 test failures each. The verifier pins exact values too tightly, and the MC simulation results are not reproducible across implementations. Recommend: (1) switch to the generic tolerance-based verifier, (2) loosen observation count to allow ±2, (3) remove or greatly relax MC-dependent checks, (4) re-run trials.
