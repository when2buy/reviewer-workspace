"""Sweep / watch the QF-Bench workspace and judge every failed trial in parallel.

Designed to run alongside the experiment harness during a deadline-rush:

    python judge_all.py --root /path/to/fb-sampled-trials --watch \
        --judge-model gpt-5 --reasoning-effort high \
        --concurrency 8 --budget-usd 50

Behavior:
  - Discovers fail trials via list_failed_trials.scan_root.
  - Skips trials with up-to-date labels.json (prompt + bundle hashes match).
  - Runs trials concurrently with per-provider Semaphores (default openai=8,
    anthropic=4, gemini=8). Override via --concurrency-openai, etc.
  - Retries on transient errors with exponential backoff via tenacity.
  - Tracks running USD cost; aborts cleanly when --budget-usd is reached.
  - Run state in <root>/.judge_state.json. Safe to Ctrl-C and resume.
  - --watch polls every --watch-interval seconds and judges newly-finished
    trials. Exits cleanly on Ctrl-C.

Each trial is processed by:
  1. _load_or_build_bundle(trial)  (writes/refreshes <trial>/agent/bundle.json)
  2. judge_trial(trial)            (writes <trial>/agent/labels.json atomically)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import signal
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    from list_failed_trials import scan_root  # type: ignore
    from judge_trial import (  # type: ignore
        ALL_MODES,
        JudgeCfg,
        applicable_modes,
        _can_skip,
        _load_or_build_bundle,
        _trial_paths,
        judge_trial,
        prompt_set_hash,
        write_labels_atomic,
    )
    from task_context import resolve_tasks_root  # type: ignore
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from list_failed_trials import scan_root  # type: ignore
    from judge_trial import (  # type: ignore
        ALL_MODES,
        JudgeCfg,
        applicable_modes,
        _can_skip,
        _load_or_build_bundle,
        _trial_paths,
        judge_trial,
        prompt_set_hash,
        write_labels_atomic,
    )
    from task_context import resolve_tasks_root  # type: ignore


# ---------- provider routing -----------------------------------------------------

def provider_for_model(model: str) -> str:
    m = model.lower()
    if m.startswith(("gpt", "o1", "o3", "o4", "openai", "azure/")):
        return "openai"
    if m.startswith(("claude", "anthropic", "bedrock/", "claude-")):
        return "anthropic"
    if m.startswith(("gemini", "google/", "vertex_ai/")):
        return "gemini"
    return "default"


# ---------- run state ------------------------------------------------------------

STATE_FILENAME = ".judge_state.json"


def _load_state(state_path: Path) -> dict[str, Any]:
    if state_path.is_file():
        try:
            return json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {"runs": [], "total_cost_usd": 0.0, "trials_judged": 0, "trials_skipped": 0}


def _persist_state(state_path: Path, state: dict[str, Any]) -> None:
    tmp = state_path.with_suffix(state_path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(state_path)


# ---------- worker ---------------------------------------------------------------

@dataclass
class WorkerCfg:
    judge: JudgeCfg
    requested_modes: list[str]
    tasks_root: Optional[Path]
    bundle_max_total_chars: int
    bundle_max_step_chars: int
    bundle_max_instruction_chars: int
    bundle_max_test_files: int
    bundle_test_head_lines: int
    include_oracle_headers: bool
    refresh_bundle: bool
    force: bool
    dry_run: bool
    judge_concurrency_per_trial: int
    # Per-provider concurrency caps. Stored as ints; the actual asyncio.Semaphore
    # objects are constructed inside the running event loop in _run() to avoid
    # Python 3.9's "Future attached to a different loop" error that occurs when
    # Semaphores are created outside `asyncio.run()`.
    concurrency_caps: dict[str, int] = field(default_factory=dict)
    semaphores: dict[str, asyncio.Semaphore] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)
    state_path: Optional[Path] = None
    budget_usd: Optional[float] = None
    stop_event: Optional[asyncio.Event] = None
    backoff_max_attempts: int = 4


async def _retry(coro_factory, *, max_attempts: int) -> Any:
    last_exc: Optional[BaseException] = None
    for attempt in range(max_attempts):
        try:
            return await coro_factory()
        except Exception as exc:
            last_exc = exc
            sleep = min(60.0, 1.5 * (2 ** attempt))
            await asyncio.sleep(sleep)
    if last_exc:
        raise last_exc


async def _process_one(entry: dict[str, Any], cfg: WorkerCfg) -> tuple[str, dict[str, Any]]:
    trial = Path(entry["trial_path"])
    paths = _trial_paths(trial)
    try:
        bundle = _load_or_build_bundle(
            trial,
            trajectory_kind=entry.get("trajectory_kind"),
            task_name=entry.get("task_name"),
            tasks_root=cfg.tasks_root,
            max_total_chars=cfg.bundle_max_total_chars,
            max_step_chars=cfg.bundle_max_step_chars,
            max_instruction_chars=cfg.bundle_max_instruction_chars,
            max_test_files=cfg.bundle_max_test_files,
            test_head_lines=cfg.bundle_test_head_lines,
            include_oracle_headers=cfg.include_oracle_headers,
            refresh=cfg.refresh_bundle,
        )
    except Exception as exc:
        return "error", {"trial": str(trial), "error": f"bundle build: {type(exc).__name__}: {exc}"}
    p_hash = prompt_set_hash()
    if not cfg.force and not cfg.dry_run and _can_skip(
        paths.labels,
        bundle_hash=bundle["bundle_hash"],
        prompt_hash=p_hash,
        judge_model=cfg.judge.model,
        requested_modes=applicable_modes(bundle["trajectory_kind"], cfg.requested_modes),
    ):
        return "skipped", {"trial": str(trial)}
    provider = provider_for_model(cfg.judge.model)
    sem = cfg.semaphores.get(provider) or cfg.semaphores.get("default")
    if sem is None:
        sem = asyncio.Semaphore(8)

    async def call() -> dict[str, Any]:
        async with sem:
            return await judge_trial(
                trial,
                cfg.judge,
                requested_modes=cfg.requested_modes,
                bundle=bundle,
                concurrency=cfg.judge_concurrency_per_trial,
                dry_run=cfg.dry_run,
            )

    try:
        payload = await _retry(call, max_attempts=cfg.backoff_max_attempts)
    except Exception as exc:
        return "error", {"trial": str(trial), "error": f"judge: {type(exc).__name__}: {exc}"}
    write_labels_atomic(paths.labels, payload)
    cost = float(payload.get("total_cost_usd") or 0.0)
    if cfg.state is not None:
        cfg.state["total_cost_usd"] = float(cfg.state.get("total_cost_usd") or 0.0) + cost
        cfg.state["trials_judged"] = int(cfg.state.get("trials_judged") or 0) + 1
        if cfg.state_path is not None:
            _persist_state(cfg.state_path, cfg.state)
    if cfg.budget_usd is not None and cfg.state.get("total_cost_usd", 0.0) >= cfg.budget_usd:
        if cfg.stop_event is not None:
            cfg.stop_event.set()
    matches = sum(1 for v in (payload.get("labels") or {}).values() if v.get("match"))
    return "judged", {"trial": str(trial), "cost_usd": cost, "n_matches": matches}


async def _sweep(root: Path, cfg: WorkerCfg) -> dict[str, Any]:
    entries = scan_root(root, tasks_root=cfg.tasks_root)
    eligible = [e for e in entries if e.get("ready_for_judging") and e.get("trajectory_kind")]
    summary = {"discovered": len(entries), "eligible": len(eligible),
               "judged": 0, "skipped": 0, "errors": 0, "errors_detail": []}
    if not eligible:
        return summary

    pending: list[asyncio.Task[Any]] = []
    for entry in eligible:
        if cfg.stop_event is not None and cfg.stop_event.is_set():
            break
        pending.append(asyncio.create_task(_process_one(entry, cfg)))
    for fut in asyncio.as_completed(pending):
        status, info = await fut
        if status == "judged":
            summary["judged"] += 1
            sys.stderr.write(
                f"[sweep] judged {Path(info['trial']).name} matches={info['n_matches']} cost=${info['cost_usd']:.4f}\n"
            )
        elif status == "skipped":
            summary["skipped"] += 1
            if cfg.state is not None:
                cfg.state["trials_skipped"] = int(cfg.state.get("trials_skipped") or 0) + 1
        else:
            summary["errors"] += 1
            summary["errors_detail"].append(info)
            sys.stderr.write(f"[sweep] ERROR {Path(info['trial']).name}: {info['error']}\n")
    if cfg.state_path is not None and cfg.state is not None:
        _persist_state(cfg.state_path, cfg.state)
    return summary


# ---------- watch loop -----------------------------------------------------------

async def _run(root: Path, cfg: WorkerCfg, *, watch: bool, watch_interval: float) -> int:
    # Build semaphores inside the running event loop. On Python 3.9, semaphores
    # built before asyncio.run() bind to a different loop, causing
    # "Future attached to a different loop" RuntimeErrors when callers wait on
    # them. Building them here avoids that.
    if not cfg.semaphores and cfg.concurrency_caps:
        cfg.semaphores = {k: asyncio.Semaphore(v) for k, v in cfg.concurrency_caps.items()}
    if cfg.stop_event is None:
        cfg.stop_event = asyncio.Event()

    def _on_signal(_signum: int, _frame: Any) -> None:
        sys.stderr.write("[judge_all] stop signal received; will exit after in-flight work\n")
        cfg.stop_event.set()

    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(s, _on_signal)
        except (ValueError, OSError):
            pass

    if not watch:
        summary = await _sweep(root, cfg)
        sys.stderr.write(f"[judge_all] done: {summary}\n")
        return 0
    sys.stderr.write(f"[judge_all] entering watch mode (interval={watch_interval}s)\n")
    cycle = 0
    while not cfg.stop_event.is_set():
        cycle += 1
        sys.stderr.write(f"[judge_all] watch cycle {cycle}\n")
        summary = await _sweep(root, cfg)
        sys.stderr.write(f"[judge_all] cycle {cycle} done: {summary}\n")
        if cfg.budget_usd is not None and (cfg.state.get("total_cost_usd") or 0.0) >= cfg.budget_usd:
            sys.stderr.write(f"[judge_all] budget cap ${cfg.budget_usd:.2f} reached; exiting\n")
            break
        try:
            await asyncio.wait_for(cfg.stop_event.wait(), timeout=watch_interval)
        except asyncio.TimeoutError:
            pass
    sys.stderr.write("[judge_all] watch loop exited\n")
    return 0


# ---------- CLI ------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sweep / watch QF-Bench failed trials.")
    p.add_argument("--root", required=True)
    p.add_argument("--tasks-root", default=None)
    p.add_argument("--judge-model", default="gpt-5")
    p.add_argument("--reasoning-effort", default="high",
                   choices=["minimal", "low", "medium", "high"])
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-tokens", type=int, default=1024)
    p.add_argument("--timeout", type=float, default=180.0)
    p.add_argument("--concurrency", type=int, default=8,
                   help="Default per-provider concurrency (overridden by per-provider flags).")
    p.add_argument("--concurrency-openai", type=int, default=None)
    p.add_argument("--concurrency-anthropic", type=int, default=None)
    p.add_argument("--concurrency-gemini", type=int, default=None)
    p.add_argument("--judge-concurrency-per-trial", type=int, default=9,
                   help="Async fan-out within one trial (across the 9 modes).")
    p.add_argument("--modes", default=None)
    p.add_argument("--bundle-max-tokens", type=int, default=80000)
    p.add_argument("--bundle-max-step-chars", type=int, default=8000)
    p.add_argument("--bundle-max-instruction-chars", type=int, default=12000)
    p.add_argument("--bundle-max-test-files", type=int, default=30)
    p.add_argument("--bundle-test-head-lines", type=int, default=80)
    p.add_argument("--include-oracle-headers", action="store_true")
    p.add_argument("--refresh-bundle", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--budget-usd", type=float, default=None,
                   help="Hard cap on cumulative judge USD spend (across the whole --root).")
    p.add_argument("--watch", action="store_true")
    p.add_argument("--watch-interval", type=float, default=60.0)
    p.add_argument("--backoff-max-attempts", type=int, default=4)
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        sys.stderr.write(f"[judge_all] root not found: {root}\n")
        return 2
    tasks_root = resolve_tasks_root(args.tasks_root, near=root)
    requested = (
        [m.strip() for m in args.modes.split(",") if m.strip()] if args.modes else list(ALL_MODES)
    )
    unknown = [m for m in requested if m not in ALL_MODES]
    if unknown:
        sys.stderr.write(f"[judge_all] unknown modes: {unknown}\n")
        return 2
    judge = JudgeCfg(
        model=args.judge_model,
        reasoning_effort=args.reasoning_effort,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
    )
    # Pass concurrency caps (ints) to WorkerCfg; the Semaphore objects are
    # constructed inside _run() under the running event loop. See WorkerCfg
    # docstring for the Python-3.9 rationale.
    concurrency_caps = {
        "openai": args.concurrency_openai or args.concurrency,
        "anthropic": args.concurrency_anthropic or args.concurrency,
        "gemini": args.concurrency_gemini or args.concurrency,
        "default": args.concurrency,
    }
    state_path = root / STATE_FILENAME
    state = _load_state(state_path)
    state.setdefault("runs", []).append({
        "started_at": time.time(),
        "judge_model": args.judge_model,
        "watch": args.watch,
    })
    cfg = WorkerCfg(
        judge=judge,
        requested_modes=requested,
        tasks_root=tasks_root,
        bundle_max_total_chars=args.bundle_max_tokens * 4,
        bundle_max_step_chars=args.bundle_max_step_chars,
        bundle_max_instruction_chars=args.bundle_max_instruction_chars,
        bundle_max_test_files=args.bundle_max_test_files,
        bundle_test_head_lines=args.bundle_test_head_lines,
        include_oracle_headers=args.include_oracle_headers,
        refresh_bundle=args.refresh_bundle,
        force=args.force,
        dry_run=args.dry_run,
        judge_concurrency_per_trial=args.judge_concurrency_per_trial,
        concurrency_caps=concurrency_caps,
        state=state,
        state_path=state_path,
        budget_usd=args.budget_usd,
        backoff_max_attempts=args.backoff_max_attempts,
    )
    if not args.dry_run and "OPENAI_API_KEY" not in os.environ and judge.model.startswith("gpt"):
        sys.stderr.write("[judge_all] WARNING: OPENAI_API_KEY not set; gpt-* judge calls will fail.\n")
    return asyncio.run(_run(root, cfg, watch=args.watch, watch_interval=args.watch_interval))


if __name__ == "__main__":
    raise SystemExit(main())
