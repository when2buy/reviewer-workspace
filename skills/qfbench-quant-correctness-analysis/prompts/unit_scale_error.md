# Failure Mode: Unit / Scale Error (B1)

*Empirical source: PR #183 pca-yield-curve (`var_explained` 86.32 vs 0.8632); PR #78 fx-carry-trade-backtest (carry signal 4.8 vs 0.048); PR #106 etf-overlap-redemption-pressure (NaN vs zero sentinel); PR #132 dirty-gap-momentum (profit_factor null vs Infinity vs 0); PR #23 stochvol (NaN replaced by 0 conflicts with `not np.any(arr==0)` test).*

## Framing

The math is right, but the answer is on the wrong scale: percent vs decimal, basis points vs decimal, annualized vs daily, dollars vs notional. The agent's number is off by a clean factor (×100, ×10000, ×252, ×√252) or has the wrong sentinel for an undefined value (NaN where 0 was expected, Infinity where null was expected, 0 where NaN was expected).

This mode is the most easily detected: the **failure ratio** `agent_value / expected_value` will be approximately one of: 100, 0.01, 10000, 0.0001, 252, √252, 365.

## Decision Procedure

1. For each failing test, compute `ratio = agent_value / expected_value` (where expected value is from the test).
2. If the ratio is approximately one of: 100, 0.01, 10000, 0.0001, 252, √252, 365, ½ — the failure is a unit/scale error. Match.
3. Verify by checking the agent's code: does it report the quantity in the wrong unit (e.g., `var_explained = 86.32` instead of `0.8632`)? Does it apply or omit a scaling factor (e.g., `* 100`, `/ 10000`, `* sqrt(252)`)?
4. For sentinel mismatches, check the test's exact assertion: `not np.any(x == 0)` requires no zeros, so substituting NaN with 0 fails; `assert pd.isna(x)` requires NaN, so substituting 0 fails.
5. **B1 vs B2**: scale errors are |ratio| ≠ 1; sign errors are ratio ≈ −1 with same magnitude.
6. **B1 vs B3**: time-conversion conventions (`r/n` vs `(1+r)^(1/n)−1`) live in B3, not B1.

## Exclusions

- Sign issue (B2).
- Compounding/day-count convention (B3).
- Rounding precision differences within tolerance.
- Wrong magnitude due to wrong formula (A2).

## Sub-rubrics

- **B1.a — Percent vs decimal.** `var_explained` stored as 86.32 instead of 0.8632. `carry_signal` as 4.8 instead of 0.048. Returns or rates as percent points instead of decimal fractions.
- **B1.b — Basis points vs decimal.** Yield changes: 5 bps vs 0.0005 (`* 10000` or `/ 10000`). DV01 scaling: dollars vs basis points exposure.
- **B1.c — Annualization factor.** Daily vol × √252 vs × √365 vs unscaled. Daily Sharpe scaled by √252 vs not.
- **B1.d — Sentinel value mismatch.** NaN where the spec expected 0, or vice versa (e.g., NaN for `implied_price` when not held vs zero for `shares_held`). `null` vs `Infinity` for undefined ratios (`profit_factor` when `gross_loss = 0`). NaN replaced by 0 conflicts with `assert not np.any(arr == 0)` test.

- **B1.e — Greeks unit-convention drift across estimators.** *Empirical: 4 trials in the 50-trial validation set (mc-greek-surface family).* Greeks have multiple in-use conventions: vega "per absolute σ unit" (e.g., 36.5 means a 1.0 change in σ moves price by $36.5) vs "per 1% σ change" (0.365 means a 1pp change moves price by $0.365), 100× apart. Same for rho (per absolute r vs per 1bp). The failure shape: the agent computes the same Greek by 2+ methods (FD, pathwise, LR, BS analytical) and the answers land 100× apart from each other within the agent's own output. Test cross-checks (e.g., `assert abs(fd_vega - pw_vega) / max(|fd_vega|, |pw_vega|) < 0.05`) immediately fire. **Diagnostic ratio:** if the agent's `fd_vega ≈ 36.5` and `pw_vega ≈ 0.365`, the discrepancy is 100× → the analytical BS vega in their code probably has `/ 100.0` somewhere while the FD path doesn't. Look for `/ 100.0` or `* 100.0` applied unevenly across the Greek computations. **Distinguish from a chain-rule formula error (A2.a):** if the formulas themselves are mathematically identical and only the unit scaling is inconsistent, this is B1.e. If one estimator is missing the chain-rule term entirely (`dS_T/dσ`), that's A2.a — the units happen to be wrong because the formula is wrong.

## Single-shot applicability

Applies fully to `solution_kind == finance-zero`. Judge generated code's unit handling vs spec.

## QF-Bench finance examples

POSITIVE — PCA yield curve: instruction's output schema for `eigenvalues.csv` includes `var_explained`. Test asserts `np.isclose(var_explained[0], 0.8632, rtol=0.01)`. Agent stores `86.32`. Ratio = 100. Match B1.a.

POSITIVE — FX carry trade: instruction says input rates are "in percent" but doesn't say whether `carry_signals` should be reported in decimal (0.048) or percent (4.8). Reference uses decimal; test pins decimal with `atol=0.002`. Agent reports in percent → exactly 100× off. Match B1.a.

POSITIVE — Profit factor: agent's strategy has zero losing trades. Agent stores `0.0` for `profit_factor`. Spec expects `null` (gross_loss = 0 ⇒ ratio undefined). Agent's `0` is materially wrong (zero profit factor implies all losses). Match B1.d.

POSITIVE — MC Greeks vega convention split (mc-greek-surface): agent's BS-analytical vega returns `S * exp(-q*T) * norm.pdf(d1) * sqrt(T) / 100.0` (per-1% convention, ~0.37). Agent's FD vega computes `(price(σ+h) − price(σ−h)) / (2*h)` with `h = 0.01` and does NOT divide by 100 (per-absolute-σ convention, ~36.5). Agent's pathwise vega divides by 100. The cross-method test `assert abs(fd_vega − bs_vega) / |bs_vega| < 0.05` reports `fd_vega = 36.5, bs_vega = 0.37`, ratio ≈ 100. The formulas themselves (`d1`, `dS_T/dσ`, FD finite difference) are all mathematically right; only the `/ 100.0` is applied in 2 of 3 paths. Match B1.e. (Cross-reference: when `dS_T/dσ` is also wrong inside the pathwise estimator — i.e., the agent multiplies by `1/σ` when they should multiply by something that simplifies to `Z√T` — the formula error is A2.a, NOT B1.e.)

NEGATIVE — Test expects 0.5 for a probability, agent returns 0.5000003. Within numerical tolerance, no match. Probably C2 if outside tolerance, but at this magnitude no match.

NEGATIVE — Test expects 5.10, agent returns 5.05. Difference ~1%, neither a 100× nor a sign issue. Probably C2 (numerical drift) or A2 (missing small term), but not B1.

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
