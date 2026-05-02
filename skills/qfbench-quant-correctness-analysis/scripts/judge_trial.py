"""Run the 9-mode quant-correctness judge over a single QF-Bench trial.

For each enabled mode:
  - Load prompts/<mode>.md and prompts/system_judge.md from the skill.
  - Substitute placeholders with the trial bundle (built via extract_solution.py).
  - Call the judge model via litellm (default: gpt-5 with reasoning_effort=high).
  - Parse the strict-JSON response (now includes a `root_cause_class` field).
  - Aggregate into <trial>/agent/labels.json (atomic write).

Resume: if labels.json exists with a matching prompt_hash + bundle_hash and the
same set of modes, the trial is skipped unless --force is passed.

All 9 quant-correctness modes apply to BOTH multi-step and single-shot
(finance-zero) trajectories — unlike the trajectory skill, which had to skip
process-only modes for single-shot. Quant content can be judged regardless of
whether the agent produced one code blob or 100 steps.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    from extract_solution import build_bundle  # type: ignore
    from list_failed_trials import _detect_trajectory_kind, _task_name_from_result, _agent_model_from_dir  # type: ignore
    from task_context import resolve_tasks_root  # type: ignore
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from extract_solution import build_bundle  # type: ignore
    from list_failed_trials import _detect_trajectory_kind, _task_name_from_result, _agent_model_from_dir  # type: ignore
    from task_context import resolve_tasks_root  # type: ignore


SKILL_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = SKILL_ROOT / "prompts"

ALL_MODES: list[str] = [
    "wrong_model_measure",
    "missing_extra_formula_term",
    "wrong_parameterization",
    "unit_scale_error",
    "sign_convention_error",
    "time_calendar_convention",
    "data_fabrication_wrong_source",
    "numerical_optimization_failure",
    "statistical_variant_mismatch",
]

# Unlike the trajectory skill, ALL 9 quant-correctness modes apply to single-shot
# generated code. Empty set kept for API compatibility with trajectory skill scripts.
SINGLE_SHOT_INAPPLICABLE: set[str] = set()

# Approximate per-1k-token costs for budget tracking. Override via --pricing-json.
DEFAULT_PRICING: dict[str, dict[str, float]] = {
    "gpt-5": {"input": 1.25 / 1000, "output": 10.00 / 1000},
    "gpt-5-mini": {"input": 0.25 / 1000, "output": 2.00 / 1000},
    "gpt-4o": {"input": 2.50 / 1000, "output": 10.00 / 1000},
    "claude-opus-4-5": {"input": 15.00 / 1000, "output": 75.00 / 1000},
    "claude-opus-4-6": {"input": 15.00 / 1000, "output": 75.00 / 1000},
    "claude-sonnet-4-5": {"input": 3.00 / 1000, "output": 15.00 / 1000},
    "claude-sonnet-4-6": {"input": 3.00 / 1000, "output": 15.00 / 1000},
    "gemini-2.5-pro": {"input": 1.25 / 1000, "output": 10.00 / 1000},
    "gemini-2.5-flash": {"input": 0.30 / 1000, "output": 2.50 / 1000},
}


# ---------- prompt loading -------------------------------------------------------

def load_prompt(mode: str) -> str:
    p = PROMPTS_DIR / f"{mode}.md"
    if not p.is_file():
        raise FileNotFoundError(f"missing prompt file: {p}")
    return p.read_text(encoding="utf-8")


def load_system_prompt() -> str:
    return (PROMPTS_DIR / "system_judge.md").read_text(encoding="utf-8")


def _format_agent_solution(bundle: dict[str, Any]) -> str:
    """Render a single 'AGENT_SOLUTION' block combining code + output files +
    failing tests for the prompt's {{AGENT_SOLUTION}} placeholder.

    The prompts use {{AGENT_SOLUTION}} as the catch-all bundle of agent-side
    artifacts. Layout:

        ## Agent code
        <agent_code>

        ## Output files
        ### <filename>
        <truncated content>

        ## Failing tests
        - <test_name>: agent=X, expected=Y, ratio=Z
          <snippet>

        ## Trajectory (multi-step only)
        <rendered>
    """
    parts: list[str] = []
    code = bundle.get("agent_code") or ""
    if code.strip():
        parts.append(f"## Agent code\n\n```python\n{code}\n```\n")
    else:
        parts.append("## Agent code\n[empty — agent did not generate runnable code]\n")
    output_files = bundle.get("output_files") or {}
    if output_files:
        parts.append("## Output files\n")
        for fn, content in sorted(output_files.items()):
            parts.append(f"### `{fn}`\n```\n{content}\n```\n")
    else:
        parts.append("## Output files\n[no output files produced]\n")
    failing = bundle.get("failing_tests") or []
    if failing:
        parts.append("## Failing tests (from verifier/test-stdout.txt)\n")
        for ft in failing:
            line = f"- **{ft.get('test_name')}**"
            av = ft.get("agent_value")
            ev = ft.get("expected_value")
            r = ft.get("ratio")
            if av is not None or ev is not None:
                line += f": agent={av!r}, expected={ev!r}"
            if r is not None:
                line += f", ratio={r:.4g}"
            parts.append(line)
            snippet = ft.get("snippet")
            if snippet:
                parts.append(f"  ```\n  {snippet}\n  ```")
        parts.append("")
    else:
        parts.append("## Failing tests\n[failing-test parser found no entries; check raw verifier/test-stdout.txt]\n")
    traj = bundle.get("trajectory_text") or ""
    if traj.strip() and bundle.get("trajectory_kind") != "finance-zero":
        parts.append("## Trajectory (multi-step rendering)\n\n" + traj)
    return "\n".join(parts)


def fill_placeholders(prompt: str, bundle: dict[str, Any]) -> str:
    ctx = bundle.get("task_context") or {}
    instr = ctx.get("instruction_md") or "[task instruction not available]"
    digest_lines: list[str] = []
    for d in ctx.get("tests_digest", []):
        digest_lines.append(f"### {d.get('path')} ({d.get('lines')} lines, truncated={d.get('truncated')})\n")
        digest_lines.append(d.get("head", ""))
        digest_lines.append("\n")
    tests_digest = "".join(digest_lines) if digest_lines else "[no tests digest available]"
    agent_solution = _format_agent_solution(bundle)
    out = prompt
    out = out.replace("{{TRAJECTORY_KIND}}", bundle.get("trajectory_kind") or "unknown")
    out = out.replace("{{TASK_INSTRUCTION_MD}}", instr)
    out = out.replace("{{TASK_TESTS_DIGEST}}", tests_digest)
    out = out.replace("{{AGENT_SOLUTION}}", agent_solution)
    # Backwards-compat alias if any prompt still uses {{TRAJECTORY}}.
    out = out.replace("{{TRAJECTORY}}", bundle.get("trajectory_text") or agent_solution)
    return out


def prompt_set_hash() -> str:
    h = hashlib.sha256()
    for name in ["system_judge.md", *(f"{m}.md" for m in ALL_MODES)]:
        p = PROMPTS_DIR / name
        h.update(name.encode("utf-8"))
        h.update(b"\x00")
        h.update(p.read_bytes())
        h.update(b"\x00")
    return h.hexdigest()


# ---------- response parsing -----------------------------------------------------

JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        first_nl = text.find("\n")
        text = text[first_nl + 1 :] if first_nl != -1 else text
        if text.endswith("```"):
            text = text[: -3]
    return text.strip()


def parse_judge_response(raw: str) -> dict[str, Any]:
    """Robust JSON parser. Returns a dict with 'ok' boolean and either the parsed
    fields or an error string."""
    text = _strip_code_fence(raw)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        m = JSON_BLOCK_RE.search(text)
        if not m:
            return {"ok": False, "error": "no JSON object found", "raw": raw[:400]}
        try:
            data = json.loads(m.group(0))
        except json.JSONDecodeError as exc:
            return {"ok": False, "error": f"json decode failed: {exc}", "raw": raw[:400]}
    if not isinstance(data, dict):
        return {"ok": False, "error": "top-level not an object", "raw": raw[:400]}
    rcc_raw = data.get("root_cause_class")
    rcc: Optional[str] = None
    if isinstance(rcc_raw, str):
        rcc_clean = rcc_raw.strip().lower()
        if rcc_clean in {"agent_conceptual", "agent_coding", "task_side"}:
            rcc = rcc_clean
        elif rcc_clean in {"", "null", "none"}:
            rcc = None
    out = {
        "ok": True,
        "match": bool(data.get("match", False)),
        "evidence_step_ids": list(data.get("evidence_step_ids") or []),
        "quote": str(data.get("quote") or ""),
        "confidence": float(data.get("confidence") or 0.0),
        "root_cause_class": rcc,
        "notes": str(data.get("notes") or ""),
    }
    return out


# ---------- litellm call ---------------------------------------------------------

@dataclass
class JudgeCfg:
    model: str
    reasoning_effort: str = "high"
    # Bumped from 1024 → 2048 after the May 2026 calibration found that with the
    # strengthened Case-2 system prompt, opus-4.6 sometimes produces 400-1000 chars
    # of preamble reasoning before emitting the JSON object. 2048 gives the model
    # enough budget to reason AND produce JSON; the prompt also now warns that
    # any non-JSON preamble fails the contract.
    temperature: float = 0.0
    max_tokens: int = 2048
    timeout: float = 180.0
    pricing: dict[str, dict[str, float]] = field(default_factory=lambda: dict(DEFAULT_PRICING))


def _pricing_for(cfg: JudgeCfg) -> Optional[dict[str, float]]:
    name = cfg.model
    if name in cfg.pricing:
        return cfg.pricing[name]
    for k, v in cfg.pricing.items():
        if k in name:
            return v
    return None


async def acomplete_judge(
    cfg: JudgeCfg,
    system_prompt: str,
    user_prompt: str,
) -> dict[str, Any]:
    """Single async judge call. Returns {ok, content, usage, cost_usd, raw}."""
    try:
        import litellm  # type: ignore
    except ImportError:
        return {"ok": False, "error": "litellm not installed", "content": None, "usage": None, "cost_usd": 0.0}
    kwargs: dict[str, Any] = {
        "model": cfg.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": cfg.temperature,
        "max_tokens": cfg.max_tokens,
        "timeout": cfg.timeout,
    }
    if cfg.reasoning_effort and cfg.model.startswith(("gpt-5", "o1", "o3", "o4")):
        kwargs["reasoning_effort"] = cfg.reasoning_effort
    try:
        resp = await litellm.acompletion(**kwargs)
    except Exception as exc:  # litellm raises a wide range of exceptions
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "content": None, "usage": None, "cost_usd": 0.0}
    content = resp.choices[0].message.content if resp.choices else ""
    usage = getattr(resp, "usage", None)
    if usage is not None and not isinstance(usage, dict):
        usage = {
            "prompt_tokens": getattr(usage, "prompt_tokens", None),
            "completion_tokens": getattr(usage, "completion_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
        }
    cost = 0.0
    p = _pricing_for(cfg)
    if usage and p:
        cost = (usage.get("prompt_tokens") or 0) * p["input"] / 1000 + (
            usage.get("completion_tokens") or 0
        ) * p["output"] / 1000
    return {"ok": True, "content": content, "usage": usage, "cost_usd": cost, "raw": str(content)[:2000]}


# ---------- judging a trial ------------------------------------------------------

@dataclass
class TrialPaths:
    trial: Path
    bundle: Path
    labels: Path


def _trial_paths(trial: Path) -> TrialPaths:
    return TrialPaths(
        trial=trial,
        bundle=trial / "agent" / "bundle.json",
        labels=trial / "agent" / "labels.json",
    )


def _load_or_build_bundle(
    trial: Path,
    *,
    trajectory_kind: Optional[str],
    task_name: Optional[str],
    tasks_root: Optional[Path],
    max_total_chars: int,
    max_step_chars: int,
    max_instruction_chars: int,
    max_test_files: int,
    test_head_lines: int,
    include_oracle_headers: bool,
    refresh: bool,
) -> dict[str, Any]:
    paths = _trial_paths(trial)
    if paths.bundle.is_file() and not refresh:
        return json.loads(paths.bundle.read_text(encoding="utf-8"))
    agent_dir = trial / "agent"
    kind, traj_path = _detect_trajectory_kind(agent_dir)
    if trajectory_kind:
        kind = trajectory_kind
    result_json = trial / "result.json"
    tn = task_name or (
        _task_name_from_result(result_json) if result_json.is_file() else None
    )
    if tn is None or kind is None or traj_path is None:
        raise RuntimeError(f"could not detect kind/task for trial {trial}")
    combo = trial.parent.parent.name
    agent, model = _agent_model_from_dir(combo)
    bundle = build_bundle(
        trial_path=trial,
        trajectory_path=traj_path,
        trajectory_kind=kind,
        task_name=tn,
        agent_harness=agent,
        model=model,
        tasks_root=tasks_root,
        max_total_chars=max_total_chars,
        max_step_chars=max_step_chars,
        max_instruction_chars=max_instruction_chars,
        max_test_files=max_test_files,
        test_head_lines=test_head_lines,
        include_oracle_headers=include_oracle_headers,
    )
    paths.bundle.parent.mkdir(parents=True, exist_ok=True)
    tmp = paths.bundle.with_suffix(paths.bundle.suffix + ".tmp")
    tmp.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(paths.bundle)
    return bundle


def _can_skip(
    labels_path: Path,
    *,
    bundle_hash: str,
    prompt_hash: str,
    judge_model: str,
    requested_modes: list[str],
) -> bool:
    if not labels_path.is_file():
        return False
    try:
        cached = json.loads(labels_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if cached.get("bundle_hash") != bundle_hash:
        return False
    if cached.get("prompt_hash") != prompt_hash:
        return False
    if cached.get("judge_model") != judge_model:
        return False
    cached_modes = set((cached.get("labels") or {}).keys())
    return set(requested_modes).issubset(cached_modes)


def applicable_modes(trajectory_kind: str, requested: list[str]) -> list[str]:
    base = list(requested) if requested else list(ALL_MODES)
    if trajectory_kind == "finance-zero":
        return [m for m in base if m not in SINGLE_SHOT_INAPPLICABLE]
    return base


# Pre-flight gate: detect cases where there is literally nothing to evaluate
# against the 9 quant-correctness rubrics, deterministically, before paying for
# any LLM calls. Three findings from the 50-trial validation drove this:
#
#   1. Finance-zero trials whose generated code is empty / a stub burn ~$15+
#      having the LLM independently re-discover "no signal here" 9 times.
#   2. Multi-step trials whose code crashed before producing outputs land at
#      the same insufficient-solution state and waste the same 9 LLM calls.
#   3. The system prompt's "insufficient solution handling: case 1" already
#      tells the judge to bail out — the gate just enforces this without an
#      LLM round-trip.
#
# The gate is intentionally conservative: it ONLY short-circuits Case 1
# ("empty / trivially short generation"). Case 2 ("code present but no
# outputs") still goes through the LLM because the code's intent is often
# classifiable (A1/A2/A3 from inspection of the formula).
#
# `_INSUFFICIENT_CODE_CHARS_THRESHOLD` is the cutoff for "trivially short" code
# in non-whitespace characters. Calibrated empirically from the 50-trial
# validation: finance-zero stubs that produced no useful work clocked in at
# 200-450 chars (just imports + config constants + an unfinished function
# signature). Real quant solutions for QF-Bench tasks routinely exceed 2000
# chars. A 500-char cutoff catches the truncated-stub pattern with no
# observed false positives in the 50-trial set.
_INSUFFICIENT_CODE_CHARS_THRESHOLD = 500


def _check_insufficient_solution(bundle: dict[str, Any]) -> tuple[bool, str]:
    """Decide whether the bundle has enough signal to run the 9 rubrics.

    Returns (insufficient, reason). When `insufficient=True`, the caller should
    skip the LLM round-trips and emit a deterministic match=false label across
    all modes with `reason` recorded in `notes`.

    Conservative criteria — only fire on Case 1 of the system_judge prompt's
    insufficient-solution guidance:

      A. Agent code is empty or under the trivially-short threshold AND the
         agent has not surfaced any other classifiable signal (no output files,
         no failing-test numerical comparisons).

    Case 2 (code present, no outputs) intentionally falls through to the LLM
    because the code's intent is often classifiable from line-level inspection.
    """
    code = bundle.get("agent_code") or ""
    code_chars = len(code.strip())
    output_files = bundle.get("output_files") or {}
    failing_tests = bundle.get("failing_tests") or []
    n_tests_with_values = sum(
        1 for t in failing_tests
        if t.get("agent_value") is not None and (
            t.get("expected_value") is not None
            or t.get("expected_lo") is not None
            or t.get("expected_hi") is not None
        )
    )

    if code_chars < _INSUFFICIENT_CODE_CHARS_THRESHOLD and not output_files and n_tests_with_values == 0:
        return (
            True,
            f"Insufficient solution (pre-flight gate): agent_code has {code_chars} "
            f"non-whitespace chars (< threshold {_INSUFFICIENT_CODE_CHARS_THRESHOLD}), "
            f"no output files produced, no failing tests with numerical comparisons. "
            f"This is a trajectory/premature-termination failure (see "
            f"qfbench-trajectory-error-analysis), not a quant-content failure. "
            f"All 9 modes auto-labeled match=false, deterministic; no LLM call made.",
        )
    return False, ""


def _build_insufficient_labels(modes: list[str], reason: str) -> dict[str, dict[str, Any]]:
    """Synthesize a labels dict for an insufficient-solution short-circuit.

    Each mode gets `gate_skipped=true` so downstream aggregators can distinguish
    deterministic gate misses from genuine LLM-judged misses (otherwise the
    aggregator would treat them as real "no match" signal, inflating the
    "agent's solution was sound on this axis" count).
    """
    return {
        mode: {
            "ok": True,
            "match": False,
            "evidence_step_ids": [0],
            "quote": "",
            "confidence": 1.0,
            "root_cause_class": None,
            "notes": reason,
            "gate_skipped": True,
            "usage": None,
            "cost_usd": 0.0,
        }
        for mode in modes
    }


async def judge_trial(
    trial: Path,
    cfg: JudgeCfg,
    *,
    requested_modes: list[str],
    bundle: dict[str, Any],
    concurrency: int = 9,
    dry_run: bool = False,
) -> dict[str, Any]:
    system = load_system_prompt()
    p_hash = prompt_set_hash()
    bundle_hash = bundle["bundle_hash"]
    kind = bundle["trajectory_kind"]
    modes = applicable_modes(kind, requested_modes)
    if not modes:
        return {
            "ok": True,
            "skipped_reason": "no applicable modes",
            "labels": {},
            "bundle_hash": bundle_hash,
            "prompt_hash": p_hash,
            "judge_model": cfg.model,
        }
    # Pre-flight gate: bail out cheaply on Case 1 (empty / trivial code).
    # Skip in dry-run mode so the dry-run path still exercises the prompts.
    if not dry_run:
        insufficient, reason = _check_insufficient_solution(bundle)
        if insufficient:
            return {
                "ok": True,
                "labels": _build_insufficient_labels(modes, reason),
                "bundle_hash": bundle_hash,
                "prompt_hash": p_hash,
                "task_context_hash": (bundle.get("task_context") or {}).get("content_hash"),
                "judge_model": cfg.model,
                "judge_reasoning_effort": cfg.reasoning_effort,
                "trajectory_kind": kind,
                "task_name": bundle["task_name"],
                "agent_harness": bundle["agent_harness"],
                "model": bundle["model"],
                "trial_path": bundle["trial_path"],
                "judged_at": time.time(),
                "total_cost_usd": 0.0,
                "gate_skipped": True,
                "gate_reason": reason,
            }

    sem = asyncio.Semaphore(concurrency)
    results: dict[str, Any] = {}
    total_cost = 0.0

    async def run_one(mode: str) -> None:
        nonlocal total_cost
        prompt = fill_placeholders(load_prompt(mode), bundle)
        if dry_run:
            results[mode] = {
                "ok": True,
                "match": False,
                "evidence_step_ids": [],
                "quote": "",
                "confidence": 0.0,
                "notes": "dry-run",
                "judge_raw": prompt[:400] + "...",
                "usage": None,
                "cost_usd": 0.0,
            }
            return
        async with sem:
            r = await acomplete_judge(cfg, system, prompt)
        if not r.get("ok"):
            results[mode] = {
                "ok": False,
                "error": r.get("error"),
                "match": False,
                "evidence_step_ids": [],
                "quote": "",
                "confidence": 0.0,
                "notes": "judge call failed",
                "usage": r.get("usage"),
                "cost_usd": r.get("cost_usd", 0.0),
            }
            total_cost += r.get("cost_usd", 0.0)
            return
        parsed = parse_judge_response(r["content"] or "")
        if not parsed.get("ok"):
            results[mode] = {
                "ok": False,
                "error": parsed.get("error"),
                "match": False,
                "evidence_step_ids": [],
                "quote": "",
                "confidence": 0.0,
                "notes": "judge JSON parse failed",
                "judge_raw": parsed.get("raw"),
                "usage": r.get("usage"),
                "cost_usd": r.get("cost_usd", 0.0),
            }
            total_cost += r.get("cost_usd", 0.0)
            return
        results[mode] = {
            "ok": True,
            "match": parsed["match"],
            "evidence_step_ids": parsed["evidence_step_ids"],
            "quote": parsed["quote"],
            "confidence": parsed["confidence"],
            "root_cause_class": parsed.get("root_cause_class"),
            "notes": parsed["notes"],
            "usage": r.get("usage"),
            "cost_usd": r.get("cost_usd", 0.0),
        }
        total_cost += r.get("cost_usd", 0.0)

    await asyncio.gather(*(run_one(m) for m in modes))
    return {
        "ok": True,
        "labels": results,
        "bundle_hash": bundle_hash,
        "prompt_hash": p_hash,
        "task_context_hash": (bundle.get("task_context") or {}).get("content_hash"),
        "judge_model": cfg.model,
        "judge_reasoning_effort": cfg.reasoning_effort,
        "trajectory_kind": kind,
        "task_name": bundle["task_name"],
        "agent_harness": bundle["agent_harness"],
        "model": bundle["model"],
        "trial_path": bundle["trial_path"],
        "judged_at": time.time(),
        "total_cost_usd": total_cost,
    }


def write_labels_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


# ---------- CLI ------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Judge a single QF-Bench trial across the 9 failure modes.")
    p.add_argument("--trial", required=True)
    p.add_argument("--judge-model", default="gpt-5")
    p.add_argument("--reasoning-effort", default="high", choices=["minimal", "low", "medium", "high"])
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-tokens", type=int, default=1024)
    p.add_argument("--timeout", type=float, default=180.0)
    p.add_argument("--concurrency", type=int, default=9)
    p.add_argument("--modes", default=None,
                   help="Comma-separated subset of modes to judge.")
    p.add_argument("--tasks-root", default=None)
    p.add_argument("--bundle-max-tokens", type=int, default=80000)
    p.add_argument("--bundle-max-step-chars", type=int, default=8000)
    p.add_argument("--bundle-max-instruction-chars", type=int, default=12000)
    p.add_argument("--bundle-max-test-files", type=int, default=30)
    p.add_argument("--bundle-test-head-lines", type=int, default=80)
    p.add_argument("--include-oracle-headers", action="store_true")
    p.add_argument("--refresh-bundle", action="store_true")
    p.add_argument("--force", action="store_true",
                   help="Rejudge even when labels.json is already up to date.")
    p.add_argument("--dry-run", action="store_true",
                   help="Build bundle and prompts without calling the LLM.")
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    trial = Path(args.trial).expanduser().resolve()
    if not trial.is_dir():
        sys.stderr.write(f"[judge_trial] trial dir not found: {trial}\n")
        return 2
    tasks_root = resolve_tasks_root(args.tasks_root, near=trial)
    requested = (
        [m.strip() for m in args.modes.split(",") if m.strip()] if args.modes else list(ALL_MODES)
    )
    unknown = [m for m in requested if m not in ALL_MODES]
    if unknown:
        sys.stderr.write(f"[judge_trial] unknown modes: {unknown}\n")
        return 2
    bundle = _load_or_build_bundle(
        trial,
        trajectory_kind=None,
        task_name=None,
        tasks_root=tasks_root,
        max_total_chars=args.bundle_max_tokens * 4,
        max_step_chars=args.bundle_max_step_chars,
        max_instruction_chars=args.bundle_max_instruction_chars,
        max_test_files=args.bundle_max_test_files,
        test_head_lines=args.bundle_test_head_lines,
        include_oracle_headers=args.include_oracle_headers,
        refresh=args.refresh_bundle,
    )
    paths = _trial_paths(trial)
    p_hash = prompt_set_hash()
    if not args.force and not args.dry_run and _can_skip(
        paths.labels,
        bundle_hash=bundle["bundle_hash"],
        prompt_hash=p_hash,
        judge_model=args.judge_model,
        requested_modes=applicable_modes(bundle["trajectory_kind"], requested),
    ):
        sys.stderr.write(f"[judge_trial] up-to-date, skipping {trial}\n")
        return 0
    cfg = JudgeCfg(
        model=args.judge_model,
        reasoning_effort=args.reasoning_effort,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
    )
    if not args.dry_run and "OPENAI_API_KEY" not in os.environ and cfg.model.startswith("gpt"):
        sys.stderr.write("[judge_trial] WARNING: OPENAI_API_KEY not set; the judge call will fail.\n")
    payload = asyncio.run(
        judge_trial(
            trial,
            cfg,
            requested_modes=requested,
            bundle=bundle,
            concurrency=args.concurrency,
            dry_run=args.dry_run,
        )
    )
    write_labels_atomic(paths.labels, payload)
    n_match = sum(1 for v in (payload.get("labels") or {}).values() if v.get("match"))
    sys.stderr.write(
        f"[judge_trial] judged {trial.name} kind={bundle['trajectory_kind']} "
        f"modes={len(payload.get('labels') or {})} matches={n_match} "
        f"cost=${payload.get('total_cost_usd', 0.0):.4f} → {paths.labels}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
