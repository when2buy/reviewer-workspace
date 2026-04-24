# Review: PR #107 - realized-vol-estimators
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/107](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/107)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Clean intraday minute-level mid quotes (deduplicate, filter to RTH), compute multi-frequency realized variance (1/2/5/15/30 min), estimate microstructure noise via Bandi-Russell (2006), apply noise-corrected RV, and compute bipower variation.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked trial results: H45=1.0, Opus46=0.0, S45=0.0
- Analyzed Opus46 test stdout (118 passed, 23 failed)

### Scorecard
- Task contract / instruction: 3/5 — Bandi-Russell formula not explicitly stated
- Verifier robustness: 4/5 — per-day parametrized tests with tolerances
- Difficulty calibration: 3/5 — interesting split but inverted (H45 passes, stronger models fail)
- Model discrimination: 3/5 — separates but in unexpected direction
- Benchmark integrity: 4/5 — data cleaning + formula application, hard to cheat
- Data realism: 4/5 — realistic intraday quote data with noise

### Findings

#### [CRITICAL] Bandi-Russell formula not specified — ambiguous instruction
File: [`instruction.md`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/51ac815/tasks/realized-vol-estimators/instruction.md) Step 3

The instruction says "Estimate the per-day microstructure-noise variance using the Bandi-Russell (2006) estimator" and cites the paper (Section 3.1) but **does not give the formula**. The Bandi-Russell paper presents multiple estimators. The canonical one is `σ²_noise = RV_1 / (2n)` but there are variants.

This ambiguity is the root cause of all Opus46 and S45 failures: all 23 failed tests are `noise_var_est`, `RV_5min_corrected`, and summary metrics that depend on noise estimation. H45 passes — likely by choosing the expected formula variant, possibly by luck.

**This is an instruction deficiency, not a model weakness.** A benchmark task should specify the exact formula when there are multiple published variants.

#### [MAJOR] Inverted model discrimination
H45=1.0, Opus46=0.0, S45=0.0 is inverted from typical difficulty expectations. This suggests the test measures "which model happens to pick the right Bandi-Russell variant" rather than quant reasoning ability. The RV computation, data cleaning, and bipower variation are all correct for Opus46 (118/141 tests pass) — only the noise estimator diverges.

#### [MINOR] Test data has 10 consecutive calendar dates including weekends
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/51ac815/tasks/realized-vol-estimators/tests/test_outputs.py)

Expected dates include 2024-01-06 (Saturday) and 2024-01-07 (Sunday). This is fine for synthetic data but slightly unusual.

#### [MINOR] Noise correction uses grand mean, not per-day — clearly specified
The instruction correctly specifies to use `grand_mean_noise_var` (not per-day), which is good.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-realized-vol-estimators) | 1.0 | 69s | 479,954in / 9,470out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-realized-vol-estimators) | 0.0 | 82s | 150,786in / 2,853out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-realized-vol-estimators) | 0.0 | 146s | 298,183in / 8,065out |


**Opus key failures:**
```
FAIL: test_noise_var_est
E       AssertionError: 2024-01-02 noise_var_est=1.449183212380096e-07, expected ~8.457063e-07
E       assert False
E        +  where False = <function isclose at 0x7f62f8359130>(1.449183212380096e-07, 8.457063e-07, rtol=0.001)
E        +    where <function isclose at 0x7f62f8359130> = np.isclose
FAIL: test_noise_var_est
E       AssertionError: 2024-01-03 noise_var_est=1.9140204453972472e-07, expected ~8.396994e-07
E       assert False
```


**Sonnet key failures:**
```
FAIL: test_noise_var_est
E       AssertionError: 2024-01-02 noise_var_est=2.890857703452523e-07, expected ~8.457063e-07
E       assert False
E        +  where False = <function isclose at 0x7ff89a4f6930>(2.890857703452523e-07, 8.457063e-07, rtol=0.001)
E        +    where <function isclose at 0x7ff89a4f6930> = np.isclose
FAIL: test_noise_var_est
E       AssertionError: 2024-01-03 noise_var_est=3.8181748060244057e-07, expected ~8.396994e-07
E       assert False
```

### Summary
The data cleaning, multi-frequency RV, and bipower variation components are well-specified and work correctly across all models. The Bandi-Russell noise estimator is under-specified — the instruction cites a paper but doesn't give the formula, causing 2/3 models to fail on noise-dependent tests. H45's success appears to be the right guess, not superior reasoning.

### Verdict
**不建议 Merge**

The instruction must explicitly specify the Bandi-Russell noise variance formula (e.g., `σ²_noise = RV_1min / (2 * n_1min)` or whichever variant is intended). Without this, the task measures formula guessing rather than quant implementation skill. Fix the instruction and re-run.
