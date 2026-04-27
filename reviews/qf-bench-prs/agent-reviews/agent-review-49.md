# Review: PR #49 - rough-vol-rbgergomi
Reviewer: Grim 🔍 | Date: 2026-04-23

### What This PR Does
Agent simulates the rough Bergomi (rBergomi) model via fractional Brownian motion, prices options at multiple strikes via Monte Carlo, inverts Black-Scholes for implied volatilities, and computes the vol smile/skew.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py, test.sh, solution/solve.py
- Noted: No Dockerfile, no trial results
- Verified fBm simulation methodology, test coverage

### Scorecard
- Task contract / instruction: 3/5
- Verifier robustness: 3/5
- Difficulty calibration: N/A (no trials)
- Benchmark integrity / anti-cheating: 3/5
- Financial correctness: 4/5

### Findings

#### [CRITICAL] Missing Dockerfile
No environment/Dockerfile. Cannot run.

#### [MAJOR] Instruction is overly prescriptive and confusing on fBm simulation
The instruction describes multiple approaches for fBm discretization (Cholesky, then "simpler approximation" via Riemann-Liouville convolution, then Euler scheme) in a contradictory way. Lines like "Actually, use this simpler scheme" mid-instruction are confusing. The kernel normalization `((k+1)^(H+0.5) - k^(H+0.5))` is stated without clear derivation context.

The solution uses FFT convolution with proper C_H = 1/Gamma(H+0.5) normalization, which is more sophisticated than what the instruction describes. This mismatch between instruction and solution could cause agents to implement the wrong approach.

#### [MAJOR] Tests are very lenient
Tests only check: skew < 0, 0.05 < atm_iv < 1.0, all IVs positive, IV[80] > IV[120], no extreme jumps between adjacent strikes. These are qualitative structural checks. An agent producing garbage IVs could pass as long as they decrease from left to right and are in (0.05, 1.0).

#### [MINOR] difficulty="very_hard" — plausible
rBergomi with fBm simulation + BS inversion is genuinely challenging. The "very_hard" label is appropriate.

#### [MINOR] Solution uses FFT convolution — good performance
O(n log n) per path instead of O(n²) naive loop. This is the right approach.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-rough-vol-rbgergomi) | no trial data | — | — |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-rough-vol-rbgergomi) | no trial data | — | — |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-rough-vol-rbgergomi) | no trial data | — | — |

### Summary
Interesting and genuinely hard rough volatility task. However: missing Dockerfile blocks execution, instruction is confusing with multiple contradictory fBm approaches, and tests are too lenient to validate correctness.

### Verdict
**不建议 Merge**

Missing Dockerfile + confusing instruction + lenient tests. Needs: (1) Dockerfile, (2) cleaner instruction picking one fBm method, (3) tighter test tolerances or oracle-pinned IV values.
