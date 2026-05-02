# Failure Mode: Missing or Extra Formula Term (A2)

*Empirical source: PR #208 garch-sp500-fit (missing `−log(scale)` Jacobian); PR #182 var-es-estimation (Student-t ES composition error); PR #166 fx-quanto-options (compo vol missing FX component); PR #137 multimodal-alpha-fusion (OU NLL on different sample size); PR #28 mc-greek-surface (Greek-not-available-for-method); PR #61 pairs-trading (transaction cost double-counted); PR #158 chooser-option-pricing (missing discount factor).*

## Framing

The agent uses the right model but the formula is missing a required term or includes a spurious one. Common missing terms: Jacobian / measure-change in MLE objectives (`−log(scale)` for location-scale standardized t); Itô / martingale corrections in exponential SDE discretization (`−½η²t^{2H}` in rBergomi); discount factors omitted or applied twice; component contributions in composite quantities (FX vol in compo option; cross-asset terms in multi-factor variance). Common extra terms: transaction costs subtracted twice (entry + realized); Greeks reported for methods where they're not defined (pathwise gamma is null because indicator is non-differentiable).

## Decision Procedure

1. Identify the formula the task asks for, term-by-term. If the formula is implicit (the task names the model without writing the formula), use the canonical derivation from the named source.
2. Compare against the agent's implementation. Look for:
   - missing additive terms (e.g., Jacobian penalty in log-likelihood)
   - missing multiplicative factors (e.g., discount `e^{−rT}`)
   - missing summands in composite expressions (cross-term in vol, off-diagonal in Σ)
   - **extra** spurious terms (e.g., a Greek that should be `null` reported as a number; cost double-counting)
3. If a required term is absent (or a spurious one is present) and it materially affects the output, match. "Material" = changes the test outcome or shifts the parameter estimate by more than tolerance.
4. **A2 vs A1**: wrong overall model = A1; right model, missing term = A2.
5. **A2 vs A3**: parameter convention differs = A3; specific term missing = A2. (E.g., σ_k = std vs CV is A3; missing the `/μ_k²` term *given* a fixed convention is A2.)

## Exclusions

- The "missing" term is conventionally negligible at the parameter scale (e.g., higher-order term in a leading-order expansion) and the agent's claim is appropriately narrowed.
- Format-only omissions (e.g., reporting precision differences within tolerance).
- Term-omission that's actually a parameterization choice with two defensible readings → A3 (convention default).

## Sub-rubrics

- **A2.a — Transformation term missing.** Jacobian missing in change of variables: `−log(scale)` in t-likelihood with location-scale standardization (`scale = sqrt((ν−2)/ν)`) — when omitted, optimizer pushes ν → ∞ because penalty disappears at large ν. Itô correction `−½η²t^{2H}` missing in exponential variance process (rBergomi). Discount factor missing or applied twice (chooser option mispricing).

  **Pathwise Greek estimators with missing chain-rule term.** *(Confirmed canonical reference: Haugh 2017, IEOR E4703 Eq. 9, citing Glasserman 2004 Ch. 7.)* Under GBM, `S_T = S_0 · exp((r − σ²/2)T + σ√T·Z)`. The pathwise chain rule for vega is:
  ```
  ∂S_T/∂σ = S_T · (Z√T − σT)
  ```
  The `Z√T` term is the derivative of the diffusion `σ√T·Z`; the `−σT` term is the derivative of the convexity correction `−σ²T/2`. **Both terms appear in the canonical formula**; neither is "absorbed by discounting" or otherwise dropped. The full pathwise vega for a European call is therefore:
  ```
  ∂Y/∂σ = e^{−rT} · 1{S_T > K} · S_T · (Z√T − σT)
  ```
  Agents commonly mangle this in three ways: (i) **drop the `−σT` convexity-correction term** (formula becomes `S_T · Z√T`); (ii) **insert a spurious `1/σ` factor** (writing `(Z·√T − σT)/σ` or `(Z·√dt/σ − dt)`, often biased by ~3-4× at typical σ=0.3); (iii) **substitute `√dt` for `√T`** when the time-step is conflated with time-to-maturity. The same family of bugs hits LR rho (missing `−T` term in score `[Z√T/σ − T]`) and pathwise theta. (Recurred 3× in mc-greek-surface trials in the 50-trial validation set.)
- **A2.b — Composite-quantity missing constituent.** Compo option vol uses `σ_S` only, dropping `σ_X` and `2ρσ_Sσ_X` cross-term. Multi-factor portfolio variance uses only diagonal of Σ. Cross-currency forward uses only one rate.
- **A2.c — Likelihood / AIC across different sample sizes.** OU model NLL on n−1 obs (because AR(1) regression consumes one lag) while martingale/GBM/Merton use n obs → AIC = 2k + 2·NLL is biased toward OU. The fix is to add the log-marginal of the dropped first observation under the OU stationary distribution, so all four likelihoods are computed on n observations.
- **A2.d — Greek not available for chosen method.** Pathwise gamma is null because the indicator function is non-differentiable. LR theta is null because the time score is complex. Reporting a non-null value for either is "extra term" (the agent fabricated a Greek that the method cannot produce).
- **A2.e — Extra term double-counted.** Entry transaction cost subtracted at trade entry AND again in the realized P&L formula at exit. Cost applied 3× round-trip instead of 2×. Same pattern: bid-ask half-spread accounted for twice; financing applied to both legs of a hedge.
- **A2.f — Region / boundary identification missing constraint guard.** When computing a *derived* quantity by scanning a domain — exercise boundary `S*(t)`, support of an arbitrage-free vol surface, root in implied-vol inversion, threshold in regime detection — the financially-meaningful constraint must be checked explicitly. Example: for an American put, the exercise boundary `S*(t)` is "the largest `S` where `V(S) = payoff(S)`" *AND* `payoff(S) > 0`. Scanning the full domain without the `payoff > 0` guard picks the deep-OTM zone (where both `V ≈ 0` and `payoff = 0`) trivially, reporting `S* = S_max` for every `t`. Implied-vol Newton-Raphson without a "price > intrinsic value" guard converges to spurious roots. Arbitrage-region detection without a "price > lower bound" guard mis-identifies the boundary.

- **A2.g — Wrong coefficient in canonical ODE / characteristic function.** The agent uses the right model and the right structural form but a sign or scale factor inside the canonical formula is wrong.

  *Empirical examples:*

  - **Heston / two-factor Heston** (4 trials in the 50-trial validation set). The Riccati ODE `d` coefficient in Heston (1993) Eq. (6) is `d_j = sqrt((ρσi·φ − b_j)² − σ²·(2u_j·i·φ − φ²))` where `(b_2, u_2) = (κ, −1/2)` for P_2 and `(b_1, u_1) = (κ−ρσ, +1/2)` for P_1. Substituting these gives **P_2:** `d_2 = sqrt((κ − ρσi·φ)² + σ²·(i·φ + φ²))` and **P_1:** `d_1 = sqrt((κ − ρσ − ρσi·φ)² − σ²·(i·φ − φ²))`. Agents commonly drop the `i·φ` linear term inside the polynomial, sign-flip `(2u·i·φ − φ²)`, or use the same `d` for both branches. Output symptom: NaN implied vols, ATM IV way off (e.g., 3.12 vs 0.279), negative call prices for ~28% of strikes.

  - **Hull-White 1F bond pricing — variance correction in `log A(t,T)`** (verified against Brigo-Mercurio textbook / OpenGamma reference). The canonical zero-coupon bond price is `P(t,T) = A(t,T)·exp(−B(t,T)·r_t)` with `B(t,T) = (1 − e^{−a(T−t)})/a` and:
    ```
    log A(t,T) = log[P(0,T)/P(0,t)] + B(t,T)·f(0,t) − (σ²/(4a))·(1 − e^{−2at})·B(t,T)²
    ```
    The variance-correction term is **`(σ²/(4a))·(1 − e^{−2at})·B(t,T)²`** (note the `4a` in denominator, NOT `2a`). Agents commonly write `σ²·B(t,T)²·(1 − e^{−2at})/(2a)` — wrong by a factor of 2 — or drop the `(1 − e^{−2at})` factor entirely (treating variance as if it grows linearly in time when it actually saturates due to mean reversion).

  **Distinguish from A2.a:** A2.a is "missing term" (term zero); A2.g is "term present but coefficient wrong" (sign / factor / power). When the agent's formula is correct in form but wrong in arithmetic, prefer A2.g.

- **A2.h — Silent approximation abuse (sub-case extension).** The agent uses a method that is exact only in a restricted sub-case and silently applies it to the full case. *Empirical:* PR-style escrowed-dividend approach for American options (1 trial in 50; pattern is well-documented in reviewer post-mortems).

  Escrowed dividends `S_adj = S − PV(future divs)` is a deterministic-dividend approximation that is **exact for European calls under the specific assumption that the firm escrows dividends in a riskless account** (then the risky stock equals `S_adj` exactly). Outside that corporate-finance assumption — and ALWAYS for American calls — it is an *approximation*. Applying it to American options is structurally wrong even granting the escrow assumption: the early-exercise condition is `V ≥ payoff(S, t)` (where `payoff = max(S − K, 0)` lives in the original `S`), not `V ≥ payoff(S_adj, t)`. PSOR projection on the `S_adj` grid effectively prices a European call on the dividend-deterministic stock, missing the early-exercise premium that comes specifically from cum-dividend exercise.

  Other recurring members of this family: using closed-form GBM Asian-Geometric as a control variate without the GBM-specific lognormal correction; applying lognormal IV inversion to a price quoted as normal-vol; using flat-vol BS Greeks on a skew model and calling them "model" Greeks.

  **Decision rule:** match A2.h when (a) the method is named-correct for sub-case X, (b) the spec asks for the full case, and (c) the agent's code shows no projection / boundary / correction step that would lift X-only to full-case validity.

## Single-shot applicability

Applies fully to `solution_kind == finance-zero`. Judge the generated code's likelihood / pricing / aggregation expressions against the spec.

## QF-Bench finance examples

POSITIVE — GARCH-t MLE: instruction's Step 3 likelihood is `L = Σ[log f_t(z_t; ν) − ½ log σ²_t]` with `z_t = X_t / σ_t`. Reference solution actually uses `z = X / (σ·scale)` with `scale = sqrt((ν−2)/ν)` and `L = Σ[logpdf(z, ν) − log(σ) − log(scale)]`. Agent follows the instruction literally — omits `−log(scale)` Jacobian. Optimizer pushes ν → 100 (upper bound) because the penalty for large ν disappears. Match A2.a (note: this is also an instruction-vs-code divergence — the task itself is buggy; the *agent failure mode* is still A2).

POSITIVE — Compo option pricing: agent uses `σ_S` in d1/d2 instead of `σ_d = √(σ_S² + σ_X² + 2ρ σ_S σ_X)`. With ρ = 0 and σ_X > 0, compo option price equals quanto, but financially compo should be strictly larger due to FX vol exposure. Match A2.b.

POSITIVE — MC Greeks task: instruction says `pathwise_gamma_call: null` and `lr_theta_call: null` because these are not defined for the chosen method (indicator is non-differentiable; time score is complex). Agent reports concrete numbers for both. Match A2.d (extra term).

POSITIVE — American put exercise-boundary detection: agent's loop is `for i in range(N_S, 0, -1): if V[i, n] - payoff[i] <= EXERCISE_TOL: boundary[n] = S[i]; break`. For a put, `payoff(S) = max(K-S, 0) = 0` for `S > K`. Wherever `V` is also ≈ 0 in that zone (deep OTM, or PDE bug), `V − payoff = 0` is satisfied trivially across the entire `S > K` region. The scan picks `i = N_S` immediately, reports `S*(t) = S_max` for every `t`. Missing guard: `payoff[i] > 0`. Match A2.f.

POSITIVE — Two-factor Heston characteristic function: agent codes the Riccati `d` coefficient as `d = sqrt((b)² + γ·(2·u·i·φ − φ²))` with `b = κ − ρσi·φ` but flips the sign on the polynomial inside the square root and drops the linear `i·φ` term in `b² − γ·...`. Pricing returns negative call values for ~28% of strikes and 41/144 NaN implied vols; ATM IV from inversion is 3.12 vs the test-pinned 0.279. Match A2.g (wrong coefficient in canonical char-fn). Cascades to all downstream IV-surface tests.

POSITIVE — Hull-White swaption variance term: agent writes `V = (σ·B(t,T))² · (1 − e^{−2at}) / (2a)` for the log-bond-price variance, but the canonical Hull-White value is `V = (σ²/2a²) · ∫₀^t [B(s,T) − B(s,t)]² ds` — the agent merged the integral over `s` and the outer `(σ²/2a²)` into a single squared expression. Bond-price test ratios cluster around 1.04 to 1.12 (uniformly biased, indicating one wrong constant); swaption prices are 5–8% off across the curve. Match A2.g.

POSITIVE — American option with discrete dividends, escrowed approach: agent computes `S_adj(t) = S(t) − Σ_{ti > t} D_i · e^{-r(ti−t)}`, runs Crank-Nicolson PSOR on the BS PDE in `S_adj`, and returns the resulting price for *both* European and American calls. `american_call - european_call` test fails at ~0.001 (i.e., the agent reports the same number twice). The PSOR projection `V_n^{n+1} = max(V_n^{n+1}, payoff(S_adj))` enforces early exercise on the *adjusted* stock, but the early-exercise condition for an American call on the dividend-paying stock is `V ≥ max(S − K, 0)` in the *original* `S` — escrowed-div is exact only for European. Match A2.h. (Cascades to test_no_div_american_call_equals_european_call passing trivially because there are no divs to escrow, and test_dividends_decrease_call_value showing the same wrong number on both sides.)

POSITIVE — Pathwise vega for European call (h45br-r3-mc-greek-surface-1): agent codes `vega = payoff_indicator · S_T · (Z·√dt / σ − dt) · e^{−rT}`. Canonical (Haugh Eq. 9 / Glasserman 2004 Ch. 7): `e^{−rT} · 1{S_T > K} · S_T · (Z√T − σT)`. Three structural errors visible: (i) `Z·√dt` instead of `Z·√T` (uses time-step where time-to-maturity belongs); (ii) extra `/σ` factor that should not appear; (iii) `−dt` instead of `−σT` (off in both magnitude and dimensional units). At σ=0.3, T=1, this overstates vega by a factor of ~1/σ ≈ 3.3, matching the empirical "pathwise ~126 vs FD ~36" in the failing test. Match A2.a. **Cascade rule:** any A3.c "wrong parameterization" framing is subsumed — the agent did not pick a different convention; they wrote a structurally wrong formula. A2.a owns the root cause; A3.c returns match=false with redirect.

NEGATIVE — Agent uses Black-Scholes when the task says Black-Scholes. d1, d2, all Greeks correct including signs. No missing terms. No match.

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
