# Review: PR #131 - garch-vecm-cointegration
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/131](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/131)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
VECM cointegration analysis on 3 energy-sector ETFs: clean dirty data (duplicates, NaN, outliers, negative prices), ADF unit root tests, Johansen cointegration test, VECM estimation with BIC lag selection, half-life computation, and spread stationarity verification.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `solution/solve.sh`
- Checked: data cleaning rules, Johansen test parameters, VECM estimation, BIC computation, half-life formula
- Reviewed trial outputs: H45 24/24 PASSED, Opus46 5/24 FAILED, S45 24/24 PASSED

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 4/5 |
| Verifier robustness | 4/5 |
| Difficulty calibration | 3/5 |
| Model discrimination | 2/5 |
| Benchmark integrity | 4/5 |

### Findings

#### [MAJOR] Inverted model discrimination — H45 and S45 pass, Opus46 fails
The provided scores are (H:1.0, O:0.0, S:1.0). H45 (weakest) and S45 pass perfectly while Opus46 (strongest) fails 5 tests. This is anomalous — it suggests the task rewards a specific implementation path that H45/S45 happen to follow but Opus46 doesn't. This is the opposite of good calibration.

#### [MAJOR] BIC computation in oracle is non-standard
File: [`solution/solve.sh`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/485e6aa/tasks/garch-vecm-cointegration/solution/solve.sh)
The oracle computes BIC manually: `bic = -2 * ll + n_params * np.log(T)` with a hand-counted `n_params`. The statsmodels VECM object has its own BIC computation that may differ in parameter counting. This creates a situation where using the library's built-in BIC gives a different lag selection than the oracle's manual BIC.

#### [MAJOR] Adjustment coefficient scaling is ambiguous
File: [`solution/solve.sh`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/485e6aa/tasks/garch-vecm-cointegration/solution/solve.sh)
The oracle does `alpha_scaled = alpha_col * beta[norm_idx, 0]` — scaling adjustment coefficients by the normalization factor. The instruction says "normalized so the first element equals 1.0" but doesn't specify how alpha should be reported (raw or scaled). The test expects specific values (e.g., `-0.022`, `-0.0157`) — agents must guess the convention.

#### [POSITIVE] Data cleaning rules are well-specified
The instruction gives exact, ordered cleaning steps: (1) drop duplicates, (2) drop NaN, (3) drop non-positive, (4) drop >5× median. This is clear and deterministic.

#### [POSITIVE] Uses real-world data with realistic quality issues
Energy-sector ETF data with injected quality problems (duplicates, spikes, missing values) is a realistic benchmark scenario.

#### [MINOR] Task title includes "GARCH" but there's no GARCH modeling
File: [`task.toml`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/485e6aa/tasks/garch-vecm-cointegration/task.toml)
The task is purely about VECM/cointegration — no GARCH component. The title is misleading.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-garch-vecm-cointegration) | 1.0 | 141s | 817,350in / 8,639out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-garch-vecm-cointegration) | 0.0 | 158s | 199,637in / 6,483out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-garch-vecm-cointegration) | 1.0 | 158s | 467,703in / 7,373out |


**Opus key failures:**
```
FAIL: test_cointegrating_vector_third_element
E       AssertionError: Third element: got -0.009113970148887986, expected ~0.0201
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f35eed6a970>(-0.009113970148887986, 0.0201, rtol=0.1)
E        +    where <function isclose at 0x7f35eed6a970> = np.isclose
FAIL: test_adjustment_coefficient
E       AssertionError: Alpha[0]: got -0.027186389591988176, expected ~-0.022
E       assert np.False_
```

### Summary
Good cointegration analysis task with realistic dirty data. The main concern is inverted model discrimination (H45 passes, Opus46 fails) — this suggests the task rewards a specific implementation path rather than reasoning ability. The BIC computation and alpha scaling conventions create implementation-sensitive failure modes.

### Verdict
**需要 Human Review**

The inverted discrimination (H45 beats Opus46) is a red flag. Human should investigate what causes Opus46 to fail (likely BIC computation or alpha scaling convention) and consider whether the task rewards the right thing. The financial content is sound but the calibration needs adjustment.
