# Review: PR #186 — pot-gpd-bitcoin
Reviewer: Agent (automated) | Date: 2026-04-26

## What This PR Does
Peaks-over-Threshold GPD tail risk for Bitcoin. Agent implements the model from instruction and produces output files.

## Trial Evidence
- **Haiku 4.5:** 🟡 25/46 (reward=0.0) — partial pass
- **Sonnet 4.5:** Pending
- **Opus 4.6:** Pending

## What I Did to Review This
- Oracle verification: PASS
- Haiku H4.5 trial via Harbor
- Deep-dived instruction.md, tests/test_outputs.py, solution/ code
- Analyzed failure patterns in verifier output

## Findings

### [MAJOR] Convention/parameterization ambiguity
GPD shape parameter xi sign flipped. Agent gets xi=-0.16, oracle expects xi=+0.15. scipy.stats.genpareto uses c=-xi convention. Instruction gives VaR/ES formulas with xi but doesn't clarify scipy convention mismatch. If agent uses scipy.genpareto.fit() directly, sign will be wrong.

## Verdict
**需要 Human Review** — 🟡 The failures may stem from legitimate ambiguity in the instruction rather than agent incompetence. Awaiting Sonnet/Opus trials for more evidence. If stronger models also fail on the same tests, instruction likely needs clarification.
