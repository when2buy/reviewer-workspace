# QF Industry-Standard Reference Catalog (v3.2.7, May 2026)

This catalog grounds the **Industry-Standard pre-check** in the v3.1 system_judge.md.
When the spec is silent on a numerical convention, an experienced quant defaults to the
variant most widely used in production / textbooks / industry. The judge uses this catalog
to determine whether the agent's choice is a *defensible-but-non-standard* variant
(`agent_conceptual / A3.f`) or a genuinely under-specified case with no industry default
(`task_side`).

Entries are web-verified against finance documentation, sandwich/statsmodels libraries,
and standard quant references. Sources are cited per entry.

---

## A. Volatility & Risk Statistics

### A.1  Sharpe-ratio annualization

**Industry standard:** Daily returns → `Sharpe_annual = (mean_excess_return / std) × √252`
where 252 = US-equity trading days/year. Use √260 only if explicitly excluding weekends
without business-day filtering. Never `√365` for trading-day returns. Volatility scales as
`√t` under serial-independence assumption (Brownian motion).

*Source:* QuantStart, QuantInsti, paperswithbacktest.com — universally adopted across
algorithmic trading literature and practitioner blogs.

### A.2  Sample standard deviation (`ddof`)

**Industry standard:** `ddof=1` for sample standard deviation (Bessel's correction). This
matches `pandas.DataFrame.std()` default and is the convention for financial volatility
estimation (vol, Sharpe denominator, Newey-West-style covariance).

**Caveat:** `numpy.std()` defaults to `ddof=0` (population std). Senior quants explicitly
set `ddof=1` when computing volatility. Using numpy's default without override is a
classic A3.f pattern.

*Source:* NumPy v2.5 docs explicitly state ddof=0 default; pandas docs state ddof=1
default. Towards AI: "Here Is Why You Probably Use numpy.std Incorrectly".

### A.3  Volatility of asset returns: simple vs log returns

**Industry standard:** Simple returns `(P_t/P_{t-1} - 1)` for short-horizon analysis (daily,
weekly). Log returns `ln(P_t/P_{t-1})` for compound-period analysis or when working under
GBM where `dS/S = μdt + σdW` and integrated returns are normal under log space.

For Sharpe, vol-targeting: simple returns are standard. For OU/AR(1) on log-prices: log
returns. Mixing is an A3.f gap.

### A.4  Realized variance / Bipower variation (BV)

**Industry standard (Barndorff-Nielsen & Shephard 2004):**
`BV = (π/2) · Σ |r_{i-1}| · |r_i|` over high-frequency intraday returns.
The π/2 factor is *required* — π/4 is just a derivation error (off by 2). 

*Source:* BNS 2004 paper; survey papers on realized-vol estimators (Andersen-Bollerslev,
Bandi-Russell, Zhang-Mykland-Aït-Sahalia).

### A.5  Newey-West HAC bandwidth

**Industry standard (modern):** NW1994 automatic bandwidth selection
`L = floor(4·(T/100)^(2/9))` (Bartlett kernel) — implemented as default in R `sandwich`
package's `NeweyWest()`. The 1987 version requires manual lag specification and is older
practice.

**Disambiguation rule:** If the spec mentions only "Newey-West" or "NW HAC" without a
year, the modern default is NW1994 auto-bandwidth. NW1987 is acceptable only with
explicit citation.

*Source:* Wikipedia "Newey-West estimator"; R sandwich package docs (Zeileis 2004).

### A.6  Expected Shortfall (ES) / Conditional VaR (CVaR)

**Industry standard:** Acerbi-Tasche rank-based form
`ES_α = (1/⌊α·N⌋) · Σ sorted_loss[1..⌊α·N⌋]` — i.e., mean of the `⌊α·N⌋` worst losses.

**Alternative (less common):** Threshold form `E[L | L > VaR_α]`. Used when the loss
distribution is continuous (no atoms). The two forms agree in continuous distributions,
disagree at discrete-loss atoms.

If the spec doesn't pin: use Acerbi-Tasche rank-based form — it's the stable choice for
empirical samples.

### A.7  VaR/CVaR sign convention

**Industry standard:** Reported as **positive losses** (loss-space). VaR_α at α=99% is
"a 1-in-100 day loss of $X" reported as +$X. CVaR likewise.

Reporting VaR/CVaR as a *negative return* (return-space) is a non-standard convention and
fails most regulatory reporting tests. This is an A3.f gap when seen.

### A.9  Cumulative-return computation: variance drain

**Industry standard:** Compound simple returns geometrically; sum log returns. Never mix.

- Simple returns: `cum_ret = (1 + r).prod() - 1`
- Log returns: `cum_log = log_returns.sum()`, then `cum_ret = exp(cum_log) - 1` if you
  need a simple-return equivalent.

The gap between arithmetic-mean and compounded (geometric) return is the **variance
drain** (also called the "volatility tax"):

`CAGR ≈ AR − ½ σ²`

where AR is the arithmetic-mean of period returns and σ² is the variance of period
returns. The drag is meaningfully larger than rounding error for any vol > 5%:
- 15% annual vol → drag ≈ 1.13%/year
- 30% annual vol → drag ≈ 4.5%/year

Summing simple returns to get total return — instead of compounding — is the canonical
implementation gap and produces drift of order σ²·T/2 over horizon T.

References:
- [Wikipedia — *Volatility (finance)*](https://en.wikipedia.org/wiki/Volatility_(finance)) *(directly verified passage: "CAGR ≈ AR − ½σ²")*
- [Kitces — *Volatility Drag: How Variance Drains Investment Returns*](https://www.kitces.com/blog/volatility-drag-variance-drain-mean-arithmetic-vs-geometric-average-investment-returns/) *(directly verified passage: "Geometric Return = Arithmetic Return − ½ Variance")*
- [Bogleheads wiki — *Variance drain*](https://www.bogleheads.org/wiki/Variance_drain) *(paywalled / anti-bot — content corroborated by Wikipedia + Kitces)*
- [Jacquier, Kane, Marcus (2003), *Geometric or Arithmetic Mean: A Reconsideration*, Financial Analysts Journal](https://people.bu.edu/jacquier/papers/geom.faj0312.pdf) — academic primary source for the σ²/2 derivation

---

## B. Time Series & Statistics

### B.1  AR(1) / Vasicek / OU half-life

**Industry standard:** For an AR(1) `y_t = c + φ·y_{t-1} + ε_t` fitted on the **spread**
(not the residuals), half-life is `t_{1/2} = -ln(2) / ln(φ)` when `0 < φ < 1`.

**Critical:** Compute on the *spread* (the cointegration residual or mean-reversion
target), not on the Kalman-filter innovations. Innovations are white noise by
construction → their lag-1 correlation is ~0 or negative → log of negative → garbage
half-life. This is a recurring A3.f gap (canonical example: pairs-cointegration-kalman in
QF-Bench V11 — 33/33 cells emit sub-day half-life because they fit AR(1) on innovations
instead of spread).

### B.2  AR(1) MLE: exact vs conditional

**Industry standard for short series (T < 200):** Exact MLE (Hamilton 1994 §5):
`L = L_conditional × p(y_1 | stationary marginal)` — adds the marginal of the first
observation under stationarity.

**Acceptable for long series (T >> 200):** Conditional MLE (drop first observation).

Mixing exact and conditional MLE across competing AR(1) models in the same AIC comparison
is invalid (different sample sizes). Senior quants ensure all candidate models use the
same likelihood form.

### B.3  Cointegration test (ADF / Engle-Granger / Johansen)

**Industry standard:** For pair-wise cointegration: Engle-Granger two-step (regress y on
x, ADF-test the residuals). For multi-asset: Johansen (`coint_johansen` in
statsmodels). Default ADF lag selection: AIC or BIC (AIC most common). Default trend
specification: 'c' (constant only).

### B.4  Kalman filter for time-varying β

**Industry standard:** State equation `β_t = β_{t-1} + η_t` (random walk), measurement
`y_t = α + β_t · x_t + ε_t`. Initial state mean = OLS estimate over first window;
initial state covariance = OLS standard errors squared (large, diffuse).

---

## C. Numerical Methods (FD, MC, Trees)

### C.1  Finite-difference Greeks: Rannacher smoothing for non-smooth payoffs

**Industry standard (Rannacher 1984):** When discounting a non-smooth payoff (digital
option, American option early-exercise kink, barrier option at the barrier) under
Crank-Nicolson FD, *the first 4 timesteps must use Backward Euler* (Rannacher start)
before switching to Crank-Nicolson. This dampens the high-frequency oscillations in
Greeks (delta, gamma, vega) that would otherwise corrupt hedging.

**This is a "no one tells you" common-sense rule** — an experienced quant instinctively
applies Rannacher start to digital/barrier/American FD pricers. Failure to do so produces
plausible prices but wildly oscillating Greeks.

*Source:* Rannacher 1984; Forsyth-Vetzal-Zvan; multiAssetOptions R package.

### C.2  Trinomial tree branching (Hull-White)

**Industry standard:** Three-branching at interior nodes, two-branching at boundaries
(j_max, j_min) where the tree shifts back. Branching probabilities computed by
moment-matching the first two moments of the underlying SDE under the truncated
distribution. Arrow-Debreu calibration for fitting initial yield curve.

### C.3  Monte Carlo Greeks: pathwise vs likelihood-ratio (LR) vs finite-difference

**Industry standard:** Use **pathwise** when payoff is piecewise differentiable
(European call delta), **LR** when payoff is discontinuous (digital delta), **FD** as
fallback. Common bump size: 0.01% for delta, 1% for vega — but always test convergence.
Same RNG seed across bumped/base paths is *required* — RNG-state contamination is a
common C2.j gap.

### C.4  Monte Carlo seeding

**Industry standard:** Pin random seed once at top of script (`np.random.seed(42)` or
`rng = np.random.default_rng(42)`). For multi-stage pipelines, document seed propagation.
Reporting MC results without seed pinning is a `task_side` issue if the spec doesn't
mandate, but `agent_conceptual` if the agent should have known.

---

## D. Pricing & Calibration

### D.1  Black-Scholes inputs convention

**Industry standard:** `r` is risk-free rate as continuous compounding (annualized).
`q` is continuous dividend yield (annualized). `T` in years. `σ` annualized. ATM strike
= forward `K = S₀·exp((r-q)T)`, NOT spot. Most calibration uses log-moneyness
`m = ln(K/F)` with `F = S₀·exp((r-q)T)`.

### D.2  Implied vol surface calibration grid

**Industry standard for equity options:** Strike grid centered around ATM forward,
spanning ~[0.5×F, 1.5×F] in log-moneyness (so ~±0.7 in log space). Maturity grid: 1W,
1M, 3M, 6M, 1Y, 2Y. For longer-dated, vols are typically illiquid and noisier.

**Liquidity caveat (commodity futures vols):** Front 1–6 months are liquid, beyond 1 year
typically bad (low volume, wide bid-ask). An experienced commodity quant downweights or
filters >1Y options when calibrating SV models. **This is "no one tells you" knowledge
that an LLM agent may miss.**

### D.3  Heston calibration

**Industry standard:** Carr-Madan FFT with α damping factor in [0.75, 1.5] (typical 1.0).
Log-strike grid spacing η = 0.25, N = 4096 (so log-strike range ≈ ±512). Calibrate to
implied vol *not* to price (vol-space objective is more stable).

### D.4  Kirk vs Margrabe spread option

**Industry standard:** Margrabe (1978) for K=0 (zero-strike spread); Kirk (1995) for
K ≠ 0. Apply Kirk's substitution `β = F₂/(F₂+K)` (where `Fᵢ = Sᵢ·exp((r−Dᵢ)T)`) and
treat as Black-Scholes-like on a single asset with proxy volatility
`σ_K = √(σ₁² − 2·β·ρ·σ₁σ₂ + (β·σ₂)²)`. Margrabe is recovered when K=0 (β=1).

**Kirk is an approximation, not exact.** It is exact only when ρ=±1 OR β=1 OR
either σ_i=0 (Carmona-Durrleman 2003). At all other parameter values it has a
moment-matching bias whose magnitude grows with `T`, `|ρ|` (especially as ρ → 1),
and with `|K|` (extreme moneyness, both deep-ITM K<<0 and deep-OTM K>>0). Carmona-
Durrleman characterize Kirk's accuracy as *"relative price errors usually within
a few percentages"* — directionally true but understated for the high-correlation
or long-maturity regime.

**Quantitative Kirk error magnitudes** (Harutyunyan & Masip Borrás 2018, S₀_1=S₀_2=100,
σ₁=0.30, σ₂=0.20, T=0.5, K∈[0,20], 5M-trial MC benchmark):

| ρ      | Max Kirk error vs MC (% of MC price) | Regime |
|--------|---------------------------------------|--------|
| 0.80   | ~0.5%                                 | low ρ, errors small across all K |
| 0.85   | ~0.8%                                 | low ρ |
| 0.90   | ~0.7%                                 | mid ρ |
| **0.95** | **up to ~7% at large K**            | **high ρ — exponential spike** |
| 0.999  | up to ~5% at large K                  | extreme ρ |

A specific worked example from page 26 of that paper: at ρ=0.80, K=5, T=0.5,
Kirk = 0.5616 vs MC 95% CI (0.5399, 0.5428) — **Kirk falls outside a narrow MC CI
by ~3.5-4%** even at low correlation, given enough Monte Carlo paths. The Modified
Kirk's Approximation (Alòs & León 2015, Malliavin-calculus correction) brings the
error back inside the CI; original Kirk does not.

Surface plots at T ∈ {0.1, ..., 0.5} (paper's Figures 6-10) confirm Kirk's error
"takes an exponential shape" with increasing T, ρ, K — i.e., **the longer the
maturity, the more extreme the strike, the more correlated the assets, the bigger
the Kirk-vs-MC gap.**

**Implication for benchmark test design.** When a task pins Kirk by name and tests
Kirk-vs-MC agreement at fixed tolerance, the tolerance must absorb Kirk's intrinsic
approximation error in the regime tested:

- Modest correlation (ρ ≤ 0.85), modest |K|, short T: 1-2% tolerance is fine
- High correlation (ρ ≥ 0.95) OR deep ITM/OTM (|K| ≳ 0.10·avg_spot) OR long T (≥ 1y):
  **Kirk vs MC will disagree by 3-7% by formula, not by Monte Carlo error.** A
  3·SE bound (typical SE ~0.3-1% of price at 500K paths) is too tight to absorb
  this; tests should use either `max(3·SE + ε, 0.04·price)` or skip the deepest
  grid points.
- For empirical validation: in the QF-Bench v323 sweep, all 5 trials of
  `spread-option-kirk-margrabe` (across 5 distinct model families: codex-53c,
  codex-54mini, claude-code_opus46, codex-gpt-5.4-mini, G5.4m) failed
  `test_kirk_mc_agreement` deterministically at the same single grid point
  (T=1.0, K=−0.10·avg_spot, deepest-ITM) with 3-5% Kirk-vs-MC gap. This is
  **the formula's bias, not an agent error** — agents who follow the spec's
  Kirk pin verbatim cannot pass a tolerance tighter than Kirk's intrinsic error.

**Decision procedure for judging:** when an agent fails `test_kirk_mc_agreement`
on a spec-pinned Kirk implementation:

1. Verify the agent's Kirk formula matches canonical (β = F₂/(F₂+K), σ_K as above).
2. Locate the failing (T, K) grid points.
3. If the failing points are ATM/short-T/low-ρ: this is a real agent bug
   (likely B1 unit error, or A2 missing exp(-rT) discount).
4. **If the failing points are extremes (deep-ITM, deep-OTM, long-T, high-ρ): match
   `task_side / brittle pin`, NOT an A/B/C/D mode.** The Kirk formula is doing what
   Kirk does; the test threshold is the bug.

References (verified):
- [Harutyunyan & Masip Borrás (2018), *A Numerical Analysis of the Modified Kirk's
  Formula and Applications to Spread Option Pricing Approximations* — arXiv:1812.04272](https://arxiv.org/abs/1812.04272)
  *(directly verified — pages 22-31 contain Figures 1-10 with Kirk-vs-MC error
  tables at ρ ∈ {0.80, 0.85, 0.90, 0.95, 0.999} and T ∈ {0.1..0.5}; explicit
  numerical example on page 26)*
- [Alòs & León (2015), *On the short-maturity behaviour of the implied volatility
  skew for random strike options*, Quantitative Finance 16(1):31-42](https://www.tandfonline.com/doi/abs/10.1080/14697688.2015.1013499)
  *(introduces the Malliavin-calculus correction that becomes "Modified Kirk")*
- [Carmona & Durrleman (2003), *Pricing and Hedging Spread Options*, SIAM Review
  45(4):627-685](https://www.researchgate.net/publication/228993136_Pricing_and_Hedging_Spread_Options)
  *(directly verified abstract — characterizes Kirk as "relatively accurate" with
  "relative price errors usually within a few percentages"; lower-bound method
  proposed as alternative; full quantitative tables not extracted here)*
- [Margrabe (1978), *The Value of an Option to Exchange One Asset for Another*,
  Journal of Finance 33(1):177-186](http://www.stat.nus.edu.sg/~stalimtw/MFE5010/PDF/margrabe1978.pdf)
- Kirk, E. (1995), *Correlation in the Energy Markets*, in *Managing Energy Price
  Risk* (Risk Publications) — original 1995 reference, no open URL

### D.5  Cliquet / ratchet pricing

**Industry standard:** Per-period local cap and floor, plus global floor. Reset at each
fixing date. Closed-form available under BS for vanilla cliquet; Heston/SV requires MC.

### D.9  Implied-vol surface parameterization

**Industry standard:**
- **Parametric (per-slice / full surface):** SVI (*Stochastic Volatility Inspired*) for
  individual maturity slices; SSVI (Surface SVI) for the full surface, with arbitrage-free
  calibration constraints.
- **Non-parametric:** arbitrage-free smoothing splines (Fengler 2009) — fit to call
  prices vs strike (not to vols vs moneyness), under shape constraints. The non-arbitrage
  conditions take a simpler form on call prices than on vols.

A non-arbitrage-free surface produces negative transition probabilities downstream
(local-vol calibration, exotics pricing) and corrupts every Greek that uses the surface
as input. Failing to enforce arbitrage-freeness when the spec asks for an IV surface is
an A3.f gap.

References:
- [Gatheral & Jacquier (2014), *Arbitrage-Free SVI Volatility Surfaces*, Quantitative Finance 14(1):59–71 — arXiv preprint](https://arxiv.org/abs/1204.0646) *(directly verified — title, authors, abstract confirm SSVI calibration)*
- [Gatheral (2004), *A parsimonious arbitrage-free implied volatility parameterization* — Baruch MFE distinguished lecture notes](https://mfe.baruch.cuny.edu/wp-content/uploads/2015/06/VW3.pdf)
- [Fengler (2009), *Arbitrage-free smoothing of the implied volatility surface*, Quantitative Finance 9(4):417–428 — Tandfonline DOI](https://www.tandfonline.com/doi/abs/10.1080/14697680802595585) *(paywalled; DOI verified `10.1080/14697680802595585` via RePEc + Semantic Scholar + ResearchGate)*
- [Fengler (2009) — open-access SSOAR mirror](https://www.ssoar.info/ssoar/bitstream/handle/document/22137/ssoar-2009-04-fengler-arbitrage-free_smoothing_of_the_implied.pdf?sequence=1&isAllowed=y)
- [RePEc index entry for Fengler (2009)](https://ideas.repec.org/a/taf/quantf/v9y2009i4p417-428.html)

---

## E. Curve Construction & Bond Math

### E.1  OIS-discounting for collateralized swaps

**Industry standard (post-2008):** Use OIS (overnight) curve for discounting cashflows
on collateralized derivatives. Use LIBOR/SOFR projection curve for forecasting floating
legs. Conflating into a single-curve model is a 2004-style gap that fails in modern
markets.

### E.2  Day-count conventions

**Industry standard (USD market):**
- USD floating leg (LIBOR/SOFR): **ACT/360**
- USD fixed leg: **30/360 ISDA**
- US Treasury: **ACT/ACT**
- Sovereign bonds (UK gilts, German bunds): **ACT/365F**

For swap rates, the day-count drives the payment-fraction calculation. Wrong day-count
shows up as ~2.5% drift in PV (depending on tenor).

### E.3  Yield curve bootstrapping order

**Industry standard:** Bootstrap zero rates *recursively* from short to long. Compute
DF[T_n] using already-known DF[T_1..T_{n-1}] and the n-th instrument's par/zero rate.
Solving each tenor independently produces non-monotonic curves and is a clear A3.f gap.

### E.4  Par-to-zero rate conversion

**Industry standard:** `z = -(2/τ) · ln(1 - r·τ/2)` for semi-annual par rates to
continuous zero. The factor of 2 (semi-annual) is critical. A common B1 gap: forgetting
the 2× scaling produces zeros half their correct magnitude.

### E.5  Nelson-Siegel functional form

**Industry standard:**
`r(T) = β₀ + β₁ · (1-exp(-T/λ))/(T/λ) + β₂ · ((1-exp(-T/λ))/(T/λ) - exp(-T/λ))`

The `(1-exp(-T/λ))/(T/λ)` weighting is *required* — without it, the function is just an
exponential decay and lacks the hump-shape Nelson-Siegel was designed to capture.
Svensson (1995) extends by adding `β₃` term with second decay parameter `λ₂`.

---

## F. Portfolio Construction

### F.1  Cross-sectional momentum

**Industry standard (Jegadeesh-Titman 1993):** 11-month formation window
`[t-12, t-2]` (skip the most recent month, which exhibits short-term reversal). Rank
on sum of 11 monthly returns (arithmetic). Hold 1 month, equal-weight long top decile,
short bottom decile (or top/bottom 3 in small universe).

### F.2  Mean-variance optimization

**Industry standard:** Sample covariance + Ledoit-Wolf shrinkage to identity (or to
single-factor). Pure sample covariance is unstable for N > T/4.

### F.3  Risk parity / Equal Risk Contribution (ERC)

**Industry standard:** Solve
`w_i · (Σw)_i = w_j · (Σw)_j` for all i, j subject to `Σ w_i = 1`. Use SLSQP or
Newton with positivity constraint. Closed-form for diagonal Σ: `w_i = 1/σ_i / Σ(1/σ_j)`.

### F.4  Bollinger Bands

**Industry standard:** Lookback = 20 periods, k = 2 standard deviations. Trade rules:
- Mean-reversion: short on touch of upper band, long on touch of lower band, exit at MA
- Breakout: long on close above upper band, short on close below lower band

The `k=2` is universal — k=1 or k=2.5 require explicit citation. The mean-reversion
interpretation is more common in equities backtests.

### F.5  Execution cost / market impact for backtests

**Industry standard (model layer):**
- **Optimal-execution framework:** Almgren–Chriss (2000) — `cost = ½ · γ · X² + η · X²/T + λ·σ²·∫x(t)²dt` for total quantity X over time T. Linear permanent
  impact `γ·X` and linear temporary impact `η·X/T` are the canonical model assumptions.
- **Empirical impact for large parent orders (rule of thumb):** the **square-root law**
  — `impact ≈ Y · σ · √(Q / V)` where Q is order size, V is daily volume, σ daily
  vol. Widely documented in the empirical microstructure literature (BARRA / Torre-Ferrari, Kissell, Bouchaud / CFM).
  - Note: the square-root is empirical and does *not* come from Almgren–Chriss (2000)
    or Almgren et al. (2005). Almgren et al. (2005) actually rejected √ in favor of a
    `3/5` power law on their dataset; the universal-√ claim is from a separate
    empirical literature.

**Industry standard (backtest layer):**
For daily / monthly equity backtests, model TC as `tc = 0.5·spread + impact_term`:
- `0.5·spread` covers the half-spread an aggressor pays.
- `impact_term`: constant (bps) is fine for sub-1% participation; switch to
  `λ·σ·√(participation)` once orders exceed ~5% of ADV.

Treating TC as a single hard-coded bps figure is acceptable for low-frequency strategies
but breaks down on intraday or large-notional simulations. For these, a participation-
dependent impact model is required.

References:
- [Almgren & Chriss (2000), *Optimal Execution of Portfolio Transactions*, Journal of Risk 3(2):5–39 — author PDF mirror](https://www.smallake.kr/wp-content/uploads/2016/03/optliq.pdf) *(linear-impact framework; cited correctly for the model, NOT for the √-law)*
- [Almgren-Chriss (2000) — Risk.net journal page (paywall)](https://www.risk.net/journal-of-risk/volume-3-number-2-winter-2000)
- [Almgren-Chriss (2000) — Semantic Scholar entry](https://www.semanticscholar.org/paper/Optimal-execution-of-portfolio-trans-actions-Almgren-Chriss/4ea1885d7f00dc2ba59be2d6cc62923de23599ce)
- [Almgren, Thum, Hauptmann, Li (2005), *Direct Estimation of Equity Market Impact*, Risk 18(7):58–62](https://www.cis.upenn.edu/~mkearns/finread/costestim.pdf) — **NOTE**: this paper REJECTS the universal √-law in favor of a 3/5 power exponent on its dataset. Cite for the empirical pipeline, NOT for the √-law claim.
- [Bouchaud (2024), *The Square-Root Law of Market Impact* — practitioner survey on the empirical √-law](https://bouchaud.substack.com/p/the-square-root-law-of-market-impact) *(directly verified: states "price moves up/down by amount proportional to sqrt(Q)")*
- [Durin, Rosenbaum, Szymanski (2023), *The two square root laws of market impact and the role of sophisticated market participants*, arXiv 2311.18283](https://arxiv.org/abs/2311.18283) *(directly verified — modern refinement of the empirical √-law)*
- [Lillo, *Market impact models and optimal execution algorithms* — Imperial College CFM lecture series (June 2016)](https://www.imperial.ac.uk/media/imperial-college/research-centres-and-groups/cfm-imperial-institute-of-quantitative-finance/events/Lillo-Imperial-Lecture3.pdf)

### F.10  Cross-sectional standardization order: winsorize THEN z-score

**Industry standard:** Apply in this order at every rebalance period:
1. **Winsorize** raw factor values cross-sectionally at the 1st / 99th percentile (or
   ±3σ for z-pre-cap pipelines).
2. **Z-score** the winsorized values to mean 0, std 1 (cross-sectional, market-cap-weighted
   mean for some commercial models).
3. (Optional) Combine multiple standardized factors with weights.

Reversing the order — z-score first, then winsorize — pulls outliers back into the
z-score's tail because winsorization caps *after* z = 5σ outliers have inflated the
denominator. The downstream factor combination then weighs those outliers
inappropriately. This is a documented, recurring A3.f / F.10 gap.

Used by all three large commercial vendors:

References:
- [MSCI Quality Indexes Methodology (June 2014)](https://www.msci.com/eqb/methodology/meth_docs/MSCI_Quality_Indexes_Methodology_June_2014.pdf) *(directly verified passage: "After winsorizing all the three variables within each MSCI Parent Index, the Z-Score for each... can be calculated using the mean and standard deviation of the relevant variable")*
- [MSCI FaCS Methodology (January 2018)](https://www.msci.com/downloads/web/msci-com/research-and-insights/blog-post/international-small-caps-are-alive-and-kicking/Introducing-MSCI-FaCS-White-Paper.pdf) — same MSCI standardization convention
- [AQR — *Measuring Portfolio Factor Exposures: A Practical Guide*](https://www.aqr.com/-/media/AQR/Documents/Insights/Trade-Publications/Measuring-Portfolio-Factor-Exposures-A-Practical-Guide.pdf) *(directly verified passage: "raw scores are computed, extremes are winsorized to limit outliers, and standardization (z-scores) is applied for cross-sectional comparability")*
- [AQR practical guide — open mirror](https://www.smallake.kr/wp-content/uploads/2017/03/Measuring_Portfolio_Factor_Exposures_A_Practical_Guide.pdf)
- [Barra USE3 US Equity Risk Model Handbook (alacra mirror)](https://www.alacra.com/alacra/help/barra_handbook_US.pdf) *(descriptor-level: winsorize-then-z-score; factor-exposure level: re-z-score-then-winsorize at ±3σ)*
- [Barra USE4 Methodology Notes (August 2011)](https://www.top1000funds.com/wp-content/uploads/2011/09/USE4_Methodology_Notes_August_2011.pdf) — current-version Barra US Equity model documentation

---

## G. Schema & Output Conventions

### G.1  Date serialization

**Industry standard:** ISO-8601 date-only `YYYY-MM-DD` for date columns; ISO-8601 with
timezone `YYYY-MM-DDTHH:MM:SS+00:00` for timestamps. Pandas `.dt.strftime('%Y-%m-%d')`
is the standard idiom. Mixing timestamp with `00:00:00` time component is a D1.f gap.

### G.2  Numeric serialization in JSON

**Industry standard:** Floats as `float`, ints as `int`, no string-encoded numbers. NaN
serialization: typically `null` (not `NaN` literal) unless using `simplejson` with
`ignore_nan=False`. Dates as ISO strings, not Unix timestamps.

### G.3  Sentinel values

**Industry standard:** `None` / `null` for missing data, never `999999` or `-1` (sentinel
values are vendor-specific; in production they get winsorized or NaN-filled before
modeling).

---

## I. Backtest Discipline (Point-in-Time Integrity)

These are universal — every backtest a senior quant signs off on must satisfy them.
Look-ahead bias is the single most common backtest gap and the one institutional risk
teams audit hardest. Failure to apply any of these is `agent_conceptual` (industry
knowledge gap), not `task_side`.

### I.1  Signal-at-time-t uses only data with timestamp ≤ t

**Industry standard:** Any rolling, expanding, EWMA, or cross-sectional statistic
feeding a signal at time t must be computed strictly from data observable at time t.
In code: rolling windows must end at `t-1` for the signal at `t`; or use the signal at
`t-1` to trade the open at `t`. Pandas `.shift(1)` is the standard idiom.

The aliased canonical mistake: `df['signal'] = df['close'].rolling(20).mean()` and
trading at `df['close'][t]` on the same day — the rolling mean already absorbed the
day-t close.

### I.2  Fundamental data uses release date, not fiscal-period-end

**Industry standard:** Quarterly Compustat fundamentals are timestamped to **fiscal
period end**, but only become *publicly known* on the report-release date —
typically 4–8 weeks (quarterly) or up to 90 days (annual) later. Using the
fiscal-period-end as the "available-at" date is a classic look-ahead violation.

For analyst-estimate revisions (IBES) and consensus data, use the **historical snapshot**
as of t (not the as-of-today snapshot, which contains revisions made after t).

Point-in-time databases (Compustat-PIT, FactSet PIT, S&P PIT) timestamp every datum to
its first public-release date precisely to prevent this gap.

### I.3  Universe / survivorship — tradeable set at t

**Industry standard:** The tradeable universe at time t is the set of securities
*tradeable at time t*, not the current CRSP / S&P 500 membership backfilled. Survivorship
bias inflates backtest returns by 1–4 %/year (depending on universe definition and
horizon). For US equities, use point-in-time index membership (S&P PIT, Russell PIT) or
CRSP's monthly membership flag.

### Operational test

Three diagnostic questions a reviewer asks of any backtest code:

1. *"For every signal, can I trace the timestamp of its most recent input?"* — If any
   input has timestamp ≥ signal time → I.1 violation.
2. *"For every fundamental field, is the lookup keyed on report-release date or fiscal-
   period-end?"* — Period-end key → I.2 violation.
3. *"Was the universe filter applied with information available at t, or with today's
   index membership?"* — Today's membership → I.3 violation.

References:
- [FactSet whitepaper — *Accurately Backtesting Financial Models Through Point-In-Time*](https://insight.factset.com/hubfs/Resources%20Section/White%20Papers/ID11996_point_in_time.pdf) *(institutional-vendor whitepaper; covers I.1 / I.2 jointly)*
- [S&P Capital IQ — *Point-In-Time vs. Lagged Fundamentals* (whitepaper)](https://www.spglobal.com/marketintelligence/en/documents/sp-capitaliq-quantamental-point-in-time-vs-lagged-fundamentals.pdf) *(403 anti-bot block on direct fetch; document is real per S&P Marketplace listing — cross-vendor confirmation that PIT backtests differ from lagged-fundamentals backtests, with deviation inversely related to reporting-window length)*
- [FactSet — *Understanding Regime Changes for Robustness in Backtesting*](https://insight.factset.com/understanding-regime-changes-for-robustness-in-backtesting) — secondary FactSet PIT discussion
- [AnalystPrep CFA Level 2 — *Problems in Backtesting and Biases in Data*](https://analystprep.com/study-notes/cfa-level-2/problems-in-backtesting/) *(directly verified content: covers look-ahead, survivorship, reporting lag as canonical biases)*
- [Corporate Finance Institute — *Look-Ahead Bias*](https://corporatefinanceinstitute.com/resources/career-map/sell-side/capital-markets/look-ahead-bias/) *(directly verified content: educational definition matching I.1)*
- [Calcbench — *Point-in-Time Fundamental Data*](https://www.calcbench.com/blog/post/153949139113/Point-In-Time-Fundamental-Data) *(directly verified content: discusses report-release vs fiscal-period-end lag for I.2)*

---

## H. The "No One Tells You" List

These are common-sense practices an experienced quant applies *without being prompted*.
An LLM agent failing to apply these is `agent_conceptual` (industry knowledge gap),
not `task_side`:

1. **Rannacher start** for FD pricing of non-smooth payoffs (digital, American, barrier).
2. **Filter / downweight long-dated commodity options** (>1Y) when calibrating vols —
   they're illiquid and noisy.
3. **Same RNG seed across bumped/base paths** for FD-based MC Greeks.
4. **Pin sort kind to `'stable'`** in `pandas.sort_values` when followed by
   `drop_duplicates(keep='last')` (else: D1.g engineering gap).
5. **Vol-space (not price-space) objective** in implied-vol surface calibration.
6. **Anchor PCA eigenvector signs** — first loading positive, OR maximize positive
   correlation with reference series.
7. **Refit AR(1) on the spread, not residuals/innovations** for half-life
   estimation.
8. **Use OIS for discounting, projection curve for forwards** (post-2008 dual-curve).
9. **`ddof=1` explicitly** when using `numpy.std` for sample-volatility (numpy default
   ddof=0 is biased).
10. **Annualize Sharpe by `√252`**, not `√365` or `√260`.
11. **Forward ATM, not spot ATM**, for option-strike anchoring.
12. **Recursive bootstrap** for yield curve, not independent per-tenor solving.
13. **Acerbi-Tasche rank-based ES**, not threshold form, for empirical samples.
14. **Loss-space VaR/CVaR sign** (positive losses), not return-space (negative returns).
15. **NW1994 auto-bandwidth** as default for HAC unless NW1987 explicitly cited.

---

## Operational Use

In v3.1, when judging a cell where an A3 / C3.c / B-class hit appears, apply this
catalog:

1. **Spec citation present?** (YES → spec-authored case in authorship pre-check, A1/A2/A3
   normally with strict-variant requirement.)
2. **Industry standard exists in this catalog?** (YES → if agent picked non-standard,
   classify as **A3.f** with `root_cause_class = agent_conceptual`. Add to `notes`:
   *"Industry standard for [X] is [Y]; agent used [Z] without justification — see
   INDUSTRY_STANDARDS.md §[ref]."*)
3. **Neither cited nor industry-standard?** (YES → genuine `task_side`, classify as
   C3.c.)

This catalog is a living document; new entries should be added when a new
"no-one-tells-you" pattern recurs across ≥2 task failures and is verifiable against
finance literature.
