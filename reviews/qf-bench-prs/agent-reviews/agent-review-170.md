# Review: PR #170 - Kou Double-Exponential Jump-Diffusion
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Calibrate a Kou double-exponential jump-diffusion model to SPY daily log-returns via MLE, price European calls using the Kou-Merton series formula across a 3×7 grid, extract implied vols, and compute conditional moments.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py, environment/Dockerfile
- Reviewed trial results for h45, opus46, s45 (all reward=0.0)
- Checked verifier tolerance calibration and financial correctness

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 2/5 — boundary bug + narrow ATM tolerances
- Difficulty calibration: 2/5 — 0/0/0 across all models raises red flags
- Model discrimination: 1/5 — no model passes
- Benchmark integrity: 4/5

### Findings

#### [CRITICAL] Strict inequality on parameter bounds causes false negatives
File: `tests/test_outputs.py:61`
The test uses `assert 2.1 < data["alpha"] < 50.0` with strict `<`. Opus produced `alpha=50.0` (at the optimization bound) and failed because `50.0 < 50.0` is false. The instruction specifies bounds `α ∈ [2.1, 50.0]` (closed interval). The test should use `<=` to match the stated bounds. Same issue applies to all parameter bound checks in the test.

**Impact:** Opus's solution was otherwise correct (all other 11 tests passed) but was rejected by this boundary bug. This alone would flip Opus from 0→1.

#### [CRITICAL] ATM price ranges are too narrow / likely miscalibrated
File: `tests/test_outputs.py:130-134`
The hardcoded ATM price ranges `{0.25: (15, 40), 0.5: (25, 55), 1.0: (40, 85)}` are failing both Haiku (14.48 for T=0.25) and Sonnet (32.29 for T=1.0). These ranges appear to be calibrated to one specific set of MLE parameters, but the Kou MLE is multi-modal — different local optima yield different but financially valid prices. The ranges should either be widened substantially or replaced with consistency checks (e.g., monotonicity, put-call parity, comparison to BS bounds).

**Impact:** Even correct implementations with different (valid) MLE calibrations will fail.

#### [MAJOR] No solution file provided
File: `solution/solve.py`
The solution file is empty. Without an oracle solution, there's no way to verify the test ranges were computed from a correct implementation. This undermines confidence in all hardcoded tolerance values.

#### [MINOR] Missing `set -euo pipefail` concern is absent
File: `tests/test.sh`
The test.sh uses `$?` after pytest correctly (no pipefail issue).

### Summary
The task is well-designed conceptually but the verifier has two blocking issues: (1) a strict-inequality bug on parameter bounds that rejects valid solutions at the boundary, and (2) ATM price ranges too narrow for a multi-modal MLE problem. The 0/0/0 reward pattern is a calibration problem, not evidence that the task is appropriately hard. No oracle solution is provided.

### Verdict
**不建议 Merge** — Verifier boundary bug and narrow tolerances cause false negatives across all models. Fix `<` to `<=` on bounds and widen ATM price ranges.
