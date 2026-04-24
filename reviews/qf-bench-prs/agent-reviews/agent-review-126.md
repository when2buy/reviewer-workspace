# Review: PR #126 - merton-cds-copula
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/126](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/126)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Complete credit risk pipeline: calibrate Merton structural model for 10 firms (extract asset value/volatility from equity), compute distance-to-default and default probabilities, price 5-year CDS spreads via hazard rates, and run Gaussian copula MC for portfolio loss distribution (EL, VaR, ES).

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `solution/solve.sh`, `tests/reference_data/expected.json`, `tests/reference_data/checkpoints.json`
- Checked: Merton solver, CDS pricing formula, copula MC, tolerance calibration
- Reviewed trial outputs: H45 FAILED, Opus46 FAILED, S45 FAILED

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 4/5 |
| Verifier robustness | 3/5 |
| Difficulty calibration | 3/5 |
| Model discrimination | 2/5 |
| Benchmark integrity | 4/5 |

### Findings

#### [CRITICAL] All three frontier models fail despite generous tolerances
Trial results: H45 FAILED, Opus46 FAILED, S45 FAILED. The scores (H:0.9, O:0.9, S:0.9) suggest they're very close but fail at PERFECT. This is likely a single checkpoint or deliverable causing the failure.

#### [MAJOR] Merton solver uses hand-rolled Newton-Raphson with numerical Jacobian
File: [`solution/solve.sh`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/2922806/tasks/merton-cds-copula/solution/solve.sh)
The oracle uses a custom Newton-Raphson with `eps=1e-6` perturbation for Jacobian approximation and `0.5` step damping. Different solver choices (scipy.fsolve, different initial guesses, different damping) will produce slightly different V and σ_V, cascading through all downstream computations. With `rtol=0.2` on most outputs, this should be tolerable — but it apparently isn't, given all models fail.

#### [MAJOR] Portfolio loss % computation is non-standard
File: [`solution/solve.sh`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/2922806/tasks/merton-cds-copula/solution/solve.sh)
`portfolio_expected_loss_pct = portfolio_el / N * 100` where N=10 firms. This divides by number of firms rather than total notional. If `exposure_per_firm` differs across firms (it's constant here but could confuse agents), this would be wrong. The denominator choice is not specified in the instruction.

#### [MINOR] ES computed on tail beyond VaR, not including VaR
File: [`solution/solve.sh`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/2922806/tasks/merton-cds-copula/solution/solve.sh)
`portfolio_es = float(np.mean(losses_sorted[var_idx + 1:]))` — this excludes the VaR quantile itself from the ES average. Both conventions exist, but this should be explicit.

#### [POSITIVE] Excellent domain coverage
The task meaningfully exercises credit modeling (Merton), derivative pricing (CDS), and portfolio risk (Gaussian copula MC). The instruction is detailed and the financial concepts are correctly described.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.9 | 127s | 974,538in / 19,984out |
| Opus 4.6 | 0.9 | 91s | 157,880in / 3,779out |
| Sonnet 4.5 | 0.9 | 104s | 118,883in / 5,413out |


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
E       AssertionError: Verification failed: WRONG
E       assert 'WRONG' == 'PERFECT'
E
E         - PERFECT
E         + WRONG
```

### Summary
High-quality credit risk task with genuine multi-domain coverage. The main concern is all models fail despite scores of 0.9 — likely a single tight checkpoint. The Merton solver sensitivity and loss % convention are potential failure points. With minor tolerance relaxation, this could be an excellent benchmark item.

### Verdict
**需要 Human Review**

Scores of 0.9 across all models suggest this is very close to working. A human should check which specific checkpoint/deliverable causes failure and consider targeted tolerance relaxation. The financial content is sound.
