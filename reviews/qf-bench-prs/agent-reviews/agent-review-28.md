# Review: PR #28 - data-cleaning
Reviewer: Grim 🔍 | Date: 2026-04-23

### What This PR Does
Agent must clean dirty OHLCV CSV data (forward-fill NaNs, dedup dates, fix negatives, sort) and produce a clean CSV + JSON summary.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py, test.sh, Dockerfile
- Reviewed trial results: H45=1.0, Opus46=1.0, S45=1.0
- Checked test coverage, anti-cheat, calibration

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 3/5
- Difficulty calibration: 3/5
- Benchmark integrity / anti-cheating: 2/5
- Data realism / determinism: 3/5

### Findings

#### [MAJOR] All three models pass — task is too easy for "easy" label
The task is trivially solved by all models including Haiku 4.5 in ~28 seconds. For a benchmark, even "easy" tasks should provide some signal. This one provides zero discrimination.

#### [MAJOR] Tests verify against agent's own output, not oracle values
`test_results_json_mean_close` checks that `results.json` mean matches the CSV mean — but both are produced by the agent. If the agent applies cleaning incorrectly but consistently, all tests pass. The test hardcodes `len(df) == 14` which is the only real anchor, but there are no pinned numeric values for mean_close or date range.

#### [MINOR] No solution/solve.py provided
The solution directory appears empty. Oracle solution should be present for reproducibility.

#### [MINOR] Dockerfile missing sha256 pin
`FROM finance-bench-sandbox:latest` — no digest pin unlike PR#51's Dockerfile.

#### [NIT] Instruction says "fictional stock ticker" — synthetic data
Not real-world data, which weakens benchmark realism.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 1.0 | 54s | 220,519in / 1,369out |
| Opus 4.6 | 1.0 | 45s | 50,371in / 754out |
| Sonnet 4.5 | 1.0 | 56s | 102,733in / 1,228out |

### Summary
Task is trivially easy with zero model discrimination. Tests are self-referential (verify consistency, not correctness) except for the row count check. The 14-row hardcode is the only meaningful anchor — an agent could produce wrong values for everything else and still pass if internally consistent. No oracle solution present.

### Verdict
**需要 Human Review**

Task provides no discrimination signal (3/3 models pass trivially). Consider whether this belongs in the benchmark at all, or if tests need pinned oracle values to become meaningful.
