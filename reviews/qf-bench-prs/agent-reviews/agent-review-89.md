# Review: PR #89 - lob-pc-signal
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/89](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/89)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
LOB (Limit Order Book) signal construction: compute Weighted True OFI across 15 levels, PCA to extract PC1, rolling regression to predict next-minute mid returns from crypto order flow data.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, environment/Dockerfile
- Reviewed trial results: ALL THREE FAIL with Docker build error (wrong base image)
- No actual agent execution occurred

### Scorecard
- Task contract / instruction: 4/5 — Clear pipeline description
- Verifier robustness: 2/5 — Tests pin exact reference values with rtol=1e-2, potential for brittle PCA sign/ordering
- Difficulty calibration: N/A — Cannot assess, no trials completed
- Benchmark integrity: 3/5 — Full reference dict in test file exposes all answers

### Findings

#### [CRITICAL] Dockerfile uses wrong base image — all trials fail to build
File: [`environment/Dockerfile`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/2812e40/tasks/lob-pc-signal/environment/Dockerfile)
Uses `quantitative-finance-bench-sandbox:latest` instead of `finance-bench-sandbox:latest`. All three trials (h45, opus46, s45) fail with: `pull access denied, repository does not exist or may require authorization`. No agent execution or verification occurred.

#### [MAJOR] Full reference values embedded in test file
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/2812e40/tasks/lob-pc-signal/tests/test_outputs.py)
The `REFERENCE` dict contains all 30+ expected values with full precision. An agent that reads the test file can trivially hardcode these values. This is a significant anti-cheat concern.

#### [MINOR] PCA sign convention not specified in instruction
File: [`instruction.md`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/2812e40/tasks/lob-pc-signal/instruction.md)
PCA eigenvectors are sign-ambiguous. The instruction doesn't specify a sign convention, but the reference values assume a specific sign. This could cause agents to produce correct but sign-flipped results.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | error reading | — | — |
| Opus 4.6 | error reading | — | — |
| Sonnet 4.5 | error reading | — | — |

### Summary
Cannot be evaluated — the Dockerfile base image is wrong, preventing any trial from running. Additionally, the test file contains full reference answers, creating an anti-cheat vulnerability.

### Verdict
**不建议 Merge**

Blocker: Dockerfile base image `quantitative-finance-bench-sandbox:latest` doesn't exist. Needs to be changed to the correct base image. Also needs anti-cheat mitigation for exposed reference values.
