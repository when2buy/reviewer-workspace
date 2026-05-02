# Failure Mode: Numerical / Optimization Failure (C2)

*Empirical source: PR #196 copula-garch-portfolio (GS α local optimum, atol too tight, lower bound 4 excludes ν ≈ 2.1); PR #208 garch-sp500-fit (ν pinned at upper bound); PR #178 variance-swap-pricing (Heston κ at 50, fit-without-bounds); PR #172 merton-jump-diffusion (intentional λ binding at boundary, undocumented); PR #168 heston-cf-pricing (rounding error); PR #161 compound-option-geske (Sonnet bivariate normal Φ₂ implementation error caught by parity check); PR #154 barone-adesi-whaley (BAW critical-price iteration); PR #98 nelson-siegel (warm-start poisoning + extra `gtol` kwarg); PR #126 merton-cds-copula (Cholesky → identity silent fallback, empty-array tail); PR #65 bond-portfolio-analytics (KRD silently returns 0 if no curve point match); PR #86 dcc-garch (penalty wall inside box bounds breaks L-BFGS-B); PR #140 localvol-barrier (MC barrier hits per step vs per path).*

## Framing

The right model, the right formula, the right inputs — but the *numerical* solution path failed. Local optimum (multimodal likelihood, no warm-start), divergence, ignored convergence flag, parameter pinned at boundary unexpectedly, special-function approximation error, MC counting off-by-one, or a fallback that silently substitutes a wrong value when a numerical primitive fails.

C2 is about *how the numerical computation was run*, not *what it computed*.

## Decision Procedure

**0. PREREQUISITE — math-correctness check (gate this rubric).** Before matching C2,
   verify the agent's *formula* is mathematically correct under the spec:
   - all canonical terms present (else → A2.a / A2.g)
   - right model and measure (else → A1)
   - right parameterization conventions (else → A3)

   If a formula error exists AND that error is what produces the NaN / inf /
   pinned-bound / no-convergence symptom, **C2 must return `match: false`** with
   notes redirecting to the relevant A-mode. Do not double-count one root cause
   under both A and C — see the cascade rule in the system prompt. C2 fires only
   when the math is right and the *numerical execution* path failed.

   Example: Heston char-fn returns NaN IVs because the Riccati `d` coefficient
   is wrong (A2.g). The numerics aren't broken — they faithfully evaluate a
   wrong formula. C2 = match: false; A2.g = match: true. The reverse: agent's
   formula matches the canonical Heston char-fn exactly, but `scipy.integrate.quad`
   times out at high-φ tails and returns NaN; that's C2.e (special-function /
   integration setup), and A2 = match: false.

1. Identify the numerical step: optimization, root-finding, integration, matrix decomposition, MC simulation, special-function evaluation, fixed-point iteration.
2. Check the agent's setup: solver choice (`L-BFGS-B`, `SLSQP`, `Nelder-Mead`), initial guess, bounds, kwargs (`maxiter`, `ftol`, `gtol`, `xtol`), random-seed handling for stochastic methods.
3. Look for the symptom:
   - parameter at upper/lower bound exactly (e.g., ν = 100.0, κ = 100.0)
   - NaN/Inf in output
   - optimizer `success=False` ignored, `prev_params` updated unconditionally
   - large gap to oracle on a parameter that should converge to a unique value
   - probability > 1 (MC counting bug)
   - parity check fails (special-function implementation error)
   - finite-difference Greeks oscillate or go negative (likely RNG-state issue)
4. Identify the cause:
   - multi-modal landscape with wrong start
   - lower bound > location of true MLE → excludes valid solutions
   - bounds-and-penalty inconsistency (penalty wall inside box)
   - silent fallback to identity / last-known-good when decomposition fails
   - per-step vs per-path MC indicator
   - independent random draws across bumped/base evaluations in FD Greeks (see C2.j)
5. **C2 vs A1/A2/A3**: those are *math* errors. C2 is *numerical execution given correct math*. Apply step 0 strictly.
6. **C2 vs C3**: C3 is *picking a wrong variant of a named method* (NW87 vs NW94); C2 is *executing a numerical method poorly*.

## Exclusions

- Wrong formula (A2).
- Wrong parameterization (A3).
- Numerical noise within tolerance.
- Boundary binding that's *intentional* per the instruction (e.g., "Note: λ will bind at 12.0; this is expected.") — no match.

## Sub-rubrics

- **C2.a — Local optimum / multimodal likelihood without pinned start.** GARCH-t α landed at 0.073 (oracle) vs 0.10–0.12 (agents) due to non-convex likelihood. Heston κ landed at 50 (valid local optimum) because instruction allowed "fit OR use defaults" without bounds. Lower bound > location of true MLE excludes valid solutions (Rama Cont: tail-index lower bound of 4 excludes empirically valid ν ≈ 2.1–3 for equity returns).
- **C2.b — Optimizer kwargs / extra stopping criteria.** `gtol=1e-8` added to L-BFGS-B → different convergence path → cascade across many fits. `maxiter=10000` instead of `2000`. `least_squares(trf)` substituted for `minimize(L-BFGS-B)` (these aren't interchangeable — `least_squares` doesn't even support L-BFGS-B).
- **C2.c — Boundary parameter binding (unintentional).** ν pinned at 100 because likelihood missing `−log(scale)` (this also matches A2.a). λ pinned at 12 because data wants higher (intentional per instruction → no match). When binding is unintentional, the wrong objective drives it; when intentional, the instruction must say so explicitly.
- **C2.d — MC counting / off-by-one (per-path vs per-step accumulation).** Barrier hit probability > 1 because agent counted hits per *step* instead of per *path*. Per-path indicator (max 1 per path) vs per-step indicator (sum can exceed 1). Symptom: probability > 1.
- **C2.e — Special-function / transcendental approximation error.** Bivariate normal Φ₂(a, b; ρ) at high |ρ| computed from scratch and wrong in tails (Drezner-Wesolowsky vs Genz vs other). Modified Bessel I_ν, K_ν overflow at large argument. Hypergeometric ₂F₁ branch-cut handling. Symptom: plausible-looking final number but parity / arbitrage check fails.
- **C2.f — Smooth-pasting / fixed-point iteration setup.** BAW critical-price iteration: seed from perpetual boundary, exponential correction, Brent's method on `S* − K = C_euro(S*) + A₂(S*)`. Wrong seed or missing correction → wrong critical price → wrong American premium.
- **C2.g — Silent fallback on numerical failure.** Cholesky fails → `L = identity` (no correlation in MC, wrong tail risk, no warning). Optimizer `result.success = False` → `prev_params` updated unconditionally → one bad local minimum poisons all subsequent warm-starts. KRD curve interpolation: no curve point within 0.01 of key tenor → returns 0.0 silently.
- **C2.h — Empty-array / boundary edge case.** `losses_sorted[var_idx + 1:]` empty when `var_idx = n_sims − 1` → `np.mean([])` returns NaN with RuntimeWarning → silently becomes `null` in JSON output.
- **C2.i — Penalty wall inside box bounds.** L-BFGS-B bounds allow `(a, b)` with `a + b < 0.999`, but manual `if a + b >= 0.999: return 1e10` creates a discontinuity *inside* the box. Finite-difference gradient breaks. Either tighten bounds (constraint enforced by box alone) or use SLSQP.

- **C2.j — RNG-state contamination in finite-difference Greeks (Monte Carlo).** *Empirical: 3 trials in the 50-trial validation set (mc-greek-surface family).* For finite-difference Greeks under Monte Carlo, the bumped and base evaluations **must consume identical random draws**, otherwise the FD estimator carries the variance of two independent MC runs and the gradient is dominated by noise rather than signal. Three failure shapes:
  1. Different seeds: `MCSimulator(S0+h, ..., seed=SEED+1)` and `MCSimulator(S0-h, ..., seed=SEED-1)` — bumped runs use disjoint random streams. Symptom: gamma goes negative for an obviously convex payoff; vega oscillates by 50%+ between consecutive runs.
  2. Mutating RNG state: `self.rng = np.random.default_rng(seed)` is set at init, then `self.rng.standard_normal(...)` is called inside `price()`. The base call drains the stream; the bumped call sees a DIFFERENT stream because state advanced. Symptom: same as (1) — even though "the seed is the same", the draws aren't.
  3. CRN abandoned for variance reduction: the agent comments "use antithetic for variance reduction" and replaces `Z` with `np.concatenate([Z, -Z])` in only the base eval, not the bumped — so base uses 2N paths antithetic, bumped uses N paths plain.
  
  **Fix pattern (what a correct solution looks like):** generate a SINGLE `Z = rng.standard_normal((N, M))` array OUTSIDE the price function, pass it as an argument to all (S0+h, S0, S0-h, σ+h, σ-h, ...) evaluations, never re-seed inside price. Common-random-numbers (CRN) is the canonical name for this technique.
  
  **Identification cue:** look for `np.random.seed(SEED + k)`, `np.random.default_rng(SEED + k)`, or fresh RNG creation INSIDE a price function called repeatedly by the FD bumper. Also look for FD Greeks computed by re-simulating from scratch each time. The fix is invariably "generate `Z` once at the top, pass it down". Match C2.j when this pattern is visible AND a Greek is wildly off (e.g., gamma negative, vega 100× off) AND the formula itself is correct.

## Single-shot applicability

Applies fully to `solution_kind == finance-zero`. Single-shot agents can still set up bad solver kwargs or implement wrong special functions.

## QF-Bench finance examples

POSITIVE — GARCH(1,1)-t fit: agent's optimizer lands at α = 0.105, oracle at 0.073. Both are valid local maxima of the non-convex likelihood; agent's start and solver differ from oracle's. Test asserts `np.isclose(alpha, 0.073, atol=0.03)`, fails. Root cause: instruction didn't pin starting values or solver. Match C2.a.

POSITIVE — DCC-GARCH calibration: bounds `(1e-6, 0.5)` and `(1e-6, 0.999)` allow `a + b` up to 1.499. Penalty `if a + b >= 0.999: return 1e10` creates step at a ridge inside the box. L-BFGS-B's finite difference returns garbage gradient. Convergence stalls, `success=False`. Match C2.i.

POSITIVE — Geske compound option: agent implements bivariate normal Φ₂ from scratch using a series expansion that fails at |ρ| > 0.95. Final compound-option price looks plausible (~$3.50) but put-call parity check fires: `|C − P − K2_disc + S0| > 0.01`. Match C2.e.

POSITIVE — Barrier MC: agent counts barrier hits per step instead of per path: `for step in range(N): if S[t] < barrier: hits += 1`. With multi-step paths, `hits` can exceed `n_paths`. Estimated barrier-hit probability = 1.34 (impossible). Match C2.d.

POSITIVE — MC FD Greeks RNG contamination: agent's `_compute_fd_greeks` calls `MCSimulator(S0+h, r, q, sigma, T, N_PATHS, RANDOM_SEED + 1)` for the up-bump and `... RANDOM_SEED + 2` for the down-bump. Each MCSimulator constructs a fresh `np.random.default_rng` from the integer seed, so the up and down evaluations use **disjoint** random streams. FD gamma reported as −0.069 (negative for an at-the-money European call — physically impossible, gamma must be ≥ 0 for any European call). Pathwise gamma reported correctly as +0.045 because pathwise doesn't re-simulate. The agent's BS reference, pathwise estimator, and FD formula are all mathematically right; only the RNG handling is wrong. Match C2.j. (Step 0 prerequisite: confirmed BS d1/d2/Φ usage is canonical; A2/A3 = no match.)

NEGATIVE — Agent's L-BFGS-B converged with `success=True`, parameters within tolerance of oracle. No numerical failure.

NEGATIVE — Agent uses an explicit numerical method (Newton-Raphson with finite-difference gradient) that the instruction allowed. Convergence to a non-oracle value because the instruction's named method is ambiguous (NR vs bisection+NR). That's C3 (statistical/numerical method variant), not C2.

NEGATIVE — Two-factor Heston returns NaN implied vols because the agent's Riccati `d` coefficient drops the `i·φ` linear term. The numerics aren't broken — `scipy.integrate.quad` returned a finite (wrong) value, `iv_inversion` correctly raised on negative call price. The math is wrong; numerics faithfully evaluated it. C2 = match: false; A2.g owns the finding.

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
