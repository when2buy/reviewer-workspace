# Review: PR #105 - yield-curve-bond-immunization
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Bootstrap zero curves from Treasury par yields, price a hedge universe (fixed bullets, callable, FRN), compute KRDs and PCA factor exposures, construct a liability immunization hedge at t0, then re-hedge at t1 with stress testing.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked trial results: H45=0.0, Opus46=0.0, S45=0.0
- Analyzed Opus46 test stdout (36 passed, 5 failed)

### Scorecard
- Task contract / instruction: 4/5 — detailed conventions, explicit methods
- Verifier robustness: 3/5 — some tests use string dict keys that depend on output format
- Difficulty calibration: 2/5 — all models fail, zero discrimination
- Model discrimination: 1/5 — no separation
- Benchmark integrity: 4/5 — convention-sensitive, deterministic
- Data realism: 5/5 — real Treasury data, realistic bond parameters

### Findings

#### [CRITICAL] All models score 0.0 despite passing 36/41 tests (Opus46)
Opus46 passes 88% of tests but scores 0.0. The 5 failures are:
1. `test_pinned_zero_rates[zero_curve_t1.csv-20.0-0.05093]` — zero rate slightly off
2. `test_pinned_prices[BUL15-103.676961-104.208211]` — cascading from curve error
3. `test_objective_is_low` — hedge objective too high (cascading)
4. `test_target_krd_mismatch_is_small` — KRD dict uses numeric keys, test expects string "5.0"
5. `test_selected_krd_bucket_improves` — same KeyError on "5.0"

#### [MAJOR] KRD key format mismatch causes spurious failures
File: `tests/test_outputs.py` lines 201, 228

The test accesses `self.data["portfolio_target_krd"]["5.0"]` using string keys. If the agent outputs numeric keys (e.g., `{5.0: ...}` in JSON which becomes `{"5": ...}` or `{5.0: ...}`), the lookup fails with KeyError. This is a verifier bug — the test should normalize key types.

#### [MAJOR] Cascading failures from single curve point
The t1 zero rate at 20Y is slightly off, which cascades to BUL15 pricing, then to hedge objective and KRD matching. A single bootstrap error at the long end propagates through 4 test failures.

#### [MINOR] Task complexity is very high for "hard"
Two-phase hedge (t0 + t1), 8 instruments including callable and FRN, PCA factor exposures, stress testing. Expert estimate of 120 min seems low.

### Summary
Excellent fixed-income task with real data and meaningful quant content (bootstrapping, bond pricing, immunization). However, verifier issues (KRD key format, cascading from single curve point) cause all models to fail. The task would likely show discrimination if the verifier were fixed.

### Verdict
**不建议 Merge**

Fix two verifier issues: (1) normalize KRD dictionary key types (string vs numeric), (2) consider wider tolerance on the t1 20Y zero rate or add partial credit. The underlying task is strong and would likely discriminate well after fixes.
