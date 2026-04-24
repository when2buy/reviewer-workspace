# Review: PR #66 - portfolio-risk-attribution
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Factor model portfolio construction: price adjustment, monthly resampling, single-factor OLS, factor covariance matrix, minimum-variance and tangency portfolios, risk decomposition (MCTR, CR, PCR), out-of-sample walk-forward evaluation, and parametric VaR with component decomposition.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, Dockerfile
- Checked: trial results for h45, opus46, s45 (all reward=0.0)
- Analyzed: failure patterns across models

### Scorecard
- Task contract / instruction: 3/5
- Verifier robustness: 2/5 — likely oracle or spec bug
- Difficulty calibration: 4/5
- Model discrimination: 3/5
- Benchmark integrity: 4/5

### Findings

#### [CRITICAL] OOS Sharpe test fails for ALL models — likely oracle or spec issue
File: `tests/test_outputs.py`

All three models produce `oos_sharpe ≈ 0.092` while the oracle expects `1.0317`. This 10× discrepancy across all models is too consistent to be agent error.

- **Opus (best):** 59/60 passed — only `test_oos_sharpe` fails
- **Haiku:** 54/60 passed — oos_sharpe + 5 component_var failures
- **Sonnet:** 36/60 passed — many min-var weight failures (different covariance approach)

The instruction says: "annualized out-of-sample Sharpe ratio" and "Annualize monthly mean by multiplying by 12. Annualize monthly vol by multiplying by sqrt(12)." But it does **not specify whether Sharpe uses excess returns (net of rf) or raw returns**. The oracle value of 1.03 with oos_return=0.242 and oos_vol=0.216 implies `(0.242 - 0.02)/0.216 ≈ 1.03` (excess), while models likely compute `0.242/0.216 ≈ 1.12` or a different variant.

**Root cause:** The instruction mentions `risk_free_annual` in params.json but never explicitly states to subtract rf from OOS returns when computing OOS Sharpe. The earlier Sharpe discussion is only in the context of the factor model, not OOS evaluation.

**Fix:** Explicitly state in instruction: "OOS Sharpe = (ann_oos_return − risk_free_annual) / ann_oos_vol"

#### [MAJOR] Component VaR tolerance too tight for Haiku
File: `tests/test_outputs.py`

Haiku fails all 5 component_var tests with tolerance of 0.002. The values are close but just outside tolerance — suggests a slightly different VaR computation path. This is reasonable discrimination but combined with the OOS Sharpe bug, makes the task untestable.

#### [MINOR] Task is large and complex for "hard" — appropriate difficulty label
The task combines 8 distinct computational steps (factor model, covariance, optimization, risk decomposition, walk-forward, VaR). Opus getting 59/60 suggests the difficulty is well-calibrated once the oracle bug is fixed.

### Summary
Strong task design with good model discrimination (Opus >> Haiku >> Sonnet on non-buggy tests). However, the OOS Sharpe specification ambiguity causes universal failure. This is a one-line fix in the instruction.

### Verdict
**不建议 Merge** — OOS Sharpe specification gap causes all models to fail. Clarify the Sharpe formula in instruction.md and verify the oracle. Once fixed, this would be a well-calibrated "hard" task with good model discrimination.
