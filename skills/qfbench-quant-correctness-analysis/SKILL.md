---
name: qfbench-quant-correctness-analysis
description: Classify FAILED agent solutions on QF-Bench (Quantitative Finance Bench) tasks against a 10-mode taxonomy — 9 quant-correctness modes (Model & Formula, Convention & Units, Data & Numerics) plus a 10th non-quant mode (Spec & Output Compliance) for schema/format failures on data-engineering tasks. Where the trajectory-error-analysis skill judges *how* an agent behaviorally failed (Execution / Coherence / Verification — process), this skill judges *what kind of financial or output-schema mistake* the agent made in its math or its output format. Cross-references each trial's task_name to the original QF-Bench task folder (instruction.md, unit tests, oracle) for grounded judging. Use when reviewing failed QF-Bench agent solutions, when the user asks why an agent's numbers are wrong, when classifying quant-error patterns across many trials, or when looking for systematic mistakes (sign convention, unit scale, missing Jacobian, local-optimum trap, schema vocabulary mismatch, etc.) in a model's solution code.
---

# QF-Bench Quantitative Correctness Analysis

Classifies failed QF-Bench agent solutions against a **10-mode taxonomy** (9 quant + 1 non-quant). The taxonomy is empirically grounded in 75+ real PR reviews on the QF-Bench repository plus the v10 batch analysis (May 2026) — every mode and sub-rubric is sourced from a documented failure pattern observed across Haiku 4.5 / Sonnet 4.6 / Opus 4.6 trial runs and human reviewer post-mortems.

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

## The 10 failure modes (9 quant + 1 non-quant)

**A. Model & Formula** *(quant)* — *what was computed* (the math itself is wrong)
- A1 — Wrong Model / Measure
- A2 — Missing or Extra Formula Term
- A3 — Wrong Parameterization / Convention Default

**B. Convention & Units** *(quant)* — *how it was expressed* (math is right, but on the wrong scale, sign, or clock)
- B1 — Unit / Scale Error
- B2 — Sign Convention Error
- B3 — Time / Date / Calendar Convention

**C. Data & Numerics** *(quant)* — *how it was fed in or solved* (math and conventions right, but inputs wrong or solver failed)
- C1 — Data Fabrication / Wrong Source
- C2 — Numerical / Optimization Failure
- C3 — Statistical Variant Mismatch

**D. Spec & Output Compliance** *(non-quant — orthogonal axis)* — *did the output match the schema?* (quant content right, output format wrong)
- D1 — Output Schema & Spec Compliance (sub-rubrics: D1.a vocabulary, D1.b shape, D1.c column order, D1.d type serialization, D1.e JSON precision, D1.f date-format, **D1.g library/API default-induced numerical drift**)

Class D fires **independently of A/B/C** — a trial can match D1 *and* any A/B/C mode simultaneously (orthogonal axes). The cascade rule operates *within* an axis, not across them. **Special case for D1.g:** when an engineering-layer bug (library API default, not the agent's QF reasoning) produces wrong numerical values, D1.g matches as primary AND subsumes the parallel A3 / A2 / B1 match. This is the only place where D subsumes a quant-axis mode — see TAXONOMY § "D1.g special case".

Full rubrics with framing, decision procedures, exclusions, and finance examples: [TAXONOMY.md](TAXONOMY.md).

## Independent judging + cascade rule

Every mode is independently judged ("yes / no for this mode given the agent's solution and the task spec"). A trial may match zero, one, or several modes.

**Cascade rule (strict — priority-enforced):** Many QF-Bench task failures show **one root computational error cascading into 5–10 test failures** (e.g., wrong WoE smoothing in PR #130 → wrong IV → wrong feature selection → wrong logistic regression → 8 metric failures). The skill enforces this via a **priority hierarchy** in the system_judge prompt: A1 > A2 > A3 > B1 > B2 > B3, with C2 subsumed by A1/A2/A3 (Step-0 prerequisite) and C3.c routing for under-specified specs. When the same root cause matches multiple modes, the highest-priority mode wins; subsumed modes return `match=false` with redirect notes. See [TAXONOMY.md](TAXONOMY.md) § "Cross-cutting: cascade rule" for the full priority table and worked examples.

**v3.2 update (May 2026)** — added the **Spec-Citation Extraction Pre-check** to `prompts/system_judge.md`. After scanning all 85 V11-focus task instructions, the audit found that QF-Bench specs use eight distinct citation forms (author cites, textbook section refs, cross-file refs, inline TeX, library kwargs, pinned numerical params, day-count pins, pseudocode-fence formulas) and the original Authorship pre-check missed several of them — leading to ~31 cells being mis-flagged as A3.f when they should have been A2 (failure to follow an explicit pin). The new pre-check enumerates all eight forms with regex sketches and concrete task examples (`references/spec_citation_patterns.md`), and reclassifies tasks into three regimes: spec-authored (56 of 85), spec-delegates (23), silent (6). The scanner script is in `scripts/scan_citations_v2.py`.

**v3.2.1 (May 2026)** — extended `INDUSTRY_STANDARDS.md` with seven new web-verified industry-standard rules, each backed by a primary literature citation (live URLs to vendor methodology PDFs, peer-reviewed journals, or Wikipedia/CFA-curriculum sources for established convention claims). Additions: §A.9 (variance-drain `CAGR ≈ AR − ½σ²`), §D.9 (SVI/SSVI vs Fengler arbitrage-free spline for IV surface), §F.5 (Almgren-Chriss linear impact + empirical √-law for execution cost), §F.10 (winsorize-then-z-score order; MSCI/AQR/Barra), and §I (Backtest discipline: I.1 PIT signal alignment / I.2 fundamental release-date timestamping / I.3 universe survivorship). Citations were verified via direct WebFetch where possible; two false positives caught in pre-edit review (Petersen 2009 → "lag=6 for FM" — actually practitioner folklore not Petersen; Almgren et al. 2005 → √-impact — actually rejects √ in favor of 3/5 power) were corrected before any rule was added.

**v3.2.4 (May 5 2026)** — substantially expanded `INDUSTRY_STANDARDS.md` § D.4 (Kirk vs Margrabe spread option) from a 5-line summary into a full reference entry with paper-verified Kirk-vs-MC error tables (Harutyunyan & Masip Borrás 2018, arXiv:1812.04272 — explicit max errors of <1% at ρ ≤ 0.90, up to ~7% at ρ=0.95, exponential growth with T/ρ/K), plus a worked numerical example (Kirk = 0.5616 vs MC CI (0.5399, 0.5428) at ρ=0.80, K=5, T=0.5, page 26). Added a decision procedure for judging Kirk-vs-MC test failures: ATM/short-T/low-ρ failures = real bug; deep-ITM/deep-OTM/long-T/high-ρ failures = `task_side` (Kirk's intrinsic bias > test tolerance). Empirically validated by the v323 sweep: 5 of 5 trials of `spread-option-kirk-margrabe` across 5 distinct model families failed `test_kirk_mc_agreement` deterministically at the same single grid point (T=1.0, K=−0.10·avg_spot, deepest-ITM) with 3-5% Kirk-vs-MC gap. Companion reference doc at `references/spread_option_approximations.md`.

**v3.2.5 (May 5 2026)** — added the **hidden-quality-threshold decision rule** to `TAXONOMY.md`. Distinguishes intentionally-hard tasks (where the spec withholds the numerical threshold to force production-quality code) from genuinely brittle pins (where the test tolerance is tighter than the formula's intrinsic error). Diagnostic: oracle / threshold ratio ≤ 0.5 → hidden quality gate (agent failures = `agent_coding`); 0.5-0.95 → borderline (check formula bias); > 1 → genuine task-side breakage. Companion to v3.2.4 — together they discriminate "fix the test" vs "this catches real bugs."

**v3.2.6 (May 5 2026)** — added the **trajectory-failure sub-classification** to `TAXONOMY.md`. The previously-monolithic `insufficient` root_cause class is now split into three distinct sub-types with separate aggregator treatment: (Pattern A) `agent_engineering_weakness` → reclass to `agent_coding`, counts as legitimate agent failure (wall-time / context-budget overrun on intentionally-hard tasks); (Pattern B) `agent_ux_bug` → new root_cause class, count toward agent score with caveat (Plan-mode trap is a Claude Code harness UX issue, not a quant capability gap); (Pattern C) `infra_failure` → new root_cause class, **exclude from quality scores** (provider 429, container path mismatch, network errors). Empirically validated: 11 of 22 v323 insufficient-class trials reclassified across the three patterns. Aggregate reports now produce three distinct metrics: agent quality score (excluding infra), `agent_ux_bug_rate`, and `infra_failure_rate`.

**v3.2.7 (May 5 2026)** — fixed a rule-vs-example inconsistency in `TAXONOMY.md` § "D1.g routing" (cross-sectional-momentum POSITIVE example). The v3.2.1 inline pre-labeling "(or task_side... as it does here for cross-sectional-momentum)" contradicted the v3.2.5 hidden-quality-threshold rule and v3.2.6 Pattern A rationale. Updated to: D1.g defaults to `agent_coding`; reserve `task_side` ONLY for cases where the spec explicitly writes the buggy library call verbatim with the wrong kwarg specified. Specs that are merely silent on a kwarg (the common case) test engineering judgment → `agent_coding`. Reclassified 9 cross-sectional-momentum trials in v323 corpus (8 → agent_coding D1.g; 1 → infra_failure Pattern C). Added a **mandatory rule-consistency self-check procedure** to `OPS.md` for future rule additions: when adding any new general rule that affects routing, audit existing worked examples for contradictions before publishing the rule, and document the audit in CHANGELOG.

**v3.2.8 (May 5 2026)** — retroactive application of the v3.2.7 self-check rule. Found 3 additional inconsistencies that pre-dated v3.2.5/v3.2.6/v3.2.7 and contradicted the newer general rules: (1) `TAXONOMY.md` L683 D1 Authorship sub-question — generic D1 routing didn't mention the v3.2.2-pat9 vocab-substitution carve-out or the v3.2.7 D1.g engineering-kwarg carve-out; updated to enumerate both. (2) `TAXONOMY.md` L696 D1.e JSON precision routing — said *"Mostly task-side — the test tolerance is unreasonably tight for JSON round-tripping"*, contradicting v3.2.5 hidden-quality-threshold (standard `json.dumps` preserves ~17 sig digits, well under any 1e-12 threshold; oracle achieves the threshold trivially); updated to default `agent_coding`, reserve `task_side` only when the spec mandates intermediate rounding and a downstream test pins values computed without rounding. (3) `TAXONOMY.md` L715 13f-amendment-aware-crowding example — note that this v3.2.8 framing was **superseded by v3.2.9** below.

**v3.2.9 (May 6 2026)** — added a new cross-cutting routing rule: `root_cause_class = infra_failure`, `infra_subrubric = stale_spec_checkout`. Fires when the harness operator's `tasks/` checkout is older than `origin/main` at trial-launch time AND the agent receives a pre-edit instruction while the verifier evaluates against post-edit expectations. **Mandatory diagnostic before classifying any uniform-failure (κ ≥ 0.9) D1.a/D1.b/D1.c case as `agent_conceptual`:** read trajectory.json step-2; get date-anchored `git show <commit>:tasks/<task>/instruction.md` where `<commit>` is the latest `origin/main` commit before trial timestamp; check whether distinctive content (binding clauses, controlled-vocabulary enumerations) appears in trial msg. If absent → `infra_failure / stale_spec_checkout`. **Why this isn't `task_side`:** the maintainer's `origin/main` spec is correct; the bug is in the harness pipeline, not in task design. Calling stale-checkout failures `task_side` would mislead the maintainer into editing a working spec — the actionable owner is the harness operator. **Empirical scope (v323 audit, 2026-05-06):** systemic deep-read pass found this pattern in `13f-amendment-aware-crowding` (21 trials), `dupire-local-vol` (21 trials), `compound-option-geske` (4 trials), and several individual trials of `fx-carry-forward-hedge`, `yield-curve-bond-immunization`, `credit-migration-matrix` — total 50 v323 trials reclassified `agent_conceptual / D1.*` → `infra_failure / D1.* / stale_spec_checkout`. **Lesson:** a κ=1.0 universal-failure signature can be either (a) genuine LLM-prior attractor (when agent received the spec) or (b) stale-spec infra issue (when agent received an older spec). Distinguishable only by reading `trajectory.json` step-2 — never classify uniform-failure D1.* as agent capability without that verification. `TAXONOMY.md` § "Cross-cutting: infra_failure / stale_spec_checkout" + `prompts/system_judge.md` `root_cause_class` enumeration updated; corrected the v3.2.8 13f example.

**v3.2.10 (May 6 2026, same-day expansion of v3.2.9)** — closed three methodology gaps in the v3.2.9 rule that under-counted stale_spec cases by 90 trials: (1) **Sub-pattern 2: pre-merge PR-branch served before maintainer revised it** — generalized stale_spec_checkout to fire on ANY divergence between trajectory and origin/main spec, regardless of literal date ordering (the v3.2.9 "spec edit predates trial" check was necessary but not sufficient); the squash-merge commit on origin/main can post-date the trial yet still represent the canonical spec the verifier's tests assume. (2) **Mandatory test-name verification step** — extract failing test names from `verifier/test-stdout.txt`, compare against `git show origin/main:tasks/<task>/tests/test_outputs.py`. Match ratio is the discriminator: 100% on origin/main → real `infra_failure`; 0% → "consistently stale" (verifier and instruction were aligned at older version) → leave original A/B/C/D classification; mixed → flip on majority. Without this check, audits over-flip "consistently stale" cases (3 mtm-xccy v323 trials would have been wrongly flipped). (3) **Cross-batch consistency rule for parallel sub-agent audits** — sister trials of the same task split across batches must get identical classification on identical evidence; the audit aggregator MUST run a final consistency pass and flag inconsistent classifications for re-judge. Empirically v3.2.10 found stale_spec_checkout in 8 task families (91 v323 trials) — 4× the v3.2.9 estimate of 1 task. The v3.2.10 rule and supporting `OPS.md` § "Parallel sub-agent audit pipeline rules" prevent the four bugs that v3.2.9 release exposed: leaner-prompt sub-agents missing flips, literal-date-only checks missing PR-branch sub-pattern, no test-name verification, and no cross-batch consistency check.

**v3.2.11 (May 6 2026, sub-rule for math-equivalence-shortcuts)** — added a new sub-rule to disambiguate `A3.f` vs `C3.c` when the agent takes a mathematically-equivalent shortcut. The rule: when a spec procedure has multiple math-equivalent implementations that consume RNG state or take different code paths, the agent must follow the LITERAL reading. Math shortcuts (e.g., `z * scales` instead of separate per-component draws; `np.where` vs `np.select`; analytic identity vs MC sampling) classify as **A3.f / agent_conceptual** when EITHER (i) the test pins specific numeric values rather than shape invariants, or (ii) the spec uses literal verbs like "draw from / sample from / select" with explicit subjects. Pinned-numeric tests are a strong signal that the maintainer ran a canonical implementation and pinned ITS output — the spec is NOT genuinely under-specified, the maintainer had ONE recipe in mind. Discovered when an Opus 4.7 sub-agent classified `var-es-estimation` Opus R3 trial as `C3.c / task_side` because spec L22 *"draw from the selected component accordingly"* doesn't explicitly pin the RNG-call sequence; manual review caught that the pinned RMSE test (`assert isclose(0.1036, rtol=0.10)`) and the literal verb "draw from" both indicate `A3.f`. Encoded in TAXONOMY.md § "Sub-rule: Mathematical equivalence ≠ literal compliance" + system_judge.md mandatory callout in Authorship Case 3.

**v3.2.12 (May 6 2026, MANDATORY task_side self-check / doubt mechanism)** — added a 6-question doubt mechanism that fires automatically before any `task_side` classification is finalized. v3.2.11's sub-rule was passive — sub-agents could still skip it under literal "spec doesn't pin → C3.c." v3.2.12 makes the discriminators an active checklist with output JSON enforcement. **The 6 questions:** Q1 failing tests are shape invariants (vs pinned numeric)?; Q2 no industry standard exists?; Q3 spec doesn't cite paper/textbook/library?; Q4 agent did NOT take a math-equivalence shortcut?; Q5 spec doesn't use literal verbs?; Q6 sister trials consistent?. **Decision rule:** task_side stands ONLY if ALL 6 answer "task_side plausible" (no DOWNGRADE). If ANY question downgrades, reclassify away from task_side. **Required output:** any `task_side` label MUST include a `task_side_self_check` JSON field with all 6 answers + `passed: true/false`. The audit aggregator REJECTS task_side labels lacking this field. The mechanism enforces the v3.2.x → v3.2.11 discriminators (test-type signal, industry-standard, citation, math shortcut, literal verb, sister consistency) in a single mandatory checklist with output schema enforcement. Encoded in TAXONOMY.md § "Cross-cutting: MANDATORY task_side self-check" + system_judge.md mandatory callout. Lesson: `task_side` is the audit's claim against the maintainer's spec — the bar should be high, and the doubt checklist enforces that bar by forcing the sub-agent to walk through each discriminator with evidence.

**v3.2.13 (May 6 2026, gatekeeper Q0 added to task_side self-check)** — added a gatekeeper Q0 at the FRONT of the v3.2.12 task_side self-check that forces a deep re-examination using the full skill BEFORE Q1–Q6 are answered. **Q0 specification:** "Are you sure this is task_side? Re-examine deeply using the full skill before continuing." The sub-agent MUST: (1) re-read the spec end-to-end on origin/main; (2) re-read the failing test assertion verbatim; (3) re-read the agent's actual code verbatim; (4) cross-check against the skill's discriminator sections (Pre-check 3 cases, Industry-Standard pre-check, Math-equivalence sub-rule, hidden-quality-threshold); (5) cross-check against canonical TAXONOMY POSITIVE/NEGATIVE examples; (6) write the task_side claim in concrete terms (specific spec line + specific defect + why no other mode fits). Output schema requires a `q0_deep_recheck` sub-block including spec-full-reread, test-assertion-verbatim, agent-code-verbatim, discriminator-checks, task-side-claim-in-concrete-terms, and confidence-after-deep-recheck. **Decision rule:** if `confidence_after_deep_recheck < 0.7` after deep re-examination, STOP and reclassify without proceeding to Q1–Q6 — the sub-agent's own uncertainty is itself a signal task_side is wrong. If ≥ 0.7, proceed to Q1–Q6. **Why Q0 specifically:** Q1–Q6 catch specific signal types but trigger AFTER the sub-agent has provisionally committed to task_side; without Q0, the sub-agent might rationalize discriminator answers to support its initial guess. Q0 forces a "blank slate" deep re-examination FIRST, breaking confirmation bias before it kicks in. Encoded in TAXONOMY.md § "Cross-cutting: MANDATORY task_side self-check" (expanded) + system_judge.md (Q0 added to mandatory callout). Aggregator REJECTS labels lacking the q0_deep_recheck sub-block, OR with the contradiction `passed: true` while `confidence_after_deep_recheck < 0.7`.

**v3.2.15 (May 6 2026, Q0 confidence threshold raised 0.7 → 0.8)** — stricter conservative-discipline tuning of the Q0 deep-recheck threshold introduced in v3.2.13. After the v3.2.14 v323 corpus rejudge (558 trials), the empirical Q0 confidence distribution showed a bimodal cluster: most genuine task_side claims had Q0 ≥ 0.85, while borderline cases sat at 0.70–0.78. The 0.7 threshold was admitting borderline cases that, on closer inspection, were plausibly defensible as agent_conceptual under industry-standard or canonical-method readings. v3.2.15 raises the Q0 pass threshold to 0.8, matching the empirical signal floor between "borderline plausible" (which we want to downgrade) and "high-confidence task_side" (which we want to keep). Aggregator validation rule updated accordingly: any `task_side` label with `q0_deep_recheck.confidence_after_deep_recheck < 0.8` is auto-rejected. Empirical impact on v3.2.14 final state (n=558, 13 task_side): 12 × `credit-portfolio-var-cvar` at Q0 ≥ 0.85 unchanged; 1 × `fb-v11-opus46-r3-yield-curve-bond-immunization` at Q0=0.72 flips to A3.b agent_conceptual. Net task_side share: 13 → 12 (2.3% → 2.2%). Files updated: `TAXONOMY.md`, `prompts/system_judge.md`. Historical CHANGELOG entries (v3.2.13/v3.2.14) retain their original 0.7 references — those describe the threshold *as it stood at those versions*.

**v3.2.14 (May 6 2026, UNCONDITIONAL trigger rule for task_side self-check)** — strengthened the v3.2.13 self-check trigger from "MUST run before finalizing" (write-time) to "ALWAYS triggers on intent to assign task_side" (reasoning-time). v3.2.13's wording left a loophole: a sub-agent could write the JSON output with `root_cause_class: task_side` without ever running the self-check (no `task_side_self_check` field at all); the aggregator catches the missing field but the sub-agent's *reasoning* would still have committed to task_side without the discriminator check. v3.2.14 closes the loophole with a non-negotiable trigger rule placed at the TOP of the Output contract (`prompts/system_judge.md`): **"If at ANY point in your reasoning you find yourself about to assign root_cause_class = task_side, you MUST FIRST run the full Q0–Q6 self-check."** Trigger fires unconditionally — regardless of confidence, corpus, sister-trial classifications, memory-note suggestions, or whether it's a confirmation re-judge of an existing task_side label. **No exceptions, no shortcuts.** The schema is split into two: non-task_side (simple 6-field) and task_side (REQUIRES the v3.2.13 self-check block with Q0+Q1–Q6+evidence). Added a verification step before submitting JSON: the sub-agent must check its response for `"root_cause_class": "task_side"` AND confirm `task_side_self_check.passed: true` is also present. Aggregator validation made explicit: any task_side label with `q0_deep_recheck.confidence_after_deep_recheck < 0.7` OR `task_side_self_check.passed != true` is auto-rejected and the trial is flagged for re-judge. Also added `infra_failure` and `agent_ux_bug` to the schema enumeration (they were missing from v3.2.13 schema). The combination — Q0 gatekeeper + Q1–Q6 discriminators + unconditional intent-based trigger + schema validation — makes task_side a deliberately-evidenced classification, not a default fallback.

**Empirical sub-rubrics added from the May 2026 50-trial validation:**
- **A1.d** — *Structural deviation:* implementation uses model name/notation but isn't the named model on 2+ structural axes (e.g., HW trinomial tree with constant probabilities, generic spacing, no Arrow-Debreu calibration)
- **A2.g** — *Wrong coefficient in canonical ODE / characteristic function* (e.g., Heston Riccati `d` with sign-flipped polynomial; HW log-bond variance `(σ²/(4a))·B²·(1−e^{−2at})` with wrong denominator)
- **A2.h** — *Silent approximation abuse* (escrowed-dividend for American options without lifting the projection step)
- **B1.e** — *Greeks unit-convention drift across estimators* (FD per-σ vs PW per-1% within one agent's own output)
- **C2.j** — *RNG-state contamination in FD Greeks under Monte Carlo* (bumped/base sims using disjoint random streams)

**Class D added from the v10 batch analysis (May 2026)** — when 5 sub-agents on the same data-engineering trial picked 3 different mode classifications for the same root cause, it surfaced that the 9-mode taxonomy was forcing schema/format failures into A3 or C3.c at high inter-judge variance. Class D resolves this:
- **D1** — *Output Schema & Spec Compliance* — quant content right, output format/vocabulary/shape wrong
  - **D1.a** — Vocabulary/label mismatch (agent invents `'RESET'` vs spec-pinned `'replace_initial'`)
  - **D1.b** — Shape mismatch (string vs list, scalar vs array; e.g., `"A-B"` vs `["A", "B"]`)
  - **D1.c** — Column ordering / missing columns in tabular output
  - **D1.d** — Type serialization (str vs int, bool vs `Y/N`/blank, identity-column drift)
  - **D1.e** — JSON float-precision / serialization rounding (often `task_side`)
  - **D1.f** — Date / timestamp serialization format (`'2025-12-31 00:00:00'` vs `'2025-12-31'`)
  - **D1.g** — *Library/API default-induced numerical drift (engineering bug, not QF bug).* Added 2026-05-04 from `cross-sectional-momentum` deep-dive. Agent's QF reasoning is correct (right model, right formula, right convention pick) but a library API default (e.g., `pandas.sort_values` non-stable + `drop_duplicates(keep='last')`, `np.argsort` tie-break, JSON float round-trip) silently corrupts the numerical output. Diagnostic: bug fixable with one keyword-argument change (`kind='stable'`, `dtype=float`, `errors='raise'`, etc.) — no formula or convention change needed. Distinguishes engineering bugs from QF-knowledge gaps. Empirically validated: temp-fix to spec lifted Haiku 0/3 → 1/1 on `cross-sectional-momentum`. **D1.g uniquely subsumes A3 / A2 / B1 on the same root cause** (the only place D subsumes a quant-axis mode), preventing engineering bugs from being mis-attributed as finance-knowledge gaps in capability assessments.

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
