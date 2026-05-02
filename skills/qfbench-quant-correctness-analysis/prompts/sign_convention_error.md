# Failure Mode: Sign Convention Error (B2)

*Empirical source: PR #186 pot-gpd-bitcoin (R/ismev k = −ξ vs scipy c = +ξ); PR #72 treasury-curve-pca-butterfly (PCA eigenvector signs); PR #124 pairs-cointegration-kalman (PnL sign on mean-reversion direction); PR #128 etf-cross-asset-lead-lag (lag direction sign); PR #123 ipca-latent-factors (eigenvector indeterminacy); PR #131 garch-vecm (signed vs absolute α[0]).*

## Framing

The magnitude is right but the sign is wrong. Includes loss-vs-P&L convention, ξ vs −ξ in heavy-tail parameters across software ecosystems, long vs short weight signs, lag-direction in lead-lag asymmetry, and eigenvector / factor-rotation sign indeterminacy in PCA.

The signature symptom is `ratio = agent_value / expected_value ≈ −1` across one or more failing tests with same magnitude.

## Decision Procedure

1. For each failing test, compute `ratio = agent_value / expected_value`.
2. If `ratio ≈ −1` (within sign tolerance) across one or more tests, sign convention is the leading hypothesis.
3. Check the agent's code for:
   - drift sign in SDE
   - residual sign convention in MLE objective
   - log-likelihood gradient sign (negate or not)
   - P&L sign convention (long vs short)
   - shape parameter sign for heavy-tail families (especially GPD)
   - lag direction in correlation slicing
   - PCA eigenvector sign-fixing rule
4. For PCA / factor rotations: eigenvectors have inherent sign indeterminacy. The instruction must specify a sign-fixing rule; if not, the agent's sign may flip. The expected value is fixed by the reference's implicit rule.
5. **B2 vs B1**: scale errors are |ratio| ≠ 1; sign errors are ratio ≈ −1 with same magnitude.
6. **B2 vs A1**: sign-flip is B2; entirely wrong model is A1 (e.g., long-call vs short-call payoff is A1, not B2 — different formulas, not just signs).

## Exclusions

- Pure scale (B1).
- Sign error that's actually a different *model* (A1).
- Within-tolerance sign-preserving differences (no match).

## Sub-rubrics

- **B2.a — Shape parameter sign across ecosystems.** GPD shape: scipy `genpareto` uses `c = +ξ` (heavy tail = positive ξ); R's `ismev` package (Coles textbook) uses `k = −ξ` (heavy tail = negative k). Modern EVT (McNeil/Frey/Embrechts) agrees with scipy. Agents trained on R-flavored references can produce sign-flipped fits. Empirically: `scipy.stats.genpareto.fit()` returns c = +0.25 for true ξ = +0.3.
- **B2.b — Loss vs P&L convention.** VaR conventionally positive (loss). Returns conventionally as profit (gain positive). Agent flipping these breaks `VaR > 0` and `ES ≥ VaR` consistency tests.
- **B2.c — Long vs short weight sign.** Short positions: negative weight (long-short notation) or positive exposure with side flag (book-keeping notation)? PnL on short leg in pairs trading: drift signs reversed. PnL sign on mean-reversion direction.
- **B2.d — Lag direction / lead-lag asymmetry.** "If A leads B" means asymmetry > 0 with leader=A. The slice formula `corr(A[0:n−k], B[k:n])` is `corr(A_t, B_{t+k})` (positive k means A leads B). Agents flipping this produce sign-inverted leader/lagger labels.
- **B2.e — Eigenvector / factor rotation sign indeterminacy.** PCA eigenvectors have free signs. PC2 sign-fixing heuristic `if np.sum(vec) < 0: flip` is unstable for PC2 (sum near zero). Without an explicit sign-fixing rule, factors come out sign-flipped, downstream metrics like Sharpe with flipped sign.

## Single-shot applicability

Applies fully to `solution_kind == finance-zero`. Judge generated code's sign conventions vs spec.

## QF-Bench finance examples

POSITIVE — IPCA factor extraction: eigendecomposition leaves eigenvector signs undetermined. Reference uses an implicit anchor (largest-loading positive). Agent uses `if vec[0] < 0: flip`. Factors 1 and 3 come out with opposite signs → Sharpe ratios with flipped signs → tests fail. Match B2.e.

POSITIVE — GPD POT analysis on Bitcoin losses: scipy returns c = +0.30 for the empirical loss tail. Agent (trained on R/ismev examples) negates: stores `xi = -0.30`. The VaR formula `u + (β/ξ)((n/N_u(1−α))^{−ξ}−1)` with wrong ξ sign produces wildly wrong VaR (positive ξ shrinks the tail extension; negative makes it explode). Match B2.a. (Note: in our actual PR #186 review, agent did NOT make this mistake — but the pattern is real and worth flagging.)

POSITIVE — ETF cross-asset lead-lag: agent's correlations are correct in magnitude but every leader/lagger label is flipped. (GLD, LQD) asymmetry: agent reports +0.108, reference −0.108. Agent's slice convention treats "A[t]·B[t+k]" as "A lags B" instead of "A leads B." Match B2.d.

NEGATIVE — Agent's call price is 5.10, oracle's is 5.05. Difference = 0.05 (positive), ratio = 1.0099, neither a sign nor a scale error. Probably tolerance / numerical method drift — investigate elsewhere.

NEGATIVE — Test expects DV01 = +245.6 for a long bond, agent reports +245.6. Same sign, same magnitude. No match.

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
