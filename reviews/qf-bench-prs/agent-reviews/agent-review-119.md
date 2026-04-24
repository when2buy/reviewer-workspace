# Review: PR #119 - option-put-call-parity-forward-audit
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/119](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/119)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Audit option quotes for put-call parity violations: clean quotes (stale, crossed, one-sided), match call/put pairs, compute synthetic forwards, compare to theoretical forwards, identify violations, and compute implied borrow rates.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `solution/solve.py`
- Checked: put-call parity formula, synthetic forward computation, violation detection logic, verifier design

### Scorecard
- Task contract: 5/5 — clear specification of all cleaning rules, forward formulas, and output format
- Verifier robustness: 4/5 — covers structure and values but uses pinned expected values
- Difficulty calibration: N/A — no trial results available
- Financial correctness: 5/5 — put-call parity C - P = PV(F - K), synthetic forward = K + (C - P)/DF is correct
- Benchmark integrity: 3/5 — similar concern to PR #118

### Findings

#### [MAJOR] Complete expected values in test file (similar to PR #118)
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/7ab12bd/tasks/option-put-call-parity-forward-audit/tests/test_outputs.py)
Based on the test structure (I can see it follows the same author pattern as PR #118), expected values are likely fully pinned. With a small option chain, this creates hardcoding risk.

#### [MINOR] Synthetic forward uses bid/ask correctly
File: [`solution/solve.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/7ab12bd/tasks/option-put-call-parity-forward-audit/solution/solve.py)
`synthetic_forward_bid = K + (call_bid - put_ask) / DF` and `_ask = K + (call_ask - put_bid) / DF` — correctly uses the worst-case side for each bound. Good financial practice.

#### [MINOR] Implied borrow rate calculation
The solution correctly derives `implied_borrow = r - q - ln(F_synth/S) / T`, which inverts the carry model. Financially sound.

#### [POSITIVE] Good audit workflow design
The task represents a realistic options desk workflow: quote cleaning → pair matching → parity check → violation flagging. This is a practical skill.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | error reading | — | — |
| Opus 4.6 | error reading | — | — |
| Sonnet 4.5 | error reading | — | — |

### Summary
Well-designed options audit task with correct put-call parity implementation. The audit workflow (clean → match → check → flag) is realistic and practical. However, like PR #118 (same author), the task may have complete expected values in the test file, which creates integrity concerns for small datasets.

### Verdict
**需要 Human Review**

Same author as PR #118, likely similar integrity profile. No trial results available to assess calibration. Human should verify the test file doesn't expose too much of the answer for the given dataset size.
