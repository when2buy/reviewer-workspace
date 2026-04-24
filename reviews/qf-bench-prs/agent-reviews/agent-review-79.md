# Review: PR #79 - execution-is-vwap
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/79](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/79)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Comprehensive Transaction Cost Analysis (TCA): implementation shortfall, VWAP slippage, market impact decomposition, participation rates, TWAP comparison, Huang-Stoll spread decomposition, Almgren-Chriss optimal execution with time-varying impact, and Kyle's lambda estimation. A massive 11-section microstructure task.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, Dockerfile
- Checked: trial results for h45, opus46, s45 (all reward=0.0)
- Analyzed: failure patterns across models

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 3/5
- Difficulty calibration: 4/5
- Model discrimination: 5/5 — excellent separation
- Benchmark integrity: 4/5

### Findings

#### [MAJOR] Excellent model discrimination — Sonnet nearly passes
- **Sonnet: 1 failure** (efficiency_ratio_ord002) — nearly perfect
- **Opus: 5 failures** (AC actual cost, efficiency ratios, Kyle's lambda)
- **Haiku: 9 failures** (AC + Kyle's lambda + bucket counts)

This is excellent discrimination — the hardest sections (Almgren-Chriss optimal execution and Kyle's lambda) separate models effectively, while the classical TCA metrics (IS, VWAP, Huang-Stoll) are achievable by all tiers.

#### [MAJOR] Kyle's lambda Lee-Ready quote lag specification is a key trap
File: [`instruction.md`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/08cc1de/tasks/execution-is-vwap/instruction.md), Section 10

The instruction specifies: "use the mid price from the bar strictly *before* the fill timestamp (not the bar at or before). This implements the standard 1-period quote lag from Lee & Ready (1991)." This is a subtle but important detail — Haiku gets Kyle's lambda negative (wrong sign) while Opus/Sonnet get it positive but with different magnitudes. Good test of careful reading.

#### [MINOR] AC optimal cost with non-SPD impact matrix
File: [`instruction.md`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/08cc1de/tasks/execution-is-vwap/instruction.md), Section 9

The test expects `well_posedness_satisfied = False` for ORD001 and `impact_matrix_min_eigenvalue < 0`. When A is not positive definite, the "optimal schedule" from `A⁻¹1` may not be a minimum. The instruction handles this by still computing the schedule — this is mathematically valid but worth noting that the "optimal" cost may not be meaningful when A is not SPD.

The AC actual cost for ORD003 is expected to be **negative** (-39,446) — this is only possible when A is not SPD. Good test of edge case handling.

#### [MINOR] Bucket count disagreement for ORD001
Haiku produces 13 eta buckets instead of expected 12 (60min / 5min). This suggests Haiku includes a partial bucket at the boundary. The instruction says "5-minute bucket within the execution window (start_time to end_time)" — whether the endpoint is inclusive or exclusive is not specified.

#### [NIT] Difficulty label "hard" with expert estimate 30 min
File: [`task.toml`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/08cc1de/tasks/execution-is-vwap/task.toml)

Expert time of 30 min seems low for an 11-section TCA task. The task is genuinely hard (Sonnet barely passes), so the "hard" label is appropriate, but the time estimate should probably be 60-90 min.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 86s | 576,389in / 16,702out |
| Opus 4.6 | 0.0 | 173s | 263,984in / 9,766out |
| Sonnet 4.5 | 0.0 | 179s | 360,562in / 10,446out |


**Haiku key failures:**
```
FAIL: test_ac_actual_cost_ord003
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f0e30d26cb0>(-45166.02561538044, -39446.63, atol=200.0)
E        +    where <function isclose at 0x7f0e30d26cb0> = np.isclose
FAIL: test_efficiency_ratio_ord005
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f0e30d26cb0>(1.0, 0.865, atol=0.05)
E        +    where <function isclose at 0x7f0e30d26cb0> = np.isclose
```


**Opus key failures:**
```
FAIL: test_ac_actual_cost_ord003
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7ff84fe38130>(-44799.800517724485, -39446.63, atol=200.0)
E        +    where <function isclose at 0x7ff84fe38130> = np.isclose
FAIL: test_efficiency_ratio_ord002
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7ff84fe38130>(-0.018399840706703932, 0.15, atol=0.05)
E        +    where <function isclose at 0x7ff84fe38130> = np.isclose
```

### Summary
Excellent benchmark task with superb model discrimination. The instruction is comprehensive and contains well-placed domain traps (quote conventions, Lee-Ready lag, non-SPD impact matrices). Sonnet's near-perfect performance (1 failure) shows the task is solvable but challenging.

The single Sonnet failure (efficiency_ratio_ord002) and the 5 Opus failures in AC/Kyle sections represent genuine difficulty, not spec bugs.

### Verdict
**需要 Human Review** — Very strong task. Sonnet at 1 failure suggests the calibration is excellent. The remaining failures are in the hardest sections (AC optimal execution, Kyle's lambda) which provide genuine discrimination. Minor questions: (1) Should bucket boundary inclusivity be clarified? (2) Is the expert time estimate realistic? If the human reviewer confirms the oracle values for AC/Kyle are correct, this should merge.
