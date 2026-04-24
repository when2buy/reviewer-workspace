# Review: PR #53 - equity-vendor-restatement-break-audit
Reviewer: Grim 🔍 | Date: 2026-04-23

### What This PR Does
Agent audits vendor restatements between two publication vintages for a US equity, identifies checkpoint breaks, groups them into break windows, and diagnoses root causes using vendor bulletins.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py, test.sh, solution/solve.py, Dockerfile
- Reviewed trial results: H45=0.0, Opus46=0.0, S45=0.0
- Analyzed failure patterns across all three models

### Scorecard
- Task contract / instruction: 3/5
- Verifier robustness: 3/5
- Difficulty calibration: 2/5
- Benchmark integrity / anti-cheating: 4/5
- Data realism / determinism: 4/5

### Findings

#### [CRITICAL] All three models fail on same verifier ambiguity
All models (H45, Opus, S45) produce `vintage_from = "2003-03-10"` instead of expected `"vendor_reference_v1"`. The test expects `intermediates["vintage_from"]["value"] == "vendor_reference_v1"` — meaning the vintage identifier should be the filename stem, not a date.

The instruction says: "Treat `vendor_reference_v1.csv` as the `vintage_from` checkpoint baseline." The `results.json` schema shows `"vintage_from": <string>` without specifying what the string should be. The test pins it to `"vendor_reference_v1"`.

This is an **instruction gap**: the instruction doesn't explicitly say that `vintage_from` should be the filename stem `"vendor_reference_v1"` rather than a date extracted from the data. All three frontier models make the same reasonable interpretation error.

#### [MAJOR] Opus and S45 fail on vendor_audit_windows exact match
The test pins exact expected rows for `vendor_audit_windows.csv` including exact `max_abs_diff` values. Opus passes `test_corrected_and_cancelled_bulletins_are_explicitly_diagnosed` but S45 and H45 don't — suggesting the break detection logic is partially ambiguous.

#### [MAJOR] 0/3 pass rate suggests specification problem, not difficulty
When all three frontier models (including Opus 4.6) fail, the most likely explanation is ambiguous specification rather than genuine difficulty. The failures are on schema/naming conventions, not on financial reasoning.

#### [MINOR] Good domain concept — vendor restatement auditing
The task itself is a realistic data engineering + domain knowledge problem. Break window detection, bulletin-aware root cause diagnosis, and vintage comparison are genuine quant data ops skills.


### Trial Evidence
| Model | Reward | Duration | Tokens |
|---|---|---|---|
| Haiku 4.5 | 0.0 | 56s | 150,698in / 3,901out |
| Opus 4.6 | 0.0 | 73s | 114,282in / 2,555out |
| Sonnet 4.5 | 0.0 | 81s | 102,501in / 4,429out |


**Haiku key failures:**
```
FAIL: test_results_json_schema_and_summary_counts
E       AssertionError: assert '2003-03-10' == 'vendor_reference_v1'
E
E         - vendor_reference_v1
E         + 2003-03-10
FAIL: test_vendor_audit_windows_schema_order_and_window_aggregation
E       AssertionError: assert [{'break_row_...lletin', ...}] == [{'break_row_...lletin', ...}]
E
```


**Opus key failures:**
```
FAIL: test_results_json_schema_and_summary_counts
E       AssertionError: assert '2003-03-10' == 'vendor_reference_v1'
E
E         - vendor_reference_v1
E         + 2003-03-10
FAIL: test_vendor_audit_windows_schema_order_and_window_aggregation
E       AssertionError: assert [{'break_row_...lletin', ...}] == [{'break_row_...lletin', ...}]
E
```

### Summary
Promising task concept undermined by specification gaps. All three models fail because `vintage_from` meaning (filename stem vs date) is ambiguous. The instruction should explicitly state: "Use the CSV filename stem (e.g., `vendor_reference_v1`) as the vintage identifier."

### Verdict
**不建议 Merge**

Fix the instruction to clarify vintage identifier format, then re-run trials. The underlying task is good but the 0/3 failure is a specification problem.
