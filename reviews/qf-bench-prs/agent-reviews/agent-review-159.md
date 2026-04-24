# Review: PR #159 - cir-bond-pricing
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/159](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/159)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Calibrate a Cox-Ingersoll-Ross short-rate model to Federal Funds Rate data via MLE, price zero-coupon bonds using the Ricatti closed-form, construct a yield curve, compare to market yields, and compute forward rates.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked: CIR SDE, Ricatti bond pricing formulas (A(τ), B(τ)), Feller condition, MLE approach
- Reviewed: trial results for h45, opus46, s45

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 5 |
| Verifier robustness | 5 |
| Difficulty calibration | 3 |
| Model discrimination | 1 |
| Benchmark integrity / anti-cheating | 5 |

### Findings

#### [MINOR] No model discrimination — all three pass
H:1.0, O:1.0, S:1.0 — all pass 35/35. Same issue as PR#152. This is labeled "hard" but all models pass easily. The CIR model is well-known, and the instruction provides explicit formulas for A(τ), B(τ), the transition density, and even the optimization method (L-BFGS-B with 5 restarts). This level of specificity makes the task more of a coding exercise.

#### [MINOR] MLE calibration is stochastic but all models converge
The "5 random restarts" requirement introduces non-determinism, but the CIR likelihood surface for Fed Funds data is well-behaved enough that all models find similar optima. Tests wisely use range-based checks rather than pinned parameter values.

#### [MINOR] Excellent test design
Tests check: parameter bounds, Feller condition consistency, bond price properties (positive, <1, decreasing in τ), yield formula consistency, forward rate positivity, and cross-consistency between calibration→bonds→forwards. This is a model of good verifier design.

#### [NIT] Financial correctness is solid
The Ricatti formulas for A(τ) and B(τ) in the instruction are correct. The CIR transition density via non-central χ² is correct. The Feller condition 2κθ ≥ σ² is stated correctly.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 1.0 | 79s | 265,657in / 6,116out |
| Opus 4.6 | 1.0 | 98s | 122,148in / 3,881out |
| Sonnet 4.5 | 1.0 | 719s | 353,291in / 7,547out |

### Summary
Excellent task design and verifier quality. The CIR model instruction is thorough and correct. Tests are comprehensive, property-based, and robust. The only issue is zero model discrimination — all models pass. The "hard" label is too aggressive given that the instruction provides all formulas explicitly. Consider "medium" or reduce formula specificity.

### Verdict
**建议 Merge**

Correct, well-tested, robust verifier. Lack of discrimination is a calibration concern but not a blocker. Consider relabeling difficulty from "hard" to "medium."
