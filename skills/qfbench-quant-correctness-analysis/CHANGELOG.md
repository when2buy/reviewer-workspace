# Changelog

This file tracks every iteration of the `qfbench-quant-correctness-analysis` skill, recording **what was enhanced** and **why** at each version. Newest first.

---

## v3.2.15 (May 6 2026 — Q0 confidence threshold raised 0.7 → 0.8)

**Type:** stricter conservative-discipline tuning of the v3.2.13/v3.2.14 task_side self-check.

**What changed:**
- Q0 deep-recheck pass threshold: `confidence_after_deep_recheck >= 0.7` → **`>= 0.8`**
- Aggregator validation rule updated to match: any `task_side` label with `q0_deep_recheck.confidence_after_deep_recheck < 0.8` is auto-rejected and reclassified.

**Why this update:**

After the v3.2.14 v323 corpus rejudge (558 trials across 60 tasks), the empirical Q0 confidence distribution showed a bimodal cluster: most genuine task_side claims had Q0 ≥ 0.85, while borderline cases sat at 0.70–0.78. The 0.7 threshold was admitting borderline cases that, on closer inspection, were plausibly defensible as agent_conceptual under industry-standard or canonical-method readings.

Empirical impact on the v3.2.14 final-state corpus (n=558, 13 task_side trials):
- 12 × `credit-portfolio-var-cvar` trials at Q0 ≥ 0.85 — **unchanged** (still pass 0.8)
- 1 × `fb-v11-opus46-r3-yield-curve-bond-immunization` at Q0 = 0.72 — **flips to A3.b agent_conceptual** under 0.8

Net: task_side share drops 13 → 12 (2.3% → 2.2% of n=558). The stricter threshold reflects the user's preference for treating task_side as a high-bar last-resort classification rather than a "borderline plausible" default.

**Files updated:**
- `TAXONOMY.md` — Q0 threshold mentions updated 0.7 → 0.8 throughout § "Cross-cutting: MANDATORY task_side self-check"
- `prompts/system_judge.md` — Q0 threshold + aggregator validation rule updated 0.7 → 0.8
- `SKILL.md` — version log entry added

**Historical CHANGELOG entries (v3.2.13, v3.2.14) retain their original 0.7 references** — those describe the threshold *as it stood at those versions*. v3.2.15 is the first version where the threshold is 0.8.

---

## v3.2.14 (May 6 2026 — UNCONDITIONAL trigger rule for task_side self-check)

**Type:** strengthened the v3.2.13 self-check from "MUST run before finalizing" to "ALWAYS triggers on intent to assign task_side, with hard schema validation."

**Why this update:**

v3.2.12 + v3.2.13 added the doubt mechanism (Q0 gatekeeper + Q1–Q6 discriminators). But "MUST run before finalizing" wording leaves a loophole: a sub-agent could write the JSON output with `root_cause_class: "task_side"` and skip the self-check entirely (no `task_side_self_check` field at all). The aggregator would catch the missing field, but the sub-agent's *reasoning* would still have committed to task_side without ever running the discriminators.

v3.2.14 closes the loophole by making the trigger **unconditional and intent-based**:

> **If at ANY point in your reasoning you find yourself about to assign `root_cause_class = "task_side"`, you MUST FIRST run the full Q0–Q6 self-check.** This trigger fires unconditionally, regardless of confidence, regardless of corpus, regardless of sister-trial classifications, regardless of memory-note suggestions, regardless of whether it's a confirmation re-judge of an existing task_side label.

**No exceptions. No shortcuts.**

**Implementation across files:**

1. **prompts/system_judge.md** — added a new "MANDATORY trigger rule for task_side" section at the TOP of the Output contract, before the schema. Six bullet points enumerate non-exception cases (regardless of confidence, corpus, sister trials, certainty, memory, re-judge). Added a "Verification step before submitting your JSON" instruction: the sub-agent must check its own response for `"root_cause_class": "task_side"` and confirm `task_side_self_check.passed: true` is also present.

2. **Schema split** — the JSON schema in system_judge.md is now explicitly split into two:
   - **Non-task_side schema:** simple 6-field structure (no self-check required)
   - **Task_side schema (REQUIRED v3.2.13 self-check block):** full structure with `task_side_self_check.q0_deep_recheck` (all 6 sub-fields populated) + Q1–Q6 + `task_side_evidence` block

3. **Aggregator validation rule (made explicit):** task_side labels MUST have `task_side_self_check.q0_deep_recheck.confidence_after_deep_recheck ≥ 0.7` AND `task_side_self_check.passed == true`. Any violation → auto-rejected, label discarded, trial flagged for re-judge with explicit instruction.

4. **infra_failure listed in non-task_side schema** — was missing from the v3.2.13 schema enumeration. v3.2.14 makes it explicit.

5. **agent_ux_bug listed in non-task_side schema** — was missing. v3.2.14 makes it explicit.

**Why "intent-based trigger" specifically:**

v3.2.13's trigger fired "before finalizing" — i.e., at the moment of writing the output JSON. By that point the sub-agent has already done the reasoning, often committed to a tentative task_side answer, and may rationalize the discriminator answers to support its commitment. v3.2.14 fires earlier: at the moment the sub-agent's *reasoning* starts pointing toward task_side. The sub-agent must drop everything and run Q0 first. This breaks confirmation bias before it gets a foothold.

**Verification step (added v3.2.14):**

Before the sub-agent submits its JSON response, it MUST verify:
1. Does the response contain `"root_cause_class": "task_side"`?
2. If yes, does it ALSO contain the complete `task_side_self_check` block with `q0_deep_recheck` populated and `passed: true`?

If question 1 is yes and question 2 is no (or "I haven't checked"), the response is invalid — the sub-agent must go back, run the self-check, and rewrite.

**Files updated:**

- `prompts/system_judge.md` — added the MANDATORY trigger rule section at the top of Output contract; split the schema into non-task_side vs task_side; added the verification step
- `SKILL.md` — version log updated to v3.2.14
- `CHANGELOG.md` — this entry

**Lesson encoded for future audits:**

A self-check rule is only as strong as its trigger. v3.2.13 made the self-check exist; v3.2.14 makes it impossible to write task_side without running the self-check. The combination — Q0 gatekeeper + Q1–Q6 discriminators + unconditional trigger + schema validation — is what makes task_side a deliberately-evidenced classification rather than a default fallback.

---

## v3.2.13 (May 6 2026 — gatekeeper Q0 added to task_side self-check)

**Type:** added a gatekeeper question Q0 at the front of the v3.2.12 task_side self-check.

**Why this update:**

The v3.2.12 doubt checklist was 6 specific discriminator questions (Q1–Q6). Each Q1–Q6 catches a specific signal (test type, industry standard, citation, math shortcut, literal verb, sister consistency). But the v3.2.12 design didn't force the sub-agent to **deeply re-examine the trial** before answering the discriminators. A sub-agent that's already provisionally classified the trial as task_side could mechanically tick through Q1–Q6 without actually re-considering whether task_side is the right answer at all.

**The fix:** add a gatekeeper Q0 at the FRONT that forces a deep re-examination using the full skill before Q1–Q6 are answered.

**Q0 specification (added in TAXONOMY.md and prompts/system_judge.md):**

> "Are you sure this is task_side? Re-examine deeply using the full skill before continuing."

The sub-agent MUST:
1. Re-read the spec end-to-end on `origin/main` (not just the relevant section)
2. Re-read the failing test assertion verbatim
3. Re-read the agent's actual code verbatim
4. Cross-check against the skill's discriminator sections (Pre-check 3 cases, Industry-Standard pre-check, Math-equivalence sub-rule, hidden-quality-threshold)
5. Cross-check against canonical TAXONOMY POSITIVE/NEGATIVE examples
6. Write the task_side claim in concrete terms (specific spec line + specific defect + why no other mode fits)

**Output schema (Q0 sub-block in `task_side_self_check.q0_deep_recheck`):**

```json
"q0_deep_recheck": {
  "spec_full_reread": "<one-sentence end-to-end summary>",
  "test_assertion_verbatim": "<copy-paste failing assert>",
  "agent_code_verbatim": "<copy-paste agent's diverging code>",
  "discriminator_checks": {
    "case1_spec_authored": "no/yes",
    "case2_canonical": "no/yes",
    "industry_standard_check": "no_standard | <standard-name>",
    "math_shortcut_check": "literal_compliance | shortcut_taken",
    "hidden_threshold_ratio": "oracle-margin | N-A"
  },
  "task_side_claim_in_concrete_terms": "<2–3 sentences>",
  "confidence_after_deep_recheck": <0–1>
}
```

**Decision rule:** if `confidence_after_deep_recheck < 0.7` after the deep re-examination, **STOP and reclassify** without proceeding to Q1–Q6. The sub-agent's own uncertainty after careful re-examination is itself a strong signal that task_side is not the right answer. If `confidence_after_deep_recheck ≥ 0.7`, proceed to Q1–Q6.

**Aggregator enforcement:** the audit aggregator REJECTS task_side labels lacking the `q0_deep_recheck` sub-block, AND REJECTS labels with the contradiction `passed: true` while `q0_deep_recheck.confidence_after_deep_recheck < 0.7`.

**Why Q0 specifically (not just Q1–Q6):**

Q1–Q6 catch specific signal types but they're triggered AFTER the sub-agent already committed to a provisional task_side answer. The sub-agent walking through Q1–Q6 might rationalize discriminator answers to support its initial guess. Q0 forces a "blank slate" deep re-examination FIRST — re-reading sources, listing concrete evidence, writing out the claim in plain terms. This breaks confirmation bias before it kicks in. If the sub-agent can't write a concrete task_side claim with confidence ≥ 0.7 after re-examining, that's the signal to abandon task_side regardless of how Q1–Q6 might be answered.

**Files updated:**

- `TAXONOMY.md` — § "Cross-cutting: MANDATORY task_side self-check" expanded with Q0 specification (6-step deep re-examination procedure), updated output JSON schema, updated decision rule, updated aggregator enforcement
- `prompts/system_judge.md` — Authorship Case 3 mandatory callout updated to include Q0 explicitly with the 6-step procedure
- `SKILL.md` — version log updated to v3.2.13
- `CHANGELOG.md` — this entry

**Lesson encoded for future audits:**

`task_side` is the audit's claim against the maintainer's spec. It should require both depth (Q0 deep re-examination) AND breadth (Q1–Q6 discriminators). Q0 catches the "rationalized after the fact" failure mode where a sub-agent provisionally labels something task_side then rubber-stamps the discriminators. Q1–Q6 catch the specific signal types. Together they make task_side a deliberate, well-evidenced decision.

---

## v3.2.12 (May 6 2026 — MANDATORY task_side self-check / doubt mechanism)

**Type:** new mandatory doubt mechanism that fires before any `task_side` classification is finalized.

**Why this update:**

`task_side` is a high-bar classification — it tells the maintainer "your spec on `origin/main` has a defect." Calling something `task_side` when it isn't misroutes action to the wrong owner (maintainer instead of agent or harness operator) and damages audit credibility. Empirical track record from v3.2.x → v3.2.11:

- v3.2.10 audit found 90 trials over-attributed to `agent_conceptual` that were actually `infra_failure / stale_spec_checkout`
- v3.2.11 added the math-equivalence sub-rule after var-es-estimation was over-routed to `task_side`
- v3.2.11's *passive* sub-rules don't enforce themselves — sub-agents can still skip them under literal application of "spec doesn't pin → C3.c"

The fix: **make the discriminators an active checklist that fires automatically** before finalizing any `task_side` label.

**The mechanism (in TAXONOMY.md § "Cross-cutting: MANDATORY task_side self-check"):**

When a sub-agent provisionally classifies a trial as `task_side`, it MUST run a 6-question doubt checklist before finalizing:

| # | Question | Failure → action |
|---|---|---|
| Q1 | Failing tests are shape invariants only (positivity, in-band, etc.)? | NO (test pins specific numeric) → DOWNGRADE to A3.f |
| Q2 | No clear industry-standard exists for the named convention? | NO (industry standard exists) → DOWNGRADE to A3.f |
| Q3 | Spec doesn't mention any paper/textbook/library/eponym? | NO (citation present) → DOWNGRADE to A1/A2/A3 |
| Q4 | Agent did NOT take a math-equivalence shortcut? | NO (shortcut taken) → DOWNGRADE to A3.f per v3.2.11 sub-rule |
| Q5 | Spec doesn't use literal verbs ("draw from / select / compute")? | NO (literal verb) → DOWNGRADE to A3.f |
| Q6 | Sister trials in other batches consistently classified? | NO (inconsistent) → FLAG for cross-batch review |

**Output JSON requirement:** any `task_side` label MUST include a `task_side_self_check` field documenting all 6 answers + `passed: true/false`. The audit aggregator REJECTS any `task_side` label without this field.

**How this differs from existing rules:**

- v3.2.10 added the test-name verification step — focused on `infra_failure` discrimination
- v3.2.11 added the math-equivalence sub-rule — passive, sub-agents could skip it
- v3.2.12 makes the entire bundle of v3.2.x signals an **active mandatory checklist**, with output JSON enforcement

**Worked example baked in:**

The TAXONOMY entry includes the var-es-estimation case:
- Q1: failing tests are `assert isclose(RMSE, 0.1036, rtol=0.10)` → PINNED NUMERIC → DOWNGRADE
- Q5: spec uses verb "draw from the selected component" → LITERAL VERB → DOWNGRADE
- Q4: agent wrote `z * scales` instead of separate per-component draws → MATH SHORTCUT → DOWNGRADE
- 3 downgrades → reclassify to **A3.f / agent_conceptual**

The doubt checklist would have caught this automatically, with the answer chain documented in the output JSON.

**Files updated:**

- `TAXONOMY.md` — added § "Cross-cutting: MANDATORY task_side self-check" with the 6-question checklist, output JSON schema, and aggregator enforcement rule
- `prompts/system_judge.md` — added MANDATORY callout in the Authorship Case 3 bullet pointing at the new checklist
- `SKILL.md` — version log updated to v3.2.12
- `CHANGELOG.md` — this entry

**Lesson encoded for future audits:**

`task_side` is the audit's claim against the maintainer's spec. The bar should be high. The 6-question doubt checklist enforces that bar by forcing the sub-agent to walk through each discriminator (test type, industry standard, citation, math shortcut, literal verb, sister consistency) explicitly, with evidence in the output JSON, before finalizing.

---

## v3.2.11 (May 6 2026 — sub-rule for math-equivalence-shortcuts)

**Type:** new sub-rule under "Pre-check" — disambiguates A3.f vs C3.c when the agent takes a mathematically-equivalent shortcut.

**Why this update:**

During the v12 audit (Phase 5, after v3.2.10 was published), a deep-read of `fb-v12-opus47-r3-var-es-estimation` (and 2 sister trials) by an Opus 4.7 sub-agent classified the trial as `C3.c / task_side` because spec L22 *"draw from the selected component accordingly"* doesn't explicitly pin the RNG-call sequence. Manual review caught that this is a borderline mis-classification:

- Test pins specific numeric values: `assert RMSE_close_to(0.1036, rtol=0.10)`. Pinned numerics indicate the maintainer ran a canonical implementation and pinned ITS output — the spec is NOT genuinely under-specified, the maintainer had ONE recipe in mind.
- Spec uses literal verb "draw from the selected component" — naturally read as 3 RNG calls (1 uniform + 2 N(0,·) draws + np.where), NOT 2 calls (1 uniform + 1 N(0,1) + scale).
- Agent's `z * scales` is a math-equivalence shortcut (`N(0,9) = 3·N(0,1)`) that produces the same *distribution* but a different *concrete RNG sample sequence*. This bypasses the literal procedure.

The strict v3.2.10 rule "A3.f only when spec PINS the default" routed this to C3.c because the spec didn't explicitly say "use 3 RNG calls." But the literal-reading + pinned-test signals together indicate A3.f.

**The new sub-rule (in TAXONOMY.md § "Sub-rule: Mathematical equivalence ≠ literal compliance"):**

When the agent takes a mathematical shortcut that produces the same distribution / same final value but consumes RNG state differently or takes a different code path, classify as `A3.f / agent_conceptual` (not C3.c) when EITHER:
1. **Test pins specific numeric values** (not shape invariants like `> 0`, `in_band`, etc.)
2. **Spec uses literal verbs** ("draw from", "sample from", "select", "compute") with explicit subjects, where literal reading determines canonical execution

C3.c / task_side genuinely fits when ALL hold: tests use shape invariants only, spec describes a goal without procedure, multiple non-equivalent procedures exist, no maintainer-implied default.

**Files updated:**

- `TAXONOMY.md` — added sub-rule under § "Pre-check: who authored the formula?" with the worked example (var-es-estimation 0.0899 vs pinned 0.1036)
- `prompts/system_judge.md` — added MANDATORY sub-rule callout in the Authorship Case 3 bullet
- `SKILL.md` — version log updated to v3.2.11
- `CHANGELOG.md` — this entry

**Lesson encoded for future audits:**

Before classifying a trial as `task_side` due to "spec doesn't pin", check the test for pinned-numeric-vs-shape-invariant signal. Pinned numerics mean the maintainer had a canonical implementation in mind; agent shortcuts that bypass it are A3.f, not C3.c.

---

## v3.2.10 (May 6 2026 — same-day v3.2.9 expansion)

**Type:** expansion of v3.2.9 `infra_failure / stale_spec_checkout` rule + lessons from a 10-Opus-sub-agent re-judge of the v323 audit.

**Why this update was necessary:**

The v3.2.9 entry was published with two methodology gaps that produced an under-count of stale-spec cases (off by 90 trials):

1. **Missed sub-pattern 2 (PR-branch served before merge).** v3.2.9's diagnostic was "spec edit predates trial." But a frequent harness failure is when the operator's `tasks/` is on a *feature branch HEAD* that the maintainer subsequently revised before squash-merging. In that case the `origin/main` merge commit can post-date the trial — yet the agent's instruction still diverges from what the verifier's tests assume. v3.2.10 generalizes the rule: stale_spec_checkout fires on ANY divergence between agent's instruction and verifier's test expectations, regardless of literal date ordering.

2. **No mandatory test-name verification step.** Without checking whether failing tests exist on current origin/main, audits over-flip "consistently stale" cases (where instruction AND test were aligned at older versions, so the agent's failure is real within that older framework) and miss the discriminator between real `infra_failure` and "consistently stale." v3.2.10 makes the test-name match check mandatory.

3. **No cross-batch consistency check.** During parallel-sub-agent audits (typical for 800+ trial sweeps), sister trials of the same task split across batches sometimes get inconsistent classifications — one batch flips, another doesn't, on indistinguishable evidence. v3.2.10 adds a mandatory cross-batch consistency pass to catch sub-agent inconsistencies.

**Empirical findings from the re-judge:**

| Source | v3.2.9 estimate | v3.2.10 finding |
|---|---|---|
| Stale-spec cases in v323 audit | 1 task (21 trials) | 8 task families (91 trials) |
| Over-attribution to `agent_conceptual` | 21 trials | 91 trials (11.3% of corpus) |
| Methodology gap | "spec edit predates trial" too narrow | Sub-pattern 2 + test-name check + cross-batch consistency |

The v3.2.10 final v323 distribution: agent_conceptual 543 / task_side 92 / agent_coding 74 / **infra_failure 91** / agent_ux_bug 6 / unknown 1.

**Specific lessons encoded into the skill (so future sub-agents don't repeat them):**

1. **The "spec edit predates trial" check is necessary but NOT sufficient.** A trial that ran *before* a `origin/main` merge commit can still be a stale_spec_checkout if the operator served a pre-revision PR-branch HEAD. The substantive question is: did the agent's instruction match `origin/main`? Not: did `origin/main` change after the trial?

2. **Test-name verification is the discriminator.** Failing test names match `origin/main:tasks/<task>/tests/test_outputs.py` → real stale_spec. 0% match → consistently stale (verifier and instruction were aligned at older version) — leave original A/B/C/D classification, do NOT flip. Skipping this check causes systematic over-flipping (3 mtm-xccy v323 trials would have been wrongly flipped without this check).

3. **All sub-agents in a parallel audit must get identical skill context.** v3.2.9 release Phase-4 audit had batches 0/1 run with leaner prompts (3 skill files vs 5 for batches 5–9), causing batches 0/1 to take a stricter literal reading of v3.2.9 ("spec edit predates trial") and miss 2 flips that batches 5–9 correctly identified. The aggregator caught this only via post-hoc cross-batch consistency check. Future audits should pin a single uniform prompt template.

4. **The 13f-amendment "LLM-prior attractor" framing was wrong.** v3.2.8 (and earlier session memory) framed the 21/21 universal failure on 13f-amendment as "agents have a pretraining bias for SEC-style RESET/REPLACE/APPEND vocabulary that overrides explicit pins." That framing is incorrect: agents reasoned correctly from the (older) instruction they received and invented short labels by analogy to the verb description ("non-amendment filing **resets** the state"). They never saw the controlled-vocabulary enumeration. **A κ=1.0 universal-failure signature can be either a genuine LLM-prior attractor (agent saw the pin, ignored it) or a stale_spec_checkout (agent never saw the pin) — distinguishable only by reading trajectory.json step-2.**

5. **Action ownership matters for routing.** `task_side` says "fix the spec." `infra_failure / stale_spec_checkout` says "fix the harness pipeline." Conflating them misroutes action to the wrong owner. The maintainer's `origin/main` is correct in stale_spec_checkout cases — calling it `task_side` would mislead them into editing a working spec.

**Files updated:**

- `TAXONOMY.md` § "Cross-cutting: infra_failure / stale_spec_checkout" — expanded with sub-pattern 2, mandatory four-step diagnostic, cross-batch consistency rule, full empirical scope (8 task families, 91 trials).
- `prompts/system_judge.md` — `infra_failure` bullet now lists both sub-patterns and the mandatory four-step diagnostic.
- `OPS.md` — added "Parallel sub-agent audit pipeline rules" with mandatory uniform-prompt + cross-batch-consistency checks.
- `SKILL.md` — version log updated to v3.2.10.
- v323 labels: 91 trials at `infra_failure / stale_spec_checkout` (up from 21 in v3.2.9; preserves `original_root_cause_class` for audit trail).
- GitHub issue QF-Bench/QuantitativeFinance-Bench#226 updated with full empirical scope and two-sub-pattern documentation.

---

## v3.2.9 (May 6 2026)

**Type:** new sub-rubric — `infra_failure / stale_spec_checkout` — and retroactive correction of the v3.2.8 13f-amendment example.

**What was added:**

A new cross-cutting routing rule: `root_cause_class = infra_failure`, `infra_subrubric = stale_spec_checkout`. Fires when the harness operator's `tasks/` checkout is older than `origin/main` at trial-launch time and the agent receives a pre-edit instruction while the verifier evaluates against post-edit expectations.

**Why discovered:**

While auditing the v3.2.8 13f-amendment-aware-crowding example (κ=1.0 universal failure across 7 model families), direct verification of `agent/trajectory.json` step-2 (the literal user-role message sent to the LLM) revealed that **agents never received the L41-44 controlled-vocabulary enumeration** (`{replace_initial, replace_restatement, append_new_holdings}`). The Apr-23 commit `75d5f1a` added that block to `origin/main`, but the May 1-4 v12 sweep served a pre-`75d5f1a` snapshot. Verified bit-identical to the harness operator's GitHub upload (LFS hash match). Independent corroboration: agents' raw output (`agent/codex.txt` / `claude-code.txt`) repeatedly quotes/echoes the OLD verbal description ("non-amendment filing resets the state...") and never references the NEW enum strings (zero hits across 21 trials).

**The v3.2.8 framing of 13f-amendment as "universal LLM-prior attractor" was wrong** — agents reasoned correctly from the (older) instruction they actually received and invented short labels (RESET / REPLACE / APPEND) by analogy to the verb description. There was no controlled-vocabulary pin in their input to override.

**Diagnostic procedure (now in TAXONOMY § "Cross-cutting: infra_failure / stale_spec_checkout"):**

Before classifying any uniform-failure (κ ≥ 0.9) D1.a / D1.b case as `agent_conceptual`:
1. Read trajectory.json step-2 user message.
2. Get date-appropriate spec: `git show <commit>:tasks/<task>/instruction.md` where `<commit>` is the latest `origin/main` commit before trial timestamp.
3. Check if a distinctive line from (2) appears in (1). Absent → `infra_failure / stale_spec_checkout`.

**Empirical scope:** systemic check across all 75 v323 tasks found exactly **one** stale-spec case — `13f-amendment-aware-crowding` (21 trials reclassified). Other suspect uniform-failure tasks all received the date-appropriate spec — their failures are real agent errors.

**Why this isn't `task_side`:**

`task_side` says "fix the spec." But `origin/main` is correct. Calling stale-checkout failures `task_side` would mislead the maintainer into editing a working spec. Action belongs to the harness operator (sync `tasks/` before launching, or pin `git_commit_id` in `config.json`), not the task maintainer.

**Files updated:**

- `TAXONOMY.md` — added cross-cutting section "infra_failure / stale_spec_checkout" with diagnostic procedure; corrected the 13f-amendment positive example (was `agent_conceptual / D1.a`, now `infra_failure / D1.a / stale_spec_checkout`)
- `prompts/system_judge.md` — added `infra_failure` bullet to the root_cause_class enumeration with the mandatory diagnostic for uniform-failure cases
- v323 labels: 21 13f-amendment trials reclassified `agent_conceptual` → `infra_failure`, with `original_root_cause_class` preserved for audit trail
- Memory note `qfbench-13f-amendment-llm-prior-attractor.md` rewritten to lead with the retraction
- GitHub issue filed: QF-Bench/QuantitativeFinance-Bench#226 (alerts harness operator)

**v323 audit dashboard delta:**

- agent_conceptual: 626 → 605 (−21)
- task_side: 93 → 93
- agent_coding: 77 → 77
- infra_failure: 4 → 25 (+21)
- agent_ux_bug: 6 → 6

**Lesson for future audits:**

Always verify what the agent actually saw (trajectory.json step 2) before classifying universal-failure patterns as capability gaps. The κ=1.0 signature can be either (a) a genuine LLM-prior attractor (when the agent received the spec) or (b) a stale-spec infra issue (when the agent received an older spec). Without trajectory verification, (a) and (b) are indistinguishable from the symptom alone.

---

## v3.2.8 (May 5 2026)

**Type:** retroactive application of v3.2.7 self-check rule — found 3 more inconsistencies.

**What was found and fixed:**

After v3.2.7 added the rule-consistency self-check procedure to OPS.md, applied it retroactively to the entire skill. Found 3 more inconsistencies that pre-dated v3.2.5/v3.2.6/v3.2.7 and contradicted the newer general rules:

1. **TAXONOMY.md L683 (Authorship sub-question for D1)** — generic D1 routing said "prose enumerated → agent_coding" without mentioning the v3.2.2-pat9 carve-out (vocabulary substitution from LLM priors → agent_conceptual) or the v3.2.7 D1.g carve-out (engineering kwarg → agent_coding regardless). Updated to enumerate both carve-outs explicitly.

2. **TAXONOMY.md L696 (D1.e JSON precision)** — said *"Mostly task-side — the test tolerance is unreasonably tight for JSON round-tripping"*. Wrong by v3.2.5 hidden-quality-threshold rule: standard `json.dumps` preserves ~17 sig digits, well under any 1e-12 threshold; oracle achieves the threshold trivially. Agent's manual-rounding-before-serialization is engineering carelessness, not a brittle test. Updated routing: defaults to `agent_coding`; reserves `task_side` only for the rarer case where spec mandates intermediate rounding and a downstream test pins values computed without rounding (1 v323 trial, `etf-cross-asset-lead-lag`, fits the carve-out).

3. **TAXONOMY.md L715 (13f-amendment-aware-crowding POSITIVE example)** — inline pre-labeled as `task_side` ("instruction prose did not enumerate the canonical action labels"). Wrong by v3.2.2-pat9: instruction.md L41-45 DOES explicitly enumerate the canonical action labels using binding language *"must be one of"* — Pattern #9 schema-key-list-in-prose fires. Agents who substitute SEC's real-world `AMENDMENTTYPE` values (`RESET / REPLACE / APPEND`) are making a finance-concept substitution (LLM-prior attractor), not following an under-specified spec. The actual v323 labels (21 of 21 trials → `agent_conceptual`, κ=1.0) confirm the corrected reading. Updated to `agent_conceptual` with the empirical evidence cited.

**No trial reclassifications needed for these 3 fixes:**
- v323 13f-amendment trials are already `agent_conceptual` (judges followed v3.2.2-pat9 correctly; only the SKILL example was stale)
- v323 D1.e+task_side trial (`etf-cross-asset-lead-lag`) is correctly labeled — fits the carve-out for genuine spec-test inconsistency
- L683 was a wording clarification only

**Auditing process** (now documented in OPS.md as the standard procedure):

```bash
grep -nE "as it does here|canonical .*case|for [a-z-]+ specifically|\
task_side .*if .*spec mandated|\
root_cause_class\s*=\s*\`?[a-z_]+" SKILL.md TAXONOMY.md INDUSTRY_STANDARDS.md OPS.md
```

For each match, verify the inline pre-label is consistent with all subsequent v3.2.x rules. The v3.2.7 process audit ran this grep against 4 skill files and found 4 hits requiring fixes (1 in v3.2.7 + 3 in v3.2.8).

**Lessons for the audit cadence:**
- Run the grep recipe **whenever** a new general rule (v3.2.x) lands, not just on suspicion.
- Cross-check inline examples against the actual v323 trial labels — if they disagree, the SKILL is stale.
- Document each match's verdict in the CHANGELOG (consistent / updated / reclassified) so future audits can skip already-checked entries.

**Practical impact:** The aggregate-report root_cause distribution remains the same as v3.2.7 (no trial reclassifications in v3.2.8) — but the SKILL's worked examples now match the rules, eliminating a future-judge trap where the more-specific older example would override a newer general rule.

---

## v3.2.7 (May 5 2026)

**Type:** rule consistency fix + new self-check process rule.

**What was changed:**

- `TAXONOMY.md` § "D1.g routing" (around the cross-sectional-momentum POSITIVE example): rewrote the routing rule to be consistent with v3.2.5/v3.2.6. Default D1.g routing is now **`agent_coding`**. Reserve **`task_side`** ONLY for cases where the spec explicitly writes the buggy library call verbatim with the wrong kwarg specified (e.g., spec literally says `df.sort_values('date', kind='quicksort').drop_duplicates(keep='last')`). Specs that are merely **silent on the kwarg** (the common case, including cross-sectional-momentum's "sort by date ascending") test the agent's engineering judgment and route to `agent_coding`.

- Removed the misclaim "as it does here for cross-sectional-momentum" from the POSITIVE example. The spec for cross-sectional-momentum says only "sort by date ascending" — silent on stability, not mandating the buggy idiom. Spec-level "silent on kwarg" is fundamentally different from "spec mandates buggy idiom."

- Added cross-reference to v3.2.5 (hidden-quality-threshold): if oracle's drift on the failing test is ≪ test threshold, this is a quality gate, not a brittle pin → route to `agent_coding`. For cross-sectional-momentum: oracle drift = 0 (Python stable list.sort), test threshold = 1e-12, ratio = 0% → unambiguous quality gate.

- **Reclassified 9 cross-sectional-momentum trials in v323 corpus:** 8 from `task_side` → `agent_coding` (D1.g, agent didn't add `kind='stable'` defensively); 1 from `task_side` → `infra_failure` (Pattern C, fb-v10-h45 had correct first-session output then 429 cascade on harness rerun).

**New self-check rule (process improvement):**

When adding a new general rule to the skill, **audit existing worked examples for consistency**. The cross-sectional-momentum mislabeling happened because v3.2.5 (hidden-quality-threshold) and v3.2.6 (trajectory sub-classification) introduced new general routing principles, but the older v3.2.1 worked example for cross-sectional-momentum had an inline pre-labeling ("as it does here → task_side") that contradicted the new rules. Judges followed the more-specific older example and missed the new general rule.

**Going forward (added to OPS.md / skill maintenance checklist):**

When adding ANY new rule that affects routing, search for:
- Pre-labeled worked examples with concrete verdicts ("as it does here → X")
- Inline parentheticals carving exceptions ("(or X if Y)")
- "Canonical X case" claims in POSITIVE/NEGATIVE blocks
- Any phrasing that hardcodes a routing for a specific task or trial

For each match: verify it's still consistent with the new rule. If not, update or remove the example. Document the audit in the CHANGELOG entry for the new rule.

**Rationale:** rule-based skills accrete worked examples over time. New general rules are correct in the abstract but can silently contradict old worked examples. Judges (correctly) follow the more-specific older example, so the new rule has no effect. The cross-sectional-momentum mislabel cost 8 mis-attributed trial labels in v323 — a quality-of-classification metric across the entire benchmark would have been wrong without this audit.

**Practical impact:**
- Forward-looking: future rule additions trigger an explicit "audit existing examples" step. Reduces silent inconsistency.
- Retrospective: v3.2.5/v3.2.6 introduction missed this audit; v3.2.7 catches it. Aggregate-report numbers in v323 should now be more accurate (task_side 93 not 102).

---

## v3.2.6 (May 5 2026)

**Type:** taxonomy addition — sub-classify trajectory failures into 3 distinct patterns.

**What was added:**

- `TAXONOMY.md` § "Trajectory-failure sub-classification" (between Pre-flight gate and Pre-check) — new ~150-line section that splits the previously-monolithic `insufficient` root_cause class into three sub-types with distinct interpretation in aggregate reporting:

  - **Pattern A — `agent_engineering_weakness`** (root: `agent_coding`): wall-clock or context-budget overrun caused by inefficient agent code (naive scipy.quad per grid point, non-vectorized inner loops, excessive input-file probing). The time/context limits are **part of the task's intentional difficulty design** — failing to fit reveals real engineering weakness. **Counts as legitimate agent failure.** Examples: `fb-v10-s45-stochvol-implied-surface-new` (slow CZ pricer hit 1800s wall), `fb-v11-opus46-yield-curve-bond-immunization` (burnt 30-min on file probing, zero Write calls).

  - **Pattern B — `agent_ux_bug`** (NEW root_cause class): Plan-mode trap. Agent enters Plan mode, drafts a complete and quant-correct plan, calls `ExitPlanMode`; harness rejects (no user to approve in non-interactive context); agent treats rejection as a clarifying-question prompt and exits without executing. **NOT a quant capability gap** — agent's reasoning was demonstrably correct. **NOT infrastructure** — provider responded fine. It's a Claude-Code-specific mode-management bug that manifests in non-interactive harnesses. Empirically: 6 trials across 5 distinct tasks (`implied-vol-approximations` ×2, `compound-option-geske`, `merton-jump-diffusion`, `digital-barrier-options`, `fft-compound-poisson`); affects all Claude Code variants (Haiku 4.5, Opus 4.6, Sonnet 4.5). Aggregator handling: count toward agent score WITH explicit caveat (signals harness/UX bug, not capability).

  - **Pattern C — `infra_failure`** (NEW root_cause class): provider 429 (Bedrock ThrottlingException, etc.), container/volume path-isolation mismatch, network errors. Agent has no agency over upstream throttling or harness plumbing. **EXCLUDE from agent quality score** — these signal benchmark infrastructure quality, not model capability. Examples: 2 Bedrock-routed Haiku 4.5 trials (`cme-hdd-option-pricing`, `swap-curve-bootstrap-ois`) hit 429 cascade across 10 retries with model never even receiving the prompt; 1 trial (`hull-white-swaption` opus46 R2) had agent's outputs invisible to verifier due to container path-visibility mismatch.

- Added explicit **decision flow** for routing trajectory failures to the right sub-class.

- Added **aggregator treatment guidance**: Pattern A counts as agent failure; Pattern B counts with caveat (track separately for harness feedback); Pattern C is excluded from quality scores (track as `infra_failure_rate` metric instead).

**Rationale:** during the v323 task-fix audit, the user pointed out that lumping all trajectory failures under a single `insufficient` label conflates three very different signals. Wall-clock overruns from naive code (Pattern A) are legitimate agent weakness — the time limit is part of the task's hardness, designed to test efficient engineering. Plan-mode traps (Pattern B) are a Claude Code harness-UX issue distinct from quant capability — the agent's reasoning was correct, just couldn't execute. Provider 429s (Pattern C) are infrastructure noise that shouldn't even count toward the agent's quality score. Treating these identically would distort capability comparisons across models (e.g., a benchmark sweep where one model happens to route through a more-throttled provider would look artificially worse).

**Practical impact:**
- Forward-looking: future judges have a 3-way decision flow when a trial has no quant content — diagnostic signatures and sub-class names are cited explicitly, with empirical examples from v323 keyed to each.
- Retrospective: 11 of 22 insufficient-class trials in v323 should be reclassified per the new sub-types:
  - 3 → `agent_coding` / `agent_engineering_weakness` (stochvol, 2× yield-curve-bond-immunization opus46)
  - 6 → `agent_ux_bug` (Plan-mode trap on 5 distinct tasks)
  - 3 → `infra_failure` (2× Bedrock 429, 1× container path opus46-r2-hull-white-swaption)
- Aggregate reports can now produce three distinct metrics: agent quality score (excluding infra), `agent_ux_bug_rate` (Claude Code harness feedback), and `infra_failure_rate` (benchmark plumbing health).

---

## v3.2.5 (May 5 2026)

**Type:** rule addition — hidden-quality-threshold decision rule.

**What was added:**

- `TAXONOMY.md` § "Cross-cutting: hidden quality thresholds — NOT brittle pins" — new ~50-line section between cascade examples and provenance. Documents the **intentional task-design pattern** where:
  - Spec states a metric formula + asks the agent to report it (e.g., `rmse_bps`)
  - Spec withholds the numerical threshold (e.g., never says "RMSE must be < 5 bps")
  - Test enforces the threshold (e.g., `assert rmse < 5.0`)
  - Oracle passes with comfortable margin

  When all four hold, the task is **intentionally hard** (forces production-quality code, not threshold-targeting), and agent failures are `agent_coding`/`agent_conceptual`, NOT `task_side`. The hidden threshold is doing its job — catching subtle implementation bugs.

- Added **gap-diagnostic table**: Oracle/threshold ratio ≤ 0.5 → hidden-threshold quality gate (agent_coding); 0.5-0.95 → borderline (check formula's intrinsic bias at failure point); > 1 → genuine task-side breakage.

- Added **worked example pair** for contrast:
  - `hull-white-swaption` test_caplet_diffs_below_3bps — oracle 1.59 bps vs 3-bps bound (47% headroom). Agent fails despite identical (a, σ). **Correct label: `agent_coding`** (subtle long-T HW caplet pricer divergence). The original task_side label on `fb-codex-55-r3-hull-white-swaption` is now flagged as misclassification.
  - `spread-option-kirk-margrabe` test_kirk_mc_agreement — oracle FAILS (or passes by < 5%) on a deepest-ITM grid point where Kirk's 1995 formula has documented 3-5% bias. **Correct label: `task_side / brittle pin`** (the bound is tighter than the formula's intrinsic error).

**Rationale:** during the v323 task-fix audit, the user pointed out that `hull-white-swaption` is intentionally designed to hide thresholds — the spec deliberately doesn't tell agents the bar, so agents must produce production-quality calibration code rather than aiming for the minimum that passes. Without this rule, future judges would lazily attribute hard-task failures to "brittle pins" and request unnecessary task-side fixes, eroding the benchmark's difficulty signal. The rule cleanly distinguishes:
- **Brittle pin** (test threshold tighter than the formula's intrinsic error; oracle barely passes or fails) → fix the test
- **Hidden quality gate** (test threshold is achievable; oracle passes with margin; agent fails because of a real bug) → don't fix anything; reclassify the trial as agent-side

**Practical impact:**
- Forward-looking: tasks like `hull-white-swaption` (and any other "spec defines metric, test imposes hidden bound, oracle passes by ≥50% margin") route correctly to agent_coding/agent_conceptual instead of being mis-flagged as task_side.
- Retrospective: `fb-codex-55-r3-hull-white-swaption` and `fb-v10-opus46-r2-hull-white-swaption` (the latter being a separate harness/container infrastructure issue) now have explicit guidance to be re-classified.
- Connects to v3.2.4's brittle-pin guidance — the two patterns are mutually exclusive, and this rule lets judges discriminate.

---

## v3.2.4 (May 5 2026)

**Type:** content addition (industry standards expanded with quantitative Kirk approximation data).

**What was added:**

- `INDUSTRY_STANDARDS.md` § D.4 (Kirk vs Margrabe spread option) — substantially expanded from a 5-line summary to a full reference entry with:
  - Quantitative Kirk-vs-MC error magnitudes from Harutyunyan & Masip Borrás (2018), arXiv:1812.04272 — explicit table of max error % across ρ ∈ {0.80, 0.85, 0.90, 0.95, 0.999} at K∈[0,20], T=0.5: **<1% at ρ ≤ 0.90; up to ~7% at ρ=0.95; up to ~5% at ρ=0.999.** Worked example from p.26: at ρ=0.80, K=5, T=0.5, Kirk=0.5616 falls **outside** narrow MC CI (0.5399, 0.5428) by 3.5-4%.
  - Direction of error growth: paper's own statement that errors "take an exponential shape" with increasing T, ρ, K (Figures 6-10).
  - Explicit decision procedure for judging Kirk-vs-MC test failures: ATM/short-T failures = real bug; deep-ITM/deep-OTM/long-T/high-ρ failures = `task_side / brittle pin`.
  - Empirical confirmation from QF-Bench v323 sweep: 5 trials of `spread-option-kirk-margrabe` across 5 distinct model families (codex-53c, codex-54mini, claude-code_opus46, codex-gpt-5.4-mini, G5.4m) all failed `test_kirk_mc_agreement` deterministically at the same single grid point (T=1.0, K=−0.10·avg_spot, deepest-ITM) with 3-5% Kirk-vs-MC gap.
  - Verified citations: Harutyunyan & Masip Borrás 2018 (PDF read directly, pages 22-31 contain Figures 1-10 with explicit error tables); Alòs & León 2015 (Modified Kirk derivation); Carmona-Durrleman 2003 (verbatim "few percentages" quote verified); Margrabe 1978 (open URL); Kirk 1995 (book reference).

**Rationale:** the `spread-option-kirk-margrabe` task in v323 produced 5 task-side failures across the model-family stratification — same single grid point, same 3-5% gap, every time. Investigation revealed Kirk's intrinsic 1995 approximation has documented bias whose magnitude exceeds typical 3·SE Monte Carlo tolerance bands at extremes. Without this catalog entry, future judges would either (a) repeat the same investigation or (b) mis-attribute the failure as A3 (parameterization) or C2 (numerical) when the real cause is task-side test brittleness on a known-imperfect formula.

**Practical impact:**
- Forward-looking: `spread-option-kirk-margrabe`-class trials route correctly to `task_side` with citation-supported confidence ≥ 0.85 instead of being mis-bucketed under A/B/C.
- Same pattern applies to any task that pins a known-imperfect approximation (Bjerksund-Stensland for American options, Hagan SABR for vanilla IV, Tilley-Longstaff for early-exercise) against a tighter-than-the-formula tolerance — D.4 is the template.

---

## v3.2.3 (May 5 2026)

**Type:** prompt clarification (no rule changes; precedence rule made explicit).

**What was added:**
- In `prompts/system_judge.md` § Spec-Citation Extraction Pre-check: explicit two-mechanism hierarchy. **Deep-read is canonical and reliable**; **regex scanner (`scripts/scan_citations_v2.py`) is for reference only and not reliable on its own**. Precedence rule: when deep-read disagrees with the scanner's regime label, deep-read wins, full stop.
- Empirical example documented (the `dupire-local-vol` case where the scanner missed *"with the following exact keys: S0, r, D, n_expiries, n_options_filtered, expiry_dates"* — pattern #9 regex catches *"with top-level keys:"* but not *"with the following exact keys:"*. Deep-read correctly classified as spec-authored; the verdict came out right because the rule says deep-read overrides).

**Rationale:** the regex scanner inherently can't catch every prose variation a spec author might use. Trying to extend pattern #9 to cover every form (*"top-level keys"*, *"exact keys"*, *"required keys"*, JSON-skeleton fences, …) leads to ever-broader regexes with diminishing returns. The cleaner answer is to acknowledge the scanner is a triage hint, not the source of truth, and to make deep-read the canonical mechanism. The v3.2.2-pat9 deep-read mandate already required reading the spec in full; v3.2.3 just makes the precedence over the scanner explicit so future judges don't blindly trust the scanner's regime label.

**Practical impact:** zero on past judgments (the dupire verdict was already correct because deep-read overrode the scanner). Forward-looking: future judges will explicitly know to override the scanner on regex misses, rather than going through the dance of expanding the regex.

---

## v3.2.2-pat9 (May 5 2026)

**Type:** rule addition — Spec-Citation Pre-check expanded from 8 to 9 patterns; new mandatory deep-read guideline.

**What was added:**
- **Pattern #9 (schema-key list in prose)** added to the v3.2 Spec-Citation Pre-check. Triggers on language like *"must contain (exactly) these keys: X, Y, Z"*, *"must be an object with scalar values for ..."*, *"Columns: 1. ticker 2. name ..."*, or *"Write a JSON object with exactly these top-level keys: ..."*. When pattern #9 fires, the spec is authored on the schema/output layer — schema/output failures (D1.a vocabulary, D1.d type-serialization, D1.f date-format, D1.b shape) route to **agent_conceptual**, NOT `task_side`.
- **Deep-read mandatory rule** added to `prompts/system_judge.md` § Judging principles. Forbids producing labels from preflight signals alone — the judge must open `verifier/ctrf.json`, `verifier/diagnostic.json`, agent code, `instruction.md`, and the relevant test source before emitting a verdict. Heuristic preflight is now explicitly defined as a "planning aid only" not a substitute for trace reading.
- Updated `scripts/scan_citations_v2.py` with regex patterns + `scan_schema_keys()` function detecting numbered Columns: lists, prose triggers, and inline backticked-key lists. Wired into the regime classifier with weight 2 (same as inline-math / param-pin / day-count-strong).
- Updated `references/spec_citation_patterns.md` with full Pattern #9 documentation including the empirical motivation case (`etf-overlap-redemption-pressure`) and false-positive guard.

**Rationale (empirical):** during the V11 stratified-50 sweep on May 5 2026, the v3.2.1 batch heuristic classifier mis-judged `fb-codex-55-r2-etf-overlap-redemption-pressure` as D1.a / `task_side` based on a "silent regime" classification. On detailed re-review, the instruction explicitly enumerated required `summary.json` keys (lines 196-211) AND explicitly distinguished null-for-prices vs zero-for-exposures (line 6). The agent's failure was: (a) emitting `0.0` for `implied_price_spy` where the spec said null (D1.d), and (b) missing `largest_redeemed_nav_dollars_scenario` and `top_ticker_by_dollars` keys entirely (D1.a). Both are spec-pinned violations → `agent_conceptual`. Pattern #9 closes the regex gap; the deep-read rule prevents the parallel anti-pattern of producing labels without trace reading.

**Empirical impact on V11 stratified-50 results:** one row corrected. Original report: 16 task→agent flips + 2 agent→task flips. After v3.2.2-pat9 correction: 16 task→agent + **1** agent→task (the asian-option ground-truth-verified case is now the only true reverse flip). See `~/qfbench-trials/v11-analysis-v321/V11_REPORT_v321.md` for the corrected aggregate and `entries/fb-codex-55-r2-etf-overlap-redemption-pressure.md` for the corrected per-cell entry.

**Operational guidance for future judges:**
- Always run the Spec-Citation Pre-check BEFORE concluding "silent regime". Pattern #9 catches schema-key enumeration that the prior 8 patterns miss.
- Always read ctrf.json trace lines before producing a D1 vs A2 vs A3 judgment. The trace text (`KeyError: 'X'` vs `0.0 != nan` vs `expected 47.05, got 46.07`) distinguishes the modes definitively in ways that test-name patterns alone cannot.

---

## v3.2.1-routing-examples (May 5 2026)

**Type:** documentation enhancement (no rule changes; empirical pattern catalog).

**What was added:**
- `examples.md` Example 5 — D1.a worked example (the asian-option-levy-curran case): full trial setup, instruction excerpt, schema, test assertion, oracle code, ground-truth verification (693 close prices vs 692 log-returns), agent's behavior, and a complete `labels.json` snippet showing v3.2.1 routing to D1.a / task_side. This was the underrepresented mode (D1.a) in the original 4-example set.
- `references/v321_routing_changes.md` — new reference documenting the **3 mechanism patterns** that drive v3.2.1 vs v3.1 verdict diffs:
  1. Per-cell vs per-task analysis (cell-level ctrf reading reveals heterogeneous failures within a trial)
  2. Sub-rubric refinement (B2 vs A3.f distinction for spec-pinned vs industry-default convention failures)
  3. Spec-pinned convention enforcement (Spec-Citation Pre-check tightens task_side bar when 1+ of the 8 inline-pin patterns fire)
  Each pattern is illustrated with worked cases from the May 5 2026 stratified-10 pilot.

**Rationale:** the v3.2.1 routing produces materially different labels than v3.1 on ~30% of cells in pilot judging. Without documenting *why*, future sessions wouldn't understand whether the diffs are real improvements or model-side noise. The 3-pattern catalog grounds the diffs in specific, reproducible rule mechanisms — anchored to the canonical empirical ground-truth case (asian-option triple-contradiction, where 693 ≠ 692 was directly verified against the SPY data file).

**Empirical grounding:** May 5 2026 stratified-10 pilot. 4 of 10 cells produced different verdicts under v3.2.1; the 4 diffs cluster into the 3 documented mechanisms. Net direction: 3 task→agent flips + 1 agent→task flip; the agent→task flip caught a real verifiable spec defect (asian-option) that v3.1 had misclassified.

**Operational use:** future judges should consult `references/v321_routing_changes.md` when:
- A trial's v3.2.1 verdict disagrees with the historical v3.1 label and the disagreement needs explanation.
- Calibrating against historical labels (κ comparisons) and unexpected disagreements need attribution.
- Debugging whether an unexpected `task_side` should actually be `agent_conceptual` (Pattern 3 diagnostic).

---

## v3.2.1-refs (May 4 2026)

**Type:** documentation enhancement (no rule changes; reference-provenance audit).

**What was enhanced in `INDUSTRY_STANDARDS.md`:**
- §A.9 variance drain — added direct-verified passage quotes for Wikipedia + Kitces; added Jacquier-Kane-Marcus 2003 academic primary source.
- §D.9 SVI/SSVI/Fengler — promoted SSOAR open-access mirror to its own bullet; added RePEc index entry; added direct-verified annotation on Gatheral-Jacquier arXiv.
- §F.5 execution cost — added Risk.net + Semantic Scholar alternates for Almgren-Chriss; sharpened the "Almgren et al. 2005 rejects √-law" caveat; added direct-verified annotations on Bouchaud + arXiv 2311.18283.
- §F.10 winsorize-then-z-score — added direct-verified passage quotes for MSCI Quality + AQR; added AQR open mirror; added Barra USE4 Methodology Notes (current-version doc); clarified Barra's two-stage descriptor-vs-factor-exposure pipeline.
- §I Backtest Discipline — added S&P Capital IQ PIT-vs-lagged whitepaper as cross-vendor confirmation; added FactSet Regime Changes secondary article; added direct-verified annotations on AnalystPrep + CFI + Calcbench.

**Rationale:** v3.2.1 had reference URLs but no per-citation provenance. v3.2.1-refs adds an explicit verification-status annotation on each citation (paywall vs anti-bot vs URL-only vs content-verified), making it cheap for a future reviewer to spot-check claims.

**Empirical verification work:** all 28 reference URLs HTTP-checked (18 × 200 OK, 2 paywalled, 2 anti-bot, plus alternate mirrors); content-verified 11 via direct WebFetch in the session; flagged paywalled and anti-bot blocks explicitly.

**Artifact:** `~/Downloads/qfbench-quant-correctness-analysis-v3.2.1-refs-20260504-224513.zip` (178 KB).

---

## v3.2.1 (May 4 2026)

**Type:** content addition — 7 new industry-standard rules across 5 sections of `INDUSTRY_STANDARDS.md`.

**What was added:**
- **§A.9** — Cumulative-return computation: variance drain (`CAGR ≈ AR − ½σ²`).
- **§D.9** — Implied-vol surface parameterization (SVI/SSVI per Gatheral-Jacquier 2014; Fengler 2009 arbitrage-free smoothing splines as alternative).
- **§F.5** — Execution cost / market impact (Almgren-Chriss 2000 linear-impact framework + empirical √-law as separate citation lineage).
- **§F.10** — Cross-sectional standardization order: winsorize THEN z-score (MSCI Quality, MSCI FaCS, AQR practical guide, Barra US Equity v3 handbook).
- **§I** (new top-level section) — Backtest Discipline / Point-in-Time Integrity. Three sub-rules: I.1 signal-time integrity, I.2 fundamental release-date timestamping, I.3 universe / survivorship.

**Rationale:** user-driven enrichment of high-value industry rules grounded in recurring patterns observed across V11 trials. Each rule was vetted via web search for primary references before the entry was added; citations were verified via direct WebFetch where possible (Wikipedia, Kitces, Gatheral-Jacquier arXiv, Bouchaud Substack, arXiv 2311.18283) and via secondary sources for paywalled/binary docs.

**Artifact:** `~/Downloads/qfbench-quant-correctness-analysis-v3.2.1-20260504-203152.zip` (176 KB).

---

## v3.2 (May 4 2026)

**Type:** core inference-rule addition — Spec-Citation Extraction Pre-check.

**What was added:**
- Spec-Citation Extraction Pre-check in `prompts/system_judge.md` (runs FIRST, before the existing Authorship pre-check).
- `references/spec_citation_patterns.md` — full empirical catalog with per-task regime table.
- `scripts/scan_citations_v2.py` — reproducible regex scanner.
- A3.f sub-rubric refinement in `prompts/wrong_parameterization.md` to require running the new pre-check first.

**Rationale (empirical):** systematically scanned all 85 V11-focus task instructions (canonical 82 + 3 PR tasks #135/#136/#137). Found that QF-Bench specs use **8 distinct citation forms** that the original Authorship pre-check missed several of:
1. Author–year cite (e.g., `Levy (1992)`, `Barone-Adesi & Whaley (1987)`)
2. Textbook section ref (e.g., `Vol II §3.2.2`, `Problems 1, 5`)
3. Cross-file ref (e.g., `see formulas.md`, `in /app/data/spec.json`)
4. Inline TeX math (`$...$`, `\Phi`, `\frac`)
5. Library kwarg pin (`np.quantile(method='lower')`, `ddof=1`)
6. Pinned numerical parameter (`m = 3`, `nu = 4`)
7. Day-count pin (`ACT/360`, `ACT/365F`)
8. **Pseudocode-fence formula** (Markdown ``` blocks with assignments / sums / math operators) — STRONGEST form, missed entirely in v3.1.

**Result:** scan classified the 85 tasks into **56 spec-authored / 23 spec-delegates / 6 silent**. Under v3.1 rules, ~31 cells were mis-flagged as A3.f `agent_conceptual` when they should have been A2 spec-authored (failure to follow an explicit pin). v3.2 fixes this routing.

**Artifact:** `~/Downloads/qfbench-quant-correctness-analysis-v3.2-20260504-193048.zip` (172 KB).

---

## v3.1 (earlier May 2026)

**Type:** taxonomy refinement — A3.f sub-rubric and Industry-Standard pre-check.

**What was added:**
- A3.f "Agent overthink / non-industry-standard convention default" sub-rubric in `prompts/wrong_parameterization.md`.
- Industry-Standard pre-check in `prompts/system_judge.md` (mandatory before classifying any A3 / C3.c / B-class hit as `task_side`).
- Initial `INDUSTRY_STANDARDS.md` with sections A–H (volatility/risk, time series, numerical methods, pricing, curves, portfolio, schema, "no one tells you" trivia).

**Rationale:** v10 batch analysis showed ~50% of trial labels were being attributed to `task_side` when the actual cause was `agent_conceptual` (knowledge gap about industry default). Tightening the bar for `task_side` and routing more cells to `agent_conceptual` better reflects the actual capability gap being measured.

---

## v3.0 / earlier

**Type:** initial 10-mode taxonomy.

**What's there:**
- 9 quant-correctness modes: A1–A3 (Model & Formula), B1–B3 (Convention & Units), C1–C3 (Data & Numerics).
- D1 (Spec & Output Compliance) added from the v10 batch analysis when 5 sub-agents on the same data-engineering trial picked 3 different mode classifications for the same root cause.
- D1.g engineering-layer special case (subsumes A/B/C when a wrong-value bug comes from a library API default the agent didn't override).
- Cohen's κ = 0.89 on a 20-trial stratified sample over 7 calibration rounds (see `CALIBRATION.md`).

**Empirical grounding:** ~75 unique PRs across the QF-Bench repo PR review corpus.

---

## Convention for future iterations

When making changes:
1. Add a new entry at the top of this file (newest-first).
2. Include: type (rule change / doc-only), what-was-added, rationale, and the artifact zip path.
3. Cite the artifact zip in `~/Downloads/` so the version-state is reproducible.
4. Cross-reference the relevant memory file in `~/.claude/projects/-Users-jojo-temp/memory/` if the rationale relies on session-specific empirical work.
