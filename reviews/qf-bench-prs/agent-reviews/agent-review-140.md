# Review: PR #140 - localvol-barrier
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/140](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/140)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
A "hard" derivatives-pricing task: clean BTC option data from Deribit, pair calls/puts, construct a synthetic call-price surface, derive a Dupire local-volatility surface, and price a discretely monitored down-and-out call via local-vol Monte Carlo. Pipeline task where upstream errors cascade.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`
- Checked trial results and stdout for all models
- Reviewed financial conventions and test pinned values

### Trial Results
| Model | Reward |
|-------|--------|
| Haiku 4.5 | 0.0 |
| Opus 4.6 | 0.0 |
| Sonnet 4.5 | 0.0 |

### Scorecard
- Task contract / instruction: 4/5 — Well-specified pipeline with explicit conventions
- Verifier robustness: 4/5 — Tests pin intermediate values (101 cleaned rows, 50 paired nodes, 35 call surface nodes) plus exact numeric values for sample nodes
- Difficulty calibration: 2/5 — All models fail; zero discrimination
- Benchmark integrity: 3/5 — Tests contain pinned exact values for surface nodes (forward_usd, synthetic_call_usd, otm_side) which partially leak the solution
- Financial correctness: 4/5 — Zero discounting (r=q=0 for BTC) is a deliberate simplification, properly stated

### Findings

#### [MAJOR] Zero discrimination across all models
Opus46 gets close — stdout shows 27/34 tests passing, with failures mainly in surface node pinned values (small numeric discrepancies like 75042.6 vs 75037.5 for forward_usd). This suggests the task is borderline solvable but numerically fragile.

#### [MAJOR] Pinned intermediate values may be too tight
The tests pin exact intermediate values for surface nodes with `rtol=5e-3, atol=1e-2`. For a pipeline that involves BTC→USD conversion using forward proxies, paired node selection, and interpolation, these tolerances may be too tight. The Opus46 run shows it gets the pipeline structure right but fails on numeric precision.

#### [MINOR] Monte Carlo final price introduces randomness
The barrier pricing uses MC simulation. The task should specify a seed for determinism. The instruction mentions `task_rules.json` but doesn't explicitly state the MC seed requirement in the visible instruction excerpt.

#### [NIT] Using BTC option data is a nice touch — realistic and domain-specific.

### Summary
Well-designed derivatives pipeline task. Opus46 nearly passes (27/34 tests), suggesting the task is borderline — a good difficulty level for "hard". The main concern is whether numeric tolerances on intermediate values are too tight, causing a "correct but slightly different" solution to fail.

### Verdict
**需要 Human Review** — Close to passing for Opus. Human should verify whether the pinned intermediate tolerances (rtol=5e-3) are fair or need loosening. If Opus is failing for trivial numeric reasons, the task loses signal.
