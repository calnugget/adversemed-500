#!/usr/bin/env python3
"""Recompute inference cost from logged token counts at a dated published price table.

WHY THIS EXISTS
---------------
The per-run `cost_usd` in the inference logs is computed at run time from price constants
hard-coded in `providers/*.py`. Those constants went stale: they carried legacy Claude-3-era
Opus pricing ($15/$75 per 1M against a published $5/$25), and were wrong for four of the five
models. A correction pass on 2026-08-24 reconciled the AdverseMed-500 arm against published
list prices -- BY HAND, with no script. See `reviews/COST_RECOMPUTE_2026-08-24.md`.

Because that pass left no code behind, the MedQA in-distribution arm added five weeks later
silently picked the stale constants back up, and the paper ended up reporting one arm at list
prices and the other at legacy prices while claiming both were at list prices. This script
exists so that cannot happen a third time: repricing is now a command, not a memory.

THE TABLE IS DATED, DELIBERATELY
--------------------------------
Prices are as retrieved 2026-08-24 and are reproduced here verbatim from the review document,
which names a source for each row. The runs executed 2026-08-02, so a vendor reprice between
those dates is unmodelled -- a disclosed limitation, not a hidden one. Do not silently update
these numbers to today's prices: Table 6 of the paper reproduces exactly from THIS table, and
changing it changes published figures. Add a new dated table instead.

USAGE
    python3 reprice.py <run-dir> [<run-dir> ...]        # per-cell and per-model costs
    python3 reprice.py --check <run-dir> --expect-total 12.63
"""
import argparse
import collections
import glob
import json
import sys
from pathlib import Path

# $ per 1M tokens, (input, output). Source: reviews/COST_RECOMPUTE_2026-08-24.md lines 80-86,
# list prices retrieved 2026-08-24. Each row's source is named in that document.
PRICES_2026_08_24 = {
    "Claude Opus 4.7":     (5.00, 25.00),   # Anthropic pricing table
    "Claude Haiku 4.5":    (1.00,  5.00),   # Anthropic pricing table (pipeline already matched)
    "Gemini Pro (latest)": (1.25, 10.00),   # ai.google.dev, prompts <=200k
    "GPT-5.4-mini":        (0.75,  4.50),   # developers.openai.com
    # deepseek-chat is absent from DeepSeek's price list; this is the nearest successor rate
    # (V4-Flash, cache-miss, off-peak) as of 2026-08-24. The least trustworthy row in the table,
    # and flagged as such in the review document and in the paper.
    "DeepSeek-Chat":       (0.22,  0.66),
}

# Gemini's logged completion count is `candidates_token_count`, which excludes billed
# `thoughts_token_count`. Gemini cost cells are therefore LOWER BOUNDS, not estimates.
LOWER_BOUND_MODELS = {"Gemini Pro (latest)"}


def rows(path: Path):
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


def tally(run_dir: Path):
    """(model, method) -> [prompt_tokens, completion_tokens, logged_cost_usd]."""
    cells = collections.defaultdict(lambda: [0, 0, 0.0])
    files = sorted(run_dir.glob("*.jsonl"))
    if not files:
        print("ERROR: no run files under %s" % run_dir, file=sys.stderr)
        raise SystemExit(2)
    for f in files:
        for r in rows(f):
            k = (r.get("model_id"), r.get("method"))
            cells[k][0] += r.get("prompt_tokens") or 0
            cells[k][1] += r.get("completion_tokens") or 0
            cells[k][2] += r.get("cost_usd") or 0.0
    unknown = {m for m, _ in cells} - set(PRICES_2026_08_24)
    if unknown:
        # Fail loudly. A model with no price silently contributing $0 is exactly how the
        # MedQA arm went unnoticed.
        print("ERROR: no price for: %s" % ", ".join(sorted(map(str, unknown))), file=sys.stderr)
        raise SystemExit(2)
    return cells, len(files)


def repriced(cells):
    out = {}
    for (model, method), (p, c, logged) in cells.items():
        i, o = PRICES_2026_08_24[model]
        out[(model, method)] = {
            "prompt_tokens": p, "completion_tokens": c,
            "logged_usd": round(logged, 4),
            "repriced_usd": round(p / 1e6 * i + c / 1e6 * o, 4),
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dirs", nargs="+", type=Path)
    ap.add_argument("--check", action="store_true", help="exit 1 if --expect-total disagrees")
    ap.add_argument("--expect-total", type=float, default=None)
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = ap.parse_args()

    grand_rep = grand_log = 0.0
    payload = {}
    for d in args.run_dirs:
        cells, nfiles = tally(d)
        rp = repriced(cells)
        by_model = collections.defaultdict(lambda: [0.0, 0.0])
        for (m, _), v in rp.items():
            by_model[m][0] += v["repriced_usd"]
            by_model[m][1] += v["logged_usd"]
        sub_rep = sum(v[0] for v in by_model.values())
        sub_log = sum(v[1] for v in by_model.values())
        grand_rep += sub_rep
        grand_log += sub_log
        payload[d.name] = {"n_runs": nfiles,
                           "per_model": {m: {"repriced_usd": round(v[0], 4),
                                             "logged_usd": round(v[1], 4)} for m, v in by_model.items()},
                           "total_repriced_usd": round(sub_rep, 4),
                           "total_logged_usd": round(sub_log, 4)}
        if not args.json:
            print("=== %s (%d runs) ===" % (d.name, nfiles))
            print("  %-24s %12s %12s" % ("model", "repriced", "logged"))
            for m in sorted(by_model):
                mark = "  (lower bound)" if m in LOWER_BOUND_MODELS else ""
                print("  %-24s %12.4f %12.4f%s" % (m, by_model[m][0], by_model[m][1], mark))
            print("  %-24s %12.4f %12.4f" % ("TOTAL", sub_rep, sub_log))
            print()

    if args.json:
        payload["grand_total_repriced_usd"] = round(grand_rep, 4)
        payload["grand_total_logged_usd"] = round(grand_log, 4)
        print(json.dumps(payload, indent=2))
    else:
        print("GRAND TOTAL  repriced $%.4f   logged $%.4f" % (grand_rep, grand_log))

    if args.expect_total is not None:
        ok = abs(round(grand_rep, 2) - args.expect_total) < 1e-9
        print("expected $%.2f, got $%.2f -- %s" % (args.expect_total, grand_rep, "OK" if ok else "MISMATCH"),
              file=sys.stderr)
        if not ok:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
