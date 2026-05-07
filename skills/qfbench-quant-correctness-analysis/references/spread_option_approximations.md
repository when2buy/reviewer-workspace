# Spread Option Approximations — Reference for Judges

Companion reference for `INDUSTRY_STANDARDS.md` § D.4. When judging a failed
trial that involves Margrabe / Kirk / Modified-Kirk / Bjerksund-Stensland
spread option formulas, consult this doc first.

## What's exact, what's approximate

| Formula | Exact when | Approximate when | Bias direction |
|---|---|---|---|
| **Margrabe (1978)** | K = 0 always | (never approximate at K=0) | (none) |
| **Kirk (1995)** | ρ = ±1 OR β = 1 OR σ_i = 0 | All other (ρ, K, T) | Generally **over-prices** at low/mid ρ; **under-prices** at very high ρ |
| **Modified Kirk** (Alòs-León 2015) | (same exactness conditions as Kirk) | Reduces Kirk error by ~10× at high ρ via Malliavin correction | Smaller residual bias |
| **Bjerksund-Stensland (2014)** | Same exactness conditions | Improves over Kirk for energy markets and asymmetric vols | Comparable to Modified Kirk |

**Margrabe is exact**, full stop, when K=0. Tests that compare Margrabe to MC at K=0
should use only `tol = c·SE` for Monte Carlo error — there's no formula bias to
absorb. Failures here = real agent bug.

**Kirk is approximate** in all real cases (ρ=±1 doesn't occur empirically, β=1 means
K=0 which is Margrabe). The bias is deterministic given the parameters.

## Empirical Kirk error magnitudes (paper-verified)

From [Harutyunyan & Masip Borrás (2018), arXiv:1812.04272](https://arxiv.org/abs/1812.04272),
S₀_1 = S₀_2 = 100, σ₁ = 0.30, σ₂ = 0.20, T = 0.5, K ∈ [0, 20], 5M-trial MC benchmark:

```
ρ=0.80:  ~0.5% max     ← <1% across all K
ρ=0.85:  ~0.8% max     ← <1%
ρ=0.90:  ~0.7% max     ← <1%
ρ=0.95:  up to ~7%     ← spike at large K
ρ=0.999: up to ~5%     ← spike at large K
```

(Read directly from the paper's superposed-plot y-axis limits, page 28-31.)

**Specific worked example** (page 26): at ρ=0.80, K=5, T=0.5:
- Kirk = 0.5616
- MC 95% CI = (0.5399, 0.5428)
- Modified Kirk = 0.5414 (inside CI)
- **Kirk is 3.5-4% over-priced even at low correlation when MC is precise enough.**

**Surface plots** (Figures 6-10, T ∈ {0.1, 0.2, 0.3, 0.4, 0.5}): the paper's own
statement is that Kirk's error *"takes an exponential shape"* with increasing T,
ρ, K. Modified Kirk stays nearly constant.

## Empirical evidence from QF-Bench v323

`spread-option-kirk-margrabe` (15 trials judged across 5 model families):
- 5 of 15 failed `test_kirk_mc_agreement`
- All 5 failed at the **same single grid point**: T=1.0, K=−0.10·avg_spot
  (deepest-ITM longest-T)
- Error magnitude across the 5 trials: **3.4-4.5% Kirk-vs-MC gap**
- Test tolerance: 3·SE ≈ 0.04 of price
- All other 14 of 15 grid points pass

**This is empirical proof that Kirk's intrinsic bias at the deepest-ITM extreme
is in the same 3-5% range as the paper documents at high-correlation extremes.**
The bias mechanism is symmetric: Kirk's moment-match deteriorates whenever β
moves far from 1, which happens at extreme |K| OR extreme |ρ|.

## Decision procedure for judging Kirk-vs-MC failures

1. **Read the failing test traces.** Identify the (T, K) grid points where the
   test fails.

2. **Classify the regime:**

   | Regime | Likely Kirk-vs-MC gap | Likely cause |
   |---|---|---|
   | ATM (K≈0), short T, low ρ | <0.5% | Real agent bug if it fails |
   | OTM/ITM moderate (|K|/spot < 0.05), T ≤ 0.5 | <1% | Real agent bug if it fails |
   | Deep ITM/OTM (|K|/spot ≥ 0.10) OR high ρ (≥0.95) OR long T (≥1y) | 3-7% | **Task-side brittle pin if test tol is <5%** |

3. **Verify the agent's Kirk formula is canonical.** It should be:
   ```
   F_i  = S_i · exp((r - D_i) · T)
   beta = F_2 / (F_2 + K)
   sigma_K = sqrt(sigma_1^2 - 2*beta*rho*sigma_1*sigma_2 + (beta*sigma_2)^2)
   v   = sigma_K * sqrt(T)
   d_1 = (log(F_1 / (F_2 + K)) + 0.5 * v^2) / v
   d_2 = d_1 - v
   price = exp(-r * T) * (F_1 * Phi(d_1) - (F_2 + K) * Phi(d_2))
   ```

4. **If formula is canonical AND failing point is in the extreme regime:**
   match `task_side / brittle pin`, NOT A/B/C/D. Confidence 0.85+ if there are
   replicates across model families.

5. **If formula is wrong:** match the appropriate A/B mode (A2 missing
   discount, B1 unit error in σ, B2 sign flip, etc.) at high confidence.

## Recommended task-design fixes

When a benchmark task pins Kirk by name and the test trips at an extreme point,
the task itself is the bug. Fixes in order of disruption:

1. **Tolerance with absolute floor.** Replace `tol = 3*se + 0.001` with
   `tol = max(3*se + eps, 0.04 * max(kirk, mc))`. The 4% floor matches the paper-
   documented + empirical-verified worst-case Kirk bias and absorbs the formula's
   intrinsic error while still catching agents whose Kirk is grossly wrong.

2. **Skip the deepest grid points.** Exclude `(T=1, K = ±0.10·avg_spot)` from
   the agreement test — keep monotonicity and ATM tests intact.

3. **Add a spec note.** *"Kirk's approximation is known to have ~3-5% bias at
   deep-ITM/deep-OTM long-T grid points. Test tolerance allows for this."* —
   doesn't fix the test, but at least documents intent.

4. **Switch to Modified Kirk.** Update spec to require Alòs-León 2015 Modified
   Kirk; tighten test tolerance accordingly. Most disruption — agents now need
   to know the Malliavin correction.

## References (verified)

- **Margrabe (1978).** *The Value of an Option to Exchange One Asset for Another.*
  Journal of Finance 33(1):177-186.
  [Open PDF](http://www.stat.nus.edu.sg/~stalimtw/MFE5010/PDF/margrabe1978.pdf)
- **Kirk (1995).** *Correlation in the Energy Markets.* In *Managing Energy
  Price Risk* (R. Jameson, ed.), Risk Publications and Enron Capital & Trade
  Resources, pp. 71-78. Original 1995 reference; no open URL — book chapter only.
- **Carmona & Durrleman (2003).** *Pricing and Hedging Spread Options.* SIAM
  Review 45(4):627-685. *(Comprehensive survey. Verbatim quote: "Kirk's
  approximation is relatively accurate given its simple form, with relative
  price errors usually within a few percentages.")*
  [ResearchGate](https://www.researchgate.net/publication/228993136_Pricing_and_Hedging_Spread_Options)
- **Alòs & León (2015).** *On the short-maturity behaviour of the implied
  volatility skew for random strike options and applications to option pricing
  approximation.* Quantitative Finance 16(1):31-42.
  doi:10.1080/14697688.2015.1013499. *(Introduces the Malliavin-calculus
  correction that becomes Modified Kirk.)*
- **Harutyunyan & Masip Borrás (2018).** *A Numerical Analysis of the Modified
  Kirk's Formula and Applications to Spread Option Pricing Approximations.*
  arXiv:1812.04272. *(Source of the quantitative error tables in this doc.
  Read directly from PDF; pages 22-31 are the numerical-results section.)*
  [arXiv](https://arxiv.org/abs/1812.04272)

## Note on offline reference

The Harutyunyan & Borrás paper is the primary quantitative source. Future
judges can find it at the arXiv URL above. We do not vendor the PDF in this
skill repo (copyright); the citation + page numbers + extracted summary in
this doc and in `INDUSTRY_STANDARDS.md` § D.4 are the canonical extract.
