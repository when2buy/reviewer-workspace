# Failure Mode: Data Fabrication / Wrong Source (C1)

*Empirical source: PR #97 factor-momentum-spanning (Ken French preamble parsing); PR #88 event-study-earnings (dropna granularity); PR #86 dcc-garch-portfolio-var (dropna only checks first ticker); PR #80 credit-migration-matrix (CEREP withdrawals/defaults distinction); finance-zero single-shot trial pattern (synthesizing returns instead of loading CSV).*

## Framing

The agent's math and conventions are right, but it's operating on the wrong inputs. Either the agent fabricated data (synthesized via `np.random` instead of loading the prescribed CSV), used the wrong file/column/frequency, introduced look-ahead by using future data in a backward-looking signal, silently corrupted the panel via over-aggressive `dropna`, or failed on parsing because of non-standard file headers (Ken French preamble, FRED metadata footer).

This mode is the QF-Bench analog of MAST §1 "data fabrication" — but here the diagnostic is *did the agent rely on the fabricated data to satisfy a deliverable*, not just *did it call np.random*.

## Decision Procedure

1. Identify the prescribed input source(s) in the instruction. Path, file, column, frequency, time range.
2. Check what the agent's code actually reads. Look for:
   - `np.random.*` / `pd.DataFrame(...)` calls used as inputs (not just for synthetic test fixtures inside utility functions)
   - `yfinance.download()` or other external API calls (when the spec says use the local CSV)
   - hard-coded constants used in place of computed quantities (e.g., `sigma = 0.20` instead of computing σ from log-returns)
   - wrong column reads (`open` instead of `close`)
   - wrong frequency (daily when monthly was asked)
3. **Reliance test**: count only if the fabricated/wrong-source artifact is *used* to satisfy a requirement, pass a check, or serve as a deliverable. A throwaway synthetic dataset for one-off plotting doesn't match.
4. Look-ahead: agent uses information at time `t+k` in a signal claimed to be available at time `t`.
5. **C1 vs A3**: A3 is *interpretation* of a correctly-loaded input (σ_k = std vs CV); C1 is *origin* of the input (loaded vs fabricated).
6. **C1 vs C2**: C1 is bad data; C2 is bad numerical solver. Agent that loads correct data and gets a local-optimum is C2.

## Exclusions

- Right source, wrong analysis (A1/A2/A3).
- Right inputs, wrong solver (C2).
- Schema/format gaps where the spec is silent on a non-numerical detail (task design issue, not C1).

## Sub-rubrics

- **C1.a — Synthesized data substituted for prescribed source.** `np.random.normal(0, 0.01, 2520)` instead of `pd.read_csv("/app/data/returns.csv")`. Hard-coded `sigma = 0.20` instead of computing σ from log-returns of the provided file. Common in finance-zero single-shot generation when the agent assumes the file is unreadable; particularly visible when the agent's intermediate result is suspiciously round.
- **C1.b — Wrong source / file / column.** `yfinance.download()` instead of the provided CSV. `open` column instead of `close`. Daily frequency when monthly was asked. Adjusted vs raw close confusion that's about the *column read*, not the adjustment math.
- **C1.c — Look-ahead / future information leak.** Signal at time `t` uses `t+1` data. Computing rolling vol with same-day inclusion when "as-of `t`" is required.
- **C1.d — Multi-line preamble / non-standard CSV header.** Real-world data files (Ken French factors, FRED, Bloomberg) often have copyright preambles, end-of-file footers, mixed delimiters. Agent applies naive `pd.read_csv` / `pd.to_datetime(format='%Y%m%d')` and crashes (or silently corrupts row 0). The fix is `header=N`, `skiprows=`, `skipfooter=`, `engine='python'`. Symptom: cryptic `ValueError: time data "Copyright 2026 ..."`.
- **C1.e — Dropna granularity.** `dropna()` without `subset=` removes rows where *any* column has NaN — one ticker's gap removes others' valid data, inflating the missing-value count. `dropna(subset=[tickers[0]])` only checks the first ticker — silently passes NaNs through to OLS, giving NaN coefficients. The fix is `dropna(subset=[f"ret_{t}" for t in tickers])`.
- **C1.f — Data interpretation that drops information.** CEREP credit transition data: defaults are sometimes recorded under the "Withdrawals" column (when the issuer's rating was withdrawn before defaulting). Naïve reading of the "Default" column alone undercounts defaults — CCC→Default rate ~3% vs corrected ~31%. Real-world reference data interpretation matters.

## Single-shot applicability

Especially relevant for `solution_kind == finance-zero`: single-shot generated code is the most common venue for data fabrication, since the agent doesn't have the chance to discover the actual file format and may fall back to synthetic inputs.

## QF-Bench finance examples

POSITIVE — Task: "Compute σ_hist from `/app/spy_daily.csv` log-returns and use it to calibrate CEV α." Agent's code: `np.random.seed(0); returns = np.random.normal(loc=0.0, scale=0.01, size=2520); sigma = std(returns) * sqrt(252)`. The fabricated returns are *used* to set σ. The eventual α calibration relies on the fabricated σ. Match C1.a.

POSITIVE — Ken French factor task: agent code calls `pd.read_csv(url, ...)` then `pd.to_datetime(df["date"], format="%Y%m%d")`. Crashes with `ValueError: time data "Copyright 2026 Eugene F. Fama and Kenneth R. French" doesn't match format`. The 5-line text preamble was never stripped (`skiprows=5` would fix). All 25 fixture tests cascade-error. Match C1.d.

POSITIVE — Multi-stock event study: agent's `dropna()` removes a row whenever *any* of 8 stocks has a missing return. NVDA's IPO date was 1999, agent's panel starts 1995 → 4 years of NVDA NaN drops 4 years of data for ALL stocks. Estimation windows shrink, OLS coefficients shift. Match C1.e.

NEGATIVE — Agent loads the right CSV, picks the right column, computes σ_hist correctly, but uses it in a wrong-model price (Black-Scholes when CEV mandated). That's A1, not C1.

NEGATIVE — Agent loads the right data, runs a correct GARCH fit, and the optimizer lands at a local optimum because the spec didn't pin starting values. That's C2, not C1.

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
