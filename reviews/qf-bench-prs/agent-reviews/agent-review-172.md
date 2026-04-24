# Review: PR #172 - Merton Jump-Diffusion
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/172](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/172)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Calibrate a Merton jump-diffusion model to SPY daily returns via MLE, price European calls using the Merton series formula across a 3×7 grid, compare to Black-Scholes, and extract implied volatility smiles.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py (229 lines), Dockerfile
- Checked: No trial results exist (H:N/A, O:N/A, S:N/A)
- Analyzed test structure and financial correctness

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 3/5 — pinned values present
- Difficulty calibration: N/A — no trial data
- Model discrimination: N/A
- Benchmark integrity: 3/5

### Findings

#### [CRITICAL] No trial results available
No trials were run for any model. Without run evidence, difficulty calibration and verifier robustness cannot be empirically validated.

#### [MAJOR] Pinned ATM Merton prices may be fragile
File: [`tests/test_outputs.py:160-`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/609e209/tasks/merton-jump-diffusion/tests/test_outputs.py:160-#L172)
The test pins ATM Merton prices to specific oracle values: T=0.25→24.72, T=0.5→37.69, T=1.0→58.67 with rtol=0.05 (5%). Since Merton MLE is multi-modal (similar to Kou), different valid local optima may produce prices outside this 5% window. This is the same class of issue as PR#170 — and without trials we can't tell if it's actually blocking.

#### [MAJOR] No oracle solution
File: [`solution/solve.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/609e209/tasks/merton-jump-diffusion/solution/solve.py)
Empty. Combined with no trials, there's zero empirical evidence this task works.

#### [MINOR] Structural overlap with PR#170 (Kou)
This task is very similar to PR#170 — same SPY data, same MLE approach, same Poisson-weighted series pricing. The main difference is jump distribution (normal vs double-exponential). Consider whether both are needed or if one should be dropped to avoid redundancy.

#### [MINOR] Test log-likelihood threshold
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/609e209/tasks/merton-jump-diffusion/tests/test_outputs.py#L87)
`assert ll > 2000` — this is a reasonable lower bound but depends on the data. Without oracle reference, hard to validate.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-merton-jump-diffusion) | no trial data | — | — |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-merton-jump-diffusion) | no trial data | — | — |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-merton-jump-diffusion) | no trial data | — | — |

### Summary
The task is financially sound and well-specified, closely paralleling PR#170 but with Merton's normal jumps instead of Kou's double-exponential. The major concern is zero empirical evidence — no trials, no oracle solution. The pinned ATM prices with 5% tolerance may be fragile for multi-modal MLE.

### Verdict
**需要 Human Review** — No trial results to validate. Task design is sound but empirical calibration is unverified. Run trials before merging. Also consider redundancy with PR#170.
