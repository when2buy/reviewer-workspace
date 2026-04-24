# Review: PR #120 - barra-cne6-risk + ipca-latent-factors
Reviewer: Agent 🔍 | Date: 2026-04-23

## Part A: barra-cne6-risk

### What This PR Does
Build a Barra CNE-6 style multi-factor equity risk model: cross-sectional WLS factor return estimation, Newey-West HAC factor covariance, EWMA specific risk, and portfolio risk decomposition (style vs industry).

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/verifier.py`, `tests/reference_data/expected.json`, `solution/`
- Checked: WLS estimation, Newey-West HAC, EWMA specific risk, risk decomposition, verifier design

### Scorecard
- Task contract: 4/5 — well-specified but relies on params.json conventions
- Verifier robustness: 5/5 — multi-phase verifier with PERFECT/IMPERFECT/WRONG classification and partial credit
- Difficulty calibration: 3/5 — H:0.23, O:0.27, S:0.31 (all low scores)
- Financial correctness: 5/5 — standard Barra methodology
- Benchmark integrity: 4/5 — expected.json under /tests/ (Harbor-protected); tolerances are generous (5% rtol)

### Findings

#### [CRITICAL] All models score very low (H:0.23, O:0.27, S:0.31)
Even Opus only achieves 0.27. This suggests the task may be:
1. Too hard / under-specified for current models
2. Have verifier issues that reject valid implementations
3. Require specific implementation choices not stated in the instruction

A task where the best model scores 0.31 provides limited benchmark value — it may be measuring noise rather than capability.

#### [POSITIVE] Multi-phase verifier with partial credit
File: `tests/verifier.py`
The verifier classifies results as PERFECT (all pass), IMPERFECT (deliverables pass, checkpoints partially fail), or WRONG (deliverables fail). This is sophisticated and allows partial credit.

#### [MAJOR] Instruction may under-specify critical implementation details
For a Barra-style model, many decisions affect results: how to handle missing characteristics, exact winsorization method, market-cap weighting in WLS, Newey-West lag structure. If the expected values assume specific choices not fully documented in the instruction, agents will fail even with correct methodology.

#### [MINOR] Good use of glossary.json
Providing a glossary for technical terms is helpful.

---

## Part B: ipca-latent-factors

### What This PR Does
Estimate an IPCA model (Kelly, Pruitt, Su 2019) — latent factor model where loadings are linear functions of characteristics. Compute R², factor Sharpe ratios, and GRS test.

### Scorecard
- Task contract: 4/5 — good specification but ALS convergence depends on implementation
- Verifier robustness: 5/5 — same multi-phase verifier as barra-cne6-risk
- Difficulty calibration: 3/5 — H:0.33, O:0.69, S:0.29 (Opus does best but still under 0.7)
- Financial correctness: 5/5 — IPCA formulation is correct
- Benchmark integrity: 4/5 — expected.json with generous tolerances

### Findings

#### [MAJOR] ALS initialization sensitivity
IPCA estimation via alternating least squares is sensitive to initialization. The task specifies a random seed, but the exact initialization method (how F is initialized from the seed) is not specified in the instruction. Different initializations can converge to different local optima, especially with the eigendecomposition rotation step.

#### [MINOR] O:0.69 is the best score — moderate difficulty
Opus achieves 0.69, suggesting it gets most deliverables right but fails on some checkpoints. This is reasonable for a "hard" task.

#### [POSITIVE] GRS test is a good discriminator
The GRS joint alpha test requires correct factor estimation AND proper statistical testing. This tests both econometric implementation and statistical knowledge.

---

## Combined Summary
Both tasks use the same excellent multi-phase verifier framework. Financial methodology is correct in both. The barra-cne6-risk task has concerning low scores across all models (max 0.31), suggesting under-specification. The ipca-latent-factors task is better calibrated with Opus at 0.69.

## Combined Verdict
- **barra-cne6-risk**: **需要 Human Review** — All models score ≤0.31. Need to investigate whether this is under-specification or genuine difficulty. If the former, tighten the instruction.
- **ipca-latent-factors**: **建议 Merge** — Good discrimination (H:0.33, O:0.69, S:0.29), correct methodology, partial credit verifier. The ALS sensitivity concern is inherent to the method and mitigated by generous tolerances.
