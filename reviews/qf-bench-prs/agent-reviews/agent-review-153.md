# Review: PR #153 - asian-option-levy-curran
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/153](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/153)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Price arithmetic Asian options using three methods: exact geometric Asian (closed-form), Levy moment-matching approximation, and Curran geometric conditioning. Monte Carlo serves as a verification benchmark. Input is SPY daily OHLCV.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked: financial correctness, test design, tolerance calibration
- Reviewed: trial results for h45, opus46, s45

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 4 |
| Verifier robustness | 4 |
| Difficulty calibration | 4 |
| Model discrimination | 4 |
| Benchmark integrity / anti-cheating | 4 |

### Findings

#### [MINOR] Good model discrimination
Only Opus passes (25/25). Haiku and Sonnet both fail on `test_geo_less_than_arith` — the geometric average price must be ≤ arithmetic average price, a mathematically guaranteed property (AM-GM inequality). That both weaker models get this wrong indicates real implementation errors, not test brittleness.

#### [MINOR] Instruction is somewhat vague on analytical formulas
The instruction describes the Levy and Curran methods conceptually but doesn't give explicit formulas. This is appropriate for a "hard" task — agents need domain knowledge to implement correctly. However, it increases the risk that different valid implementations produce slightly different numbers.

#### [NIT] Tests use range-based checks rather than pinned values
Most tests are structural (positive prices, monotonicity, row counts) with a few pinned ATM ranges. This is good for robustness but means a subtly wrong implementation could still pass.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-asian-option-levy-curran) | 0.0 | 523s | 866,921in / 12,745out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-asian-option-levy-curran) | 1.0 | 125s | 113,310in / 6,535out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-asian-option-levy-curran) | 0.0 | 381s | 847,907in / 23,860out |


**Haiku key failures:**
```
E           AssertionError: geo_exact=47.050447420152864 > mc_arith=46.07294627521128 at K=652.7069999999999, T=0.5
E           assert 47.050447420152864 <= (46.07294627521128 + 0.01)
E       AssertionError: geo_less_than_arith_pct=72.22222222222223, expected in [80, 100]
E       assert 80.0 <= 72.22222222222223
```


**Sonnet key failures:**
```
E           AssertionError: geo_exact=55.61010916553004 > mc_arith=48.71423524497567 at K=652.7069999999999, T=0.5
E           assert 55.61010916553004 <= (48.71423524497567 + 0.01)
E       AssertionError: geo_less_than_arith_pct=50.0, expected in [80, 100]
E       assert 80.0 <= 50.0
```

### Summary
Well-designed task with good discrimination. The three pricing methods (exact geometric, Levy, Curran) test genuine quant finance knowledge. Only Opus passes, which is appropriate for "hard" difficulty. Tests are mostly property-based with reasonable tolerances.

### Verdict
**建议 Merge**

Correct financial content, good calibration, appropriate difficulty for "hard" label.
