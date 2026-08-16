"""Inference orchestrator — one CLI invocation per (model × benchmark × method) tuple.

Design contract (per TASK_18 §4.1):
- Reads benchmark JSONL streamingly (no full load into memory)
- Writes one row per question to an output JSONL with fixed schema (§4.2 of TASK_18)
- Emits a schema-version header row as first line of the output file (if new)
- Checkpoints implicitly via the output file itself: on --resume, reads existing
  question_ids from output and skips them
- Retries provider errors with exponential backoff (max 3 attempts), then writes
  a row with `error` set and moves on
- Flushes output every 10 questions (survives crashes)
- Emits <output>.summary.json at end with grand-total cost + wall time + counts

Usage:
    python3 -m _pipeline.run_inference \\
        --model claude-opus-4-7 \\
        --benchmark datasets/adversemed_500.jsonl \\
        --method verbal_probability \\
        --output inference_outputs/adversemed_500/claude-opus-4-7__verbal_probability.jsonl \\
        [--limit 500] [--resume]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import traceback
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterator

from _pipeline.elicitation import (
    ElicitationOutput,
    elicit_log_probability,
    elicit_self_consistency,
    elicit_temperature_0,
    elicit_verbal_probability,
)
from _pipeline.prompt import format_prompt
from _pipeline.providers.base import Provider
from _pipeline.secrets_helper import get_secret

SCHEMA_VERSION = "adversemed_inference_v1"

# ---------------------------------------------------------------------------
# Model + method registries
# ---------------------------------------------------------------------------

def _make_claude_opus() -> Provider:
    # Native Anthropic — unfunded as of 2026-08-01. Kept for future re-enablement.
    from _pipeline.providers.anthropic import ClaudeOpusProvider
    return ClaudeOpusProvider(get_secret("anthropic"))

def _make_claude_haiku() -> Provider:
    # Native Anthropic — unfunded as of 2026-08-01. Prefer claude-haiku-4-5-bedrock.
    from _pipeline.providers.anthropic import ClaudeHaikuProvider
    return ClaudeHaikuProvider(get_secret("anthropic"))

def _make_claude_haiku_bedrock() -> Provider:
    from _pipeline.providers.bedrock_proxy import ClaudeHaikuBedrockProvider
    return ClaudeHaikuBedrockProvider()

def _make_claude_sonnet_bedrock() -> Provider:
    # Substitutes for Claude Opus 4.7 (OSF Amendment #2)
    from _pipeline.providers.bedrock_proxy import ClaudeSonnetBedrockProvider
    return ClaudeSonnetBedrockProvider()

def _make_gpt() -> Provider:
    from _pipeline.providers.openai import GPT54MiniProvider
    return GPT54MiniProvider(get_secret("openai"))

def _make_gemini() -> Provider:
    from _pipeline.providers.google import Gemini25ProProvider
    return Gemini25ProProvider(get_secret("gemini"))

def _make_deepseek() -> Provider:
    from _pipeline.providers.deepseek import DeepSeekProvider
    return DeepSeekProvider(get_secret("deepseek"))

MODEL_REGISTRY: dict[str, Callable[[], Provider]] = {
    # Native Anthropic — unfunded 2026-08-01; kept for later re-enablement
    "claude-opus-4-7": _make_claude_opus,
    "claude-haiku-4-5": _make_claude_haiku,
    # Bedrock proxy — active path for Claude models under dad's AWS billing
    "claude-haiku-4-5-bedrock": _make_claude_haiku_bedrock,
    "claude-sonnet-4-bedrock": _make_claude_sonnet_bedrock,
    # Other providers
    "gpt-5.4-mini": _make_gpt,
    "gemini-2.5-pro": _make_gemini,
    "deepseek-chat": _make_deepseek,
}

METHOD_REGISTRY: dict[str, Callable[[Provider, str], ElicitationOutput]] = {
    "verbal_probability": elicit_verbal_probability,
    "log_probability": elicit_log_probability,
    "self_consistency": elicit_self_consistency,
    "temperature_0": elicit_temperature_0,
}

# ---------------------------------------------------------------------------
# Row I/O
# ---------------------------------------------------------------------------

def _iter_benchmark(path: Path) -> Iterator[dict]:
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def _read_completed_ids(output_path: Path) -> set[str]:
    """Read all question_ids already present in the output JSONL (for --resume)."""
    completed: set[str] = set()
    if not output_path.exists():
        return completed
    with output_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            # Skip the schema header row
            if row.get("__schema__"):
                continue
            qid = row.get("question_id")
            if qid:
                completed.add(qid)
    return completed


def _write_header_if_new(output_path: Path, run_id: str, model_id: str, method: str, benchmark: str) -> None:
    if output_path.exists() and output_path.stat().st_size > 0:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    header = {
        "__schema__": SCHEMA_VERSION,
        "run_id": run_id,
        "run_started_at": datetime.now(timezone.utc).isoformat(),
        "model_id": model_id,
        "method": method,
        "benchmark": benchmark,
    }
    with output_path.open("a") as f:
        f.write(json.dumps(header) + "\n")

# ---------------------------------------------------------------------------
# Row builder
# ---------------------------------------------------------------------------

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _build_row(
    *,
    question: dict,
    provider: Provider,
    method: str,
    elicit_out: ElicitationOutput,
    prompt: str,
    run_id: str,
    error: str | None,
) -> dict:
    """Build one output row per §4.2 schema."""
    ground_truth = question.get("ground_truth", "")
    chosen = elicit_out.chosen_answer
    correct = (chosen == ground_truth) if ground_truth else None

    # AdverseMed-500 has false_premise_category + difficulty; other benchmarks don't
    category = question.get("false_premise_category") or question.get("category")
    difficulty = question.get("difficulty")

    # Sum prompt/completion tokens across raw responses (self-consistency = many)
    prompt_tokens = sum(r.get("prompt_tokens", 0) for r in elicit_out.raw_responses)
    completion_tokens = sum(r.get("completion_tokens", 0) for r in elicit_out.raw_responses)

    # Grab a representative raw_text (last response is usually fine)
    raw_text = elicit_out.raw_responses[-1].get("raw_text", "") if elicit_out.raw_responses else ""

    return {
        "question_id": question.get("question_id", ""),
        "benchmark": question.get("benchmark_source", "unknown"),
        "model_id": provider.model_id,
        "provider_id": provider.provider_id,
        "method": method,
        "chosen_answer": chosen,
        "ground_truth": ground_truth,
        "correct": correct,
        "confidence": elicit_out.confidence,
        "category": category,
        "difficulty": difficulty,
        "prompt_sha256": _sha256(prompt),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cost_usd": elicit_out.total_cost_usd,
        "wall_ms": elicit_out.total_wall_ms,
        "n_api_calls": elicit_out.n_calls,
        "raw_text": raw_text,
        "run_id": run_id,
        "seed_index": question.get("source_seed_index"),
        "error": error,
    }


def _response_error(elicit_out: ElicitationOutput) -> str | None:
    """Surface provider errors that adapters record inside raw_responses."""
    errors = [
        str(r.get("error"))
        for r in elicit_out.raw_responses
        if r.get("error")
    ]
    if not errors:
        return None
    first = errors[0]
    if len(errors) == 1:
        return first
    return f"{first} (+{len(errors) - 1} more response errors)"


# ---------------------------------------------------------------------------
# Retry wrapper
# ---------------------------------------------------------------------------

def _with_retry(fn, *, max_attempts: int = 3) -> tuple[object, str | None]:
    """Retry fn() with exponential backoff. Return (result, error) — error is str
    on final failure, else None."""
    last_err: str | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn(), None
        except Exception as e:
            last_err = f"attempt_{attempt}: {type(e).__name__}: {str(e)[:200]}"
            if attempt == max_attempts:
                return None, last_err
            time.sleep(2 ** attempt)  # 2, 4 seconds
    return None, last_err

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def run(args: argparse.Namespace) -> int:
    benchmark_path = Path(args.benchmark)
    output_path = Path(args.output)

    if args.model not in MODEL_REGISTRY:
        print(f"Unknown model: {args.model}. Options: {sorted(MODEL_REGISTRY)}", file=sys.stderr)
        return 2
    if args.method not in METHOD_REGISTRY:
        print(f"Unknown method: {args.method}. Options: {sorted(METHOD_REGISTRY)}", file=sys.stderr)
        return 2
    if not benchmark_path.exists():
        print(f"Benchmark file not found: {benchmark_path}", file=sys.stderr)
        return 2

    provider = MODEL_REGISTRY[args.model]()
    method_fn = METHOD_REGISTRY[args.method]

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    completed = _read_completed_ids(output_path) if args.resume else set()
    if args.resume and completed:
        print(f"[resume] skipping {len(completed)} completed question_ids")

    _write_header_if_new(output_path, run_id, provider.model_id, args.method, benchmark_path.name)

    n_done = 0
    n_errors = 0
    n_parse_failures = 0
    n_not_applicable = 0
    grand_cost = 0.0
    grand_wall_ms = 0
    t_wall_start = time.perf_counter()

    with output_path.open("a") as out_f:
        for i, question in enumerate(_iter_benchmark(benchmark_path)):
            if args.limit is not None and i >= args.limit:
                break
            qid = question.get("question_id", f"row_{i}")
            if qid in completed:
                continue

            prompt = format_prompt(question["question"], question["choices"])

            elicit_out, error = _with_retry(lambda: method_fn(provider, prompt))
            if elicit_out is None:
                # Retry-exhausted failure → synthesize a placeholder ElicitationOutput
                elicit_out = ElicitationOutput(
                    method=args.method,
                    chosen_answer="parse_failure",
                    confidence=None,
                    n_calls=0,
                    total_cost_usd=0.0,
                    total_wall_ms=0,
                )
            else:
                provider_error = _response_error(elicit_out)
                if provider_error and error is None:
                    error = provider_error

            row = _build_row(
                question=question,
                provider=provider,
                method=args.method,
                elicit_out=elicit_out,
                prompt=prompt,
                run_id=run_id,
                error=error,
            )
            out_f.write(json.dumps(row) + "\n")
            n_done += 1
            if row["chosen_answer"] == "parse_failure":
                n_parse_failures += 1
            if row["chosen_answer"] == "" and row["n_api_calls"] == 0 and row["confidence"] is None:
                n_not_applicable += 1
            if row["error"]:
                n_errors += 1
            grand_cost += elicit_out.total_cost_usd
            grand_wall_ms += elicit_out.total_wall_ms

            if n_done % 10 == 0:
                out_f.flush()
                elapsed = time.perf_counter() - t_wall_start
                print(
                    f"  [{n_done:4d}] {qid} → answer={row['chosen_answer']} conf={row['confidence']} "
                    f"cost=${grand_cost:.4f} wallclock={elapsed:.0f}s errors={n_errors}"
                )

    # Summary
    summary_path = output_path.with_suffix(".summary.json")
    summary = {
        "run_id": run_id,
        "model_id": provider.model_id,
        "method": args.method,
        "benchmark": benchmark_path.name,
        "rows_written_this_run": n_done,
        "rows_previously_completed": len(completed),
        "rows_total": n_done + len(completed),
        "n_errors": n_errors,
        "n_parse_failures": n_parse_failures,
        "n_not_applicable": n_not_applicable,
        "grand_cost_usd": grand_cost,
        "grand_wall_seconds": grand_wall_ms / 1000,
        "run_ended_at": datetime.now(timezone.utc).isoformat(),
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")

    print(f"\n[run_inference] {args.model} / {args.method} on {benchmark_path.name}:")
    print(f"  rows_written_this_run={n_done} (prev={len(completed)}, total={n_done + len(completed)})")
    print(f"  errors={n_errors} · cost=${grand_cost:.4f} · wallclock={grand_wall_ms/1000:.0f}s")
    print(f"  summary → {summary_path}")

    return 1 if n_errors > 0 else 0


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run one (model × benchmark × method) inference tuple.")
    p.add_argument("--model", required=True, choices=sorted(MODEL_REGISTRY))
    p.add_argument("--benchmark", required=True, help="Path to benchmark JSONL")
    p.add_argument("--method", required=True, choices=sorted(METHOD_REGISTRY))
    p.add_argument("--output", required=True, help="Output JSONL path")
    p.add_argument("--limit", type=int, default=None, help="Only process first N rows (for smoke)")
    p.add_argument("--resume", action="store_true", help="Skip question_ids already in output")
    return p.parse_args(argv)


if __name__ == "__main__":
    try:
        raise SystemExit(run(_parse_args()))
    except KeyboardInterrupt:
        print("\n[run_inference] interrupted by user. Partial output preserved.", file=sys.stderr)
        raise SystemExit(130)
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
