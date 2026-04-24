# Review: PR #177 - Spread Option (Kirk & Margrabe)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Price Margrabe exchange options and Kirk spread call options on AAPL/MSFT using closed-form approximations. Validate via Monte Carlo (500K paths) and analyze correlation sensitivity.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py (344 lines), Dockerfile
- Reviewed trial results: H:0.0, O:1.0, S:1.0
- Checked financial correctness and test design

### Scorecard
- Task contract / instruction: 5/5
- Verifier robustness: 4/5
- Difficulty calibration: 4/5
- Model discrimination: 4/5 — good separation
- Benchmark integrity: 4/5

### Findings

#### [MINOR] Haiku failure is substantive — genuine formula errors
Haiku (0/1 reward, 4 test failures) produced negative Margrabe prices and failed Kirk/MC agreement. This indicates fundamental errors in the exchange option formula implementation, not verifier brittleness. Healthy discrimination.

#### [MINOR] Kirk K=0 ≈ Margrabe check is well-designed
File: `tests/test_outputs.py:293-299`
Testing that Kirk's approximation with K=0 matches Margrabe within 5% is a good sanity check that validates both implementations simultaneously.

#### [MINOR] MC agreement tolerance is well-calibrated
File: `tests/test_outputs.py:238-253`
The test uses `3 * SE + 0.001` as absolute tolerance plus 1% relative tolerance — a reasonable multi-tiered approach that accounts for both MC noise and small-price regimes.

#### [MINOR] No oracle solution
File: `solution/solve.py`
Empty, but the Margrabe and Kirk formulas are well-known and the tests are self-consistent.

#### [MINOR] Correlation sensitivity correctly tests monotonicity
File: `tests/test_outputs.py:273-280`
The test verifies that Margrabe prices decrease with correlation, which is the correct financial intuition (higher correlation → less dispersion → lower exchange option value).

### Summary
Excellent task design. The instruction provides clear formulas, the tests check both structural properties and cross-validation (Kirk K=0 ≈ Margrabe, MC agreement). Model discrimination is good: Opus and Sonnet pass while Haiku fails for genuine mathematical reasons. The 500K MC paths provide tight confidence intervals.

### Verdict
**建议 Merge** — Correct, well-calibrated, good model discrimination. Add oracle solution for completeness.
