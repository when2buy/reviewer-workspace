# Review: PR #95 - fixed-income-market-stress
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Construct a composite market stress indicator from Treasury yield curve metrics and FINRA TRACE bond trading volume data. Tasks include curve shape metrics, volatility, flow metrics (flight-to-quality, HY/IG ratio), liquidity proxies, composite stress scoring, and regime classification.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, environment/Dockerfile
- Reviewed trial results: h45 (1.0), opus46 (0.0), s45 (1.0)
- Checked test pinned values and data merging logic

### Scorecard
- Task contract / instruction: 4/5 — Detailed with precise formulas
- Verifier robustness: 4/5 — Pinned values with 1-3% rtol, date checks
- Difficulty calibration: 3/5 — Medium; unusual that Opus fails while H45/S45 pass
- Benchmark integrity: 3/5 — Test values exposed in assertions
- Data realism: 5/5 — Real Treasury + TRACE data, complex merging required

### Findings

#### [MAJOR] Opus fails while Haiku and Sonnet pass — inverted discrimination
File: trial results
H45=1.0, O46=0.0, S45=1.0. Opus failing on a "medium" task while Haiku passes suggests either: (1) a subtle spec ambiguity that Opus interprets differently, or (2) unlucky implementation choice. This is concerning for calibration.

#### [MINOR] Complex data merging may introduce ambiguity
File: `instruction.md`
The task requires merging Treasury (MM/DD/YYYY, most-recent-first) with TRACE (YYYY-MM-DD) data. Date format differences and filtering requirements create many points where implementations could diverge.

### Summary
Complex cross-domain task combining yield curve analysis with TRACE flow metrics. The data merging requirements add genuine difficulty. However, the inverted model discrimination (Opus fails, Haiku passes) is a concern worth investigating.

### Verdict
**需要 Human Review**

The Opus failure while Haiku passes warrants investigation. If Opus fails due to a spec ambiguity, the instruction may need clarification. If it's just implementation variance, the task is fine to merge.
