# Review: PR #144 - double-sort / residual-momentum / stable-residual
Reviewer: Agent 🔍 | Date: 2026-04-23

This is a multi-task PR by mingjun-sun. Reviewing each task separately.

---

## Task 1: double-sort (Betting Against Beta & Momentum Dependent Double Sort)

### What This Task Does
Construct and backtest an equal-weighted, transaction-cost-adjusted corner portfolio based on a dependent double sort of BAB (`betabab_1260d`) and momentum (`ret_12_7`). Uses monthly stock panel with 150 stocks over 695 months.

### Trial Results
| Model | Reward |
|-------|--------|
| Haiku 4.5 | ERROR (RewardFileNotFoundError) |
| Opus 4.6 | ERROR (RewardFileNotFoundError) |
| Sonnet 4.5 | ERROR (RewardFileNotFoundError) |

### Findings

#### [CRITICAL] Verifier broken — RewardFileNotFoundError for all models
All three trials fail with `RewardFileNotFoundError`. The h45 test-stdout shows a checksum verification failure, suggesting the test.sh has a `set -euo pipefail` at the top that causes early exit before writing reward.txt. Looking at `test.sh`: it uses `set -euo pipefail` at the top, then later `set +e` around pytest, but the `exit $STATUS` at the end will cause the container to exit with a non-zero code if tests fail, and importantly the reward file IS written. The actual issue is the test-stdout showing a checksum failure BEFORE pytest runs — this may be a Harbor infrastructure issue, not a task issue.

#### [MAJOR] test_outputs.py recomputes the full solution inside the test
The test file contains `_compute_reference()` which rebuilds the entire double-sort strategy from input data. This means the verifier contains a complete canonical solution. While the agent can't access `/tests/` at runtime under Harbor assumptions, this is fragile for benchmark integrity.

#### [MINOR] Claimed "hard" but the task is a straightforward dependent double sort
The quintile formula and equal-weighting are explicitly given. The main complexity is the turnover calculation and transaction cost deduction. This seems more "medium" than "hard."

### Verdict for double-sort
**不建议 Merge** — Verifier is broken (all trials error). Fix the test infrastructure, then re-run trials.

---

## Task 2: residual-momentum (Residual Momentum vs. Raw Momentum)

### What This Task Does
Evaluate whether residual momentum dominates raw momentum using Fama-MacBeth regressions, OOS expanding-window forecasts, and deterministic portfolio sorts. Three models (A: raw, B: residual, C: both) with 15 controls. Outputs FMB results, monthly OOS spreads, and monthly coefficients.

### Trial Results
| Model | Reward |
|-------|--------|
| Haiku 4.5 | 0.0 |
| Opus 4.6 | 1.0 ✓ |
| Sonnet 4.5 | 1.0 ✓ |

### Findings

#### Good discrimination (0/1/1) — proper "medium" calibration
H45 fails, both frontier models pass. This is ideal for a medium-difficulty task.

#### [MINOR] Very detailed specification reduces reasoning requirement
The instruction specifies exact quintile formula, exact Newey-West lag, exact ddof, exact OOS start rule. This tests implementation fidelity more than financial reasoning. But for a benchmark, this determinism is appropriate.

#### [NIT] No solution/ directory visible — only `solve.sh` exists. The task relies on the instruction being self-contained, which it is.

### Verdict for residual-momentum
**建议 Merge** — Well-specified, good model discrimination, financially sound FMB methodology.

---

## Task 3: stable-residual (Stable Residual Alpha with Beta-Neutral, Turnover-Capped Execution)

### What This Task Does
Build a fully deterministic monthly long-short equity strategy with: residualization of 14 signals against 15 controls, expanding-window coefficient estimation with sign-filtering, beta-neutral projection, turnover-capped execution, and transaction costs. Very complex end-to-end pipeline.

### Trial Results
| Model | Reward |
|-------|--------|
| Haiku 4.5 | 0.0 |
| Opus 4.6 | 0.0 |
| Sonnet 4.5 | 0.0 |

### Findings

#### [MAJOR] Zero discrimination — all models fail
Even Opus 4.6 scores 0.0 on this task. The instruction is extremely long and involves many sequential steps (winsorization → residualization → OLS → sign-filtering → ranking → beta-neutral projection → turnover cap → transaction costs). Any small error cascades through the pipeline.

#### [MAJOR] Excessive specification complexity
The task has 14 signals, 15 controls, winsorization, cross-sectional OLS residualization, 36-month median coefficients with sign-filtering (24/36 threshold), beta-neutral projection via null-space, turnover capping with iterative clipping, and multiple output files. This is closer to "implement a full quant research pipeline" than a focused benchmark task.

#### [MINOR] Claimed "medium" but should be "hard"
Given that Opus 4.6 fails, this is at minimum "hard." The task.toml says difficulty = "Medium" which is miscalibrated.

### Verdict for stable-residual
**不建议 Merge** — Zero discrimination. Either simplify the pipeline or re-label as "hard" and accept aspirational difficulty. The difficulty label "Medium" is wrong.

---

## Overall PR #144 Verdict
- double-sort: **不建议 Merge** (broken verifier)
- residual-momentum: **建议 Merge** ✓
- stable-residual: **不建议 Merge** (zero discrimination, miscalibrated difficulty)
