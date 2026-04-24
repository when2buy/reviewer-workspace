# Review: PR #132 - dirty-gap-momentum-aapl
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Clean dirty AAPL OHLCV data (duplicates, missing adj_open imputation, stale zero-volume rows), then backtest an overnight gap-momentum strategy with transaction costs and short borrow fees. Produce cleaned CSV, trade log, daily portfolio, Plotly chart, and performance metrics.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `solution/solve.sh`
- Checked: data cleaning rules, backtest logic, transaction cost model, performance metric formulas
- Reviewed trial outputs: H45 19/19 PASSED, Opus46 19/19 PASSED, S45 19/19 PASSED

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 5/5 |
| Verifier robustness | 4/5 |
| Difficulty calibration | 3/5 |
| Model discrimination | 2/5 |
| Benchmark integrity | 4/5 |

### Findings

#### [POSITIVE] All three models pass — oracle is well-calibrated
H45, Opus46, and S45 all achieve 19/19 PASSED. This confirms the oracle is correct, the tolerances are reasonable, and the instruction is clear enough for all tiers.

#### [MAJOR] No model discrimination — all pass equally
Scores are (H:1.0, O:1.0, S:1.0). While this proves the task is solvable, it provides zero signal about model capability differences. For a benchmark, this is a problem — the task may be too easy or too well-specified.

#### [POSITIVE] Instruction is exceptionally clear and complete
Every cleaning rule, backtest parameter, cost formula, and metric definition is explicitly stated. The `adj_open` imputation via adjustment ratio, the stale zero-volume detection, the `floor(cash/adj_open)` sizing — all precisely defined. This is a model instruction.

#### [MINOR] Tests check exact row count (1026)
File: `tests/test_outputs.py`
`assert len(df) == 1026` — exact match. This is fine given the deterministic cleaning rules, but any interpretation difference in stale-row detection would cause a hard failure.

#### [MINOR] Difficulty may be understated
File: `task.toml`
No difficulty level specified. Given all three models pass, this is likely "easy" difficulty, which is consistent with a single-stock data cleaning + simple backtest task.

#### [POSITIVE] Good test coverage
19 tests cover file existence, data cleaning validation, trade structure, metric precision, Plotly output, and consistency checks. The test for imputation correctness (`test_cleaning_rules_handle_imputation_and_duplicate_removal`) is particularly well-designed.

### Summary
Clean, well-specified task with perfect instruction quality. All three models pass, confirming correctness but providing no discriminative signal. This is a good "easy" benchmark item — it tests data handling and careful specification following. Consider pairing with harder tasks for meaningful difficulty calibration.

### Verdict
**建议 Merge**

Correct, well-calibrated, and solvable by all tiers. The lack of discrimination is a minor concern for benchmark design (suggests "easy" difficulty) but the task quality is high. Good as a baseline/warmup item in the benchmark suite.
