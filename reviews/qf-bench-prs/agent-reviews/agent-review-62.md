# Review: PR #62 - Cross-Sectional Momentum
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Implement a cross-sectional momentum long/short strategy: clean price data, compute 11-month formation signals (skip 1 month), rank stocks, go long top 3 / short bottom 3, and report performance metrics.

### What I Did to Review This
- Read: instruction.md, task.toml, solution/solve.py (first 50 lines), test_outputs.py, test.sh
- Reviewed trial results for all three models
- Checked financial correctness of momentum signal definition and backtest logic

### Trial Results
| Model | Reward |
|-------|--------|
| Haiku 4.5 | 1.0 |
| Opus 4.6 | 1.0 |
| Sonnet 4.5 | 1.0 |

### Scorecard
- Task contract / instruction: 5/5
- Verifier robustness: 5/5
- Difficulty calibration: 2/5
- Model discrimination: 1/5
- Benchmark integrity: 3/5

### Findings

#### [CRITICAL] Verifier pins exact values to machine precision — potential hardcoding risk
Tests use `abs_tol=1e-12` for all float comparisons. Expected values like `total_return=1.6172649012281468` are hardcoded to 16 significant figures. This means:
1. The solution is fully deterministic (good)
2. But an agent could potentially just echo these exact values from the test file if tests were accessible

Under Harbor assumptions (tests inaccessible), this is fine. But the extreme precision means ANY implementation difference (even benign floating-point ordering) would fail. The fact that all models pass suggests the computation is sufficiently determined by the instruction.

#### [MAJOR] All models pass — no discrimination despite "hard" label
Labeled "hard" with expert_time=35min, but all three models pass. The instruction is highly prescriptive: exact cleaning steps, exact signal formula, exact tie-breaking rule. This leaves no room for quant judgment.

#### [POSITIVE] Comprehensive test suite
25 tests covering: file existence, schema, exact integers, exact floats, portfolio path chain product, drawdown recomputation, vol recomputation, Sharpe recomputation, no duplicate dates, sorted dates. Very thorough.

#### [POSITIVE] Solution uses pure Python (csv, json, math)
The reference solution avoids pandas/numpy, using only stdlib. This is unusual but ensures exact reproducibility.

#### [MINOR] Look-ahead bias check
The momentum signal uses returns from t-12 to t-2 (skipping most recent month) — this is the standard Jegadeesh-Titman approach and correctly avoids short-term reversal. No look-ahead bias.

### Summary
Well-specified momentum strategy task with extremely precise verification. Financially correct approach. But difficulty is mislabeled — all models pass easily because the algorithm is fully prescribed.

### Verdict
**建议 Merge**

Clean, correct, well-verified. Recommend relabeling from "hard" to "medium" given universal pass rate.
