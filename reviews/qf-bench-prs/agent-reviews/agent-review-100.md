# Review: PR #100 - minimum-cost-equity-etf-hedger
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/100](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/100)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Given an equity portfolio, historical prices, and sector maps, construct a minimum-cost ETF hedge that achieves exact beta neutrality and exact sector neutrality via linear programming. Output betas, hedge weights, and summary metrics.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked trial results: H45=1.0, Opus46=1.0, S45=1.0

### Scorecard
- Task contract / instruction: 4/5 — clear specification with exact output formats
- Verifier robustness: 5/5 — tight numeric tolerances, reference-based
- Difficulty calibration: 2/5 — all three models pass perfectly
- Benchmark integrity: 3/5 — full answer in reference_data, but all-pass raises concern
- Data realism: 4/5 — realistic portfolio hedging scenario

### Findings

#### [MAJOR] Zero discrimination — all models score 1.0
All three models (H45, Opus46, S45) achieve perfect scores. A medium-difficulty task should ideally have some model separation. When all models pass, the task doesn't contribute to benchmark discrimination.

This could indicate:
1. The task is easier than "medium" — more like "easy"
2. The LP formulation is well-known and straightforward for current models
3. The instruction is detailed enough to be mechanical

#### [MINOR] Tolerances are very tight but still passed by all
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/58c6e66/tasks/minimum-cost-equity-etf-hedger/tests/test_outputs.py)

Beta tolerance `rtol=1e-6, atol=1e-8` and hedge notional tolerance `atol=1e-4` are extremely tight. The fact that all models hit these suggests the LP solution is unique and well-conditioned, which is good for determinism but means the task essentially has one correct answer.

#### [NIT] No canary GUID in task.toml
File: [`task.toml`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/58c6e66/tasks/minimum-cost-equity-etf-hedger/task.toml)

Missing the canary comment that other PRs include.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-minimum-cost-equity-etf-hedger) | 1.0 | 147s | 1,432,673in / 19,673out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-minimum-cost-equity-etf-hedger) | 1.0 | 100s | 176,245in / 4,684out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-minimum-cost-equity-etf-hedger) | 1.0 | 147s | 293,088in / 7,921out |

### Summary
Clean, well-specified task with a working environment and robust verifier. The main concern is that it provides zero model discrimination — all three models pass perfectly. Consider whether this task adds value to the benchmark given that it cannot separate model capabilities.

### Verdict
**需要 Human Review**

The task is technically correct and well-built, but all three models score 1.0, providing zero discrimination. A human should decide whether this is acceptable for the benchmark or whether the task needs to be harder (e.g., dirty data, ambiguous constraints, or less prescriptive instructions).
