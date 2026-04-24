# Review: PR #154 - barone-adesi-whaley
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/154](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/154)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Implement the Barone-Adesi & Whaley (1987) quadratic approximation for American options. Compare to BS European prices and CRR binomial tree benchmarks. Analyze early exercise premium, critical price surface, and dividend sensitivity.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked: financial correctness, test design, model discrimination
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

#### [MINOR] Good model discrimination (Opus+Sonnet pass, Haiku fails)
Haiku fails 6/36 tests including the ATM put value, binomial comparison relative differences, and dividend sensitivity. Opus and Sonnet both pass all 36. This is good discrimination — BAW requires understanding the quadratic approximation and iterative root-finding for the critical price, which Haiku gets partially wrong.

#### [MINOR] Instruction appropriately vague on BAW formulas
The instruction describes the method conceptually without giving exact formulas. The agent must know or derive the BAW quadratic approximation. This is appropriate for the difficulty level.

#### [NIT] Tests check both structural properties and some pinned values
`test_atm_put_T1` checks the ATM put within `25 < baw_put < 40` — a wide range. `test_call_reldiff_small` checks BAW-vs-CRR relative difference. Good mix of property and value tests.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 195s | 749,169in / 19,312out |
| Opus 4.6 | 1.0 | 215s | 345,841in / 13,376out |
| Sonnet 4.5 | 1.0 | 180s | 211,300in / 11,178out |


**Haiku key failures:**
```
E       assert np.float64(42.03670008887672) < 40
E       assert np.False_
E        +  where np.False_ = all()
E        +    where all = 0    0.030262\n1    0.040682\n2    0.058811\nName: call_reldiff, dtype: float64 < 0.01.all
E       assert np.False_
E        +  where np.False_ = all()
E        +    where all = 0    0.063209\n1    0.144659\n2    0.327246\nName: put_reldiff, dtype: float64 < 0.01.all
E       assert np.False_
```

### Summary
Clean, well-calibrated task. The BAW approximation is a standard but non-trivial quant method. Good discrimination (2/3 models pass). Tests are robust with appropriate tolerances. Financial correctness is sound — the structural tests (American ≥ European, premium non-negative, critical price monotonicity) are all correct.

### Verdict
**建议 Merge**

Correct, well-calibrated, good model discrimination.
