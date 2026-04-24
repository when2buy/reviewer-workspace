# Review: PR #128 - etf-cross-asset-lead-lag
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/128](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/128)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Compute lead-lag relationships across 10 ETFs using lagged correlation asymmetry with Fisher-z significance gating. Split into in-sample/out-of-sample, remove market factor via residualization, and check temporal stability of top pairs.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `solution/solve.py`, `solution/solve.sh`
- Checked: lagged correlation computation, Fisher-z significance gate, market model residualization, test pinned values
- Reviewed trial outputs: H45 12/24 failed, Opus46 1/24 failed, S45 1/24 failed

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 4/5 |
| Verifier robustness | 3/5 |
| Difficulty calibration | 3/5 |
| Model discrimination | 3/5 |
| Benchmark integrity | 3/5 |

### Findings

#### [CRITICAL] All models score 0.0 despite Opus46 and S45 passing 23/24 tests
The provided scores are (H:0.0, O:0.0, S:0.0), but trial results show Opus46 fails only 1 test (`test_persistence_summary_matches_reference`) and S45 fails only 1 test (`test_dimensions_and_sample_split`). The strict 0/1 reward means near-perfect performance still gets 0.

#### [MAJOR] Test values are pinned to 6 decimal places
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/93ff709/tasks/etf-cross-asset-lead-lag/tests/test_outputs.py)
Tests check exact values like `raw_top1_asymmetry=0.166512` with atol=1e-6, `tlt_beta_to_spy=-0.273395` with atol=1e-6. While the instruction specifies `numpy.corrcoef` and exact slicing conventions, 6-decimal precision leaves zero room for floating-point differences across implementations.

#### [MAJOR] Answer leakage via pinned test values
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/93ff709/tasks/etf-cross-asset-lead-lag/tests/test_outputs.py)
The test file contains the complete solution: top leader/lagger pairs ("LQD", "VNQ"), exact asymmetry values, beta coefficients, rank bands, and process counts. This is visible to agents at test time under Harbor assumptions? If agents can read test files, the answers are fully leaked.

#### [POSITIVE] Instruction is exceptionally detailed
The instruction specifies exact correlation slicing conventions, Fisher-z formula with the exact z-critical value (1.959963984540054), significance gating, and sorting conventions. This level of specificity is appropriate for a reproducibility benchmark.

#### [POSITIVE] Good model discrimination
H45 fails 12/24 tests while Opus46 and S45 fail only 1/24. This shows genuine discrimination between model tiers. The task would be well-calibrated if the verifier used partial credit.

#### [MINOR] `test_dimensions_and_sample_split` checks exact dates
The test checks `in_sample_start: "2018-01-03"` — the first return date. An agent computing returns differently (e.g., including or excluding the first price date) would fail this check.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-etf-cross-asset-lead-lag) | 0.0 | 106s | 308,506in / 11,000out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-etf-cross-asset-lead-lag) | 0.0 | 147s | 162,612in / 9,953out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-etf-cross-asset-lead-lag) | 0.0 | 157s | 286,420in / 10,218out |


**Haiku key failures:**
```
FAIL: test_solution_intermediates_reference_values
E           assert np.False_
E            +  where np.False_ = <function isclose at 0x7f7879f271b0>(0.162535, 0.11204929713296363, atol=1e-06)
E            +    where <function isclose at 0x7f7879f271b0> = np.isclose
FAIL: test_log_returns_not_simple_returns
E       assert 0.162535 < 0.116
FAIL: test_top_lead_lag_pairs_match_reference
E           assert np.False_
```


**Opus key failures:**
```
FAIL: test_persistence_summary_matches_reference
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7fce9105c8b0>(0.089753, 0.08975531935486965, atol=1e-06)
E        +    where <function isclose at 0x7fce9105c8b0> = np.isclose
```

### Summary
Well-designed lead-lag analysis task with excellent instruction specificity and good model discrimination (H45 clearly worse than Opus46/S45). The main issues are: (1) strict 0/1 scoring wastes the discrimination signal — Opus46 and S45 are essentially correct but score 0, and (2) test values at 1e-6 tolerance are too tight for a benchmark. With tolerance relaxation or partial credit, this would be a strong task.

### Verdict
**需要 Human Review**

Opus46 and S45 each fail only 1 of 24 tests — they're essentially correct. The task has real discrimination value but the strict verifier + tight tolerances waste it. Human should decide: (1) relax the 1-2 failing tests, or (2) adopt partial credit scoring. The financial content and instruction quality are strong.
