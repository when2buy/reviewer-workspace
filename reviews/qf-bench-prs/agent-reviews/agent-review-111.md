# Review: PR #111 - historical-var-data-prep
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/111](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/111)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Clean a dirty returns CSV (multiple date formats, non-trading days, duplicates, outliers, NaNs) and compute historical 95%/99% VaR for an equal-weight 5-ETF portfolio.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `solution/solve.sh`
- Checked: cleaning pipeline ordering, VaR formula, verifier logic

### Scorecard
- Task contract: 5/5 — canonical pipeline ordering explicitly stated with per-step counts
- Verifier robustness: 5/5 — exact counts plus numerical VaR checks
- Difficulty calibration: 3/5 — H:1.0, O:1.0, S:1.0 (all pass); rated "easy" which is consistent
- Benchmark integrity: 4/5 — pinned counts and values in tests
- Data realism: 4/5 — synthetic dirty data but representative of real issues

### Findings

#### [MINOR] Zero discrimination — all models pass
H:1.0, O:1.0, S:1.0. The task is rated "easy" and all models solve it. This is expected for a data-prep task but provides no differentiation signal among models.

#### [MINOR] Cleaning pipeline is fully specified — little room for agent reasoning
The instruction specifies exact step ordering, exact filter thresholds, and exact conventions (`method='linear'`, keep last duplicate, etc.). This is good for determinism but reduces the task to recipe-following.

#### [NIT] Good use of trading calendar as external reference
Shipping `trading_calendar.csv` rather than requiring the agent to compute NYSE holidays is a clean design choice.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 1.0 | 63s | 277,470in / 3,472out |
| Opus 4.6 | 1.0 | 80s | 228,037in / 2,768out |
| Sonnet 4.5 | 1.0 | 112s | 177,261in / 3,529out |

### Summary
Clean, well-specified data-prep task. Correct VaR conventions. The "easy" difficulty rating is honest — all models pass. Useful as a baseline sanity check in the benchmark suite but provides no model discrimination.

### Verdict
**建议 Merge**

Correct and clean. The zero discrimination is consistent with its "easy" rating.
