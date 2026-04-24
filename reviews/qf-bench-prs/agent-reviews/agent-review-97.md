# Review: PR #97 - factor-momentum-spanning
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Investigate factor momentum — timing Fama-French factors based on trailing returns. Construct factor momentum portfolio, run spanning regressions, multi-horizon robustness, Politis-Romano block bootstrap inference, and regime-conditional analysis.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, environment/Dockerfile
- Reviewed trial results: h45 (0.0), opus46 (0.0), s45 (0.0) — ALL FAIL
- Analyzed test-stdout for all three models

### Scorecard
- Task contract / instruction: 4/5 — Detailed pipeline, clear data parsing requirements
- Verifier robustness: 2/5 — **Concern**: oracle values may be wrong or tolerances too tight
- Difficulty calibration: 1/5 — **Blocker**: All models fail, including Opus 4.6
- Benchmark integrity: 3/5 — Expected values exposed in test file

### Findings

#### [CRITICAL] All models fail — possible oracle calibration issue
File: `tests/test_outputs.py`
All three models fail, with 16-26 test failures each. The failures are concentrated in:
- `alpha_monthly` and `alpha_tstat` for spanning regressions (across periods)
- Multi-horizon alpha values
- Bootstrap inference values
- Regime alpha values

Notably, S45 has the fewest failures (16) and passes many structural tests. The failing tests are all pinned numerical values. When all three models consistently fail on the same value-pinning tests, the most likely explanation is that the oracle values are computed with a subtly different implementation than what the instruction specifies.

#### [MAJOR] Multiple potential sources of numerical divergence
File: `instruction.md`
The pipeline involves: (1) parsing multi-line header CSVs, (2) compounding daily→monthly returns, (3) 12-1 momentum signal construction, (4) Newey-West t-stats, (5) block bootstrap. Each step introduces potential for small numerical differences that compound. The tolerances (e.g., alpha_monthly ±0.0003) may be too tight for this chain.

#### [MAJOR] Difficulty labeled "hard" but all models fail for wrong reasons
File: `task.toml`
If all models fail due to tolerance/oracle mismatch rather than inability to implement the pipeline, the task doesn't actually measure difficulty — it measures luck in matching the oracle's exact implementation choices.

### Summary
The factor momentum concept is strong, and the multi-step pipeline is genuinely challenging. However, all three models failing suggests the oracle values need recalibration or tolerances need loosening. The S45 result (52 pass / 16 fail) shows agents can implement most of the pipeline correctly — they just can't match the exact pinned values.

### Verdict
**不建议 Merge**

All three models fail, likely due to oracle calibration rather than genuine difficulty. Recommend: (1) verify oracle values with an independent implementation, (2) loosen tolerances on pinned values, especially for bootstrap and regime analysis.
