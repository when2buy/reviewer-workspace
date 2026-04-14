# QFBench Review Template

Use this structure and keep it concrete.

## Review: PR #<number> - <title>
Reviewer: Grim 🔍 | Date: YYYY-MM-DD

### What This PR Does
Explain the task in plain language for a reader who may not know the domain.
State what the agent is supposed to do, what artifact it must produce, and why this is a meaningful benchmark behavior.

### What I Did to Review This
List the actual work performed. Be specific.
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `solution/solve.*`, `environment/Dockerfile`, relevant skills
- Ran: commands, oracle runs, verifier runs, spot checks
- Checked: formulas, hidden assumptions, leakage, reward logic, task scope

### Scorecard
Score the dimensions that matter for the PR. Example dimensions:
- Task contract / instruction
- Verifier robustness
- Difficulty calibration
- Model discrimination
- Benchmark integrity / anti-cheating
- Data realism / determinism
- Review hygiene / PR cleanliness

Use a simple 1 to 5 scale when useful. Skip scores if they do not help.

### Findings

#### [CRITICAL] <short title>
File: `<path>`
Explain the issue, why it matters for QFBench, and what should change.

#### [MAJOR] <short title>
File: `<path>`
Explain the issue, why it matters, and the likely fix direction.

#### [MINOR] <short title>
File: `<path>`
Explain briefly.

#### [NIT] <short title>
File: `<path>`
Optional polish only.

### Summary
Lead with the blockers. Say what is good only if it is materially true.

### Verdict
APPROVE / REQUEST CHANGES / NEEDS DISCUSSION

One sentence explaining the verdict.

## Notes
- Prefer benchmark-level findings over generic style comments.
- If you executed code, say so.
- If the PR evidence is weak, say the evidence is weak.
- If visible tests expose too much oracle logic, say that directly.
- If the PR is mislabeled as hard, say so directly.
