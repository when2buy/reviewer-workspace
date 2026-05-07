# Failure Mode: Wrong Parameterization / Convention Default (A3)

*Empirical source: PR #195 creditrisk-plus-model (σ_k = std vs CV); PR #120 barra-cne6-risk (Barra USE4 sqrt-mcap weighting); PR #66 portfolio-risk-attribution (Sharpe excess vs raw, simple vs compound rate conversion); PR #61 pairs-trading-cointegration (annualization basis); PR #122 barra-cne6-risk (factor-vs-total variance denominator); PR #133 shrinkage-meanvar-portfolio (target vs drifted weights); PR #86 dcc-garch (Engle Q̄ convention).*

## Framing

Same formula symbol, different definition. The agent reads "σ_k" or "Sharpe" or "ATM" or "weights" and resolves it to a *convention* different from the one the test pins. Includes distribution parameterization (Gamma shape vs scale; Student-t standard vs standardized), proprietary/institutional convention defaults (Barra USE4 sqrt-mcap weighting, Engle DCC Q̄), metric definition conventions (Sharpe excess vs raw; ATM spot vs forward; factor-vs-total variance denominator; annualization basis), and backtest state-tracking (target vs drifted weights between rebalances).

Distinguish from C3: C3 is *named-method variants* (Newey-West NW87 vs NW94 — different formulas under the same name); A3 is *parameter-definition variants* (σ_k = std vs CV — same formula, different definition of what σ_k means).

## Decision Procedure

1. Identify the parameter or metric whose definition could resolve to multiple conventions in standard finance literature. Common candidates: σ in distribution params; weights (target vs drifted); Sharpe (excess vs raw); ATM (spot vs forward); annualization basis (deployed vs total); rate conversion (simple vs compound).
2. Check what the task's instruction actually states. Often the instruction names only the symbol without pinning the convention.
3. Check what the test pins. Usually the test fixes a specific numerical convention via the expected value.
4. Identify what the agent's code resolves it to. Two correct readings producing different numbers = ambiguity. Agent picking the non-test-aligned reading = match.
5. **A3 vs A1**: A1 changes the *model class* (BS → CEV); A3 keeps the model and changes a *parameter definition* (σ = std → σ = CV).
6. **A3 vs C3**: A3 is parameter definitions (`σ_k`, `Sharpe`, `weights`); C3 is named-method variants (`Newey-West`, `Corrado test`, `Acerbi-Tasche ES`).
7. **A3 vs B1**: B1 is unit/scale of a well-defined number; A3 is the definition itself.
8. **A3 vs A2 (cascade priority — important).** A3 fires when the agent's code is **internally consistent under a chosen convention** that disagrees with the test's pinned convention. If the agent's formula is structurally wrong (missing/wrong chain-rule term, missing factor, dimensional inconsistency) and the output landing in a different-looking convention is a *consequence* of that structural bug rather than an explicit convention choice, **A2 owns it**; A3 returns `match: false` with notes redirecting to A2. Concrete test: ask "did the agent INTENTIONALLY pick a convention, or did they write a wrong formula that happens to produce wrong-convention output?" If the latter, A2.

9. **A3 vs D1.g (engineering-layer — mandatory pre-check).** Before matching A3, ask: **does the agent's wrong value come from their QF reasoning, or from a library API default they didn't think to override?**
   - **Plain-English defense test:** can the agent defend the choice in plain English? "I picked ddof=0 because the Gaussian MLE requires biased variance" — defensible reasoning → A3 with `agent_conceptual`. "I just used `df.sort_values()` — didn't realize it was unstable" — no reasoning, library default surprised them → **D1.g**, redirect.
   - **One-keyword-fix test:** can the agent's code be made correct by changing exactly one keyword argument (`kind='stable'`, `keep='last'`, `dtype=float`, `errors='raise'`, `sort_keys=True`, etc.) without touching any formula, model class, or convention pick? Yes → **D1.g**.
   - **Mechanism-locality test:** is the bug at the data-engineering layer (CSV parsing, sort, dedup, merge, type coercion, JSON round-trip, regex)? Engineering layer → **D1.g**. Quant-formula layer → A3.
   - When D1.g applies, return A3 `match: false` with notes redirecting to D1.g. This is the only quant-axis mode that gets subsumed by a D-axis mode (see TAXONOMY § "D1.g special case"). Rationale: classifying a pandas API quirk as "wrong parameterization" mis-attributes engineering bugs as QF-knowledge gaps.
   - Concrete example: `cross-sectional-momentum` agent writes `df.sort_values('date').drop_duplicates(keep='last')` → wrong total_return. Code's QF logic is identical to oracle's; bug is pandas non-stable-sort default. Redirect to D1.g, NOT A3.

## Exclusions

- Wrong numeric value of a well-defined parameter (that's a code error, not a convention error).
- Pure unit/scale (% vs decimal) → B1.
- Pure sign (+ vs −) → B2.
- Methodological variants of a named method → C3.
- **Library/API default-induced wrong values where QF logic is correct → D1.g.** See decision-procedure step 9 above. Do NOT match A3 for these.

## Sub-rubrics

- **A3.a — Distribution parameterization.** Gamma `(α, β)` shape & rate vs shape & scale (scipy uses scale). Student-t standard `t(ν)` (variance = ν/(ν−2)) vs standardized (variance = 1, scale = `sqrt((ν−2)/ν)`). NegBin failures vs trials. CreditRisk+ σ_k: std of mixing variable (`Var(S_k) = σ_k²`) vs coefficient of variation (`Var(S_k) = σ_k²/μ_k²`).
- **A3.b — Proprietary / institutional convention default.** Barra USE4: sqrt-market-cap weighting (not linear, not equal); double-pass standardization with winsorization; OLS-style t-stat (not HAC); Taylor-approximation EWMA `λ = 1 − ln(2)/halflife` (not exact `0.5^(1/HL)`). Engle (2002) DCC: `Q̄ = (1/T) Σ z_t z_t'` (sample 2nd moment) vs `np.corrcoef` (demeaned correlation). LLM training data covers conceptual layer but not vendor-handbook details.
- **A3.c — Metric definition convention.**
  - Sharpe ratio: excess return `(r − r_f)/σ` vs raw `r/σ`.
  - ATM: spot `K = S₀` vs forward `K = F_T = S₀·e^{(r−q)T}`.
  - Factor-vs-total variance denominator: `style_pct + industry_pct = 1` (normalized within factor variance) vs `= factor_pct` (denominator is total variance).
  - Annualization basis: `(1+r)^(252/N)−1` where N = trading days *with position* vs total trading days.
  - Return-frequency conversion: simple `r_monthly = r_annual/12` vs compound `(1+r_annual)^(1/12)−1`.
- **A3.d — Backtest state-tracking convention.** Between rebalances, portfolio tracks *target weights* (held constant, no drift) vs *actual weights* (drifted by daily returns, snapped back at rebalance). Same for `w_old` in turnover: previous target vs current drifted weight. Both defensible; tests pin one.
- **A3.f — Agent overthink / non-industry-standard convention default.** *(Added May 2026 v3.1; refined v3.2.)* The agent picks a less-common variant of an under-specified convention where a clear industry-standard variant exists. A senior quant with industry experience would either (i) check the instruction for a citation/reference and use that variant, or (ii) apply the industry-standard default. The agent's failure to do either reflects a knowledge gap about industry common sense, not spec ambiguity. **`root_cause_class = agent_conceptual`** (not `task_side`).
  - **v3.2 prerequisite (mandatory).** Before classifying as A3.f, run the **Spec-Citation Extraction Pre-check** in `prompts/system_judge.md`. A3.f only fires when the regime is `spec-delegates` (eponym named, formula not pinned) or `silent` AND a clear industry-standard variant still exists. If the regime is `spec-authored` (any of the 8 patterns: author cite, section ref, cross-file ref, inline TeX, library kwarg, pinned param, day-count pin, pseudocode fence), the failure is **A2 / A3.a–e — failure to follow an explicit pin**, not A3.f. See `references/spec_citation_patterns.md` for the full pattern catalog and the empirical examples that motivated the v3.2 refinement (~31 V11 cells were misrouted to A3.f under v3.1 because the pre-check missed cross-file refs and pseudocode fences).
  - *Examples.* `ddof=0` for sample std when industry default is `ddof=1`; `× √365` annualization for trading-day returns when standard is `× √252`; loss-space VaR reported as a return (negative sign) when standard is positive loss; threshold-form ES `E[L|L>VaR]` when industry typically uses the rank-based Acerbi-Tasche form; `pct_change` with `fill_method` defaults to `pad` (deprecated) when explicit handling is required; non-stable PCA eigenvector signs without an anchor when standard practice is "first loading positive" or "anchor to reference series".
  - *Distinguishing A3.f from A3.a/b/c.* A3.a/b/c describe specific named conventions where the agent's choice is internally consistent but disagrees with the test. A3.f is the meta-rubric: the agent's variant is *less common in industry* than the test's variant, AND the spec offered no signal to prefer the agent's choice over the industry default.
  - *Distinguishing A3.f from `task_side`.* Apply the Industry-Standard pre-check (system_judge.md). If the spec has any citation/reference, OR a clear industry standard exists, the failure is A3.f `agent_conceptual`. Only when neither condition holds is `task_side` appropriate. **By construction, A3.f raises the bar for `task_side` significantly:** under v3.1, `task_side` should fire only on (i) genuinely under-specified procedural goals with no industry default, (ii) brittle test anchors on non-portable internal values (e.g., scipy iteration counts), or (iii) genuine spec ambiguity / oracle bugs.

## Single-shot applicability

Applies fully to `solution_kind == finance-zero`. Judge the generated code's parameter definitions against what the test pins.

## QF-Bench finance examples

POSITIVE — CreditRisk+ task: instruction defines σ_k as "volatility of default rate" (a standard deviation) but writes line 29 `Var(S_k) = σ_k²/μ_k²` (the CV reading). Tests use `Var = σ_k²` (std reading; matches the prose). Agent follows the line-29 formula literally → wrong Gamma shape → systematically low VaR (5.9 vs 6.5 oracle). Match A3.a.

POSITIVE — Multi-factor risk task: instruction says "All `*_pct` are fractions of total variance, with style/industry split referring to contributions to the factor variance component." Two defensible readings: (i) split *within factor variance* (style + industry = 1, denominator = factor variance), or (ii) split *of total variance* (style + industry = factor_pct, denominator = total variance). Agent picks (i); test pins (ii). Match A3.c.

POSITIVE — Pairs-trading task: instruction defines `annualized_return = (1 + total_return)^(252/N) − 1` with "N = trading days with position." Agent uses `len(equity_arr)` (~2014, full sample). Annualization stretched over period including 59-row warmup with no position → understates annualized return. Match A3.c.

NEGATIVE — Task: "Compute Sharpe with `r_f = 0`." Agent does `r/σ` and the test compares against the same. No convention mismatch. No match.

NEGATIVE — Task names "Newey-West with automatic bandwidth." Agent picks NW(1987), test expects NW(1994). That's a method-variant ambiguity → C3, not A3.

# Inputs

## Solution kind

{{TRAJECTORY_KIND}}

## Task instruction (instruction.md)

{{TASK_INSTRUCTION_MD}}

## Task tests digest

{{TASK_TESTS_DIGEST}}

## Agent solution

{{AGENT_SOLUTION}}

# Output

Return ONLY the JSON object specified in the system prompt. No fences, no prose.
