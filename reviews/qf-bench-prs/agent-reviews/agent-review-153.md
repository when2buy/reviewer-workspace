# Review: PR #153 - asian-option-levy-curran
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

### Summary
Well-designed task with good discrimination. The three pricing methods (exact geometric, Levy, Curran) test genuine quant finance knowledge. Only Opus passes, which is appropriate for "hard" difficulty. Tests are mostly property-based with reasonable tolerances.

### Verdict
**建议 Merge**

Correct financial content, good calibration, appropriate difficulty for "hard" label.
