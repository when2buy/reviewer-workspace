"""Aggregate per-trial labels.json into camera-ready CSVs and a Markdown report.

Walks every trial under <root>/<agent>_<model>/ (curated `pass`/`fail` layout
*and* flat `<combo>/<trial>/` layout are both supported) and consumes
agent/labels.json from each. Produces:

    <out>/labels.csv             one row per (trial × mode)
    <out>/summary_by_model.csv   per agent_harness × model: % of trials with
                                 each mode and any-mode-in-class
    <out>/summary_by_task.csv    per task_name: % of trials with each mode
    <out>/agreement.csv          (only if --human-labels CSV is provided):
                                 Cohen's-κ per mode + overall vs LLM judge
    <out>/report.md              paper-ready Markdown report
    <out>/figures/fig8_failure_profile.png    Terminal-Bench Fig-8-style chart

Optional arg --human-labels points to the CSV emitted by seed_calibration.py
after the user has filled in 0/1 labels per mode.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Optional

try:
    from judge_trial import ALL_MODES  # type: ignore
    from list_failed_trials import walk_trial_dirs  # type: ignore
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from judge_trial import ALL_MODES  # type: ignore
    from list_failed_trials import walk_trial_dirs  # type: ignore


CLASS_OF: dict[str, str] = {
    "wrong_model_measure": "Model_Formula",
    "missing_extra_formula_term": "Model_Formula",
    "wrong_parameterization": "Model_Formula",
    "unit_scale_error": "Convention_Units",
    "sign_convention_error": "Convention_Units",
    "time_calendar_convention": "Convention_Units",
    "data_fabrication_wrong_source": "Data_Numerics",
    "numerical_optimization_failure": "Data_Numerics",
    "statistical_variant_mismatch": "Data_Numerics",
}

ROOT_CAUSE_CLASSES: list[str] = ["agent_conceptual", "agent_coding", "task_side"]

LOW_CONF_THRESHOLD = 0.5


def _walk_labels(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for combo in sorted(p for p in root.iterdir() if p.is_dir() and "_" in p.name):
        agent_harness, _, model = combo.name.partition("_")
        for trial, _split in walk_trial_dirs(combo):
            labels_path = trial / "agent" / "labels.json"
            if not labels_path.is_file():
                continue
            try:
                payload = json.loads(labels_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            labels = payload.get("labels") or {}
            for mode, info in labels.items():
                if not info:
                    continue
                rows.append(
                    {
                        "trial_path": str(trial),
                        "trial_name": trial.name,
                        "agent_harness": payload.get("agent_harness") or agent_harness,
                        "model": payload.get("model") or model,
                        "task_name": payload.get("task_name"),
                        "trajectory_kind": payload.get("trajectory_kind"),
                        "mode": mode,
                        "mode_class": CLASS_OF.get(mode, ""),
                        "match": bool(info.get("match")),
                        "confidence": float(info.get("confidence") or 0.0),
                        "root_cause_class": info.get("root_cause_class") or "",
                        "ok": bool(info.get("ok", True)),
                        # `gate_skipped` distinguishes deterministic short-circuit
                        # by the insufficient-solution pre-flight gate from real
                        # LLM-judged "no match" labels. Aggregators should treat
                        # gate_skipped as a separate bucket: it tells us the
                        # trial had no evaluable signal, not that the agent's
                        # solution was sound.
                        "gate_skipped": bool(info.get("gate_skipped", False))
                        or bool(payload.get("gate_skipped", False)),
                        "judge_model": payload.get("judge_model"),
                        "evidence_step_ids": json.dumps(info.get("evidence_step_ids") or []),
                        "quote": (info.get("quote") or "").replace("\n", " ")[:200],
                        "notes": (info.get("notes") or "").replace("\n", " ")[:300],
                    }
                )
    return rows


def _summarize(rows: list[dict[str, Any]], group_keys: list[str]) -> list[dict[str, Any]]:
    """For each group of (group_keys), compute per-mode match rates (over the
    set of *trials* in the group), plus per-class any-mode rates and n_trials."""
    by_group: dict[tuple, dict[str, Any]] = {}
    for r in rows:
        key = tuple(r.get(k) for k in group_keys)
        g = by_group.setdefault(key, {"trials": {}, "matches_by_mode": {}, "matches_by_class": {}})
        tp = r["trial_path"]
        if tp not in g["trials"]:
            g["trials"][tp] = {"modes": {}, "classes": {}, "gate_skipped": False}
        if r.get("gate_skipped"):
            # Mark the whole trial as gated; per-mode rates exclude these from
            # the denominator so they don't dilute "agent's solution was sound"
            # rates. Gate-skipped trials are reported separately below.
            g["trials"][tp]["gate_skipped"] = True
        elif r["ok"]:
            g["trials"][tp]["modes"][r["mode"]] = r["match"]
            g["trials"][tp]["classes"].setdefault(r["mode_class"], False)
            if r["match"]:
                g["trials"][tp]["classes"][r["mode_class"]] = True
    out: list[dict[str, Any]] = []
    for key, g in sorted(by_group.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
        n_trials = len(g["trials"])
        row: dict[str, Any] = dict(zip(group_keys, key))
        row["n_trials"] = n_trials
        # per-mode rates
        for mode in ALL_MODES:
            n_judged = sum(1 for t in g["trials"].values() if mode in t["modes"])
            n_match = sum(1 for t in g["trials"].values() if t["modes"].get(mode))
            row[f"{mode}_n_judged"] = n_judged
            row[f"{mode}_n_match"] = n_match
            row[f"{mode}_pct"] = (n_match / n_judged * 100.0) if n_judged else 0.0
        # per-class any-mode rates
        for cls in ("Model_Formula", "Convention_Units", "Data_Numerics"):
            n_judged = sum(1 for t in g["trials"].values() if cls in t["classes"])
            n_match = sum(1 for t in g["trials"].values() if t["classes"].get(cls))
            row[f"{cls}_n_match"] = n_match
            row[f"{cls}_pct"] = (n_match / n_judged * 100.0) if n_judged else 0.0
        out.append(row)
    return out


def _write_csv(path: Path, rows: list[dict[str, Any]], columns: Optional[list[str]] = None) -> None:
    import csv
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    if columns is None:
        columns = list(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columns)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in columns})


# ---------- Cohen's kappa --------------------------------------------------------

def cohens_kappa(a: list[int], b: list[int]) -> float:
    """Cohen's kappa for binary labels. Returns NaN for empty inputs."""
    if not a or len(a) != len(b):
        return float("nan")
    n = len(a)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pa1 = sum(a) / n
    pb1 = sum(b) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    if pe >= 1.0:
        return 1.0 if po == 1.0 else float("nan")
    return (po - pe) / (1 - pe)


def _load_human_labels(path: Path) -> dict[tuple[str, str], int]:
    """Read CSV with at least columns: trial_path, mode, human_match. Returns
    {(trial_path, mode): 0/1}."""
    import csv
    out: dict[tuple[str, str], int] = {}
    with path.open("r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            tp = row.get("trial_path") or ""
            mode = row.get("mode") or ""
            v = row.get("human_match")
            if v is None or v == "":
                continue
            try:
                out[(tp, mode)] = int(v)
            except ValueError:
                continue
    return out


# ---------- quality flags --------------------------------------------------------

def _quality_flags(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate parse-failed and low-confidence-positive judgments per mode.

    Following the SkillsBench guidance to never silently fold "uncertain" or
    "parse-failed" judgments into the negative bucket — they are a separate
    population that should be surfaced for human review.
    """
    per_mode: dict[str, dict[str, int]] = {
        m: {"n_judged": 0, "n_parse_failed": 0, "n_low_conf_pos": 0, "n_match": 0}
        for m in ALL_MODES
    }
    review_rows: list[dict[str, Any]] = []
    for r in rows:
        mode = r["mode"]
        if mode not in per_mode:
            continue
        per_mode[mode]["n_judged"] += 1
        if not r["ok"]:
            per_mode[mode]["n_parse_failed"] += 1
            review_rows.append({**r, "review_reason": "parse_failed"})
            continue
        if r["match"]:
            per_mode[mode]["n_match"] += 1
            if r["confidence"] < LOW_CONF_THRESHOLD:
                per_mode[mode]["n_low_conf_pos"] += 1
                review_rows.append({**r, "review_reason": "low_confidence_positive"})
    summary_rows: list[dict[str, Any]] = []
    for mode in ALL_MODES:
        s = per_mode[mode]
        n = s["n_judged"]
        summary_rows.append({
            "mode": mode,
            "n_judged": n,
            "n_match": s["n_match"],
            "n_parse_failed": s["n_parse_failed"],
            "n_low_conf_pos": s["n_low_conf_pos"],
            "parse_failed_pct": (s["n_parse_failed"] / n * 100.0) if n else 0.0,
            "low_conf_pos_pct": (
                (s["n_low_conf_pos"] / s["n_match"] * 100.0) if s["n_match"] else 0.0
            ),
        })
    totals = {
        "n_judged": sum(s["n_judged"] for s in per_mode.values()),
        "n_match": sum(s["n_match"] for s in per_mode.values()),
        "n_parse_failed": sum(s["n_parse_failed"] for s in per_mode.values()),
        "n_low_conf_pos": sum(s["n_low_conf_pos"] for s in per_mode.values()),
    }
    return {"per_mode": summary_rows, "review_rows": review_rows, "totals": totals}


def _agreement_table(
    rows: list[dict[str, Any]], human: dict[tuple[str, str], int]
) -> list[dict[str, Any]]:
    by_mode: dict[str, list[tuple[int, int]]] = {}
    overall: list[tuple[int, int]] = []
    for r in rows:
        if not r["ok"]:
            continue
        key = (r["trial_path"], r["mode"])
        if key not in human:
            continue
        h = human[key]
        m = 1 if r["match"] else 0
        by_mode.setdefault(r["mode"], []).append((h, m))
        overall.append((h, m))
    out: list[dict[str, Any]] = []
    for mode in ALL_MODES:
        pairs = by_mode.get(mode, [])
        a = [p[0] for p in pairs]
        b = [p[1] for p in pairs]
        out.append({
            "mode": mode,
            "n": len(pairs),
            "kappa": cohens_kappa(a, b),
            "n_human_match": sum(a),
            "n_judge_match": sum(b),
        })
    out.append({
        "mode": "OVERALL",
        "n": len(overall),
        "kappa": cohens_kappa([p[0] for p in overall], [p[1] for p in overall]),
        "n_human_match": sum(p[0] for p in overall),
        "n_judge_match": sum(p[1] for p in overall),
    })
    return out


# ---------- markdown report ------------------------------------------------------

def _md_table(rows: list[dict[str, Any]], cols: list[str], format_pct: set[str]) -> str:
    if not rows:
        return "*(no data)*\n"
    head = "| " + " | ".join(cols) + " |\n"
    sep = "| " + " | ".join("---" for _ in cols) + " |\n"
    body_lines: list[str] = []
    for r in rows:
        cells: list[str] = []
        for c in cols:
            v = r.get(c, "")
            if c in format_pct and isinstance(v, (int, float)) and not isinstance(v, bool):
                cells.append(f"{v:.1f}%")
            elif isinstance(v, float):
                if math.isnan(v):
                    cells.append("—")
                else:
                    cells.append(f"{v:.3f}")
            else:
                cells.append(str(v))
        body_lines.append("| " + " | ".join(cells) + " |")
    return head + sep + "\n".join(body_lines) + "\n"


def _build_report_md(
    by_model: list[dict[str, Any]],
    by_task: list[dict[str, Any]],
    agreement: Optional[list[dict[str, Any]]],
    quality: dict[str, Any],
    *,
    n_trials_total: int,
    n_modes_judged: int,
) -> str:
    pct_cols_class = ["Model_Formula_pct", "Convention_Units_pct", "Data_Numerics_pct"]
    pct_cols_modes = [f"{m}_pct" for m in ALL_MODES]
    out: list[str] = []
    out.append("# QF-Bench Trajectory Error Analysis — Failure Mode Report\n")
    out.append(
        f"Trials with labels: **{n_trials_total}**. "
        f"Mode-level judgments aggregated: **{n_modes_judged}**.\n"
    )
    out.append("Rubric source: arXiv:2601.11868 §C.1–C.2 (Terminal-Bench).\n")
    out.append("\n## Per-class match rate by `agent_harness × model`\n")
    out.append(_md_table(
        by_model,
        ["agent_harness", "model", "n_trials"] + pct_cols_class,
        format_pct=set(pct_cols_class),
    ))
    out.append("\n## Per-mode match rate by `agent_harness × model`\n")
    out.append(_md_table(
        by_model,
        ["agent_harness", "model", "n_trials"] + pct_cols_modes,
        format_pct=set(pct_cols_modes),
    ))
    out.append("\n## Per-mode match rate by `task_name`\n")
    out.append(_md_table(
        by_task,
        ["task_name", "n_trials"] + pct_cols_modes,
        format_pct=set(pct_cols_modes),
    ))
    if agreement is not None:
        out.append("\n## LLM-judge vs human agreement (Cohen's κ)\n")
        out.append(_md_table(
            agreement,
            ["mode", "n", "kappa", "n_human_match", "n_judge_match"],
            format_pct=set(),
        ))
    totals = quality["totals"]
    if totals["n_parse_failed"] or totals["n_low_conf_pos"]:
        out.append("\n## Coverage & confidence (needs human review)\n")
        out.append(
            f"Of {totals['n_judged']} mode-level judgments, "
            f"**{totals['n_parse_failed']}** failed to parse as strict JSON and "
            f"**{totals['n_low_conf_pos']}** positives carry confidence < "
            f"{LOW_CONF_THRESHOLD}. These are *not* folded into the negatives — "
            "see `low_confidence.csv` for the full list and re-judge or label by hand "
            "before citing the headline numbers.\n"
        )
        out.append(_md_table(
            quality["per_mode"],
            ["mode", "n_judged", "n_match", "n_parse_failed", "n_low_conf_pos",
             "parse_failed_pct", "low_conf_pos_pct"],
            format_pct={"parse_failed_pct", "low_conf_pos_pct"},
        ))
    out.append("\n*See `figures/fig8_failure_profile.png` for a Terminal-Bench Figure-8-style stacked bar chart.*\n")
    return "".join(out)


# ---------- figure ---------------------------------------------------------------

def _plot_fig8(by_model: list[dict[str, Any]], path: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        sys.stderr.write(f"[aggregate_labels] matplotlib unavailable; skipping figure: {exc}\n")
        return
    if not by_model:
        return
    labels = [f"{r['agent_harness']}\n{r['model']}\n(n={r['n_trials']})" for r in by_model]
    classes = ["Model_Formula", "Convention_Units", "Data_Numerics"]
    data = {cls: [r.get(f"{cls}_pct", 0.0) for r in by_model] for cls in classes}
    x = list(range(len(by_model)))
    bar_w = 0.25
    fig, ax = plt.subplots(figsize=(max(8, 1.5 * len(by_model)), 5))
    for i, cls in enumerate(classes):
        ax.bar([xi + (i - 1) * bar_w for xi in x], data[cls], width=bar_w, label=cls)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=0, fontsize=8)
    ax.set_ylabel("% of failed trials with ≥1 match in class")
    ax.set_title("QF-Bench failure-mode profile by agent × model")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper right")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------- CLI ------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Aggregate labels.json into CSVs + report + figure.")
    p.add_argument("--root", required=True)
    p.add_argument("--out", default=None)
    p.add_argument("--human-labels", default=None,
                   help="Optional CSV with columns trial_path,mode,human_match.")
    p.add_argument("--low-conf-threshold", type=float, default=LOW_CONF_THRESHOLD,
                   help=f"Confidence below this is flagged as low-confidence positive "
                        f"(default {LOW_CONF_THRESHOLD}).")
    return p.parse_args()


def main() -> int:
    global LOW_CONF_THRESHOLD
    args = _parse_args()
    LOW_CONF_THRESHOLD = float(args.low_conf_threshold)
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        sys.stderr.write(f"[aggregate_labels] root not found: {root}\n")
        return 2
    out = Path(args.out).expanduser().resolve() if args.out else (root / "reports")
    out.mkdir(parents=True, exist_ok=True)
    rows = _walk_labels(root)
    if not rows:
        sys.stderr.write(f"[aggregate_labels] no labels.json found under {root}\n")
        return 1

    by_model = _summarize(rows, ["agent_harness", "model"])
    by_task = _summarize(rows, ["task_name"])
    quality = _quality_flags(rows)
    n_trials_total = len({r["trial_path"] for r in rows})
    n_modes_judged = len(rows)
    label_cols = [
        "trial_path", "trial_name", "agent_harness", "model", "task_name",
        "trajectory_kind", "mode", "mode_class", "match", "confidence",
        "root_cause_class", "ok",
        "judge_model", "evidence_step_ids", "quote", "notes",
    ]
    _write_csv(out / "labels.csv", rows, columns=label_cols)
    pct_cols_modes = [f"{m}_pct" for m in ALL_MODES]
    pct_cols_class = ["Model_Formula_pct", "Convention_Units_pct", "Data_Numerics_pct"]
    by_model_cols = ["agent_harness", "model", "n_trials"] + pct_cols_class + pct_cols_modes + [
        f"{m}_n_match" for m in ALL_MODES
    ] + [f"{m}_n_judged" for m in ALL_MODES]
    by_task_cols = ["task_name", "n_trials"] + pct_cols_class + pct_cols_modes + [
        f"{m}_n_match" for m in ALL_MODES
    ] + [f"{m}_n_judged" for m in ALL_MODES]
    _write_csv(out / "summary_by_model.csv", by_model, columns=by_model_cols)
    _write_csv(out / "summary_by_task.csv", by_task, columns=by_task_cols)

    review_cols = ["trial_path", "trial_name", "agent_harness", "model", "task_name",
                   "mode", "mode_class", "match", "confidence", "ok",
                   "judge_model", "review_reason", "quote", "notes"]
    _write_csv(out / "low_confidence.csv", quality["review_rows"], columns=review_cols)

    agreement: Optional[list[dict[str, Any]]] = None
    if args.human_labels:
        hpath = Path(args.human_labels).expanduser().resolve()
        if not hpath.is_file():
            sys.stderr.write(f"[aggregate_labels] --human-labels not found: {hpath}\n")
        else:
            human = _load_human_labels(hpath)
            agreement = _agreement_table(rows, human)
            _write_csv(
                out / "agreement.csv",
                agreement,
                columns=["mode", "n", "kappa", "n_human_match", "n_judge_match"],
            )
    md = _build_report_md(by_model, by_task, agreement, quality,
                          n_trials_total=n_trials_total, n_modes_judged=n_modes_judged)
    (out / "report.md").write_text(md, encoding="utf-8")
    _plot_fig8(by_model, out / "figures" / "fig8_failure_profile.png")
    sys.stderr.write(
        f"[aggregate_labels] wrote labels.csv ({len(rows)} rows), "
        f"summary_by_model.csv ({len(by_model)} rows), "
        f"summary_by_task.csv ({len(by_task)} rows), "
        f"low_confidence.csv ({len(quality['review_rows'])} rows), "
        f"report.md, fig8 → {out}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
