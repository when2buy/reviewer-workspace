---
name: qfbench-quant-correctness-analysis
description: Classify FAILED agent solutions on QF-Bench (Quantitative Finance Bench) tasks against a 9-mode quantitative-finance correctness taxonomy (Model & Formula, Convention & Units, Data & Numerics). Where the trajectory-error-analysis skill judges *how* an agent behaviorally failed (Execution / Coherence / Verification — process), this skill judges *what kind of financial mistake* the agent made in its math (formula / convention / data — content). Cross-references each trial's task_name to the original QF-Bench task folder (instruction.md, unit tests, oracle) for grounded judging. Use when reviewing failed QF-Bench agent solutions, when the user asks why an agent's numbers are wrong, when classifying quant-error patterns across many trials, or when looking for systematic mistakes (sign convention, unit scale, missing Jacobian, local-optimum trap, etc.) in a model's solution code.
---

# QF-Bench Quantitative Correctness Analysis

Classifies failed QF-Bench agent solutions against a 9-mode quantitative-finance correctness taxonomy. The taxonomy is empirically grounded in 75+ real PR reviews on the QF-Bench repository — every mode and sub-rubric is sourced from a documented failure pattern observed across Haiku 4.5 / Sonnet 4.6 / Opus 4.6 trial runs and human reviewer post-mortems.

This skill is the **content-correctness counterpart** to the trajectory-error-analysis skill:

| | `qfbench-trajectory-error-analysis` | `qfbench-quant-correctness-analysis` (this skill) |
|---|---|---|
| **Question** | *How* did the agent fail behaviorally? | *What kind* of financial mistake did the agent make? |
| **Axis** | Process (Execution / Coherence / Verification) | Content (Formula / Convention / Data-Numerics) |
| **Evidence** | Step-by-step trajectory + final claims | Generated code + output files + task spec |
| **Example match** | "Agent did step repetition without progress" | "Agent stored `var_explained` as 86.32 instead of 0.8632" |

Both skills are independent and complementary — a single failed trial can match modes from both.

## Scope: failed trials only

**This skill judges only failed trials.** Successful trials are silently skipped at discovery time and never reach the LLM judge. Pass/fail is determined from `result.json:verifier_result.rewards.reward` (1.0 = pass; ≤0 or missing = fail), independent of any directory layout. The 9 rubrics presuppose failure — applying them to a passing trial would produce meaningless labels.

For finance-zero single-shot solutions (one generated code blob, no multi-step interaction), every mode applies — the rubric judges the code-vs-spec gap.

## The 9 failure modes

**A. Model & Formula** — *what was computed* (the math itself is wrong)
- A1 — Wrong Model / Measure
- A2 — Missing or Extra Formula Term
- A3 — Wrong Parameterization / Convention Default

**B. Convention & Units** — *how it was expressed* (math is right, but on the wrong scale, sign, or clock)
- B1 — Unit / Scale Error
- B2 — Sign Convention Error
- B3 — Time / Date / Calendar Convention

**C. Data & Numerics** — *how it was fed in or solved* (math and conventions right, but inputs wrong or solver failed)
- C1 — Data Fabrication / Wrong Source
- C2 — Numerical / Optimization Failure
- C3 — Statistical Variant Mismatch

Full rubrics with framing, decision procedures, exclusions, and finance examples: [TAXONOMY.md](TAXONOMY.md).

## Independent judging + cascade rule

Every mode is independently judged ("yes / no for this mode given the agent's solution and the task spec"). A trial may match zero, one, or several modes.

**Cascade rule (strict — priority-enforced):** Many QF-Bench task failures show **one root computational error cascading into 5–10 test failures** (e.g., wrong WoE smoothing in PR #130 → wrong IV → wrong feature selection → wrong logistic regression → 8 metric failures). The skill enforces this via a **priority hierarchy** in the system_judge prompt: A1 > A2 > A3 > B1 > B2 > B3, with C2 subsumed by A1/A2/A3 (Step-0 prerequisite) and C3.c routing for under-specified specs. When the same root cause matches multiple modes, the highest-priority mode wins; subsumed modes return `match=false` with redirect notes. See [TAXONOMY.md](TAXONOMY.md) § "Cross-cutting: cascade rule" for the full priority table and worked examples.

**Empirical sub-rubrics added from the May 2026 50-trial validation:**
- **A1.d** — *Structural deviation:* implementation uses model name/notation but isn't the named model on 2+ structural axes (e.g., HW trinomial tree with constant probabilities, generic spacing, no Arrow-Debreu calibration)
- **A2.g** — *Wrong coefficient in canonical ODE / characteristic function* (e.g., Heston Riccati `d` with sign-flipped polynomial; HW log-bond variance `(σ²/(4a))·B²·(1−e^{−2at})` with wrong denominator)
- **A2.h** — *Silent approximation abuse* (escrowed-dividend for American options without lifting the projection step)
- **B1.e** — *Greeks unit-convention drift across estimators* (FD per-σ vs PW per-1% within one agent's own output)
- **C2.j** — *RNG-state contamination in FD Greeks under Monte Carlo* (bumped/base sims using disjoint random streams)

**Insufficient-solution pre-flight gate:** `judge_trial.py` deterministically short-circuits trials with empty/trivial agent code AND no output files AND no failing-test numerical comparisons — emits 9 `match=false` labels with `gate_skipped: true` at $0 cost. Calibrated on the 50-trial validation: gate fires on ~50% of stub-heavy samples with 0 false positives. Saves ~50% on production-sweep cost.

## Expected workspace layout

Same as `qfbench-trajectory-error-analysis` (this skill is a sibling, sharing infrastructure):

```
<root>/
├── <agent>_<model>/                       # e.g. claude-code_sonnet45, finance-zero_gpt5
│   └── <trial-name>/
│       ├── result.json                    # reward → pass/fail decision
│       ├── config.json
│       └── agent/
│           ├── trajectory.json            # for multi-step agents
│           └── <agent-name>.txt           # raw stream / generated code
```

Pass/fail is **always derived from `result.json:verifier_result.rewards.reward`**.

## How Claude reads this skill interactively

When the user points Claude at a failed trial folder (or asks "why did this agent fail?"):

1. **Locate the agent's solution.** Read whatever the agent generated:
   - `agent/<agent-name>.txt` for raw stream
   - The Python code emitted by the agent (often the entire content of `solve.sh`-equivalent)
   - The output files actually produced (`/app/output/*.json`, `*.csv`, etc.)

2. **Locate the task spec.** Read `tasks/<task-id>/instruction.md` and `tasks/<task-id>/tests/test_outputs.py` to know what was *required* vs what the agent *did*.

3. **Compute the failure ratio first** (see `OPS.md` § Debug Workflow). For each failing test, compare `agent_value / expected_value`. The ratio often pinpoints the mode before any rubric is read:
   - ~100 or ~0.01 → B1 (unit/scale)
   - ~−1 → B2 (sign convention)
   - hits parameter upper bound → C2 (numerical/optimization)
   - identical wrong value across all rows → A2 or A3 (uniform formula or parameterization error)
   - off by a *task-specific* magnitude (S₀, K, notional, …) → likely A2.b or C3.c, NOT B1 — see step 4

4. **Authorship pre-check** (mandatory before matching A1 / A2 / A3 on a formula error). For each formula in the agent's code that you suspect is wrong, ask: *who authored the expectation that this formula should be different?* See `TAXONOMY.md` § "Pre-check: who authored the formula?" — three cases:
   - **Case 1** (spec writes the formula or cites a specific paper): A1/A2/A3 apply normally.
   - **Case 2** (canonical, well-known model with unique form — BS, Merton, Hull-White, Heston, GARCH MLE, Reiner-Rubinstein, …): A1/A2/A3 apply normally; agent should know it.
     - Caveat: if the canonical method has multiple variants (NW87/94, Corrado, ES forms, …) → C3.a.
   - **Case 3** (spec only names a procedural goal; agent had to invent the formula; multiple defensible forms exist): prefer **C3.c**, NOT A1/A2/A3. Note task-side under-specification in `notes`.

5. **Walk through each of the 9 mode rubrics** in `TAXONOMY.md`. For each, follow its Decision Procedure to a yes/no verdict, citing evidence (line numbers, formula, output value).

5. **Output a labels report** in the format from `prompts/system_judge.md`. One JSON object per mode, with `match`, `evidence_step_ids`, `quote`, `confidence`, `notes`.

For batch/automated use over many trials, see option (b) in `OPS.md` (port the `qfbench-trajectory-error-analysis` scripts).

## Output contract

Each mode is judged with a strict JSON object:

```json
{
  "match": true,
  "evidence_step_ids": [37, 41],
  "quote": "z = X / sigma_t",
  "confidence": 0.92,
  "notes": "t-likelihood formula omits the scale factor sqrt((nu-2)/nu) in z definition AND drops the -log(scale) Jacobian term. Both mistakes go together — the scale is treated as 1. Cascades to nu pinned at the upper bound of 100. Mode A2 (missing transformation term)."
}
```

`evidence_step_ids` are line numbers into the agent's solution code (single-shot) or step IDs into a rendered trajectory (multi-step). Use `[0]` for single-shot if you can't pin to a specific line.

## What to flag (and what not to)

**Flag as a mode match:**
- The agent's code or output is wrong in a way the rubric explicitly captures
- The wrong-ness is materially affecting verifier results (not just style or formatting)
- The evidence is concrete: a specific line, a specific formula, a specific output value with the wrong sign/scale/term

**Do not flag:**
- Code style, naming, minor inefficiencies
- Trajectory-level behavioral failures (step repetition, premature termination, weak verification) — those belong in `qfbench-trajectory-error-analysis`
- Task-design problems (oracle bug, ambiguous instruction, broken Docker) — those belong in `qf-bench-review` (yesterday's task-review skill)
- Failures caused entirely by the task being broken when the agent did the financially correct thing — flag in `notes` but match=false; the agent didn't make a finance error

## Empirical grounding

The taxonomy was derived from systematic review of:

- 5 PRs in the PR#180-209 deep review (Haiku/Sonnet/Opus runs with `harbor`)
- 18 PRs in `HUMAN-REVIEW-SUMMARY.md` (independent re-test, 2026-04-26)
- ~25 substantive entries in `FINAL-SUMMARY.md`'s 备注 column
- 33 PRs PQCat commented on
- 107 open PRs across 5 pages of comments review
- Plus ~10 empirical findings already encoded in the `qf-bench-review` skill

Net: **~75 unique PRs** contributed substantive content to this taxonomy. Every sub-rubric in `TAXONOMY.md` cites the specific PR(s) where it was first observed.

## Validation status

**Cohen's κ = 0.89** on a 20-trial stratified sample (May 2026). 7 of 9 modes at perfect agreement; 2 modes at κ ≈ 0.7 (single isolated disagreements at known interpretive boundaries). All canonical formulas in the rubrics audited against authoritative sources (Glasserman 2004, Heston 1993, Brigo-Mercurio, Newey-West 1994, Acerbi-Tasche 2002, Engle 2002, MSCI USE4 Methodology Notes) and against QF-Bench reference solutions. **No known formula errors remaining in the rubrics.** See [CALIBRATION.md](CALIBRATION.md) for the full methodology, 7-round κ trajectory, and audit findings.

## Key files

- [TAXONOMY.md](TAXONOMY.md) — the 9 modes with full rubrics, sub-patterns (A1.a-d, A2.a-h, A3.a-d, B1.a-e, B2.a-e, B3.a-h, C1.a-f, C2.a-j, C3.a-d), finance examples, cascade priority table
- [examples.md](examples.md) — three worked examples (one per high-level class)
- [OPS.md](OPS.md) — operations runbook (Phase 1 interactive use, Phase 2 batch scripts, Phase 3 production lessons: LFS pull, Python 3.9 asyncio fix, Anthropic rate-limit tuning)
- [CALIBRATION.md](CALIBRATION.md) — validation methodology + κ result + formula audit log
- `prompts/system_judge.md` — the LLM judge system prompt with strict JSON output contract + cascade-rule priority hierarchy
- `prompts/<mode>.md` — one self-contained prompt per failure mode
- `scripts/` — `extract_solution.py`, `judge_trial.py` (with pre-flight gate), `judge_all.py` (async batch with budget cap), `aggregate_labels.py` (Cohen's κ vs human labels), `seed_calibration.py` (stratified hand-label sample)

## Companion skills

- [`qf-bench-review`](../qf-bench-review/SKILL.md) — reviews a *task* (instruction + solution + tests) for financial correctness. Use this when a contributor opens a PR and you need to vet whether the task itself is sound.
- [`qfbench-trajectory-error-analysis`](https://github.com/.../qfbench-trajectory-error-analysis) — classifies *behavioral* failure modes (Execution / Coherence / Verification). Use this when you need to understand the agent's process, not its math.

The three skills together cover the full review pipeline: vet the task → run agents → classify what the math got wrong → classify what the behavior got wrong.
