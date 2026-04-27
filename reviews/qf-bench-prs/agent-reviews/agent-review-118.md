# Review: PR #118 - perpetual-funding-ledger-reconciliation
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/118](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/118)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Reconcile a USDT-margined perpetual futures account: merge fills, fees, funding, and transfers into a time-ordered ledger, compute realized PnL under weighted-average cost, mark-to-market the closing position, and identify exceptions (unmatched transfers).

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `solution/solve.py`
- Checked: WAC PnL logic, ledger ordering, exception handling, verifier exactness

### Scorecard
- Task contract: 5/5 — extremely precise specification of every output field, format, and convention
- Verifier robustness: 5/5 — exact value matching with Decimal arithmetic; tests cover schema, arithmetic identities, position transitions, and cross-file consistency
- Difficulty calibration: N/A — no trial results available
- Financial correctness: 5/5 — WAC, fill-linked fees, funding cashflows all handled correctly
- Benchmark integrity: 3/5 — (see below)

### Findings

#### [CRITICAL] Verifier pins ALL expected values — essentially a lookup table
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/d95fa21/tasks/perpetual-funding-ledger-reconciliation/tests/test_outputs.py)
The test file contains:
- `EXPECTED_RESULTS` dict with every single output value
- `EXPECTED_EVENT_IDS` — exact event ordering
- `EXPECTED_RUNNING_CASH` — exact cash balance at every step
- `EXPECTED_EXCEPTION` — exact exception content
- `EXPECTED_SOLUTION` — exact intermediate values

If the agent can read `/tests/test_outputs.py` (violating Harbor assumptions), it can hardcode every answer. This is a significant integrity concern. The task has only 10 events — small enough that the complete answer is embedded in the test file.

#### [MAJOR] Small dataset makes the task trivial to hardcode
With only 10 events total, the entire ledger can be reconstructed by hand or by copying expected values. The task's value depends entirely on the Harbor assumption preventing test file access.

#### [MINOR] Good use of Decimal arithmetic in verifier
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/d95fa21/tasks/perpetual-funding-ledger-reconciliation/tests/test_outputs.py)
The verifier uses Python `Decimal` for exact cash path verification. This is rigorous and appropriate for a ledger reconciliation task.

#### [MINOR] Task is more data-engineering than quant finance
Despite being in the QF-Bench, this task tests ledger reconciliation / accounting skills rather than financial modeling. The quant content (WAC, mark-to-market) is basic.

#### [NIT] Missing canary GUID in task.toml
File: [`task.toml`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/d95fa21/tasks/perpetual-funding-ledger-reconciliation/task.toml)
No canary comment, unlike most other tasks. The instruction.md has a different GUID than the standard one.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-perpetual-funding-ledger-reconciliation) | error reading | — | — |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-perpetual-funding-ledger-reconciliation) | error reading | — | — |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-perpetual-funding-ledger-reconciliation) | error reading | — | — |

### Summary
Well-specified ledger reconciliation task with an extremely thorough verifier. However, the small dataset (10 events) combined with complete expected values in the test file creates a significant hardcoding risk under weak Harbor assumptions. The task tests data engineering more than quantitative finance.

### Verdict
**需要 Human Review**

The integrity concern (complete answer in test file + small dataset) needs human judgment. If Harbor isolation is trusted, the task is fine. If not, the answer leakage makes it unsuitable as a benchmark item.
