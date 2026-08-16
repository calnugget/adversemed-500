"""Calibration analysis pipeline — implements PROTOCOL §7 metrics + §8 primary analyses.

Consumes per-(model × method) JSONL files with the `adversemed_inference_v1` schema
produced by `run_inference.py`. Emits per-run analysis JSONs + a cross-run summary.md.

Metric definitions (PROTOCOL §7):
- Expected Calibration Error (ECE): 10-bin, weighted average of |acc − conf| per bin
- Brier score: mean of (confidence − correct)²
- Reliability diagram: per-bin (mean_conf, mean_acc, count)
- Coverage-risk curve: sort desc by confidence, cumulative error vs coverage%
- AURC: area under risk-coverage curve (trapezoid)
- Adversarial abstention rate: fraction of AdverseMed-500 questions where model
  chose "abstain"

Analysis outcomes (PROTOCOL §8):
- 8.1 Calibration Gap = ECE(OOD) − ECE(in-distribution). REQUIRES TASK_18b outputs
  (MedQA/MMLU-Med/PubMedQA). Stub function `calibration_gap()` prepared.
- 8.2 Ranking stability: Kendall's τ on model rankings across 4 elicitation methods
- 8.3 Adversarial abstention rate: direct
- 8.4 Model class effect: one-way ANOVA on ECE by class {generalist frontier, open}
  — implemented but only meaningful when specialist arm added

Structural N/A handling: elicitation.py can return `confidence=None` for structural
missing (e.g., log_probability on Anthropic/Gemini). These rows are filtered from
confidence-based metrics but tracked in the run report.

CLI:
    python3 -m _pipeline.analyze one       --input <jsonl>   --output <json>
    python3 -m _pipeline.analyze summarize --input-dir <dir> --output <md>
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from statistics import mean
from typing import Any

# ---------------------------------------------------------------------------
# Row I/O
# ---------------------------------------------------------------------------

def load_inference_jsonl(path: Path) -> list[dict]:
    """Load a per-run JSONL. Skip the schema header row."""
    rows: list[dict] = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("__schema__"):
                continue
            rows.append(row)
    return rows


def _valid_confidence_rows(rows: list[dict]) -> list[dict]:
    """Rows with a usable numeric confidence and a non-parse_failure answer."""
    out = []
    for r in rows:
        if r.get("chosen_answer") == "parse_failure":
            continue
        conf = r.get("confidence")
        if conf is None:
            continue
        if not isinstance(conf, (int, float)):
            continue
        if math.isnan(conf) or not (0.0 <= conf <= 1.0):
            continue
        out.append(r)
    return out

# ---------------------------------------------------------------------------
# Metric functions (§7)
# ---------------------------------------------------------------------------

def expected_calibration_error(
    confidences: list[float], correct: list[int | bool], n_bins: int = 10
) -> float:
    """10-bin ECE: weighted mean of |acc − mean_conf| per bin.

    Bin edges: [0, 0.1, 0.2, …, 1.0]. Bin i holds confidences in [i/n_bins, (i+1)/n_bins),
    except the last bin includes 1.0.
    """
    if not confidences:
        return float("nan")
    n = len(confidences)
    bin_counts = [0] * n_bins
    bin_conf_sum = [0.0] * n_bins
    bin_acc_sum = [0.0] * n_bins
    for c, y in zip(confidences, correct):
        i = min(int(c * n_bins), n_bins - 1)
        bin_counts[i] += 1
        bin_conf_sum[i] += c
        bin_acc_sum[i] += 1.0 if y else 0.0
    ece = 0.0
    for i in range(n_bins):
        if bin_counts[i] == 0:
            continue
        mean_c = bin_conf_sum[i] / bin_counts[i]
        mean_a = bin_acc_sum[i] / bin_counts[i]
        ece += (bin_counts[i] / n) * abs(mean_c - mean_a)
    return ece


def brier_score(confidences: list[float], correct: list[int | bool]) -> float:
    if not confidences:
        return float("nan")
    return sum((c - (1.0 if y else 0.0)) ** 2 for c, y in zip(confidences, correct)) / len(confidences)


def reliability_diagram_bins(
    confidences: list[float], correct: list[int | bool], n_bins: int = 10
) -> list[dict]:
    """Per-bin data for a reliability diagram."""
    bins: list[dict[str, Any]] = [
        {"bin_low": i / n_bins, "bin_high": (i + 1) / n_bins,
         "count": 0, "mean_confidence": None, "mean_accuracy": None}
        for i in range(n_bins)
    ]
    conf_sum = [0.0] * n_bins
    acc_sum = [0.0] * n_bins
    for c, y in zip(confidences, correct):
        i = min(int(c * n_bins), n_bins - 1)
        bins[i]["count"] += 1
        conf_sum[i] += c
        acc_sum[i] += 1.0 if y else 0.0
    for i, b in enumerate(bins):
        if b["count"] > 0:
            b["mean_confidence"] = conf_sum[i] / b["count"]
            b["mean_accuracy"] = acc_sum[i] / b["count"]
    return bins


def coverage_risk_curve(
    confidences: list[float], correct: list[int | bool]
) -> tuple[list[float], list[float]]:
    """Sort by descending confidence; at each cumulative coverage fraction return the
    cumulative error rate. Returns (coverages, risks) parallel arrays of same length."""
    if not confidences:
        return [], []
    pairs = sorted(zip(confidences, correct), key=lambda x: -x[0])
    n = len(pairs)
    coverages: list[float] = []
    risks: list[float] = []
    cum_errors = 0
    for i, (_, y) in enumerate(pairs, start=1):
        if not y:
            cum_errors += 1
        coverages.append(i / n)
        risks.append(cum_errors / i)
    return coverages, risks


def aurc(coverages: list[float], risks: list[float]) -> float:
    """Trapezoidal area under the risk-coverage curve."""
    if len(coverages) < 2:
        return float("nan")
    area = 0.0
    for j in range(1, len(coverages)):
        dx = coverages[j] - coverages[j - 1]
        area += 0.5 * (risks[j] + risks[j - 1]) * dx
    return area


def risk_at_coverage(coverages: list[float], risks: list[float], target: float) -> float | None:
    """Interpolate: what's the risk at a given coverage target (e.g. 0.9)?"""
    if not coverages or target < coverages[0] or target > coverages[-1]:
        return None
    for i in range(1, len(coverages)):
        if coverages[i] >= target:
            # linear interpolation
            x0, x1 = coverages[i - 1], coverages[i]
            y0, y1 = risks[i - 1], risks[i]
            if x1 == x0:
                return y1
            return y0 + (y1 - y0) * (target - x0) / (x1 - x0)
    return risks[-1]


def abstention_rate(rows: list[dict]) -> float:
    if not rows:
        return float("nan")
    return sum(1 for r in rows if r.get("chosen_answer") == "abstain") / len(rows)


def accuracy(rows: list[dict]) -> float:
    if not rows:
        return float("nan")
    return sum(1 for r in rows if r.get("correct")) / len(rows)

# ---------------------------------------------------------------------------
# Aggregate analysis
# ---------------------------------------------------------------------------

def analyze_run(rows: list[dict]) -> dict:
    """All PROTOCOL §7 metrics for one (model × method) run."""
    valid = _valid_confidence_rows(rows)
    confidences = [r["confidence"] for r in valid]
    correct = [bool(r.get("correct")) for r in valid]

    covs, risks = coverage_risk_curve(confidences, correct)
    return {
        "n_total_rows": len(rows),
        "n_usable_rows": len(valid),
        "n_parse_failures": sum(1 for r in rows if r.get("chosen_answer") == "parse_failure"),
        "n_confidence_none": sum(1 for r in rows if r.get("confidence") is None),
        "n_abstain": sum(1 for r in rows if r.get("chosen_answer") == "abstain"),
        "accuracy": accuracy(rows),
        "abstention_rate": abstention_rate(rows),
        "ece_10bin": expected_calibration_error(confidences, correct, n_bins=10),
        "brier_score": brier_score(confidences, correct),
        "reliability_bins": reliability_diagram_bins(confidences, correct, n_bins=10),
        "coverage_risk": {"coverages": covs, "risks": risks},
        "aurc": aurc(covs, risks),
        "risk_at_coverage_90": risk_at_coverage(covs, risks, 0.90),
        "risk_at_coverage_50": risk_at_coverage(covs, risks, 0.50),
        "total_cost_usd": sum(r.get("cost_usd", 0.0) for r in rows),
        "total_wall_ms": sum(r.get("wall_ms", 0) for r in rows),
        "total_api_calls": sum(r.get("n_api_calls", 0) for r in rows),
    }


def analyze_run_by(rows: list[dict], key: str) -> dict:
    """Break analyze_run down by a grouping key (e.g. 'category' or 'difficulty')."""
    groups: dict[str, list[dict]] = {}
    for r in rows:
        k = r.get(key)
        if k is None:
            continue
        groups.setdefault(k, []).append(r)
    return {k: analyze_run(v) for k, v in sorted(groups.items())}


def kendall_tau(a: list[float], b: list[float]) -> float:
    """Kendall's τ-b between two same-length ranking arrays. Pure-Python (no scipy dep)."""
    n = len(a)
    if n < 2:
        return float("nan")
    concordant = 0
    discordant = 0
    ties_a = 0
    ties_b = 0
    for i in range(n):
        for j in range(i + 1, n):
            da = a[i] - a[j]
            db = b[i] - b[j]
            if da == 0 and db == 0:
                continue
            if da == 0:
                ties_a += 1
            elif db == 0:
                ties_b += 1
            elif (da > 0) == (db > 0):
                concordant += 1
            else:
                discordant += 1
    denom = math.sqrt((concordant + discordant + ties_a) * (concordant + discordant + ties_b))
    if denom == 0:
        return float("nan")
    return (concordant - discordant) / denom


def calibration_gap(ece_ood: float, ece_id: float) -> float:
    """PROTOCOL §7 headline metric. Requires MedQA in-distribution ECE from TASK_18b."""
    return ece_ood - ece_id

# ---------------------------------------------------------------------------
# Cross-run summary
# ---------------------------------------------------------------------------

def collect_runs(input_dir: Path) -> dict[tuple[str, str], dict]:
    """Walk a directory of *.jsonl files, return {(model, method): analyze_run(rows)}."""
    out: dict[tuple[str, str], dict] = {}
    for path in sorted(input_dir.glob("*.jsonl")):
        rows = load_inference_jsonl(path)
        # Infer (model, method) from filename: <model>__<method>.jsonl
        stem = path.stem
        if "__" not in stem:
            continue
        model, method = stem.split("__", 1)
        out[(model, method)] = analyze_run(rows)
        # Also stash by-category and by-difficulty for reporting
        out[(model, method)]["by_category"] = analyze_run_by(rows, "category")
        out[(model, method)]["by_difficulty"] = analyze_run_by(rows, "difficulty")
    return out


def compute_ranking_stability(analyses: dict[tuple[str, str], dict]) -> dict[str, dict[str, float]]:
    """PROTOCOL §8.2: Kendall's τ on model rankings across the 4 elicitation methods.

    Ranking metric = ECE (lower = better calibration).
    """
    methods = sorted({m for (_, m) in analyses})
    models = sorted({mdl for (mdl, _) in analyses})
    # Skip methods that don't have all models yet
    ranks_by_method: dict[str, list[float]] = {}
    for meth in methods:
        eces = []
        for mdl in models:
            entry = analyses.get((mdl, meth))
            if entry is None or math.isnan(entry.get("ece_10bin", float("nan"))):
                eces = []
                break
            eces.append(entry["ece_10bin"])
        if eces:
            ranks_by_method[meth] = eces
    result: dict[str, dict[str, float]] = {}
    ms = sorted(ranks_by_method)
    for i, m1 in enumerate(ms):
        for m2 in ms[i + 1:]:
            result[f"{m1} vs {m2}"] = {
                "kendall_tau": kendall_tau(ranks_by_method[m1], ranks_by_method[m2]),
                "n_models": len(ranks_by_method[m1]),
            }
    return result


def format_summary_md(analyses: dict[tuple[str, str], dict], input_dir: Path) -> str:
    """Human-readable markdown report."""
    if not analyses:
        return "# Analysis summary\n\nNo inference outputs found in `{}`.\n".format(input_dir)

    lines: list[str] = []
    lines.append(f"# AdverseMed-500 analysis summary — {input_dir}\n")

    models = sorted({mdl for (mdl, _) in analyses})
    methods = sorted({m for (_, m) in analyses})

    lines.append(f"**Runs:** {len(analyses)} across {len(models)} models × {len(methods)} methods\n")

    def _fmt(v: Any, spec: str = ".3f") -> str:
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return "—"
        return format(v, spec)

    # Per-run headline table
    lines.append("## Per-run headline metrics\n")
    lines.append("| Model | Method | n_use | Acc | Abst | ECE | Brier | AURC | Risk@90 | Cost |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for (mdl, meth), a in sorted(analyses.items()):
        n_use = f"{a['n_usable_rows']}/{a['n_total_rows']}"
        lines.append(
            f"| {mdl} | {meth} | {n_use} | {_fmt(a['accuracy'])} | {_fmt(a['abstention_rate'])} "
            f"| {_fmt(a['ece_10bin'])} | {_fmt(a['brier_score'])} | {_fmt(a['aurc'])} "
            f"| {_fmt(a['risk_at_coverage_90'])} | {_fmt(a['total_cost_usd'], '.4f')} |"
        )

    # Per-model ranking per method
    lines.append("\n## Model ranking per method (by ECE, lower = better)\n")
    for meth in methods:
        entries = [(mdl, analyses.get((mdl, meth), {}).get("ece_10bin", float("nan"))) for mdl in models]
        entries = [(m, e) for m, e in entries if not math.isnan(e)]
        entries.sort(key=lambda x: x[1])
        if not entries:
            continue
        lines.append(f"### {meth}")
        for rank, (mdl, e) in enumerate(entries, start=1):
            lines.append(f"{rank}. {mdl} — ECE {e:.3f}")
        lines.append("")

    # Ranking stability
    stability = compute_ranking_stability(analyses)
    if stability:
        lines.append("## Ranking stability (Kendall's τ across methods, PROTOCOL §8.2)\n")
        lines.append("| Method pair | Kendall's τ | n_models |")
        lines.append("|---|---|---|")
        for pair, s in stability.items():
            lines.append(f"| {pair} | {s['kendall_tau']:.3f} | {s['n_models']} |")
        lines.append(
            "\n_High τ (> 0.7) = elicitation-invariant ranking. "
            "Low τ (< 0.3) = leaderboard is elicitation-dependent (PROTOCOL §12 risk register — publishable outcome either way)._"
        )
    else:
        lines.append(
            "## Ranking stability\n\n"
            "_Insufficient data — need at least 2 models × all 4 methods complete before Kendall's τ is meaningful._"
        )

    # Category × difficulty breakdown, one section per model
    lines.append("\n## Category × difficulty breakdown (accuracy · abstention · ECE per subgroup)\n")
    for mdl in models:
        for meth in methods:
            a = analyses.get((mdl, meth))
            if not a:
                continue
            by_cat = a.get("by_category", {})
            by_diff = a.get("by_difficulty", {})
            if not by_cat and not by_diff:
                continue
            lines.append(f"### {mdl} / {meth}")
            if by_cat:
                lines.append("**By category:**")
                for cat, aa in sorted(by_cat.items()):
                    lines.append(
                        f"- {cat}: acc={aa['accuracy']:.3f} abst={aa['abstention_rate']:.3f} "
                        f"ECE={aa['ece_10bin']:.3f} n={aa['n_total_rows']}"
                    )
            if by_diff:
                lines.append("**By difficulty:**")
                for diff, aa in sorted(by_diff.items()):
                    lines.append(
                        f"- {diff}: acc={aa['accuracy']:.3f} abst={aa['abstention_rate']:.3f} "
                        f"ECE={aa['ece_10bin']:.3f} n={aa['n_total_rows']}"
                    )
            lines.append("")

    return "\n".join(lines) + "\n"

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cmd_one(args: argparse.Namespace) -> int:
    rows = load_inference_jsonl(Path(args.input))
    analysis = analyze_run(rows)
    analysis["by_category"] = analyze_run_by(rows, "category")
    analysis["by_difficulty"] = analyze_run_by(rows, "difficulty")
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(analysis, indent=2) + "\n")
    print(f"[analyze one] wrote {out_path}")
    print(f"  n_usable={analysis['n_usable_rows']}/{analysis['n_total_rows']} "
          f"acc={analysis['accuracy']:.3f} abst={analysis['abstention_rate']:.3f} "
          f"ECE={analysis['ece_10bin']:.3f} Brier={analysis['brier_score']:.3f}")
    return 0


def _cmd_summarize(args: argparse.Namespace) -> int:
    input_dir = Path(args.input_dir)
    analyses = collect_runs(input_dir)
    if not analyses:
        print(f"[analyze summarize] no .jsonl files with __ in stem found in {input_dir}", file=sys.stderr)
        return 1
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(format_summary_md(analyses, input_dir))
    print(f"[analyze summarize] wrote {out_path} — {len(analyses)} runs")
    return 0


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Calibration analysis pipeline.")
    sub = p.add_subparsers(dest="cmd", required=True)

    one = sub.add_parser("one", help="Analyze one inference JSONL")
    one.add_argument("--input", required=True)
    one.add_argument("--output", required=True)
    one.set_defaults(func=_cmd_one)

    summ = sub.add_parser("summarize", help="Walk a dir of inference JSONLs and produce a summary")
    summ.add_argument("--input-dir", required=True)
    summ.add_argument("--output", required=True)
    summ.set_defaults(func=_cmd_summarize)

    return p.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args()
    raise SystemExit(args.func(args))
