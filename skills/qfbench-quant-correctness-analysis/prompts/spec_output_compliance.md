# D1. Output Schema & Spec Compliance

## Framing

The agent's *quantitative content* is correct (or off-axis), but the *output format / schema / vocabulary* doesn't match what the verifier expects. The failure is on the way out (formatting / labeling / shape), not on the way in (math).

Class D fires on a **separate axis** from A/B/C. A trial can match D1 *and* any A/B/C mode at the same time. The cascade rule operates *within* an axis, not across them — D1 never subsumes A/B/C and is never subsumed by them.

This mode was added in May 2026 from the v10 batch analysis when ~30–40% of finance-bench tasks turned out to be data-engineering / pipeline-reconstruction tasks where schema/format compliance is the dominant failure axis. Before D1 existed, the 9 quant modes were forced to fit, producing high inter-judge variance (one validation trial got 3 different mode picks across 5 sub-agents on the same root cause).

## Decision Procedure

1. **Identify failing tests.** What does each failing test assert?
   - Numerical-value tests (e.g., `assert_almost_equal`, `pytest.approx`, ratio checks): these are *quant-axis* tests; if these fail, A/B/C apply.
   - Schema/format tests: string equality on labels (`assert action == 'replace_initial'`), shape (`isinstance(x, list)`, `len(x) == 2`), column ordering (`df.columns[0] == 'rank'`), type assertions (`isinstance(n, int)`, `isinstance(b, bool)`), exact dict-key matching.

2. **Did the agent's quantitative content pass the quant-axis tests?** If yes (or if there are no quant-axis tests), and there are schema-axis test failures, **D1 fires**.

3. **D1 fires INDEPENDENTLY of A/B/C.** If a trial has both quant-axis failures (formula bug → A2) AND schema-axis failures (wrong vocabulary → D1), match BOTH. Do not collapse.

4. **Authorship sub-question (sets `root_cause_class`):**
   - Did the *prose* enumerate the canonical labels/shape?
     - **Yes** → `root_cause_class = agent_coding` (agent should have followed; spec was clear).
     - **No, but the test pins them** → `root_cause_class = task_side` (spec under-specified; agent's defensible reading didn't match the test's hidden vocabulary). Cross-reference `qf-bench-review`.
   - In both cases D1 still fires (the schema mismatch is real); the `root_cause_class` differentiates blame.

5. **Cite the specific schema mismatch in evidence.** Quote the agent's wrong literal AND the test's expected literal. E.g., `agent: action='RESET'` vs `expected: 'replace_initial'`.

## Sub-rubrics

### D1.a — Vocabulary / label mismatch
Agent invents a defensible string token where the spec/test pins a specific literal.
- *v10 example:* `13f-amendment-aware-crowding` — agent emitted `RESET / RESTATEMENT / APPEND` (uppercase, derived from the SEC `AMENDMENTTYPE` column) while the test pinned `replace_initial / replace_restatement / append_new_holdings` (lowercase snake-case verbs). All 5 model-rounds (h45 R1/R2/R3, s45 R1, opus46 R1) hit this.
- Common shapes: uppercase-vs-snake_case, abbreviated-vs-full ("REPLACE" vs "replace_initial"), agent-invented-from-data-vocabulary vs spec-pinned canonical labels, snake_case vs camelCase.

### D1.b — Shape mismatch (scalar/string vs list/struct)
- `summary.max_overlap_pair` written as `"DAVIDSON_KEMPNER-FULCRUM"` (string) vs expected `["DAVIDSON_KEMPNER", "FULCRUM"]` (2-element list).
- `holder_list` joined with `,` vs expected `|`-joined.
- A tuple emitted as JSON array of distinct types vs uniform-typed array.
- Test asserts `isinstance(x, list)` or `len(x) == 2` and the agent fails on shape, not on content.

### D1.c — Column ordering / missing columns
- `effective_holdings.csv` has `weight` at index 10 instead of (say) index 4.
- `crowded_securities_latest.csv` is missing the leading `rank` column.
- Tests assert `df.columns[i] == "weight"` or `"rank" in df.columns and df.columns.get_loc("rank") == 0`.
- Agent's columns are all present numerically, just in the wrong order.

### D1.d — Type serialization (str-vs-int/bool, identity-column convention)
- `summary.json` numeric counts written as `"79"` (string) instead of `79` (int).
- `all_checks_passed: "True"` instead of `True`.
- `ISAMENDMENT` round-tripped through `bool()` to produce Python `'True'/'False'` strings instead of preserving raw `Y/N/''`.
- Identity drift: agent emits `manager_order` (int 2) where the test expects `manager_label` (str `"OXFORD"`) — same identity but wrong column.

### D1.e — JSON float-precision / serialization rounding
- Agent rounds `max_turnover_value` to 9 decimals during JSON serialization (`0.78043996`); test pins to `0.7804399659638062` at `atol=1e-12`.
- *Mostly task-side* — the test tolerance is unreasonably tight for JSON round-tripping.
- **Match at LOW confidence (≤0.7) with `root_cause_class = task_side`.** This is more a `qf-bench-review` issue than an agent failure.

### D1.f — Date / timestamp serialization format
- Agent emits `'2025-12-31 00:00:00'` (ISO with time) where test expects `'2025-12-31'` (date-only string).
- Or vice versa: test wants ISO-with-tz, agent emits date-only.
- Distinct from B3 (calendar convention) because there is no calendar error — the underlying date is correct, only the string serialization differs. (Subsumes some earlier B3-partial matches.)

### D1.g — Library/API default-induced numerical drift (engineering bug, not QF bug)

**This is the only D1 sub-rubric where the failing test asserts on a numerical *value* rather than a schema artifact.** It earns its place in D because the *mechanism* is engineering-layer (library API quirk), not QF-layer (formula / convention).

**Diagnostic checklist** — fire D1.g only when ALL of these hold:
1. Failing test asserts on a numeric value (not on a string label, list shape, dtype, or column ordering).
2. Code inspection shows the agent's QF-axis choices match oracle: same model class, same formula structure, same convention pick (sign, scale, day-count, ddof), same statistical-method variant.
3. The wrong value can be made correct by changing exactly one keyword argument in a library call (`kind='stable'`, `keep='last'`, `dtype=float`, `errors='raise'`, `sort_keys=True`, `regex=False`, etc.). NO formula or convention change is needed.
4. The mechanism lives at the data-engineering layer: CSV parsing, sort, dedup, merge, type coercion, JSON round-trip, regex matching, hash-based ordering — NOT at the quant-formula layer.

**Canonical example: `cross-sectional-momentum`.**
Agent's code (Opus R1, identical pattern across all 9 cells of the canonical run):
```python
df = df.sort_values('date', ascending=True)
df = df.drop_duplicates(subset='date', keep='last')
```
Failing test: `total_return = 1.6172649012281468` (expected) vs `1.5898447485869` (agent). Ratio ≈ 0.983 — doesn't match any pure-scale signature, suggesting a single-row data corruption that cascades.

Code inspection confirms: formation window `iloc[t-12:t-1]`, simple-arithmetic-sum aggregation, top-3/bottom-3 long/short, `.mean()` realization, `prod(1+r)-1` total return — all identical to oracle's pure-Python implementation. The QF logic is right.

Root cause: the input CSV has duplicate rows on `2017-12-31` with *different AAPL prices*. `pandas.sort_values('date')` defaults to `kind='quicksort'` which is **not stable**, and on this dataset it flips the duplicate-row order. Then `drop_duplicates(keep='last')` silently keeps the wrong row. Verified end-to-end: the same agent code with the spec amended to require `kind='stable'` lifts Haiku 4.5 from 0/3 → 1/1.

**Verdict:** Match D1.g. Set `root_cause_class = agent_coding` (or `task_side` if the spec mandated the buggy idiom — for `cross-sectional-momentum`, the spec literally says "1. sort by date ascending; 2. drop_duplicates(keep='last')" without pinning `kind='stable'`, so the responsibility shifts to the spec).

A3 should return `match: false` with note: `"Subsumed by D1.g — wrong value caused by pandas non-stable sort default, not by agent's QF parameterization choice."`

**Other patterns under D1.g** (each is a "one keyword fix" away from correct):
- Non-deterministic `pandas.merge` row order → `.iloc[0]` picks different row.
- `pandas.read_csv` infers `int64` from integer-valued floats → later division truncates.
- `numpy.argsort` with default `kind` produces different tie-break than oracle.
- `json.dumps(default=float)` round-trips `np.float32` and loses precision the test asserts.
- `re.match` vs `re.fullmatch` ambiguity in label parsing.
- `pandas.DataFrame.groupby(...).first()` ordering depends on internal hash.

**Distinguishing D1.g from A3:**
| Aspect | A3 (parameterization) | D1.g (engineering layer) |
|---|---|---|
| Where the bug lives | Agent's formula or convention pick | Library API default |
| Could agent defend in plain English? | Yes — they reasoned the choice | No — they didn't think about it |
| One-keyword fix? | No — formula or convention change needed | Yes — single kwarg change |
| `root_cause_class` | `agent_conceptual` | `agent_coding` (or `task_side`) |
| What's a true positive? | "I picked ddof=0 for MLE consistency" | "I just used `df.sort_values()` — didn't realize it was unstable" |

**Cascade interaction:** D1.g is the *only* place where D subsumes a quant-axis mode. When D1.g matches, return `match: false` for the parallel A3 (or A2/B1) match with subsumption note. This prevents mis-attributing engineering bugs as QF-knowledge gaps.

## Exclusions (do NOT match D1)

1. **Numerical tolerance issues on values caused by genuine QF reasoning gaps** — if the agent picked `ddof=0` because they reasoned about MLE, that's A3 with `agent_conceptual`, NOT D1.g. The test for D1.g is the one-keyword-fix + plain-English-defense check above.

2. **Missing output files entirely** — if `verifier/test-stdout.txt` shows `FileNotFoundError: /app/output/X.json`, that's a trajectory-side termination issue (the agent didn't run to completion / didn't produce output). Route to `qfbench-trajectory-error-analysis` (Premature Termination domain). D1 does not match.

3. **Empty agent code (Case 1 of insufficient-solution)** — the pre-flight gate already handles this; emit `match=false, gate_skipped=true`.

4. **Code present but no outputs (Case 2)** — the agent's code intent can still be classified for A/B/C, but D1 *cannot* match because there's no output to assess for schema compliance. D1 returns `match=false`.

## Worked examples

### POSITIVE — `fb-v10-h45-13f-amendment-aware-crowding` (D1.a + D1.b + D1.c + D1.d + D1.f)

Agent's `process_13f.py` correctly:
- Loads SEC SUBMISSION/COVERPAGE/SUMMARYPAGE/INFOTABLE.tsv files
- Reconciles amendment filings into effective state
- Computes HHI = Σwᵢ², 1/HHI, turnover = ½Σ|Δwᵢ|, weighted-overlap = Σmin(wᵢ,wⱼ), crowding ranking
- Passes all 35 numeric tests on those quantities

But fails 13 schema tests:
- D1.a: `action` column emitted as `RESET/APPEND/RESTATEMENT` vs pinned `replace_initial/append_new_holdings/replace_restatement` (5 cascading test failures)
- D1.b: `max_overlap_pair` emitted as `'A|B'` string vs `['A', 'B']` list (2 cascading test failures)
- D1.c: `holder_list` joined with `,` vs spec-implied `|`
- D1.d: `summary.json` counts as `"79"` strings; `ISAMENDMENT` as `'True'/'False'` Python booleans vs raw `Y/N/''`
- D1.f: `latest_period_end` as `'2025-12-31 00:00:00'` vs expected `'2025-12-31'`

→ Match: `D1.a + D1.b + D1.c + D1.d + D1.f`. `root_cause_class = task_side` (instruction prose did not enumerate the canonical action labels — agent's labels were a defensible reading of the verbal description "non-amendment resets", "RESTATEMENT replaces", "NEW HOLDINGS appends"). All A/B/C modes return `match=false` with notes "no quant-axis failure on this trial."

### NEGATIVE — wrong Sharpe ratio value
Agent computes Sharpe with `√365` instead of `√252`. Numeric test fails. → This is **B3** (calendar convention), not D1. D1 does not fire because the failure is on the value, not the format.

### NEGATIVE — agent prints results to stdout but doesn't write the required output file
Agent's code is correct, but it `print()`s results instead of writing to `/app/output/results.json`. All FileExistence tests fail. → This is a *trajectory* issue (agent didn't follow the I/O protocol), not D1. Route to trajectory-error skill.

## Output contract (matches system_judge.md)

```json
{
  "match": true,
  "evidence_step_ids": [142, 156, 178],
  "quote": "action_map = {'AMENDMENT-NEW-HOLDINGS': 'APPEND', ...}",
  "confidence": 0.92,
  "root_cause_class": "task_side",
  "notes": "D1.a + D1.b + D1.d. Agent invented uppercase action labels (RESET/APPEND/RESTATEMENT) from AMENDMENTTYPE; test pins lowercase canonical (replace_initial/append_new_holdings/replace_restatement). Also: max_overlap_pair as string vs expected 2-list (D1.b). Plus ISAMENDMENT as bool 'True/False' vs raw 'Y/N/''' (D1.d). All 35 numeric tests pass. Spec prose under-specifies labels — task_side."
}
```

`root_cause_class` choice:
- `agent_coding` — instruction prose enumerated the canonical labels/shape; agent missed them despite spec being clear.
- `task_side` — instruction prose under-specifies; agent's invention is a defensible reading of the verbal description; canonical labels live only in the test files.
- `agent_conceptual` — rare for D1 (would mean agent has a systematic schema-thinking gap, e.g., always returns scalars where lists are required across all tasks).
