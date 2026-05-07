# Operations Runbook

How to use the `qfbench-quant-correctness-analysis` skill — interactively (Phase 1, current state) and at scale (Phase 2, port from trajectory skill).

This skill ships **content only** (rubrics, prompts, taxonomy, examples) — no orchestration scripts. For interactive Claude usage, that's enough. For batch judging across many trials, see Phase 2 below.

---

## Phase 1 — Interactive use (current state)

The intended interactive workflow when the user points Claude at one failed trial folder, or asks "why did this agent fail?":

### 1. Locate the agent's solution and the task spec

```
trial_path = /path/to/jobs/<timestamp>/<task-id>/agent/
task_path  = /path/to/QuantitativeFinance-Bench/tasks/<task-id>/
```

Read:
- `<trial_path>/<agent-name>.txt` (raw stream / generated code)
- `<trial_path>/output/*.json` and `*.csv` (the agent's actual output files)
- `<task_path>/instruction.md` (canonical spec)
- `<task_path>/tests/test_outputs.py` (the verifier — what was *expected*)

### 1a. Insufficient-solution check — early exit before scoring

Before computing failure ratios or applying any rubric, check whether the agent's solution is sufficient to be judged on finance content at all. Three sub-cases:

| Case | What you see | Right action |
|---|---|---|
| **Empty generation** | `<agent>.txt` shows `Generated script (0 chars)` and an empty code section, OR `trial.log` confirms no code was produced. All tests fail at `FileNotFoundError` (file-existence tests). | **All 9 modes → `match=false`, `confidence=0.0`, `notes="insufficient solution: agent generated 0 chars of code"`.** Exit. The trial belongs to the trajectory skill (likely Premature Termination, Reasoning–Action Mismatch). No finance error to classify. |
| **Code produced but no output files** | Agent's code is non-empty (you can read formulas, model choices), but `output/` is empty or all `TestFileExistence` tests fail. Could be: agent's code crashed early, agent wrote to wrong path, agent forgot to call its own `main()`. | **Read the code anyway.** Classify A1/A2/A3 from the code's *intent* (formulas, model choices) even without numerical outputs. The output-tier tests (value range, monotonicity) will be skipped, but the formula-tier classification is still valid. Cite line numbers in the code; note in `notes` that the trial also has an upstream "no output produced" issue belonging to the trajectory skill. |
| **Code + outputs both present** | Normal case. `<agent>.txt` is non-empty, output files exist (even if values are wrong). | Proceed to step 2 normally. |

**Empty-generation pattern is most common in finance-zero single-shot trials**, where the model can fail to emit any code at all (timeout during generation, refusal, prompt confusion, harness bug). The `fb-fz-gpt5-american-option-fd-new` trial is the canonical example: model `azure/gpt-5`, 0 chars generated, exit code 0, all 54 tests fail with FileNotFoundError. Don't try to extract finance signal from this — it's pure trajectory failure.

**Important**: do NOT confuse "no output files" with "wrong output files". The latter is normal (agent's code ran, just produced wrong numbers) — proceed normally. The former (no files at all because no code ran or code crashed before any write) is the early-exit case.

### 2. Read the failure ratios first (Debug Workflow)

For each failing test, compute `ratio = agent_value / expected_value`. The ratio frequently identifies the mode before any rubric is read:

| Ratio | Failure mode | Where to look |
|---|---|---|
| ~100 or ~0.01 | **B1 — Unit / Scale** | Percent vs decimal; rates in %; `var_explained` as 86.32 vs 0.8632 |
| ~10000 or ~0.0001 | **B1 — Unit / Scale (basis points)** | Yield changes in bps vs decimal; DV01 scaling |
| ~−1 | **B2 — Sign Convention** | Loss vs P&L; ξ vs −ξ; long vs short; `−log(scale)` missing changes sign of gradient |
| ~1 + constant offset | **A2 — Missing Term** | Jacobian omitted; discount factor missing; boundary condition wrong |
| Hits parameter upper/lower bound (e.g. 100.0, 99.999, 4.0) | **C2 — Numerical / Optimization** | Wrong objective → optimizer pins parameter at bound; check likelihood formula |
| Widely varying ratios across rows | **C1 — Wrong Inputs** | Agent loaded wrong data subset, or applied formula to wrong column |
| Identical wrong value for all rows | **A2 / A3** — Uniform formula error | Same wrong constant applied everywhere; check parameterization |
| 0.0 or NaN | **C2 / B1** — Missing computation or sentinel | Agent skipped a step, wrote wrong output key, or sentinel mismatch |

### 3. Apply the financial sanity checks before any rubric

These catch issues the tests don't always cover:

**Volatility and correlation**
- Implied vols positive; equity range 5%–80% annualized; >150% suspicious
- Correlation matrices: symmetric, diagonal = 1, all ∈ [−1, 1], PSD (eigenvalues ≥ −1e-8)
- GARCH: ω > 0, α ≥ 0, β ≥ 0, α + β < 1; typical equity daily ω ≈ 1e-6, α ∈ [0.05, 0.15], β ∈ [0.80, 0.92], ν ∈ (2, 10]

**Risk measures**
- VaR positive (loss convention); VaR_99 > VaR_95 > VaR_90 (monotone)
- ES ≥ VaR at the same α, always. ES < VaR is a hard bug
- Normal distributions: ES_99/VaR_99 ≈ 1.13. Large deviations suggest formula error
- GPD shape ξ for equity daily: expect ξ ∈ (0.1, 0.5); ξ > 1 implies infinite mean (implausible); ξ < 0 means bounded tail (unusual)

**PCA outputs**
- All eigenvalues ≥ 0 (covariance matrix is PSD)
- Explained variance: each ∈ [0, 1]; cumulative non-decreasing; final = 1.0 (not 100.0)
- Yield curve PC1: all loadings same sign (level). PC2: monotone (slope). PC3: signs change exactly twice (curvature)

**Option prices**
- 0 ≤ call ≤ S·e^{−qT}; 0 ≤ put ≤ K·e^{−rT}
- Call ≥ max(S·e^{−qT} − K·e^{−rT}, 0)
- Put-call parity: C − P = S·e^{−qT} − K·e^{−rT} (≤ $0.01 for European)
- Implied vol positive; butterfly spread ≥ 0; calendar spread non-decreasing in total variance

**Fixed income**
- DV01 > 0 for long bond
- Modified duration ≈ maturity for zero-coupon
- Portfolio VaR ≤ Σ individual VaRs (subadditivity, elliptical)

### 4. Walk through each of the 9 mode rubrics

Open `TAXONOMY.md` (or each `prompts/<mode>.md`). For each mode, follow its Decision Procedure to a yes/no verdict, citing concrete evidence (line number, formula, output value).

#### 4a. Authorship pre-check — before matching any Class A mode (A1, A2, A3)

For each formula in the agent's code that you suspect is wrong, ask: **who authored the expectation that this formula should be different?**

| Case | When | Where the expectation comes from | Right mode |
|---|---|---|---|
| **1** | Spec-authored | `instruction.md` writes the formula explicitly OR cites a specific paper / textbook page | **A1 / A2 / A3** apply normally |
| **2** | Canonical / well-known | Spec names a classical model (BS, Merton, Hull-White, Heston, CIR, SABR, Vasicek, GBM, OU, Jamshidian, CRR binomial, Crank-Nicolson PSOR, Reiner-Rubinstein barriers, GARCH(1,1) MLE, parametric Gaussian VaR, …) with a *unique* canonical form that any working quant should know | **A1 / A2 / A3** apply normally |
| **2'** | Named method *with multiple variants* | Spec names a method that has multiple defensible variants (Newey-West NW87 vs NW94, Corrado 1989 vs Corrado-Zivney 1992, threshold ES vs Acerbi-Tasche, half-life formulas, IV approximations, post-1994 RV literature) | **C3.a** (or C3.b for post-1994), not A1/A2/A3 |
| **3** | Agent-invented under under-specified spec | Spec names a *procedural goal* ("parametric VaR decomposition", "Greek-based stress test", "factor-neutral hedge") but doesn't pin a formula AND multiple defensible formulas exist | **C3.c** primary; A2 secondary only if the agent's invented formula is also dimensionally inconsistent |

**Concrete steps for the pre-check:**

1. Open `instruction.md`. `grep` or scan for the formula symbols / function names the agent's code uses.
2. If you find a written formula → **Case 1**.
3. If the spec names a classical model without writing the formula → **Case 2** (or 2' if the method has known variants).
4. If the spec only names a goal and doesn't pin the formula → **Case 3**. In this case, prefer **C3.c** match. Only fall through to A2 if the agent's invented formula has its *own* internal dimensional / construction inconsistency.

**Why this matters:** The PR `barrier-garch-var` Haiku trial is a clean Case 3 example — instruction said only "computes a parametric VaR decomposition" with no formula, agent invented `pl_delta = delta · dS_pct` (missing S₀ factor). Without the pre-check, this looks like A2 (missing term) or B1 (off by S₀). With the pre-check, it's C3.c (under-specified spec → variant trap), with a task-side flag for `qf-bench-review` to write the VaR formula explicitly. Same root cause as PR #130 ml-credit-scoring (WoE smoothing).

#### 4b. Apply the cascade rule

When one root computational error causes many test failures, classify the root cause once, not each downstream symptom. Use `notes` to record cascades.

#### 4c. Localized vs systematic — set the `root_cause_class`

After matching a mode at the symptom level, classify the root cause by checking how localized the failure is:

| Pattern | Root cause class | Action |
|---|---|---|
| One specific (object × method × parameter) combination fails; sibling computations using the same method/object pass | **`agent_coding`** | Likely a typo / copy-paste-without-sign-flip / off-by-one. Cross-ref trajectory skill's Reasoning–Action Mismatch. The mode match is still valid (output IS wrong), but the root cause lives in implementation, not finance content. |
| Multiple related computations all wrong in a related way | **`agent_conceptual`** | Default for most matches. Genuine knowledge gap. |
| Agent's quant content is defensible; failure is from oracle bug, instruction under-specification, or test tolerance too tight | **`task_side`** | Match symptom mode at lower confidence; cross-reference `qf-bench-review`. |

**Concrete diagnostic**: when matching B2 (sign), B1 (scale), or A2 (missing term), look at the broader output:
- Does the *same* error (sign flip / scale / missing term) appear elsewhere where the same method or formula was applied?
- Does the agent's stated method/intent in the trajectory contradict the localized buggy line?

If only one specific combination fails out of many related ones (e.g., only `pw_put_delta` is wrong while `pw_call_delta`, `fd_put_delta`, `lr_put_delta`, `asian_pw_put_delta` are all correct), this is `agent_coding` — a localized bug in adapting code from one case to another. Set `root_cause_class: "agent_coding"` and note in `notes` that the trajectory skill's Reasoning–Action Mismatch likely also fires for this trial.

This separation is important for downstream consumers: a benchmark report should distinguish "5% of failures are from a model knowledge gap on Greek formulas" from "5% of failures are from typos in put-vs-call adaptation code." The mode tells you what the output looks wrong about; `root_cause_class` tells you why.

### 5. Output a labels report

Write a JSON object per mode following the schema in `prompts/system_judge.md`:

```json
{
  "wrong_model_measure":           {"match": false, "evidence_step_ids": [], "quote": "", "confidence": 0.95, "notes": "..."},
  "missing_extra_formula_term":    {"match": true,  "evidence_step_ids": [12, 13], "quote": "z = X / sigma_t", "confidence": 0.95, "notes": "..."},
  "wrong_parameterization":        {"match": false, "evidence_step_ids": [], "quote": "", "confidence": 0.85, "notes": "..."},
  "unit_scale_error":              {"match": false, ...},
  "sign_convention_error":         {"match": false, ...},
  "time_calendar_convention":      {"match": false, ...},
  "data_fabrication_wrong_source": {"match": false, ...},
  "numerical_optimization_failure":{"match": true,  "evidence_step_ids": [12, 13, 24], "quote": "nu = 99.999", "confidence": 0.90, "notes": "C2.c boundary binding, downstream cascade from A2.a"},
  "statistical_variant_mismatch":  {"match": false, ...}
}
```

Note: in this example A2 and C2 *both* match, but the C2 binding is *caused by* the A2 missing term. The judge's `notes` should indicate the upstream-most mode is the real classification; C2 is a downstream symptom. Some teams prefer to classify only the upstream cause; others prefer to record the full chain. Pick a convention and state it in your aggregator.

---

## Phase 2 — Batch judging (built, port-of-trajectory-skill scripts)

The orchestration scripts are now in `scripts/`:

| Script | Role |
|---|---|
| `task_context.py` | Load `instruction.md` + tests digest for one task |
| `list_failed_trials.py` | Walk a workspace and emit a manifest of failed trials |
| `extract_solution.py` | Build a per-trial judging bundle (task context + agent code + output files + failing tests parsed from `test-stdout.txt`) |
| `judge_trial.py` | Score one trial across the 9 modes via the LLM judge — with the **insufficient-solution pre-flight gate** that short-circuits empty/stub trials at $0 cost |
| `judge_all.py` | Async batch orchestration with per-provider concurrency caps, hash-based resume, and budget cap |
| `aggregate_labels.py` | Aggregate `labels.json` files across the workspace into CSVs + a markdown report |
| `seed_calibration.py` | Pick N random trials for a hand-labeling calibration round (Cohen's-κ vs judge) |

### End-to-end usage

```bash
# 1. Set up workspace layout: <root>/<combo>/<trial>/{result.json, agent/}
#    (combo = "<harness>_<model>", e.g., "claude-code_sonnet45")

# 2. Sweep + judge
python scripts/judge_all.py \
    --root /path/to/workspace \
    --tasks-root /path/to/tasks \
    --judge-model anthropic/claude-opus-4-6 \
    --concurrency 2 --judge-concurrency-per-trial 3 \
    --bundle-max-tokens 40000 \
    --backoff-max-attempts 8 \
    --budget-usd 100

# 3. Aggregate
python scripts/aggregate_labels.py \
    --root /path/to/workspace \
    --out /path/to/reports
```

The `judge_all.py` run is resumable — re-running it after Ctrl-C or budget cap will skip trials whose `labels.json` hash matches the current bundle + prompt set + judge model.

### Calibration step

```bash
python scripts/seed_calibration.py --root <root> --n 20 --out calibration/
# Hand-fill calibration/human_labels.csv (columns: trial_path, mode, human_match)
python scripts/aggregate_labels.py --root <root> --human-labels calibration/human_labels.csv --out reports/
# → reports/agreement.csv with Cohen's-κ per mode + overall
```

If a mode has Cohen's-κ < 0.7, tighten that mode's rubric and re-run. Iterate until all modes ≥ 0.7.

---

## Phase 3 — Running batches at scale: operational lessons

These are gotchas surfaced by a 50-trial validation run on the
`when2buy/fb-bench-tracker` workspace (May 2026, opus-4.6 judge, ~$118 spend).
Bake them into your run setup before kicking off the next batch.

### 3a. `git lfs pull` after cloning the trials repo

The `fb-bench-tracker` repo stores ~38% of trial trajectories (`agent/trajectory.json`)
as **git-LFS pointer files**, not real content. A plain `git clone --depth=1`
gets you the pointers but not the trajectories. If the bundle build fails with

```
[sweep] ERROR <trial>: bundle build: JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

inspect any failing `trajectory.json`:

```bash
head -c 50 /path/to/<trial>/agent/trajectory.json
# version https://git-lfs.github.com/spec/v1   ← LFS pointer, not content
```

Fix:

```bash
# If git-lfs isn't installed (macOS without brew):
curl -sL https://github.com/git-lfs/git-lfs/releases/download/v3.5.1/git-lfs-darwin-arm64-v3.5.1.zip -o /tmp/lfs.zip
unzip /tmp/lfs.zip -d /tmp/
chmod +x /tmp/git-lfs-3.5.1/git-lfs
cd /path/to/fb-bench-tracker
/tmp/git-lfs-3.5.1/git-lfs install --local
/tmp/git-lfs-3.5.1/git-lfs pull
```

LFS-pulled trial dirs add ~600MB-1GB to the repo. If disk is constrained,
sparse-checkout only the trial-prefix you need (e.g., only `fb-pr-*`).

### 3b. Python 3.9 asyncio Semaphore loop binding (already fixed in `judge_all.py`)

If you're running on Python 3.9 and see this error in the second wave of trials:

```
[sweep] ERROR <trial>: judge: RuntimeError: Task <Task pending name='Task-N' ...>
got Future <Future pending> attached to a different loop
```

the cause is that `asyncio.Semaphore(N)` constructed BEFORE `asyncio.run()`
binds to a default loop that `asyncio.run()` later replaces. The first few
trials acquire the semaphore immediately (no `wait()`), so they don't trip
the bug; later ones must wait, which crosses loops and explodes.

`judge_all.py` already constructs Semaphores INSIDE `_run()` (the running
loop), so this should not bite you with the current scripts. If you fork
the script and move the construction back to `main()`, the bug returns.
Python 3.10+ doesn't have this issue.

### 3c. Anthropic 800K-tok-per-minute org rate limit (the dominant pain point)

With opus-4.6 and the default `--bundle-max-tokens 80000`, each mode call
sends ~16K-80K input tokens depending on bundle size (claude-code multi-step
trials run heavy because of large trajectories; finance-zero trials run
light). At default concurrency `8 trials × 9 modes parallel = 72 in-flight`,
the burst hits 1-5M input tokens/min → **rate limit fires within seconds**.

The retry-with-backoff (`--backoff-max-attempts 8`) sleeps `1.5 × 2^attempt`,
capped at 60s. Even with 8 attempts the total wait is ~95s — still inside the
1-min rate window if the burst is heavy enough.

**Recommended settings by judge model:**

| Model | `--concurrency` | `--judge-concurrency-per-trial` | `--bundle-max-tokens` | `--backoff-max-attempts` | Per-call input tokens (typical) |
|---|---|---|---|---|---|
| **gpt-5** (default) | 8 | 9 | 80000 | 4 | varies; OpenAI rate caps differ from Anthropic |
| **claude-opus-4-6** (heaviest) | **2** | **3** | **40000** | **8** | ~16K-30K |
| **claude-sonnet-4-6** | 4 | 6 | 60000 | 6 | ~12K-25K |
| **claude-haiku-4-5** | 6 | 9 | 80000 | 4 | ~10K-20K |

If trials still fail with rate-limit errors, the next step is to drop to
`--concurrency 1 --judge-concurrency-per-trial 2` (a worst-case sequential
run) and accept the longer wallclock. The 50-trial validation needed this
fallback for 7 heavy claude-code trials with ~1 MB trajectories.

**Identifying rate-limit failures post-hoc:**

```bash
python3 -c "
import json, glob
fail = 0
for lf in glob.glob('<root>/*/*/agent/labels.json'):
    data = json.loads(open(lf).read())
    for mode, label in (data.get('labels') or {}).items():
        if 'RateLimitError' in (label.get('error') or '') or \
           'judge call failed' in (label.get('notes') or ''):
            fail += 1
print('rate-limited mode calls:', fail)
"
```

If non-zero, delete the affected `labels.json` and `bundle.json`, then re-run
`judge_all.py` with reduced concurrency. The hash-based resume will skip
already-completed trials.

### 3d. Insufficient-solution pre-flight gate (cost saver)

`judge_trial.py` has a deterministic gate that short-circuits trials with
`agent_code < 500 chars AND no output_files AND no failing-test numerical
comparisons`. Hits Case 1 of the system_judge prompt's three-case
insufficient-solution guidance.

In the 50-trial validation, the gate would have fired on **24/49 trials**
(0 false positives), saving ~$56 of the $118.63 actual spend. Today's runs
benefit automatically.

Output trails: gate-skipped trials get `gate_skipped: true` on each
mode's label, `total_cost_usd: 0.0` on the trial-level payload, and a
`gate_reason` field explaining the skip. The aggregator's `labels.csv`
preserves `gate_skipped` so downstream analysis can bucket these
separately from real LLM-judged "no match" labels.

If the gate fires on a trial you think SHOULD be evaluable, lower the
threshold (`_INSUFFICIENT_CODE_CHARS_THRESHOLD` in `judge_trial.py`) or
just delete the gate-synthesized `labels.json` and rerun with
`--bundle-max-tokens` bumped — the gate's check only looks at the bundle
contents.

### 3e. Pricing table maintenance

`DEFAULT_PRICING` in `judge_trial.py` is keyed on model substring match.
When a new model (e.g., `claude-opus-5`, `gpt-5.5`) lands, add it
explicitly — otherwise `cost_usd` will silently stay at $0 for that model
and your budget cap won't trigger.

Current entries (May 2026):
- `gpt-5`, `gpt-5-mini`, `gpt-4o`
- `claude-opus-4-5`, `claude-opus-4-6`
- `claude-sonnet-4-5`, `claude-sonnet-4-6`
- `gemini-2.5-pro`, `gemini-2.5-flash`

### 3f. Concurrent calls and budget cap (soft cap)

`--budget-usd N` is a *soft* cap: it triggers when cumulative cost crosses
N, but in-flight concurrent calls still complete. With `--concurrency 6`
and 9 modes per trial, up to 54 calls can be in flight at the moment the
cap fires — so actual spend can land 5-15% over the cap. Set the cap with
this overshoot in mind. The 50-trial run spent $118.63 with a $100 cap.

### 3g. Workspace layout requirement

`list_failed_trials.py` expects `<root>/<combo>/<trial>/` where `combo`
contains an `_` (it splits on `_` to get `(agent_harness, model)`). Flat
layouts like `<root>/<trial>/` are NOT auto-detected — you'll get
"discovered: 0, eligible: 0" with no error.

If your trials are flat (e.g., `fb-bench-tracker/trials/fb-pr-h45-foo`),
build a sibling workspace via symlinks based on trial-name prefix:

```python
# Example shim — adapt the prefix→combo mapping to your naming scheme
PREFIX_TO_COMBO = {
    "fb-pr-h45": "claude-code_haiku-4.5",
    "fb-pr-s45": "claude-code_sonnet-4.5",
    "fb-pr-opus46": "claude-code_opus-4.6",
    "fb-fz-gem": "finance-zero_gemini-2.5-pro",
    "fb-fz-gpt5": "finance-zero_gpt-5",
    # ...
}
```

then symlink each trial into `<workspace>/<combo>/<trial>` matching its
prefix. The combo name only needs to contain `_` to be discoverable —
the actual `agent_harness` / `model` strings don't have to match anything
upstream.

---

## Skill maintenance — rule-consistency self-check

**Mandatory step when adding a new general rule** (introduced v3.2.7).

Rule-based skills accrete worked examples over time. New general rules
are correct in the abstract but can silently contradict old worked
examples. Judges (correctly) follow the more-specific older example,
so the new rule has no effect.

**The cross-sectional-momentum mislabel** (v3.2.5/v3.2.6 → v3.2.7) is the
canonical case: when v3.2.5 added the hidden-quality-threshold rule
("oracle drift ≪ test threshold → agent_coding"), the older v3.2.1 worked
example for cross-sectional-momentum had inline pre-labeling
("(or task_side... as it does here for cross-sectional-momentum)") that
contradicted the new rule. Judges followed the more-specific older
example. 8 trials in v323 mislabeled.

**Self-check procedure** to run when adding ANY new rule that affects
routing or classification:

1. **Search for inline pre-labelings** that hardcode a verdict for a
   specific task or trial:
   ```bash
   grep -nE "as it does here|canonical .*case|canonical case explicitly|\
   for [a-z-]+ specifically|task_side .*if .*spec mandated|\
   (route|label|classify) .* as `[a-z_]+`" SKILL.md TAXONOMY.md
   ```
2. **For each match**: verify the example's pre-labeled verdict is still
   consistent with the new rule. Apply the new rule's diagnostic test
   (e.g., for v3.2.5: compute oracle / threshold ratio; for v3.2.6:
   classify into Pattern A/B/C).
3. **If inconsistent**: update the example to match the new rule, OR
   remove the pre-labeling and replace with "see § new-rule" cross-reference.
4. **Document in CHANGELOG**: list every example you audited and whether
   it was updated, removed, or already consistent.

**Never** add a new rule without running steps 1-4. The cost of skipping
is measured in mis-attributed labels across the entire benchmark corpus.

---

## Parallel sub-agent audit pipeline rules (added v3.2.10)

When running large-scale audits via parallel sub-agents (the typical pattern: 8–16 sub-agents fanning out a 100–800 trial corpus), the following rules are MANDATORY to prevent cross-batch inconsistencies that would otherwise undermine audit reliability.

### Rule 1: Uniform prompt template across all sub-agents

**Bug pattern (observed v323 Phase 4):** batches 0/1 ran with leaner prompts (3 skill files: TAXONOMY, CHANGELOG, memory) while batches 5–9 had the full bundle (5 skill files + 2 memory files + batch list). Result: batches 0/1 took a stricter literal reading of the rule and missed 2 flips that batches 5–9 correctly identified on identical evidence.

**Required:** all sub-agents in one audit run MUST get the same set of skill files in their prompt. Concretely, every sub-agent prompt must include:

```
1. SKILL.md
2. TAXONOMY.md (the operative rules)
3. prompts/system_judge.md (formal routing)
4. CHANGELOG.md (latest version semantics)
5. INDUSTRY_STANDARDS.md
6. Relevant memory notes (at minimum the canonical examples for each rule)
7. Per-trial batch list
```

If memory files are task-specific, every sub-agent gets ALL of them — even sub-agents working on tasks that don't reference a particular memory note. Cost is small (a few extra tokens per agent); cost of inconsistency is large (audit reliability).

### Rule 2: Mandatory cross-batch consistency check

**Bug pattern:** sister trials of the same task split across batches sometimes get inconsistent classifications — one batch flips, another doesn't, on indistinguishable evidence. The aggregator only catches this via post-hoc inspection.

**Required:** the audit aggregator MUST run a final consistency pass before publishing results:

```python
for task in distinct_tasks_in_audit:
    trial_groups = group_by_signature(trials_of_task)
    # signature = (trajectory-step-2 hash, failing-test-set, agent_code_pattern)
    for sig, trials_with_sig in trial_groups:
        classes = {trial.root_cause_class for trial in trials_with_sig}
        if len(classes) > 1:
            flag_for_re_judge(trials_with_sig, reason="cross-batch inconsistency on indistinguishable evidence")
```

The flag-for-re-judge cases should be re-audited by a single sub-agent (with the full prompt template per Rule 1) to settle the disagreement. Empirically v323 Phase 4 had 2 such cases that were settled by manual cross-check.

### Rule 3: Test-name verification is a precondition for stale_spec_checkout flips

**Bug pattern:** sub-agents see a trajectory missing distinctive content from origin/main, conclude "stale checkout," and flip without checking whether the failing tests actually exist on origin/main. When tests don't exist on origin/main (i.e., test was renamed or task pre-merge had different test names), the trial is "consistently stale" — instruction and verifier were aligned at an older version, so the agent's failure is genuine within that older framework. Flipping such cases over-attributes to infrastructure.

**Required:** before classifying any trial as `infra_failure / stale_spec_checkout`, the sub-agent prompt must explicitly require this check, and the output JSON must include the match ratio:

```json
{
  "old_class": "agent_conceptual",
  "new_class": "infra_failure",
  "test_name_verification": "4/5 on origin/main",  // MUST be present
  ...
}
```

The aggregator rejects any flip where `test_name_verification` is missing or shows 0% match (flag for re-judge).

### Rule 4: Ratio-test exit criteria for batch quota

When a batch's "verified-correct" count exceeds 90% of trials with 0 flips (e.g., batch 0 returned 14/15 verified-correct with 0 flips), the aggregator should sample-spot-check 2-3 of the "verified-correct" trials in that batch by comparing to sister trials in other batches. If sister trials of the same task were flipped elsewhere, those "verified-correct" calls are suspect — re-judge them with a fresh sub-agent and full prompt context.

Empirically: Phase 4 batches 0 and 1 had this ratio (14/15 and 14/15 verified-correct, 0 flips). Spot-check found 2 missed flips that were flipped in batches 5–9 on identical task patterns.

---

## Configuration

| Variable | Purpose |
|----------|---------|
| `QFBENCH_TASKS_ROOT` | Path to the QF-Bench `tasks/` folder. Resolution order: CLI flag → env → sibling `../QuantitativeFinance-Bench/tasks` → degraded "task_context: missing" with one warning. |
| `OPENAI_API_KEY` | Required for the default `gpt-5` judge. |
| `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` | Required when `--judge-model` or `--ensemble` uses those providers. |

---

## Companion skills

| Use case | Skill |
|---|---|
| Vet a task before merging (instruction + reference solution + tests) | `qf-bench-review` |
| Classify how an agent behaviorally failed (Execution / Coherence / Verification) | `qfbench-trajectory-error-analysis` |
| Classify what kind of finance error an agent made in its math | **this skill** (`qfbench-quant-correctness-analysis`) |

The three skills are independent and complementary. A given trial can match modes from `qfbench-trajectory-error-analysis` (e.g., "premature termination") *and* `qfbench-quant-correctness-analysis` (e.g., "missing Jacobian") simultaneously — they're orthogonal axes.

---

## Provenance

- 9-mode taxonomy: empirically derived from review of ~75 PRs on the QF-Bench repository (see TAXONOMY.md "Provenance" section).
- Rubric format and JSON output contract: mirrored from `qfbench-trajectory-error-analysis` (Terminal-Bench arXiv:2601.11868 §C.1–C.2 derived).
- Companion skill `qf-bench-review` encodes the *task-side* counterpart of these findings (CreditRisk+ σ_k convention trap, GARCH MLE local-optima, Rama Cont ν > 2 lower bound, Student-t GARCH Jacobian, ES discrete-distribution boundary, etc.).
