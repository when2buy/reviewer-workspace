# Review: PR #96 - credit-spread-decomposition
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/96](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/96)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Decompose BAA-Treasury credit spread into default risk, liquidity risk, and inflation risk components using rolling 48-month OLS with Newey-West HAC inference and covariance-based variance decomposition. Identify regime breaks.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, environment/Dockerfile
- Reviewed trial results: h45 (0.0), opus46 (1.0), s45 (1.0)
- Checked FRED data handling, HAC inference, and pinned values

### Scorecard
- Task contract / instruction: 5/5 — Exceptional detail on data handling (FRED "." encoding, LIBOR discontinuation, monthly alignment)
- Verifier robustness: 5/5 — Tests pin sampled decomposition values at multiple dates, HAC t-stats, and regime break dates
- Difficulty calibration: 4/5 — Medium is appropriate; H45 fails, O46/S45 pass. Newey-West is non-trivial
- Benchmark integrity: 4/5 — Sampled values at specific dates are harder to reverse-engineer than full series
- Data realism: 5/5 — Real FRED data (BAA, AAA, DGS10, TEDRATE, T10YIE), 2003-2024

### Findings

#### [MINOR] Variance decomposition can produce negative percentages
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/d9fd50f/tasks/credit-spread-decomposition/tests/test_outputs.py)
Sampled variance decomposition values include negative percentages (e.g., `pct_liquidity = -0.481116` at 2016-02-01). This is mathematically valid for covariance-based decomposition but may confuse users. The instruction should clarify this is expected.

#### [NIT] TED rate forward-fill after LIBOR cessation is a simplification
File: [`instruction.md`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/d9fd50f/tasks/credit-spread-decomposition/instruction.md)
Forward-filling TEDRATE after 2022-01 is pragmatic but not financially rigorous. Acceptable for a benchmark task.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-credit-spread-decomposition) | 0.0 | 146s | 690,861in / 11,962out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-credit-spread-decomposition) | 1.0 | 143s | 328,396in / 6,267out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-credit-spread-decomposition) | 1.0 | 537s | 1,541,890in / 32,940out |


**Haiku key failures:**
```
E       AssertionError: Expected 217 rows (264 aligned months - 48 window + 1), got 211
E       assert 211 == 217
E       AssertionError: First date 2007-01-01 00:00:00 should be 2006-12-01 (48-month window from Jan 2003)
E       assert Timestamp('2007-01-01 00:00:00') == Timestamp('2006-12-01 00:00:00')
E        +  where Timestamp('2007-01-01 00:00:00') = min()
E        +  and   Timestamp('2006-12-01 00:00:00') = <class 'pandas._libs.tslibs.timestamps.Timestamp'>('2006-12-01')
E        +    where <class 'pandas._libs.tslibs.timestamps.Timestamp'> = pd.Timestamp
E       AssertionError: Date 2006-12-01 not found in results
```

### Summary
Excellent credit analysis task. The rolling OLS + Newey-West + variance decomposition pipeline is a genuine test of quantitative credit skills. Data handling challenges (FRED quirks, LIBOR discontinuation, monthly alignment) add realistic complexity. Good model discrimination.

### Verdict
**建议 Merge**

Well-designed, well-calibrated, production-quality benchmark item.
