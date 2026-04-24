# Review: PR #141 - swap-curve-bootstrap-ois
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/141](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/141)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
A "medium" fixed-income task: debug and fix a provided Python template (`template.py`) that bootstraps a dual-curve USD swap curve (OIS discount + 3M LIBOR projection), reprices all input instruments, and values a specific IRS. The template has computational bugs the agent must find and fix.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`
- Checked trial results for all models
- Reviewed conventions.json reference and expected values in tests

### Trial Results
| Model | Reward |
|-------|--------|
| Haiku 4.5 | 0.0 |
| Opus 4.6 | 1.0 ✓ |
| Sonnet 4.5 | 1.0 ✓ |

### Scorecard
- Task contract / instruction: 5/5 — Excellent: provides conventions.json as single source of truth, template.py as starting point
- Verifier robustness: 5/5 — Tests pin exact OIS/LIBOR pillar values (DF, zero rate, forward) with tight tolerances, plus swap NPV. Hardcoded from oracle run.
- Difficulty calibration: 5/5 — Perfect separation: H45 fails, O46/S45 pass. This is exactly what "medium" should look like.
- Benchmark integrity: 4/5 — Tests contain exact expected values but the agent must produce them by fixing real bugs, not by hardcoding
- Financial correctness: 5/5 — Proper dual-curve framework, ACT/360 vs 30/360, semi-annual fixed vs quarterly float, log-linear DF interpolation

### Findings

#### [NIT] "dev/" directory included
The task includes a `dev/` directory with `HANDOFF.md`, `generate_data.py`, and `oracle_outputs_snapshot/`. This is development artifact that should probably be excluded from the task distribution to avoid giving the agent hints.

#### [NIT] The `dev/oracle_outputs_snapshot/` contains the exact expected output files (ois_discount_curve.csv, libor_forward_curve.csv, etc). If accessible to the agent at runtime, this is a major integrity issue — the agent could just copy these files. Need to verify these are excluded from the Docker image.

### Summary
Excellent benchmark task. Clean debug-and-fix format, proper financial conventions, good model discrimination (0/1/1). The only concern is whether the `dev/` directory is accessible at runtime.

### Verdict
**建议 Merge** — Well-calibrated, financially correct, good discrimination. Verify that `dev/` is not copied into the Docker image.
