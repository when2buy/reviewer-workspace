# Review: PR #78 - fx-carry-trade-backtest
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/78](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/78)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
G7 FX carry trade backtest: compute monthly FX log returns with correct quote convention handling, construct carry signals using day-count-adjusted interest rate differentials, build a long/short carry portfolio, and analyze performance with conditional crash risk metrics and carry/spot decomposition.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, Dockerfile
- Checked: trial results for h45, opus46, s45 (all reward=0.0)
- Analyzed: failure patterns across models

### Scorecard
- Task contract / instruction: 4/5
- Verifier robustness: 3/5
- Difficulty calibration: 4/5
- Model discrimination: 4/5
- Benchmark integrity: 4/5

### Findings

#### [MAJOR] `num_months` ambiguity — 167 vs 168
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/f60c5e6/tasks/fx-carry-trade-backtest/tests/test_outputs.py), `test_num_months`

Test expects 167 months but Haiku and Sonnet produce 168. The instruction says data covers "December 2009 through December 2023 (169 month-end observations)" with "The first observation (2009-12) serves as the initial level for computing returns starting January 2010." This gives 168 monthly returns (Jan 2010 – Dec 2023).

The test expects 167, which implies the first month (Jan 2010) should be excluded from the "active period" because positions are zero. The instruction says the first month should have zero positions, but whether that month counts toward `num_months` is ambiguous. The instruction should explicitly state: "Report num_months as the number of months with active (non-zero) positions."

Opus gets 167 correctly, showing this is solvable but ambiguous.

#### [MAJOR] Max drawdown sign/value disagreement for Opus
Opus fails only `test_max_drawdown`. The test expects -0.427337 but Opus gets a different value. The instruction doesn't specify whether max_drawdown is computed from the net (post-TC) or gross returns — this could cause a small difference. Also, max drawdown computation depends on the cumulative return series construction, which is sensitive to whether the initial month (zero return) is included.

#### [MINOR] Carry signal day-count convention is a good discriminator
File: [`instruction.md`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/f60c5e6/tasks/fx-carry-trade-backtest/instruction.md)

The instruction specifies ACT/360 for USD, EUR, CHF, JPY and ACT/365 for GBP, AUD, CAD. This is a genuine real-world convention that tests domain knowledge. Haiku and Sonnet fail `test_carry_signal_values_2011_01`, suggesting they don't handle day count correctly.

#### [MINOR] Position construction is well-tested
The tests check dollar-neutrality, ±0.5 weights, 2 longs and 2 shorts — good verification of the carry trade portfolio construction.

#### [NIT] Carry/spot decomposition tests fail for Haiku
Haiku fails `test_carry_component_positive` and `test_spot_component_negative` — likely because the carry signal computation is wrong (day count issue), which cascades through the decomposition.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| [Haiku 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-h45-fx-carry-trade-backtest) | 0.0 | 187s | 1,820,265in / 30,117out |
| [Opus 4.6](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-opus46-fx-carry-trade-backtest) | 0.0 | 167s | 154,529in / 8,665out |
| [Sonnet 4.5](https://github.com/when2buy/fb-bench-tracker/tree/51a42f1/trials/fb-pr-s45-fx-carry-trade-backtest) | 0.0 | 295s | 1,092,863in / 13,202out |


**Haiku key failures:**
```
FAIL: test_num_months
E       assert 168 == 167
FAIL: test_carry_signal_values_2011_01
E       AssertionError: AUD carry signal incorrect
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f6af0332870>(4.805, 0.048029, atol=0.002)
E        +    where <function isclose at 0x7f6af0332870> = np.isclose
FAIL: test_positions_first_month_zero
```


**Opus key failures:**
```
FAIL: test_max_drawdown
E       assert np.False_
E        +  where np.False_ = <function isclose at 0x7f22cfb2b970>(-0.5086059637, -0.427337, atol=0.03)
E        +    where <function isclose at 0x7f22cfb2b970> = np.isclose
```

### Summary
Good FX carry trade task with genuine domain traps (quote conventions, day count). Opus comes very close (1 failure — max drawdown). The main issue is the num_months ambiguity and possibly a max drawdown edge case.

### Verdict
**需要 Human Review** — Opus at 1 failure shows the task is nearly well-calibrated. Fix the `num_months` specification (explicitly state what counts as an "active month") and investigate the max_drawdown discrepancy. Minor fixes would make this merge-ready.
