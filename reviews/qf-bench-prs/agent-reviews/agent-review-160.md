# Review: PR #160 - cliquet-ratchet-pricing
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/160](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/160)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Price cliquet (ratchet) options as portfolios of forward-starting ATM calls under Black-Scholes. Compare to standard European options. Output per-period forward-start details.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked: forward-start option pricing under BS, oracle values, tolerance calibration
- Reviewed: trial results for h45, opus46, s45

### Scorecard
| Dimension | Score |
|-----------|-------|
| Task contract / instruction | 4 |
| Verifier robustness | 2 |
| Difficulty calibration | 3 |
| Model discrimination | 3 |
| Benchmark integrity / anti-cheating | 2 |

### Findings

#### [MAJOR] Hardcoded oracle values with very tight tolerances (atol < 0.01)
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/fc3e45a/tasks/cliquet-ratchet-pricing/tests/test_outputs.py)

ORACLE_CLIQUET_PRICES contains exact prices to 13+ decimal places with tolerance < 0.01. The cliquet pricing formula (sum of forward-start BS calls with dividend yield) has subtle implementation choices: whether discounting is applied per-period or at maturity, whether the forward-start uses `S₀·e^{(r-D)·t_start}` or just S₀, etc. Different valid interpretations could produce prices differing by several percent.

Haiku gets max_cliquet_price ≈ 271.5 vs oracle 281.1 (3.4% off). Sonnet gets ≈ 242.2 (14% off). These could be formula interpretation differences rather than errors.

#### [MAJOR] Full oracle values leaked in test file
ORACLE_CLIQUET_PRICES, ORACLE_CALIBRATION, and ORACLE_SUMMARY are all embedded in the test file with exact values. An agent with test access could hardcode outputs. Under Harbor assumptions tests are hidden, but this is still a best-practice violation.

#### [MINOR] Calibration test has extremely tight tolerances
`test_calibration_values` checks `return_mean`, `return_std`, `annualized_vol` with tolerances down to `1e-10`. This requires exact matching of ddof=1, specific log-return computation, etc. Sonnet fails this — likely using a slightly different computation (e.g., ddof=0 or different precision).

#### [MINOR] Only Opus passes — good discrimination but possibly for wrong reasons
Opus matches the oracle exactly, but Haiku/Sonnet fail on price values rather than structural properties. The failures may reflect that only Opus matches the specific forward-start formula interpretation used by the oracle, not that the others are fundamentally wrong.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 96s | 446,844in / 7,207out |
| Opus 4.6 | 1.0 | 81s | 116,556in / 3,296out |
| Sonnet 4.5 | 0.0 | 137s | 270,480in / 6,964out |


**Haiku key failures:**
```
E           AssertionError: Row 0: cliquet_price mismatch
E           assert 0.9015331390128267 < 0.01
E            +  where 0.9015331390128267 = abs((94.02870817593592 - 94.93024131494874))
E            +    where 94.02870817593592 = float('94.02870817593592')
E       AssertionError: max_cliquet_price mismatch
E       assert 9.583934485641748 < 0.01
E        +  where 9.583934485641748 = abs((271.54430714312116 - 281.1282416287629))
```


**Sonnet key failures:**
```
E       AssertionError: return_skewness mismatch
E       assert 0.0015329059647316567 < 1e-06
E        +  where 0.0015329059647316567 = abs((0.7067546367047516 - 0.7052217307400199))
E           AssertionError: Row 0: cliquet_price mismatch
E           assert 13.130923283017552 < 0.01
E            +  where 13.130923283017552 = abs((81.7993180319312 - 94.93024131494874))
E            +    where 81.7993180319312 = float('81.7993180319312')
E       AssertionError: max_cliquet_price mismatch
```

### Summary
The cliquet pricing concept is good — forward-starting options and their aggregation into cliquets is a practical exotic structure. However, the test design relies too heavily on hardcoded oracle values with tight tolerances. The instruction's ambiguity about the exact forward-start formula (with dividends) combined with tight tolerances means models may fail for having a different but valid interpretation. Oracle leakage in tests is also a concern.

### Verdict
**需要 Human Review**

The task concept is sound and Opus-only discrimination is interesting, but: (1) the tight tolerances on cliquet prices may penalize valid alternative formula interpretations, (2) full oracle values are leaked in tests. A human should verify whether the oracle's forward-start formula is the uniquely correct one, or if there are multiple valid approaches. If the formula is unambiguous, widen tolerances slightly and consider property-based tests.
