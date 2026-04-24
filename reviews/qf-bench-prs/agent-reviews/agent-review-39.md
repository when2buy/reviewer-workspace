# Review: PR #39 - Corporate Action Adjustment
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Adjust historical equity prices for stock splits and cash dividends using a backward-adjustment algorithm. Agent produces adjusted price/volume series and summary statistics.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py, test.sh, Dockerfile
- Reviewed trial results for all three models
- Checked financial correctness of adjustment algorithm and dividend factor formula

### Trial Results
| Model | Reward |
|-------|--------|
| Haiku 4.5 | 1.0 |
| Opus 4.6 | 1.0 |
| Sonnet 4.5 | 1.0 |

### Scorecard
- Task contract / instruction: 5/5
- Verifier robustness: 3/5
- Difficulty calibration: 2/5
- Model discrimination: 1/5
- Benchmark integrity: 3/5

### Findings

#### [MAJOR] Zero model discrimination
All three models pass. The instruction fully prescribes the algorithm (chronological order, exact factor formulas, exact handling of splits vs dividends). No reasoning challenge remains.

#### [MINOR] Tests are mostly sanity checks, not precision checks
Tests verify: row count matches, last price unchanged, early adjusted < unadjusted×0.5, n_actions count, cum_factor < 0.5, total_dividends sum. These are property checks that any reasonable implementation would pass. No exact numerical comparison of adjusted prices.

#### [MINOR] test_total_dividends recomputes from input
`test_total_dividends` sums dividend amounts directly from the input JSON. This is correct but means the test only checks that the agent can sum — not that adjustments were applied correctly.

#### [NIT] Dividend adjustment formula uses ex-date close price
The instruction says to use `close_on_ex_date` for the dividend factor, but also says "if action date doesn't exist in price series, use nearest prior trading day." This edge case handling is well-specified.

### Summary
Well-structured corporate actions task with clear instruction and correct financial logic. The backward-adjustment approach is standard. However, all models pass easily — this provides no signal on model capability differentiation.

### Verdict
**建议 Merge**

Correct and clean. No blockers.
