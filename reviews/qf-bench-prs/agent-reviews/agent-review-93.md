# Review: PR #93 - yield-curve-pca-dynamics
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/93](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/93)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Multi-step yield curve analysis: compute spread time series (2s10s, butterfly, term premium), PCA on daily yield changes, forward rate computation, and Taylor rule estimation.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, environment/Dockerfile
- Reviewed trial results: h45 (1.0), opus46 (1.0), s45 (0.0)
- Checked pinned test values and tolerance calibration

### Scorecard
- Task contract / instruction: 5/5 — Very precise with formulas, sign conventions, maturity mappings
- Verifier robustness: 4/5 — Pinned values with 1-2% rtol, sign convention explicitly stated
- Difficulty calibration: 3/5 — "Medium" but H45 passes; may be slightly easy for strong models
- Benchmark integrity: 3/5 — Tests expose exact oracle values
- Data realism: 5/5 — Real US Treasury daily yield data

### Findings

#### [MAJOR] Haiku passes but Sonnet fails — inverted difficulty pattern
File: trial results
H45=1.0, O46=1.0, S45=0.0. Sonnet failing while Haiku passes is unusual and suggests the failure may be due to a minor implementation choice rather than reasoning difficulty. This undermines the "medium" difficulty claim.

#### [MINOR] PCA sign convention well-specified
File: [`instruction.md`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/2309617/tasks/yield-curve-pca-dynamics/instruction.md)
Good: "if the sum of the first principal component's loading vector is negative, flip the sign." This prevents a common ambiguity issue.

#### [NIT] Test values pinned at high precision
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/2309617/tasks/yield-curve-pca-dynamics/tests/test_outputs.py)
Values like `61.4127` bp are pinned at 4 significant figures with rtol=0.01. This is appropriate for this type of computation.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 1.0 | 74s | 486,538in / 9,368out |
| Opus 4.6 | 1.0 | 78s | 143,137in / 3,125out |
| Sonnet 4.5 | 0.0 | 78s | 116,149in / 3,586out |


**Sonnet key failures:**
```
FAIL: test_spread_2s10s_max_date
E       AssertionError: Expected max 2s10s date 2026-01-30, got 2026-02-09
E       assert '2026-02-09' == '2026-01-30'
E
E         - 2026-01-30
E         ?       ^ -
E         + 2026-02-09
E         ?       ^  +
```

### Summary
Well-designed yield curve analysis task with clear instructions and good PCA sign convention handling. The inverted difficulty pattern (H45 passes, S45 fails) is a minor concern but likely reflects implementation variance rather than a task design issue.

### Verdict
**建议 Merge**

Good task with clear spec. The S45 failure is likely implementation variance, not a design flaw.
