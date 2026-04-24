# Review: PR #101 - sec-8k-event-alpha
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
File: `tests/test.sh`

Unlike other PRs, `test.sh` doesn't have the `echo 1/0 > reward.txt` pattern — the verifier.py handles reward writing. This is actually cleaner but inconsistent with other PRs in this batch.

#### [MINOR] Filing-to-event mapping is fixed (4 filings, 4 types)
The instruction states "Each filing maps to one event type" with exactly 4 filings and 4 event types. This means classification is partially constrained — once you identify 3, the 4th is forced. However, the extraction of specific numbers (guidance midpoints, debt amounts) still requires careful parsing.

#### [NIT] Difficulty rated "medium" but model spread suggests appropriate calibration
The H45→S45 spread from 0.96 to 0.54 is excellent for a medium task.

### Summary
This is one of the strongest tasks in the batch. It has real SEC filings, requires genuine document understanding, uses a well-designed partial credit verifier, and shows excellent model discrimination. The instruction is clear and the formulas are explicit.

### Verdict
**建议 Merge**

Well-calibrated task with excellent model discrimination (S45=0.54, H45=0.96, Opus46=1.0), real data, robust verifier with partial credit, and clear specification.
