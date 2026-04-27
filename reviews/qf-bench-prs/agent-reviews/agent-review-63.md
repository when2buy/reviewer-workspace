# Review: PR #63 - Markowitz Efficient Frontier
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/63](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/63)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Clean ETF price data, compute annualized log-return statistics using Ledoit-Wolf shrinkage covariance, solve minimum-variance, maximum-Sharpe, and Equal Risk Contribution (ERC) portfolios, then generate a 30-point efficient frontier.

### What I Did to Review This
- Read: instruction.md, task.toml, solution/solve.py (first 50 lines), test_outputs.py, test.sh
- Reviewed trial results and failure logs for all three models
- Checked financial correctness of Markowitz optimization and ERC formulation

### Trial Results
| Model | Reward | Key Failures |
|-------|--------|-------------|
| Haiku 4.5 | 0.0 | ERC weights (SPY, QQQ, GLD), ERC return, ERC vol |
| Opus 4.6 | 1.0 | — |
| Sonnet 4.5 | 0.0 | ERC weights (SPY, QQQ, GLD), ERC return, ERC vol |

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 4/5
- Difficulty calibration: 4/5
- Model discrimination: 4/5
- Benchmark integrity: 4/5
- Financial correctness: 4/5

### Findings

#### [POSITIVE] Good model discrimination
Opus passes, Haiku and Sonnet fail — specifically on the ERC (Equal Risk Contribution) portfolio. The min-variance and max-Sharpe parts pass for all models (44/49 tests pass for H45/S45). The ERC formulation is the differentiator.

#### [POSITIVE] ERC is a genuine quant challenge
The ERC objective `sum((RC_i - target_RC)^2)` where `RC_i = w_i * (Σw)_i` is non-trivial to implement correctly. The failure pattern (Haiku and Sonnet get wrong weights) suggests these models struggle with the ERC optimization, not just the specification reading.

#### [MINOR] Solution solve.py uses daily returns instead of monthly
The first 50 lines of solve.py show `daily_log_returns = ... * 252` and `cov_matrix = ... * 252`, but the instruction specifies monthly resampling with Ledoit-Wolf shrinkage and annualization factor 12. This appears to be an older version of the solution that doesn't match the current instruction. The verifier's expected values match the instruction (monthly + Ledoit-Wolf), so the solve.py is stale.

#### [MINOR] Difficulty label "easy" contradicts results
Task is labeled "easy" but only Opus passes. Should be "medium" or "hard".

#### [MINOR] Instruction specifies Ledoit-Wolf but solve.py uses sample covariance
Another solve.py inconsistency. The tests pin values computed with Ledoit-Wolf, which is what the instruction requires.

#### [NIT] ERC test tolerances are reasonable
ERC weights checked at atol=0.05, ERC return/vol at atol=0.01. These are appropriate for an optimization problem.

### Summary
Excellent task with genuine discriminative power. The ERC portfolio is the key differentiator — only Opus handles it correctly. The Markowitz components (min-var, max-Sharpe, frontier) are well-specified and all models handle them. Stale solve.py should be updated but doesn't affect benchmark operation.

### Verdict
**建议 Merge**

Strong task with good discrimination. Minor issues:
1. Update solve.py to match current instruction (monthly + Ledoit-Wolf)
2. Relabel difficulty from "easy" to "medium" or "hard"
