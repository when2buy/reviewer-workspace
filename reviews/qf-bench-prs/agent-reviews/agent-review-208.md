# Review: PR #208 — garch-sp500-fit
Reviewer: Agent (automated) | Date: 2026-04-26

## What This PR Does
GARCH(1,1) with Student-t innovations on S&P 500. Agent implements the model from instruction and produces output files.

## Trial Evidence
- **Haiku 4.5:** 🟡 33/47 (reward=0.0) — partial pass
- **Sonnet 4.5:** Pending
- **Opus 4.6:** Pending

## What I Did to Review This
- Oracle verification: PASS
- Haiku H4.5 trial via Harbor
- Deep-dived instruction.md, tests/test_outputs.py, solution/ code
- Analyzed failure patterns in verifier output

## Findings

### [MAJOR] Convention/parameterization ambiguity
GARCH-t parameterization issue. 14 failures all in Student-t section (nu, alpha, beta, loglik). Different GARCH libraries (arch, statsmodels, hand-written MLE) parameterize Student-t differently. Instruction says 'Student-t with nu > 2' but doesn't specify library. Oracle uses hand-written MLE.

## Verdict
**需要 Human Review** — 🟡 The failures may stem from legitimate ambiguity in the instruction rather than agent incompetence. Awaiting Sonnet/Opus trials for more evidence. If stronger models also fail on the same tests, instruction likely needs clarification.
