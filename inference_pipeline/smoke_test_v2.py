"""Smoke test v2 — 5 questions × 5 models × 4 methods on AdverseMed-500.

Drives run_inference.py under the hood (validates the orchestrator itself).
Total: 5 × 5 × 4 = 100 API calls, ~$0.50, ~5 minutes.

Emits both stdout summary AND a persistent report at
inference_outputs/smoke_v2_<ts>/report.md with per-model / per-method
breakdown + cost projection for the full 500-row run.

Usage (from papers/paper-1-medllm-calibration/):
    source .venv/bin/activate
    python3 -m _pipeline.smoke_test_v2
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
BENCHMARK = REPO_ROOT / "datasets" / "adversemed_500.jsonl"
SMOKE_ROOT = REPO_ROOT / "inference_outputs" / f"smoke_v2_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"

MODELS = [
    "deepseek-chat",       # cheapest first
    "claude-haiku-4-5",
    "gpt-5.4-mini",
    "gemini-2.5-pro",
    "claude-opus-4-7",     # most expensive last
]
# Note: Bedrock variants (`claude-haiku-4-5-bedrock`, `claude-sonnet-4-bedrock`)
# remain registered in run_inference.py as backup infrastructure if Anthropic
# access fails mid-run. Not used for the pre-registered comparative audit.
METHODS = [
    "verbal_probability",
    "log_probability",
    "self_consistency",
    "temperature_0",
]
N_QUESTIONS = 5


def _run_one(model: str, method: str) -> dict:
    output = SMOKE_ROOT / f"{model}__{method}.jsonl"
    cmd = [
        sys.executable, "-m", "_pipeline.run_inference",
        "--model", model,
        "--method", method,
        "--benchmark", str(BENCHMARK),
        "--output", str(output),
        "--limit", str(N_QUESTIONS),
    ]
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    wall = time.perf_counter() - t0

    summary_path = output.with_suffix(".summary.json")
    if summary_path.exists():
        summary = json.loads(summary_path.read_text())
    else:
        summary = {"rows_total": 0, "n_errors": 0, "grand_cost_usd": 0.0}
    sample_errors: list[str] = []
    if output.exists():
        with output.open() as f:
            for line in f:
                row = json.loads(line)
                if row.get("__schema__"):
                    continue
                if row.get("error"):
                    sample_errors.append(f"{row.get('question_id')}: {row['error'][:300]}")
                elif row.get("chosen_answer") == "parse_failure":
                    sample_errors.append(
                        f"{row.get('question_id')}: parse_failure raw={row.get('raw_text', '')[:120]!r}"
                    )
                if len(sample_errors) >= 3:
                    break

    return {
        "model": model,
        "method": method,
        "exit_code": proc.returncode,
        "wall_seconds": wall,
        "cost_usd": summary.get("grand_cost_usd", 0.0),
        "rows": summary.get("rows_total", 0),
        "errors": summary.get("n_errors", 0),
        "parse_failures": summary.get("n_parse_failures", 0),
        "not_applicable": summary.get("n_not_applicable", 0),
        "stdout_tail": proc.stdout.splitlines()[-3:] if proc.stdout else [],
        "stderr_tail": proc.stderr.splitlines()[-3:] if proc.stderr else [],
        "sample_errors": sample_errors,
    }


def _write_report(results: list[dict]) -> Path:
    report_path = SMOKE_ROOT / "report.md"

    total_cost = sum(r["cost_usd"] for r in results)
    total_wall = sum(r["wall_seconds"] for r in results)
    total_errors = sum(r["errors"] for r in results)
    total_parse_failures = sum(r["parse_failures"] for r in results)
    total_not_applicable = sum(r["not_applicable"] for r in results)

    projections: dict[str, float] = {}
    for r in results:
        if r["rows"] > 0:
            per_row = r["cost_usd"] / r["rows"]
            projections[f"{r['model']}__{r['method']}"] = per_row * 500

    grand_projection = sum(projections.values())

    per_model_cost: dict[str, float] = {}
    for r in results:
        per_model_cost[r["model"]] = per_model_cost.get(r["model"], 0.0) + r["cost_usd"]

    lines: list[str] = []
    lines.append(f"# Smoke test v2 report — {SMOKE_ROOT.name}\n")
    lines.append(
        f"**Total:** {len(results)} runs · ${total_cost:.4f} · {total_wall:.0f}s · "
        f"{total_errors} errors · {total_parse_failures} parse failures · "
        f"{total_not_applicable} structural N/A rows"
    )
    lines.append(f"\n**Projected full 500-row × 4-method × 5-model cost:** ${grand_projection:.2f}\n")

    lines.append("## Per (model × method) results\n")
    lines.append("| Model | Method | Rows | Cost | Wallclock | Errors | Parse failures | N/A | Exit |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in results:
        lines.append(
            f"| {r['model']} | {r['method']} | {r['rows']} | ${r['cost_usd']:.4f} "
            f"| {r['wall_seconds']:.1f}s | {r['errors']} | {r['parse_failures']} "
            f"| {r['not_applicable']} | {r['exit_code']} |"
        )

    lines.append("\n## Per-model total smoke cost\n")
    lines.append("| Model | 5q × 4 methods |")
    lines.append("|---|---|")
    for m, c in sorted(per_model_cost.items()):
        lines.append(f"| {m} | ${c:.4f} |")

    lines.append("\n## Full-run cost projection (per model × method)\n")
    lines.append("| Model × Method | Projected 500-row cost |")
    lines.append("|---|---|")
    for k, v in sorted(projections.items()):
        lines.append(f"| {k} | ${v:.2f} |")

    lines.append(f"\n**Grand projection:** ${grand_projection:.2f} (PROTOCOL §11 budget: ~$115; gate: $150)")

    if grand_projection > 150:
        lines.append("\n⚠️  **PROJECTION EXCEEDS $150 GATE — DO NOT PROCEED to full run without discussion.**")
    elif grand_projection > 115:
        lines.append(f"\n⚠️  Projection ${grand_projection:.2f} exceeds PROTOCOL §11 budget ($115) but within $150 gate.")
    else:
        lines.append(f"\n✅ Projection ${grand_projection:.2f} within PROTOCOL §11 budget ($115).")

    lines.append("\n## Failure detail (for any exit_code != 0, errors > 0, or parse failures > 0)\n")
    for r in results:
        if r["exit_code"] != 0 or r["errors"] > 0 or r["parse_failures"] > 0:
            lines.append(
                f"### {r['model']} / {r['method']} "
                f"(exit={r['exit_code']}, errors={r['errors']}, "
                f"parse_failures={r['parse_failures']})"
            )
            if r["stdout_tail"]:
                lines.append("stdout tail:")
                lines.append("```")
                lines.extend(r["stdout_tail"])
                lines.append("```")
            if r["stderr_tail"]:
                lines.append("stderr tail:")
                lines.append("```")
                lines.extend(r["stderr_tail"])
                lines.append("```")
            if r["sample_errors"]:
                lines.append("sample row errors:")
                lines.append("```")
                lines.extend(r["sample_errors"])
                lines.append("```")

    report_path.write_text("\n".join(lines) + "\n")
    return report_path


def main() -> int:
    SMOKE_ROOT.mkdir(parents=True, exist_ok=True)
    print(f"Smoke root: {SMOKE_ROOT}")
    print(f"Benchmark: {BENCHMARK}")
    print(f"Plan: {len(MODELS)} models × {len(METHODS)} methods × {N_QUESTIONS} questions "
          f"= {len(MODELS) * len(METHODS) * N_QUESTIONS} API calls\n")

    results: list[dict] = []
    for model in MODELS:
        print(f"═══ {model} ═══")
        for method in METHODS:
            print(f"  {method}...", end=" ", flush=True)
            r = _run_one(model, method)
            results.append(r)
            print(f"exit={r['exit_code']} rows={r['rows']} cost=${r['cost_usd']:.4f} "
                  f"wallclock={r['wall_seconds']:.1f}s errors={r['errors']} "
                  f"parse_failures={r['parse_failures']} n/a={r['not_applicable']}")
        print()

    report_path = _write_report(results)
    print(f"Report → {report_path}")

    grand_cost = sum(r["cost_usd"] for r in results)
    total_errors = sum(r["errors"] for r in results)
    total_parse_failures = sum(r["parse_failures"] for r in results)
    print(f"\nSMOKE DONE. Total: ${grand_cost:.4f} · errors={total_errors} · parse_failures={total_parse_failures}")
    return 0 if total_errors == 0 and total_parse_failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
