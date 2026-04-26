# Review: PR #183 — pca-yield-curve
Reviewer: Agent (automated) | Date: 2026-04-26

## What This PR Does
PCA-based yield curve VaR. Agent implements the model from instruction and produces output files.

## Trial Evidence
- **Haiku 4.5:** 🟡 22/26 (reward=0.0) — partial pass
- **Sonnet 4.5:** Pending
- **Opus 4.6:** Pending

## What I Did to Review This
- Oracle verification: PASS
- Haiku H4.5 trial via Harbor
- Deep-dived instruction.md, tests/test_outputs.py, solution/ code
- Analyzed failure patterns in verifier output

## Findings

### [MAJOR] Convention/parameterization ambiguity
PCA eigenvector sign convention ambiguity. Test pins exact VaR values (184900) but PCA sign is mathematically indeterminate. Agent gets correct magnitudes but different signs lead to different portfolio VaR. Need to verify if instruction fully specifies the sign convention.

## Verdict
**需要 Human Review** — 🟡 The failures may stem from legitimate ambiguity in the instruction rather than agent incompetence. Awaiting Sonnet/Opus trials for more evidence. If stronger models also fail on the same tests, instruction likely needs clarification.
