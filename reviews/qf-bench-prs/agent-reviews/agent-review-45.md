# Review: PR #45 - heston-mc-pricing
Reviewer: Grim 🔍 | Date: 2026-04-23

### What This PR Does
Agent prices European options under the Heston stochastic volatility model using Monte Carlo simulation (Euler-Maruyama with antithetic variates) and semi-analytical characteristic function inversion, then compares results.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py, test.sh, solution/solve.py
- Noted: No Dockerfile present, no trial results (all N/A)
- Checked financial correctness of solution, test robustness

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 4/5
- Difficulty calibration: N/A (no trial data)
- Benchmark integrity / anti-cheating: 3/5
- Financial correctness: 4/5

### Findings

#### [CRITICAL] Missing Dockerfile
No `environment/Dockerfile` found. The task cannot be run without it. All trials show N/A because the environment cannot be built.

#### [MAJOR] Tests read /app/params.json but instruction doesn't mention it
`test_analytical_put_call_parity` and other tests load `/app/params.json` to get S0, K, r, T. But the instruction hardcodes these parameters inline. The Dockerfile should COPY a params.json, but since there's no Dockerfile, this is unverifiable. The instruction should explicitly state params.json exists.

#### [MINOR] Solution uses Albrecher formulation — good
The solution correctly uses the "Little Heston Trap" (Albrecher et al. 2007) formulation to avoid branch-cut issues. This is the correct approach for production-quality Heston pricing.

#### [MINOR] Tests have good no-arbitrage checks
Tests check put-call parity, call > intrinsic, call < spot, call > put for positive rate. These are financially meaningful structural tests.

#### [NIT] seed=42 specified but tolerance is 2% — reasonable for 100K paths
The MC tolerance is well-calibrated for the path count.

### Summary
Well-designed quant derivatives task with correct financial modeling and good structural tests. However, the task is **completely non-functional** due to missing Dockerfile. No trial data exists.

### Verdict
**不建议 Merge**

Missing Dockerfile is a blocker. Task cannot run. Once Dockerfile is added with params.json, this would be a good benchmark item — re-review after fix.
