# Review: PR #109 - variance-swap-replication
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/109](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/109)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Agent must clean a dirty option chain, compute fair variance-swap strike via Carr-Madan/DDKZ log-contract replication with trapezoidal weights, extract ATM IV at the forward, and price a long variance swap under three RV scenarios.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `solution/solve.sh`, `environment/data/params.json`
- Checked: replication formula, OTM classification, filter logic, trapezoidal weights, scenario PnL

### Scorecard
- Task contract: 5/5 — every step precisely specified with formulas
- Verifier robustness: 5/5 — tests cover structure, counts, intermediate values, and identity checks
- Difficulty calibration: 4/5 — medium; H:1.0, O:1.0, S:1.0 means all models pass (could be too easy)
- Benchmark integrity: 4/5 — test values are pinned but interconnected through formulas
- Financial correctness: 5/5 — Carr-Madan replication, OTM selection, trapezoidal weights all correct

### Findings

#### [MINOR] All models pass (H:1.0, O:1.0, S:1.0) — weak discrimination
The task may be too well-specified for its difficulty level. All three model tiers solve it perfectly. The step-by-step instruction essentially serves as a recipe. Consider whether this provides useful signal.

#### [NIT] `test_scenario_pnl_identity` is a good sanity check
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/211cbb3/tasks/variance-swap-replication/tests/test_outputs.py)
Verifies `pnl = 10_000 * (RV² - K_var²)` independently — good practice.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-variance-swap-replication) | 1.0 | 81s | 416,575in / 7,984out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-variance-swap-replication) | 1.0 | 76s | 129,408in / 2,353out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-variance-swap-replication) | 1.0 | 85s | 112,161in / 3,651out |

### Summary
Textbook-quality variance swap replication task. Financially correct, well-specified, deterministic. The only concern is weak model discrimination — all tiers pass comfortably, suggesting the instruction over-specifies the solution path. Still a valid benchmark item for testing whether agents can follow a precise quantitative finance recipe.

### Verdict
**建议 Merge**

Correct and clean. The weak discrimination is a design choice (medium difficulty), not a bug.
