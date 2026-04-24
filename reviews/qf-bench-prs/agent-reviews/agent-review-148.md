# Review: PR #148 - futures-carry-repair / insider-buy-clusters / post-earnings-drift
Reviewer: Agent 🔍 | Date: 2026-04-23

This is a multi-task PR by judy12345. Reviewing each task separately.

---

## All Three Tasks: Infrastructure Blocker

### Trial Results (all three tasks)
| Model | Reward |
|-------|--------|
| Haiku 4.5 | ERROR (RuntimeError — Docker build fail) |
| Opus 4.6 | ERROR (RuntimeError — Docker build fail) |
| Sonnet 4.5 | ERROR (RuntimeError — Docker build fail) |

### [CRITICAL] Dockerfile uses nonexistent base image
All three tasks' Dockerfiles use `FROM quantitativefinance-bench-sandbox:latest` which does not exist:
```
pull access denied, repository does not exist or may require authorization
```

The standard base image used by other tasks is `finance-bench-sandbox:latest`. This typo/mismatch means **no trial could even start** for any of the three tasks. Zero data, zero signal.

---

## Task 1: futures-carry-repair (Hard — Repair a futures roll-yield carry strategy)

### What This Task Does
Repair a broken `run_backtest.py` for a futures carry strategy. Requires implementing contract selection with blackout days, annualized roll yield, vol-scaled weights, and full backtest mechanics. Debug-and-fix format similar to PR#141.

### Assessment (from instruction review only)
- **Instruction quality**: 4/5 — Well-specified with exact function signatures, explicit formulas for carry, vol, weights
- **Financial correctness**: 4/5 — Log roll yield, vol-scaled long/short weights, gross normalization are standard
- **Potential concern**: The `root_ret = (carry_curr - signal) * 0.01` formula is unusual — typically carry strategies use the actual futures return, not a scaled carry change. This may be intentional for simplification but should be documented.

### Verdict for futures-carry-repair
**不建议 Merge** — Docker image broken; no trial data. Fix `FROM` line and re-run.

---

## Task 2: insider-buy-clusters (Easy — Reconstruct insider-buy clusters from SEC filings)

### What This Task Does
Build insider buy cluster signals from Form 4 transaction data. Involves filtering, deduplication, amendment handling, rolling 3-day window analysis, and tie-breaking. Claimed "easy."

### Assessment (from instruction review only)
- **Instruction quality**: 5/5 — Very clear filtering rules, dedup logic, window definition, tie-break rules
- **Financial correctness**: 4/5 — Standard Form 4 analysis, reasonable cluster definition
- **Difficulty concern**: Labeled "easy" but has multi-step dedup + amendment logic + rolling window + tie-breaking which may be medium

### Verdict for insider-buy-clusters
**不建议 Merge** — Docker image broken; no trial data. Fix and re-run.

---

## Task 3: post-earnings-drift (Medium — Build a sector-neutral PEAD factor)

### What This Task Does
Construct a latest-rebalance cross-sectional panel with earnings seasonality signal, 2-day market reaction, sector neutralization, and decile assignment. Uses EPS data, daily prices, and a fixed rebalance date.

### Assessment (from instruction review only)
- **Instruction quality**: 5/5 — Clear step-by-step with explicit formulas, pinned evaluation date
- **Financial correctness**: 5/5 — Standard PEAD methodology: standardized earnings surprise + abnormal return + sector neutralization
- **Verifier**: Test recomputes the full reference from inputs (similar concern to double-sort)
- **Good design**: Single rebalance date makes the task deterministic and focused

### Verdict for post-earnings-drift
**不建议 Merge** — Docker image broken; no trial data. Fix and re-run. Task design looks solid.

---

## Overall PR #148 Verdict
**不建议 Merge** — All three tasks have a broken Dockerfile (`quantitativefinance-bench-sandbox:latest` should be `finance-bench-sandbox:latest`). No trials could run. Fix the base image and re-run all trials before review can proceed. The task designs themselves look reasonable based on instruction review.
