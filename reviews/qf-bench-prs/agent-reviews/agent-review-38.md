# Review: PR #38 - Zero-Coupon Bootstrapping
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/38](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/38)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Bootstrap a zero-coupon yield curve from par coupon rates. Agent must implement the standard bootstrapping algorithm with linear interpolation of zero rates for intermediate coupon dates, then output zero rates, discount factors, and forward rates.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py, test.sh, Dockerfile
- Reviewed trial results for h45, opus46, s45
- Checked financial correctness of bootstrapping formula and test logic

### Trial Results
| Model | Reward |
|-------|--------|
| Haiku 4.5 | 1.0 |
| Opus 4.6 | 1.0 |
| Sonnet 4.5 | 1.0 |

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 4/5
- Difficulty calibration: 2/5
- Model discrimination: 1/5
- Benchmark integrity / anti-cheating: 3/5
- Data realism: 3/5

### Findings

#### [MAJOR] All three models pass — no discrimination
All models (including Haiku) pass with reward 1.0. For a "medium" difficulty task, there is zero model separation. The algorithm is fully specified in the instruction, making this essentially a code-transcription task rather than a reasoning task.

#### [MINOR] Tests verify properties, not exact values
Tests check monotonicity, consistency between DF and zero rates, and par-bond repricing within atol=0.002. This is good for robustness but combined with fully-prescribed algorithm means the verifier is lenient enough that any correct implementation passes.

#### [MINOR] No solve.py provided
The solution directory appears empty. This doesn't affect benchmark operation but makes review harder — can't verify oracle correctness.

#### [NIT] Forward rate formula only covers integer maturities
Instruction defines forward rates for integer T≥2 and T=1, but if maturities include non-integer values the forward rate definition is ambiguous.

### Summary
Financially correct task with a well-specified bootstrapping algorithm. Tests are property-based and sound. However, all three models pass trivially — this task has no discriminative power. The instruction is so prescriptive that it's a coding exercise, not a quant reasoning task.

### Verdict
**建议 Merge**

Clean, correct task. Low discrimination is a concern but acceptable for a "medium" difficulty baseline item.
