# Scripts — QF-Bench Quant Correctness Analysis

Pipeline for the `qfbench-quant-correctness-analysis` skill. See [`../OPS.md`](../OPS.md) for the full operations runbook including production-deployment lessons (LFS pull, Python 3.9 asyncio fix, Anthropic rate-limit tuning). This README is a one-page quick-start.

## Scripts

| Script | Purpose |
|---|---|
| `list_failed_trials.py` | Walk `<root>/<combo>/<trial>/` and emit a manifest of failed trials gated on `result.json:reward`. Auto-detects flat vs `pass/`/`fail/` curated layouts. |
| `task_context.py` | Resolve `task_name` to its QF-Bench `tasks/<task-id>/` folder; load `instruction.md` + tests digest. |
| **`extract_solution.py`** | Build the per-trial judging bundle: task context + agent's generated code + output files + failing tests parsed from `test-stdout.txt` (with values where possible). Hashed for resume. |
| **`judge_trial.py`** | Async LLM judge over the 9 modes for one trial. Includes the **deterministic insufficient-solution pre-flight gate** that short-circuits empty/stub trials at $0 cost. Atomic `labels.json` writes. |
| `judge_all.py` | Orchestrator: parallel sweep with per-provider concurrency caps, hash-based resume, `--budget-usd` cap, exponential backoff on rate limits. |
| `aggregate_labels.py` | CSVs (`labels.csv`, `summary_by_model.csv`, `summary_by_task.csv`) + Markdown report + Cohen's-κ vs human labels (when `--human-labels` is provided) + Fig-8-style stacked-bar chart. |
| `seed_calibration.py` | Stratified-sample N trials and emit a `human_labels.csv` template for hand-labeling and κ measurement. |

## Install

```bash
pip install -r requirements.txt
```

Dependencies: `litellm`, `tenacity`, `openpyxl` (optional, for xlsx export).

## Quick start

### 1. Set up workspace

The scripts expect `<root>/<combo>/<trial>/` where `combo` contains `_` (e.g., `claude-code_sonnet45/`). If your trials are flat (e.g., `fb-bench-tracker/trials/fb-pr-h45-foo`), build a sibling workspace via symlinks (see OPS.md §3g).

For `fb-bench-tracker` specifically: also run `git lfs pull` after cloning — ~38% of trajectory.json files are LFS-stored (see OPS.md §3a).

### 2. Sweep + judge

**Recommended settings (validated on 50-trial run, May 2026):**

```bash
python judge_all.py \
    --root /path/to/workspace \
    --tasks-root /path/to/tasks \
    --judge-model anthropic/claude-opus-4-6 \
    --concurrency 2 \
    --concurrency-anthropic 2 \
    --judge-concurrency-per-trial 3 \
    --bundle-max-tokens 40000 \
    --max-tokens 2048 \
    --backoff-max-attempts 8 \
    --budget-usd 100
```

The `2 × 3 = 6` concurrency caps Anthropic input-token usage at ~288K/min, well under the 800K/min org rate limit. With opus-4.6 you'll spend ~$2-4 per trial; with sonnet-4.6 (3× cheaper) ~$0.50-1.

The run is resumable — re-running after Ctrl-C or budget cap will skip trials whose `labels.json` hash matches the current bundle + prompt set + judge model.

### 3. Aggregate

```bash
python aggregate_labels.py \
    --root /path/to/workspace \
    --out /path/to/reports
```

Produces `reports/labels.csv`, `reports/summary_by_*.csv`, `reports/report.md`, and `reports/figures/fig8_failure_profile.png`.

### 4. Calibration (optional but recommended for citation-grade results)

```bash
# Sample 20 trials, stratified across (harness × model)
python seed_calibration.py --root <workspace> --tasks-root <tasks> --n 20 --out calibration/

# Hand-fill calibration/human_labels.csv (see CALIBRATION.md for methodology)

# Compute Cohen's κ
python aggregate_labels.py \
    --root <workspace> \
    --human-labels calibration/human_labels.csv \
    --out reports/
# → reports/agreement.csv with per-mode κ + overall
```

The skill's reference calibration achieved **κ = 0.89** (substantial agreement, 7 of 9 modes at perfect agreement). See [`../CALIBRATION.md`](../CALIBRATION.md) for the methodology.

## Pre-flight gate

`judge_trial.py` deterministically short-circuits trials with:
- `agent_code` < 500 non-whitespace chars **AND**
- 0 output files **AND**
- 0 failing tests with numerical comparisons

…producing 9 `match=false` labels with `gate_skipped: true` flag at $0 cost. This catches the "agent generated only imports + a stub function" case that finance-zero models commonly fall into.

Calibrated on the 50-trial validation: gate fires on ~50% of stub-heavy samples, **0 false positives** on 61 trials checked. Saves ~50% on production-sweep cost.

To disable (for debugging): edit `_INSUFFICIENT_CODE_CHARS_THRESHOLD` in `judge_trial.py`.

## Imports

The scripts import each other as siblings (e.g. `from task_context import build_context`). Each script also self-installs its containing directory onto `sys.path` if launched directly, so you can run any of them via `python /path/to/scripts/<name>.py ...` without setting `PYTHONPATH`.

## Dry-runs

`judge_trial.py` and `judge_all.py` accept `--dry-run`, which builds the judging bundle and fills the prompt placeholders but does not call the LLM. Useful for verifying the workspace layout before incurring spend.

## Rate-limit tuning by judge model

| Model | `--concurrency` × `--judge-concurrency-per-trial` | `--bundle-max-tokens` | Per-call typical input | Notes |
|---|---|---|---|---|
| **gpt-5** | 8 × 9 (default) | 80000 | varies | OpenAI rate caps differ |
| **claude-opus-4-6** | **2 × 3** | **40000** | ~16-30K | Heaviest model; needs conservative settings |
| **claude-sonnet-4-6** | 4 × 6 | 60000 | ~12-25K | 3× cheaper, similar κ on this rubric |
| **claude-haiku-4-5** | 6 × 9 | 80000 | ~10-20K | Cheapest; good for bulk pre-screens |

## Pricing table

`DEFAULT_PRICING` in `judge_trial.py` is keyed on model substring match. When a new model lands, add it explicitly — otherwise `cost_usd` will silently stay at $0 for that model and `--budget-usd` won't trigger.

Current entries: `gpt-5`, `gpt-5-mini`, `gpt-4o`, `claude-opus-4-5`, `claude-opus-4-6`, `claude-sonnet-4-5`, `claude-sonnet-4-6`, `gemini-2.5-pro`, `gemini-2.5-flash`.
