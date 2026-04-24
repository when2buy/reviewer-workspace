# Review: PR #139 - mtm-xccy-basis-desk
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
A "hard" cross-currency rates task: price and risk-manage a live GBP/USD mark-to-market cross-currency basis swap. Requires quote cleaning, OIS/LIBOR curve bootstrapping, FX forward curve construction, cashflow scheduling, swap valuation, and 8 stress scenarios. Very desk-style workflow.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`
- Checked trial results and stdout for all models
- Reviewed reference data files (checkpoints.json, expected.json)

### Trial Results
| Model | Reward |
|-------|--------|
| Haiku 4.5 | 0.0 |
| Opus 4.6 | 0.0 |
| Sonnet 4.5 | 0.0 |

### Scorecard
- Task contract / instruction: 5/5 — Extremely detailed, real-desk workflow with explicit conventions
- Verifier robustness: 4/5 — Uses reference_data/checkpoints.json and expected.json for comparison
- Difficulty calibration: 2/5 — All models fail; zero discrimination
- Benchmark integrity: 4/5 — Reference data in tests/reference_data/ but not trivially exploitable
- Financial correctness: 5/5 — Proper dual-curve framework, ACT/360 vs ACT/365F, FX forward conventions

### Findings

#### [MAJOR] Zero discrimination across all models
All three score 0.0. Opus46 stdout shows 10/12 tests failing. The task is genuinely hard (cross-currency basis swap MTM with stress scenarios) but provides no signal if nobody passes.

#### [MINOR] Instruction is very long and specification-heavy
The instruction covers quote cleaning, 4 curves, FX forwards, cashflow scheduling, swap valuation, 8 stress scenarios, consistency checks, and a reconciliation sheet. This is realistic for a desk workflow but may be too many moving parts for a single benchmark task.

#### [NIT] Good financial practice: day count conventions, FRA quote adjustments, basis curve reconciliation are all properly specified.

### Summary
Excellent financial-engineering task with proper conventions and real desk-style complexity. The problem is that no model can solve it, yielding zero benchmark signal. The task would be a strong addition if at least one frontier model could pass.

### Verdict
**需要 Human Review** — Financially correct and well-designed, but zero discrimination. Human should judge whether this is an acceptable "aspirational hard" task or needs simplification.
