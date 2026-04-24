# Review: PR #52 - ust-carry-roll-down-attribution
Reviewer: Grim 🔍 | Date: 2026-04-23

### What This PR Does
Agent computes position-level holding-period attribution for a UST portfolio: opening dirty value, carry, roll-down, curve shock P&L, coupon cash, ending dirty value, and verifies the attribution identity sums to residual.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py, test.sh, solution/solve.py, Dockerfile
- Reviewed trial results: H45=0.0, Opus46=1.0, S45=1.0
- Checked test pinned values, attribution identity, cross-file consistency

### Scorecard
- Task contract / instruction: 5/5
- Verifier robustness: 5/5
- Difficulty calibration: 4/5
- Benchmark integrity / anti-cheating: 4/5
- Financial correctness: 5/5

### Findings

#### [MINOR] Haiku fails but Opus/Sonnet pass — good discrimination
Haiku produced wrong `portfolio_identity_lhs` (1.07B vs expected ~10.9M), suggesting it misunderstood the quantity/price scaling. Opus and Sonnet both pass perfectly. This shows meaningful model discrimination at the frontier boundary.

#### [MINOR] Tests pin exact portfolio totals — strong verification
`EXPECTED_PORTFOLIO_TOTALS` hardcodes exact values for all 7 attribution components. Tests check 6-decimal precision, CSV format compliance, cross-file sum consistency (position rows → portfolio totals), and solution.json intermediates. This is thorough.

#### [MINOR] Clean task contract
Instruction clearly specifies the attribution identity, output schemas, and file formats. The `per_100` convention in input data (carry_per_100, roll_down_per_100) requires the agent to understand fixed-income pricing conventions — this is a genuine domain knowledge test.

#### [MINOR] Real-world UST portfolio context
Three positions (2Y, 5Y, 10Y) with realistic dirty prices, carry/roll-down values, and coupon cashflows. Small but representative.

#### [NIT] Only 3 positions — could be more complex
A larger portfolio would increase difficulty, but the current size is sufficient for testing the attribution logic.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 51s | 322,176in / 6,903out |
| Opus 4.6 | 1.0 | 76s | 152,715in / 3,455out |
| Sonnet 4.5 | 1.0 | 76s | 120,079in / 4,032out |


**Haiku key failures:**
```
FAIL: test_results_json_schema_identity_and_expected_totals
E           assert False
E            +  where False = <built-in function isclose>(1095375250.0, 10953752.5, abs_tol=1e-06)
E            +    where <built-in function isclose> = math.isclose
FAIL: test_position_rows_sum_to_portfolio_totals
E           AssertionError: assert Decimal('1095375250.000000') == Decimal('10953752.500000')
E            +  where Decimal('10953752.500000') = Decimal('10953752.500000')
FAIL: test_solution_json_schema_and_cross_file_checks
```

### Summary
Excellent fixed-income attribution task. Clean specification, exact pinned values, proper cross-file consistency checks. Haiku's failure is substantive (wrong scaling), not trivial (format mismatch), which demonstrates good calibration.

### Verdict
**建议 Merge**

Well-calibrated, correctly specified, strong verification. Ready for production.
