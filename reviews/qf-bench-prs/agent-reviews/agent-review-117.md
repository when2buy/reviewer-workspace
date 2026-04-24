# Review: PR #117 - credit-portfolio-var-cvar
PR: [https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/117](https://github.com/QF-Bench/QuantitativeFinance-Bench/pull/117)
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Build a Monte Carlo credit portfolio model with Gaussian and Student-t copulas, wrong-way risk, Euler marginal CVaR allocation, Vasicek analytical benchmarks, Gordy granularity adjustment, and sector risk decomposition. Produces 9 output files.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `solution/solve.py`
- Checked: copula implementation, Euler decomposition, Gordy adjustment, Vasicek formula, verifier invariants, reference value windows

### Scorecard
- Task contract: 4/5 — very comprehensive but extremely long instruction
- Verifier robustness: 5/5 — brilliant mix of structural invariants + reference value windows (±10%)
- Difficulty calibration: 2/5 — H:0.0, O:1.0, S:0.0 is concerning for a "hard" task
- Financial correctness: 5/5 — solution covers Gaussian/t copulas, Vasicek, Gordy correctly
- Benchmark integrity: 4/5 — invariant-based tests don't leak answers; reference windows are wide enough

### Findings

#### [CRITICAL] H:0.0, O:1.0, S:0.0 — extreme discrimination but only Opus passes
This is a massive task (9 output files, ~100+ tests). The all-or-nothing verifier means S:0.0 despite the task being "hard." This pattern suggests the task is testing Opus-level capability specifically, which may not be useful for benchmarking if only one model tier can solve it.

However, looking at the verifier more carefully — it's NOT all-or-nothing per se. The `test.sh` uses `if [ $? -eq 0 ]; then echo 1; else echo 0`. So one failed test → reward 0. Given ~100 tests spanning 9 output files, this is extremely harsh.

#### [MAJOR] Task scope is too large for a single benchmark item
File: [`instruction.md`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/c8429bc/tasks/credit-portfolio-var-cvar/instruction.md)
The task requires: Gaussian copula MC, Student-t copula MC, wrong-way risk simulation, Euler CVaR decomposition, Vasicek analytical VaR, Gordy granularity adjustment, concentration risk metrics, sector risk decomposition. This is essentially 4-5 separate tasks bundled into one. Any single error in any component cascades to total failure.

**Recommendation**: Consider splitting into smaller, independently scorable tasks or implementing partial credit.

#### [MAJOR] Verifier has reference value windows in TestReferenceValueWindows
File: [`tests/test_outputs.py`](https://github.com/QF-Bench/QuantitativeFinance-Bench/blob/c8429bc/tasks/credit-portfolio-var-cvar/tests/test_outputs.py)
The `TestReferenceValueWindows` class pins specific dollar values (e.g., Gaussian VaR 99% ≈ $411.9M) with ±10% tolerance. These are seeded MC results. If the agent uses a different RNG implementation or different numpy version, these could shift. The seed-based reproducibility depends on exact `numpy.random.default_rng` behavior.

#### [POSITIVE] Invariant-based tests are excellent
The structural/invariant tests (CVaR ≥ VaR, monotonicity, t-copula heavier tails, Euler sum = total) are robust and don't leak answers. This is excellent verifier design.

#### [MINOR] Student-t copula implementation requires shared chi-squared mixing
The instruction says "Both the systematic and idiosyncratic components must share a common mixing variable." This is the critical implementation detail that separates correct from incorrect t-copula implementations. Well-specified.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 1827s | 1,698,710in / 26,246out |
| Opus 4.6 | 1.0 | 191s | 295,948in / 9,706out |
| Sonnet 4.5 | 0.0 | 562s | 1,743,440in / 30,337out |


**Haiku key failures:**
```
E       AssertionError: Student-t VaR at 99.9% (494464565.29) must be strictly > Gaussian (732854485.81) due to tail dependence
E       assert np.float64(494464565.29) > np.float64(732854485.81)
E       AssertionError: Expected 6 rows, got 3
E       assert 3 == 6
E       AssertionError: assert ['wrong_way'] == ['base', 'wrong_way']
E
E         At index 0 diff: 'wrong_way' != 'base'
E         Right contains one more item: 'wrong_way'
```


**Sonnet key failures:**
```
E               AssertionError: GA is 5.34% of Vasicek VaR — too large for ~990 obligors at 0.95
E               assert np.float64(5.343832957974839) < 5.0
E       AssertionError: Wrong-way VaR 99% = 550034443.77, expected ~466912940.18 (±10.0%)
E       assert False
E        +  where False = <function TestReferenceValueWindows._within at 0x7f98795200e0>(550034443.77, 466912940.18, 0.1)
E        +    where <function TestReferenceValueWindows._within at 0x7f98795200e0> = <test_outputs.TestReferenceValueWindows object at 0x7f987953edd0>._within
E        +    and   0.1 = <test_outputs.TestReferenceValueWindows object at 0x7f987953edd0>.TOL
E       AssertionError: Wrong-way CVaR 99% = 734830229.57, expected ~642078023.85 (±10.0%)
```

### Summary
Ambitious and financially correct credit risk benchmark. The verifier design is impressive — invariant tests + reference windows is the right approach. However, the task is too large for a single all-or-nothing item. The H:0.0/O:1.0/S:0.0 pattern suggests only Opus can handle this scope, and the all-or-nothing scoring is too punitive for a 9-file, 100-test task.

### Verdict
**需要 Human Review**

The task is financially correct and well-designed, but needs either (a) partial credit scoring or (b) splitting into smaller tasks. The S:0.0 result with all-or-nothing verifier on such a large scope is likely a calibration issue, not a quality issue.
