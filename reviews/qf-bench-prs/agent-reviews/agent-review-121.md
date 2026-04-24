# Review: PR #121 - alpha-hedge-strategy
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/121](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/121)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Agent must clean stock return data, construct a cross-sectional momentum alpha signal (rolling cumulative return z-score), run a monthly-rebalanced long-short backtest with transaction costs, and regress strategy returns on Fama-French factors to decompose alpha vs factor exposure. Outputs `results.json` and `solution.json` with ~10 checkpoints.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/verifier.py`, `solution/solve.sh`, `tests/reference_data/expected.json`, `tests/reference_data/checkpoints.json`, `environment/data/params.json` (structure)
- Checked: oracle solution logic, tolerance calibration, trial results, verifier architecture
- Reviewed trial outputs: H45 FAILED, Opus46 PASSED, S45 PASSED

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 4/5 |
| Verifier robustness | 4/5 |
| Difficulty calibration | 3/5 |
| Model discrimination | 3/5 |
| Benchmark integrity / anti-cheating | 4/5 |
| Data realism / determinism | 4/5 |

### Findings

#### [MINOR] Instruction leaves "cross-sectional alpha signal" slightly ambiguous
File: [`instruction.md`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/9ba8da1/tasks/alpha-hedge-strategy/instruction.md)
The instruction says "build a per-stock signal based on the stock's recent return behaviour over that lookback" without explicitly saying "rolling cumulative return." The oracle uses `np.sum(window, axis=0)` (cumulative simple return sum). An agent could reasonably use geometric return, Sharpe, or other momentum signals. The tolerances are generous enough (rtol 0.15–0.3) that this may still pass, but it's a spec gap.

#### [MINOR] Oracle uses `np.sum` of simple returns as cumulative return
File: [`solution/solve.sh`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/9ba8da1/tasks/alpha-hedge-strategy/solution/solve.sh)
This is an approximation—summing simple returns rather than compounding. For a benchmark task, this is acceptable given the short lookback, but it's worth noting as a convention choice.

#### [NIT] Tolerances are generous
File: [`tests/reference_data/expected.json`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/9ba8da1/tasks/alpha-hedge-strategy/tests/reference_data/expected.json)
`sharpe_ratio` has rtol=0.2 + atol=0.15, `market_beta_residual` has rtol=0.3 + atol=0.15. These are quite wide, which reduces discriminative power but increases robustness to minor implementation differences.

#### [POSITIVE] Good multi-phase verifier design
The generic verifier with CC (deliverables) + CP (checkpoints) + concept graph is well-structured. Canary strings are present. The verifier doesn't contain the oracle solution—it reads from `reference_data/expected.json`.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-alpha-hedge-strategy) | 0.635714 | 71s | 307,102in / 4,161out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-alpha-hedge-strategy) | 1.0 | 102s | 153,164in / 3,645out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-alpha-hedge-strategy) | 1.0 | 108s | 199,730in / 4,684out |


**Haiku key failures:**
```
FAIL: test_verification
E       AssertionError: Verification failed: WRONG
E       assert 'WRONG' == 'PERFECT'
E
E         - PERFECT
E         + WRONG
```

### Summary
Well-constructed cross-domain task combining portfolio construction, backtesting, and factor attribution. Instruction is mostly clear but the alpha signal construction could be more explicit. Trial results show good discrimination: H45 fails while frontier models pass. Tolerances are generous but reasonable for a multi-step pipeline.

### Verdict
**建议 Merge**

Solid task with good calibration. The instruction ambiguity on signal construction is minor and the tolerances accommodate reasonable interpretations.
