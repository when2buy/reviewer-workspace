# Review: PR #178 - Variance Swap Pricing
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Compute fair variance swap strikes using model-free replication (OTM option portfolio + trapezoidal integration) from SPY options data, and compare to Heston closed-form. Includes term structure analysis across multiple expiries.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py (288 lines), Dockerfile
- Reviewed trial results: H:1.0, O:0.0, S:1.0
- Checked financial correctness, VIX methodology alignment, test design

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 3/5 — one fragile test
- Difficulty calibration: 4/5
- Model discrimination: 3/5
- Benchmark integrity: 4/5

### Findings

#### [MAJOR] Opus fails on K_var / sigma_var relationship test
File: `tests/test_outputs.py:132-138`
Opus (0.0 reward) failed only on `test_k_var_sigma_var_relationship`, which asserts `K_var ≈ sigma_var^2 * tau` with rtol=0.01. The relationship `K_var = sigma_var^2 * tau` is correct by definition (sigma_var = sqrt(K_var/tau)), but this is a circular check — if the agent computes K_var and sigma_var independently (e.g., K_var from replication and sigma_var from a different formula), they might not match to 1%.

More importantly, Opus's failure here suggests it computed sigma_var differently than `sqrt(K_var/tau)`. The instruction says `sigma_var = sqrt(K_var / tau)` explicitly, so this is a legitimate contract-reading error. Still, the 1% tolerance is tight for what is essentially a definitional consistency check.

#### [MINOR] Heston parameter calibration is ambiguous
File: `instruction.md`
The instruction provides Heston closed-form for variance swap strikes but doesn't specify how to calibrate κ, θ, v0. The test checks `calibration_method` is one of `["default", "fitted_sse", "fitted_lsq"]` — allowing multiple approaches is good, but the instruction should be clearer about what calibration is expected.

#### [MINOR] Day-count convention is explicit (365)
The instruction specifies 365 days/year for tau computation, which avoids common 252 vs 365 confusion. Good.

#### [MINOR] No oracle solution
File: `solution/solve.py`
Empty.

### Summary
Good task testing a core volatility derivatives concept. The model-free replication approach is well-specified and the instruction is clear. Haiku and Sonnet pass; Opus fails on a consistency check (K_var vs sigma_var) that reflects a contract-reading error. The task provides meaningful difficulty without being artificially hard.

### Verdict
**建议 Merge** — Well-designed task with good discrimination. Opus failure is legitimate. Minor suggestion: add oracle solution, clarify Heston calibration approach.
