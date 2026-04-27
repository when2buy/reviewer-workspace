# Review: PR #163 - double-barrier-options
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/163](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/163)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Prices double-barrier knock-out European options using the Kunitomo-Ikeda Fourier series method, verifies via knock-in/knock-out parity and Monte Carlo simulation.

### What I Did to Review This
- Read: instruction.md, test_outputs.py, trial results
- Checked financial correctness of DBKO parity and monotonicity tests
- Reviewed model discrimination pattern

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 4/5
- Difficulty calibration: 4/5
- Model discrimination: 3/5 — Only Opus passes
- Benchmark integrity: 4/5

### Findings

#### [MINOR] Opus-only pass pattern
Opus (1.0) passes all tests. Haiku fails on pinned value `test_dbko_call_085_115_T050` (expected 11.82±0.5) and vol smile effect. Sonnet fails on the same pinned value plus parity/DBKI non-negativity issues — suggesting its Fourier series implementation has numerical issues. This is a reasonable difficulty gradient.

#### [MINOR] Good parity tests
`test_parity_holds` checks DBKO + DBKI = Vanilla to machine precision (1e-10). This is a genuine mathematical identity and not tautological. `test_dbko_leq_vanilla` is also a valid constraint.

#### [MINOR] Pinned price value
`test_dbko_call_085_115_T050` pins to 11.82 with atol=0.5. This is from the oracle solution and serves as a sanity check. Tolerance seems reasonable for a Fourier series with N_terms=200.

#### [MINOR] MC comparison tests
MC tests use relative error bounds — good for validation. The tests check wider barriers converge better (larger survival probability, less barrier monitoring bias).


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-double-barrier-options) | 0.0 | 161s | 438,947in / 6,999out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-double-barrier-options) | 1.0 | 587s | 483,642in / 15,631out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-double-barrier-options) | 0.0 | 252s | 329,703in / 14,439out |


**Haiku key failures:**
```
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f8264a814f0>(np.float64(12.936462555819883), 11.82, atol=0.5)
E        +    where <function isclose at 0x7f8264a814f0> = np.isclose
E       assert False is True
```


**Sonnet key failures:**
```
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7fd0eb50d730>(np.float64(10.962012066003824), 11.82, atol=0.5)
E        +    where <function isclose at 0x7fd0eb50d730> = np.isclose
E       assert np.False_
E        +  where np.False_ = all()
E       assert np.False_
E        +  where np.False_ = all()
E       assert np.float64(0.1028602815493927) < 0.1
```

### Summary
Solid task with correct financial framework. The Kunitomo-Ikeda Fourier series is a genuinely difficult implementation. Good parity and monotonicity tests. Only Opus passing is consistent with difficulty.

### Verdict
**建议 Merge** — Correct, well-calibrated, good discrimination for a hard exotic options task.
