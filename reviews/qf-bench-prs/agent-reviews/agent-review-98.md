# Review: PR #98 - nelson-siegel-yield-curve-fit
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/98](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/98)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Fit 6-parameter Nelson-Siegel-Svensson yield curves to 25 years of FRED Treasury constant-maturity data (2000–2024), day by day, using warm-started L-BFGS-B optimization. Output fitted parameters + RMSE per day, and flag outlier dates where RMSE > 10bp.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked trial results: H45=0.0, Opus46=0.0, S45=0.0
- Analyzed test stdout for Opus46 failure mode

### Scorecard
- Task contract / instruction: 5/5 — exceptionally detailed, reproducible
- Verifier robustness: 3/5 — outlier count range too tight
- Difficulty calibration: 2/5 — all three models score 0.0 for a single borderline test
- Benchmark integrity: 4/5 — warm-start chain prevents hardcoding
- Data realism: 5/5 — real FRED data, 25 years

### Findings

#### [CRITICAL] Outlier count window too narrow — single test blocks all models
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/6aa2daf/tasks/nelson-siegel-yield-curve-fit/tests/test_outputs.py) line 177

The test asserts `150 < len(df) < 210` for outlier dates. Opus46's output produced 269 outlier dates — passing 24/25 tests but failing this one. The outlier count depends sensitively on the warm-start optimization trajectory; small numerical differences in the L-BFGS-B chain compound over 6000+ days, shifting many dates near the 10bp boundary. The range [150, 210] is too tight for a benchmark that targets multiple solver implementations.

All three models (H45, Opus46, S45) score 0.0 because of this single test or similarly tight checks. This means the task has **zero discrimination** — it cannot distinguish a nearly-correct solution from a completely wrong one.

**Recommendation:** Widen the outlier count window to [100, 350] or remove the count check entirely and rely on the RMSE distribution tests (which all pass). Alternatively, add partial credit.

#### [MAJOR] Over-prescribed optimization method reduces to implementation matching
File: [`instruction.md`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/6aa2daf/tasks/nelson-siegel-yield-curve-fit/instruction.md)

The instruction specifies exact optimizer, method, tolerances, bounds, initial seed, and warm-start strategy. This means the task tests whether agents can faithfully transcribe an optimization recipe, not whether they understand yield curve fitting. While reproducibility is the stated goal, this makes the task more of a "follow instructions precisely" challenge than a quant reasoning task.

#### [MINOR] No solve.py provided
File: [`solution/solve.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/6aa2daf/tasks/nelson-siegel-yield-curve-fit/solution/solve.py)

The solution file is empty. This is acceptable for review but means the oracle solution cannot be independently verified.

#### [NIT] test.sh uses `$?` after `if [ $? -eq 0 ]` pattern correctly
The reward writing pattern is clean.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-nelson-siegel-yield-curve-fit) | 0.0 | 294s | 620,511in / 9,645out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-nelson-siegel-yield-curve-fit) | 0.0 | 291s | 216,275in / 3,030out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-nelson-siegel-yield-curve-fit) | 0.0 | 337s | 326,678in / 6,738out |


**Haiku key failures:**
```
E       AssertionError: Expected ~180 outlier dates (±30), got 269
E       assert 269 < 210
```


**Opus key failures:**
```
E       AssertionError: Expected ~180 outlier dates (±30), got 269
E       assert 269 < 210
```

### Summary
The task is well-designed with real data and a meaningful quant problem. However, the outlier count test creates a cliff where all models score 0 despite producing high-quality NSS fits (24/25 tests pass for Opus46). The task has zero model discrimination in its current form.

### Verdict
**不建议 Merge**

The outlier count window [150, 210] is too narrow and causes all three models to fail a single borderline test, yielding 0.0 across the board. Widening the window or adding partial credit would make this a strong benchmark item.
