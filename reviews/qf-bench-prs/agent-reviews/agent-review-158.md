# Review: PR #158 - chooser-option-pricing
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Price simple and complex chooser options. Simple: holder chooses call or put at time τ (same K, T). Complex: different strikes/maturities for call vs put. Uses put-call parity decomposition and bivariate normal CDF.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked: oracle values, financial correctness, test tolerance, failure patterns
- Reviewed: trial results for h45, opus46, s45

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 3 |
| Verifier robustness | 2 |
| Difficulty calibration | 2 |
| Model discrimination | 1 |
| Benchmark integrity / anti-cheating | 2 |

### Findings

#### [CRITICAL] Oracle values for simple chooser likely have a formula error
File: `tests/test_outputs.py`

ALL three models fail `test_simple_chooser_atm_tau025` (oracle: 63.785). Opus passes the complex chooser tests but fails the simple chooser at τ=0.25. Sonnet passes τ=0.50 but fails τ=0.25. This pattern strongly suggests the oracle's simple chooser formula has a bug, specifically at τ=0.25.

The simple chooser value should equal `call(S,K,T) + put(S, K·e^{-(r-D)(T-τ)}, τ)` via put-call parity decomposition. If the oracle incorrectly handles the adjusted strike or the discounting in this decomposition, it would produce wrong values that vary with τ.

#### [MAJOR] Hardcoded oracle values with tight tolerances
The test file embeds full oracle price tables (ORACLE_SIMPLE_CHOOSER, ORACLE_COMPLEX_CHOOSER) with exact values to 4+ decimal places and tight tolerances. This is fragile — any formula interpretation difference causes failure. It also means the test **leaks the full answer set**, making the task trivially solvable by hardcoding if tests are visible.

#### [MAJOR] Test leakage — oracle values fully exposed in test_outputs.py
ORACLE_SIMPLE_CHOOSER and ORACLE_COMPLEX_CHOOSER contain all 16 expected prices. An agent with access to test files could hardcode these values. Under Harbor assumptions this shouldn't happen, but it's still poor practice.

#### [MINOR] All models score 0 — no discrimination
H:0, O:0, S:0. Even if the oracle were correct, the tight tolerances and hardcoded values make this fragile.

### Summary
The task concept (chooser option pricing with bivariate normal) is good. However, the oracle values for simple chooser pricing appear to be wrong (all models fail at τ=0.25), tolerances are too tight, and oracle values are fully leaked in the test file. Needs significant rework.

### Verdict
**不建议 Merge**

Blockers: (1) Likely oracle formula error in simple chooser pricing at τ=0.25 — all models fail. (2) Full oracle values leaked in test file. Fix the simple chooser formula, widen tolerances, and remove hardcoded oracle values from tests (use property-based checks instead).
