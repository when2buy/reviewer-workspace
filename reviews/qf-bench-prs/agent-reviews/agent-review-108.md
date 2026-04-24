# Review: PR #108 - delta-hedging-pnl-simulation
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/108](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/108)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Simulates discrete delta hedging of a short European call with escrowed-dividend Black-Scholes, asymmetric transaction costs, time-varying IV, and discrete cash dividends at four rebalancing frequencies.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `solution/solve.sh`, `environment/data/fee_schedule.csv`
- Checked: financial formulas, verifier logic, leakage, calibration scores

### Scorecard
- Task contract / instruction: 5/5 — exceptionally detailed, every convention spelled out
- Verifier robustness: 4/5 — pinned expected values with tight tolerances; all-or-nothing
- Difficulty calibration: 4/5 — medium is reasonable; H:0.0 suggests Haiku struggles with the multi-step simulation
- Benchmark integrity: 4/5 — hardcoded expected values in tests, but task complexity makes hardcoding non-trivial
- Data realism: 4/5 — synthetic but well-designed paths

### Findings

#### [MINOR] Hardcoded expected values in test_outputs.py
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/eca3bfb/tasks/delta-hedging-pnl-simulation/tests/test_outputs.py)
All expected PnL, TC, and dividend values are pinned constants (e.g., `EXPECTED_SIMS`). An agent could theoretically extract these from the test file and hardcode outputs. However, the Harbor assumption should prevent test file access at runtime, and the values are numerous and interconnected enough that partial hardcoding is unlikely to help.

#### [MINOR] Canary present but no task.toml author_email
File: [`task.toml`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/eca3bfb/tasks/delta-hedging-pnl-simulation/task.toml)
`author_email` is empty string. Minor metadata gap.

#### [NIT] Solution uses inline Python heredoc
File: [`solution/solve.sh`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/eca3bfb/tasks/delta-hedging-pnl-simulation/solution/solve.sh)
Clean and readable; no issues.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 348s | 3,078,174in / 31,869out |
| Opus 4.6 | 1.0 | 69s | 110,216in / 2,172out |
| Sonnet 4.5 | 1.0 | 87s | 101,275in / 4,045out |


**Haiku key failures:**
```
FAIL: test_t0_price
E       AssertionError: t0.price=0.12663637009305617, expected ~8.746564
E       assert False
E        +  where False = <function isclose at 0x7f2343f8c070>(0.12663637009305617, 8.746564, rtol=0.0001)
E        +    where <function isclose at 0x7f2343f8c070> = np.isclose
FAIL: test_t0_delta
E       AssertionError: t0.delta=0.1867080711055233, expected ~0.576496
E       assert False
```

### Summary
Well-crafted derivatives pricing benchmark. The instruction is extremely detailed — every convention is locked down, eliminating ambiguity. The escrowed-dividend BS model, asymmetric TC, and time-varying IV create genuine complexity. The H:0.0 / O:1.0 / S:1.0 split shows good model discrimination at the Haiku tier. The verifier is deterministic and covers both structure and numerical accuracy. No blockers.

### Verdict
**建议 Merge**

Clean, well-specified task with good model discrimination. Ready for production.
