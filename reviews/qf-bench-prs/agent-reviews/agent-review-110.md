# Review: PR #110 - evt-pot-var
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/110](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/110)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Compute VaR/ES using four methods (Historical, Normal, EVT-POT, GARCH-EVT) on S&P 500 data, then run a rolling backtest with Kupiec/Christoffersen tests. Partial-credit scoring based on per-deliverable pass rate.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `solution/solve.sh`, `environment/data/formulas.md`, `tests/reference_data/expected.json`
- Checked: EVT formulas, GARCH-EVT pipeline, backtest logic, Kupiec/Christoffersen formulas, verifier design

### Scorecard
- Task contract: 4/5 — detailed but dense; some conventions buried in the wall of text
- Verifier robustness: 5/5 — partial credit via 53 deliverables with per-deliverable tolerance
- Difficulty calibration: 4/5 — H:0.71, O:1.0, S:0.92 shows good spread
- Financial correctness: 5/5 — formulas.md provides exact references; solution matches standard EVT/GARCH theory
- Benchmark integrity: 4/5 — reference expected.json in tests/reference_data contains all answers but is under /tests/ (Harbor-protected)

### Findings

#### [MINOR] Instruction is dense and convention-heavy
File: [`instruction.md`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/3a1d2c1/tasks/evt-pot-var/instruction.md)
The instruction packs many conventions into a single wall of text: `np.quantile(..., method='lower')`, `ddof=1`, strict greater-than for exceedances, percentage-return scaling for GARCH, etc. While each is necessary for determinism, the density may test reading comprehension more than quant skill. This is a design choice, not a bug.

#### [MINOR] `formulas.md` in environment/data — good practice
Providing exact formulas in `/app/data/formulas.md` reduces ambiguity and ensures the agent has a clear reference. Well done.

#### [NIT] Partial credit scoring is well-designed
File: [`tests/test.sh`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/3a1d2c1/tasks/evt-pot-var/tests/test.sh)
Uses `passed/total` from CTRF report as reward. This is much better than all-or-nothing for a 53-deliverable task.

#### [NIT] GARCH-EVT rolling backtest is computationally expensive
The rolling backtest refits GARCH(1,1) at each step. This is correct but may stress agent timeout (1800s). The solution uses `arch` package which is fast enough.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.707547 | 502s | 2,329,933in / 23,487out |
| Opus 4.6 | 1.0 | 186s | 187,944in / 5,851out |
| Sonnet 4.5 | 0.924528 | 218s | 563,415in / 8,729out |


**Haiku key failures:**
```
FAIL: test_verification
E       AssertionError: assert 'WRONG' == 'PERFECT'
E
E         - PERFECT
E         + WRONG
```


**Sonnet key failures:**
```
FAIL: test_verification
E       AssertionError: assert 'WRONG' == 'PERFECT'
E
E         - PERFECT
E         + WRONG
```

### Summary
Comprehensive tail-risk benchmark covering EVT-POT, GARCH-EVT, and backtesting. The partial-credit verifier is well-designed. Good model discrimination (H:0.71 vs O:1.0). Financial formulas are correct and well-documented. The main risk is instruction density, but this is inherent to the domain.

### Verdict
**建议 Merge**

Solid risk management benchmark with good discrimination and partial credit. Ready.
