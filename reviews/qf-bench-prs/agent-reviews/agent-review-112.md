# Review: PR #112 - ewma-portfolio-risk-decomposition
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Agent must debug a buggy template.py implementing EWMA covariance, parametric VaR, and Euler risk decomposition. The template has intentional bugs; the agent must identify and fix them.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `solution/solve.sh`, `environment/data/template.py`, `environment/data/params.json`
- Checked: bugs in template vs oracle, verifier recomputation logic, financial correctness

### Scorecard
- Task contract: 5/5 — clear description of what's wrong, hints at specific bug categories
- Verifier robustness: 5/5 — verifier recomputes expected values from data (not pinned constants!)
- Difficulty calibration: 3/5 — H:0.0, O:1.0, S:1.0; Haiku fails but both frontier models pass
- Financial correctness: 5/5 — oracle is textbook EWMA + Euler decomposition
- Benchmark integrity: 5/5 — verifier recomputes, no answer leakage

### Findings

#### [POSITIVE] Verifier recomputes expected values
File: `tests/test_outputs.py`
The `_compute_expected()` function recomputes the canonical answer from the raw data at test time. This is excellent — no pinned constants to leak, and the verifier is self-validating.

#### [POSITIVE] Well-designed bugs in template
File: `environment/data/template.py`
The template has at least 5 bugs:
1. Mean-centering returns before EWMA (wrong — EWMA uses raw returns)
2. `np.dot(R[t], R[t])` instead of `np.outer(R[t], R[t])` — scalar vs matrix
3. Hardcoded `z = 2.33` instead of `norm.ppf(conf_level)`
4. `marginal_risk = sigma_w * port_vol` instead of `sigma_w / port_vol`
5. Ignores `estimation_window_days` parameter from params.json

These test genuine debugging ability and quant finance knowledge.

#### [MINOR] Instruction hints are quite specific
The instruction says "pay attention to: how returns should be preprocessed, which numpy operation correctly computes the rank-1 update, how the z-score should be obtained..." — these are strong hints pointing at each bug. This may make it easier than intended.

### Summary
Excellent debugging-style benchmark. The recomputing verifier is best-in-class design. The bugs are realistic and require quant finance knowledge to identify. Good discrimination between Haiku (fails) and frontier models (pass).

### Verdict
**建议 Merge**

Outstanding verifier design and well-calibrated bugs. Ready for production.
