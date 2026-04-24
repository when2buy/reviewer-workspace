# Review: PR #158 - chooser-option-pricing
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/158](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/158)
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
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/74ce023/tasks/chooser-option-pricing/tests/test_outputs.py)

ALL three models fail `test_simple_chooser_atm_tau025` (oracle: 63.785). Opus passes the complex chooser tests but fails the simple chooser at τ=0.25. Sonnet passes τ=0.50 but fails τ=0.25. This pattern strongly suggests the oracle's simple chooser formula has a bug, specifically at τ=0.25.

The simple chooser value should equal `call(S,K,T) + put(S, K·e^{-(r-D)(T-τ)}, τ)` via put-call parity decomposition. If the oracle incorrectly handles the adjusted strike or the discounting in this decomposition, it would produce wrong values that vary with τ.

#### [MAJOR] Hardcoded oracle values with tight tolerances
The test file embeds full oracle price tables (ORACLE_SIMPLE_CHOOSER, ORACLE_COMPLEX_CHOOSER) with exact values to 4+ decimal places and tight tolerances. This is fragile — any formula interpretation difference causes failure. It also means the test **leaks the full answer set**, making the task trivially solvable by hardcoding if tests are visible.

#### [MAJOR] Test leakage — oracle values fully exposed in test_outputs.py
ORACLE_SIMPLE_CHOOSER and ORACLE_COMPLEX_CHOOSER contain all 16 expected prices. An agent with access to test files could hardcode these values. Under Harbor assumptions this shouldn't happen, but it's still poor practice.

#### [MINOR] All models score 0 — no discrimination
H:0, O:0, S:0. Even if the oracle were correct, the tight tolerances and hardcoded values make this fragile.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 70s | 224,128in / 5,188out |
| Opus 4.6 | 0.0 | 88s | 103,373in / 4,185out |
| Sonnet 4.5 | 0.0 | 143s | 186,732in / 7,329out |


**Haiku key failures:**
```
E       AssertionError: ATM simple chooser (tau=0.25) price mismatch: 71.1564 vs 63.7854
E       assert 7.371000000000002 < 0.01
E        +  where 7.371000000000002 = abs((71.1564 - 63.7854))
E       AssertionError: ATM simple chooser (tau=0.5) price mismatch: 76.6047 vs 71.3489
E       assert 5.255799999999994 < 0.01
E        +  where 5.255799999999994 = abs((76.6047 - 71.3489))
E       AssertionError: ATM complex chooser (Tp=1.0) price mismatch: 45.1223 vs 71.34885498568323
E       assert 26.22655498568323 < 0.01
```


**Opus key failures:**
```
E       AssertionError: ATM simple chooser (tau=0.25) price mismatch: 63.818546 vs 63.7854
E       assert 0.03314599999999501 < 0.01
E        +  where 0.03314599999999501 = abs((63.818546 - 63.7854))
E       AssertionError: ATM simple chooser (tau=0.5) price mismatch: 71.464511 vs 71.3489
E       assert 0.11561100000000124 < 0.01
E        +  where 0.11561100000000124 = abs((71.464511 - 71.3489))
E       AssertionError: atm_simple_tau025 mismatch: 63.818546 vs 63.78543320700385
E       assert 0.033112792996149665 < 0.01
```

### Summary
The task concept (chooser option pricing with bivariate normal) is good. However, the oracle values for simple chooser pricing appear to be wrong (all models fail at τ=0.25), tolerances are too tight, and oracle values are fully leaked in the test file. Needs significant rework.

### Verdict
**不建议 Merge**

Blockers: (1) Likely oracle formula error in simple chooser pricing at τ=0.25 — all models fail. (2) Full oracle values leaked in test file. Fix the simple chooser formula, widen tolerances, and remove hardcoded oracle values from tests (use property-based checks instead).
