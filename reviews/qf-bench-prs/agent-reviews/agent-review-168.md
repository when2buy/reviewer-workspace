# Review: PR #168 - heston-cf-pricing
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/168](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/168)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Implements Heston stochastic volatility model pricing via characteristic function and Fourier inversion (Formulation 2 / Albrecher). Compares integration methods (quad, Gauss-Laguerre, Simpson), checks BS and κ→∞ limits, extracts implied vol smile, verifies with Monte Carlo.

### What I Did to Review This
- Read: instruction.md, test_outputs.py (full), solve.sh (full), trial results
- Checked Heston CF implementation, integration methods, limit tests
- Reviewed failure modes across all models

### Scorecard
- Task contract / instruction: 3/5
- Verifier robustness: 2/5
- Difficulty calibration: 2/5 — All models fail (0/0/0)
- Model discrimination: 1/5 — No discrimination
- Benchmark integrity: 3/5

### Findings

#### [CRITICAL] All three models score 0.0, but each fails on trivial schema issues, not financial errors
- Haiku: fails on `test_K_values_correct` (K ≠ S0 × moneyness — likely rounding), `test_integration_methods_csv_has_5_rows` (produced different number of methods), and `test_integration_methods_agree`
- Opus: fails only on `test_K_values_correct` — 73/74 tests pass! One trivial schema test blocks a perfect score
- Sonnet: fails on `test_v0_equals_theta_squared_sigma` and `test_theta_equals_sigma_squared` — the test expects v0 == sigma_hist², but the instruction says "v₀ = sample variance of log-returns" which IS sigma_hist² (variance of daily returns, not annualized). Sonnet likely annualized.

#### [MAJOR] test_K_values_correct is overly strict
The test asserts `K == S0 * moneyness` to 1e-6 precision. If the agent uses rounded moneyness or computes K differently (e.g., via forward moneyness), this fails even though the financial computation is correct. This single test blocks Opus from scoring 1.0.

#### [MAJOR] test_v0_equals_theta_squared_sigma is ambiguous
The instruction says "v₀ = sample variance of log-returns" and "θ = sample variance". The test then checks `v0 == sigma_hist²`. But `sigma_hist` is defined in the oracle as `np.std(log_returns)` (daily std, not annualized). The instruction says "v₀ = sample variance of log-returns" without specifying daily vs annualized. This ambiguity is what causes Sonnet's failure.

#### [MINOR] Very comprehensive test suite
The 74 tests cover put-call parity, BS limits, κ limits, IV smile skew, ρ sensitivity, MC comparison, and integration method agreement. The financial content is excellent. The tests are well-relaxed for numerical challenges (50% tolerance for Simpson, 30% mean MC error).

#### [MINOR] Tolerances are overly generous in some tests
`test_bs_limit_converges` allows mean reldiff < 0.1 (10%) for ITM options, and `test_kappa_limit_converges` allows 20%. These are very loose and may pass incorrect implementations.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 551s | 1,999,482in / 46,773out |
| Opus 4.6 | 0.0 | 751s | 2,177,907in / 46,446out |
| Sonnet 4.5 | 0.0 | 1168s | 4,534,270in / 91,226out |


**Haiku key failures:**
```
E           assert np.float64(0.0019999999999527063) < 1e-06
E            +  where np.float64(0.0019999999999527063) = abs((np.float64(549.65) - np.float64(549.648)))
E       assert 3 == 5
E       assert 1 >= 2
```


**Opus key failures:**
```
E           assert np.float64(0.0019999999999527063) < 1e-06
E            +  where np.float64(0.0019999999999527063) = abs((np.float64(549.65) - np.float64(549.648)))
```

### Summary
Opus scores 73/74 and is blocked by a single trivial `K_values_correct` test. The task has excellent financial content but the verifier has two schema traps (`K == S0*moneyness` precision, v0/theta definition ambiguity) that prevent any model from passing. Fixing these two tests would likely give Opus reward=1.0.

### Verdict
**需要 Human Review** — Excellent financial content, but two verifier issues block all models. Fix `test_K_values_correct` tolerance and clarify v0/theta definition, then re-run trials. Opus is very close to passing.
