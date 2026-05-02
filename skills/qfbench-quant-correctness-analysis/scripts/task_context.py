"""Resolve a QF-Bench task_name to its task folder and emit a compact context bundle.

A QF-Bench task folder is expected at <tasks_root>/<task_name>/ and typically
contains:

    instruction.md            (canonical agent instruction; required if present)
    tests/                    (unit tests run by the verifier)
    solution/  or oracle/     (reference solution; optional)
    task.yaml                 (optional metadata)
    data/                     (optional)

Resolution order for tasks_root:
    1. --tasks-root flag
    2. QFBENCH_TASKS_ROOT environment variable
    3. sibling ../QuantitativeFinance-Bench/tasks of the trial workspace
    4. sibling ../qf-bench/tasks of the trial workspace

Outputs a JSON object with keys:
    task_name, tasks_root, resolved_path, found,
    instruction_md, instruction_md_path, instruction_md_truncated,
    tests_digest [{path, head, lines, truncated}], tests_root,
    oracle_summary (only if --include-oracle-headers),
    content_hash (sha256 over the canonical content)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Optional


# ---------- candidate resolution -------------------------------------------------

def _candidate_roots(explicit: Optional[str], near: Optional[Path]) -> list[Path]:
    cands: list[Path] = []
    if explicit:
        cands.append(Path(explicit).expanduser())
    env = os.environ.get("QFBENCH_TASKS_ROOT")
    if env:
        cands.append(Path(env).expanduser())
    if near is not None:
        near = near.resolve()
        for parent in [near, *near.parents]:
            cands.append(parent / "QuantitativeFinance-Bench" / "tasks")
            cands.append(parent / "qf-bench" / "tasks")
            if parent.parent == parent:
                break
    seen: set[Path] = set()
    out: list[Path] = []
    for c in cands:
        c = c.expanduser()
        try:
            c = c.resolve()
        except OSError:
            pass
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def resolve_tasks_root(
    explicit: Optional[str], near: Optional[Path] = None
) -> Optional[Path]:
    for c in _candidate_roots(explicit, near):
        if c.is_dir():
            return c
    return None


# ---------- task folder content loading ------------------------------------------

_TEST_FILE_GLOBS = ["**/*.py", "**/*.sh", "**/*.json", "**/*.yaml", "**/*.yml", "**/*.txt"]


def _load_instruction_md(task_dir: Path, max_chars: int) -> tuple[Optional[str], Optional[str], bool]:
    """Return (text, path, truncated)."""
    candidate_names = ["instruction.md", "instructions.md", "INSTRUCTION.md", "task.md", "README.md"]
    for name in candidate_names:
        p = task_dir / name
        if p.is_file():
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            truncated = False
            if len(text) > max_chars:
                text = text[:max_chars] + "\n\n[... truncated by task_context.py ...]"
                truncated = True
            return text, str(p), truncated
    return None, None, False


def _enumerate_tests(task_dir: Path, max_files: int, head_lines: int) -> tuple[list[dict[str, Any]], Optional[str]]:
    tests_dir = None
    for cand in ("tests", "test", "verification", "verifier"):
        p = task_dir / cand
        if p.is_dir():
            tests_dir = p
            break
    if tests_dir is None:
        return [], None
    files: list[Path] = []
    for pattern in _TEST_FILE_GLOBS:
        files.extend(tests_dir.glob(pattern))
    files = sorted({f for f in files if f.is_file()})
    digest: list[dict[str, Any]] = []
    for f in files[:max_files]:
        try:
            with f.open("r", encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
        except OSError:
            continue
        truncated = len(lines) > head_lines
        head = "".join(lines[:head_lines])
        digest.append(
            {
                "path": str(f.relative_to(task_dir)),
                "lines": len(lines),
                "truncated": truncated,
                "head": head,
            }
        )
    return digest, str(tests_dir.relative_to(task_dir))


_DEF_PATTERN = re.compile(r"^\s*(def|class)\s+\w+.*:\s*$", re.MULTILINE)


def _oracle_summary(task_dir: Path, max_chars: int) -> Optional[str]:
    for cand in ("solution", "oracle", "sample_solution", "reference"):
        d = task_dir / cand
        if d.is_dir():
            sigs: list[str] = []
            for f in sorted(d.rglob("*.py")):
                try:
                    text = f.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                rel = f.relative_to(task_dir)
                hits = _DEF_PATTERN.findall(text)
                lines = [m.group(0) for m in _DEF_PATTERN.finditer(text)]
                if not lines:
                    continue
                sigs.append(f"# {rel}")
                sigs.extend(lines)
                if sum(len(s) for s in sigs) > max_chars:
                    break
            if sigs:
                joined = "\n".join(sigs)
                if len(joined) > max_chars:
                    joined = joined[:max_chars] + "\n# [... truncated ...]"
                return joined
    return None


# ---------- public API -----------------------------------------------------------

def build_context(
    task_name: str,
    tasks_root: Optional[Path],
    *,
    max_instruction_chars: int = 12000,
    max_test_files: int = 30,
    test_head_lines: int = 80,
    include_oracle_headers: bool = False,
    max_oracle_chars: int = 4000,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "task_name": task_name,
        "tasks_root": str(tasks_root) if tasks_root else None,
        "resolved_path": None,
        "found": False,
        "instruction_md": None,
        "instruction_md_path": None,
        "instruction_md_truncated": False,
        "tests_root": None,
        "tests_digest": [],
        "oracle_summary": None,
    }
    if tasks_root is None:
        out["content_hash"] = _hash_payload(out)
        return out
    task_dir = tasks_root / task_name
    if not task_dir.is_dir():
        out["content_hash"] = _hash_payload(out)
        return out
    out["resolved_path"] = str(task_dir)
    out["found"] = True
    instr, instr_path, truncated = _load_instruction_md(task_dir, max_instruction_chars)
    out["instruction_md"] = instr
    out["instruction_md_path"] = instr_path
    out["instruction_md_truncated"] = truncated
    digest, tests_root = _enumerate_tests(task_dir, max_test_files, test_head_lines)
    out["tests_digest"] = digest
    out["tests_root"] = tests_root
    if include_oracle_headers:
        out["oracle_summary"] = _oracle_summary(task_dir, max_oracle_chars)
    out["content_hash"] = _hash_payload(out)
    return out


def _hash_payload(ctx: dict[str, Any]) -> str:
    payload = {
        "task_name": ctx.get("task_name"),
        "found": ctx.get("found"),
        "instruction_md": ctx.get("instruction_md"),
        "instruction_md_path": ctx.get("instruction_md_path"),
        "tests_root": ctx.get("tests_root"),
        "tests_digest": [
            {
                "path": d.get("path"),
                "lines": d.get("lines"),
                "truncated": d.get("truncated"),
                "head": d.get("head"),
            }
            for d in ctx.get("tests_digest", [])
        ],
        "oracle_summary": ctx.get("oracle_summary"),
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


# ---------- CLI ------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Resolve a QF-Bench task and emit context JSON.")
    p.add_argument("--task-name", required=True)
    p.add_argument("--tasks-root", default=None, help="Path to <repo>/tasks; falls back to QFBENCH_TASKS_ROOT.")
    p.add_argument("--near", default=None, help="A path near the trial; used to look for sibling tasks roots.")
    p.add_argument("--max-instruction-chars", type=int, default=12000)
    p.add_argument("--max-test-files", type=int, default=30)
    p.add_argument("--test-head-lines", type=int, default=80)
    p.add_argument("--include-oracle-headers", action="store_true")
    p.add_argument("--max-oracle-chars", type=int, default=4000)
    p.add_argument("--out", default=None, help="Output JSON path; default stdout.")
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    near = Path(args.near).expanduser() if args.near else None
    root = resolve_tasks_root(args.tasks_root, near)
    if root is None and (args.tasks_root or os.environ.get("QFBENCH_TASKS_ROOT")):
        sys.stderr.write(
            "[task_context] WARNING: tasks-root could not be resolved; emitting degraded context.\n"
        )
    ctx = build_context(
        args.task_name,
        root,
        max_instruction_chars=args.max_instruction_chars,
        max_test_files=args.max_test_files,
        test_head_lines=args.test_head_lines,
        include_oracle_headers=args.include_oracle_headers,
        max_oracle_chars=args.max_oracle_chars,
    )
    serialized = json.dumps(ctx, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(serialized, encoding="utf-8")
    else:
        sys.stdout.write(serialized + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
