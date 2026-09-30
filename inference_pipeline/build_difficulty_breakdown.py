#!/usr/bin/env python3
"""Generate analysis_outputs/<benchmark>/difficulty_breakdown.json, or verify it.

WHY THIS EXISTS
---------------
The v3 manuscript tells a reader that the full obvious/subtle/expert accuracy table, per
(model x method) cell, "is available in the release bundle at
analysis_outputs/adversemed_500/difficulty_breakdown.json". That file had never been created --
not in the repo, not on Zenodo, not on disk. A reader following the pointer found nothing.

The data was there the whole time: every inference row carries `difficulty` and `correct`. So the
honest fix is to produce the file the paper promises rather than delete the sentence. This script
derives it from the logged rows, which means it cannot drift from them the way a hand-written
table would.

`correct` does not depend on confidence, so these accuracies are unaffected by the 2026-08-24
re-parse and the 2026-09-28 log-probability correction (see CORRECTIONS.md).

USAGE
    python3 build_difficulty_breakdown.py --check     # exit 1 if the file is missing or stale
    python3 build_difficulty_breakdown.py --write     # (re)generate it

--check is the one to run before a release. It never writes.
"""
import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# The raw inference logs are NOT in this repository; they are in the Zenodo archive
# (concept DOI 10.5281/zenodo.21961770). Unpack them and pass --runs-dir. See REPRODUCING.md.
DEFAULT_RUNS = ROOT / "inference_outputs" / "adversemed_500_final"
DEFAULT_OUT = ROOT / "scoring" / "analysis_outputs" / "difficulty_breakdown.json"

# The corpus difficulty strata, in the order the paper reports them.
STRATA = ["obvious", "subtle", "expert"]


def rows(path: Path):
    """Yield the per-item rows of a run file, skipping its header record.

    The first line is a run header (no `question_id`); every later line is one item.
    """
    with path.open() as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "question_id" in r:
                yield r


def build(runs_dir: Path) -> dict:
    files = sorted(runs_dir.glob("*.jsonl"))
    if not files:
        print("ERROR: no run files under %s" % runs_dir, file=sys.stderr)
        raise SystemExit(2)

    cells = {}
    totals = collections.defaultdict(lambda: [0, 0])  # difficulty -> [n_correct, n]
    skipped = []

    for f in files:
        by_diff = collections.defaultdict(lambda: [0, 0])
        model = method = None
        n = 0
        for r in rows(f):
            model = model or r.get("model_id")
            method = method or r.get("method")
            d = r.get("difficulty")
            if d is None:
                continue
            n += 1
            by_diff[d][1] += 1
            totals[d][1] += 1
            if r.get("correct"):
                by_diff[d][0] += 1
                totals[d][0] += 1
        if not n or model is None or method is None:
            skipped.append(f.name)
            continue

        cell = {}
        for d in STRATA:
            c, t = by_diff.get(d, [0, 0])
            cell[d] = {
                "n": t,
                "n_correct": c,
                "accuracy": round(c / t, 4) if t else None,
            }
        cell["all"] = {
            "n": sum(cell[d]["n"] for d in STRATA),
            "n_correct": sum(cell[d]["n_correct"] for d in STRATA),
        }
        cell["all"]["accuracy"] = (
            round(cell["all"]["n_correct"] / cell["all"]["n"], 4) if cell["all"]["n"] else None
        )
        cells["%s__%s" % (model, method)] = cell

    # Coverage guard. A sweep that can silently skip a run proves nothing, so refuse to emit a
    # file whose cell count does not match the run files it claims to summarise.
    if skipped:
        print("ERROR: %d run file(s) yielded no usable rows: %s"
              % (len(skipped), ", ".join(skipped)), file=sys.stderr)
        raise SystemExit(2)
    if len(cells) != len(files):
        print("ERROR: %d run files but %d cells - a run was dropped"
              % (len(files), len(cells)), file=sys.stderr)
        raise SystemExit(2)

    return {
        "benchmark": "adversemed_500",
        "source": "derived from %s by _pipeline/build_difficulty_breakdown.py" % runs_dir.name,
        "note": ("Accuracy is chosen_answer == ground_truth and does not depend on stated "
                 "confidence, so these values are unaffected by the confidence re-parse and the "
                 "log-probability correction recorded in CORRECTIONS.md."),
        "strata": STRATA,
        "corpus_totals": {
            d: {"n": totals[d][1], "n_correct": totals[d][0],
                "accuracy": round(totals[d][0] / totals[d][1], 4) if totals[d][1] else None}
            for d in STRATA
        },
        "n_cells": len(cells),
        "cells": dict(sorted(cells.items())),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="fail if the file is missing or stale")
    g.add_argument("--write", action="store_true", help="(re)generate the file")
    ap.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    fresh = build(args.runs_dir)

    if args.check:
        if not args.out.exists():
            print("FAIL: %s does not exist" % args.out, file=sys.stderr)
            return 1
        stored = json.loads(args.out.read_text())
        if stored != fresh:
            print("FAIL: %s disagrees with the logged rows - regenerate it" % args.out,
                  file=sys.stderr)
            return 1
        print("difficulty_breakdown OK - %d cells, all reproduce from %s"
              % (fresh["n_cells"], args.runs_dir.name))
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(fresh, indent=2) + "\n")
    print("wrote %s - %d cells" % (args.out, fresh["n_cells"]))
    for d in STRATA:
        t = fresh["corpus_totals"][d]
        print("  %-8s n=%-5d pooled accuracy %.4f" % (d, t["n"], t["accuracy"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
