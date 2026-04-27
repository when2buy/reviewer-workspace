# Review: PR #42 - PCA Factor Portfolio
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/42](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/42)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Extract PCA factors from asset returns, compute factor exposures, and construct a factor-neutral portfolio via constrained least-squares hedging.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py, test.sh, Dockerfile
- Reviewed trial results for all three models
- Verified PCA and lstsq hedging logic

### Trial Results
| Model | Reward |
|-------|--------|
| Haiku 4.5 | 1.0 |
| Opus 4.6 | 1.0 |
| Sonnet 4.5 | 1.0 |

### Scorecard
- Task contract / instruction: 5/5
- Verifier robustness: 5/5
- Difficulty calibration: 2/5
- Model discrimination: 1/5
- Benchmark integrity: 4/5

### Findings

#### [MAJOR] All models pass — no discrimination despite "hard" label
Task is labeled "hard" but all three models including Haiku pass. The instruction prescribes the exact algorithm: use sklearn PCA, numpy lstsq with specific augmented matrix construction. This is too prescriptive for a "hard" task.

#### [POSITIVE] Verifier has reference implementation
`_ref()` recomputes EVR, components, neutral weights from scratch using the same sklearn PCA. This ensures correctness.

#### [POSITIVE] Good test coverage
Tests verify: EVR ordering, sum < 1, reference match, factor loadings shape, neutral weights sum, near-zero exposures, and exact neutral weight match. Comprehensive.

#### [MINOR] PCA sign ambiguity
PCA components have arbitrary sign. The instruction and tests use `sklearn.decomposition.PCA` which has deterministic sign convention (largest absolute loading positive), so this is handled correctly.

#### [MINOR] Difficulty mislabeled
Should be "medium" at most given the fully prescribed algorithm and universal pass rate.

### Summary
Clean, well-verified PCA portfolio construction task. Financially sound approach. But the "hard" label is not justified — all models pass trivially because the algorithm is fully specified.

### Verdict
**建议 Merge**

Correct task. Recommend relabeling difficulty from "hard" to "medium".
