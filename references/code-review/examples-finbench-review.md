# Example FinBench Review Template

Demo Review A — REQUEST CHANGES

Task: merton-credit-model
PR: QF-Bench/QuantitativeFinance-Bench#12
Reviewer: Grim 🔍 | Date: 2026-04-01

---

## What This PR Does

This PR adds a new Hard-rated task asking an AI agent to implement the Merton structural credit model, calibrating firm asset value and volatility from equity prices, then computing distance-to-default and credit spreads for a set of companies. The agent receives raw equity data and must produce a structured JSON output with the calibrated parameters and risk metrics.

Review focus: The core risk here is answer leakage and formula correctness. Merton calibration involves an implicit system of equations. If the data or tests expose the answer, the task collapses. The domain math also needs to be airtight since a latent formula bug can be invisible when T=1.

---

## Scorecard

| Dimension | Score | Weight | Weighted |
| --- | ---: | ---: | ---: |
| A. Structural Completeness | 8 / 10 | 20% | 1.6 |
| B. Data Quality & Ground Truth | 4 / 10 | 30% | 1.2 |
| C. Reasoning & Domain Knowledge | 5 / 10 | 30% | 1.5 |
| D. Evaluation Criteria (Test Quality) | 6 / 10 | 20% | 1.2 |
| Total |  |  | 5.5 / 10 |

Threshold: 7.0 → 🔴 REQUEST CHANGES

---

## A. Structural Completeness — 8/10

All 6 required files present. CI passes. Canary GUID in all source files. Oracle: reward = 1. Finance-Zero: reward = 0, difficulty appropriate.

(-2) Dockerfile missing COPY paths for Codex and Goose skill directories. Only Claude path present.

---

## B. Data Quality & Ground Truth — 4/10

Input CSV contains a column named `expected_dd`, the answer is embedded directly in the data. An agent can trivially hard-code the output without computing anything. This invalidates the task entirely as a benchmark item.

Additionally, there is no data provenance in the PR description. Source, date range, and license of `credit_data.csv` are undocumented. The golden answer cannot be independently verified.

Fix: Remove `expected_dd` column. Document data source in PR description. Re-verify oracle output against documented source.

---

## C. Reasoning & Domain Knowledge — 5/10

The DD formula in the oracle divides by `sigma_a` instead of `sigma_a * sqrt(T)`. This is currently masked because all test cases use `T = 1`. It will silently produce wrong answers for any `T != 1` variant.

The instruction also does not specify continuous vs. discrete dividend convention. Two valid implementations can therefore produce different outputs, making the task non-deterministically evaluable.

Fix: Correct the DD formula. Add a `T = 0.5` test case. Specify dividend convention explicitly in `instruction.md`.

---

## D. Evaluation Criteria — 6/10

Only 8 assertions for a Hard-rated task. Missing financial consistency checks: no no-arbitrage bound (`equity > 0`), no monotonicity test (`DD` decreases as leverage increases). These are the checks that catch financially plausible but mathematically wrong answers.

`atol=1e-2` on `credit_spread` is too loose for a basis-point-level metric.

Fix: Add no-arbitrage and monotonicity checks. Tighten spread tolerance to `rtol=0.01`.

---

## Summary

The answer leakage in the input data is a fundamental integrity failure. This alone blocks the PR. The domain formula bug is a close second. Both must be fixed before re-review.

| Priority | Action |
| --- | --- |
| 🔴 Must fix | Remove `expected_dd` from input data |
| 🔴 Must fix | Correct DD formula and add a non-unit-horizon test |
| 🟠 Should fix | Document data provenance and dividend convention |
| 🟠 Should fix | Strengthen financial consistency checks |

## Verdict

REQUEST CHANGES

The benchmark is not review-ready until the leakage issue and formula correctness issue are fixed.
