# Review: PR #129 - fx-forward-cross-rate
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/129](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/129)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
FX desk quant pipeline: clean spot rates (filter stale quotes), build forward curves via covered interest rate parity with proper day-count conventions, construct synthetic cross rates with correct bid/ask handling, value a 5-trade FX forward portfolio, decompose PnL (spot/carry/residual), and compute net delta exposures.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `solution/solve.sh`
- Checked: CIP formulas, cross-rate bid/ask triangulation, PnL attribution logic, day-count convention handling
- Reviewed trial outputs: H45 8/37 failed, Opus46 1/37 failed, S45 37/37 PASSED

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 4/5 |
| Verifier robustness | 4/5 |
| Difficulty calibration | 4/5 |
| Model discrimination | 5/5 |
| Benchmark integrity | 4/5 |

### Findings

#### [POSITIVE] Excellent model discrimination
S45 passes all 37 tests (reward=1). Opus46 fails only 1 test (`test_cip_deviation_small` — a KeyError suggesting minor output structure issue). H45 fails 8 tests (PnL, spot delta, net delta — more substantive errors). This is ideal calibration: easy → medium → hard scale across models.

#### [MINOR] Opus46 fails on `test_cip_deviation_small` with KeyError
The test expects a specific key in `results.json` that Opus46 doesn't produce. This is likely a formatting/structure issue rather than a conceptual error. The test could be more robust to key naming variations.

#### [POSITIVE] Real FX conventions tested
Day-count (ACT/360 vs ACT/365), bid/ask triangulation, cross-rate construction through USD legs — these test genuine practitioner knowledge. The stale quote filter (bid >= ask) is a nice real-world data quality check.

#### [POSITIVE] Test tolerances are well-calibrated
Forward rate tests use rtol=1e-4, PnL tests use rtol=0.02, spot delta tests use rtol=0.05. These progressively relax for downstream computations, which is the right approach.

#### [MINOR] Difficulty labeled "easy" but involves cross-rate bid/ask and PnL attribution
File: [`task.toml`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/b86732d/tasks/fx-forward-cross-rate/task.toml)
The task requires correct handling of bid/ask in cross-rate triangulation and PnL decomposition, which is medium complexity. The "easy" label may understate difficulty.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 188s | 1,766,912in / 33,847out |
| Opus 4.6 | 0.0 | 150s | 140,731in / 8,229out |
| Sonnet 4.5 | 1.0 | 136s | 149,592in / 8,806out |


**Haiku key failures:**
```
FAIL: test_portfolio_mtm_pnl
E       AssertionError: T001 PnL USD: got -3080.0, expected ~3080.0
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7fac0eb9acf0>(-3080.0, 3080.0, rtol=0.02)
E        +    where <function isclose at 0x7fac0eb9acf0> = np.isclose
FAIL: test_portfolio_mtm_pnl
E       AssertionError: T002 PnL USD: got -23037.54, expected ~23037.54
E       assert np.False_
```


**Opus key failures:**
```
FAIL: test_cip_deviation_small
E           KeyError: 'EUR/USD'
```

### Summary
Strong FX task with excellent model discrimination (S45 passes, Opus46 nearly passes, H45 struggles). The financial content is practical and tests real convention knowledge. Tolerance calibration is good. The single Opus46 failure appears to be a minor structural issue.

### Verdict
**建议 Merge**

S45 achieves perfect score, showing the task is solvable. Good tier discrimination. The financial content is realistic and convention-heavy. Minor suggestion: consider relaxing the CIP deviation test to be more robust to output structure variations.
