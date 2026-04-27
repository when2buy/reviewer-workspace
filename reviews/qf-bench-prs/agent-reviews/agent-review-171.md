# Review: PR #171 - Lookback Options
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/171](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/171)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Price fixed-strike and floating-strike lookback options using closed-form formulas (Goldman-Sosin-Gatto, Conze-Viswanathan) and validate against Monte Carlo simulation with real SPY data.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py (184 lines), Dockerfile
- Reviewed trial results: H:0.0, O:1.0, S:1.0
- Checked test robustness and financial correctness

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 4/5
- Difficulty calibration: 4/5 — good model discrimination
- Model discrimination: 4/5 — Haiku fails, Opus/Sonnet pass
- Benchmark integrity: 4/5

### Findings

#### [MINOR] Haiku failure is substantive
Haiku produced non-monotonic lookback prices (m=1.05: T=0.25 price=73.37 > T=0.5 price=60.17), indicating a genuine implementation error in the Conze-Viswanathan formula — not a verifier issue. This is healthy discrimination.

#### [MINOR] No oracle solution provided
File: [`solution/solve.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/7a8bc85/tasks/lookback-options/solution/solve.py)
Empty. Would be good to have for reference, but tests are reasonable sanity checks (monotonicity, positivity, row counts, MC validation flag) rather than pinned values, so this is less critical than PR#170.

#### [MINOR] Tests are mostly structural
Tests check positivity, monotonicity, row counts, and field existence — no pinned numerical values. This is actually good for lookback options where MC noise introduces variability, but it also means a subtly wrong closed-form formula that preserves monotonicity could pass.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-lookback-options) | 0.0 | 1195s | 6,207,252in / 101,717out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-lookback-options) | 1.0 | 1261s | 3,953,689in / 77,178out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-lookback-options) | 1.0 | 948s | 2,278,449in / 49,141out |


**Haiku key failures:**
```
E           AssertionError: Row 0: cf_price not positive
E           assert 0.0 > 0
E            +  where 0.0 = float('0.00')
E               AssertionError: T=0.25: prices not decreasing with K. Got [0.0, 0.0, 20.46, 73.37, 118.26]
E               assert 0.0 > 0.0
E               AssertionError: m=1.05: prices not increasing with T. Got [73.37, 60.17, 60.29]
E               assert 73.37 < 60.17
```

### Summary
Well-designed task with good model discrimination. Tests are structural but appropriate for a task involving MC validation. Haiku fails for genuine mathematical reasons. The instruction is clear and the test suite is robust without being brittle.

### Verdict
**建议 Merge** — Correct, well-calibrated, good discrimination between models.
