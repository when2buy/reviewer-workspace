# Review: PR #161 - compound-option-geske
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Prices compound options (call-on-call, put-on-put) using the Geske (1979) bivariate normal formula, validates via compound put-call parity, prices simple chooser options, and verifies with Monte Carlo.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py, solve.sh, Dockerfile
- Examined trial results for h45 (1.0), opus46 (0.0), s45 (0.0)
- Checked financial correctness of Geske formula implementation
- Reviewed verifier robustness and test structure

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 3/5
- Difficulty calibration: 3/5
- Model discrimination: 2/5 — inverted (Haiku passes, Opus/Sonnet fail)
- Benchmark integrity: 4/5

### Findings

#### [MAJOR] Inverted model discrimination — Haiku passes, Opus/Sonnet fail
Haiku (reward=1.0) passes all 34 tests while Opus (0.0) fails on `test_types` (likely schema issue — "AssertionError" suggesting wrong type labels) and Sonnet (0.0) fails on parity error. This inverted pattern (weakest model passes, strongest fail) suggests the task may reward a particular implementation style rather than genuine understanding. The failures look like minor schema/precision issues rather than fundamental errors.

#### [MAJOR] Parity check is tautological in solve.py
The `verify_parity` function computes `pc_price` (put-on-call) directly *from* the parity relationship (`pc_price = cc_price - bs_c + K1*e^{-rT1}`), then checks parity against that derived value. This guarantees zero parity error by construction. A proper parity check should independently compute put-on-call and then verify the relationship holds.

#### [MINOR] n_returns test pins exact value 692
`test_n_returns` asserts exactly 692. This is fragile if the data file changes and unnecessarily tests data loading rather than financial logic.

#### [MINOR] MC seed is shared across call/put pricing
The seed is reset for each MC call (SEED=42 for calls, SEED+1 for puts), which is fine but the MC comparison is not deeply tested — only `mc_validates` checks max error < 1.0, a very loose bound.

### Summary
The parity check is tautological (computes one side from the other). The model discrimination is inverted — Haiku passes while Opus and Sonnet fail on minor schema issues, which is a calibration concern. The financial content (Geske formula, bivariate normal) is solid.

### Verdict
**需要 Human Review** — The tautological parity check and inverted model discrimination need discussion. The task has good financial content but calibration issues.
