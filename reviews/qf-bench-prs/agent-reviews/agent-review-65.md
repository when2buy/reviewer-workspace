# Review: PR #65 - bond-portfolio-analytics
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/65](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/65)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Comprehensive fixed-income analytics for an 8-bond Treasury portfolio: accrued interest (30/360), dirty price, YTM (Newton-Raphson), Macaulay/modified duration, convexity, DV01, z-spread (continuously compounded), key-rate durations (2/5/10/30Y), and portfolio-level aggregates with scenario P&L.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, Dockerfile
- Checked: trial results for h45, opus46, s45 (all reward=1.0)
- Analyzed: test structure, oracle values, tolerances

### Scorecard
- Task contract / instruction: 5/5
- Verifier robustness: 4/5
- Difficulty calibration: 3/5 — claimed "medium" but all models pass easily
- Model discrimination: 1/5 — zero discrimination
- Benchmark integrity: 4/5

### Findings

#### [MAJOR] All three models pass with reward=1.0 — zero model discrimination
Results: H45=1.0, Opus=1.0, S45=1.0

All three models (including Haiku, the weakest) pass all tests. The task is claimed "medium" difficulty but provides no discrimination between model tiers. A benchmark task that every model passes offers no signal.

**Note:** The trial output shows only 9 tests (B1, B2 bond metrics + portfolio + ordering), which is far fewer than the 60+ tests in the current test file (8 CUSIPs × multiple metrics + portfolio aggregates). This suggests the trials were run on an earlier, simpler version of the tests. The current comprehensive test suite may provide better discrimination — **re-running trials on the current test version is essential before drawing conclusions.**

#### [MINOR] Instruction is extremely prescriptive — almost a recipe
The instruction specifies exact methods (Newton-Raphson with specific initial guesses, tolerances, max iterations), leaving little room for the agent to demonstrate financial understanding vs. just following detailed steps.

#### [NIT] test.sh uses `uv` for dependency installation
File: [`tests/test.sh`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/9d6e63e/tasks/bond-portfolio-analytics/tests/test.sh)

Uses `curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh` which adds network dependency at test time. Not a blocker but differs from the simpler `pip3 install` pattern used in other tasks.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-bond-portfolio-analytics) | 1.0 | 44s | 138,086in / 1,602out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-bond-portfolio-analytics) | 1.0 | 47s | 85,672in / 982out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-bond-portfolio-analytics) | 1.0 | 50s | 86,974in / 1,432out |

### Summary
Well-crafted fixed-income task with excellent instruction clarity and comprehensive test coverage in the current version. The main concern is that trial results show all models passing on what appears to be a simpler test version. Re-trial with the current comprehensive tests is needed to assess actual discrimination.

### Verdict
**需要 Human Review** — The current test file is comprehensive and well-designed, but the trial evidence (all 1.0) was collected on a simpler test version. Need re-trials on the current tests to confirm difficulty calibration. If all models still pass easily, consider making it harder (e.g., tighter tolerances, additional edge cases).
