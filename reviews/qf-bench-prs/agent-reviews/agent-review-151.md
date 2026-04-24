# Review: PR #151 - fomc-tone-event-study
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
A "medium" fixed-income-NLP task: score FOMC statement tone using a provided lexicon, compute rolling tone surprises, align to Treasury yield events, run OLS regressions (baseline + state-adjusted with interactions), compute influence/diagnostics, and produce a full event panel. 18 FOMC meetings.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`
- Checked trial results and stdout for all models
- Reviewed test structure and expected output schema

### Trial Results
| Model | Reward |
|-------|--------|
| Haiku 4.5 | 0.0 |
| Opus 4.6 | 1.0 ✓ |
| Sonnet 4.5 | 0.0 |

### Scorecard
- Task contract / instruction: 5/5 — Extremely explicit: exact text normalization rules, exact rolling window definitions, exact AR(1) specification, exact regression variables
- Verifier robustness: 4/5 — Tests check schema, field existence, and pinned numeric values; 20 tests total
- Difficulty calibration: 4/5 — Good separation: only Opus passes, Haiku and Sonnet fail
- Benchmark integrity: 4/5 — Tests check structure heavily; numeric values in results.json are verified
- Financial correctness: 5/5 — Standard event-study methodology, proper Newey-West correction, AR(1) expected change, Cook's distance diagnostics

### Findings

#### [MINOR] Only Opus passes — Sonnet failure is surprising
For a "medium" task, having Sonnet fail is somewhat concerning. The task involves many precise steps (text tokenization → tone scoring → rolling surprise → yield event alignment → AR(1) estimation → two OLS regressions → influence analysis → diagnostics). The Sonnet failure may be due to a single misstep cascading. Opus passing 20/20 tests shows the task is well-calibrated for frontier models.

#### [MINOR] TF-IDF novelty adds NLP complexity to a rates task
The TF-IDF novelty score requires building vocabulary, computing idf, tf-idf vectors, and cosine similarity with rolling windows. This is non-trivial NLP mixed with fixed-income analysis. Appropriate for "medium" but pushes toward "hard" territory.

#### [NIT] Good design: 18 events is small enough to be tractable but large enough for meaningful regression.

### Summary
Excellent event-study task combining NLP tone scoring with fixed-income yield analysis. Good Opus-only discrimination (0/1/0). Financially sound methodology with proper regression diagnostics.

### Verdict
**建议 Merge** — Well-calibrated, financially correct, good model discrimination. The 0/1/0 pattern is a bit unusual but acceptable — it means the task effectively separates frontier reasoning capability.
