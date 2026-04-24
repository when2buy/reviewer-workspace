# Review: PR #47 - merton-jump-diffusion
Reviewer: Grim 🔍 | Date: 2026-04-23

### What This PR Does
Agent prices European options under the Merton (1976) jump-diffusion model using the exact series formula and Monte Carlo, compares with Black-Scholes to quantify jump premium.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py, test.sh, solution/solve.py
- Noted: No Dockerfile, no trial results
- Verified Merton series formula correctness, test coverage

### Scorecard
- Task contract / instruction: 5/5
- Verifier robustness: 4/5
- Difficulty calibration: N/A (no trials)
- Benchmark integrity / anti-cheating: 3/5
- Financial correctness: 5/5

### Findings

#### [CRITICAL] Missing Dockerfile
No environment/Dockerfile. Task cannot run. No trial data.

#### [MINOR] Good financial tests
Tests check merton_call > bs_call (correct for negative mean jump + convexity), put-call parity, reasonable price range [5,25], MC within 3% of analytical. These are well-calibrated.

#### [MINOR] Solution is correct
Merton series formula with lambda' = lambda_j * (1+kappa_j), adjusted r_n and sigma_n per term — matches standard textbook derivation. MC uses single-step exact simulation with Poisson jumps, which is correct.

#### [MINOR] Instruction clearly derives all formulas
The instruction provides lambda', r_n, sigma_n formulas explicitly. This makes the task more about implementation than derivation, which is appropriate for "hard" difficulty.

#### [NIT] test_merton_prices_reasonable hardcodes range [5,25]
This is a reasonable range for ATM options with these parameters but could be derived from the params.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | no trial data | — | — |
| Opus 4.6 | no trial data | — | — |
| Sonnet 4.5 | no trial data | — | — |

### Summary
Excellent quant derivatives task with correct Merton jump-diffusion implementation, good financial tests including put-call parity and no-arbitrage checks. The only blocker is the missing Dockerfile.

### Verdict
**不建议 Merge**

Missing Dockerfile is a blocker. After adding Dockerfile + params.json, this would be a high-quality benchmark item ready to merge.
