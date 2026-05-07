# QF-Bench Quantitative Correctness Failure Taxonomy

The 10 modes used by this skill (9 quant + 1 non-quant), grounded in 75+ real PR reviews on the QF-Bench repository plus the v10 batch analysis (May 2026). Each mode has the same shape:

- **Framing** — what the mode is and is not.
- **Decision Procedure** — numbered steps the judge follows.
- **Exclusions** — things that look like the mode but are not.
- **Sub-rubrics** — recurring sub-patterns within the mode (each tied to specific PRs).
- **Finance examples** — POSITIVE and NEGATIVE worked examples.

Every mode is independently judged. **A trial may (and often should) match more than one mode** — see "Independent vs cascading" below. The cascade rule collapses *symptoms of one root cause* into one match; it does NOT suppress *genuinely independent root causes*.

## High-level classes

| Class | Question | Modes |
|---|---|---|
| **A. Model & Formula** *(quant)* | What was computed? | A1 Wrong Model / Measure · A2 Missing or Extra Formula Term · A3 Wrong Parameterization / Convention Default |
| **B. Convention & Units** *(quant)* | How was it expressed? | B1 Unit / Scale Error · B2 Sign Convention Error · B3 Time / Date / Calendar Convention |
| **C. Data & Numerics** *(quant)* | How was it fed in / solved? | C1 Data Fabrication / Wrong Source · C2 Numerical / Optimization Failure · C3 Statistical Variant Mismatch |
| **D. Spec & Output Compliance** *(non-quant — orthogonal axis)* | Does the output match the spec's schema? | D1 Output Schema & Spec Compliance |

**Important:** Class D is the **non-quant axis** — it captures failures where the agent's quantitative content is correct but the *output format / schema / vocabulary* doesn't match what the verifier expects. Class D fires **independently of A/B/C** (orthogonal); a trial can match both D1 (wrong schema vocabulary) and A2 (missing formula term) simultaneously when both are present.

## Single-shot applicability (finance-zero)

Every mode applies to single-shot generated code. Unlike the trajectory skill, this taxonomy is purely about the math content, so all 9 modes are evaluated whether the agent ran multi-step or one-shot.

---

## Pre-flight gate: insufficient solution

Before any of the 9 mode rubrics run, `judge_trial.py` applies a deterministic
**insufficient-solution gate** to skip cases where there is literally nothing to
evaluate. This was added after the 50-trial validation found 60.8% of mode
judgments were spent on stub trials (agent code = imports + config + an
unfinished function signature) burning ~$0.20-$2.40 per trial × 9 modes to
have the LLM independently re-discover "no signal here" 9 times.

Gate criteria (must satisfy ALL three for a short-circuit):

1. `agent_code` non-whitespace length < 500 chars
2. `output_files` is empty (the trial produced no output the verifier could
   read)
3. `failing_tests` has zero entries with both `agent_value` and an
   `expected_value` / `expected_lo` / `expected_hi` (no numerical comparison
   signal)

When the gate fires, the trial gets a synthesized `labels.json` with all 9
modes set to `match: false`, `confidence: 1.0`, `gate_skipped: true`, and a
`notes` field explaining the deterministic skip and pointing to the
companion trajectory-error-analysis skill. **Cost:** $0.

The gate is intentionally conservative — it only catches Case 1 of the
system_judge prompt's "insufficient solution" three-case taxonomy (empty /
trivially short generation). Case 2 (code present, no outputs) still goes
through the LLM because the code's intent can often be classified from
line-level inspection.

**Empirical calibration on the 50-trial validation set:** gate fires on
24/49 trials (49%); 0 false positives (every trial that the LLM judge
matched against any of the 9 modes was correctly let through the gate).

**Aggregator handling:** the `gate_skipped` flag is preserved in
`labels.csv`. Aggregators should treat gate-skipped trials as a separate
bucket from real LLM-judged "no match" labels — the former tells you the
trial had no evaluable signal, the latter tells you the agent's solution
was sound on that axis. Lumping them together inflates the "agent's
solution was sound" count.

---

## Trajectory-failure sub-classification (when no quant content can be judged)

When `root_cause_class = insufficient` the trial has no evaluable quant content,
but **the reason matters** for downstream interpretation — one trajectory
failure can be the agent's fault, another can be infrastructure noise, a third
can be a known harness UX issue. The skill subdivides `insufficient` into
three sub-types, each with distinct treatment in aggregate reporting:

| Sub-type | Root-cause `class` | Counts as agent failure? | Excluded from quality score? |
|----------|---------------------|--------------------------|------------------------------|
| **`agent_engineering_weakness`** (Pattern A — wall-time / context overrun on intentional limits) | `agent_coding` | **Yes** (engineering signal) | **No** — counted as legitimate fail |
| **`agent_ux_bug`** (Pattern B — Plan-mode trap, ExitPlanMode misinterpretation, mode-management) | `agent_ux_bug` (NEW) | **Special** (flag for harness/UX feedback; counts toward agent score with caveat) | Track separately in reports |
| **`infra_failure`** (Pattern C — provider 429, container path mismatch, network) | `infra_failure` (NEW) | **No** (external) | **Yes** — exclude from agent quality score |

### Pattern A — Agent engineering weakness (wall-time / context overrun)

**Diagnostic signature:**
- Agent generated non-trivial code (often partial)
- Trial terminated by harness wall-clock or context-budget cap (`AgentTimeoutError`,
  exception_message: "execution timed out after 1800.0 seconds", or context-window
  exhaustion before any Write call)
- Inspection of agent's strategy reveals an **engineering choice** that caused
  the overrun: non-vectorized inner loop, naive `scipy.integrate.quad` per grid
  point instead of precompute-and-reuse, repeated reading of input files,
  excessive environment probing, debugging dead ends

**Why this is `agent_coding`, not `infra_failure`:**

The wall-clock and context-budget caps are **part of the task's difficulty
design**. Tasks like `stochvol-implied-surface-new` deliberately include
expensive grids that test whether the agent can write efficient code. An
agent that can't fit a Chiarella-Ziveyi pricer + IV inversion + Dupire local-vol
into 30 minutes of wall time has demonstrated **real engineering weakness**:
they didn't recognize the need for vectorization, didn't precompute the
characteristic-function on a shared grid, didn't cache intermediate quantities.
A capable agent would have produced output within the budget.

**Worked examples (QF-Bench v323):**
- `fb-v10-s45-stochvol-implied-surface-new` (sonnet 4.5 R1) — naive `scipy.quad`
  per (K, T, branch) → 288 quad calls per surface, hit 1800s wall before
  Step 3 (IV inversion) finished. **Label: `agent_coding`** with sub-rubric
  `agent_engineering_weakness`. The slow inner loop is the bug; the time
  limit is the test.
- `fb-v11-opus46-yield-curve-bond-immunization` (Opus 4.6 R1, R2) — burnt
  30-min budget on input-file reading and environment probing (4 Reads + 3
  Bash, zero Write calls before kill). Strategy choice (over-investigating
  before acting) is the bug. **Label: `agent_coding`**.

**What `notes` should record:**
"Agent self-induced budget exhaustion via [specific engineering choice].
A capable implementation would have completed within the [N-second / N-token]
budget. Counts as legitimate agent failure (Pattern A: engineering weakness)."

### Pattern B — Agent UX-design bug (Plan-mode trap)

**Diagnostic signature:**
- Agent enters Plan mode (Claude Code feature)
- Drafts a plan via `ExitPlanMode` tool call
- Harness rejects (no user to approve in non-interactive context)
- Agent treats rejection as a clarifying-question prompt → re-asks, exits, or
  loops on the plan rather than falling back to direct code execution
- Final result: zero output files, plan markdown sometimes saved to logs but
  no executable code ever written

**Why this is `agent_ux_bug`, not `agent_coding` or `agent_conceptual`:**

The agent's quant reasoning is **demonstrably correct** — the trial entries
show "complete and quant-correct plans" drafted (e.g., all 5 IV approximation
formulas with sanity-checked numerical values, FFT+MC plans for compound
Poisson). The failure is **mode-management**, specifically:
- Misreading harness's `ExitPlanMode` rejection as a user clarifying-question
  signal
- Treating Plan mode as a hard contract requiring approval before execution
- Failing to detect non-interactive benchmark context (no canary/OUTPUT_DIR
  cue translation into "skip planning, execute directly")

This is **not** a quant-skill failure (model knows the math) and **not** an
infrastructure failure (the API/provider is responding fine). It's a
specifically-Claude Code agent-UX bug that manifests in benchmark harnesses.

**Worked examples (QF-Bench v323):**
- 6 trials across 5 distinct tasks (`implied-vol-approximations` ×2,
  `compound-option-geske`, `merton-jump-diffusion`, `digital-barrier-options`,
  `fft-compound-poisson`) — all Claude Code variants (Haiku 4.5, Opus 4.6,
  Sonnet 4.5). Each agent drafted a complete and quant-correct plan, then
  failed to escape Plan mode.

**What `notes` should record:**
"Agent UX bug (Pattern B): Plan-mode trap. Agent drafted complete plan via
ExitPlanMode; harness rejected (non-interactive context); agent treated
rejection as clarifying-question and exited without executing. Quant
reasoning was correct; failure is in mode-management. Cross-reference for
Claude Code harness/UX feedback."

**Aggregator treatment:** count toward agent score *with explicit caveat* —
this signals a UX bug that should be fixed in Claude Code, not a model
capability gap. Best-of-N reporting may legitimately retry through the
trap and succeed on a later round.

### Pattern C — Infrastructure failure

**Diagnostic signature:**
- HTTP 429 from provider (Bedrock `ThrottlingException`,
  Anthropic-direct rate_limit_error, OpenAI rate-limit), or
- Container/volume path-isolation mismatch (agent writes files at path P;
  verifier reads from path P; verifier sees empty directory despite
  agent-side `ls -la` confirming files written), or
- Network errors, DNS failures, transient provider 5xx
- Critically: **the model never received the prompt** (for 429s), or the
  agent's outputs are correct but invisible to the verifier (for path
  mismatches)

**Why this is `infra_failure`, not `agent_coding`:**

The agent has no agency over whether the provider returns 200 vs 429, or
whether the harness mounts `/output` correctly across the agent and verifier
containers. These are **external** to the agent's behavior. Including
infra-failure trials in the quality score conflates infrastructure quality
with model quality.

**Worked examples (QF-Bench v323):**
- `fb-v10r2-h45-cme-hdd-option-pricing`, `fb-v10r2-h45-swap-curve-bootstrap-ois`
  — Bedrock 429 cascade across 10 retries → harness raised
  NonZeroAgentExitCodeError. Agent's reasoning was never invoked for the
  failed attempts. **Label: `infra_failure`**.
- `fb-v10-opus46-r2-hull-white-swaption` — agent's `ls -la $OUTPUT_DIR`
  showed all 7 expected files written; verifier (separate container view)
  saw empty `/output/`. Quant code was correct; container path-visibility
  bug. **Label: `infra_failure`**.

**What `notes` should record:**
"Infrastructure failure (Pattern C): [provider 429 / container path /
network error]. Agent's [reasoning was not invoked / outputs were
correct but invisible to verifier]. EXCLUDE from agent quality score —
this is a benchmark infrastructure quality signal, not a model capability
signal."

**Aggregator treatment:** **exclude** from per-model quality score.
Track separately as an `infra_failure_rate` metric — high rates indicate
benchmark plumbing issues (lower concurrency, increase retry budget, switch
provider routing) rather than model weakness.

### Decision flow

```
Failure has no evaluable quant content (no outputs, or outputs all wrong-shape)
  │
  ├── Was the agent's prompt invoked at all?
  │     │
  │     ├── No (provider 429, network error)              → infra_failure (Pattern C)
  │     └── Yes
  │           │
  │           ├── Did agent enter Plan mode and never escape?
  │           │     │   (drafted complete plan, ExitPlanMode rejected,
  │           │     │    no Write/Bash for actual code)
  │           │     └── YES                              → agent_ux_bug (Pattern B)
  │           │
  │           ├── Did agent run code that was correct, but verifier
  │           │   couldn't see outputs (container path mismatch)?
  │           │     └── YES                              → infra_failure (Pattern C)
  │           │
  │           └── Did agent run code that was inefficient and hit
  │               wall-clock or context-budget cap?
  │                 └── YES                              → agent_coding (Pattern A)
  │
  └── Otherwise (agent generated 0 chars, or pure pre-flight gate)
        → keep generic `insufficient` label
```

### Why this matters for benchmark reporting

Without sub-classification, "insufficient = trajectory failure" lumps
together three very different signals:
1. The agent is engineering-weak (Pattern A, valid signal)
2. Claude Code has a Plan-mode UX bug (Pattern B, fixable in harness)
3. AWS Bedrock throttled (Pattern C, fixable in infrastructure)

A model-capability score that treats all three identically is misleading.
The v3.2.6 sub-classification preserves the right interpretation in the
aggregate report.

---

## Pre-check: who authored the formula? (applies to Class A)

**Before matching A1, A2, or A3** when the agent's formula appears wrong, identify the authorship of the formula expectation. There are three cases — the right mode depends on which one applies:

### Case 1 — Spec-authored

The instruction explicitly writes the formula OR cites a specific paper / book / textbook section that defines the method. Examples: `instruction.md` contains `L = Σ[log f_t(z_t; ν) − ½ log σ²_t]` verbatim; or "use the Reiner-Rubinstein 1991 closed-form for down-and-out barrier calls"; or "Compute the Gibbons-Ross-Shanken (1989) test statistic"; or "follow the Bandi-Russell (2006) realized vol estimator."

→ The agent **must follow that exact formula / paper**. Deviations — even to mathematically-equivalent reformulations or "more modern" textbook variants — are **NOT acceptable**. The agent has been told which source to follow; choosing a different source (Hayashi rewriting GRS 1989, McNeil reproducing Acerbi-Tasche, etc.) is a violation of an explicit directive.

→ Classify deviations as **A1 / A2 / A3**, NOT C3.a.

→ If the deviation produces only a small numerical drift (e.g., 0.5% from a different small-sample correction in an equivalent form), that's still A2 or A3 — *not* a "tolerance issue" to be downgraded to C3 or pushed to qf-bench-review. The agent failed to follow the cited paper.

→ The C3.a "named method with multiple defensible variants" routing **does NOT apply when a specific paper is cited**. C3.a is for Case 2 only (canonical method named without a paper).

### Case 2 — Canonical / well-known model

The instruction names a classical model that any working quant is expected to know without further reference. Non-exhaustive list (these have a *unique* canonical form):

- **Pricing:** Black-Scholes 1973, Black '76, Merton 1973, Bachelier, put-call parity
- **IR / term-structure:** Vasicek 1977, CIR 1985, Hull-White 1F/2F 1990, BDT, HJM 1992, LMM (Brace-Gatarek-Musiela 1997)
- **Local / stoch vol:** Dupire 1994, Heston 1993
- **Jumps:** Merton 1976 jump diffusion (with the standard "λ\* = λ, μ\_J\* = μ\_J" risk-neutral choice if not stated otherwise)
- **Trees / PDE:** Cox-Ross-Rubinstein 1979, Jarrow-Rudd, trinomial Hull-White, Crank-Nicolson, PSOR for American free boundary
- **Barriers:** Reiner-Rubinstein 1991 closed-form for single-barrier European
- **American:** Brennan-Schwartz, Bensoussan-Lions, smooth-pasting condition
- **MLE / likelihood:** Gaussian / Student-t log-density (with proper Jacobian under standardization), AR(1) likelihood, GARCH(1,1) likelihood (Bollerslev 1986)
- **Greeks:** pathwise (Broadie-Glasserman 1996), likelihood-ratio score functions
- **Risk:** parametric Gaussian VaR, historical VaR, Cornish-Fisher expansion, ES via tail integral, Euler decomposition, modified duration / convexity, DV01 = duration × dirty price / 10000

→ The agent is expected to know the formula. **A1 / A2 / A3 apply normally.**

**Caveat — named method with multiple variants (Case 2 ONLY).** If the named method is well-known but has multiple defensible variants in the literature (Newey-West NW87 vs NW94, Corrado 1989 vs Corrado-Zivney 1992, threshold ES vs Acerbi-Tasche, VECM half-life formulas, IV approximations Brenner-Subrahmanyam vs Li 2005 vs CMH), AND no specific paper has been cited, this is **C3.a** (named-method variants), not A1/A2/A3.

**This caveat does NOT extend to Case 1.** If a specific paper is cited (e.g., "use Newey-West 1994 bandwidth `floor(4·(T/100)^{2/9})`"), the variant has been pinned and the agent must use it. A deviation to NW87 would be A2/A3, not C3.a.

### Case 3 — Agent-invented under under-specified spec

The instruction names a *procedural goal* (e.g., "parametric VaR decomposition", "Greek-based stress test", "factor-neutral hedge", "shrinkage estimator") but does NOT pin a specific formula AND multiple defensible formulas exist. The reference oracle pins one specific implementation; the agent invents a different one.

→ **Do NOT auto-match A1 / A2 / A3** just because the agent's invented formula differs from the reference's. Instead:
- If the agent's formula is *dimensionally consistent and defensible* under any standard interpretation → **match C3.c** (non-canonical reference variant / inverse trap), and flag the task-design issue (spec should pin the formula or widen tolerance) for the companion `qf-bench-review` skill.
- If the agent's formula is *also dimensionally inconsistent* or has an obvious construction error within their invented framework → **match A2** (missing term in self-invented formula) **and note in `notes` that the upstream cause is task-side under-specification.**

In well-designed QF-Bench tasks, Cases 1 and 2 should dominate. Case 3 is a yellow flag for task quality.

### Quick decision flow

```
Agent's formula is wrong. Was the formula expectation:
├── Case 1 (spec wrote it / spec cited a specific paper) → match A1/A2/A3 normally
├── Case 2 (canonical, unique form, any quant should know) → match A1/A2/A3 normally
│   └── if named method has multiple variants → match C3.a instead
└── Case 3 (agent invented under under-specified spec) →
    ├── agent's formula defensible & dimensionally consistent → match C3.c
    │   └── BUT see "Mathematical equivalence ≠ literal compliance" sub-rule below
    └── agent's formula dimensionally broken → match A2 + flag task-side issue
```

### Sub-rule: "Mathematical equivalence ≠ literal compliance" (added v3.2.11)

When the spec describes a procedure with multiple **mathematically-equivalent implementations** that consume RNG state, evaluate floating-point in different orders, or take different code paths to produce the same final distribution, the agent must follow the **literal reading** of the spec procedure. Mathematical shortcuts that bypass the literal procedure are **A3.f / agent_conceptual**, NOT C3.c / task_side.

**Diagnostic — the shortcut signature:**

The agent's code is "mathematically equivalent" to the spec's procedure but:
- Uses fewer RNG calls (e.g., `z * scales` instead of separate per-component draws)
- Replaces an explicit loop with a vectorized identity
- Substitutes an analytic equivalent for a Monte-Carlo simulation when both are valid
- Uses a closed-form transform of one sample to "be" multiple samples (e.g., `N(0,9) = 3·N(0,1)`)

These produce the same *distribution* but a different *concrete sample sequence* under a shared RNG seed. When the test pins specific numeric outputs (RMSE values, point estimates, comparisons), the difference cascades into the failed assertion.

**Two strong signals that a "shortcut" is `A3.f`, not `C3.c`:**

1. **Test pins specific numeric values** (e.g., `assert RMSE_close_to(0.1036, rtol=0.10)`) rather than **shape invariants** (e.g., `assert RMSE > 0`, `assert RMSE_in_band(0.05, 0.15)`). Pinned numerics mean the maintainer ran a canonical implementation and pinned ITS output. Deviating to a mathematical equivalent breaks the canonical implementation; the maintainer had ONE recipe in mind.

2. **The spec uses verbs like "draw from", "sample from", "select", "compute"** with explicit subjects. Each verb has a literal reading that determines the canonical execution path. The agent's vectorized identity bypasses the literal procedure.

**Conversely, C3.c / task_side genuinely fits when ALL hold:**

- Tests use shape invariants only (`positive`, `in_band`, `ratio_close_to_one`, `monotonic`, etc.)
- Spec literally describes a *goal* without a procedure (e.g., "compute the alpha" without naming a regression form)
- Multiple non-equivalent procedures exist (e.g., OLS vs robust regression vs IV)
- No maintainer-implied default (e.g., no canonical reference in the literature for this combination)

**Worked example (var-es-estimation v323/v12 audit):**

Spec L22: *"Implementation: generate N uniform draws to decide the component, then draw from the selected component accordingly."*

| Reading | Implementation | RNG calls | RMSE produced |
|---|---|---|---|
| **Literal** ("draw from N(0,9) when selected") | `np.where(u<p, draws_high, draws_low)` with two N(0,·) draws | 3 | matches test pin `0.1036` |
| **Shortcut** (`N(0,9) = 3·N(0,1)`) | `z * scales` with one N(0,1) draw | 2 | `0.0899` — fails the pin |

Test pins `RMSE = 0.1036` (specific numeric, not a band). Spec uses verb "draw from the selected component." Both diagnostic signals indicate the maintainer had the literal 3-RNG-call implementation in mind. **Verdict: A3.f / agent_conceptual** ("agent took a math-equivalence shortcut that bypassed the literal spec procedure"), NOT C3.c / task_side.

This sub-rule was added after a v12 audit re-judge (May 6 2026) where strict literal application of "spec doesn't pin → C3.c" routed 3 var-es-estimation Opus 4.7 trials to task_side. The literal reading + pinned-test signal both indicated A3.f. The mis-routing was caught by manual review — this sub-rule encodes the lesson so future sub-agents apply the right discriminator automatically.

---

## Localized vs systematic — coding bug vs conceptual error

After matching a mode at the symptom level, **always run this diagnostic** to determine the root cause class. The mode label captures what the *output* looks wrong about; this diagnostic captures *why*.

For a matched mode, look at the broader pattern:

| Indicator | Localized (likely coding bug) | Systematic (likely conceptual error) |
|---|---|---|
| Scope of failure | One specific (object × method × parameter) combination | Multiple related computations affected |
| Companion checks | Sibling computations (same method, different object; same object, different method) all pass | Sibling computations also fail with related root cause |
| Magnitude | Magnitude correct, only sign/small term off | Magnitude or structure off across related outputs |
| Downstream | Cascade is short (1–2 tests) | Cascade is wide (many tests, often whole pipeline) |
| Reasoning-vs-code | Agent's stated method/intent in the trajectory was correct; only the code in one spot diverges | Agent's stated method/intent was already off |

**Examples:**

| Pattern | Localized? | Right classification |
|---|---|---|
| Only `pw_put_delta` has wrong sign; pw_call_delta, fd_put_delta, lr_put_delta, asian_pw_put_delta all correct | **Localized** | B2 at symptom level; root cause = `agent_coding` (likely copy-paste-without-sign-flip). Cross-ref trajectory skill: Reasoning–Action Mismatch. |
| All Greek estimators, all option types, all methods have the wrong sign on the discount factor | **Systematic** | A2.a missing transformation term; root cause = `agent_conceptual`. The agent doesn't understand discounting. |
| GARCH ν pinned at 100 in every fit; spec is fine but agent's likelihood formula is missing the Jacobian | **Systematic** | A2.a missing Jacobian; root cause = `agent_conceptual`. |
| Single test off by 0.5% from a paper-cited formula deviation | Either | A2/A3 at symptom; root cause = `agent_conceptual` (deliberately picked a different reformulation). Could also be `task_side` if instruction is ambiguous. |
| Reference oracle has a known bug; agent's correct math fails the test | (n/a) | match: false; root cause = `task_side`. |

**Output convention.** When emitting the labels JSON for a matched mode, include a top-level `root_cause_class` field with one of:

- `agent_conceptual` — agent doesn't understand the underlying finance / math (systematic; the failure mode reflects a real knowledge gap)
- `agent_coding` — agent has the concept right but a localized implementation bug (typo, copy-paste, off-by-one, sign-flip in one branch). Cross-ref trajectory skill's Reasoning–Action Mismatch.
- `task_side` — task spec is under-specified, oracle has a bug, or test tolerance is too tight; the agent's quant content is defensible. Cross-ref `qf-bench-review`.

When `root_cause_class = agent_coding` or `task_side`, the symptom-level mode match is still valid (the output IS wrong), but downstream consumers should know the root cause lives outside the agent's finance-content reasoning. This avoids over-attributing benchmark failures to "the model lacks finance knowledge" when the actual issue is implementation reliability or task design.

---

## A. Model & Formula

### A1. Wrong Model / Measure

**Framing.** The agent implements a different mathematical model than the task specifies, or prices/computes under the wrong measure. The math is *internally correct* but not the math that was asked for. Includes "right concept, wrong family" (e.g., Black-Scholes when CEV mandated; rough Heston when rBergomi mandated). Also includes diagnostic substitutes: checking calendar arbitrage at a single ATM point when the task requires a full Gatheral log-moneyness sweep is a wrong-model match because the diagnostic itself is the wrong mathematical object.

**Decision Procedure.**
0. **Authorship pre-check.** Run the "Who authored the formula?" check (above). For Case 3 (agent invented the model under under-specified spec), prefer C3.c. For Cases 1 / 2, proceed.
1. Identify the model/method/measure stated in `instruction.md`. If none is named, no match.
2. Identify what the agent's code actually implements. Look at the imports, the closed-form, the SDE discretization, the tree branching, the integration domain.
3. If the agent's implementation differs from the spec on a *modeling* axis (different model class, different measure, different diagnostic), match.
4. Distinguish from A2: *missing a term* in the right model = A2; *implementing the wrong model* = A1.
5. Distinguish from A3: *wrong parameterization* of the right model = A3; *wrong model entirely* = A1.

**Exclusions.**
- Implementing the right model with a wrong scalar coefficient (that's A2).
- Using a non-canonical method variant when the spec didn't pin the variant (that's C3).
- Right model, wrong sign (that's B2).

**Sub-rubrics.**
- **A1.a — Model substitution.** Black-Scholes when CEV / Heston / Bates required; plain GARCH when GARCH-t required; OU when geometric mean-reversion required.
- **A1.b — Measure confusion.** Pricing under physical measure (μ) when risk-neutral (r − q) is required. Using real-world drift in option pricing.
- **A1.c — Diagnostic at single point vs full sweep.** Calendar arbitrage `∂_T w(k,T) ≥ 0` checked at single ATM strike instead of across log-moneyness range. The single-point check is a *different mathematical statement* from the full no-arbitrage condition. (PR #164 dupire-local-vol)
- **A1.d — Structural deviation: claims the model in name/notation but the implementation isn't that model.** *(50-trial validation: hull-white-swaption Haiku-4.5.)* A model is a specific mathematical structure, not just a name. When the agent uses the model's notation (`a, σ, θ(t)` for HW) but the actual implementation deviates on **two or more** structural axes — (1) state-equation/SDE structure, (2) lattice/grid construction specific to the model, (3) calibration procedure required by the model, (4) probability/weight construction specific to the model, (5) boundary conditions specific to the model — the implementation is not the named model. Use of the model's symbols alone does not launder a generic numerical method into the named model. Distinguish from A2: 0–1 structural deviation = A2 (right model, missing piece); 2+ deviations = A1.d (wrong model class). Example: HW trinomial tree built with `dt = 0.5` not `1/12`, `Δx = σ√Δt` not `σ√(3·Δt)`, constant `(0.25, 0.5, 0.25)` probabilities not drift-dependent, no Arrow-Debreu α_n calibration → 4 axes wrong → match A1.d.

**Finance examples.**

POSITIVE — Task: "Price American option via CRR binomial tree." Agent uses Jarrow-Rudd parameters (`u = exp((r−q−σ²/2)Δt + σ√Δt)`) instead of CRR (`u = exp(σ√Δt)`). Different model, different numbers → match A1.a.

POSITIVE — Task: "Use Gatheral calendar-arbitrage diagnostic across log-moneyness." Agent's `forward_variance.csv` has a single row per maturity (ATM only). The diagnostic at one point is mathematically distinct from the full surface check → match A1.c.

NEGATIVE — Task: "Use Hull-White 1F." Agent correctly implements Hull-White but forgets the convexity-adjustment term in caplet pricing. That's missing a term → A2, not A1.

---

### A2. Missing or Extra Formula Term

**Framing.** The agent uses the right model but the formula is missing a required term or includes a spurious one. Includes Jacobian/measure-change terms in MLE objectives, Itô/martingale corrections in exponential SDE discretization, discount factors omitted or applied twice, boundary-condition terms in PDE schemes, and component contributions in composite quantities (e.g., FX vol in compo option vol).

**Decision Procedure.**
0. **Authorship pre-check.** Run the "Who authored the formula?" check (above). If Case 3 (agent-invented under under-specified spec), prefer C3.c match unless the agent's invented formula is itself dimensionally broken. If Case 1 or Case 2, proceed.
1. Identify the formula the task asks for, term-by-term. If the formula is implicit (the task names a Case 2 canonical model without writing the formula), use the canonical derivation.
2. Compare against the agent's implementation. Look for: missing additive terms, missing multiplicative factors, missing summands in composite expressions.
3. If a required term is absent (or a spurious one is present) and it materially affects the output, match.
4. Distinguish from A1: *wrong overall model* = A1; *right model, missing term* = A2.

**Exclusions.**
- The "missing" term is conventionally negligible at the parameter scale (e.g., second-order term in a leading-order expansion) and the agent's claim is appropriately narrowed.
- Format-only omissions (e.g., reporting precision) — not material.

**Sub-rubrics.**
- **A2.a — Transformation term missing.** Jacobian missing in change of variables (e.g., `−log(scale)` in t-likelihood with location-scale standardization, PR #208 `garch-sp500-fit`). Itô correction `−½η²t^{2H}` missing in exponential variance process (rBergomi). Discount factor missing or applied twice (chooser option, PR #158). **Pathwise / likelihood-ratio Greek estimators with missing chain-rule term.** *(Canonical reference: Haugh 2017 IEOR E4703 Eq. 9, citing Glasserman 2004 Ch. 7.)* Under GBM `S_T = S_0·exp((r−σ²/2)T + σ√T·Z)`, the pathwise chain rule for vega is `∂S_T/∂σ = S_T·(Z√T − σT)`. **Both the `Z√T` (diffusion derivative) and `−σT` (convexity-correction derivative) terms appear in the canonical formula**; neither is "absorbed by discounting." The full pathwise vega for a European call is `e^{−rT}·1{S_T>K}·S_T·(Z√T − σT)`. Common agent bugs: drop the `−σT` term, insert a spurious `1/σ` factor (writing `(Z√T − σT)/σ`), or substitute `√dt` for `√T`. (50-trial validation: 3 trials in mc-greek-surface family.)
- **A2.b — Composite-quantity missing constituent.** Compo option vol uses `σ_S` only, dropping `σ_X` and `2ρσ_Sσ_X` cross-term (PR #166 `fx-quanto-options`). Multi-factor portfolio variance uses only diagonal of Σ. Cross-currency forward uses only one rate.
- **A2.c — Likelihood / AIC across different sample sizes.** OU model NLL on n−1 obs while martingale/GBM/Merton use n obs → AIC comparison invalid (PR #137 `multimodal-alpha-fusion`). Add the log-marginal of the dropped observation under the OU stationary distribution.
- **A2.d — Greek not available for chosen method.** Pathwise gamma is null because the indicator function is non-differentiable. LR theta is null because the time score is complex. Reporting a non-null value here is "extra term." (PR #28 `mc-greek-surface-1`)
- **A2.e — Extra term double-counted.** Entry transaction cost subtracted at trade entry AND again in the realized P&L formula at exit (PR #61 `pairs-trading-cointegration`). Cost applied 3× round-trip instead of 2×.
- **A2.f — Region / boundary identification missing constraint guard.** When computing a *derived* quantity by scanning a domain — exercise boundary `S*(t)`, support of an arbitrage-free vol surface, root in implied-vol inversion, threshold in regime detection — the financially-meaningful constraint must be checked explicitly. Example: for an American put, the exercise boundary `S*(t)` is "the largest `S` where `V(S) = payoff(S)`" *AND* `payoff(S) > 0`. Scanning from high `S` downward without the second guard picks the deep-OTM zone (where both `V ≈ 0` and `payoff = 0`) trivially, and reports `S* = S_max` for every `t`. The detection formula needs the guard `payoff > 0` (or equivalently, scan only over the in-the-money domain). Same pattern: implied-vol Newton-Raphson without a "price > intrinsic value" guard converges to spurious roots; arbitrage-region detection without a "price > lower bound" guard mis-identifies the boundary. (PR `american-option-fd-new` Haiku 4.5 trial: scan picked `i = N_S = 300` at every time step → `exercise_boundary_at_T = 300.0`.)
- **A2.g — Wrong coefficient in canonical ODE / characteristic function.** *(50-trial validation: 4 trials.)* The agent uses the right model and the right structural form but a sign or scale factor inside the canonical formula is wrong. Distinguish from A2.a: A2.a is "term zero" (missing); A2.g is "term present but coefficient wrong."
  - **Heston / two-factor Heston Riccati `d` (Heston 1993 Eq. 6).** `d_j = sqrt((ρσi·φ − b_j)² − σ²·(2u_j·i·φ − φ²))` with `(b_2, u_2) = (κ, −1/2)` for P_2 and `(b_1, u_1) = (κ−ρσ, +1/2)` for P_1. Substituted: P_2 → `sqrt((κ − ρσi·φ)² + σ²·(i·φ + φ²))`; P_1 → `sqrt((κ − ρσ − ρσi·φ)² − σ²·(i·φ − φ²))`. Agents drop the `i·φ` linear term, sign-flip `(2u·i·φ − φ²)`, or apply the same `d` to both branches. Symptom: NaN implied vols, ATM IV way off (3.12 vs 0.279), 41/144 strikes returning negative call prices.
  - **Hull-White 1F log-bond-price variance correction.** Canonical (Brigo-Mercurio textbook): `log A(t,T) = log[P(0,T)/P(0,t)] + B(t,T)·f(0,t) − (σ²/(4a))·(1 − e^{−2at})·B(t,T)²` with `B(t,T) = (1 − e^{−a(T−t)})/a`. The variance correction is `(σ²/(4a))·(1 − e^{−2at})·B(t,T)²` — note `4a` in denominator. Agents commonly write it with `2a` (off by factor 2) or drop the `(1 − e^{−2at})` factor (treating variance as if it grew linearly in time when it saturates due to mean reversion). Bond prices off by uniform 2–6% across the curve.
- **A2.h — Silent approximation abuse (sub-case extension).** *(50-trial validation: 1 direct hit, well-documented in reviewer post-mortems.)* The agent uses a method that is exact only in a restricted sub-case and silently applies it to the full case. Canonical example: escrowed-dividend `S_adj = S − PV(future divs)` is exact for **European** options on a stock with discrete dividends; applying the same construction to **American** options is wrong because the early-exercise condition `V ≥ payoff(S, t)` lives in the original `S`, not `S_adj`. Other family members: closed-form GBM Asian-Geometric used as a control variate without the GBM correction; lognormal IV inversion applied to a normal-vol-quoted price; flat-vol BS Greeks reported as "model" Greeks under a skew model. Match when (a) the method is named-correct for sub-case X, (b) the spec asks for the full case, (c) no projection / boundary / correction step in the code lifts X-only to full-case validity.

**Finance examples.**

POSITIVE — Task GARCH-t MLE: instruction's Step 3 likelihood is `L = Σ[log f_t(z_t; ν) − ½ log σ²_t]` with `z_t = X_t / σ_t`. Reference solution actually uses `z = X / (σ·scale)` with `scale = sqrt((ν−2)/ν)` and `L = Σ[logpdf(z, ν) − log(σ) − log(scale)]`. Agent follows the instruction literally — omits `−log(scale)` Jacobian. ν → 100 (upper bound). Match A2.a.

POSITIVE — Compo option pricing: agent uses `σ_S` in d1/d2 instead of `√(σ_S² + σ_X² + 2ρ σ_S σ_X)`. With ρ=0 and σ_X > 0, compo option price equals quanto, but financially compo should be strictly larger. Match A2.b.

POSITIVE — American put exercise-boundary detection: agent's loop is `for i in range(N_S, 0, -1): if V[i, n] - payoff[i] <= EXERCISE_TOL: boundary[n] = S[i]; break`. For a put, `payoff(S) = max(K-S, 0) = 0` for `S > K = 100`. Wherever the PDE has decayed `V` to ≈ 0 (whether due to a separate PDE bug or just deep-OTM), `V − payoff = 0` is satisfied trivially in the entire `S > K` zone. The scan picks `i = N_S = 300` immediately, reports `S*(T) = 300.0` for every `t`. Missing guard: `payoff[i] > 0`. Match A2.f.

NEGATIVE — Agent uses Black-Scholes when the task says Black-Scholes. d1, d2, BS price all correct. No match — and if anything were off, it would be A1 (wrong model) or B2 (sign), not A2.

---

### A3. Wrong Parameterization / Convention Default

**Framing.** Same formula symbol, different definition. The agent reads "σ_k" or "Sharpe" or "ATM" or "weights" and resolves it to a convention different from the one the test pins. Includes distribution parameterization (Gamma shape vs scale, Student-t standard vs standardized), proprietary/institutional convention defaults (Barra USE4 sqrt-mcap weighting, Engle DCC Q̄), metric definition conventions (Sharpe excess vs raw, ATM spot vs forward, factor-vs-total variance denominator, annualization basis), and backtest state-tracking (target vs drifted weights).

**Decision Procedure.**
0. **Authorship pre-check.** Run the "Who authored the formula?" check (above). For Case 3 (agent invented the parameterization under under-specified spec), prefer C3.c. For Cases 1 / 2, proceed.
1. Identify the parameter or metric whose definition could resolve to multiple conventions in standard finance literature.
2. Check what the task's instruction actually states (often: only the symbol name). Check what the test pins (often: a specific numerical convention).
3. Identify what the agent's code resolves it to. Two correct readings producing different numbers = ambiguity; the agent picking the non-test-aligned reading = match.
4. Distinguish from A1: A1 changes the *model class*; A3 keeps the model and changes a *parameter definition*.
5. Distinguish from C3: C3 is *named-method variants* (Newey-West 1987 vs 1994); A3 is *parameter-definition variants* (σ_k = std vs CV).

**Exclusions.**
- Wrong numeric value of a well-defined parameter (that's a code error, not a convention error).
- Pure unit-scale (decimal vs percent, that's B1).
- Methodological variants of a named method (that's C3).

**Sub-rubrics.**
- **A3.a — Distribution parameterization.** Gamma `(α, β)`: shape & rate vs shape & scale. Student-t: standard `t(ν)` (variance = ν/(ν−2)) vs standardized (variance = 1, scale = `sqrt((ν−2)/ν)`). Negative binomial: failures vs trials. (PR #195 σ_k = std vs σ_k = CV in CreditRisk+; instruction line 29 `Var(S_k)=σ_k²/μ_k²` was the CV reading; reference uses `Var(S_k)=σ_k²` std reading.)
- **A3.b — Proprietary / institutional convention default.** Barra USE4: sqrt-market-cap weighting (not linear-mcap, not equal); double-pass standardization; OLS-style t-stat (not HAC); Taylor-approximation EWMA `λ = 1 − ln(2)/halflife`. Engle (2002) DCC: `Q̄ = (1/T) Σ z_t z_t'` (sample 2nd moment) vs `np.corrcoef` (demeaned correlation). LLM training data covers conceptual layer but not vendor-handbook details. (PR #120 barra-cne6-risk; PR #86 dcc-garch.)
- **A3.c — Metric definition convention.** Sharpe ratio: excess return `(r − r_f)/σ` vs raw `r/σ`. ATM: spot `K = S₀` vs forward `K = F_T = S₀·e^{(r−q)T}`. Factor-vs-total variance denominator (`style_pct + industry_pct = 1` vs `= factor_pct`, PR #122 barra-cne6-risk). Annualization basis: `(1+r)^(252/N)−1` where N = trading days with position vs total trading days (PR #61 pairs-trading-cointegration). Return-frequency: `r_monthly = r_annual/12` (simple) vs `(1+r_annual)^(1/12)−1` (compound) (PR #66 portfolio-risk-attribution).
- **A3.d — Backtest state-tracking convention.** Between rebalances, does the portfolio track *target weights* (held constant, no drift) or *actual weights* (drifted by daily returns, snapped back at rebalance)? Same for `w_old` in turnover: previous target vs current drifted weight. Both defensible. (PR #133 shrinkage-meanvar-portfolio.)

**Finance examples.**

POSITIVE — CreditRisk+ task: instruction uses σ_k as "volatility of default rate" but writes line 29 `Var(S_k) = σ_k²/μ_k²`. Tests use `Var = σ_k²` (std reading). Agent follows the line-29 formula literally → wrong Gamma shape, systematically low VaR (5.9 vs 6.5). Match A3.a.

POSITIVE — Multi-factor risk task: instruction says "All `*_pct` are fractions of total variance, with style/industry split referring to contributions to the factor variance component." Agent reads "split refers to factor variance" → produces `style_pct + industry_pct = 1`. Test expects `style_pct + industry_pct = factor_pct` (denominator = total variance). Match A3.c.

NEGATIVE — Task: "Compute Sharpe with `r_f = 0`." Agent does `r/σ` and the test compares against the same. No convention mismatch. No match.

---

## B. Convention & Units

### B1. Unit / Scale Error

**Framing.** The math is right, but the answer is on the wrong scale: percent vs decimal, basis points vs decimal, annualized vs daily, dollars vs notional. The agent's number is off by a clean factor (×100, ×10000, ×252, ×√252) or has the wrong sentinel (NaN where 0 expected, Infinity where null expected).

**Decision Procedure.**
1. For each failing test, compute `ratio = agent_value / expected_value`.
2. If the ratio is approximately one of: 100, 0.01, 10000, 0.0001, 252, √252, 365, ½ — the failure is a unit/scale error. Match.
3. Verify by checking the agent's code: does it report the quantity in the wrong unit (e.g., var_explained as 86.32 instead of 0.8632)? Does it apply or omit a scaling factor?
4. Distinguish from B2: sign error gives ratio ≈ −1, not 100×.
5. Distinguish from B3: time-conversion conventions (`r/n` vs `(1+r)^(1/n)−1`) live in B3.

**Exclusions.**
- Unit confusion that's actually a sign issue (B2).
- Compounding/day-count convention (B3).
- Rounding precision differences within tolerance.

**Sub-rubrics.**
- **B1.a — Percent vs decimal.** `var_explained` stored as 86.32 instead of 0.8632 (PR #183 pca-yield-curve). `carry_signal` as 4.8 instead of 0.048 (PR #78 fx-carry-trade-backtest). Returns or rates as percent points instead of decimal fractions.
- **B1.b — Basis points vs decimal.** Yield changes: 5 bps vs 0.0005. DV01 scaling: dollars vs basis points exposure.
- **B1.c — Annualization factor.** Daily vol × √252 vs × √365 vs unscaled. Daily Sharpe scaled by √252 vs not.
- **B1.d — Sentinel value mismatch.** NaN where the spec expected 0, or vice versa (PR #106 etf-overlap: NaN for `implied_price` when not held vs zero for `shares_held`). `null` vs `Infinity` for undefined ratios (PR #132 dirty-gap-momentum: `profit_factor` when `gross_loss = 0`). NaN replaced by 0 conflicts with `assert not np.any(arr == 0)` test (PR #23 stochvol).
- **B1.e — Greeks unit-convention drift across estimators.** *(50-trial validation: 4 trials in mc-greek-surface family.)* Greeks have multiple in-use conventions: vega "per absolute σ unit" vs "per 1% σ change" (100× apart), rho "per absolute r" vs "per 1bp" (10000× apart). When the agent computes the same Greek by 2+ methods (FD, pathwise, LR, BS analytical) and the answers land 100× apart from each other within the agent's own output, this is B1.e. Look for `/ 100.0` or `* 100.0` applied unevenly across the Greek paths. **Distinguish from A2.a:** if the formulas are mathematically identical and only the unit scaling is inconsistent, B1.e. If one estimator is missing the chain-rule term entirely (`dS_T/dσ`), that's A2.a — the units happen to be wrong because the formula is wrong.

**Finance examples.**

POSITIVE — PCA yield curve: instruction's output schema says `eigenvalues.csv` has columns `pc, eigenvalue, var_explained, cumulative_var_explained`. Test asserts `var_explained[0] ≈ 0.8632`. Agent stores `86.32`. Ratio = 100. Match B1.a.

POSITIVE — `profit_factor` when there are no losing trades: agent stores `0.0`. Spec wants `null`. Reference uses `float("inf")` but `json.dump(Infinity)` produces invalid JSON, so eventually settles on `null`. Agent's `0` is materially wrong (zero profit factor implies all losses, the opposite of what the data says). Match B1.d.

NEGATIVE — Test expects `0.5` for a probability, agent returns `0.5000003`. Within numerical tolerance, no match.

---

### B2. Sign Convention Error

**Framing.** The magnitude is right but the sign is wrong. Includes loss-vs-P&L convention, ξ vs −ξ in heavy-tail parameters across software ecosystems, long vs short weight signs, lag-direction in lead-lag asymmetry, and eigenvector / factor-rotation sign indeterminacy in PCA.

**Decision Procedure.**
1. For each failing test, compute `ratio = agent_value / expected_value`.
2. If ratio ≈ −1 across one or more tests, sign convention is the leading hypothesis.
3. Check the agent's code for: drift sign, residual sign, log-likelihood gradient sign, P&L sign convention (long position negative when short).
4. For PCA / factor rotations: eigenvectors have inherent sign indeterminacy. The instruction must specify a sign-fixing rule; if not, the agent's sign may flip but the expected value is fixed.
5. Distinguish from B1: scale errors are |ratio| ≠ 1; sign errors are ratio ≈ −1 with same magnitude.

**Exclusions.**
- Pure scale (B1).
- Sign error that's actually a different *model* (e.g., long-call vs short-call payoff is A1).

**Sub-rubrics.**
- **B2.a — Shape parameter sign across ecosystems.** GPD shape: scipy `genpareto` uses `c = +ξ` (heavy tail = positive); R's `ismev` package (Coles textbook) uses `k = −ξ` (heavy tail = negative). Modern EVT (McNeil/Frey/Embrechts) agrees with scipy. Agents trained on R-flavored references can produce sign-flipped fits. (PR #186 pot-gpd-bitcoin — empirically verified scipy returns c = +0.25 for true ξ = +0.3.)
- **B2.b — Loss vs P&L convention.** VaR conventionally positive (loss). Returns conventionally as profit (gain positive). Agent flipping these breaks VaR > 0 and ES ≥ VaR consistency.
- **B2.c — Long vs short weight sign.** Short positions: negative weight or positive exposure with side flag? PnL on short leg in pairs trading: drift signs reversed. (PR #124 pairs-cointegration-kalman: PnL sign reversed on mean-reversion direction.)
- **B2.d — Lag direction / lead-lag asymmetry.** "If A leads B" is asymmetry > 0 with leader=A. The slice formula `corr(A[0:n−k], B[k:n])` is `corr(A_t, B_{t+k})` (so positive k means A leads B). Agents flip this and produce sign-inverted leader/lagger labels. (PR #128 etf-cross-asset-lead-lag.)
- **B2.e — Eigenvector / factor rotation sign indeterminacy.** PCA eigenvectors have free signs. PC2 sign-fixing heuristic `if np.sum(vec) < 0: flip` is unstable for PC2 (sum near zero). Without explicit sign-fixing rule, factors come out sign-flipped, downstream metrics like Sharpe with flipped sign. (PR #72 treasury-curve-pca-butterfly; PR #123 ipca-latent-factors.)

**Finance examples.**

POSITIVE — IPCA factor extraction: eigendecomposition leaves eigenvector signs undetermined. Reference uses an implicit anchor (largest-loading positive). Agent uses `if vec[0] < 0: flip`. Factors 1 and 3 come out with opposite signs → Sharpe ratios with flipped signs → tests fail. Match B2.e.

POSITIVE — GPD fit: scipy returns c = +0.30 for the bitcoin loss tail. Agent (trained on R/ismev) negates: stores ξ = −0.30. VaR formula `u + (β/ξ)((n/N_u(1−α))^{−ξ}−1)` with wrong ξ sign produces wildly wrong VaR. Match B2.a.

NEGATIVE — Agent's call price is 5.10, oracle's is 5.05. Difference = 0.05, ratio = 1.0099, neither a sign nor a scale error. Probably tolerance / numerical method drift — investigate elsewhere.

---

### B3. Time / Date / Calendar Convention

**Framing.** Day-count, compounding basis, annualization factor, business-day handling, timestamp meaning, timezone, fractional-time, fixing-time, loop-ordering in recursive computations, and inclusive-vs-exclusive interval boundaries. The math operates on the wrong "clock."

**Decision Procedure.**
1. Identify any time/calendar convention referenced (or implicit) in the instruction.
2. Check the agent's code for: day-count basis, annualization factor, period boundary handling, loop indexing.
3. If the agent's choice differs from the test's pinned convention, match.
4. Distinguish from B1: B1 is unit/scale on numbers; B3 is convention on time.

**Exclusions.**
- Pure scale (B1).
- Off-by-one in array indexing that isn't about a *time* convention (that's a code bug, not a finance convention error).

**Sub-rubrics.**
- **B3.a — Day-count basis.** ACT/360 (USD money market) vs ACT/365 (GBP) vs 30/360 (US corporate) vs ACT/ACT (US Treasuries). Mixing these silently produces wrong accrued interest and yield. (PR #119 option-put-call-parity: fractional-second ACT/365 vs integer-day τ.)
- **B3.b — Compounding & rate conversion.** Continuous (`exp(−rT)`) vs simple (`1/(1+rT)`) vs semi-annual. Annual-to-monthly: simple `r_annual/12` vs compound `(1+r_annual)^(1/12)−1`. (PR #66 portfolio-risk-attribution.)
- **B3.c — Annualization factor.** Daily vol × √252 vs ×√365 vs ×√250. Sharpe daily-to-annual scaled by √252 vs other.
- **B3.d — Bar timestamp meaning / fixing-time.** "1-min bar at 10:03" = trades 10:03–10:04 (bar-start) or 10:02–10:03 (bar-end). Both conventions appear in real data (TRTH/Refinitiv mixes them). (PR #79 execution-is-vwap.)
- **B3.e — Timezone handling.** `tz_convert("America/New_York")` vs raw `−04:00` offset. Reference omits the tz_convert and treats raw offset as local. Agent does the financially correct tz_convert and gets penalized. (PR #150 earnings-news-event-alpha — note: agent is right, oracle is wrong; this is a *task* bug, but the agent failure mode label is still B3.)
- **B3.f — Date-range semantics.** `date_range.start` = first *price* date or first *return* date (one day later, since returns need a prior price). (PR #128 etf-cross-asset-lead-lag.) Fractional time-to-expiry: `(expiry − quote).days` (integer days) vs `total_seconds / (365·86400)` (fractional). (PR #119.)
- **B3.g — Loop ordering / pre- vs post-update state in recursive computation.** Process `x_0 = 0`, evolves to `x_{t+1}`. Day-1 cost uses `x_0` (pre-update) or `x_1` (post-update)? Both are defensible, both are different MC prices. (PR #84 cme-hdd-option-pricing.) Same for HDD aggregation, and for `daily_pnl[0] = equity_0 − capital_base` vs `0` (PR #135 prediction-markets).
- **B3.h — Inclusive vs exclusive index slicing.** "120 trading days ending day −11" with Python slice `[event_idx−130, event_idx−10)` is end-exclusive → 119 days, not 120. (PR #88 event-study-earnings.) "1-year forward T−1 to T" with maturity gaps > 1y silently divides by `(T − T_prev)` instead of 1. (PR #38 zero-coupon-bootstrapping.)

**Finance examples.**

POSITIVE — VWAP execution task: instruction says "the bar at or just before the arrival timestamp." Agent picks bar-end convention (timestamp marks trades 10:02–10:03), so the "10:03 arrival" picks the wrong bar. Kyle's λ off by 30%, three downstream tests fail. Match B3.d.

POSITIVE — Cap-floor pricing: ACT/365 fractional time-to-expiry is `total_seconds/(365·86400)`. Agent uses integer-day `(expiry − quote).days / 365`. For a 30-day cap with morning fixing time, the difference is meaningful. Match B3.a / B3.f.

NEGATIVE — Test expects accrued interest = $1.234 on a 30/360 bond, agent returns $1.234 to 4 decimals. No convention mismatch.

---

## C. Data & Numerics

### C1. Data Fabrication / Wrong Source

**Framing.** The agent's math and conventions are right, but it's operating on the wrong inputs. Either the agent fabricated data (synthesized via `np.random` instead of loading the prescribed CSV), used the wrong file/column/frequency, or introduced look-ahead by using future data in a backward-looking signal. Includes silent data corruption from over-aggressive `dropna` and parsing failures on non-standard file headers.

**Decision Procedure.**
1. Identify the prescribed input source(s) in the instruction. Path, file, column, frequency.
2. Check what the agent's code actually reads. Look for: `np.random.*` calls used as inputs, `yfinance` pulls, hard-coded constants used in place of computed quantities, wrong column reads.
3. If the agent's input source materially differs from the spec and is *relied upon* (not just generated and discarded), match.
4. Look-ahead: the agent uses information not available at the decision time.
5. Distinguish from A3: A3 is *interpretation* of an input; C1 is *origin* of the input.

**Exclusions.**
- Right source, wrong analysis (A1/A2/A3).
- Right inputs, wrong solver (C2).
- Schema/format gaps where the spec is silent on a non-numerical detail.

**Sub-rubrics.**
- **C1.a — Synthesized data substituted for prescribed source.** `np.random.normal(0, 0.01, 2520)` instead of `pd.read_csv("/app/data/returns.csv")`. Hard-coded `sigma = 0.20` instead of computing σ from log-returns. Common in finance-zero single-shot generation when the agent assumes the file is unreadable.
- **C1.b — Wrong source / file / column.** `yfinance.download()` instead of the provided CSV. `open` column instead of `close`. Daily frequency when monthly was asked.
- **C1.c — Look-ahead / future information leak.** Signal at time t uses `t+1` data. Computing rolling vol with same-day inclusion when "as-of t" is required. (PR #164 dupire-local-vol's reference itself uses 2025-12-30 close as S₀ for a 2024-03-15 valuation date — this is a task bug, but the *pattern* is real for agents.)
- **C1.d — Multi-line preamble / non-standard CSV header.** Real-world data files (Ken French factors, FRED, Bloomberg) often have copyright preambles, end-of-file footers, mixed delimiters. Agent applies naive `pd.read_csv` / `pd.to_datetime(format='%Y%m%d')` and crashes (or silently corrupts row-0). (PR #97 factor-momentum-spanning: Finance-Zero failed because didn't strip Ken French preamble.)
- **C1.e — Dropna granularity.** `dropna()` without `subset=` removes rows where *any* column has NaN. `dropna(subset=[tickers[0]])` only checks the first ticker. Both can corrupt a panel: the first inflates the missing-value count (one ticker's gap removes others' valid data); the second silently passes NaNs through to OLS, giving NaN coefficients. (PR #88 event-study-earnings; PR #86 dcc-garch.)
- **C1.f — Data interpretation that drops information.** CEREP credit transition data: defaults are sometimes recorded under the "Withdrawals" column (when the issuer's rating was withdrawn before defaulting). Naïve reading of the "Default" column alone undercounts defaults — CCC→Default rate ~3% vs corrected ~31%. (PR #80 credit-migration-matrix.)

**Finance examples.**

POSITIVE — Task: "Compute σ_hist from `/app/spy_daily.csv` log-returns and use it to calibrate CEV α." Agent's code: `np.random.seed(0); returns = np.random.normal(0, 0.01, 2520); sigma = std(returns) * sqrt(252)`. The fabricated returns are used to set σ. Match C1.a (single-shot finance-zero pattern from the trajectory skill's examples).

POSITIVE — Ken French factor task: agent calls `pd.read_csv(url)` then `pd.to_datetime(df["date"], format="%Y%m%d")`. Crashes with `ValueError: time data "Copyright 2026 Eugene F. Fama..."`. The 5-line preamble was never stripped. Match C1.d.

NEGATIVE — Agent loads the right CSV, picks the right column, computes σ_hist correctly, but uses it in a wrong-model price (Black-Scholes when CEV mandated). That's A1, not C1.

---

### C2. Numerical / Optimization Failure

**Framing.** The right model, the right formula, the right inputs — but the *numerical* solution path failed. Local optimum (multimodal likelihood, no warm-start), divergence, ignored convergence flag, parameter pinned at boundary unexpectedly, special-function approximation error, or a fallback that silently substitutes a wrong value when a numerical primitive fails.

**Decision Procedure.**
1. Identify the numerical step: optimization, root-finding, integration, matrix decomposition, MC simulation, special-function evaluation.
2. Check the agent's setup: solver choice, initial guess, bounds, kwargs (`maxiter`, `ftol`, `gtol`, `xtol`).
3. Look for the symptom: parameter at upper/lower bound, NaN/Inf in output, optimizer `success=False` ignored, large gap to oracle on a parameter that should converge.
4. Identify the cause: multi-modal landscape with wrong start; bounds-and-penalty inconsistency; silent fallback to identity / last-known-good when decomposition fails.
5. Distinguish from A1/A2/A3: those are *math* errors. C2 is *numerical* execution given correct math.

**Exclusions.**
- Wrong formula (A2).
- Wrong parameterization (A3).
- Numerical noise within tolerance.

**Sub-rubrics.**
- **C2.a — Local optimum / multimodal likelihood without pinned start.** GARCH-t α landed at 0.073 (oracle) vs 0.10–0.12 (agents) due to non-convex likelihood (PR #196 copula-garch-portfolio). Heston κ landed at 50 (valid local optimum) vs oracle 2.0 because instruction allowed "fit OR use defaults" without bounds (PR #178 variance-swap-pricing). Lower bound > location of true MLE excludes valid solutions (Rama Cont: tail-index lower bound of 4 excludes empirically valid ν ≈ 2.1–3).
- **C2.b — Optimizer kwargs / extra stopping criteria.** `gtol=1e-8` added to L-BFGS-B → different convergence path → cascade across 6,253 dates (PR #98 nelson-siegel). `maxiter=10000` instead of `2000`. `least_squares(trf)` substituted for `minimize(L-BFGS-B)`.
- **C2.c — Boundary parameter binding.** ν pinned at 100 because likelihood missing `−log(scale)` (PR #208 — also matches A2). λ pinned at 12 because data wants higher (PR #172 — *intentional* per instruction). When binding is unintentional, the wrong objective drives it. When binding is intentional, the instruction must say so explicitly.
- **C2.d — MC counting / off-by-one.** Barrier hit probability > 1 because agent counted hits per *step* instead of per *path* (PR #140 localvol-barrier). Per-path indicator (max 1 per path) vs per-step indicator (sum can exceed 1).
- **C2.e — Special-function / transcendental approximation error.** Bivariate normal Φ₂(a, b; ρ) at high |ρ| computed from scratch and wrong in tails (PR #161 compound-option-geske: parity check caught Sonnet's Φ₂ implementation error). Modified Bessel I_ν, K_ν overflow at large argument. Hypergeometric ₂F₁ branch-cut handling. Symptom: plausible-looking final number but parity/arbitrage check fails.
- **C2.f — Smooth-pasting / fixed-point iteration setup.** BAW critical-price iteration: seed from perpetual boundary, exponential correction, Brent's method on `S* − K = C_euro(S*) + A₂(S*)`. Wrong seed or missing correction → wrong critical price → wrong premium. (PR #154 barone-adesi-whaley.)
- **C2.g — Silent fallback on numerical failure.** Cholesky fails → `L = identity` (no correlation in MC, wrong tail risk, no warning). Optimizer `result.success = False` → `prev_params` updated unconditionally → one bad local minimum poisons all subsequent warm-starts (PR #98). KRD curve interpolation: no curve point within 0.01 of key tenor → returns 0.0 silently (PR #65 bond-portfolio-analytics).
- **C2.h — Empty-array / boundary edge case.** `losses_sorted[var_idx + 1:]` empty when `var_idx = n_sims − 1` → `np.mean([])` returns NaN with RuntimeWarning → silently becomes `null` in JSON output (PR #126 merton-cds-copula).
- **C2.i — Penalty wall inside box bounds.** L-BFGS-B bounds allow `(a, b)` with `a + b < 0.999`, but manual `if a + b >= 0.999: return 1e10` creates a discontinuity *inside* the box. Finite-difference gradient breaks. Either tighten bounds (constraint enforced by box alone) or use SLSQP. (PR #86 dcc-garch.)
- **C2.j — RNG-state contamination in finite-difference Greeks (Monte Carlo).** *(50-trial validation: 3 trials in mc-greek-surface family.)* For finite-difference Greeks under MC, bumped and base evaluations must consume identical random draws (common random numbers, CRN); otherwise the FD estimator carries the variance of two independent MC runs and the gradient is dominated by noise. Three failure shapes: (i) Different seeds passed to bump/base sims (`seed+1`, `seed+2`); (ii) Mutating RNG state — agent calls `self.rng.standard_normal()` inside `price()`, so the second call advances state and gets different draws; (iii) Variance-reduction trick applied unevenly (antithetic in base only). Symptom: gamma negative for an obviously convex payoff, vega oscillates 50%+ between consecutive runs. Fix pattern: generate a single `Z = rng.standard_normal((N, M))` array OUTSIDE the price function and pass to all evaluations. **Step 0 prerequisite still applies:** if the agent's pricing formula itself is wrong, that's A2 — match A2 only.

**Finance examples.**

POSITIVE — GARCH(1,1)-t fit: agent's optimizer lands at α = 0.105, oracle at 0.073. Both are valid local maxima of the non-convex likelihood; agent's start and solver differ from oracle's. Test asserts `np.isclose(alpha, 0.073, atol=0.03)`, fails. Root cause: instruction didn't pin starting values or solver. Match C2.a.

POSITIVE — DCC-GARCH calibration: bounds `(1e-6, 0.5)` and `(1e-6, 0.999)` allow `a + b` up to 1.499. Penalty `if a + b >= 0.999: return 1e10` creates step at a ridge inside the box. L-BFGS-B's finite difference returns garbage gradient. Convergence stalls. Match C2.i.

NEGATIVE — Agent's L-BFGS-B converged with `success=True`, parameters within tolerance of oracle. No numerical failure.

---

### C3. Statistical Variant Mismatch

**Framing.** The instruction names a statistical method by its eponym (Newey-West, Corrado, Acerbi-Tasche, …) without writing the formula, but multiple variants of that method exist in the literature and produce different numbers. The test pins one variant; the agent picks another defensible variant from training memory. The QF-Bench analog of "Formula by reference trap." This is the **single most-validated mode in the dataset** — 5+ PRs hit it directly.

**Decision Procedure.**
1. Identify any named method in the instruction (especially named after a person/paper).
2. Check whether the instruction reproduces the formula. If only the name is given, the variant is under-specified.
3. Check the agent's implementation. Does it match the test's pinned variant, or a different one in the literature?
4. If agents from different training mixes will pick different variants, and the test pins one specific variant without naming it, match.
5. Distinguish from A3: A3 is a *parameter* with multiple definitions; C3 is a *method* with multiple formulas.

**Exclusions.**
- The instruction reproduces the exact formula (no ambiguity).
- Different agents converge to the same variant — no variant ambiguity.

**Sub-rubrics.**
- **C3.a — Multiple equally-named methods.**
  - **Newey-West "automatic" bandwidth.** NW(1987), NW(1994), Andrews (1991), Schwert. All produce different lag counts for the same T. (PR #76 fama-macbeth-risk-premia: oracle uses NW(1994) `floor(4·(T/100)^(2/9))` = 6; Haiku → 11, Sonnet → 7.)
  - **Corrado test (1989).** Original 1989, Corrado-Zivney 1992 multi-day, Eventus/SAS macro variant. Different denominators and aggregation. (PR #88 event-study-earnings: H/S/O each fail differently on Corrado, all pass KP — because instruction reproduces KP formula but not Corrado.)
  - **Expected Shortfall.** Threshold form `E[L | L > VaR]` vs rank-based Acerbi-Tasche `mean(top-⌈(1−α)·N⌉ losses by rank)`. These agree for continuous distributions but differ when there's an atom at VaR (always the case on a discrete grid). (PR #126 merton-cds-copula: Opus failed on this single test; PR #182 var-es-estimation.)
  - **VECM half-life.** `−ln(2)/ln(1+α[0])` (single-α simplification) vs `ln(2)/|α[0]|` (continuous-time limit) vs `−ln(2)/ln|1+β'α|` (rigorous spread eigenvalue). All defensible; pairs-trading desks usually use the third. (PR #131 garch-vecm.)
  - **Numerical method variants.** Newton-Raphson vs bisection+Newton. (PR #65 bond-portfolio-analytics: instruction prescribed Newton-Raphson but reference uses hybrid; can fail to converge for deep-discount long bonds.)
- **C3.b — Post-1994 / recent-literature variant trap.** When the cited method comes from a paper after ~1994 (e.g., Bandi-Russell 2006, Barndorff-Nielsen-Shephard 2004, Li 2005 IV approximation, Corrado-Miller-Hallerbach), training-data depth varies across agents. Pre-1994 classical methods (BS, Black '76) are uniformly trained; post-1994 papers less so. Each agent picks a different variant from memory and fails on a different test. (PR #107 realized-vol-estimators: Sonnet 108/141, Opus 141/141 — depends on which BR or BNS variant the agent learned in depth. PR #169 implied-vol-approximations: Brenner-Subrahmanyam, Li 2005, CMH — H/S/O each fail on a *different* method.)
- **C3.c — Non-canonical reference variant / under-specified procedural goal (inverse trap).** Two flavors, both involving spec under-specification:
  - **Flavor 1: Reference uses a non-textbook variant.** Spec names a well-known method without writing the formula; reference uses a non-canonical implementation; agent follows standard practice and fails. Example: WoE/IV smoothing applied to *proportions* `(good_pct + 0.5)` — non-standard, dampens WoE 8× toward zero — vs textbook (Siddiqi *Credit Risk Scorecards*) smoothing on *raw counts* `(good_count + ε) / total_good`. Both Haiku and Sonnet defaulted to the canonical formula; reference's IV is 3.4× lower, cascading to 8 failures. (PR #130 ml-credit-scoring-fairness.)
  - **Flavor 2: Spec under-specifies a procedural goal.** Instruction names a *goal* like "parametric VaR decomposition", "Greek-based stress test", "factor-neutral hedge", "shrinkage estimator with smoothing" — but does NOT pin a specific formula AND multiple defensible formulas exist. The reference oracle pins one specific formula; the agent invents a different defensible one. Example: PR `barrier-garch-var` Haiku trial: instruction says only "computes a parametric VaR decomposition for a portfolio of `n_contracts` options at the given confidence level" — no formula. Agent invents a Greek-based delta-gamma-vega Gaussian VaR; reference pins something else; partial credit ~0.15.
  Both flavors are C3.c matches *and* task-design issues — the fix is to write the exact formula in the instruction (or widen the test tolerance). When flagging this, note in `notes` that the upstream cause is task-side under-specification, even though the agent-output label is C3.c.
- **C3.d — `np.quantile` method on discrete distributions.** `method='linear'` (default) interpolates between sample atoms; `method='higher'` returns `inf{l : P(L ≤ l) ≥ α}` — the generalized inverse CDF, correct for discrete loss distributions (PR #126; constant-LGD constant-exposure portfolios have only N+1 possible loss values).

**Finance examples.**

POSITIVE — Fama-MacBeth task: instruction says "use automatic bandwidth selection for Newey-West." No formula given. Test asserts `nw_lags == 6`. Reference uses NW(1994) `floor(4·(T/100)^(2/9))`. Agents pick: NW(1987) → 5, Andrews (1991) → varies, Schwert → 6, Stock-Watson → 6. Sonnet picks Andrews → 7, all 4 cascading failures from this single bandwidth miss. Match C3.a.

POSITIVE — ML credit scoring task: instruction says "compute Weight of Evidence per bin. Use the smoothing constant from params to avoid log(0)." Standard textbook (Siddiqi): smooth raw counts. Reference: smooth proportions, dampening WoE ~8× toward zero. Both Haiku and Sonnet implement the textbook form → IV 3.4× too high → 8 cascading failures. Match C3.c.

NEGATIVE — Instruction explicitly writes out the Newey-West formula in full. Agent implements that exact formula. Test passes. No variant ambiguity, no match.

---

## D. Spec & Output Compliance *(non-quant — orthogonal axis)*

### D1. Output Schema & Spec Compliance

**Framing.** The agent's *quantitative content* is correct — formulas right, conventions right, data sources right, numerical solvers converged — but the *output format / schema / vocabulary* doesn't match what the verifier expects. The failure is a "shape" or "labeling" mismatch on the way out, not a math error on the way in. This mode was added in May 2026 after the v10 batch analysis showed ~30–40% of finance-bench tasks are dominantly data-engineering / pipeline-reconstruction tasks where this is the dominant failure axis.

**Why a separate class.** Classes A/B/C target *quant content*: formula correctness, unit/sign/calendar conventions, data sourcing, numerical methods, statistical-method variants. Schema/vocabulary failures live on a different axis — the agent could be a perfect quant and still fail D1 by guessing the wrong column ordering or label spelling. Treating D1 as a forced fit under A3 or C3.c was creating high inter-judge variance (validation found 3 different mode picks across 5 sub-agents on the same root cause). Class D resolves that.

**Decision Procedure.**
1. Identify the failing tests. Are they checking *numerical output values* (vague match-by-value) or *schema artifacts* (string equality on labels, list shape, column ordering, type assertions like `isinstance(x, list)`, exact-match dictionary keys)?
2. If the failing tests are **schema/format-only** AND the agent's numerical computations *that ARE checked* all pass → D1 fires.
3. If the trial has BOTH schema failures AND numerical failures → match D1 *and* the appropriate quant mode(s). D fires independently of A/B/C (orthogonal axis).
4. **Authorship sub-question.** Did the *prose* enumerate the canonical vocabulary/shape? If yes → D1 with `root_cause_class = agent_coding` (agent should have followed) OR `agent_conceptual` (if the agent substituted a real-world concept the spec disallowed — e.g., LLM-prior attractor on a controlled vocabulary). If no → D1 with `root_cause_class = task_side` (spec under-specified). In all cases D1 fires; the `root_cause_class` differentiates blame.

   **Carve-outs**:
   - **D1.g** has its own routing (see § "D1.g routing" below): defaults to `agent_coding`, reserves `task_side` only for explicit-buggy-spec cases (v3.2.7).
   - **D1.e (JSON precision)**: defaults to `agent_coding` when oracle achieves the threshold without manual rounding (the typical case — standard `json.dumps` preserves 17 sig digits, well under 1e-12). Reserve `task_side` only for the rarer spec-test inconsistency where the spec mandates intermediate rounding (e.g., *"round correlation outputs to 6 decimals"*) but a downstream test pins values computed without rounding — see L696.
5. Cite the specific schema mismatch in evidence (e.g., `agent action='RESET' vs expected 'replace_initial'`). Quote the agent's wrong output and the test's expected literal.

**Exclusions.**
- Tolerance issues on numerical values (small float drift): *not D1.* That's a `qf-bench-review` task-side issue (test tolerance set too tight) — flag as `task_side` but match=false on D1.
- Missing output files entirely (`FileNotFoundError` on a required output): *not D1*; that's a trajectory-side termination issue → trajectory-error skill.
- Complete output absence with non-empty agent code (Case 2 of insufficient-solution): *not D1*; the agent didn't fail to comply with schema, it didn't produce output at all.

**Sub-rubrics.**
- **D1.a — Vocabulary / label mismatch.** Agent invents a defensible string token where the spec/test pins a specific literal. (v10 example: `13f-amendment-aware-crowding` — agent emitted `RESET / RESTATEMENT / APPEND` derived from `AMENDMENTTYPE` while the test pinned `replace_initial / replace_restatement / append_new_holdings`. All 5 model-rounds hit this.) Often surfaces as: uppercase-vs-snake_case, abbreviated-vs-full, agent invents from data-vocabulary vs spec-pinned canonical labels.
- **D1.b — Shape mismatch (scalar/string vs list/struct).** `summary.max_overlap_pair` written as `"DAVIDSON_KEMPNER-FULCRUM"` (string) vs expected `["DAVIDSON_KEMPNER", "FULCRUM"]` (2-element list); `holder_list` joined with `,` vs `|`; tuple emitted as JSON array of distinct types. Test asserts `isinstance(x, list)` or `len(x) == 2` and the agent fails on shape, not on content.
- **D1.c — Column ordering / missing columns.** `effective_holdings.csv` has `weight` at the wrong index; `crowded_securities_latest.csv` missing the leading `rank` column. Tests assert `df.columns[i] == "weight"` or `"rank" in df.columns at position 0`.
- **D1.d — Type serialization (str-vs-int/bool, identity-column convention).** `summary.json` numeric counts written as `"79"` (string) instead of `79` (int); `all_checks_passed: "True"` instead of `True`; `ISAMENDMENT` round-tripped through `bool()` to produce Python `'True'/'False'` strings instead of preserving raw `Y/N/''`. Also: agent emits `manager_order` (int 2) where test expects `manager_label` (str `"OXFORD"`) — same identity but wrong column.
- **D1.e — JSON float-precision / serialization rounding.** Agent rounds `max_turnover_value` to 9 decimals during JSON serialization (`0.78043996`); test pins to `0.7804399659638062` at `atol=1e-12`. **Routing depends on whether oracle achieves the test tolerance:**
  - **Default = `agent_coding`** (v3.2.5 hidden-quality-threshold). Standard Python `json.dumps(x)` preserves ~17 significant digits, well under any `atol=1e-12` threshold. If oracle achieves the threshold with margin, the agent's manual-rounding-before-serialization is engineering carelessness — they should know `json.dumps` preserves full float64 precision and not pre-round when the test tolerance is tight.
  - **`task_side` only** if the spec mandates intermediate rounding (e.g., *"round correlation outputs to 6 decimals"*) and a downstream test pins values computed without rounding — that's a genuine spec-test inconsistency (the agent followed the spec's rounding instruction faithfully). Example: `fb-v10-opus46-etf-cross-asset-lead-lag` (avg_abs_asymmetry_ratio computed from 6dp-rounded inputs vs full-precision test pin).
- **D1.f — Date / timestamp serialization format.** Agent emits `'2025-12-31 00:00:00'` (ISO with time) where test expects `'2025-12-31'` (date-only string). Distinct from B3 because there is no calendar-convention error — the underlying date is correct, only the serialization differs. (Subsumes one earlier B3-partial match in the validation entries.)
- **D1.g — Library/API default-induced numerical drift (engineering bug, not QF bug).** The agent's QF reasoning is correct — right model, right formula, right convention pick — but a *library API default* corrupts the numerical output that reaches the verifier. The failing test asserts on a numerical *value* (not a schema artifact), but the root cause lives at the data-engineering layer, not the quant-knowledge layer. This is the only D1 sub-rubric where the failing test is on a numeric value rather than a schema/format artifact — it earns its place in D because the **mechanism is engineering, not finance**.

  Canonical examples:
  - **Non-stable sort + `drop_duplicates(keep='last')`.** When the input has duplicate keys with *different values*, `pandas.DataFrame.sort_values('date')` with the default unstable algorithm can flip duplicate-row positions. A subsequent `drop_duplicates(keep='last')` then keeps the wrong row, silently corrupting one input value. Cascades through all downstream computations as small numerical drift. (v10 example: `cross-sectional-momentum` — Opus 0/3 rounds passing across all 9 cells of the canonical run; Haiku 1/3 passes by luck of pandas-version. After a one-line spec fix that pins `kind='stable'` in the sort, Haiku passes 1/1.)
  - **Floating-point JSON round-trip drift.** Agent computes `0.7804399659638062` correctly, but `json.dump(..., default=float)` or `np.float32` casting truncates to `0.78043997`. Test asserts at `atol=1e-12`. (Adjacent to D1.e but distinct: D1.e is about *rounding the agent applied*; D1.g is about *library defaults the agent didn't override*.)
  - **`numpy.argsort` / `np.sort` default `kind` differs from oracle's tie-break.** Agent's argsort returns different tie-break order on integer-equal scores, picking different stocks at portfolio-formation tie boundaries.
  - **`pandas.read_csv` dtype inference.** Agent reads price column as `int64` instead of `float64` because all visible values are integer-valued, then a later division silently truncates.
  - **`pandas.merge` non-deterministic row ordering.** Agent merges on a key with duplicates; the result row order is implementation-defined and depends on hash-collision details, so subsequent `.iloc[0]` picks a different row than oracle.
  - **`json.dumps` non-deterministic dict-key ordering.** Pre-Python-3.7 or with `sort_keys` mismatch.

  **How to distinguish D1.g from A3:**
  - **A3 (parameterization)** is when the agent's *QF reasoning* picked the wrong convention (e.g., chose `ddof=0` because they thought MLE; chose conditional MLE because that's what they remember from a textbook). The agent would defend the choice in plain English. → `agent_conceptual`.
  - **D1.g** is when the agent's *QF reasoning* is correct but a *library default* silently picked a different convention than oracle's. The agent would be surprised and fix it instantly when shown. → `agent_coding`.
  - **Test:** if you can rewrite the agent's code with one keyword-argument change (e.g., `kind='stable'`, `dtype=float`, `keep='last'`) and the answer becomes correct, it's D1.g. If you'd need to change a formula, a convention pick, or a model class, it's A/B/C.

**Finance examples.**

POSITIVE — `fb-v10-h45-13f-amendment-aware-crowding`: agent's HHI / turnover / weighted-overlap / crowding computations all pass their numeric tests; 13 schema failures (action vocab, holder_list joiner, ISAMENDMENT typing, summary.json string-vs-int, max_overlap_pair shape, datetime format). Match D1 (D1.a + D1.b + D1.c + D1.d + D1.f). **`root_cause_class = infra_failure / stale_spec_checkout`** (corrected 2026-05-06; see Cross-cutting § "infra_failure / stale_spec_checkout" below). The trial-time `agent/trajectory.json` step-2 user message DOES NOT contain the L41-45 enumeration — agents received a pre-`75d5f1a` (Apr-23) snapshot of the instruction in which only the verbose verb description appears (*"non-amendment filing resets / RESTATEMENT replaces / NEW HOLDINGS appends"*). Verified bit-identical to remote LFS hash; not a local mutation. The maintainer's `origin/main` spec is correct since Apr 23, but the harness operator's `tasks/` checkout was stale at the May 1-4 v12 sweep. The 21/21 universal failure is a benchmark infrastructure bug, NOT an LLM pretraining-prior attractor — agents reasoned correctly from the (older) instruction they actually received.

POSITIVE — Hypothetical: agent computes Sharpe ratio correctly (numeric test passes) but writes it as a percentage string `"1.23"` instead of float `1.23`. Test asserts `isinstance(sharpe, float)` → fails. Match D1.d.

POSITIVE — `cross-sectional-momentum` 9 of 9 canonical cells (Haiku/Sonnet/Opus × R1/R2/R3): agent's momentum logic is structurally identical to oracle's (`iloc[t-12:t-1].sum()` arithmetic-sum formation, `[:3]` long / `[-3:]` short, simple monthly returns, `prod(1+r) - 1` total return). The failing test is on `total_return = 1.6172649012281468` (Opus produces 1.5898, all 5 metric-anchors fail). Code-line root cause: `df.sort_values('date').drop_duplicates(subset='date', keep='last')` — pandas's default unstable sort flips two duplicate rows on `2017-12-31`, then `keep='last'` silently keeps the wrong one. **Empirical:** a single-line `kind='stable'` addition lifts Haiku 0/3 → 1/1 on the same prices.csv. Match D1.g + co-fire A3 with `notes: "Subsumed by D1.g engineering layer; agent's QF reasoning correct, root cause is pandas sort-default."`. **`root_cause_class = agent_coding`** — the spec says "sort by date ascending" without specifying stability; this is *silent on the kwarg*, NOT *mandating the buggy idiom*. A senior engineer who sees `drop_duplicates(keep='last')` AND knows the data has duplicates with different values is expected to add `kind='stable'` defensively. The spec is testing exactly this engineering judgment; agents who don't apply it are showing real engineering weakness, not victims of a spec trap. (See § "D1.g routing" below for the precise discrimination between `agent_coding` and `task_side`.)

**D1.g routing — when is it `agent_coding` vs `task_side`?**

The default routing is **`agent_coding`** (the agent should add the right kwarg; defaults to library defaults that misbehave is engineering carelessness, especially in time-series/duplicate-key contexts). Reserve **`task_side`** ONLY for cases where the spec **explicitly writes the buggy library call verbatim with the wrong kwarg specified** — e.g., the spec literally instructs `df.sort_values('date', kind='quicksort').drop_duplicates(keep='last')`. Specs that are **silent on the kwarg** (like cross-sectional-momentum, which says only "sort by date ascending") are testing the agent's engineering judgment, NOT mandating the buggy idiom. Cross-check this against v3.2.5 (hidden-quality-threshold): if the oracle achieves the answer with margin (oracle_drift ≪ test_threshold), the test is a quality gate, not a brittle pin → `agent_coding`.

NEGATIVE — Agent computes Sharpe ratio with the wrong annualization factor (`√365` instead of `√252`). Numeric test fails because the *value* is wrong. This is B3 (calendar convention), not D1.

NEGATIVE — Agent's `max_turnover_value` is `0.45` instead of `0.78`. Numeric test fails because the *computation* is wrong (e.g., agent forgot to divide by 2). This is A2 / A3 / B1 depending on the upstream cause, not D1.

NEGATIVE — Agent uses `ddof=0` because they reasoned "MLE Gaussian density requires biased-variance estimator." Test expects `ddof=1`. The agent would defend the choice in plain English; the QF reasoning is the variable that needs to change. This is **A3 with `agent_conceptual`**, NOT D1.g.

**Cross-class interactions (independent matches).**
- D1 fires **independently** of A/B/C. A trial can match A2 (missing formula term) AND D1.a (wrong action vocabulary) when both bugs are present and uncorrelated.
- The cascade rule applies *within* D (one D1.a vocabulary error producing 5 cascading test failures = one D1.a match). It does NOT collapse D into A/B/C or vice versa.
- **D1.g special case (engineering layer subsuming a quant-axis match).** When D1.g fires, an A3 (or A2/B1) match is *also* technically firing on the same root cause — the wrong numerical value. Apply a **D1.g-precedence rule** in this case: match D1.g as primary (since the mechanism is engineering, not QF), and mark the parallel A3 with `match: false` plus `notes: "Subsumed by D1.g — wrong value caused by library API default, not by agent's QF reasoning."`. This is the *only* place where D subsumes a quant-axis mode. Rationale: classifying as A3 with `agent_conceptual` would mis-attribute an engineering bug as a finance-knowledge gap, polluting capability assessments.

**Provenance.** D1 added 2026-05 from v10 batch analysis. Initial sub-rubrics seeded from `13f-amendment-aware-crowding` (5 model-rounds). D1.g added 2026-05-04 from `cross-sectional-momentum` deep-dive — first canonical case where an engineering-layer bug (pandas non-stable sort + `drop_duplicates`) produced wrong-value test failures while QF logic was provably correct. Verified end-to-end with a one-line spec fix that lifted Haiku 0/3 → 1/1.

---

## Cross-cutting: cascade rule (strict — priority-enforced)

A finance bug often touches multiple modes at once: e.g., a single missing `/S₀` in an LR delta score is simultaneously (i) a missing formula term [A2], (ii) a wrong score-function parameterization [A3], and (iii) a 100× unit-scale symptom [B1]. All three rubrics technically fire on the same code line.

**The cascade rule says:** classify the root cause ONCE, under the most upstream / most structurally-deep rubric. Return `match: false` for the downstream rubrics with `notes` pointing to the chosen mode (e.g., *"Subsumed by A2.a: same /S₀ omission. Same root cause."*).

### Priority hierarchy for shared root causes within the QUANT axis (A/B/C, high → low)

| Priority | Mode | Captures | Subsumed-by-others-when |
|---|---|---|---|
| 1 | **A1** | Wrong model class / wrong measure | Never |
| 2 | **A2** | Right model, missing or extra formula term | Subsumed by A1 if model itself is wrong |
| 3 | **A3** | Right formula structure, wrong parameterization / convention | Subsumed by A2 if a structural term is missing on the same line |
| 4 | **B1** | Formula structurally right, expressed at wrong scale | Subsumed by A2/A3 if those apply to the same code line |
| 5 | **B2** | Right scale, wrong sign | Subsumed by A2/A3 if those apply to the same code line |
| 6 | **B3** | Right scale and sign, wrong time/calendar convention | Subsumed by A2/A3 if those apply to the same code line |
| 7 | **C1** | Inputs wrong (separate axis) | Fires independently |
| 8 | **C2** | Math right, solver/numerics failed | Subsumed by A1/A2/A3 (Step-0 prerequisite already enforces this) |
| 9 | **C3** | Math right, but a method-variant choice the spec didn't pin | Subsumed by A1/A2/A3 unless authorship pre-check Case 3 applies |

### Class D — separate axis, fires independently

| Mode | Captures | Subsumption |
|---|---|---|
| **D1** | Output schema/format/vocabulary doesn't match spec; quant content is correct or off-axis | **Never subsumed by A/B/C and never subsumes them.** A trial can match D1 *and* any A/B/C mode simultaneously. |

The cascade rule operates *within* an axis, not across axes. D1 fires whenever the schema-mismatch criteria in its decision procedure are met, independent of whether A/B/C also fire on the same trial.

### When the cascade rule does NOT collapse modes

**Independent root causes get independent matches.** If one trial has both a wrong Heston char-fn coefficient (root cause #1 → A2.g) AND wrong RNG state in the FD Greeks (root cause #2 → C2.j), these are separate code lines and separate mechanisms — both modes match.

**Multiple major errors → multiple matches (not just one).** When you encounter a trial with several genuinely independent quant errors, mark **every** mode whose rubric fires — do NOT artificially pick "the most upstream" if the bugs are on different code lines or different mechanisms. The cascade rule's purpose is to suppress *symptoms of one root cause being counted twice* (A2 + B1 from one missing factor), not to suppress *legitimately different bugs being counted separately*. When in doubt: ask "are these the same code line / same mechanism / same mathematical step?" — if yes, collapse; if no, both match.

**Cross-axis matches always co-fire.** D1 + A2 + C1 can all match simultaneously on a trial that has (i) a wrong formula term, (ii) wrong input data, AND (iii) wrong output schema. These are three orthogonal failures.

**B1.e vs A3.c special case.** These target genuinely different mechanisms even though they often share symptoms:
- A3.c = "agent picked wrong-but-CONSISTENT convention" (one bug, applied uniformly)
- B1.e = "agent applied two DIFFERENT conventions across methods" (consistency failure across multiple code lines)

When only one applies, match it. When the agent applied `/100` in BS-vega but not in FD-vega — that's specifically B1.e (drift). When the agent applied `/100` everywhere consistently and the spec wanted no `/100` — that's A3.c (single wrong choice). Do NOT collapse these into one when the mechanisms truly differ.

### Cascade examples

- PR #130 (1 → 8): WoE smoothing error → IV → feature selection → logistic regression → AUC + Gini + KS + KS-threshold + DPR + EOD + top-3-features-by-IV + iv_top_feature. **One root cause → A2 match only**, all downstream tests recorded in notes as cascades.
- PR #98 (1 → 6,253 dates): single bad warm-start poisoning a time-series fit. **C2.g match only.**
- PR #208 (1 → 12): `−log(scale)` Jacobian missing → ν pinned at 100 → wrong volatility → all parameter tests fail. **A2.a match only**; the C2.c boundary-binding is subsumed (downstream symptom of the missing Jacobian, not a separate numerical issue).

## Cross-cutting: MANDATORY task_side self-check (added v3.2.12)

`task_side` is a high-bar classification — it tells the maintainer "your spec on `origin/main` has a defect." Calling something `task_side` when it isn't misroutes action to the wrong owner and damages audit credibility. Empirical track record from v3.2.x → v3.2.11 shows that sub-agents systematically over-route to `task_side` under literal application of "spec doesn't pin → C3.c." This self-check is a doubt mechanism that fires automatically when a sub-agent provisionally classifies a trial as `task_side`.

### When to run

Run this self-check **before finalizing** any classification with `root_cause_class = task_side`. Output JSON MUST include a `task_side_self_check` field documenting the answer to each question. If even one question downgrades, **reclassify away from task_side** and explain in `judge_notes`.

### The 7-question doubt checklist (Q0 + Q1–Q6)

**Q0 is the gatekeeper** — it forces a deep re-examination of the entire claim before the remaining six discriminator questions are answered. Q0 must be answered FIRST and in the deepest detail; the other six questions only proceed if Q0 has been answered carefully.

#### Q0 — MANDATORY deep re-examination (added v3.2.13)

> **"Are you sure this is a task issue? Re-examine deeply using the full skill before continuing."**

Before answering Q1–Q6, the sub-agent MUST:

1. **Re-read the spec end-to-end on `origin/main`** — not just the section that seems relevant. `git show origin/main:tasks/<task>/instruction.md` in full. Skim the entire instruction with fresh eyes for any pin you missed: cited papers, library function names, numerical pins, schema enumerations, formula blocks, eponym references, day-count specifications, library kwargs.
2. **Re-read the failing test assertion(s) verbatim** from `verifier/test-stdout.txt`. Look at the actual numeric values, comparison operators, tolerances. Is it `assert x > 0` (shape invariant) or `assert isclose(x, K, rtol=R)` (pinned numeric with K and R explicit)? Quote the literal assertion line.
3. **Re-read the agent's actual code** from `agent/<agent-name>.txt` or trajectory writes. Find the EXACT lines where the agent diverged from what would have produced the test-passing value. Don't paraphrase — quote the agent code.
4. **Cross-check against the skill's discriminators**: read § "Pre-check: who authored the formula?" (3 cases), § "Industry-Standard pre-check", § "Sub-rule: Mathematical equivalence ≠ literal compliance", § "Cross-cutting: hidden quality thresholds". Do any of these route the trial AWAY from task_side?
5. **Cross-check against the existing canonical examples** in TAXONOMY.md POSITIVE/NEGATIVE finance examples. Does the trial's pattern match an established `agent_conceptual` or `agent_coding` example better than a `task_side` example?
6. **Write out the task_side claim explicitly** in 2–3 sentences: *what specifically is wrong with the maintainer's `origin/main` spec, what evidence shows the spec defect, why no other classification fits*. If you cannot write this in concrete terms (specific spec line, specific defect, specific test pin that the spec couldn't have intended) — that is itself a signal the trial isn't task_side.

**Q0 output format** — the JSON output MUST include a `q0_deep_recheck` field with the following sub-fields:

```json
"q0_deep_recheck": {
  "spec_full_reread": "<one-sentence summary of what spec says, end-to-end>",
  "test_assertion_verbatim": "<copy-paste the assert line>",
  "agent_code_verbatim": "<copy-paste the relevant agent code lines>",
  "discriminator_checks": {
    "case1_spec_authored": "<no/yes — did spec write formula or cite paper?>",
    "case2_canonical": "<no/yes — is this a canonical model the agent should know?>",
    "industry_standard_check": "<no_standard / standard-name>",
    "math_shortcut_check": "<literal_compliance / shortcut_taken>",
    "hidden_threshold_ratio": "<oracle-margin / N-A>"
  },
  "task_side_claim_in_concrete_terms": "<2–3 sentences naming spec defect + test pin + why no other mode fits>",
  "confidence_after_deep_recheck": <0–1>
}
```

If `confidence_after_deep_recheck < 0.8` after the deep re-examination, **STOP and reclassify** — do not proceed to Q1–Q6. The sub-agent's own uncertainty is itself a signal that task_side is not the right answer.

If `confidence_after_deep_recheck ≥ 0.8`, proceed to Q1–Q6.

#### Q1–Q6 — Specific discriminator questions

For each question, answer Y / N / N-A. The right column shows what each YES/NO triggers.

| # | Question | If YES → | If NO → |
|---|---|---|---|
| **Q1** | Are the failing tests **shape invariants only** (positivity, monotonicity, in-band, ratio-close-to-one, exists, len(x) == n)? | task_side plausible (continue) | **DOWNGRADE to A3.f / agent_conceptual** — pinned numeric tests indicate the maintainer ran a canonical implementation and pinned ITS output; the spec is NOT genuinely under-specified |
| **Q2** | Is there **NO clear industry-standard** implementation for the named convention? (Run the Industry-Standard pre-check from § Pre-check.) | task_side plausible (continue) | **DOWNGRADE to A3.f / agent_conceptual** — agent should have used the industry standard; deviation is a knowledge gap |
| **Q3** | Does the spec **NOT mention** any paper, textbook section, library function, named author, eponym, or convention shorthand for the procedure? | task_side plausible (continue) | **DOWNGRADE to A1/A2/A3 (Case 1)** — citation pins the convention; agent must follow it |
| **Q4** | Did the agent's code **NOT take a mathematical shortcut** bypassing the literal spec procedure (per v3.2.11 sub-rule)? | task_side plausible (continue) | **DOWNGRADE to A3.f / agent_conceptual** — math-equivalence shortcut is an A3.f signal, not under-spec |
| **Q5** | Does the spec **NOT use literal verbs** ("draw from", "sample from", "select Z", "compute Y") whose literal reading would determine canonical execution? | task_side plausible (continue) | **DOWNGRADE to A3.f / agent_conceptual** — literal verb reading is the canonical procedure |
| **Q6** | Have **sister trials of the same task in other batches** been classified consistently (NOT all classified differently)? | task_side plausible (continue) | **FLAG for cross-batch review** — if sisters are `agent_conceptual`, reconsider; if sisters are `infra_failure`, check stale-spec |

**Decision rule:** task_side stands ONLY if Q0 passed (`confidence_after_deep_recheck ≥ 0.8`) AND ALL 6 of Q1–Q6 answer "task_side plausible" (no DOWNGRADE). If Q0 fails confidence threshold OR any of Q1–Q6 downgrades, reclassify to whichever mode the failing question pointed to, with confidence noted.

### Required output JSON addendum

When finalizing a `task_side` label, the output JSON MUST include the full Q0 deep re-check + the 6 discriminator answers:

```json
{
  ...standard fields...,
  "root_cause_class": "task_side",
  "task_side_self_check": {
    "q0_deep_recheck": {
      "spec_full_reread":           "<one-sentence summary of what spec says, end-to-end>",
      "test_assertion_verbatim":    "<copy-paste the failing assert line>",
      "agent_code_verbatim":        "<copy-paste the agent's diverging code>",
      "discriminator_checks": {
        "case1_spec_authored":      "<no/yes — did spec write formula or cite paper?>",
        "case2_canonical":          "<no/yes — canonical model agent should know?>",
        "industry_standard_check":  "<no_standard | standard-name>",
        "math_shortcut_check":      "<literal_compliance | shortcut_taken>",
        "hidden_threshold_ratio":   "<oracle-margin | N-A>"
      },
      "task_side_claim_in_concrete_terms": "<2–3 sentences: spec defect + test pin + why no other mode fits>",
      "confidence_after_deep_recheck": <0–1>
    },
    "q1_test_type":         "shape_invariants",      // or "pinned_numeric" → DOWNGRADE
    "q2_industry_standard": "no_standard_exists",    // or "<standard-name>" → DOWNGRADE
    "q3_spec_citation":     "no_citation",           // or "<paper/textbook ref>" → DOWNGRADE
    "q4_math_shortcut":     "literal_compliance",    // or "math_equivalent_shortcut" → DOWNGRADE
    "q5_literal_verb":      "no_literal_verb",       // or "<verb-line>" → DOWNGRADE
    "q6_sister_consistency": "consistent",           // or "inconsistent" → FLAG
    "passed": true                                    // false if Q0 conf < 0.8 OR any Q1–Q6 DOWNGRADE
  },
  "task_side_evidence": {
    "what_spec_doesnt_pin":         "...",
    "why_no_industry_standard":     "...",
    "agent_choice_defensibility":   "..."
  }
}
```

If Q0's `confidence_after_deep_recheck < 0.8`, **STOP and reclassify** without proceeding to Q1–Q6.
If Q0 passes but any of Q1–Q6 DOWNGRADEs, set `passed: false` and reclassify.

### Audit aggregator enforcement

The audit aggregator MUST reject any `task_side` label lacking the full `task_side_self_check.q0_deep_recheck` block (with all sub-fields populated) AND `task_side_self_check.passed = true` (with all 7 questions documented). Sub-agents that produce undocumented `task_side` labels — or labels with `q0_deep_recheck.confidence_after_deep_recheck < 0.8` but `passed: true` (a contradiction) — get re-judged with this checklist explicitly required.

### Why this exists

Three months of v3.2.x audits show a consistent pattern: when a sub-agent applies the literal "spec doesn't pin → C3.c task_side" rule, it under-weights the pinned-numeric-test signal, the literal-verb signal, and the math-shortcut signal. The result is over-attribution to `task_side`. This doubt checklist forces the sub-agent to walk through each signal explicitly, with evidence in the output JSON, before finalizing the high-bar `task_side` label.

**Worked example (var-es-estimation, the case that motivated this rule):**

A v12 audit Opus 4.7 sub-agent provisionally classified `fb-v12-opus47-r3-var-es-estimation` as `C3.c / task_side` because spec L22 *"draw from the selected component accordingly"* doesn't explicitly pin the RNG-call sequence. Running the doubt checklist:

- Q1: Failing tests are `assert isclose(RMSE, 0.1036, rtol=0.10)` — **PINNED NUMERIC** → DOWNGRADE
- Q5: Spec uses verb "draw from" — **LITERAL VERB** → DOWNGRADE
- Q4: Agent wrote `z * scales` instead of separate per-component draws — **MATH SHORTCUT** → DOWNGRADE

Three downgrades → reclassify to **A3.f / agent_conceptual** (math-equivalence shortcut bypassed literal spec procedure). The doubt checklist catches the over-routing automatically.

---

## Cross-cutting: hidden quality thresholds — NOT brittle pins

A common task-design pattern in QF-Bench is to **state the metric formula in the spec but withhold the threshold value**. The agent is told *"compute and report `rmse_bps`"* but not *"RMSE must be < 5 bps"*; the threshold lives only in the test. This is intentional difficulty design — the agent is forced to write production-quality code rather than aiming for the minimum that passes a stated gate.

**Diagnostic for a hidden-threshold task:**

1. The spec asks the agent to compute and report a quality metric (RMSE, max-abs-error, monotonicity, residual norm, etc.) in an output file
2. The spec does NOT state the numerical threshold the metric must satisfy
3. The test code imposes a numerical bound (e.g., `assert rmse < 5.0`)
4. **The oracle passes the bound with comfortable margin** (typically 30%+ headroom)

When all four hold, the task is **intentionally hard**, NOT brittle. The hidden threshold is a quality bar the agent must meet by writing correct code, not by tuning to the bound.

**Decision rule for failures on hidden-threshold tests:**

- **Oracle passes the bound by a comfortable margin** (e.g., RMSE 1.06 vs threshold 5; worst caplet 1.59 vs threshold 3) AND **agent fails** despite using the same calibrated parameters / pinned method / pinned init: this is `agent_coding` — a subtle implementation difference from oracle that the bound caught. Do NOT label `task_side`. The bound is doing its job.

- **Oracle barely passes the bound** (within 10-20% of threshold) AND **agent fails by ≤2x the same margin**: borderline. Look at whether the failure point is where the formula has known intrinsic bias (Kirk-deep-ITM, SABR-ATM, Bjerksund-Stensland-near-zero-T) — if yes, then `task_side / brittle pin` per industry-standards § D.4 etc. If the formula is well-behaved at the failure point, agent is `agent_coding`.

- **Oracle FAILS the bound** (oracle's `pytest tests/` does not pass): this is genuine task-side breakage, file an issue with maintainer.

**Worked example** (from QF-Bench v323): `hull-white-swaption` test_caplet_diffs_below_3bps. Spec gives RMSE definition only, no threshold. Oracle: RMSE = 1.06 bps, worst caplet = 1.59 bps (47% headroom under 3-bps bound). Agent codex-55 R3: identical calibrated `(a, σ) = (0.10008, 0.01107)` as oracle, but worst caplet = 3.50 bps. With identical params, the residual difference comes from the agent's HW caplet pricing function — a subtle long-T implementation bug. **Correct label: `agent_coding`, not `task_side`.** The 3-bps test is catching a real bug, not imposing a brittle pin.

**Counterexample** (from QF-Bench v323): `spread-option-kirk-margrabe` test_kirk_mc_agreement. Spec pins Kirk (1995) by name. Oracle uses Kirk and fails this test at the deepest-ITM grid point because Kirk has documented 3-5% intrinsic bias there (Harutyunyan & Borrás 2018; see `INDUSTRY_STANDARDS.md` § D.4). Multiple agents reproduce identically. Bound is tighter than the formula's known bias. **Correct label: `task_side / brittle pin`.** Bound is the bug, not the agents.

**Gap diagnostic — quick mental test:**

```
Oracle vs threshold ratio              | Verdict
---------------------------------------|------------------------------
Oracle ≤ 0.5 × threshold (≥50% margin) | Hidden-threshold quality gate.
                                         Agent failures = agent_coding.
Oracle 0.5-0.95 × threshold            | Borderline. Check formula's
                                         intrinsic bias at failure point.
Oracle > 1 × threshold (oracle FAILS)  | Genuine task-side breakage.
```

## Cross-cutting: `infra_failure / stale_spec_checkout` (added v3.2.9, expanded v3.2.10)

Some failures look like agent capability gaps but are actually **benchmark infrastructure bugs** — the harness operator's `tasks/` checkout diverged from `origin/main` at trial-launch time, so the agent received a non-canonical instruction.md while the verifier evaluated against `origin/main`-aligned test expectations. The maintainer's `origin/main` spec is correct; the trial environment served a different snapshot.

This pattern is **categorically different** from `task_side` (which means the spec on `origin/main` itself has a defect). It belongs to `root_cause_class = infra_failure` because the bug lives in the harness pipeline, not in the maintainer's spec or in agent reasoning.

### Two sub-patterns of stale_spec_checkout (both fire `infra_failure`)

**Sub-pattern 1: stale checkout of `origin/main`.** Operator's local `tasks/` is older than `origin/main` HEAD. Common cause: forgot to `git pull` before launching sweep. The agent receives a pre-edit snapshot of an instruction that has since been revised on `origin/main`.

**Sub-pattern 2 (added v3.2.10): pre-merge PR-branch served instead of merged `origin/main`.** Operator's `tasks/` is checked out to a *feature branch* HEAD that the maintainer subsequently revised before squash-merging. The agent gets a draft that differs from what eventually merged. **The verifier still ran the post-merge tests, because tests are typically packaged from a separate path or pulled fresh, while instruction.md was packaged from the stale branch checkout.** This sub-pattern is harder to detect because:

- The literal "spec edit predates trial" check from v3.2.9 may NOT fire (the squash-merge commit on origin/main can post-date the trial).
- The agent's instruction matches a real, committed git ref — just not `origin/main`.
- The data files may also be stale (e.g., form4 trials got PDF data files matching the pre-revision PR branch while origin/main had switched to XML — agents physically cannot succeed when input format mismatches reference data).

**v3.2.10 generalized rule:** stale_spec_checkout fires when there is ANY divergence between (a) the instruction the agent received and (b) the spec the verifier's tests assume — regardless of literal date ordering. The infrastructure failure is the divergence itself, not specifically that one is "older."

### Diagnostic — mandatory three-source verification

Apply BEFORE any classification on uniform-failure (κ ≥ 0.7) D1.* cases, AND any time a sister trial of the same task is suspected stale:

1. **Read the trial's literal instruction**: `agent/trajectory.json` step 2 (the user-role message sent to the LLM). This is what the agent actually saw.

2. **Read the canonical spec on `origin/main`**: `git show origin/main:tasks/<task>/instruction.md`. The simplest comparison; if the trial msg matches this, the trial got the canonical spec.

3. **If trial msg doesn't match `origin/main`**: identify distinctive binding clauses in `origin/main` (lines containing "must be one of", "must use exact", "exactly these keys", `--- enumerated list`, numbered formulas, etc.) and check if they appear in the trial msg. If clauses are absent, the trial got a non-canonical version.

4. **MANDATORY (v3.2.10): test-name verification.** Extract failing test function names from `verifier/test-stdout.txt`, then compare against `git show origin/main:tasks/<task>/tests/test_outputs.py` (extract `def test_*` names). The match ratio is the discriminator:

   | Match ratio | Verdict |
   |---|---|
   | All failing tests present on origin/main (100%) | **Real stale_spec_checkout** — verifier ran post-merge tests against pre-merge instruction. Flip to `infra_failure`. |
   | Some present, some not (mixed, e.g., 2/4) | Likely real (verifier was post-merge, but a few failing tests were renamed). Flip on majority match. |
   | None present (0%) | **Consistently stale** — verifier ran pre-merge test version; matches the pre-merge instruction. Agent's failure is *internal* to the pre-merge framework. NOT `stale_spec_checkout`. Use original A/B/C/D classification. |

   Without this check, audits over-flip "consistently stale" cases (where instruction and test were aligned, just at an older version) and miss the actual infra issue. Empirical: 3 mtm-xccy trials in v323 audit had 0/N test-name match → correctly NOT flipped per v3.2.10 strict reading.

5. **Cross-batch consistency check (added v3.2.10).** When sister trials of the same task are split across multiple sub-agent batches in a parallel audit, every sister trial that exhibits the same trajectory-vs-spec divergence MUST receive the same classification. If one batch flips a trial and another doesn't on indistinguishable evidence, that's a sub-agent inconsistency bug, not a real classification difference. The audit aggregator MUST run a final consistency pass:

   ```
   for each task in audit:
       trials = labels-of-task
       if any trial has root_cause_class = infra_failure AND
          another sister trial has identical trajectory-step-2 hash AND
          identical failing-test pattern AND
          different root_cause_class:
              flag for re-judge
   ```

### Routing

- If trial msg lacks distinctive content from `origin/main` AND failing-test names are present on `origin/main` (≥50% match) → `root_cause_class = infra_failure`, `top_mode_subrubric = D1.a` (or D1.b, D1.c, D1.f as applicable), `infra_subrubric = stale_spec_checkout`.

- If trial msg matches `origin/main` → standard A/B/C/D classification.

- If trial msg lacks distinctive content AND failing-test names are NOT on `origin/main` (0% match) → "consistently stale" — leave at original A/B/C/D classification, note the staleness in `judge_notes` for maintainer awareness but do NOT flip.

### Empirical scope (v323 audit final, 2026-05-06)

Systemic deep-read across all 75 v323 tasks (10-Opus-sub-agent re-judge + manual cross-batch consistency check) found stale_spec_checkout in **8 task families, 91 trials total**:

| Task | # Trials | Sub-pattern | Spec mismatch type |
|---|---|---|---|
| `13f-amendment-aware-crowding` | 21 | 1 (stale checkout) | Missing L41-44 enum (added Apr-23 `75d5f1a`) |
| `dupire-local-vol` | 21 | 1 / 2 (pre-merge) | Missing `/app/output/` pin (commit `5f750bc` post-dates some trials) |
| `etf-overlap-redemption-pressure` | 18 | 2 (PR-branch) | Missing L213 binding directives (commit `ef594c9` May-3) |
| `form4-cross-sectional-sale-pressure` | 17 | 2 (PR-branch + data-file mismatch) | PDF data files vs origin/main XML; missing per_filing schema |
| `compound-option-geske` | 4 | 1 | Missing L41 `must use exact` clause (commit `9903799` Apr-27) |
| `credit-migration-matrix` | 3 | 1 (severely stale) | Missing entire Steps 7-9 (commit `c2d4fbb` May-3) |
| `fx-carry-forward-hedge` | 2 | 1 (non-canonical draft) | Missing date_diagnostics.json key enumeration |
| `yield-curve-bond-immunization` | 1 | 1 | Missing KRD bucket key labels |

Other suspect uniform-failure tasks (`ipca-latent-factors`, `mtm-xccy-basis-desk`, `dcc-garch-portfolio-var`, `event-study-earnings`, `yield-curve-pca-dynamics`, `sec-10k-report-long`, `cliquet-ratchet-pricing`, `bl-regime-hmm`, `realized-vol-estimators`) all either received the date-appropriate spec OR were "consistently stale" per the test-name match check — their failures are real agent errors, not infrastructure.

**Lesson from the v323 deep-read pass:** the original v3.2.9 entry stated "exactly one" stale-spec case. That was wrong by 90 trials. The error was a methodology gap — v3.2.9 only checked the literal "spec edit predates trial" condition, missing sub-pattern 2 (PR-branch served before merge, where the trial date can predate the `origin/main` merge commit). v3.2.10 closes this gap.

### Why this matters for benchmark methodology

A κ=1.0 universal-failure signature on a controlled-vocabulary or schema task can be either:
- (a) genuine LLM-prior attractor (when agent received the spec and ignored the pin), or
- (b) stale_spec_checkout (when agent never received the pin),
- and is **distinguishable only by reading `trajectory.json` step-2** (and ideally also checking failing-test-name match for the sub-pattern discriminator).

Without trajectory verification, (a) and (b) are visually identical from aggregate metrics. The empirical v323 finding (91 of 807 = 11.3% of failures are infra) shows this is not a fringe issue — auditing without trajectory verification systematically over-attributes failures to model capability.

**Why this isn't `task_side`:**

`task_side` says "fix the spec" — but the spec on `origin/main` is correct. Calling stale-checkout failures `task_side` would mislead the maintainer into editing a working spec. The actionable owner is the harness operator (sync `tasks/` before launching, or pin `git_commit_id` in `config.json`), not the task maintainer.

**Distinguishing from `agent_conceptual / D1.a`:**

D1.a / agent_conceptual is "agent ignored explicit controlled vocabulary the spec enumerates." That requires the spec to actually enumerate the vocabulary IN THE INSTRUCTION TEXT THE AGENT RECEIVED. If the trajectory's step-2 user message lacks the enumeration, the agent isn't ignoring anything — they don't see it.

Before flagging the headline pattern of "universal vocabulary substitution despite explicit pin," verify the agent actually received the pin. If trajectory step-2 lacks it → `infra_failure / stale_spec_checkout`, not `agent_conceptual`.

## Provenance

- Empirical findings consolidated from: PR#180-209 deep review (5 PRs); HUMAN-REVIEW-SUMMARY (18 PRs); FINAL-SUMMARY 备注 (~25 entries); PQCat's broader comment review (33 PRs); 107 open PRs across pages 1–5 of the QF-Bench repo.
- Companion skill `qf-bench-review` encodes additional empirical findings (CreditRisk+ σ_k, Rama Cont ν > 2, Student-t GARCH Jacobian, ES discrete-distribution boundary, Student-t ES composition error).
- Format and rubric structure are mirrored from `qfbench-trajectory-error-analysis` (Terminal-Bench arXiv:2601.11868 §C.1–C.2 derived).
