# Review: PR #156 - bs-greeks-pde
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/156](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/156)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Compute the full set of Black-Scholes Greeks on a moneyness×maturity grid. Verify the BS PDE residual is zero using analytical Greeks. Verify put-call parity. Check Greek limiting behaviors.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked: financial correctness (PDE residual formula, put-call parity, Greek bounds), test calibration
- Reviewed: trial results for h45, opus46, s45

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 5 |
| Verifier robustness | 5 |
| Difficulty calibration | 4 |
| Model discrimination | 3 |
| Benchmark integrity / anti-cheating | 4 |

### Findings

#### [MINOR] Haiku fails by a single test — borderline discrimination
Haiku fails only `test_atm_vega_T100` (1/39). Opus and Sonnet pass all 39. The task is labeled "medium" which is accurate — BS Greeks are textbook formulas. The narrow failure (just one vega value off) suggests Haiku almost passes; this is weak discrimination.

#### [MINOR] PDE residual test is excellent
`test_call_pde_residual_near_zero` and `test_put_pde_residual_near_zero` check that Θ + (r-D)·S·Δ + ½σ²S²Γ - rV ≈ 0. This is a strong consistency check that validates all Greeks simultaneously. Well-designed.

#### [MINOR] Financial correctness is solid
The PDE formula in the instruction correctly includes the dividend yield D in the drift term. Put-call parity formula `C - P = S·e^{-DT} - K·e^{-rT}` is correct. Delta bounds account for `e^{-DT}`. All mathematically sound.

#### [NIT] Some tests pin specific values (e.g., ATM call price ≈ 23.848 with atol=0.5)
This is fine — the values come from analytical BS formulas with known inputs, so they should be highly deterministic.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 77s | 266,960in / 5,614out |
| Opus 4.6 | 1.0 | 84s | 101,475in / 3,759out |
| Sonnet 4.5 | 1.0 | 245s | 436,764in / 14,830out |


**Haiku key failures:**
```
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f7f10a6d070>(np.float64(2.5701924582363627), 257.02, atol=2.0)
E        +    where <function isclose at 0x7f7f10a6d070> = np.isclose
```

### Summary
Excellent task design. The PDE residual check is a particularly clever test that validates consistency across all Greeks. Financial content is correct. Tests are comprehensive (39 tests covering structure, values, properties, and PDE). The only weakness is marginal discrimination — Haiku fails by one test.

### Verdict
**建议 Merge**

Clean, correct, well-tested. Good benchmark item for the "medium" tier.
