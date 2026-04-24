# Review: PR #166 - fx-quanto-options
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/166](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/166)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Prices quanto (fixed-FX) and compo (floating-FX) European options on a foreign equity, performs sensitivity analysis on correlation and FX volatility, validates with Monte Carlo and put-call parity.

### What I Did to Review This
- Read: instruction.md (full), test_outputs.py (full), solve.sh (full), trial results
- Checked quanto/compo pricing formulas in the oracle solution
- Reviewed model discrimination and failure modes

### Scorecard
- Task contract / instruction: 3/5
- Verifier robustness: 2/5
- Difficulty calibration: 2/5 — All models fail (0/0/0)
- Model discrimination: 1/5 — No discrimination
- Benchmark integrity: 3/5

### Findings

#### [CRITICAL] All three models score 0.0 — verifier is too strict on calibration schema
All three models fail on calibration key name mismatches (KeyError on `S0_f`, `r_d`, `r_f`, etc.). The instruction uses mathematical notation (S₀^f, r_d, r_f, D_f) but the test expects exact JSON keys like `S0_f`, `r_d`, `r_f`, `D_f`, `sigma_X`, `rho_SX`, `X_0`, `X_fixed`, `n_returns`. These key names are not explicitly listed in the instruction — agents must guess the exact naming convention.

#### [CRITICAL] test_rho_zero_gives_same_quanto_compo is financially incorrect
The test asserts that when ρ=0, quanto_call == compo_call to machine precision (< 1e-10). This is **wrong**. Even with ρ=0, the compo option has additional FX volatility exposure (σ_d² = σ_S² + σ_X² for the composite process), while the quanto option only depends on σ_S. The oracle solve.py uses the same σ_S for both, which is incorrect for the compo option — the compo call should use a composite volatility. All three models correctly fail this test.

Looking at the oracle `price_compo_call`, it uses `sigma_S` in d1/d2, not the composite vol `sqrt(sigma_S^2 + sigma_X^2 + 2*rho*sigma_S*sigma_X)`. When ρ=0, the compo should use `sqrt(sigma_S^2 + sigma_X^2)`, making it strictly larger than the quanto call. The oracle is wrong.

#### [MAJOR] Calibration key naming is excessively specific
The test pins `n_returns` to exactly [692, 693] and requires 10 specific JSON key names. This tests data format compliance more than financial understanding.

#### [MINOR] Good financial content otherwise
The rho sensitivity tests (quanto > compo for ρ < 0, reversed for ρ > 0) and put-call parity checks are correct in principle. The MC comparison tolerances (3% for quanto, 5% for compo) are reasonable.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 378s | 1,432,103in / 36,560out |
| Opus 4.6 | 0.0 | 551s | 658,590in / 21,322out |
| Sonnet 4.5 | 0.0 | 485s | 507,082in / 32,338out |


**Haiku key failures:**
```
E           AssertionError: Missing key: S0_f
E           assert 'S0_f' in {'S_0': 687.06, 'mean_return': 0.0007940656193173516, 'n_returns': 692, 'sigma_S': 0.15099821155186272, ...}
E       KeyError: 'S0_f'
E       KeyError: 'r_d'
E       KeyError: 'r_f'
E       KeyError: 'D_f'
E       KeyError: 'sigma_X'
E       KeyError: 'rho_SX'
```


**Opus key failures:**
```
E           AssertionError: Missing key: S0_f
E           assert 'S0_f' in {'S0': 687.06, 'n_returns': 692, 'sigma_S_annualized': 0.1511074326956573, 'sigma_daily': 0.00951887352776523}
E       KeyError: 'S0_f'
E       KeyError: 'sigma_S'
E       KeyError: 'r_d'
E       KeyError: 'r_f'
E       KeyError: 'D_f'
E       KeyError: 'sigma_X'
```

### Summary
The oracle solution contains a financial error in the compo pricing formula (uses σ_S instead of composite volatility), which makes the `test_rho_zero_gives_same_quanto_compo` test incorrect. Combined with strict calibration key naming that all models fail on, this task has fundamental issues.

### Verdict
**不建议 Merge** — The oracle compo pricing formula appears incorrect (missing composite volatility), and the calibration schema is too strict/underspecified. Needs fix to the compo pricing and clearer output specification.
