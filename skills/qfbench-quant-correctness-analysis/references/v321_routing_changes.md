# v3.1 → v3.2.1 Routing Changes — Patterns + Worked Cases

*Empirical source: V11/V12 stratified-10 pilot, May 5 2026. Same trial folders judged under both rule sets; 4 of 10 produced materially different verdicts. The 4 diffs cluster into 3 mechanism patterns documented below.*

This file records **why** v3.2.1 produces different labels than v3.1 on the same trials. It's a meta-pattern catalog — useful when:
- A future judge wonders why the v3.2.1 pre-check changed an otherwise-stable verdict.
- The skill is being calibrated against historical v3.1 labels and unexpected disagreements need explanation.
- Determining whether a future v3.X update would re-shift the routing in either direction.

---

## Pattern 1: Per-cell vs per-task analysis

**Mechanism.** Under v3.1's batch-write workflow, classifications were written *task-level* and applied across all cells of that task (R1, R2, R3 of all agents). This batch helper assumed within-task homogeneity in failure modes. **It's not always true** — different rounds / agents of the same task can hit different bugs.

v3.2.1 reads each cell's own `verifier/ctrf.json` + `verifier/diagnostic.json` and routes per-cell. When the task has cell-heterogeneous failures, this reveals diffs that v3.1 missed.

### Worked case A: `fb-codex-55x-r3-asian-option-levy-curran`

- **v3.1 label**: A2 + B3 / agent_conceptual ("Curran's two-moment lognormal has wrong second-moment + n_prices off by 1")
- **v3.2.1 label**: D1.a / task_side (vocabulary triple-contradiction; see `examples.md` Example 5)
- **Cell-specific failure**: only `test_n_prices` fails (1 of 24 tests). 23 quant tests pass.
- **Diff mechanism**: v3.1's diagnosis was applied from cross-cell signature (some R1/R2 cells had real A2 violations). For R3 specifically, only the schema test fails — making A2 structurally impossible (a real A2 would fail multiple downstream tests). v3.2.1's per-cell reading correctly identified this.

### Worked case B: `fb-v10-s45-r3-yield-curve-bootstrap-immunization`

- **v3.1 label**: A3 + C2 / task_side ("Nelson-Siegel curve fit issues — `ns_fitted_spot_rates` 24× off")
- **v3.2.1 label**: A2 + D1.a + A3 / agent_conceptual ("missing optimizer constraints on the immunization plan")
- **Cell-specific failure**: 48/52 pass; failing tests are `test_ip_keys`, `test_ip_allocations_nonnegative`, `test_ip_allocations_sum_to_pv` (all on the **immunization plan output**, not the NS curve fit).
- **Diff mechanism**: v3.1's NS-fit diagnosis applied to other cells of the trial (some did fail NS tests). For S4.5 R3 specifically, the curve-fit + analytics tests pass; the failures are constraint violations on the long-only KRD-matched portfolio. Per-cell ctrf reading reveals this.

### How to detect this pattern

Heuristic: when a trial's cells span a wide score range (e.g., R1 = 0.0, R2 = 0.6, R3 = 0.0), the cells likely hit different bugs. Reading cell-level ctrf is required.

---

## Pattern 2: Sub-rubric refinement (B2 vs A3.f)

**Mechanism.** Before v3.2, "sign convention" failures all routed to B2 (sign_convention_error), regardless of whether the spec actually pinned the sign. v3.2 added A3.f (industry-standard convention default) explicitly to disambiguate:

- **B2** = agent flipped a sign on a *spec-pinned* value (spec said "report VaR as positive losses", agent emitted negative).
- **A3.f** = spec is silent on convention; an industry standard exists; agent picked the non-standard variant (spec didn't pin sign; INDUSTRY_STANDARDS §A.7 pins loss-space; agent emitted return-space).

Both are agent_conceptual root cause — but A3.f is the more accurate sub-rubric when the spec is silent.

### Worked case: `fb-codex-54mini-crypto-funding-rate-basis-carry`

- **v3.1 label**: B2 / agent_conceptual ("VaR/CVaR sign convention flipped")
- **v3.2.1 label**: A3.f / agent_conceptual (same root cause class, more accurate sub-rubric)
- **Test signature**: `test_mc_var_cvar_nonneg_and_consistent` asserts `var_95 >= 0` and `cvar_95 >= 0`; agent emitted negative values.
- **Diff mechanism**: spec is silent on VaR/CVaR sign convention. INDUSTRY_STANDARDS §A.7 pins loss-space (positive losses) as industry default. Agent picked return-space. Routes to A3.f (industry-default failure), not B2 (pinned-sign flip).

### How to detect this pattern

Diagnostic test: read the spec for the convention in question (sign, ddof, annualization basis, etc.).
- If spec EXPLICITLY pins the convention and agent diverges → B1/B2/A3 (spec-pinned violation).
- If spec is silent AND an industry standard exists → A3.f.
- If spec is silent AND no industry standard exists → C3.c / task_side.

---

## Pattern 3: Spec-pinned convention enforcement (tightening task_side)

**Mechanism.** v3.2.1's Spec-Citation Pre-check (8 patterns: author cite, section ref, cross-file ref, inline TeX, library kwarg, pinned numerical param, day-count pin, pseudocode-fence formula) formally checks whether the spec inline-pins the convention. If yes → spec-authored regime → agent failure to follow the pin is `agent_conceptual`, never `task_side`.

v3.1 had a looser bar for `task_side`: any "convention divergence" could be labeled task_side if the spec used named methods (regardless of whether the convention itself was pinned). v3.2.1 separates "method named" from "convention pinned" cleanly.

### Worked case A: `fb-v10-opus46-r3-kelly-var-sizing`

- **v3.1 label**: A3.c / task_side ("Sharpe convention divergence — spec under-specifies annualization")
- **v3.2.1 label**: A3.c / agent_conceptual (same sub-rubric, root cause class flipped)
- **Diff mechanism**: spec literally says *"Do NOT subtract risk-free rate, annualize with sqrt(252), std ddof=1"*. Three of v3.2's eight inline-pin patterns fire (kwarg pin: `ddof=1`; numeric pin: `√252`; prose pin: "Do NOT subtract"). With three explicit pins, the convention IS authored — agent's divergence is `agent_conceptual`, not `task_side`.

### Worked case B: `fb-v10-s45-r3-yield-curve-bootstrap-immunization` (same as Pattern 1 case B)

- The spec also pins the immunization plan's output schema (named keys) and constraints (allocations non-negative, sum-to-PV). Three pins fire. Failure to satisfy these is agent_conceptual, not task_side.

### How to detect this pattern

Diagnostic test: run the v3.2 Spec-Citation Pre-check (`scripts/scan_citations_v2.py` is the regex-based scanner; `references/spec_citation_patterns.md` is the per-task catalog). If 1+ of the 8 inline-pin patterns fire on the relevant convention, the regime is spec-authored and `task_side` is unavailable for that convention.

---

## Cross-pattern: net direction of routing changes

In the May 5 2026 pilot (n=10):

| Pattern | Direction | Cases |
|---|---|---|
| Per-cell vs per-task (1) | mixed | A: agent → task_side; B: task → agent |
| Sub-rubric refinement (2) | n/a (root cause stable) | crypto-funding |
| Spec-pinned enforcement (3) | task_side → agent_conceptual | kelly-var, yield-curve-bootstrap |

**Net direction**: 3 cases flip toward `agent_conceptual`, 1 case flips toward `task_side`. But the case-1A flip (asian-option) is the most consequential — it surfaced a real, ground-truth-verified spec defect that v3.1 missed. The improvement is **case-by-case correctness in both directions**, not a uniform attribution shift.

If applied across the full 808-trial workqueue:
- ~10–15% of cells likely produce different labels under v3.2.1
- Decisive flips (catching task-side defects misattributed by v3.1) are the most valuable — they surface real benchmark bugs

## Operational guidance

When judging a new trial under v3.2.1:

1. **Read the cell's own ctrf**, not just the trial-level signature. If the trial has cell-heterogeneous failures, per-cell judging is required (Pattern 1).
2. **Run the Spec-Citation Pre-check first** (Pattern 3) — count which of the 8 inline-pin patterns fire on the convention(s) in question. Spec-authored conventions can't be `task_side`.
3. **For sign / unit / convention failures**, check whether the spec pins the convention (Pattern 2). If yes → B1/B2/A3 (spec-pinned violation). If no but industry standard exists → A3.f. If no industry standard → C3.c task_side.
4. **Sanity check**: if the cell passes 90%+ of tests with a single failing schema-named test, suspect D1.a (vocabulary mismatch) before assuming an A-class formula error. Use the Asian-option case in `examples.md` Example 5 as the canonical pattern.

---

## Cross-references

- `examples.md` Example 5 — full worked example of the asian-option D1.a case
- `references/spec_citation_patterns.md` — the 8 inline-pin patterns
- `prompts/system_judge.md` § Spec-Citation Extraction Pre-check — v3.2 rule
- `INDUSTRY_STANDARDS.md` §A.7 — VaR/CVaR loss-space convention referenced in Pattern 2
- `INDUSTRY_STANDARDS.md` §A.2 — `ddof=1` industry default referenced in Pattern 3
- `CHANGELOG.md` — v3.2 / v3.2.1 entry summarizes when the pre-check + the 5 industry-standards sections were added.
