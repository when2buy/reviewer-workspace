# Review: PR #41 - Interest Rate Cap and Floor Pricing
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Price an interest rate cap and floor using Black's model on individual caplets/floorlets. Includes put-call parity verification.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py, test.sh, Dockerfile
- Reviewed trial results and failure logs
- Verified Black's caplet formula correctness and T_i indexing convention

### Trial Results
| Model | Reward |
|-------|--------|
| Haiku 4.5 | 0.0 |
| Opus 4.6 | 1.0 |
| Sonnet 4.5 | 1.0 |

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 5/5
- Difficulty calibration: 4/5
- Model discrimination: 3/5
- Benchmark integrity: 4/5
- Financial correctness: 4/5

### Findings

#### [POSITIVE] Good model discrimination
Haiku fails (cap=6676 vs ref=7773, ~14% off) while Opus and Sonnet pass. The failure suggests Haiku mishandles the fixing-time convention (T_i = (i-1)×τ vs T_i = i×τ), which is the genuine quant subtlety in this task.

#### [POSITIVE] Verifier contains full reference implementation
`_ref()` in test_outputs.py independently computes cap/floor prices from params.json and compares with rtol=0.01. This is strong verification.

#### [MINOR] Verifier contains full solution — anti-cheat concern
The `_ref()` function in test_outputs.py is a complete pricing implementation. Under Harbor assumptions tests are inaccessible to the agent, but if test files leak this becomes trivially solvable.

#### [MINOR] test.sh uses `set -uo pipefail` without `set +e` before pytest
The `$?` check after pytest may not work correctly with `pipefail` still active. However, since `set -e` is not used, pytest failure won't abort the script — the pattern is actually fine here (only `set -uo`, not `set -euo`).

#### [NIT] Put-call parity tolerance is generous (< 1.0)
The parity error check `abs(error) < 1.0` is loose but appropriate since put-call parity should hold exactly in theory and small numerical errors are expected.

### Summary
Well-designed interest rate derivatives task with real discriminative power. The fixing-time convention (T_i = (i-1)×τ) is a genuine source of confusion that separates weaker models. Financial formulas are correct. Verifier is robust with reference implementation.

### Verdict
**建议 Merge**

Good task with meaningful difficulty calibration. The Haiku failure is for a substantive quant reason.
