# QF-Bench Review — Batch 2

## Task: standard-var-methods
PR: #205
Scores: H4.5=22/25 | S4.5=25/25 | O4.6=25/25

### Instruction Quality
Clear and comprehensive. Five VaR/ES methods fully specified with parameters (lambda=0.98 for age-weighted, lambda=0.94 for EWMA), scaling rules, and backtest procedure. Output schema well-defined.

### Failure Analysis
Haiku fails 3 tests: `test_var_1day_values[StudentT-0.99-30594.61]` (got 25307 vs expected 30594, ~17% off), `test_most_conservative` (reported HS instead of StudentT), and `test_var_range_99` (cascading from wrong StudentT VaR). Root cause: Haiku's Student-t MLE fit produced different df parameter, leading to a lower 99% VaR. The cascading failures on summary tests are expected.

### Model Discrimination
Good. H4.5 struggles with Student-t MLE fitting (a known tricky optimization), while S4.5 and O4.6 nail it perfectly. 22→25→25 progression.

### Issues Found
None. Failures are agent capability gaps in MLE optimization, not task bugs.

### Verdict: 建议 Merge
Well-constructed task with good discrimination. All failures are legitimate agent errors on Student-t fitting.

---

## Task: var-es-estimation
PR: #182
Scores: H4.5=0/47 | S4.5=46/47 | O4.6=46/47

### Instruction Quality
Very detailed instruction with explicit RNG specification (single RandomState(42), sequential generation), four estimation methods fully described, and clear output schemas. Good task design.

### Failure Analysis
- **Haiku (0/47):** Complete failure — all 47 tests ERROR with FileNotFoundError. Agent ran for only ~28s and produced no output files. Agent couldn't complete the implementation within the session.
- **Sonnet (46/47):** Fails `test_historical_var_rmse` — an RMSE tolerance check on historical simulation VaR. Likely a minor numerical difference in how quantiles are computed.
- **Opus (46/47):** Fails `test_best_for_student_t` — expected `parametric_t` as best method for Student-t distribution but got `kernel_density`. This is a judgment call in the verifier: both methods give similar RMSE, and the "best" method depends on tiny numerical differences.

### Model Discrimination
Good. 0→46→46 shows strong discrimination at the low end. The single failures in S4.5 and O4.6 are different tests, suggesting minor numerical edge cases rather than systematic issues.

### Issues Found
- [LOW] `test_best_for_student_t` and `test_historical_var_rmse` may be overly specific — "best method" depends on tiny RMSE differences that can flip based on implementation details. Consider widening tolerance or making these advisory.

### Verdict: 建议 Merge
Excellent discrimination (0 vs 46). The 1-test failures on S4.5/O4.6 are borderline verifier sensitivity issues but not blocking.

---

## Task: smith-tail-index
PR: #180
Scores: H4.5=timeout | S4.5=33/33 | O4.6=33/33

### Instruction Quality
Well-structured. Hill estimator and Smith GPD MLE clearly specified with exact k-values, confidence level, and output formats. Data source (S&P 500 daily CSV) provided.

### Failure Analysis
- **Haiku:** Timed out — agent couldn't complete implementation within the time budget. GPD MLE is computationally involved.
- **Sonnet & Opus:** Perfect 33/33. All Hill estimates, Smith estimates, comparison metrics, and summary statistics pass.

### Model Discrimination
Good. timeout→33→33. Haiku can't handle the complexity; stronger models solve it cleanly.

### Issues Found
None.

### Verdict: 建议 Merge
Clean task. Perfect scores from capable models, timeout from weak model = ideal benchmark item.

---

## Task: creditrisk-plus-model
PR: #195
Scores: H4.5=timeout | S4.5=25/30 | O4.6=25/30

### Instruction Quality
Thorough specification of CreditRisk+ with explicit portfolio parameters, sector structure, Panjer recursion grid size (ε=0.1, max 300 units), and MC validation (seed 42, 1M scenarios). Complex but well-defined.

### Failure Analysis
- **Haiku:** Timed out.
- **Sonnet & Opus (identical 5 failures):**
  1. `test_zero_loss_has_max_prob` — P(L=0) = 0.0452 < 0.05 threshold. The oracle expects P(L=0) > 0.05, but with these portfolio parameters (mean loss ~2.65), P(L=0) being ~4.5% is actually reasonable. **Verifier threshold may be slightly too tight.**
  2. `test_var_95` — got 5.9, expected ~6.5 (atol=0.5). Off by 0.1 beyond tolerance.
  3. `test_var_99` — got 7.7, expected ~9.0 (atol=0.5). Off by 0.8.
  4. `test_var_999` — got 10.2, expected ~12.6 (atol=1.5). Off by 0.9.
  5. `test_es_99` — cascading from VaR errors.

Both S4.5 and O4.6 produce **identical** wrong VaR values (5.9, 7.7, 10.2), suggesting both implement Panjer recursion the same way but the oracle expected values may assume a different discretization or loss-unit convention. The consistency of S4.5=O4.6 results strongly suggests this is a **task/verifier issue** rather than agent error.

### Model Discrimination
Bad for the failed tests — both capable models fail identically, suggesting the oracle values may be wrong or the instruction is ambiguous about discretization details.

### Issues Found
- [MEDIUM] Oracle VaR values (6.5, 9.0, 12.6) may not match the specified model parameters. Both S4.5 and O4.6 independently produce ~5.9, 7.7, 10.2 — systematic offset suggests oracle error or ambiguity in how losses map to the grid.
- [LOW] `test_zero_loss_has_max_prob` threshold of 0.05 is borderline for this portfolio (mean EL=2.65 with mixing).

### Verdict: 需要 Human Review
Two independent strong models producing identical "wrong" answers is a red flag for oracle accuracy. The VaR values are systematically lower than expected — need to verify the oracle solution's Panjer recursion implementation and discretization convention.

---

## Task: compound-option-geske
PR: #161
Scores: H4.5=34/34 | S4.5=33/34 | O4.6=34/34

### Instruction Quality
Well-specified Geske compound option pricing with explicit strike grids, maturity parameters, and parity verification requirements. Bivariate normal CDF and root-finding clearly described.

### Failure Analysis
- **Haiku (34/34):** Perfect — surprisingly the best result!
- **Sonnet (33/34):** Fails `test_parity_error_small` — max parity error 5.41 > 0.01 threshold. Also causes `test_parity_holds` to fail. Sonnet's put-on-call implementation has a numerical issue in the bivariate normal computation.
- **Opus (34/34):** Perfect.

### Model Discrimination
Mixed/inverted. H4.5 > O4.6 > S4.5 (34=34>33). Haiku outperforming Sonnet is unusual but can happen on specific numerical tasks. The parity error is a genuine implementation bug in Sonnet's run.

### Issues Found
None. The parity check is a legitimate mathematical identity that should hold to high precision.

### Verdict: 建议 Merge
All models near-perfect. Sonnet's single failure is a genuine implementation error (parity violation). Interesting that Haiku aces this one.

---

## Task: kou-double-exponential
PR: #170
Scores: H4.5=11/12 | S4.5=10/12 | O4.6=12/12

### Instruction Quality
Comprehensive Kou JD model specification with MLE calibration (5 random restarts, seed 42), Kou-Merton series pricing, and implied vol extraction. Well-structured multi-step task.

### Failure Analysis
- **Haiku (11/12):** Fails `test_kou_prices_csv_values` — ATM price at T=0.25 is 14.48, below expected range [15, 40]. Close miss, likely from slightly different calibrated parameters.
- **Sonnet (10/12):** Fails `test_calibration_json_values` (parameter out of expected range) AND `test_kou_prices_csv_values` (ATM price at T=1.0 is 32.29, below [40, 85]). Calibration issue cascades to pricing.
- **Opus (12/12):** Perfect.

### Model Discrimination
Good overall. O4.6 perfect, H4.5 close (11/12), S4.5 worst (10/12). The inverted H>S pattern suggests Sonnet's MLE optimizer converged to a worse local minimum despite random restarts.

### Issues Found
- [LOW] ATM price range [15, 40] for T=0.25 and [40, 85] for T=1.0 may be slightly tight — Haiku's 14.48 is very close to 15. But the ranges are reasonable sanity checks, not exact value tests.

### Verdict: 建议 Merge
Good task with clean Opus performance. The ATM price ranges are reasonable sanity bounds. Failures reflect genuine calibration quality differences.

---

# Summary

| Task | H4.5 | S4.5 | O4.6 | Verdict |
|------|------|------|------|---------|
| standard-var-methods | 22/25 | 25/25 | 25/25 | ✅ 建议 Merge |
| var-es-estimation | 0/47 | 46/47 | 46/47 | ✅ 建议 Merge |
| smith-tail-index | timeout | 33/33 | 33/33 | ✅ 建议 Merge |
| creditrisk-plus-model | timeout | 25/30 | 25/30 | ⚠️ 需要 Human Review |
| compound-option-geske | 34/34 | 33/34 | 34/34 | ✅ 建议 Merge |
| kou-double-exponential | 11/12 | 10/12 | 12/12 | ✅ 建议 Merge |

**Key finding:** `creditrisk-plus-model` needs oracle verification — both S4.5 and O4.6 independently produce identical VaR values that differ systematically from oracle expectations, suggesting possible oracle bug or instruction ambiguity in Panjer recursion discretization.
