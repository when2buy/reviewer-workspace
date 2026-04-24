# Review: PR #150 - earnings-news-event-alpha
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
A "hard" cross-domain task: build an NLP event factor from earnings/news event snippets, align to tradable signal dates, validate predictive power with IC analysis, construct a long-short portfolio, and estimate alpha via OLS regression. Uses 8 liquid US tickers.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`
- Checked trial results and stdout for all models
- Reviewed reference_data files (checkpoints.json, expected.json, sample_expectations.json)

### Trial Results
| Model | Reward |
|-------|--------|
| Haiku 4.5 | 0.0 |
| Opus 4.6 | 0.0 |
| Sonnet 4.5 | 0.0 |

Opus46 stdout shows 4/6 tests failing (schema passes, but results and checkpoints fail).

### Scorecard
- Task contract / instruction: 4/5 — Detailed NLP + factor pipeline specification
- Verifier robustness: 4/5 — Uses external reference files (checkpoints.json, expected.json, sample_expectations.json) rather than inline hardcoded values
- Difficulty calibration: 2/5 — All models fail; zero discrimination
- Benchmark integrity: 4/5 — Reference data in separate files, tests check intermediate checkpoints
- Financial correctness: 4/5 — Standard IC analysis, long-short portfolio, CAPM alpha estimation

### Findings

#### [MAJOR] Zero discrimination across all models
All three score 0.0. The task combines NLP event classification (matching phrases from event_taxonomy.json), time alignment (signal dates without look-ahead), IC calculation, portfolio construction, and alpha regression. The NLP component adds ambiguity that may be hard for models to get exactly right.

#### [MINOR] Good test design with intermediate checkpoints
The test checks intermediate values (num_events_after_dedup, num_scored_events, etc.) via `solution.json` checkpoints. This helps diagnose where failures occur. The Opus46 run shows it passes schema/file-existence tests but fails on numeric accuracy.

#### [MINOR] test.sh has robust fallback logic
The test script tries pytest first, falls back to uvx, then to raw Python execution. Good defensive coding.

### Summary
Well-structured NLP+factor task with good test design (separate reference data, intermediate checkpoints). However, zero discrimination makes it currently unusable. The task might be too specification-heavy in the NLP scoring step.

### Verdict
**需要 Human Review** — Good task design but zero discrimination. Human should check if the NLP scoring rules are unambiguous enough, and whether the reference values are correct. Opus getting close (4/6 tests pass) suggests this might be fixable.
