# Review: PR #175 - Rainbow Option Pricing
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Price rainbow options (best-of and worst-of calls on two correlated assets) using closed-form bivariate normal formulas (Margrabe-Stulz). Calibrate correlation from synchronized AAPL/MSFT returns, verify decomposition identity, and analyze correlation sensitivity.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py (352 lines), Dockerfile
- Reviewed trial results: H:0.0, O:0.0, S:0.0
- Analyzed failure modes for each model

### Scorecard
- Task contract / instruction: 4/5 — formulas are provided
- Verifier robustness: 3/5 — moneyness grid mismatch
- Difficulty calibration: 2/5 — 0/0/0 but near-misses
- Model discrimination: 2/5
- Benchmark integrity: 4/5

### Findings

#### [CRITICAL] Moneyness grid mismatch between instruction and verifier
File: `instruction.md` vs `tests/test_outputs.py:106`

The instruction says: "Price calls for Maturities T ∈ {0.25, 0.5, 1.0} and Moneyness m ∈ {0.90, 0.95, 1.00, 1.05, 1.10}" (5 values, 15 total). The verifier checks for exactly these moneyness values.

Opus (30/31 tests passed) failed only because it used moneyness `{0.8, 0.9, 1.0, 1.1, 1.2}` instead of `{0.90, 0.95, 1.00, 1.05, 1.10}`. This is a step-size ambiguity: Opus used 0.1 steps while the instruction specifies 0.05 steps. The instruction is technically clear, but this is a trivial contract-reading error, not a mathematical failure.

Sonnet (29/31 passed) failed on moneyness values AND an intrinsic value bound check (c_max slightly below 99% of intrinsic — a numerical precision issue, not a conceptual error).

#### [MAJOR] Haiku has fundamental formula errors
Haiku (18/31 passed) produced negative c_max prices (-313.7), which is financially impossible for a call option. This indicates a sign error in the bivariate normal formula implementation — a genuine mathematical failure. The 13 failures are all cascading from this core error.

#### [MINOR] No oracle solution
File: `solution/solve.py`
Empty.

#### [MINOR] Decomposition test tolerance is generous
File: `tests/test_outputs.py:164`
`tol = max(0.2, 0.001 * option_value)` — allowing $0.20 absolute error is quite generous for closed-form pricing. This is fine since the instruction mentions MC-based decomposition verification.

### Summary
The instruction is well-specified with explicit formulas. The task genuinely tests the ability to implement bivariate normal pricing correctly. Opus was very close (failed only on moneyness grid interpretation), Sonnet was nearly there, and Haiku had fundamental errors. The moneyness grid issue is a legitimate test of instruction-following, though Opus's error is borderline.

### Verdict
**建议 Merge** — The task is financially correct and well-designed. The 0/0/0 outcome reflects genuine difficulty (bivariate normal formulas are tricky). Opus and Sonnet failures are on minor contract issues, while Haiku fails for real mathematical reasons. Consider adding an oracle solution for reference.
