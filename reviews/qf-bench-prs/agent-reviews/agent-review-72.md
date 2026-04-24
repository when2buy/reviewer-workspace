# Review: PR #72 - treasury-curve-pca-butterfly
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/72](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/72)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Treasury yield curve analysis: bootstrap zero curve from par yields, compute forward rates, PCA on yield changes, construct a duration-neutral butterfly trade, and compute 1-day P&L.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, Dockerfile
- Checked: trial results for h45, opus46, s45 (all reward=0.0)
- Analyzed: failure patterns across models

### Scorecard
- Task contract / instruction: 3/5
- Verifier robustness: 2/5
- Difficulty calibration: 4/5
- Model discrimination: 4/5
- Benchmark integrity: 4/5

### Findings

#### [CRITICAL] PCA PC2 sign convention not specified — causes universal failure
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/222d8dd/tasks/treasury-curve-pca-butterfly/tests/test_outputs.py), test `test_pca_pc2_sign_change`

All three models fail this test. PCA eigenvectors have arbitrary sign (both v and -v are valid eigenvectors). The test enforces `ld[0] > 0 and ld[-1] < 0` (positive short end, negative long end) but the instruction never specifies a sign convention.

All three models produce PC2 with the opposite sign convention (ld[0] = -0.25..., which is negative). This is a well-known PCA issue — the fix is either to specify the sign convention in the instruction or to test `abs(ld[0]) > 0 and ld[0] * ld[-1] < 0` (sign change exists, either direction).

#### [CRITICAL] Butterfly P&L fails for ALL models with wildly different values
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/222d8dd/tasks/treasury-curve-pca-butterfly/tests/test_outputs.py), test `test_butterfly_pnl`

- Haiku: -8,228,982 (way off)
- Opus: -5,473 (closer but still far from 230.29)
- Sonnet: -5,473 (same as Opus)

The oracle expects ~230.29 but the two strongest models converge on -5,473. This strongly suggests the oracle is wrong or the instruction underspecifies the butterfly P&L calculation. Key ambiguities:
1. The instruction says "belly is SHORT 1 unit notional" — but doesn't clarify the sign convention for pricing (is P&L = Σ notional_i × ΔPrice_i, with belly notional negative?)
2. "Re-price each leg using the new zero curve" — price as what? Clean price, dirty price, PV of cash flows?
3. The 1-day interval means accrued interest changes — is this accounted for?

When Opus and Sonnet agree on -5,473 and the oracle says 230, the oracle likely has a sign or scaling error.

#### [MAJOR] DV01 tests fail inconsistently across models
Opus passes all DV01 tests; Haiku and Sonnet fail dv01_2y/5y/10y. The instruction says "DV01 = change in dirty price for a `shift_bps` parallel shift" but doesn't specify whether this is per $100 notional or per unit notional. This causes model disagreements.

#### [MINOR] Butterfly notional_sum test fails for Haiku and Sonnet
The constraint "wing notionals sum to belly notional" is clear, but some models produce notionals that don't satisfy this — suggesting they misinterpret the constraint or the belly sign.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 98s | 371,097in / 8,370out |
| Opus 4.6 | 0.0 | 121s | 147,954in / 5,140out |
| Sonnet 4.5 | 0.0 | 199s | 208,615in / 7,736out |


**Haiku key failures:**
```
FAIL: test_zero_rate_2y
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f4da8689d30>(0.0212199934433661, 0.04195242, atol=0.001)
E        +    where <function isclose at 0x7f4da8689d30> = np.isclose
FAIL: test_zero_rate_5y
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f4da8689d30>(0.02328740716132733, 0.03766137, atol=0.001)
E        +    where <function isclose at 0x7f4da8689d30> = np.isclose
```


**Opus key failures:**
```
FAIL: test_pca_pc2_sign_change
E       assert (-0.2501828014774793 > 0)
FAIL: test_butterfly_pnl
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f2f7fa82eb0>(-5473.113882449472, 230.29, atol=50.0)
E        +    where <function isclose at 0x7f2f7fa82eb0> = np.isclose
```

### Summary
Good task concept combining curve bootstrapping, PCA, and trading. However, two universal failures — PCA sign convention and butterfly P&L — indicate spec gaps. Opus is close to passing (22/24) which shows the core task is sound, but the oracle likely has errors in the butterfly P&L calculation.

### Verdict
**不建议 Merge** — Two blockers: (1) PCA eigenvector sign convention unspecified, (2) butterfly P&L oracle likely wrong (Opus+Sonnet converge on -5473 vs oracle 230). Fix both and this becomes a strong "hard" task with good discrimination.
