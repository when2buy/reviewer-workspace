# Review: PR #136 - quantamental-earnings-jumpfilter-committee
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Complex quantamental pipeline: compute three fundamental agent scores (surprise, quality, peer) from earnings data, fit stochastic process filter (martingale/GBM/OU) on trailing prices, combine into final signal via committee weighting × process conviction, construct long-short portfolio, and compute performance metrics.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `solution/solve.sh`, `solution/oracle_solver.py` (structure)
- Checked: agent score definitions, OU fitting, AIC model selection, portfolio construction rules, test expectations
- Reviewed trial outputs: H45/Opus46/S45 all failed with Docker build errors — **no valid trial data**

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 4/5 |
| Verifier robustness | 3/5 |
| Difficulty calibration | N/A |
| Model discrimination | N/A |
| Benchmark integrity | 3/5 |

### Findings

#### [CRITICAL] All trials failed with Docker environment build errors
All three model trials (H45, Opus46, S45) failed with `RuntimeError: Docker compose command failed for environment quantamental-earnings-jumpfilter-committee`. No agent output was produced. The provided scores are (H:N/A, O:N/A, S:N/A). Without working trials, calibration and discrimination cannot be assessed.

#### [MAJOR] Task complexity is very high — may be unreasonably difficult
The task requires: (1) parsing 7+ input files with different schemas, (2) computing 3 distinct agent scores with cross-sectional z-scores, vendor reference mismatch detection, and sector-level percentile ranking, (3) fitting 3 stochastic processes and selecting via AIC, (4) portfolio construction with turnover and transaction costs, (5) producing 6 output files. This is at least 2-3x more complex than other "hard" tasks in this batch.

#### [MAJOR] Test pins exact values without tolerance framework
File: `tests/test_outputs.py`
Expected values are hard-coded: `num_rebalance_dates: 86`, `num_traded_rows: 73`, `avg_process_conviction: 0.643...`, `annualized_return: -0.00425...`, etc. The test structure uses individual assertions rather than the generic tolerance-based verifier.

#### [MAJOR] Instruction relies heavily on params.json without showing parameter values
The instruction references `params.json` for weights, lookback days, penalties, conviction rules, etc. without showing the actual values. Agents must correctly parse and use ~20+ configuration parameters. Combined with the multi-file input, this creates a very high surface area for errors.

#### [MINOR] OU fitting on detrended prices is unusual
The instruction specifies fitting OU on `x_t = cumsum(log_returns - gbm_mu)` — residuals after removing drift. This is a valid but non-standard approach that tests whether agents read the instruction carefully.

#### [POSITIVE] Rich, realistic multi-agent architecture
The committee + stochastic filter design is a genuinely interesting quantamental approach. The fundamental agent scores capture different aspects (earnings surprise, data quality, peer comparison) that reflect real quant workflows.

### Summary
Ambitious and interesting task design, but completely untested — all trials failed at the Docker build stage. The task's extreme complexity (7+ input files, 3 agent scores, 3 stochastic processes, portfolio construction) makes it likely very difficult even for frontier models. Cannot assess calibration without working trials.

### Verdict
**不建议 Merge**

No valid trial data due to Docker build failures. The task cannot be evaluated for calibration or discrimination. Blockers: (1) fix the Docker environment so trials can run, (2) run all three model trials, (3) assess whether the complexity level is appropriate. The financial design is interesting but needs proof of workability.
