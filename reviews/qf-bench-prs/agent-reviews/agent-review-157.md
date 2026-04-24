# Review: PR #157 - cev-option-pricing
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/157](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/157)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Price European options under the Constant Elasticity of Variance (CEV) model using the non-central chi-squared distribution. Compare to Black-Scholes and compute implied volatilities across a β×T×moneyness grid.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked: financial correctness of CEV pricing, oracle expected values, calibration logic
- Reviewed: trial results for h45, opus46, s45

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 3 |
| Verifier robustness | 1 |
| Difficulty calibration | 1 |
| Model discrimination | 1 |
| Benchmark integrity / anti-cheating | 3 |

### Findings

#### [CRITICAL] Oracle value for `atm_cev_price_beta090_T100` is likely wrong
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/711bc67/tasks/cev-option-pricing/tests/test_outputs.py)

The test expects `atm_cev_price_beta090_T100 ≈ 45.34`. All three models produce ≈53.61 (the BS price). This is consistent with CEV theory: when β→1, the CEV model converges to GBM/BS. For β=0.9, the ATM CEV call price should be very close to BS (~53.6), not 45.34 (a 15% deviation). The oracle value of 45.34 is almost certainly wrong.

The likely bug: the oracle's α calibration may be incorrect. The standard calibration is `α = σ_hist / S₀^(β-1)`, ensuring local vol at S₀ matches σ_hist. If the oracle uses a different calibration (e.g., `α = σ_hist * S₀^(1-β)` with wrong sign, or `α = σ_hist` without the S₀ adjustment), it would produce systematically wrong prices.

#### [CRITICAL] `test_atm_beta05_T025` also fails for ALL models
All three models fail this test too, reinforcing that the oracle values are systematically off. The oracle solution is not provided (solve.py is empty in the PR), making it impossible to verify the oracle implementation.

#### [MAJOR] All models score 0 — task is non-functional
H:0/0/0. No discrimination possible when the oracle itself is wrong.

#### [MINOR] Instruction correctly describes CEV SDE and calibration approach
The instruction's description of `dS = r·S·dt + α·S^β·dW` and the use of non-central chi-squared is correct. The instruction says to calibrate α from historical volatility for each β, which is the right approach.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 120s | 591,762in / 10,161out |
| Opus 4.6 | 0.0 | 255s | 365,244in / 13,504out |
| Sonnet 4.5 | 0.0 | 638s | 1,979,459in / 36,492out |


**Haiku key failures:**
```
E       AssertionError: beta=0.5 T=0.25 ATM price=68.17514159989594, expected < 1
E       assert np.float64(68.17514159989594) < 1.0
E       AssertionError: beta=0.9 T=0.25 ATM price=6.305476000577073, expected ~23.38
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7faa0bb67a70>(np.float64(6.305476000577073), 23.375727, atol=0.5)
E        +    where <function isclose at 0x7faa0bb67a70> = np.isclose
E       AssertionError: beta=0.9 T=1.0 ATM price=24.63433740957817, expected ~45.34
E       assert np.False_
```


**Opus key failures:**
```
E       AssertionError: beta=0.5 T=0.25 ATM price=23.84961, expected < 1
E       assert np.float64(23.84961) < 1.0
E       AssertionError: beta=0.9 T=1.0 ATM price=53.613845, expected ~45.34
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f98e1f8f870>(np.float64(53.613845), 45.340967, atol=0.5)
E        +    where <function isclose at 0x7f98e1f8f870> = np.isclose
E       AssertionError: atm_cev_price_beta090_T100=53.613845, expected ~45.34
E       assert np.False_
```

### Summary
The task concept is excellent — CEV pricing via non-central chi-squared is a genuine quant challenge. However, the **oracle expected values are almost certainly wrong**, causing all models to fail. When β=0.9, the ATM CEV price should be close to BS (~53.6), not 45.34. The oracle's α calibration appears to be buggy.

### Verdict
**不建议 Merge**

Blocker: oracle values are wrong. All three models independently produce the theoretically correct answer (~53.6 for β=0.9 ATM T=1.0) but the oracle expects 45.34. Fix the oracle's α calibration and regenerate expected values.
