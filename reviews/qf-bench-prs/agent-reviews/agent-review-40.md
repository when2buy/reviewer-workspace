# Review: PR #40 - Earnings Surprise Calculator
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/40](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/40)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Calculate earnings surprise metrics (raw surprise, SUE, YoY growth, beat/miss/meet classification) for multiple companies across quarters.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py, test.sh, Dockerfile
- Reviewed trial results for all three models
- Checked formula correctness

### Trial Results
| Model | Reward |
|-------|--------|
| Haiku 4.5 | 1.0 |
| Opus 4.6 | 1.0 |
| Sonnet 4.5 | 1.0 |

### Scorecard
- Task contract / instruction: 5/5
- Verifier robustness: 4/5
- Difficulty calibration: 1/5
- Model discrimination: 1/5
- Benchmark integrity: 2/5

### Findings

#### [MAJOR] Trivially easy — no model discrimination
All three models pass. Every formula is explicitly given. This is pure formula transcription with no ambiguity.

#### [MINOR] test_msft_high_beat_rate is data-dependent assertion
The test `test_msft_high_beat_rate` asserts MSFT beat_rate >= 0.5. This leaks domain knowledge about the data content but is acceptable as a sanity check.

#### [MINOR] Verifier recomputes surprise_pct and SUE from input
Tests `test_surprise_calculation` and `test_sue_calculation` independently recompute expected values from input data, which is good practice for verification.

#### [NIT] test.sh uses `set -euo pipefail` then `set +e` before pytest
Good pattern — avoids the brittle `$?` issue.

### Summary
Extremely straightforward calculation task. All formulas are given explicitly in the instruction. No quant reasoning required — this is a data transformation exercise. Clean implementation but provides zero discriminative signal.

### Verdict
**建议 Merge**

Correct but trivial. Consider whether this adds value to the benchmark given zero discrimination.
