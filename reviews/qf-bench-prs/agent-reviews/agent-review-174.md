# Review: PR #174 - Power Options
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Price European power options (payoff depends on S_T^α) using closed-form BS-like formulas, symmetric power calls, capped power calls, and verify against Monte Carlo. Includes put-call parity verification.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py (218 lines), Dockerfile
- Reviewed trial results: H:0.0, O:0.0, S:0.0
- Analyzed failure patterns across all three models

### Scorecard
- Task contract / instruction: 3/5 — incomplete closed-form formulas
- Verifier robustness: 3/5
- Difficulty calibration: 2/5 — 0/0/0 is a red flag
- Model discrimination: 1/5
- Benchmark integrity: 3/5

### Findings

#### [CRITICAL] Opus and Sonnet produce no output files at all
Both Opus and Sonnet trials resulted in 36 errors — all `FileNotFoundError` — meaning neither model produced any output files. This is catastrophic failure, not a close miss. When two frontier models can't even produce output, the instruction likely has an ambiguity or missing detail that prevents implementation.

**Likely cause:** The instruction describes closed-form formulas for power options but doesn't provide the actual formulas — it says "Price power options using the Black-Scholes-like formula with effective parameters" without giving the formula. The agent must derive it, which is a significant mathematical derivation. The instruction should either provide the formula or give a concrete reference.

#### [MAJOR] Haiku produces output but fails on MC tolerance and parity
Haiku (H:0.0) actually produced all files and passed 33/36 tests, failing on:
1. `test_mc_reasonably_close` — MC relative error > 5% for high-α options
2. `test_parity_holds` — parity check failed
3. `test_mc_errors_bounded` — max MC error exceeded bound

The MC tolerance of 5% may be too tight for power options with α=3 (S^3 has enormous variance). The parity failure suggests Haiku's formula derivation was slightly off.

#### [MAJOR] No oracle solution
File: `solution/solve.py`
Empty. For a task that requires deriving non-trivial formulas, this is a significant gap.

#### [MINOR] Task.toml uses non-standard format
File: `task.toml`
Uses `[task]` section with `name`, `description`, `authors` instead of the standard `[metadata]` format used by other PRs. Inconsistent.

### Summary
The 0/0/0 pattern with Opus and Sonnet producing zero output suggests the instruction is under-specified. The closed-form power option formulas are not provided — agents must derive them, which is a mathematical research task, not an implementation task. Haiku got closest but still failed on MC tolerance. Either provide the formulas explicitly or accept this as a research-difficulty task.

### Verdict
**不建议 Merge** — Instruction under-specifies the key formulas. Two frontier models produce no output at all. Provide explicit closed-form formulas or a concrete derivation path, and add an oracle solution.
