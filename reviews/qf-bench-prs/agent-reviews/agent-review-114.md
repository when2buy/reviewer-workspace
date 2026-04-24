# Review: PR #114 - brinson-sector-attribution
Reviewer: Agent 🔍 | Date: 2026-04-23

### What This PR Does
Brinson-Fachler performance attribution for a sector rotation strategy with 11 sectors + cash, quarterly rebalancing with weight drift, alternative ETFs for 3 sectors. Decompose active return into allocation, selection, and interaction effects.

### What I Did to Review This
- Read: `instruction.md`, `task.toml`, `tests/test_outputs.py`, `solution/solve.sh`, `environment/data/params.json`
- Checked: Brinson-Fachler formulas, weight drift logic, cash treatment, verifier coverage

### Scorecard
- Task contract: 4/5 — detailed but some implicit conventions (e.g., "last trading day of prior month" for returns)
- Verifier robustness: 4/5 — good coverage of monthly, quarterly, sector-level values with consistency checks
- Difficulty calibration: 2/5 — H:0.0, O:1.0, S:0.0 is concerning (see below)
- Benchmark integrity: 3/5 — pinned constants in tests, many expected values exposed
- Financial correctness: 4/5 — Brinson-Fachler formulas correct; weight drift implementation correct

### Findings

#### [CRITICAL] S:0.0 despite seemingly straightforward task
File: N/A
Sonnet scores 0.0 while Opus scores 1.0. This is a red flag. Either:
1. The task has hidden ambiguities that only Opus resolves correctly (possible — weight drift between rebalances, monthly return definition, cash treatment)
2. The verifier is brittle in ways that punish minor interpretation differences
3. There's a spec issue

The all-or-nothing verifier means a single test failure → reward 0. With 30+ tests pinned to specific values (e.g., monthly allocation to 5e-5 tolerance), a single convention misunderstanding cascades to total failure. This H:0.0/O:1.0/S:0.0 pattern suggests the task is knife-edge rather than well-calibrated.

#### [MAJOR] Missing canary in task.toml
File: `task.toml`
No canary GUID comment in task.toml, unlike other PRs.

#### [MAJOR] Weight drift convention is implicit
File: `instruction.md`
The instruction says "Between rebalances, weights drift proportionally to each holding's return" and "Always use beginning of month weights for attribution." The exact drift formula is not given — the agent must infer that `w_new[i] = w_old[i] * (1 + R_i) / (1 + R_portfolio)`. This is standard but could trip up models that don't know the convention.

#### [MINOR] Cash treatment could be clearer
Cash earns `annual_rate / 12` but benchmark has 0% cash weight. The instruction specifies cash allocation = `w_cash * (R_cash - R_b)` which is correct, but the interaction between cash and the attribution framework could be stated more explicitly.

#### [MINOR] Real market data (sector ETF prices) — good
File: `environment/data/sector_etfs.csv`
Uses actual 2024 ETF prices, adding realism.

### Summary
The Brinson-Fachler implementation is financially correct and the solution is well-structured. However, the H:0.0/O:1.0/S:0.0 score pattern combined with an all-or-nothing verifier raises calibration concerns. The task has several implicit conventions (weight drift, monthly return anchoring, cash treatment) that create a knife-edge pass/fail boundary. The S:0.0 result needs investigation — is Sonnet failing on a fundamental misunderstanding or a trivial convention mismatch?

### Verdict
**需要 Human Review**

The O:1.0/S:0.0 pattern needs investigation. If Sonnet's failure is due to a spec ambiguity rather than genuine difficulty, the instruction needs tightening. If it's genuine, the all-or-nothing verifier may still be too harsh — consider partial credit.
