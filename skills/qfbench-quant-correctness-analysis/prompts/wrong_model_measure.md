# Failure Mode: Wrong Model / Measure (A1)

*Empirical source: PR #164 dupire-local-vol (calendar-arbitrage diagnostic at single point); PR #28 hull-white-swaption / mc-greek-surface; general pattern across BS-vs-CEV, GARCH-vs-GARCH-t, OU-vs-GBM substitutions.*

## Framing

The agent implements a different mathematical model than the task specifies, or prices/computes under the wrong measure. The math is *internally correct* but not the math that was asked for. Distinguish from A2 (right model, missing term) and A3 (right model, wrong parameterization). A1 is about choosing the wrong overall model class, the wrong measure (Q vs P), or substituting a different mathematical object for the requested diagnostic (e.g., a single-point check where a sweep is required).

## Decision Procedure

1. Identify the model / method / measure stated (or implied unambiguously) in `instruction.md`. If no model is named or implied, no match.
2. Identify what the agent's code actually implements. Look at:
   - imports (`from scipy.stats import t` vs `norm` for likelihood family)
   - SDE discretization (Euler vs Milstein; CIR full-truncation vs reflection vs Andersen QE)
   - tree branching (CRR `u = exp(σ√Δt)` vs JR `u = exp((r−q−σ²/2)Δt + σ√Δt)`)
   - measure-of-pricing (drift `μ` vs `r − q`)
   - diagnostic mathematical object (single-point check vs full surface sweep)
3. If the agent's implementation differs from the spec on a *modeling* axis, match.
4. **A1 vs A2**: missing or extra term in the right model = A2; implementing the wrong model = A1.
5. **A1 vs A3**: wrong parameterization of the right model = A3; wrong model entirely = A1.

## Exclusions

- Implementing the right model with a wrong scalar coefficient inside the right formula → A2, not A1.
- Using a non-canonical method variant when the spec didn't pin the variant → C3 (e.g., Newey-West NW87 vs NW94).
- Right model, wrong sign → B2.
- Right model, wrong unit/scale → B1.

## Sub-rubrics

- **A1.a — Model substitution.** Black-Scholes when CEV / Heston / Bates required; plain GARCH when GARCH-t required; OU when geometric mean-reversion required; rough Heston when rBergomi required (or vice versa).
- **A1.b — Measure confusion.** Pricing under physical measure (μ) when risk-neutral (r − q) is required.
- **A1.c — Diagnostic at single point vs full sweep.** Calendar arbitrage `∂_T w(k,T) ≥ 0` checked at single ATM strike instead of across log-moneyness range. The single-point check is a different mathematical statement from the full no-arbitrage condition.

- **A1.d — Structural deviation: claims the model in name/notation but the implementation isn't that model.** *Empirical: hull-white-swaption Haiku-4.5 — agent uses HW notation (`a, σ, θ(t)`) and invokes HW formulas in caplet pricing, but the actual "trinomial tree" is a generic 3-branch lattice with hard-coded `(0.25, 0.5, 0.25)` probabilities, lattice spacing `Δx = σ√Δt` (not the HW-required `σ√(3·Δt)`), `dt = 0.5` (not the spec's `1/12`), and no Arrow-Debreu α_n calibration to match the initial discount curve. The implementation is structurally a generic 3-pt lattice, not a Hull-White trinomial tree.*

  **Structural-deviation test.** A model is a specific mathematical structure, not a name. Match A1.d when the agent's implementation deviates from the named model on **two or more** of these axes:
  1. **State equation / SDE structure** (e.g., spec says `dr = (θ − ar)dt + σdW`, agent integrates `dr = σdW` with no mean reversion).
  2. **Lattice / grid construction specific to the model** (HW trinomial requires `Δx = σ√(3·dt)` and `j_max = ⌈0.184/(a·dt)⌉`; CRR binomial requires `u = exp(σ√Δt)`; Crank-Nicolson PSOR requires the projection step).
  3. **Calibration procedure required by the model** (HW Arrow-Debreu α_n calibration to reproduce P(0,t_n); Heston market-implied-vol calibration; rBergomi forward-variance bootstrap).
  4. **Probability / weight construction specific to the model** (HW trinomial probabilities depend on local mean-reversion drift `−a·j·Δx·Δt` AND have mirrored boundary forms at `j = ±j_max`, NOT constant `(0.25, 0.5, 0.25)`; CRR risk-neutral prob `(e^{(r−q)Δt} − d)/(u − d)`).
  5. **Boundary / terminal conditions specific to the model** (American option early-exercise projection; barrier knock-out condition; stochastic-vol leverage condition).

  Use of the model's notation/symbols alone is NOT sufficient to claim "right model" if 2+ of these structural pieces are wrong. The agent cannot launder a generic numerical method into the named model by sprinkling its parameters as variable names.

  **Distinguish from A2.** A2 = "right model, one term missing or wrong" (e.g., HW is implemented correctly but the caplet vol omits the time-integration factor). A1.d = "the implementation isn't the named model at all" (multiple structural pieces wrong). When in doubt, count the structural deviations: 0–1 wrong = A2; 2+ wrong = A1.d.

## Single-shot applicability

Applies fully to `solution_kind == finance-zero`. Judge the generated code against the spec — if the code implements a different model class than the instruction asks for, match.

## QF-Bench finance examples

POSITIVE — Task: "Price American option via CRR binomial tree with `u = exp(σ√Δt)` and risk-neutral probability." Agent uses Jarrow-Rudd parameterization with `u = exp((r−q−σ²/2)Δt + σ√Δt)` and equal probabilities. Different model, different prices → match A1.a.

POSITIVE — Task: "Verify calendar arbitrage `∂_T w(k,T) ≥ 0` across log-moneyness." Agent's `forward_variance.csv` has a single row per maturity (ATM only). Computing the diagnostic at one k is a different mathematical statement from the full no-arbitrage condition → match A1.c.

POSITIVE — Task: "Price Asian option using Levy-Curran approximation under risk-neutral measure." Agent uses physical drift μ instead of `r − q`. The discounted asset is no longer a martingale; price overstated → match A1.b.

POSITIVE — Task: "Build Hull-White trinomial tree with `Δt = 1/12`, `Δx = σ√(3·Δt)`, `j_max = ⌈0.184/(a·Δt)⌉`, with Arrow-Debreu α_n calibration so `Σ_j Q_n(j) = P(0, t_n)`." Agent's tree uses `dt = 0.5`, `dx = σ√dt` (no √3), constant probabilities `(0.25, 0.5, 0.25)` everywhere (no mean-reversion drift in branching, no boundary mirroring), and no α_n calibration step. Four structural axes wrong (lattice spacing, time step, branching probabilities, calibration procedure). Even though the agent uses Hull-White notation `a, σ, θ(t)` elsewhere in the script, the tree they built is a generic 3-pt lattice approximating a constant-drift random walk, not a Hull-White trinomial tree → match A1.d.

NEGATIVE — Task: "Use Hull-White 1F." Agent correctly implements Hull-White trinomial tree (right `Δx = σ√(3·Δt)`, right drift-dependent probabilities, right α_n calibration) but the *caplet* pricing formula is missing the time-integration factor in the bond-forward volatility. Tree is right, one analytical formula has one missing term → A2.g, not A1.

NEGATIVE — Task names "GARCH(1,1)-t MLE" but the instruction's own likelihood formula omits the Jacobian. Agent implements the formula as written and gets wrong ν. Right model implemented as instructed; the missing-term bug is in the instruction → A2 (or task-side bug), not A1.

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
