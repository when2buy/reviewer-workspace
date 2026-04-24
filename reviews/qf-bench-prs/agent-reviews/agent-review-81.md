# Review: PR #81 - lmm-markov-representation
Reviewer: Grim 🔍 | Date: 2026-04-23

### What This PR Does
Agent must determine that the LMM is non-Markovian in general, then derive a finite-dimensional Markovian representation for a specific one-factor local-vol LMM using the Frobenius theorem from differential geometry, and verify symbolically with SymPy.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py, test.sh, solution/solve.py, Dockerfile
- Reviewed trial results: H45=0.0, Opus46=0.0, S45=0.0
- Analyzed test failure patterns

### Scorecard
- Task contract / instruction: 3/5
- Verifier robustness: 2/5
- Difficulty calibration: 2/5
- Benchmark integrity / anti-cheating: 2/5
- Financial correctness: 5/5

### Findings

#### [CRITICAL] Tests check for specific string patterns in free-text fields
Tests like `test_lmm_is_not_markovian` do keyword matching on `part1_answer` looking for "not markov" or "non-markov". `test_stratonovich_mentioned` checks if "stratonovich" appears in reasoning JSON. `test_drift_simplification_mentioned` checks for "cancel", "simplif", "= tau", etc.

This is extremely fragile. An agent could give a mathematically correct answer using different phrasing and fail. Or an agent could parrot keywords without understanding and pass.

#### [CRITICAL] Symbolic verification tests check exact SymPy output format
`test_bracket_u_component_is_zero` checks `bracket[0] in ["0", "0.0", ""]`. `test_V0_has_unit_u_component` checks `v0[0] in ["1", "1.0"]`. These depend on exact string representations of SymPy expressions, which are fragile and implementation-dependent.

#### [MAJOR] This is a math derivation task, not a quant computing task
The task is fundamentally about knowing the Frobenius theorem and applying it to the LMM. This is grad-level mathematical finance theory, not practical computation. The "benchmark" here is testing whether an LLM knows Henry-Labordère's textbook, not whether it can do quant work.

#### [MAJOR] All models fail — but failures may be on formatting, not understanding
H45 trial shows it correctly identifies Frobenius theorem, produces valid SymPy code, gets V0/V1 structure right, and computes Lie brackets. But it fails on `test_markov_dimension_is_2` and keyword-matching tests. The model may understand the math but format outputs differently than expected.

#### [MINOR] Dockerfile uses python:3.11-slim, not finance-bench-sandbox
This is fine since the task only needs SymPy, not financial data tools.

#### [MINOR] Solution is mathematically correct
The derivation following Henry-Labordère is correct: C(x)=1+τx causes drift decoupling, Frobenius theorem gives dimension 2 with states (t, z₁).

### Summary
Interesting mathematical finance task but poorly suited as a benchmark. The verifier relies on keyword matching in free-text fields and exact string formatting of symbolic expressions, making it brittle. The task tests textbook knowledge rather than practical quant skills. All three models fail, but the failures appear to be format/keyword issues rather than lack of mathematical understanding.

### Verdict
**不建议 Merge**

The verifier is too brittle for a reasoning/derivation task. Tests should verify mathematical correctness (e.g., check that exp(Q) ≈ P for the stated generator), not keyword presence in prose. Redesign verification approach or accept that this type of task is poorly suited for automated benchmarking.
