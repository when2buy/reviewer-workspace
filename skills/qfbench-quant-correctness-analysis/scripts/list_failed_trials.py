"""Walk a QF-Bench trials root and emit a manifest of failed trials.

Layouts the script understands (auto-detected per combo, no flag needed):

    A. Curated:  <root>/<agent>_<model>/{pass,fail}/<trial>/
    B. Flat:     <root>/<agent>_<model>/<trial>/

In both cases the canonical pass/fail signal is

    result.json:verifier_result.rewards.reward     # 1.0 = pass, 0.0 = fail

The directory split (`pass/`, `fail/`) is treated as informational only — pass
or fail is always re-derived from `reward` so a mis-curated trial does not
silently get judged or skipped.

A trial is included in the manifest as failed iff:

    finished_at present  AND  (reward absent OR reward <= 0)

Unfinished trials and passing trials are skipped (passing can be re-included
with --include-passing for downstream analyses).

Each manifest entry:

    {
      "trial_path": "...",
      "agent_harness": "claude-code",
      "model": "sonnet45",
      "task_name": "cev-option-pricing",
      "trajectory_kind": "claude-code | codex | gemini-cli | gemini-cli-alt | finance-zero",
      "trajectory_path": ".../trajectory.json",
      "reward": 0.0,
      "is_failure": true,
      "source_split": "fail | pass | flat",
      "ready_for_judging": true,
      "tasks_root_path": "/.../QuantitativeFinance-Bench/tasks/cev-option-pricing"
    }
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

try:
    from task_context import resolve_tasks_root  # type: ignore
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from task_context import resolve_tasks_root  # type: ignore


# The authoritative task_name lives in result.json. As a fallback when the file
# is missing, we suffix-match the trial dir name against the set of task names
# under tasks_root, picking the longest match.


def _detect_trajectory_kind(agent_dir: Path) -> tuple[Optional[str], Optional[Path]]:
    if not agent_dir.is_dir():
        return None, None
    files = {f.name: f for f in agent_dir.iterdir() if f.is_file()}
    if "claude-code.txt" in files and "trajectory.json" in files:
        return "claude-code", files["trajectory.json"]
    if "codex.txt" in files and "trajectory.json" in files:
        return "codex", files["trajectory.json"]
    if "gemini-cli.txt" in files and "trajectory.json" in files:
        # standard schema preferred when both .trajectory.json and trajectory.json are present
        return "gemini-cli", files["trajectory.json"]
    if "gemini-cli.trajectory.json" in files:
        return "gemini-cli-alt", files["gemini-cli.trajectory.json"]
    if "finance-zero.txt" in files:
        return "finance-zero", files["finance-zero.txt"]
    if "trajectory.json" in files:
        return "trajectory-json", files["trajectory.json"]
    return None, None


def _extract_reward(result_json: Path) -> Optional[float]:
    try:
        with result_json.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None
    vr = data.get("verifier_result")
    if not isinstance(vr, dict):
        return None
    rewards = vr.get("rewards")
    if not isinstance(rewards, dict):
        return None
    r = rewards.get("reward")
    try:
        return float(r) if r is not None else None
    except (TypeError, ValueError):
        return None


def _result_finished(result_json: Path) -> bool:
    try:
        with result_json.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return False
    return bool(data.get("finished_at")) and isinstance(data.get("verifier_result"), dict)


def _task_name_from_result(result_json: Path) -> Optional[str]:
    try:
        with result_json.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None
    name = data.get("task_name")
    if isinstance(name, str) and name:
        return name.rsplit("/", 1)[-1]  # strip any path prefix like "qfbench/power-options"
    tid = data.get("task_id")
    if isinstance(tid, dict):
        path = tid.get("path")
        if isinstance(path, str) and path:
            return path.rsplit("/", 1)[-1]
    return None


def _task_name_from_dir(trial_name: str, known_tasks: list[str]) -> Optional[str]:
    """Recover task_name by finding the longest known task that is a suffix
    of trial_name (after stripping the `fb-` prefix). Returns None if no
    known tasks match."""
    candidate = trial_name[3:] if trial_name.startswith("fb-") else trial_name
    matches = [t for t in known_tasks if candidate.endswith(t)]
    if not matches:
        return None
    matches.sort(key=len, reverse=True)
    return matches[0]


def _list_known_tasks(tasks_root: Optional[Path]) -> list[str]:
    if tasks_root is None or not tasks_root.is_dir():
        return []
    return [p.name for p in tasks_root.iterdir() if p.is_dir() and not p.name.startswith(".")]


def _agent_model_from_dir(name: str) -> tuple[str, str]:
    if "_" in name:
        agent, model = name.split("_", 1)
        return agent, model
    return name, ""


# Names we never treat as trial directories at any level.
_RESERVED_DIRS = frozenset({".git", "reports", "calibration", ".judge_state",
                            "figures", "_cache"})


def _looks_like_trial(p: Path) -> bool:
    """A directory is a trial iff it has either result.json or an agent/ subdir."""
    if not p.is_dir() or p.name.startswith("."):
        return False
    if p.name in _RESERVED_DIRS:
        return False
    return (p / "result.json").is_file() or (p / "agent").is_dir()


def walk_trial_dirs(combo: Path) -> list[tuple[Path, str]]:
    """Yield (trial_path, source_split) for every trial under a combo dir.

    Supports both the curated `<combo>/{pass,fail}/<trial>/` layout and the
    flat `<combo>/<trial>/` layout. If both shapes are present in the same
    combo (e.g. a few uncategorized trials at the top level alongside curated
    pass/fail), all of them are picked up.

    `source_split` is informational ("pass" / "fail" / "flat"); the caller
    derives the real pass/fail status from `result.json`.
    """
    out: list[tuple[Path, str]] = []
    if not combo.is_dir():
        return out
    for child in sorted(combo.iterdir(), key=lambda p: p.name):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if child.name in ("pass", "fail"):
            for trial in sorted(child.iterdir(), key=lambda p: p.name):
                if _looks_like_trial(trial):
                    out.append((trial, child.name))
            continue
        if child.name in _RESERVED_DIRS:
            continue
        if _looks_like_trial(child):
            out.append((child, "flat"))
    return out


def scan_root(
    root: Path,
    *,
    tasks_root: Optional[Path],
    include_passing: bool = False,
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    known_tasks = _list_known_tasks(tasks_root)
    for combo in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")):
        if combo.name in _RESERVED_DIRS:
            continue
        if "_" not in combo.name:
            continue
        agent, model = _agent_model_from_dir(combo.name)
        for trial, source_split in walk_trial_dirs(combo):
            result_json = trial / "result.json"
            reward: Optional[float] = None
            ready = False
            task_name: Optional[str] = None
            if result_json.is_file():
                reward = _extract_reward(result_json)
                ready = _result_finished(result_json)
                task_name = _task_name_from_result(result_json)
            if task_name is None:
                task_name = _task_name_from_dir(trial.name, known_tasks)
            is_failure = reward is None or reward <= 0
            if not is_failure and not include_passing:
                continue
            kind, traj_path = _detect_trajectory_kind(trial / "agent")
            resolved = None
            if tasks_root is not None and task_name:
                cand = tasks_root / task_name
                if cand.is_dir():
                    resolved = str(cand)
            entries.append(
                {
                    "trial_path": str(trial),
                    "agent_harness": agent,
                    "model": model,
                    "task_name": task_name,
                    "trial_dir_name": trial.name,
                    "trajectory_kind": kind,
                    "trajectory_path": str(traj_path) if traj_path else None,
                    "reward": reward,
                    "is_failure": is_failure,
                    "source_split": source_split,
                    "ready_for_judging": bool(ready and is_failure and kind is not None),
                    "tasks_root_path": resolved,
                }
            )
    return entries


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Discover failed QF-Bench trials and emit a manifest.")
    p.add_argument("--root", default=".",
                   help="Root containing <agent>_<model>/<trial>/ or "
                        "<agent>_<model>/{pass,fail}/<trial>/ (both layouts auto-detected).")
    p.add_argument("--tasks-root", default=None,
                   help="QF-Bench tasks root; falls back to QFBENCH_TASKS_ROOT.")
    p.add_argument("--include-passing", action="store_true",
                   help="Also include passing trials in the manifest "
                        "(is_failure=false, ready_for_judging=false). Off by default.")
    p.add_argument("--out", default=None, help="Output JSON path; default stdout.")
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        sys.stderr.write(f"[list_failed_trials] root not found: {root}\n")
        return 2
    tasks_root = resolve_tasks_root(args.tasks_root, near=root)
    entries = scan_root(root, tasks_root=tasks_root, include_passing=args.include_passing)
    n_failed = sum(1 for e in entries if e["is_failure"])
    manifest = {
        "root": str(root),
        "tasks_root": str(tasks_root) if tasks_root else None,
        "n_failed": n_failed,
        "n_total_listed": len(entries),
        "entries": entries,
    }
    serialized = json.dumps(manifest, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(serialized, encoding="utf-8")
        sys.stderr.write(
            f"[list_failed_trials] wrote {n_failed} failed "
            f"({len(entries)} listed) → {args.out}\n"
        )
    else:
        sys.stdout.write(serialized + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
