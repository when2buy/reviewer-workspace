# Review: PR #157 - cev-option-pricing
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
File: `tests/test_outputs.py`

The test expects `atm_cev_price_beta090_T100 ≈ 45.34`. All three models produce ≈53.61 (the BS price). This is consistent with CEV theory: when β→1, the CEV model converges to GBM/BS. For β=0.9, the ATM CEV call price should be very close to BS (~53.6), not 45.34 (a 15% deviation). The oracle value of 45.34 is almost certainly wrong.

The likely bug: the oracle's α calibration may be incorrect. The standard calibration is `α = σ_hist / S₀^(β-1)`, ensuring local vol at S₀ matches σ_hist. If the oracle uses a different calibration (e.g., `α = σ_hist * S₀^(1-β)` with wrong sign, or `α = σ_hist` without the S₀ adjustment), it would produce systematically wrong prices.

#### [CRITICAL] `test_atm_beta05_T025` also fails for ALL models
All three models fail this test too, reinforcing that the oracle values are systematically off. The oracle solution is not provided (solve.py is empty in the PR), making it impossible to verify the oracle implementation.

#### [MAJOR] All models score 0 — task is non-functional
H:0/0/0. No discrimination possible when the oracle itself is wrong.

#### [MINOR] Instruction correctly describes CEV SDE and calibration approach
The instruction's description of `dS = r·S·dt + α·S^β·dW` and the use of non-central chi-squared is correct. The instruction says to calibrate α from historical volatility for each β, which is the right approach.

### Summary
The task concept is excellent — CEV pricing via non-central chi-squared is a genuine quant challenge. However, the **oracle expected values are almost certainly wrong**, causing all models to fail. When β=0.9, the ATM CEV price should be close to BS (~53.6), not 45.34. The oracle's α calibration appears to be buggy.

### Verdict
**不建议 Merge**

Blocker: oracle values are wrong. All three models independently produce the theoretically correct answer (~53.6 for β=0.9 ATM T=1.0) but the oracle expects 45.34. Fix the oracle's α calibration and regenerate expected values.
