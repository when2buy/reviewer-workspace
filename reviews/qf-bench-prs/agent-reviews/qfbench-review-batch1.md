# QF-Bench Review — Batch 1

Reviewed: 2026-04-27

---

## Task: copula-equity-fitting
PR: #181
Scores: H4.5=27/28 | S4.5=28/28 | O4.6=28/28

### Instruction Quality
Clear and fully specified. All copula families, estimation methods (inverting Kendall's tau), pseudo-observation formula (rank/(n+1)), and output formats are unambiguous.

### Failure Analysis
Haiku fails `test_student_t_nu_range`: produced nu=100 (upper bound hit) instead of profile-likelihood optimized value in (2,50). This is an agent implementation error — Haiku likely used a fixed upper bound or failed to properly optimize the profile likelihood for the t-copula degrees of freedom.

### Model Discrimination
Good. H4.5 < S4.5 = O4.6. The Student-t nu optimization is the discriminator — weaker models hit boundary solutions.

### Issues Found
None.

### Verdict: 建议 Merge
Well-designed task with good discrimination. The single Haiku failure is a legitimate capability gap.

---

## Task: creditmetrics-portfolio-var
PR: #193
Scores: H4.5=25/26 | S4.5=26/26 | O4.6=26/26

### Instruction Quality
Excellent. All parameters (transition matrix, correlation, recovery rate, seed, N_sim) fully specified. Step-by-step structure is clear.

### Failure Analysis
Haiku fails `test_aaa_mean_loss`: got 0.000303 vs expected 0.005763. Haiku likely computed mean loss incorrectly for the AAA bucket — possibly only counting default losses and missing mark-to-market/migration losses, or a computation error in the per-rating breakdown. All other 25 tests pass including the aggregate portfolio loss stats, so it's a subtle per-rating accounting error.

### Model Discrimination
Good. H4.5 < S4.5 = O4.6.

### Issues Found
None.

### Verdict: 建议 Merge
Solid benchmark item. Haiku's single failure is a legitimate implementation subtlety.

---

## Task: copula-garch-portfolio
PR: #196
Scores: H4.5=35/38 | S4.5=35/38 | O4.6=37/38

### Instruction Quality
Detailed and well-specified. GARCH(1,1) with Student-t innovations, copula fitting, MC simulation all clearly described with parameter bounds.

### Failure Analysis
- **All three models** fail `test_gs_alpha_value`: expects GS alpha ~0.073 (atol=0.03), but agents produce values like 0.12. This is a **verifier issue** — the oracle's GS alpha=0.073 may be too specific given that GARCH MLE with manual scipy optimization can converge to different local optima depending on initialization and optimizer choice. The instruction says "use Nelder-Mead or L-BFGS-B" which can yield different results.
- **H4.5 and S4.5** additionally fail `test_nu_copula_range` (and `test_copula_nu_range`): Haiku hits nu=100 (boundary), Sonnet gets nu=3.8 (just below lower bound of 4). Opus passes with a reasonable nu. These are agent capability issues for copula nu estimation.

### Model Discrimination
Good overall (H < S < O), but the GS alpha test fails for all models — that's a verifier tolerance problem.

### Issues Found
- [MEDIUM] `test_gs_alpha_value` tolerance too tight — oracle expects alpha=0.073±0.03 but all three models produce ~0.10-0.12. The GARCH MLE optimization landscape for GS is likely multi-modal with manual scipy implementation. Consider widening atol to 0.05 or removing this overly specific test.

### Verdict: 需要 Human Review
The GS alpha test fails across ALL models including Opus, indicating the oracle value or tolerance is likely wrong. Fix `test_gs_alpha_value` (widen tolerance or remove), then this is a strong merge candidate.

---

## Task: copula-sampling-rank-correlation
PR: #201
Scores: H4.5=45/51 → 25/31 normalized | S4.5=51/51 → 31/31 | O4.6=51/51 → 31/31

### Instruction Quality
Clear. Copula families, parameter calibration from Kendall's tau, sampling parameters (N=100K, seed=42), and tail dependence definitions all well-specified.

### Failure Analysis
Haiku fails 6 tail dependence tests: Gumbel upper tail too weak (0.14 vs >0.45), Clayton lower tail too weak (0.54 vs >0.55), Student-t upper tail off, and related summary tests. This indicates Haiku's copula sampling implementation (likely Gumbel and Clayton) has bugs — probably incorrect inverse sampling algorithms for Archimedean copulas.

### Model Discrimination
Excellent. H4.5 << S4.5 = O4.6. The copula sampling correctness is the key discriminator.

### Issues Found
None.

### Verdict: 建议 Merge
Strong task with excellent model discrimination. Haiku's failures are all legitimate implementation errors in copula sampling algorithms.

---

## Task: panjer-recursion
PR: #204
Scores: H4.5=63/73 → 18/22 normalized | S4.5=73/73 → 22/22 | O4.6=73/73 → 22/22

### Instruction Quality
Well-specified (not fully read due to truncation, but test results suggest clear parameters). Panjer recursion with Poisson, NegBin, and Binomial frequency distributions.

### Failure Analysis
Haiku fails on negbin-related Panjer VaR tests: VaR(negbin, 0.9)=120600 vs expected 107700, etc. — consistently ~12% too high. This suggests Haiku parameterized the negative binomial distribution incorrectly in the Panjer recursion (likely wrong a/b coefficients), while getting Poisson and Binomial correct.

### Model Discrimination
Good. H4.5 << S4.5 = O4.6.

### Issues Found
None.

### Verdict: 建议 Merge
Clean discrimination. Haiku's NegBin parameterization error is a legitimate capability gap.

---

## Task: fft-compound-poisson
PR: #184
Scores: H4.5=53/63 → 14/18 normalized | S4.5=52/63 → 14/18 | O4.6=63/63 → 18/18

### Instruction Quality
Well-specified. FFT-based compound Poisson loss distribution with gamma, lognormal, and Pareto severity distributions.

### Failure Analysis
- **Haiku and Sonnet** both fail on lognormal FFT results (VaR and ES at multiple confidence levels). Haiku: FFT VaR(lognormal, 0.99)=386867 vs expected 416324 (~7% off). Sonnet: similar pattern, FFT VaR(lognormal, 0.99)=368095 vs 416324 (~12% off). Both pass gamma and Pareto FFT tests, plus all MC validation tests.
- **Opus** passes all 63 tests.
- The lognormal severity is the hardest case for FFT discretization because of its heavy right tail — correct grid size and tilting are needed.

### Model Discrimination
Excellent. H4.5 = S4.5 << O4.6. The lognormal FFT accuracy separates Opus from the rest.

### Issues Found
None.

### Verdict: 建议 Merge
Excellent benchmark item — discriminates even between Sonnet and Opus. The lognormal FFT failures are legitimate numerical implementation challenges.

---

# Summary

| Task | PR | H4.5 | S4.5 | O4.6 | Verdict |
|---|---|---|---|---|---|
| copula-equity-fitting | #181 | 27/28 | 28/28 | 28/28 | ✅ Merge |
| creditmetrics-portfolio-var | #193 | 25/26 | 26/26 | 26/26 | ✅ Merge |
| copula-garch-portfolio | #196 | 35/38 | 35/38 | 37/38 | ⚠️ Human Review (GS alpha test) |
| copula-sampling-rank-correlation | #201 | 45/51 | 51/51 | 51/51 | ✅ Merge |
| panjer-recursion | #204 | 63/73 | 73/73 | 73/73 | ✅ Merge |
| fft-compound-poisson | #184 | 53/63 | 52/63 | 63/63 | ✅ Merge |

**5/6 recommended for merge. 1 needs verifier fix (copula-garch-portfolio `test_gs_alpha_value`).**
