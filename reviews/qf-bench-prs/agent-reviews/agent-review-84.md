# Review: PR #84 - cme-hdd-option-pricing
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/84](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/84)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Prices a CME monthly HDD (Heating Degree Day) call option using burn analysis, OU model calibration, Monte Carlo simulation, and Greeks via bump-and-revalue. Input is GHCN-Daily weather data.

### What I Did to Review This
- Read: instruction.md, task.toml, tests/test_outputs.py, tests/test.sh, environment/Dockerfile
- Reviewed trial results for h45 (0.0), opus46 (1.0), s45 (1.0)
- Checked financial formulas, tolerance calibration, anti-cheat posture

### Scorecard
- Task contract / instruction: 5/5 — Exceptionally detailed, specifies OU fitting method, MC seeding, Greek bump sizes
- Verifier robustness: 4/5 — Good pinned values with reasonable tolerances; MC price has ±15 atol which is appropriate
- Difficulty calibration: 4/5 — Medium is fair; H45 fails, O46/S45 pass. Discriminates weak from strong
- Benchmark integrity: 4/5 — Tests pin specific values but derive from real weather data + specified seed
- Data realism: 5/5 — Real GHCN-Daily data, proper domain conventions (F→C conversion, CME tick value)

### Findings

#### [MINOR] No solution/solve.py present
File: [`solution/`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/b2e52a0/tasks/cme-hdd-option-pricing/solution/)
No oracle solution script is provided. This makes it harder to verify the oracle values independently, though the tests contain well-motivated pinned values.

#### [NIT] Tolerance on OU parameters is generous
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/b2e52a0/tasks/cme-hdd-option-pricing/tests/test_outputs.py)
`ou_kappa` and `ou_sigma` have ±5.0 atol on values ~72-73 (~7% tolerance). This is reasonable given fitting sensitivity but could allow slightly wrong implementations to pass.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 127s | 644,672in / 10,522out |
| Opus 4.6 | 1.0 | 106s | 189,963in / 5,625out |
| Sonnet 4.5 | 1.0 | 165s | 171,985in / 7,672out |


**Haiku key failures:**
```
FAIL: test_greeks_json_exists_and_valid
E       AssertionError: bump_sigma_pct=1.0, expected 0.01
E       assert 1.0 == 0.01
```

### Summary
Well-designed weather derivatives task with strong domain specificity (GHCN data format, OU process, CME conventions). The instruction is thorough and prescriptive where needed. Trial results show good model discrimination: Haiku fails while Opus and Sonnet pass. No significant blockers.

### Verdict
**建议 Merge**

Correct, well-calibrated, with real data and good model discrimination.
