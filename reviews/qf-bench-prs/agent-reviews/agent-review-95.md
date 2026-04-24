# Review: PR #95 - fixed-income-market-stress
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/95](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/95)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Construct a composite market stress indicator from Treasury yield curve metrics and FINRA TRACE bond trading volume data. Tasks include curve shape metrics, volatility, flow metrics (flight-to-quality, HY/IG ratio), liquidity proxies, composite stress scoring, and regime classification.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, environment/Dockerfile
- Reviewed trial results: h45 (1.0), opus46 (0.0), s45 (1.0)
- Checked test pinned values and data merging logic

### Scorecard
- Task contract / instruction: 4/5 — Detailed with precise formulas
- Verifier robustness: 4/5 — Pinned values with 1-3% rtol, date checks
- Difficulty calibration: 3/5 — Medium; unusual that Opus fails while H45/S45 pass
- Benchmark integrity: 3/5 — Test values exposed in assertions
- Data realism: 5/5 — Real Treasury + TRACE data, complex merging required

### Findings

#### [MAJOR] Opus fails while Haiku and Sonnet pass — inverted discrimination
File: trial results
H45=1.0, O46=0.0, S45=1.0. Opus failing on a "medium" task while Haiku passes suggests either: (1) a subtle spec ambiguity that Opus interprets differently, or (2) unlucky implementation choice. This is concerning for calibration.

#### [MINOR] Complex data merging may introduce ambiguity
File: [`instruction.md`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/db4c264/tasks/fixed-income-market-stress/instruction.md)
The task requires merging Treasury (MM/DD/YYYY, most-recent-first) with TRACE (YYYY-MM-DD) data. Date format differences and filtering requirements create many points where implementations could diverge.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-fixed-income-market-stress) | 1.0 | 146s | 1,084,625in / 24,805out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-fixed-income-market-stress) | 0.0 | 94s | 135,565in / 4,731out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-fixed-income-market-stress) | 1.0 | 106s | 361,674in / 4,601out |


**Opus key failures:**
```
FAIL: test_adf_statistic
E       AssertionError: ADF statistic expected ~-1.20, got 0.4632
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f02cd7c90f0>(0.4632, -1.198, rtol=0.05)
E        +    where <function isclose at 0x7f02cd7c90f0> = np.isclose
```

### Summary
Complex cross-domain task combining yield curve analysis with TRACE flow metrics. The data merging requirements add genuine difficulty. However, the inverted model discrimination (Opus fails, Haiku passes) is a concern worth investigating.

### Verdict
**需要 Human Review**

The Opus failure while Haiku passes warrants investigation. If Opus fails due to a spec ambiguity, the instruction may need clarification. If it's just implementation variance, the task is fine to merge.
