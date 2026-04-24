# Review: PR #77 - cds-curve-stripping
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Bootstrap piecewise-constant hazard rates from CDS par spreads, construct the survival curve, price a risky bond, compute par-adjusted spread, and calculate recovery sensitivity. A technically demanding credit derivatives task.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, Dockerfile
- Checked: trial results for h45, opus46, s45 (all reward=0.0)
- Analyzed: failure patterns (identical across all models)

### Scorecard
- Task contract / instruction: 3/5
- Verifier robustness: 3/5
- Difficulty calibration: 5/5 — genuinely hard
- Model discrimination: 1/5 — all fail identically
- Benchmark integrity: 4/5

### Findings

#### [CRITICAL] All three models fail identically on all hazard rate / survival / premium / protection tests
All models fail the same 16 tests. The failures are in the core bootstrapping (hazard rates, survival probabilities, premium legs, protection legs). Since all downstream quantities depend on the bootstrapped curve, everything cascades.

The instruction specifies: "use the exact integral over the piecewise-constant hazard segment, not a simple point-in-time discount." This is the key subtlety — the premium and protection legs require integrating `exp(-λt)` exactly over each segment rather than using midpoint or endpoint approximations.

When all three models (including Opus) fail with similar errors, this suggests either:
1. The instruction is insufficiently specific about the exact integration method
2. The oracle values are based on a very particular implementation choice that isn't fully communicated

#### [MAJOR] Premium leg "accrued-on-default" convention unclear
File: `instruction.md`

The instruction says: "Each period's contribution must account for the possibility of default within the period — use the exact integral." But the standard CDS market convention includes an **accrued premium** payment at default (the protection buyer pays premium accrued from the last payment date to the default date). The test docstring hints at this ("with accrued-on-default") but the instruction doesn't explicitly specify it.

The difference between including and excluding accrued-on-default changes the premium leg by ~1-2%, which is enough to shift hazard rates outside the 5e-4 tolerance.

#### [MAJOR] Par-adjusted spread formula is non-standard
File: `instruction.md`

The formula `s̄ = c − r̂(T) − (P/FV − 1) / Π(T)` is a specific decomposition that isn't widely textbook-standard. When agents can't find this in reference material, they're likely to implement a different (also valid) spread measure. The instruction should either derive the formula more clearly or point to a specific reference.

#### [MINOR] Recovery sensitivity requires full re-bootstrap
The recovery sensitivity test requires re-bootstrapping the entire curve with R=0.41 instead of 0.40. This is computationally correct but adds complexity. Since all models already fail on the base case, this test provides no additional signal.

### Summary
Technically sound and genuinely hard task. The instruction covers the right concepts but leaves critical implementation details ambiguous — particularly the exact integration method for premium/protection legs and the accrued-on-default convention. All three models fail identically, which strongly suggests a spec gap rather than model weakness.

### Verdict
**不建议 Merge** — Universal failure across all models indicates spec insufficiency. The instruction needs to: (1) explicitly state the accrued-on-default convention, (2) provide the exact integral formulas for premium and protection legs, (3) clarify whether the hazard rate for each segment is the marginal (piecewise) rate. Once clarified, this would be an excellent "hard" credit task.
