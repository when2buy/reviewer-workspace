# Review: PR #101 - sec-8k-event-alpha
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/101](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/101)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Parse four SEC 8-K filing HTML documents, classify event types (guidance raise/cut, executive departure, debt financing), extract key numbers, compute alpha scores with severity and liquidity multipliers, and generate trading signals.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/verifier.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked trial results: H45=0.96, Opus46=1.0, S45=0.54
- Reviewed verifier's multi-phase partial credit system

### Scorecard
- Task contract / instruction: 5/5 — clear event definitions, explicit formulas, unambiguous
- Verifier robustness: 5/5 — multi-phase verification with partial credit (PERFECT/IMPERFECT/WRONG)
- Difficulty calibration: 4/5 — good separation: S45=0.54, H45=0.96, Opus46=1.0
- Model discrimination: 5/5 — excellent spread across models
- Benchmark integrity: 4/5 — requires actual HTML parsing, hard to hardcode
- Data realism: 5/5 — real SEC 8-K filings

### Findings

#### [MINOR] test.sh doesn't write reward.txt directly
File: [`tests/test.sh`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/e54e946/tasks/sec-8k-event-alpha/tests/test.sh)

Unlike other PRs, `test.sh` doesn't have the `echo 1/0 > reward.txt` pattern — the verifier.py handles reward writing. This is actually cleaner but inconsistent with other PRs in this batch.

#### [MINOR] Filing-to-event mapping is fixed (4 filings, 4 types)
The instruction states "Each filing maps to one event type" with exactly 4 filings and 4 event types. This means classification is partially constrained — once you identify 3, the 4th is forced. However, the extraction of specific numbers (guidance midpoints, debt amounts) still requires careful parsing.

#### [NIT] Difficulty rated "medium" but model spread suggests appropriate calibration
The H45→S45 spread from 0.96 to 0.54 is excellent for a medium task.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-sec-8k-event-alpha) | 0.961538 | 154s | 2,511,518in / 19,648out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-sec-8k-event-alpha) | 1.0 | 98s | 327,537in / 4,422out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-sec-8k-event-alpha) | 0.538462 | 92s | 329,417in / 4,247out |


**Haiku key failures:**
```
FAIL: test_verification
E       AssertionError: Verification failed: IMPERFECT
E       assert 'IMPERFECT' == 'PERFECT'
E
E         - PERFECT
E         + IMPERFECT
E         ? ++
```


**Sonnet key failures:**
```
FAIL: test_verification
E       AssertionError: Verification failed: WRONG
E       assert 'WRONG' == 'PERFECT'
E
E         - PERFECT
E         + WRONG
```

### Summary
This is one of the strongest tasks in the batch. It has real SEC filings, requires genuine document understanding, uses a well-designed partial credit verifier, and shows excellent model discrimination. The instruction is clear and the formulas are explicit.

### Verdict
**建议 Merge**

Well-calibrated task with excellent model discrimination (S45=0.54, H45=0.96, Opus46=1.0), real data, robust verifier with partial credit, and clear specification.
