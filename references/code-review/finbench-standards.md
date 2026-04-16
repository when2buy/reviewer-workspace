# Finbench Project Standards

Standards specific to the finance-bench project. Apply these on top of the general checklist.

## What This Project Does

finance-bench is a **state-aware financial agent benchmark**. It:
- Presents financial scenarios to AI agents
- Tracks agent state across multi-turn interactions
- Evaluates agent responses for correctness and quality
- Produces benchmark scores for comparison

Two things matter above all else:
1. **Evaluation logic must be deterministic** — same input → same score, always
2. **State tracking must be accurate** — agent context must not leak between tasks

## Evaluation Logic Rules

- Scoring functions must be pure (no side effects, no randomness)
- Any use of LLMs in evaluation must have fixed seeds where possible
- Grade boundaries must be explicit and documented
- If "partial credit" exists, the rubric must be explicit, not vibes-based
- Never silently drop failed evaluations — log and count them

## State Management Rules

- Agent state must be completely reset between benchmark tasks (unless testing continuity)
- No shared mutable state between concurrent evaluation runs
- State serialization must be lossless (don't lose precision on round-trip)
- Log enough state to reproduce any result from the log alone

## Data Integrity Rules

- Financial figures in test cases: store as strings or Decimal, never float
- Date references: must include timezone (UTC preferred)
- Don't mutate test case data during evaluation — copy if you need to transform

## Testing Rules

- Every scoring function needs a test with:
  - At least one full-credit case
  - At least one zero-credit case
  - At least one edge case (empty answer, None, malformed)
- Benchmark results must be reproducible from saved state alone

## Infrastructure Rules

- Long-running evals run in tmux on finance-bench-v3 (159.65.5.105)
- Results go to the results/ directory
- Always log to a file, not just stdout
- Check disk space before starting a long eval run
