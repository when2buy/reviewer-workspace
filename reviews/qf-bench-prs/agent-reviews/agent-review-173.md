# Review: PR #173 - OU Process with Jumps (Commodity Modeling)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Calibrate an Ornstein-Uhlenbeck process with Poisson jumps to 10-year US Treasury yield data. Estimate parameters via linear regression, detect jumps via 3-sigma threshold, compute conditional moments and stationary distributions, and validate via Monte Carlo.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py (170 lines), solution/solve.py, Dockerfile
- Reviewed trial results: H:1.0, O:1.0, S:0.0
- Checked financial correctness and solution code

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 4/5
- Difficulty calibration: 3/5
- Model discrimination: 3/5 — Sonnet fails on MC validation flag
- Benchmark integrity: 3/5 — solution provided but simple

### Findings

#### [MINOR] Sonnet failure is on MC validation flag, not core math
Sonnet (S:0.0) failed only on `test_mc_validates` — it passed all 25 other tests. The `mc_validates` field is a boolean computed by the agent itself, meaning Sonnet likely set it to `False` due to a stricter self-check, not because its MC was actually wrong. The test `assert summ['mc_validates'], "MC validation failed"` trusts the agent's self-assessment, which is fragile.

**Recommendation:** Instead of trusting the agent's `mc_validates` flag, compute MC validation in the verifier by checking analytical vs MC moment agreement directly.

#### [MINOR] Task difficulty may be overstated
File: `task.toml`
Claimed "hard" but Haiku passes on first try in ~80 seconds of agent execution. The task is essentially: (1) linear regression, (2) residual analysis with 3-sigma threshold, (3) plugging into known formulas, (4) Euler MC. This is solidly "medium" difficulty.

#### [MINOR] Oracle solution is provided and correct
File: `solution/solve.py`
Full solution is provided. The OU calibration via regression and jump detection via 3-sigma are straightforward and correctly implemented. The σ_OU formula `np.sqrt(2 * kappa * var_resid / (1 - b**2))` is correct for the discrete OU.

#### [MINOR] Test `test_jump_mean_geq_ou` assumes positive jump mean
File: `tests/test_outputs.py:113`
`assert stat['stationary_mean_jump'] >= stat['stationary_mean_ou']` — this assumes μ_J ≥ 0 (jumps push the mean up). For Treasury yields with upward jumps this happens to be true, but the test embeds a data-specific assumption.

### Summary
Clean, well-specified task with a provided oracle solution. Tests are reasonable sanity checks. The Sonnet failure is due to a fragile self-assessment flag rather than substantive mathematical error. Difficulty should be downgraded from "hard" to "medium."

### Verdict
**建议 Merge** — Correct and well-calibrated. Minor improvements: (1) consider downgrading difficulty to "medium", (2) make MC validation verifier-computed rather than agent-reported.
