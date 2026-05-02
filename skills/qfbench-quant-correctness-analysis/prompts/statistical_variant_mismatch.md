# Failure Mode: Statistical Variant Mismatch (C3)

*Empirical source: PR #88 event-study-earnings (Corrado test variants); PR #76 fama-macbeth-risk-premia (Newey-West "automatic" bandwidth); PR #126 merton-cds-copula (threshold ES vs Acerbi-Tasche); PR #131 garch-vecm-cointegration (3 defensible half-life formulas); PR #65 bond-portfolio-analytics (Newton-Raphson vs bisection+Newton); PR #107 realized-vol-estimators (Bandi-Russell vs BNS post-1994 RV variants); PR #169 implied-vol-approximations (Brenner-Subrahmanyam vs Li 2005 vs CMH); PR #130 ml-credit-scoring-fairness (non-canonical WoE smoothing on proportions vs textbook on counts); PR #182 var-es-estimation (ES variants); discrete `np.quantile` method.*

## Framing

The instruction names a statistical method by its eponym (Newey-West, Corrado, Acerbi-Tasche, …) without writing the formula, but multiple variants of that method exist in the literature and produce different numbers. The test pins one variant; the agent picks another defensible variant from training memory. The QF-Bench analog of the "Formula by reference" trap.

This is the **single most-validated mode in the dataset** — 5+ PRs hit it directly across diverse methods.

Distinguish from A3: A3 is *parameter-definition variants* (`σ_k = std vs CV`); C3 is *named-method variants* (`Newey-West NW87 vs NW94`).

## Decision Procedure

1. Identify any named method in the instruction (especially named after a person, paper, or eponym).
2. Check whether the instruction reproduces the formula. If only the *name* is given, the variant is under-specified.
3. Check the agent's implementation. Does it match the test's pinned variant, or a different one in the literature?
4. If agents from different training mixes will pick different variants, and the test pins one specific variant without naming it, match.
5. **C3 vs A3**: A3 is a *parameter* with multiple definitions; C3 is a *method* with multiple formulas under the same name.
6. **C3.c (inverse trap)**: when the *reference* uses a non-textbook variant (e.g., WoE smoothing on proportions instead of standard counts), the agent following standard practice will fail. Both directions of variant ambiguity match C3.

## Exclusions

- The instruction reproduces the exact formula → no variant ambiguity, no match.
- Different agents converge to the same variant → no variant ambiguity.
- Parameter-definition issue (A3).
- Numerical solver issue (C2).

## Sub-rubrics

- **C3.a — Multiple equally-named methods.**
  - **Newey-West "automatic" bandwidth.** NW(1987), NW(1994), Andrews (1991), Schwert. All produce different lag counts for the same T. NW(1994): `floor(4·(T/100)^(2/9))`. NW(1987): same formula but slightly different rounding rule. Andrews: data-dependent plug-in.
  - **Corrado test (1989).** Original 1989 form, Corrado-Zivney 1992 multi-day standardization, Eventus/SAS macro variant. Different denominators and aggregation rules — all produce different `corrado_z` numbers.
  - **Expected Shortfall.** Threshold form `E[L | L > VaR]` vs rank-based Acerbi-Tasche `mean(top-⌈(1−α)·N⌉ losses by rank)` vs Wikipedia general formula `−(1/α)·[E[X·𝟙_{X≤x_α}] + x_α(α − P[X≤x_α])]` (handles atoms correctly). Identical for continuous distributions; differ when there's an atom at VaR (always the case on discrete loss grids).
  - **VECM half-life.** `−ln(2)/ln(1+α[0])` (single-α simplification) vs `ln(2)/|α[0]|` (continuous-time limit) vs `−ln(2)/ln|1+β'α|` (rigorous spread eigenvalue, used by pairs-trading desks).
  - **Numerical method variants.** Newton-Raphson vs bisection+Newton vs Brent's method. Can fail to converge for edge cases (deep-discount long bonds; low strikes).
- **C3.b — Post-1994 / recent-literature variant trap.** When the cited method comes from a paper after ~1994 (e.g., Bandi-Russell 2006 RV with noise correction, Barndorff-Nielsen-Shephard 2004 bipower variation, Li 2005 trigonometric IV approximation, Corrado-Miller-Hallerbach rational IV approximation, Acerbi-Tasche 2002), training-data depth varies across agents. Pre-1994 classical methods (Black-Scholes, Black 76, Heston 1993) are uniformly trained; post-1994 papers less so. Each agent picks a different variant from memory and fails on a different test.
- **C3.c — Non-canonical reference variant / under-specified procedural goal (inverse trap).** Two flavors, both involving spec under-specification:
  - **Flavor 1: Reference uses a non-textbook variant.** Spec names a well-known method without writing the formula; reference uses a non-canonical implementation; agent follows standard practice and fails. Example: WoE/IV smoothing applied to *proportions* `(good_pct + 0.5)` — non-standard, dampens WoE 8× toward zero — vs textbook (Siddiqi *Credit Risk Scorecards*) smoothing on *raw counts* `(good_count + ε) / total_good`.
  - **Flavor 2: Spec under-specifies a procedural goal.** Instruction names a *goal* like "parametric VaR decomposition", "Greek-based stress test", "factor-neutral hedge", "shrinkage estimator" — but does NOT pin a specific formula AND multiple defensible formulas exist. The reference oracle pins one specific formula; the agent invents a different defensible one and fails. Example: PR `barrier-garch-var` Haiku trial — instruction says only "computes a parametric VaR decomposition for a portfolio of `n_contracts` options at the given confidence level"; agent invents a Greek-based delta-gamma-vega Gaussian VaR; reference pins something else; partial credit ~0.15.
  Both flavors are C3.c matches *and* task-design issues — the fix is to write the exact formula in the instruction (or widen tolerance). Note the upstream task-side cause in `notes`.
- **C3.d — `np.quantile` method on discrete distributions.** `method='linear'` (default) interpolates between sample atoms; `method='higher'` returns `inf{l : P(L ≤ l) ≥ α}` — the generalized inverse CDF, correct for discrete loss distributions. Constant-LGD constant-exposure portfolios have only N+1 possible loss values, so `linear` returns a value between two atoms that never actually occurs.

## Single-shot applicability

Applies fully to `solution_kind == finance-zero`. The trap is in the instruction's vagueness, not the agent's runtime behavior, so it applies regardless of trajectory style.

## QF-Bench finance examples

POSITIVE — Fama-MacBeth risk premia: instruction says "use automatic bandwidth selection for Newey-West." No formula given. Test asserts `nw_lags == 6`. Reference uses NW(1994) `floor(4·(T/100)^(2/9))` = 6. Agents pick: NW(1987) → 5, Andrews (1991) → varies, Schwert → 6. Sonnet picks Andrews → 7. All 4 cascading failures from this single bandwidth miss (the lag itself, the multivariate Wald using the same lag, `se_hodrick_differs_from_nw` because Sonnet's wrong-bandwidth NW landed numerically close to its correct Hodrick). Match C3.a.

POSITIVE — Merton-CDS-copula task: instruction says "99% Expected Shortfall (mean of the tail beyond the VaR)." Reference uses rank-based Acerbi-Tasche: `np.mean(np.sort(losses)[ceil(α·N):])`. Opus reads "mean of tail beyond VaR" literally as threshold form `np.mean(losses[losses > VaR])`. With discrete loss distribution (constant LGD × #defaults, only 11 possible values), the two formulas differ by 38% (13.50 vs 18.72). Match C3.a.

POSITIVE — ML credit scoring task: instruction says "compute Weight of Evidence per bin. Use the smoothing constant from params to avoid log(0)." Standard textbook (Siddiqi): smooth raw counts. Reference: smooth proportions `log((good_pct + 0.5) / (bad_pct + 0.5))`, dampening WoE ~8× toward zero. Both Haiku and Sonnet implement the textbook form → IV 3.4× too high → 8 cascading failures across feature selection, logistic regression metrics, fairness metrics. Match C3.c (inverse trap).

POSITIVE — Realized-vol estimators: instruction cites Bandi-Russell (2006) Section 3.1 + BNS (2004) Definition 1. Both post-1994. Sonnet 108/141 fails on BR + BNS variants (different definitions of bipower vs noise-corrected RV); Opus 141/141. Match C3.b.

NEGATIVE — Instruction explicitly writes out the Newey-West formula in full: `nw_lags = floor(4*(T/100)^(2/9))`. Agent implements that exact formula. Test passes. No variant ambiguity, no match.

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
