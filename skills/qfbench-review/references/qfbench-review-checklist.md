# QFBench Review Checklist

Work top-down. Benchmark integrity outranks code style.

## 1. Scope and review hygiene
- Is this PR cleanly scoped to one task or one coherent unit?
- Does the PR description match what is actually changed?
- Is data provenance documented in the PR description?
- Are difficulty claims supported by evidence?

## 2. Instruction quality and task contract
- Does `instruction.md` clearly say what outputs must be produced?
- Are exact output paths, formats, keys/columns, sort order, and precision specified?
- Does the instruction avoid prescribing the exact solution method unless that method is the point?
- Does the instruction avoid mentioning skills or skill file paths?
- Are there hidden canonical conventions that are enforced but not stated?

## 3. Specificity and coverage
- Do tests cover every behavior promised by the instruction?
- Do tests avoid checking behavior not stated in the instruction?
- Could an agent satisfy tests while violating the spirit of the task?
- Are there redundant checks that bloat the test count without adding signal?

## 4. Oracle and verifier robustness
- Does the oracle pass 100 percent?
- Is the oracle deterministic on reruns?
- Does `tests/test.sh` reliably write reward `1` on success and `0` on failure?
- Is there a brittle `set -euo pipefail` plus later `$?` pattern?
- Do tests recompute from inputs or mostly pin visible constants?
- Are numeric tolerances calibrated, not arbitrary?

## 5. Integrity and anti-cheat resistance
- Can the task be solved by hardcoding precomputed outputs?
- Do visible tests leak too much of the final answer?
- Do input file names, columns, or metadata embed answers?
- Are tests/solutions inaccessible to the agent at runtime under Harbor assumptions?
- Are canary strings present where required?
- Is there contamination risk because the verifier contains a full canonical solution?

## 6. Skill leakage
- If task skills exist, are they domain-general rather than task-specific?
- Do the skills mirror `solution/solve.*` too closely?
- Do the skills contain task file paths, exact column names, or expected values?
- If you swapped in another task from the same domain, would the skill still be useful?

## 7. Difficulty calibration and model discrimination
- Does the claimed difficulty match the run evidence?
- Does Finance-Zero fail for substantive reasons rather than trivial schema guessing?
- Do stronger frontier agents also face real difficulty, or do they all pass comfortably?
- Does the task separate reasoning ability, or mainly punish careless contract reading?

## 8. Data realism and determinism
- Is the dataset real, not synthetic or toy?
- Is it large and messy enough to justify the task?
- Are date ranges, prices, percentages, and units handled explicitly?
- Is output deterministic across reruns?

## 9. Code and implementation quality
- Is `environment/Dockerfile` based on the right image and are dependencies pinned?
- Are required skill copy paths present for supported agents?
- Are scripts readable and maintainable?
- Are there correctness bugs in formulas, units, indexing, or date handling?

## 10. Verdict rule of thumb
- Use `REQUEST CHANGES` for blockers in integrity, specification, verifier robustness, or major calibration problems.
- Use `NEEDS DISCUSSION` when the main issue is design direction rather than an obvious bug.
- Use `APPROVE` only when you would trust this task as a production-quality benchmark item.
