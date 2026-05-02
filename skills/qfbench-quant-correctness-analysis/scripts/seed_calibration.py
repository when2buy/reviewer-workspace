"""Stratified-sample N failed trials for human spot-checking.

Mirrors the Terminal-Bench paper's 20-trial calibration step. Output:

    <out>/manifest.json         the chosen trials (subset of list_failed_trials)
    <out>/human_labels.csv      one row per (trial × mode); fill `human_match`
                                with 0/1 then feed back to aggregate_labels.py
                                via --human-labels.
    <out>/preview/<trial-name>/ symlinks (or copies) of bundle.json + labels.json
                                for each chosen trial, for easy reading.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
from pathlib import Path
from typing import Any, Optional

try:
    from list_failed_trials import scan_root  # type: ignore
    from judge_trial import ALL_MODES, applicable_modes  # type: ignore
    from task_context import resolve_tasks_root  # type: ignore
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from list_failed_trials import scan_root  # type: ignore
    from judge_trial import ALL_MODES, applicable_modes  # type: ignore
    from task_context import resolve_tasks_root  # type: ignore


def _stratify(entries: list[dict[str, Any]], n: int, *, seed: int) -> list[dict[str, Any]]:
    """Round-robin pick from buckets keyed by (agent_harness, model) until we
    have n entries. Within a bucket, items are randomly shuffled."""
    if n <= 0 or not entries:
        return []
    rng = random.Random(seed)
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for e in entries:
        key = (e.get("agent_harness") or "", e.get("model") or "")
        buckets.setdefault(key, []).append(e)
    for v in buckets.values():
        rng.shuffle(v)
    chosen: list[dict[str, Any]] = []
    keys = list(buckets.keys())
    rng.shuffle(keys)
    cursor = 0
    while len(chosen) < n and any(buckets[k] for k in keys):
        k = keys[cursor % len(keys)]
        cursor += 1
        if buckets[k]:
            chosen.append(buckets[k].pop())
    return chosen[:n]


def _build_csv_rows(chosen: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for e in chosen:
        kind = e.get("trajectory_kind") or ""
        modes = applicable_modes(kind, list(ALL_MODES))
        for m in modes:
            rows.append({
                "trial_path": e["trial_path"],
                "trial_name": e["trial_dir_name"],
                "agent_harness": e["agent_harness"],
                "model": e["model"],
                "task_name": e["task_name"],
                "trajectory_kind": kind,
                "mode": m,
                "human_match": "",
                "human_notes": "",
            })
    return rows


def _link_preview(trial: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for name in ("bundle.json", "labels.json"):
        src = trial / "agent" / name
        dst = dest / name
        if dst.exists() or dst.is_symlink():
            try:
                dst.unlink()
            except OSError:
                pass
        if not src.is_file():
            continue
        try:
            os.symlink(src, dst)
        except OSError:
            try:
                dst.write_bytes(src.read_bytes())
            except OSError:
                pass


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sample failed trials for human calibration.")
    p.add_argument("--root", required=True)
    p.add_argument("--tasks-root", default=None)
    p.add_argument("--n", type=int, default=20)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default=None)
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        sys.stderr.write(f"[seed_calibration] root not found: {root}\n")
        return 2
    out = Path(args.out).expanduser().resolve() if args.out else (root / "calibration")
    out.mkdir(parents=True, exist_ok=True)
    tasks_root = resolve_tasks_root(args.tasks_root, near=root)
    entries = scan_root(root, tasks_root=tasks_root)
    eligible = [e for e in entries if e.get("ready_for_judging") and e.get("trajectory_kind")]
    if not eligible:
        sys.stderr.write(f"[seed_calibration] no eligible trials under {root}\n")
        return 1
    chosen = _stratify(eligible, args.n, seed=args.seed)
    (out / "manifest.json").write_text(
        json.dumps({"n": len(chosen), "entries": chosen}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    rows = _build_csv_rows(chosen)
    cols = [
        "trial_path", "trial_name", "agent_harness", "model", "task_name",
        "trajectory_kind", "mode", "human_match", "human_notes",
    ]
    with (out / "human_labels.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    preview_root = out / "preview"
    for e in chosen:
        _link_preview(Path(e["trial_path"]), preview_root / e["trial_dir_name"])
    sys.stderr.write(
        f"[seed_calibration] sampled {len(chosen)}/{len(eligible)} trials → {out}\n"
        f"[seed_calibration] fill human_match column in {out / 'human_labels.csv'}, "
        f"then re-run aggregate_labels.py --human-labels {out / 'human_labels.csv'}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
