#!/usr/bin/env python3
"""Repair out-of-range log-probability confidences in already-logged rows.

Reviewer UBqz objected that *filtering* the out-of-range rows is insufficient. It is:
`analyze.py::_valid_confidence_rows` drops any row failing `0.0 <= conf <= 1.0`, which
on gpt-5.4-mini/log_probability silently removed 26 of 500 rows — and specifically the
*most confident* 26, which is the worst possible direction for a calibration statistic.

This script repairs the derivation on the logged rows instead of dropping them. The
stored row keeps only the derived `confidence`, not the raw token log-probability, but
the map is invertible: logprob = log(confidence). We invert it, pass it through the
fixed `_pipeline.elicitation._logprob_to_confidence` (which clamps a positive
log-probability inside the quantization tolerance to exactly 1.0), and write the
result to a new directory. No raw response is altered and `correct` is asserted
unchanged on every row.

Usage:
    python3 analysis/fix_logprob_confidences.py [<in_dir> <out_dir>]

With no arguments it uses the repository's own directories. The two optional arguments exist so
the same file can run inside the released archive, where the pipeline package is called
`inference_pipeline` rather than `_pipeline` and the directory names differ; the import below
falls back accordingly. This step is NOT optional for reproducing the paper: analysing the
re-parsed logs without it yields 474/500 usable rows and ECE 0.148 on gpt-5.4-mini's
log-probability run, where the paper reports 500/500 and 0.171.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:  # repository layout
    from _pipeline.elicitation import (  # noqa: E402
        _LOGPROB_POSITIVE_TOLERANCE,
        _logprob_to_confidence,
    )
except ModuleNotFoundError:  # released-archive layout, where the package is `inference_pipeline`
    # elicitation.py imports `.providers.base`, so it has to be loaded AS a package member,
    # not as a top-level module. Put the package's parent on the path and import by the
    # directory's own name, so this works whatever the package is called.
    _here = Path(__file__).resolve().parent
    sys.path.insert(0, str(_here.parent))
    _elicitation = __import__(f"{_here.name}.elicitation", fromlist=["*"])
    _LOGPROB_POSITIVE_TOLERANCE = _elicitation._LOGPROB_POSITIVE_TOLERANCE
    _logprob_to_confidence = _elicitation._logprob_to_confidence

PAPER = Path(__file__).resolve().parents[1]
SRC = PAPER / "inference_outputs/adversemed_500_reparsed"
DST = PAPER / "inference_outputs/adversemed_500_lpfix"
if len(sys.argv) == 3:
    SRC, DST = Path(sys.argv[1]), Path(sys.argv[2])
elif len(sys.argv) != 1:
    print(__doc__.strip().splitlines()[-1], file=sys.stderr)
    raise SystemExit(2)
GRID = 2.0 ** -18


def main() -> int:
    DST.mkdir(parents=True, exist_ok=True)
    paths = sorted(SRC.glob("*__log_probability.jsonl"))
    if not paths:
        print(f"no log_probability files in {SRC}", file=sys.stderr)
        return 2
    print(f"coverage: {len(paths)} log_probability run(s) found in {SRC.name}\n")

    grand = {"rows": 0, "gt1": 0, "repaired": 0, "rejected": 0}
    for p in paths:
        out_lines = []
        n_rows = n_gt1 = n_repaired = n_rejected = 0
        offgrid = []
        with p.open() as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if row.get("__schema__") and "question_id" not in row:
                    out_lines.append(json.dumps(row))
                    continue
                n_rows += 1
                before_correct = row.get("correct")
                conf = row.get("confidence")
                if isinstance(conf, (int, float)) and not math.isnan(float(conf)) \
                        and float(conf) > 1.0:
                    n_gt1 += 1
                    lp = math.log(float(conf))
                    if abs(lp / GRID - round(lp / GRID)) > 1e-6:
                        offgrid.append((row["question_id"], lp))
                    new = _logprob_to_confidence(lp)
                    row["confidence"] = new
                    if new is None:
                        n_rejected += 1
                    else:
                        n_repaired += 1
                    row["confidence_repair"] = {
                        "original_confidence": float(conf),
                        "implied_logprob": lp,
                        "logprob_in_grid_units_2^-18": lp / GRID,
                        "tolerance": _LOGPROB_POSITIVE_TOLERANCE,
                        "reason": "positive log-probability from provider "
                                  "quantization; clamped to p=1.0",
                    }
                # `correct` must never move: it is chosen_answer == ground_truth
                assert row.get("correct") == before_correct, \
                    f"correct changed on {row.get('question_id')}"
                out_lines.append(json.dumps(row))

        (DST / p.name).write_text("\n".join(out_lines) + "\n")
        print(f"{p.name}")
        print(f"  rows={n_rows}  conf>1.0={n_gt1}  repaired={n_repaired}  "
              f"rejected_as_malformed={n_rejected}")
        print(f"  implied logprobs off the 2^-18 quantization grid: {len(offgrid)}")
        grand["rows"] += n_rows
        grand["gt1"] += n_gt1
        grand["repaired"] += n_repaired
        grand["rejected"] += n_rejected

    print(f"\nTOTAL rows={grand['rows']} conf>1.0={grand['gt1']} "
          f"repaired={grand['repaired']} rejected={grand['rejected']}")
    try:
        shown = DST.relative_to(PAPER)
    except ValueError:  # DST given on the command line, outside the paper directory
        shown = DST
    print(f"wrote corrected copies to {shown}/")
    print("`correct` verified unchanged on every row (assertion in-loop).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
