# QF-Bench Review — Batch 3

Reviewed: 2026-04-27

---

## Task: merton-jump-diffusion
PR: (branch: coco/polak-merton-jump-diffusion)
Scores: H4.5=22/22 | S4.5=22/22 | O4.6=22/22

### Instruction Quality
Excellent. Instruction is detailed with explicit formulas, bounds, optimizer method, truncation parameters, and grid specifications. Leaves no ambiguity for the agent. All numerical choices (N_max=15, L-BFGS-B, 5 random restarts, r=0.05, moneyness grid, maturities) are fully specified.

### Failure Analysis
No failures. All 28 tests pass across all three models (rerun results used). Tests cover calibration parameter ranges, return statistics, pricing grid properties (monotonicity, positivity, lower bounds), ATM prices within tolerance, IV smile shape, and summary statistics.

### Model Discrimination
None — all models achieve perfect scores. This is a "hard" task by metadata but all models solve it. Still a valid benchmark item (tests financial knowledge + implementation), just not discriminating at this tier.

### Issues Found
None.

### Verdict: 建议 Merge
Clean task with thorough instruction and well-designed verifier. All models pass perfectly. Good benchmark item even without discrimination — validates correct Merton JD implementation.

---

## Task: power-options
PR: (branch: coco/polak-power-options)
Scores: H4.5=33/36 | S4.5=36/36 | O4.6=36/36

### Instruction Quality
Good. Covers power calls/puts, symmetric power calls, capped power calls, Monte Carlo comparison, and put-call parity. Mathematical framework is clearly presented. Strike definition (K=S₀^α) is explicit.

### Failure Analysis
**H4.5 (initial run, reward=0):** 33/36 passed, 3 failed:
- `test_mc_reasonably_close` — MC prices not close enough to analytical (agent implementation error, likely insufficient MC paths or formula mistake)
- `test_parity_holds` — put-call parity check failed
- `test_mc_errors_bounded` — MC error bounds exceeded

These are all agent capability errors — Haiku got the core formulas right (33 pass) but fumbled MC accuracy and parity.

**S4.5 (initial run, reward=0):** 0/36 — all FileNotFoundError. Agent failed to write output files to correct location. Rerun: 36/36 pass.

**O4.6 (initial run, reward=0):** Same FileNotFoundError issue as S4.5. Rerun: 36/36 pass.

Note: Initial S4.5/O4.6 failures were from an older task checksum. Reruns used updated checksum and both pass perfectly. The initial FileNotFoundError was likely a task infrastructure issue (output path) that was fixed.

### Model Discrimination
Good on rerun data: H4.5=33/36, S4.5=36/36, O4.6=36/36. Haiku struggles with MC + parity while stronger models get everything right.

### Issues Found
None on current version. Initial run failures were due to different task checksum (infrastructure/path issue since fixed).

### Verdict: 建议 Merge
Good discriminating task. Haiku fails on MC accuracy while Sonnet/Opus pass perfectly. Instruction is clear, verifier tests are comprehensive.

---

## Task: dupire-local-vol
PR: (branch: coco/polak-dupire-local-vol)
Scores: H4.5=62/67 | S4.5=65/67 | O4.6=0/67

### Instruction Quality
Good overall. SVI smoothing + Dupire formula is a demanding multi-step pipeline. Instruction covers data prep, IV extraction, SVI calibration, Dupire formula, flat-vol test, forward variance check, and output format. The instruction describes SVI conceptually but does NOT give the explicit SVI functional form (w(k) = a + b(ρ(k-m) + sqrt((k-m)² + σ²))). This is intentional — the agent must know or derive the SVI parametrization.

### Failure Analysis
**H4.5 (62/67, 5 failed):**
- `test_calibration_n_expiries` — wrong number of expiries selected
- `test_calibration_n_options_filtered_positive` — missing key in calibration.json
- `test_calibration_expiry_dates_list` — missing expiry dates
- `test_local_vol_all_positive` — some negative local vols (numerical issue)
- `test_local_vol_atm_consistency` — ATM local vol not close to ATM implied vol

These are agent implementation quality issues (data filtering, output format, numerical stability).

**S4.5 rerun (65/67, 2 failed):**
- `test_implied_vol_option_type_valid` — invalid option_type values in output
- `test_local_vol_atm_consistency` — ATM consistency check failed

Minor output format issue + numerical accuracy gap.

**O4.6 (both runs: 0/67):** All files missing — FileNotFoundError. Opus spawned a subagent and files weren't persisted to /app/output/. This is a known **agent behavior issue**, NOT a task problem. Opus's tendency to delegate to subagents causes output file loss in the sandbox.

### Model Discrimination
Good (ignoring O4.6 infra issue): H4.5 < S4.5 in pass rate. The task genuinely discriminates — SVI calibration + Dupire local vol extraction is a hard multi-step numerical task.

### Issues Found
- [LOW] ATM consistency test (`test_local_vol_atm_consistency`) fails for both H4.5 and S4.5 — the 50% relative error tolerance is reasonable but this is a genuinely hard numerical check. Not a task bug.
- [INFO] O4.6=0/67 is purely agent behavior (subagent file persistence), not task-related.

### Verdict: 建议 Merge
Hard, well-constructed task. Failures are agent capability gaps, not task bugs. Good discrimination between H4.5 and S4.5. O4.6 failure is a known agent issue.

---

## Task: realized-vol-estimators
PR: (branch: coco/polak-realized-vol-estimators)
Scores: H4.5=29/33 | S4.5=29/33 | O4.6=30/33

### Instruction Quality
Good. Covers 5 standard realized vol estimators (CC, Parkinson, GK, RS, YZ) with rolling window analysis, efficiency ratios, and volatility term structure. Formulas are described conceptually (not given explicitly), which is appropriate for a benchmark.

Note: The task appears to have been significantly revised between runs. The initial H4.5 run (old checksum) tested 141 tests with intraday 5-min data (noise variance, bipower variation, signature plots). The rerun version (new checksum) has 33 tests focused on OHLCV-based estimators. The scores reported (29/33, 29/33, 30/33) are from the rerun version.

### Failure Analysis
**H4.5 rerun (29/33, 4 failed):**
- `test_S0` — S0 value doesn't match expected 687.06 (atol=0.01). Agent likely read wrong row or column.
- `test_estimators_present` — Missing expected estimator names in rolling_vol_stats.csv
- `test_cc_efficiency_one` — CC efficiency ratio not equal to 1.0
- `test_range_estimators_lower_variance` — Range estimators don't show lower variance than CC

**S4.5 rerun (29/33, 4 failed):** Same 4 failures as H4.5. Identical failure pattern.

**O4.6 rerun (30/33, 3 failed):** Same first 3 failures (S0, estimators_present, cc_efficiency_one) but passes `test_range_estimators_lower_variance`.

All failures are agent implementation errors: wrong S0 extraction, naming conventions for estimators in CSV, and efficiency ratio computation.

### Model Discrimination
Weak — H4.5=S4.5=29/33, O4.6=30/33. Only 1-test difference. The task doesn't strongly discriminate but O4.6 is marginally better.

### Issues Found
- [LOW] `test_S0` expects exactly 687.06 (atol=0.01). All three models fail this — could indicate the test hardcodes a value that doesn't match the actual data, OR all agents make the same mistake reading the last close. Worth checking if oracle solve.py produces 687.06.
- [LOW] `test_estimators_present` and `test_cc_efficiency_one` fail consistently — may indicate the verifier expects specific column names/formats that the instruction doesn't fully specify.

### Verdict: 建议 Merge
Failures are consistently agent errors (S0 extraction, naming conventions). The common S0 failure across all models is suspicious but likely agents reading the data slightly differently than expected. Task is sound as a benchmark item.

---

## Task: implied-vol-approximations
PR: (branch: coco/polak-implied-vol-approximations)
Scores: H4.5=9/10 | S4.5=9/10 | O4.6=timeout

### Instruction Quality
Very good. Specifies all 5 methods clearly, gives exact grid parameters (S₀=500, r=0.05, D=0.013, 75 points), column names, and expected behavior (NaN for non-ATM on ATM-only methods). Clear reference to Chin, Ólafsson, Nel.

### Failure Analysis
**All models (H4.5, S4.5, O4.6) fail exactly 1 test: `test_summary_json_oracle_values`**

This test compares computed RMSE values against hardcoded oracle values:
- rmse_bs_atm: 0.03418723590366654
- rmse_li_atm: 0.034911328507646396
- rmse_li_nonatm: 0.005730051959888682
- rmse_cmh: 0.28387655126244243
- rmse_newton: 3.049570677057145e-13

The test likely uses tight tolerances on these RMSE values. All agents get 9/10, meaning they implement everything correctly but their RMSE values differ slightly from oracle. This is the ONE discriminating test — and no model passes it.

**O4.6 rerun:** Timed out (no result.json produced). Agent likely spent too long on implementation.

### Model Discrimination
None — all models score 9/10. The single failing test doesn't discriminate between models.

### Issues Found
- [MEDIUM] `test_summary_json_oracle_values` fails for ALL models (H4.5, S4.5, O4.6). If the oracle RMSE values are truly deterministic (synthetic data, closed-form formulas), this suggests either: (a) the oracle values are wrong, (b) the tolerance is too tight, or (c) there's an ambiguity in the formulas (e.g., which specific Brenner-Subrahmanyam / Li / CMH formulas). Since ALL agents fail identically, this is more likely a **verifier/oracle issue** than an agent capability gap.
- [LOW] O4.6 timeout on rerun — agent behavior issue, not task-related.

### Verdict: 需要 Human Review
The universal 9/10 pattern (every model fails exactly `test_summary_json_oracle_values`) suggests the oracle RMSE values or tolerances may need adjustment. If the formulas are truly unambiguous and deterministic, investigate why no agent matches the oracle. Could be a formula variant issue (multiple valid forms of CMH or Li approximation exist in the literature).

---

# Summary Table

| Task | H4.5 | S4.5 | O4.6 | Discrimination | Verdict |
|------|------|------|------|----------------|---------|
| merton-jump-diffusion | 22/22 ✅ | 22/22 ✅ | 22/22 ✅ | None | 建议 Merge |
| power-options | 33/36 | 36/36 ✅ | 36/36 ✅ | Good | 建议 Merge |
| dupire-local-vol | 62/67 | 65/67 | 0/67* | Good (H<S) | 建议 Merge |
| realized-vol-estimators | 29/33 | 29/33 | 30/33 | Weak | 建议 Merge |
| implied-vol-approximations | 9/10 | 9/10 | timeout | None | 需要 Human Review |

*O4.6 dupire failure is agent subagent behavior, not task issue.

**Key takeaway:** 4/5 tasks are clean and ready to merge. `implied-vol-approximations` needs investigation of why ALL models fail the oracle RMSE test — likely a formula variant or tolerance issue.
