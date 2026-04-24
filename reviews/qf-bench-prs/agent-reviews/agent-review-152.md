# Review: PR #152 - american-binomial-tree
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/152](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/152)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Price American put/call options via the Cox-Ross-Rubinstein binomial tree. Tasks include: CRR tree construction, European/American pricing across a moneyness×maturity grid, early exercise boundary extraction, convergence analysis, and Greeks via finite differences. Input is SPY daily OHLCV data.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked: financial correctness, test leakage, tolerance calibration, model discrimination
- Reviewed: trial results for h45, opus46, s45

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 5 |
| Verifier robustness | 5 |
| Difficulty calibration | 3 |
| Model discrimination | 1 |
| Benchmark integrity / anti-cheating | 4 |
| Data realism / determinism | 5 |

### Findings

#### [MINOR] No model discrimination — all three models pass
All three models (Haiku, Opus, Sonnet) pass all 38 tests with reward=1.0. This is a "medium-hard" task that doesn't discriminate at all. The CRR binomial tree is a well-known textbook algorithm; the instruction is very explicit about the method. This is more of a coding exercise than a reasoning challenge.

#### [MINOR] Tests pin specific values with generous tolerances
Tests like `test_atm_amer_put_T025` use `atol=1.0` (~5% relative tolerance on an $18 option). This is reasonable for tree-based pricing but doesn't strongly validate correctness. The property-based tests (monotonicity, convergence, American ≥ European) are well-chosen.

#### [NIT] Difficulty label "medium-hard" is generous
Given 3/3 model pass rate, "medium" would be more accurate. The task is a straightforward CRR implementation with clear specifications.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 1.0 | 220s | 1,111,175in / 13,829out |
| Opus 4.6 | 1.0 | 129s | 210,629in / 5,986out |
| Sonnet 4.5 | 1.0 | 277s | 446,307in / 11,339out |

### Summary
This is a clean, well-structured task with correct financial content. The instruction is thorough, tests cover structural properties well, and the verifier is robust. The main weakness is zero model discrimination — all three models pass easily, making this task uninformative for benchmarking purposes. The canary strings are present. No anti-cheat concerns (tests don't leak exact answers; they check properties and ranges).

### Verdict
**建议 Merge**

Task is correct and well-implemented. The lack of discrimination is a calibration concern but not a blocker — some "medium" tasks passing all models is expected in a benchmark suite.
