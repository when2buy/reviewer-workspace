# Review: PR #102 - intraday-volume-fitting-and-execution-scheduling
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/102](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/102)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Given intraday OHLCV data, evaluate four volume-share prediction models (mean, median, EWMA, winsorized mean) via rolling walk-forward R², select the best model, and generate an execution schedule for a given order.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked trial results: H45=0.0, Opus46=1.0, S45=1.0
- Analyzed H45 test stdout for failure mode

### Scorecard
- Task contract / instruction: 4/5 — very detailed but lengthy
- Verifier robustness: 4/5 — reference-based with tolerances; schedule quantity tolerance QTY_TOL=1 is tight
- Difficulty calibration: 4/5 — good separation: H45=0.0, Opus46=1.0, S45=1.0
- Model discrimination: 3/5 — separates H45 from stronger models but Opus/S45 both pass
- Benchmark integrity: 4/5 — reference data comparison, hard to game
- Data realism: 4/5 — realistic intraday volume data

### Findings

#### [MAJOR] H45 fails on schedule construction, not model fitting
File: H45 test-stdout

H45 passes the model selection tests (excluded days, model performance, best model) but fails on `final_schedule` tests. The schedule cumulative quantity deviates by up to 220 from reference (tolerance is 1). This means H45 correctly identifies the best model but incorrectly constructs the execution schedule — likely a different interpretation of which bars are eligible (the "strictly after order datetime" test also fails).

The instruction specifies the schedule should use bars "strictly after" the order datetime, but this boundary condition is apparently tricky for H45.

#### [MINOR] Hard difficulty rating seems appropriate
File: [`task.toml`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/e818dc5/tasks/intraday-volume-fitting-and-execution-scheduling/task.toml)

Rated "hard" with expert estimate 90 min. The H45=0.0 vs Opus46/S45=1.0 split supports this — the task requires careful attention to multiple data processing steps, rolling evaluation, and schedule construction.

#### [MINOR] Reference data comparison is byte-sensitive for excluded_days
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/e818dc5/tasks/intraday-volume-fitting-and-execution-scheduling/tests/test_outputs.py)

`test_excluded_days_matches_reference` uses `pd.testing.assert_frame_equal` with `check_dtype=True`, which is strict. This is appropriate since excluded days should be deterministic.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-intraday-volume-fitting-and-execution-scheduling) | 0.0 | 343s | 2,958,939in / 38,484out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-intraday-volume-fitting-and-execution-scheduling) | 1.0 | 93s | 130,537in / 3,906out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-intraday-volume-fitting-and-execution-scheduling) | 1.0 | 285s | 540,116in / 11,670out |


**Haiku key failures:**
```
FAIL: test_final_schedule_only_bars_strictly_after_order_datetime
E       AssertionError: every scheduled bar must be strictly after order.json datetime
E       assert np.False_
E        +  where np.False_ = all()
FAIL: test_final_schedule_matches_reference_datetimes_and_quantities
E       AssertionError:
E       Arrays are not equal
E       datetime column must match reference exactly
```

### Summary
Well-designed execution/microstructure task with realistic intraday data. Good model separation between H45 and stronger models. The schedule construction boundary condition trips up weaker models, which is legitimate discrimination. The task works as intended.

### Verdict
**建议 Merge**

Good difficulty calibration (H45=0.0, Opus46=1.0, S45=1.0), clear specification, robust verifier. The schedule boundary condition that trips H45 is a legitimate test of instruction-following precision.
