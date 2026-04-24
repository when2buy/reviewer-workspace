# Review: PR #103 - fx-carry-forward-hedge
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/103](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/103)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Build a G10 FX carry strategy with dealer-style mechanics: CIP forwards, settlement dates, NDF basis, carry signals, forward hedge overlay, FX smile reconstruction, Garman-Kohlhagen pricing, and strategy risk metrics. Five-part task (A–E).

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `tests/test.sh`, `environment/Dockerfile`
- Checked trial results: H45=0.0, Opus46=0.0, S45=0.0
- Analyzed Opus46 test stdout (31 passed, 5 failed)

### Scorecard
- Task contract / instruction: 3/5 — extremely detailed but some ambiguities in convention-sensitive areas
- Verifier robustness: 3/5 — tight tolerances on convention-sensitive calculations
- Difficulty calibration: 2/5 — all models score 0.0 despite passing 31/36 tests
- Model discrimination: 1/5 — no separation at all
- Benchmark integrity: 4/5 — convention-sensitive, hard to cheat
- Data realism: 5/5 — real FX data, realistic dealer mechanics

### Findings

#### [CRITICAL] All-or-nothing scoring destroys signal from near-passes
Opus46 passes 31/36 tests (86%) but scores 0.0. The 5 failures are:
1. `test_broken_date_case` — broken-date forward calculation
2. `test_roll_cases_use_far_leg_rule` — swap point side selection
3. `test_carry_signals_shape_and_columns` — carry signal shape
4. `test_forward_hedged_equals_unhedged_plus_overlay` — NaN handling in return identity (atol=1e-12 with NaN)
5. `test_required_keys_and_observations` — n_obs off by 1 (1995 vs 1996)

The NaN + atol=1e-12 identity check and the n_obs off-by-one are verifier brittleness issues, not fundamental quant errors. The task should use partial credit.

#### [MAJOR] Task scope is enormous — 5 parts covering all of FX quant
File: [`instruction.md`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/763d3fb/tasks/fx-carry-forward-hedge/instruction.md)

This is effectively 5 separate tasks bundled into one. Each part (cross rates, forwards, carry signals, option pricing, risk metrics) is a full task in itself. The hard rating with 120 min expert estimate seems low — this would take an expert much longer.

#### [MAJOR] n_obs off-by-one suggests ambiguous row counting convention
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/763d3fb/tasks/fx-carry-forward-hedge/tests/test_outputs.py) line 279

The test asserts `self.data[strategy]["n_obs"] == len(self.returns)` but the carry returns DataFrame has 1996 rows while the agent reports 1995. This is likely an edge case around whether the first NaN row counts as an observation. The instruction doesn't clarify this.

#### [MAJOR] NaN-sensitive identity check at 1e-12 tolerance
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/763d3fb/tasks/fx-carry-forward-hedge/tests/test_outputs.py) line 163

`np.allclose(lhs, rhs, atol=1e-12)` fails because NaN ≠ NaN. The test should use `np.testing.assert_allclose` with `equal_nan=True` or mask NaN rows.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 487s | 4,673,762in / 95,845out |
| Opus 4.6 | 0.0 | 504s | 1,774,169in / 25,764out |
| Sonnet 4.5 | 0.0 | 461s | 1,157,057in / 28,112out |


**Haiku key failures:**
```
E       KeyError: 't_base'
E       KeyError: 'side_used'
E       assert False
E        +  where False = <function isclose at 0x7fcafed38e30>(3.6978497556700645, 3.6182, atol=0.02)
E        +    where <function isclose at 0x7fcafed38e30> = np.isclose
E       assert False
E        +  where False = <function isclose at 0x7fcafed38e30>(1.3329566263773693, 1.4122, atol=0.02)
E        +    where <function isclose at 0x7fcafed38e30> = np.isclose
```


**Opus key failures:**
```
E       KeyError: 'days_from_spot'
E       KeyError: 'swap_points'
E       assert 2247 < 2100
E       assert False
E        +    where <function allclose at 0x7f502edefef0> = np.allclose
E           assert 1995 == 1996
```

### Summary
Ambitious and convention-sensitive FX task with real data. The quant content is excellent but the task is too large and the verifier has brittleness issues (NaN handling, off-by-one). All models score 0.0 despite Opus46 passing 86% of tests.

### Verdict
**不建议 Merge**

Two blockers: (1) verifier brittleness — NaN identity check and n_obs off-by-one cause failures unrelated to quant correctness; (2) all-or-nothing scoring on a 5-part task yields zero discrimination. Fix verifier issues and add partial credit, or split into smaller tasks.
