# Review: PR #88 - event-study-earnings
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Market-model event study around earnings announcements: estimate market model via OLS, compute abnormal returns, CAR/CAAR, and statistical significance tests (Corrado rank test, Kolari-Pynnönen adjusted t-stat).

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, environment/Dockerfile
- Reviewed trial results: h45 (0.0), opus46 (0.0), s45 (0.0) — ALL FAIL
- Analyzed test-stdout to identify failure patterns

### Scorecard
- Task contract / instruction: 4/5 — Clear on the event study methodology
- Verifier robustness: 2/5 — **Blocker**: Oracle likely has a bug in KP t-statistic computation
- Difficulty calibration: 1/5 — **Blocker**: All three models fail, including Opus 4.6
- Benchmark integrity: 3/5 — Tests are mostly self-consistency based, which is good

### Findings

#### [CRITICAL] All models fail — likely oracle/verifier bug in KP t-statistic
File: `tests/test_outputs.py`
All three models (H45, O46, S45) fail. Opus and Sonnet both pass 32/34 tests — the only failures are `test_st_kp_t_full_pinned` and `test_st_kp_t_day0_pinned`. The Kolari-Pynnönen (2010) adjusted t-statistic has a very tight tolerance (rtol=0.005), and the pinned oracle values (0.26409569, 0.33249276) may be computed with a subtly different formula than what the instruction describes.

Haiku fails 8 tests due to type errors (string vs float in caar_summary.json), suggesting the JSON serialization is fragile, but the core issue is that even the strongest models cannot match the KP oracle values.

**This strongly suggests either**: (1) the instruction underspecifies the KP formula, or (2) the oracle values are wrong. The 0.5% relative tolerance is very tight for a formula that involves cross-sectional correlation estimation.

#### [MAJOR] Instruction may underspecify the Kolari-Pynnönen formula
File: `instruction.md`
The instruction mentions the KP (2010) test but the exact formula implementation details (e.g., how to compute cross-sectional correlation, how to adjust for estimation error) may need to be more explicit given the tight pinned tolerances.

### Summary
The event study methodology is sound, and most tests pass across models. However, the KP t-statistic oracle values appear to be wrong or the instruction underspecifies the formula. All three models failing on the same tests is a strong signal of an oracle bug, not agent weakness.

### Verdict
**不建议 Merge**

Oracle bug: all three models fail on the same KP t-statistic tests. The pinned values or tolerance need to be corrected before this task is usable.
