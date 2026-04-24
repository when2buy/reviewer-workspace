# Review: PR #87 - yield-curve-bootstrap-immunization
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/87](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/87)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Multi-step fixed income task: bootstrap zero-coupon discount curve from par yields, compute bond analytics (price, YTM, duration, convexity, KRDs, Z-spread), immunize a liability, fit Nelson-Siegel, and stress-test the portfolio.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, environment/Dockerfile
- Reviewed trial results for h45 (0.0), opus46 (1.0), s45 (1.0)
- Checked financial correctness of test assertions

### Scorecard
- Task contract / instruction: 5/5 — Extremely detailed with precise formulas (bootstrapping, KRD bumping, Brentq intervals)
- Verifier robustness: 5/5 — Tests verify structural consistency (par bonds price at par, spot rates from DFs) rather than just pinning values
- Difficulty calibration: 4/5 — Hard tag appropriate; H45 fails, O46/S45 pass
- Benchmark integrity: 5/5 — Tests use self-consistency checks (DF→spot rate, par-bond pricing identity) which are harder to game
- Data realism: 4/5 — FRED par yield data, real bond specs

### Findings

#### [MINOR] Claimed difficulty is "hard" but Opus/Sonnet both pass
File: [`task.toml`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/86728be/tasks/yield-curve-bootstrap-immunization/task.toml)
Both frontier models pass. This may be medium-hard rather than hard, though bootstrapping + immunization + Nelson-Siegel is a substantial multi-step pipeline.

#### [NIT] No solve.py provided
File: [`solution/`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/86728be/tasks/yield-curve-bootstrap-immunization/solution/)
Oracle solution is absent. Test consistency checks partially compensate.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-yield-curve-bootstrap-immunization) | 0.0 | 355s | 2,947,082in / 45,187out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-yield-curve-bootstrap-immunization) | 1.0 | 149s | 217,107in / 8,088out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-yield-curve-bootstrap-immunization) | 1.0 | 383s | 1,152,759in / 46,708out |


**Haiku key failures:**
```
FAIL: test_df_forward_rate_from_discount_factors
E           assert np.False_
E            +  where np.False_ = <function isclose at 0x7feb6384f4f0>(np.float64(0.0352054448664259), np.float64(0.037699777005655015), atol=1e-06)
E            +    where <function isclose at 0x7feb6384f4f0> = np.isclose
FAIL: test_ns_fitted_spot_rates
E           AssertionError: T=1: Svensson=-0.074351, bootstrapped=0.046884, diff=1212.35bp
E           assert np.float64(0.12123456174369736) < 0.0005
E            +  where np.float64(0.12123456174369736) = abs((np.float64(-0.07435097584484686) - np.float64(0.0468835858988505)))
```

### Summary
Excellent fixed-income benchmark task. The multi-step pipeline (bootstrap → analytics → immunization → stress test) is a genuine test of quant finance reasoning. Self-consistency checks in tests are a strength. Good model discrimination.

### Verdict
**建议 Merge**

Well-designed, well-tested, production-quality benchmark item.
