# code-review SKILL

**Trigger:** Activate when asked to review code, a PR, a diff, a commit, or specific files for bugs/quality/security.

**Description:** Review code changes, pull requests, and diffs for bugs, security issues, performance problems, financial logic errors, and style violations. Activate when asked to review code, PR, commit, or diff.

## Step-by-Step Review Process

### 1. Understand the Context
Before reading a single line of code:
- What is this change supposed to do? (read PR description, commit message, or ask)
- What part of the system does it touch? (state management? evaluation logic? API? infra?)
- What's the blast radius if it's wrong?

### 2. Load References
Read the following references in this skill directory:
- `references/review-checklist.md` — systematic things to check
- `references/finbench-standards.md` — project-specific rules
- `references/anti-patterns.md` — known bad patterns in this codebase

### 3. Review the Code
Work through the diff/code systematically:

**For each changed file:**
1. Understand what it does before looking at what changed
2. Read the diff — what was removed, what was added
3. Apply the checklist (severity-ordered: correctness → security → financial logic → state → perf → maintainability → style)
4. Note findings with severity labels

**Special attention triggers (always deep-read these):**
- Any file with "eval", "score", "benchmark", "metric" in name/path
- Any file touching money amounts, dates, or percentages
- Any async/concurrent code
- Any place where agent state is read or written
- Any external API calls (timeout? retry? error handling?)

### 4. Write the Review

Format:
```
## Review: [filename or PR title]
Reviewer: Grim 🔍 | Date: YYYY-MM-DD

### What This PR Does (Plain Language)
[2–4 sentences written for someone who doesn't know the domain.
Explain: what problem is being solved, what the code is supposed to do,
and why it matters. No jargon unless immediately explained.]

### What I Did to Review This
[Be specific: what files you read, what code you ran, what you calculated,
what sub-agents you used. This is the credibility section — readers should
be able to see your work and trust the findings.
Example: "I ran the oracle script against all 13 test cases and verified
the DD formula by hand for T=0.5."]

### Scorecard (for finbench task PRs)
[Use explicit dimensions, numeric scores, weights, weighted total, threshold,
and verdict color. Prefer a compact table when posting to GitHub or saving
local review docs.]

### Findings

**[CRITICAL] Short title**
File: `path/to/file.py`, line N
[Explanation of the problem and why it matters]
[Suggested fix or direction]

**[MAJOR] Short title**
...

**[MINOR] Short title**
...

**[NIT] Short title**
...

### Summary
[Concise recap. Lead with the blockers. End with the verdict.]
[For finbench task PRs, include a short priority/action table when it helps
make the re-review path obvious.]

### Verdict
APPROVE / REQUEST CHANGES / NEEDS DISCUSSION

[One sentence explaining the verdict]
```

#### Finbench task review style notes
For benchmark-task PRs, prefer the following additions when they improve clarity:
- Start with a plain-language task explanation plus a short "review focus" note explaining what could invalidate the benchmark.
- Use a weighted scorecard, not just loose bullets.
- Score dimensions that reflect benchmark quality, for example: structural completeness, data quality / ground truth, reasoning & domain knowledge, and evaluation criteria.
- In each low-scoring section, explain both the benchmark risk and the concrete fix.
- When a flaw is fundamental, say so directly, for example answer leakage, oracle exposure, contract mismatch, or invalid difficulty evidence.
- If the task is financially sensitive, call out hidden formula bugs that may be masked by the current test parameters.
- Prefer actionable fixes such as adding a non-unit horizon test, tightening tolerance, or replacing exposed constants with invariant checks.

### 5. Deliver

- If it's a GitHub PR: post as a review comment (if you have gh access)
- Otherwise: return the review as formatted text
- Always end with a clear verdict

## What NOT to Do
- Don't approve just because tests pass (tests can be wrong)
- Don't block on style when logic is correct
- Don't write vague comments ("this could be better") — be specific
- Don't write more than you need to. Dense and precise beats long and vague.
