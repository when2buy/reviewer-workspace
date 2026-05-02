# Failure Mode: Time / Date / Calendar Convention (B3)

*Empirical source: PR #41 interest-rate-cap-floor (fixing-time convention); PR #79 execution-is-vwap (bar timestamp meaning); PR #119 option-put-call-parity (fractional-second ACT/365 vs integer-day τ); PR #128 etf-cross-asset-lead-lag (date_range start/end semantics); PR #150 earnings-news-event-alpha (timezone handling); PR #84 cme-hdd-option-pricing (loop ordering pre vs post update); PR #88 event-study-earnings (inclusive vs exclusive index slicing); PR #135 prediction-markets (first-row prior in differenced series); PR #38 zero-coupon-bootstrapping (forward rate interval gap); PR #66 portfolio-risk-attribution (simple vs compound rate conversion); PR #65 bond-portfolio-analytics (EOM coupon date anchoring).*

## Framing

Day-count, compounding basis, annualization factor, business-day handling, timestamp meaning, timezone, fractional-time, fixing-time, loop-ordering in recursive computations, and inclusive-vs-exclusive interval boundaries. The math operates on the wrong "clock."

## Decision Procedure

1. Identify any time/calendar convention referenced (or implicit) in the instruction. Common implicit conventions:
   - day-count for accrued interest and discounting
   - annualization factor for vol
   - bar timestamp (start vs end)
   - timezone for timestamped events
   - date-range semantics (price date vs return date)
   - inclusive vs exclusive bounds in window definitions
   - pre- vs post-update state in recursive computations
2. Check the agent's code for:
   - day-count basis (`/360` vs `/365` vs `/365.25`)
   - annualization factor (×252, ×365, ×250, ×√252)
   - period boundary handling
   - loop indexing (`for i in range(n)` with `x[i]` or `x[i+1]`)
   - `tz_convert` calls or absence
3. If the agent's choice differs from the test's pinned convention, match.
4. **B3 vs B1**: B1 is unit/scale on numbers; B3 is convention on time.
5. **B3 vs A3**: A3 is metric definition (Sharpe excess vs raw); B3 is calendar/clock convention.

## Exclusions

- Pure scale (B1).
- Off-by-one in array indexing that isn't about a *time* convention (that's a code bug, not a finance convention error).
- Wrong formula entirely (A1/A2).

## Sub-rubrics

- **B3.a — Day-count basis.** ACT/360 (USD money market) vs ACT/365 (GBP) vs 30/360 (US corporate) vs ACT/ACT (US Treasuries). Mixing produces wrong accrued interest and yield.
- **B3.b — Compounding & rate conversion.** Continuous (`exp(−rT)`) vs simple (`1/(1+rT)`) vs semi-annual. Annual-to-monthly: simple `r_annual/12` vs compound `(1+r_annual)^(1/12)−1`.
- **B3.c — Annualization factor.** Daily vol × √252 vs ×√365 vs ×√250. Sharpe daily-to-annual scaled by √252 vs other.
- **B3.d — Bar timestamp meaning / fixing-time.** "1-min bar at 10:03" = trades 10:03–10:04 (bar-start) or 10:02–10:03 (bar-end). Both conventions appear in real data (TRTH/Refinitiv mixes them). Cap fixing-time conventions: morning fixing vs end-of-day. Six instruction passages may depend on this in a single backtest.
- **B3.e — Timezone handling.** `tz_convert("America/New_York")` vs raw offset. Reference omits tz_convert and treats raw `−04:00` as if it were local; agent does the financially correct conversion. (Often a *task* bug, but the agent failure label is still B3.)
- **B3.f — Date-range semantics.** `date_range.start` = first *price* date vs first *return* date (one day later, since returns need a prior price). Fractional time-to-expiry: `(expiry − quote).days` (integer days) vs `total_seconds / (365·86400)` (fractional, includes intraday).
- **B3.g — Loop ordering / pre- vs post-update state.** Recursively defined process `x_0 = 0 → x_{t+1}`. Day-1 cost uses `x_0` (pre-update) or `x_1` (post-update)? Same for HDD aggregation, daily P&L: `daily_pnl[0] = equity_0 − capital_base` vs `0`. Same for dividend adjustment factor using already-adjusted close (correct backward) vs raw close. Same for `next_cpn` vs `maturity` anchoring in EOM bond coupon date schedules (forward from next_cpn produces May 30; backward from maturity produces May 31).
- **B3.h — Inclusive vs exclusive index slicing.** "120 trading days ending day −11" with Python slice `[event_idx−130, event_idx−10)` is end-exclusive → 119 days, not 120. "1-year forward T−1 to T" with maturity gaps > 1y silently divides by `(T − T_prev)` instead of 1.

## Single-shot applicability

Applies fully to `solution_kind == finance-zero`. Judge generated code's calendar handling vs spec.

## QF-Bench finance examples

POSITIVE — VWAP execution: instruction says "the bar at or just before the arrival timestamp." Agent picks bar-end convention (timestamp marks trades 10:02–10:03), so the "10:03 arrival" picks the wrong bar. Kyle's λ off by 30%, three downstream tests fail (cascade). Match B3.d.

POSITIVE — Cap-floor pricing: ACT/365 fractional time-to-expiry computed via `total_seconds/(365·86400)`. Agent uses integer-day `(expiry − quote).days / 365`. For a 30-day cap with morning fixing, the difference is meaningful. Match B3.a / B3.f.

POSITIVE — Event-study estimation window: instruction says "120 trading days ending day −11 inclusive." Agent uses Python slice `[event_idx−130, event_idx−11)` (Python end-exclusive) → only 119 observations in window. Estimation OLS coefficients shifted slightly; cascades through abnormal-return computations. Match B3.h.

NEGATIVE — Test expects accrued interest = $1.234 on a 30/360 bond, agent returns $1.234 to 4 decimals. No convention mismatch.

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
