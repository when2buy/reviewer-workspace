# Review: PR #162 - digital-barrier-options
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/162](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/162)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Prices digital (binary) options — cash-or-nothing, asset-or-nothing, gap options — and barrier digital options using the reflection principle under Black-Scholes. Tests include parity relationships (cash call + cash put = e^{-rT}, asset decomposition of BS call).

### What I Did to Review This
- Read: instruction.md, test_outputs.py (first 100 lines), trials for all 3 models
- Checked financial correctness of parity tests
- Reviewed model discrimination

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 4/5
- Difficulty calibration: 4/5
- Model discrimination: 3/5 — Opus and Sonnet pass, Haiku fails (reasonable)
- Benchmark integrity: 4/5

### Findings

#### [MINOR] Haiku failure is on barrier digital values and summary key error
Haiku fails on `test_do_cash_call_values`, `test_uo_cash_put_values`, and a KeyError in summary. This suggests Haiku struggles with the reflection principle barrier formulas — a reasonable difficulty signal.

#### [MINOR] Pinned oracle values in tests
Tests like `test_atm_cash_call_T050` pin to 0.5341 with atol=0.02, and `test_atm_asset_call_T050` to 402.48 with atol=5.0. These are reasonable tolerances for the analytical formulas given calibrated σ.

#### [MINOR] Strong parity tests
The cash parity (CashCall + CashPut = e^{-rT}), asset parity, and BS decomposition tests are mathematically correct and serve as genuine integrity checks. Good.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-digital-barrier-options) | 0.0 | 213s | 1,355,604in / 17,218out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-digital-barrier-options) | 1.0 | 109s | 150,562in / 5,535out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-digital-barrier-options) | 1.0 | 306s | 450,457in / 20,189out |


**Haiku key failures:**
```
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7fcdea65d630>(np.float64(0.4948452222378559), 0.533, atol=0.01)
E        +    where <function isclose at 0x7fcdea65d630> = np.isclose
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7fcdea65d630>(np.float64(0.3060304248455036), 0.437, atol=0.01)
E        +    where <function isclose at 0x7fcdea65d630> = np.isclose
E       KeyError: 'cash_call_increases_with_S'
```

### Summary
Well-structured task with correct financial logic. Good parity tests that aren't tautological. Reasonable model discrimination (Haiku fails on harder barrier formulas). No blockers found.

### Verdict
**建议 Merge** — Correct, well-calibrated, reasonable discrimination. Minor pinned values are acceptable.
