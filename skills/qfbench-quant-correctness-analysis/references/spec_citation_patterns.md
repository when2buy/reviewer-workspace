# Spec-Citation Pattern Catalog

*Empirical source: full scan of the 85 V11-focus QF-Bench task instructions (canonical 82 + PR #135/#136/#137), May 2026. Scanner script preserved at `scripts/scan_citations_v2.py` in the audit workspace.*

This file is the empirical evidence behind the **Spec-Citation Extraction Pre-check** in `prompts/system_judge.md`. The judge consults this catalog when deciding whether a failure is `task_side` (genuinely under-specified) vs `agent_conceptual` (agent ignored a citation that was right there in the spec).

## Top-line statistics

After scanning all 85 instruction.md files:

| Regime | Count | What it means |
|---|---|---|
| **spec-authored** | 56 | Spec contains formulas / kwargs / pinned params / pseudocode → answer is **in** the spec |
| **spec-delegates** | 23 | Spec names a method or author but doesn't inline-pin the formula → industry-standard default expected |
| **silent** | 6 | Procedural-goal description with neither citation nor formula (NLP / refactor tasks; rare) |

The 56 spec-authored count is the headline finding — **two-thirds of QF-Bench task specs are fully self-contained**. Treating any failure on these as `task_side` would be a misclassification.

## Eight citation/pinning patterns

### Pattern 1 — Author–Year cite (21 tasks)

Form: `Surname (YYYY)`, `(Surname YYYY)`, `Surname & Surname (YYYY)`.

Concrete examples found:
- `Levy (1992)` — asian-option-levy-curran:75
- `Barone-Adesi & Whaley (1987)` — barone-adesi-whaley:8
- `Engle (2002)` — dcc-garch
- `Garman & Klass (1980)`, `Yang & Zhang (2000)` — ohlc-realized-vol-estimators
- `Geske (1979)` — compound-option-geske
- `Andersen et al. (2003)` — realized-vol-estimators
- `Reiner & Rubinstein (1991)` — lookback-options
- `Smith (2005)` — smith-tail-index

Authoring weight: **strong**. When present, the agent should match the named paper's variant exactly.

False-positive trap: month-year patterns (`Jan 2019`, `December 2024`). Filter out with a month-name blocklist before matching.

### Pattern 2 — Textbook section reference (11 tasks)

Form: `Vol [IVX]+ §[\d.]+`, `Chapter N`, `§N.N`, `Problem(s) N`, `Equation (N)`, `Appendix [A-Z]`.

Concrete examples:
- `Vol II §3.2.2` — barone-adesi-whaley:10
- `Vol I §4.2.3` — bs-greeks-pde:10
- `Vol II §2.2.2` — digital-barrier-options:10
- `Vol II §7.2.1, Problems 5–8` — implied-vol-approximations
- `Problems 1, 5` — dupire-local-vol:112

Most often a Chin–Ólafsson–Nel (or similar) textbook reference. Weight: **strong**. The agent should consult the cited section's exact formula.

### Pattern 3 — Cross-file reference (47 tasks)

Form: prose phrasing like `see <name>.md`, `in /app/data/<name>.json`, `from <name>.csv`, plus bare backticked filenames `` `params.json` ``.

Concrete examples:
- `in target_periods.csv` — 13f-amendment-aware-crowding:37
- `in params.json` — alpha-hedge-strategy:43
- `from /app/spy_daily.csv` — barone-adesi-whaley:38
- `formulas.md` — evt-pot-var (a sibling file fully spelling out the EVT formulas)
- `task_rules.json` — quantamental-earnings (machine-readable rule pins)
- `trade.json` — mtm-xccy-basis-desk:30 (carries day-count, interpolation, notional conventions)

Authoring weight: **strong**. Crucially, when the spec says *"use the conventions in trade.json as the source of truth"*, that file IS the spec. Failing to read it is `agent_conceptual`, not `task_side`.

Concrete miss in the original v3.1: `evt-pot-var` was scored A3.f because the v3.1 pre-check looked at instruction.md only. The cross-file reference to `formulas.md` was the actual formula pin.

### Pattern 4 — Inline TeX math (15 tasks; 277 individual hits)

Form: `$...$` (inline), `$$...$$` (display), or any `\Phi`, `\frac`, `\sqrt`, `\sigma`, `\lambda` etc. backslash macros.

Concrete examples:
- `$\frac{dS}{S} = (r - D) dt + \sigma dW$` — cliquet-ratchet-pricing:21
- `$$P_{\text{rich}} = \frac{4 P_{\text{fine}} - P_{\text{coarse}}}{3}$$` — american-option-fd-new:76
- `$$P^{(t)}_{ij} = \frac{C^{(t)}_{ij}}{\sum_{k} C^{(t)}_{ik}}$$` — credit-migration-matrix:102
- `$$\text{GA}(\alpha) = \frac{1}{2} \cdot \text{HHI}_{EL} \cdot \frac{C''(\alpha)}{C'(\alpha)}$$` — credit-portfolio-var-cvar:157

Authoring weight: **strong**. TeX-formatted formulas are unambiguously authoritative. Heaviest users: `hull-white-swaption` (122 backslash macros), `credit-portfolio-var-cvar` (113), `stochvol-implied-surface-new` (89).

### Pattern 5 — Library kwarg pin (24 tasks)

Form: a specific scipy / numpy / pandas / statsmodels / sklearn call with named keyword arguments, OR bare kwarg=value expressions in prose.

Concrete examples:
- `np.quantile(x, q, method='lower')` — evt-pot-var:3
- `np.linalg.lstsq(X, y, rcond=None)` — fama-french-factor-model-new:57
- `np.percentile(portfolio_returns, 5, method='linear')` — historical-var-data-prep:35
- `ddof=1` — alpha-hedge-strategy, bl-regime-hmm, bollinger-backtest-aapl, cliquet-ratchet-pricing, cross-sectional-momentum, … (10+ tasks)
- `kind='stable'` — cross-sectional-momentum (D1.g engineering pin)
- `floc=0` — evt-pot-var (POT location pinned to zero)

Authoring weight: **very strong**. When the spec literally writes the function call with kwargs, the agent has no interpretation latitude.

Concrete miss in the original v3.1: `alpha-hedge-strategy` had `ddof=1` and `r_f = 0` pinned in the spec, yet was originally classified A3.f for the agent's choice of `ddof=0`. The v3.2 pre-check catches this.

### Pattern 6 — Pinned numerical parameter (24 tasks)

Form: prose-form parameter assignments like `m = 3`, `lag = 12`, `ν = 5`, `df = 4`, `tol = 1e-6`, `seed = 42`.

Concrete examples:
- `df = 4` — cir-bond-pricing:30
- `nu = 4` — copula-sampling-rank-correlation:15
- `m = 3` (Bartlett kernel lag) — credit-spread-decomposition:61
- `ν = 5` — var-es-estimation:18
- `N = 1000` (paths) — barone-adesi-whaley:75
- `seed = 12345` — Monte Carlo task seed pins

Authoring weight: **very strong**. This is the most common form for distribution / numerical-method parameters.

### Pattern 7 — Day-count pin (7 tasks; literal slashed form)

Form: `ACT/360`, `ACT/365`, `ACT/365F`, `30/360`, `30E/360`, `ACT/ACT`. Distinguished from the *word* "day count" alone, which is weaker (4 additional tasks have only the word).

Concrete examples:
- `USD accrual uses ACT/360; GBP accrual uses ACT/365F` — mtm-xccy-basis-desk:30
- `ACT/365` — localvol-barrier:186
- 7 hits in swap-curve-bootstrap-ois (USD/EUR/JPY conventions)
- `30/360` — bond-coupon tasks
- 3 hits in fx-forward-cross-rate

Authoring weight: **strong** for the literal slashed form. The currency/instrument-specific pin is so precise that any deviation is a clear spec violation.

Concrete miss in the original v3.1: `mtm-xccy-basis-desk` was originally A3.f for the agent using ACT/365 on USD swaps. The literal `ACT/360` pin in the spec was missed.

### Pattern 9 — Schema-key list in prose (added v3.2.2-pat9; ~30+ tasks affected)

Form: instruction enumerates required output keys / columns inline using language like *"must contain (exactly) these keys: X, Y, Z"*, *"must be an object with scalar values for ..."*, *"Columns: 1. ticker 2. name ..."*, *"Write a JSON object with exactly these top-level keys: ..."*. The spec authors the **schema/output layer** even when it doesn't author the formula layer.

Concrete examples:
- `etf-overlap-redemption-pressure:196`: *"Write a JSON object with exactly these top-level keys: 1. `as_of_date` 2. `funds` 3. `top30_counts` 4. `universe_size` 5. `overlap_name_count` ..."*
- `etf-overlap-redemption-pressure:207`: *"`fund_bridge_extremes` must be a flat object with scalar scenario/ticker values for exactly these keys: `largest_redeemed_nav_dollars_scenario`, `largest_redeemed_nav_dollars_ticker`, `highest_redeemed_as_pct_exchange_volume_scenario`, ..."*
- `etf-overlap-redemption-pressure:6`: *"Missing fund-specific exposures should be represented as **zero** for shares, weights, and dollars, and **blank or null** for unavailable fund-implied prices."* — explicit null/zero distinction by field type.
- Most task instructions with CSV outputs include a numbered **`Columns:`** list pinning column names and order.
- `13f-amendment-aware-crowding`: explicit JSON output schema with numbered fields.
- `corporate-action-adjustment`: explicit summary key list.

Authoring weight: **strong** (on the schema/output layer; doesn't pin the formula layer).

**Empirical motivation for adding this pattern.** Without pattern #9, tasks like `etf-overlap-redemption-pressure` were classified as `silent` regime by the regex scanner (no author-year, no inline TeX, no kwargs, no day-counts, no pseudocode fences, only one eponym and that's "ETF"). When agent fails to emit explicitly-pinned schema keys (e.g., `top_ticker_by_dollars` missing → KeyError), the silent-regime classifier routed to `D1.a / task_side`. But the spec **explicitly listed these keys**! The correct routing is `D1.a / agent_conceptual` (failure to follow spec-pinned schema). Pattern #9 closes this gap.

**Routing implication.** When pattern #9 fires, schema/output failures (D1.a vocabulary, D1.d type-serialization, D1.f date-format, D1.b shape) route to `agent_conceptual`, NOT `task_side`. The spec authored the schema; failure to comply is a knowledge gap.

**False-positive guard.** Pattern #9 fires on prose lists, not on column names appearing in passing references. The trigger requires either (a) numbered list with ≥3 items following `Columns:` or `keys:`, OR (b) prose enumeration like *"must contain X, Y, Z"* / *"with values for X, Y, Z"*. Decorative use of column names (e.g., *"the `date` column is the formation date"*) doesn't fire pattern #9.

### Pattern 8 — Pseudocode-fence formula (16 tasks; STRONGEST form)

Form: Markdown ` ``` ` fences with assignments, summations, math operators (`Σ`, `×`, `√`, `**`), or function calls like `N(d1)`, `max(...)`, `sqrt(...)`, `exp(...)`.

Concrete examples:
- `interest-rate-cap-floor` — full Black caplet formula in fence:
  ```
  d1_i = (ln(f_i / K) + 0.5 × vol² × T_i) / (vol × sqrt(T_i))
  d2_i = d1_i - vol × sqrt(T_i)
  caplet_i = notional × period_length × df_i × (f_i × N(d1_i) - K × N(d2_i))
  ```
- `zero-coupon-bootstrapping` — bootstrapping recursion:
  ```
  df(T_n) = (1 - (c_n/freq) × Σ_{k=1}^{n×freq-1} df(t_k)) / (1 + c_n/freq)
  z(T) = -ln(df(T)) / T
  ```
- `earnings-surprise-calculator` — surprise metric:
  ```
  SUE = (actual_eps - consensus_estimate) / std_estimate
  ```
- `corporate-action-adjustment` — adjustment factor (in single-backtick prose, weaker variant):
  `adj_factor = (close_on_ex_date - dividend) / close_on_ex_date`

Authoring weight: **strongest of all eight forms**. Pseudocode fences leave the smallest possible interpretation surface — the agent only needs to translate to Python. Any deviation is unambiguously `agent_conceptual`.

Concrete miss in the original v3.1: tasks like `interest-rate-cap-floor` and `zero-coupon-bootstrapping` look "silent" by the v3.1 pre-check (no eponym, no author cite, no TeX) — but they are in fact **the most prescriptive of all spec types**. Treating their failures as `task_side` is the worst kind of misclassification.

## Auxiliary signal — eponymous method by name (50 tasks)

Form: a named method or person without an accompanying formula or paper cite. Triggers `spec-delegates` regime — the spec is delegating to industry-standard interpretation of the named method.

Top eponyms found in V11 specs (case-insensitive count across all 85 tasks):
- Black-Scholes (12), Crank-Nicolson (8), Newey-West (7), Vasicek (6), GARCH-family (15 across DCC/EGARCH/GJR), Sharpe (12), Brinson (4), Fama-French (5), Hull-White (5), Heston (3), Margrabe (3), Kirk (3), Geske (3), Levy-Curran (2), Dupire (4), Bollinger (4), CIR (5), Merton-jump (4), Bipower / BNS (3), Christoffersen (2), Kupiec (2), CAPM (5), Carhart (3), CreditMetrics (2), CreditRisk+ (2), Vasicek ASRF / Gordy (3), Nelson-Siegel (3), Diebold-Li (1), HAR-RV (2), Smith (2), Cornish-Fisher (3), Garman-Klass / Yang-Zhang / Parkinson / Rogers-Satchell (cluster of 8 in OHLC vol task), Bachelier (1), Jamshidian (1), LMM/HJM/BGM (cluster of 3), Bates (2), Acerbi-Tasche (2), Christensen-Diebold-Rudebusch (1), Schmukler (1).

For each, the **Industry-Standard pre-check** must run: if a clear default exists (e.g., NW1987 lag for Newey-West, π/2 for bipower variation, ddof=1 for sample std, ×√252 for trading-day annualization), the agent should use it; deviation → A3.f `agent_conceptual`. Only when no industry default exists does `task_side` become defensible.

## Per-task regime table (V11 focus list, 85 tasks)

| Regime | Tasks |
|---|---|
| **spec-authored** (56) | alpha-hedge-strategy, american-option-fd-new, asian-option-levy-curran, barone-adesi-whaley, bl-regime-hmm, brinson-sector-attribution, bs-greeks-pde, cir-bond-pricing, cliquet-ratchet-pricing, cme-hdd-option-pricing, copula-sampling-rank-correlation, credit-migration-matrix, credit-portfolio-var-cvar, credit-spread-decomposition, creditmetrics-portfolio-var, cross-sectional-momentum, crypto-funding-rate-basis-carry, earnings-surprise-calculator, etf-cross-asset-lead-lag, evt-pot-var, fama-french-factor-model-new, fft-compound-poisson, fomc-tone-event-study, fx-forward-cross-rate, geometric-mean-reverting-jd, historical-var-data-prep, hull-white-swaption, implied-vol-approximations, interest-rate-cap-floor, ipca-latent-factors, kelly-var-sizing, localvol-barrier, lookback-options, mc-greek-surface-1, merton-jump-diffusion, mtm-xccy-basis-desk, multimodal-alpha-fusion-edgar-cot-gdelt, option-put-call-parity-forward-audit, ou-jump-commodity, pairs-cointegration-kalman, pca-factor-portfolio, prediction-markets-cross-venue-dislocation, quantamental-earnings-jumpfilter-committee, realized-vol-estimators, regime-riskparity-cvar, sec-8k-event-alpha, sentiment-factor-alpha, spread-option-kirk-margrabe, standard-var-methods, stochvol-implied-surface-new, swap-curve-bootstrap-ois, var-es-estimation, variance-swap-replication, yield-curve-bond-immunization, yield-curve-pca-dynamics, zero-coupon-bootstrapping |
| **spec-delegates** (23) | 13f-amendment-aware-crowding, barrier-garch-var, binance-btc-participation-tca, bollinger-backtest-aapl, compound-option-geske, copula-equity-fitting, cta-basel-capital, dcc-garch-portfolio-var, delta-hedging-pnl-simulation, digital-barrier-options, dupire-local-vol, etf-overlap-redemption-pressure, event-study-earnings, ewma-portfolio-risk-decomposition, first-passage-time, form4-cross-sectional-sale-pressure, fx-carry-forward-hedge, intraday-volume-fitting-and-execution-scheduling, ohlc-realized-vol-estimators, regime-cta-vol-target, smith-tail-index, structured-note-risk, yield-curve-bootstrap-immunization |
| **silent** (6) | corporate-action-adjustment (inline single-backtick formulas, weaker form of pattern 8), lob-pc-signal (NLP-flavored prose), momentum-backtest, polars-api-migration (refactor task), sec-10k-report-long (information extraction), sma-crossover-spy |

Note: `corporate-action-adjustment`, `momentum-backtest`, `sma-crossover-spy` actually contain formulas in single-backtick prose (`adj_factor = (close_on_ex_date - dividend) / close_on_ex_date`), which is a *weaker* form of pattern 8 not yet caught by the regex. A future v3.3 could promote these to spec-authored by detecting single-backtick math expressions.

## Implications for v3.2 classification

When judging a failure on a task in this catalog:

1. **spec-authored tasks (56)** — failures are almost always `agent_conceptual` (didn't follow spec) or `agent_coding` (typo in implementing pinned formula). `task_side` is essentially excluded unless the spec contradicts itself or the oracle is buggy.

2. **spec-delegates tasks (23)** — apply Industry-Standard pre-check. Most failures are A3.f `agent_conceptual` (picked non-industry-standard variant). True `task_side` only when no industry default exists and the spec offered no guidance.

3. **silent tasks (6)** — these are mostly NLP/refactor tasks where the QF taxonomy doesn't apply directly. For the genuine quant ones (`corporate-action-adjustment`), the inline-backtick formulas should still be respected.

## How the judge uses this

The judge runs the Spec-Citation Extraction Pre-check (in `prompts/system_judge.md`) BEFORE the Authorship pre-check. The pre-check produces a regime label that the Authorship pre-check then dispatches on. This catalog is the empirical evidence that justifies each regime's decision rule, and provides the false-positive traps (month-name dates) and missed forms (cross-file references, pseudocode fences) that earlier versions got wrong.
