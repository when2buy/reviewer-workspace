# Review: PR #51 - binance-btc-participation-tca
Reviewer: Grim 🔍 | Date: 2026-04-23

### What This PR Does
Agent reconstructs deterministic participation-capped fills from Binance BTCUSDT futures quote/trade data, computes TCA metrics (implementation shortfall, effective spread, realized spread, temporary impact), and produces detailed per-bucket fill reports.

### What I Did to Review This
- Read: instruction.md, task.toml, test_outputs.py, test.sh, solution/solve.py, Dockerfile
- Reviewed trial results: All 3 models failed with Docker build error (sha256 image pull failure)
- Checked verifier correctness, anti-cheat properties

### Scorecard
- Task contract / instruction: 5/5
- Verifier robustness: 5/5
- Difficulty calibration: N/A (infrastructure failure, not task failure)
- Benchmark integrity / anti-cheating: 4/5
- Data realism / determinism: 5/5

### Findings

#### [CRITICAL] Dockerfile uses sha256-pinned image that doesn't exist
`FROM finance-bench-sandbox:latest@sha256:709847c6...` — all three trials failed with "pull access denied, repository does not exist." This is an infrastructure issue, not a task design issue. The image needs to be available in the build environment.

#### [MINOR] Excellent verifier design
The test suite is outstanding: it independently recomputes expected fills from raw input data (`_expected_fills_from_input_data()`), then compares against agent output row-by-row. It also pins exact expected values for all TCA metrics in `EXPECTED_RESULTS`. This is the gold standard for benchmark verification — deterministic, recomputed from inputs, with exact numeric expectations.

#### [MINOR] Very detailed instruction with precise output schema
The instruction specifies exact JSON key order, CSV column order, float formatting (6 decimals), timestamp format (epoch ms), empty-bucket rules. This is extremely precise, which makes it a strong contract test but also means agents fail on format rather than substance.

#### [MINOR] Real Binance data — excellent realism
Uses actual BTCUSDT futures quote/trade data from 2024-01-01, providing genuine market microstructure complexity.

#### [NIT] Solution and test both contain full expected values
The test hardcodes `EXPECTED_RESULTS`, `EXPECTED_SOLUTION_INTERMEDIATES`, and `EXPECTED_SOLUTION_CHECKPOINTS`. While these are in the test (not visible to agent at runtime), this is a strong anti-cheat design.

### Summary
This is one of the best-designed tasks in this batch. Precise specification, deterministic verification from raw inputs, real market data, and strong anti-cheat properties. The only issue is the Docker image availability, which is an infrastructure problem.

### Verdict
**建议 Merge**

Fix the Docker image reference (remove sha256 pin or ensure image is available). The task itself is production-quality. Re-run trials after Docker fix to get calibration data.
