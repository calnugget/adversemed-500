#!/usr/bin/env python3
"""Re-derive the `confidence` field from each row's verbatim `raw_text`.

WHY THIS EXISTS
---------------
Two parsing defects were corrected on 2026-08-24, after the inference runs had already been
logged. The raw model responses are unaffected -- only their PARSING was wrong -- so the fix is
applied by re-reading `raw_text` rather than by re-running any model:

  1. providers/deepseek.py::_CONF_RE rejected DeepSeek-Chat's misspelling "CONFIDANCE",
     silently dropping a stated confidence on ~16% of its temperature_0 rows and 77 of its
     verbal_probability rows. This corrupted PUBLISHED verbal_probability numbers.

  2. elicitation.py::elicit_temperature_0 recorded a constant confidence of 1.0, per
     PROTOCOL section 6. That made ECE = Brier = 1 - accuracy identically, so three of its four
     reported statistics were restatements of accuracy. Re-reading the in-band stated
     confidence is a DEVIATION from the registered plan, disclosed as such in the papers.

The raw inference JSONL is left untouched. Corrected copies are written to a separate
directory so the released archive carries both the pristine log and the analysed input.

USAGE
    python3 reparse_confidence.py <in_dir> <out_dir>

Accuracy is NOT affected: `correct` is chosen_answer == ground_truth and is independent of
confidence. The script asserts this and fails loudly if any row's `correct` changes.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from providers.deepseek import _parse_answer_and_confidence  # the FIXED parser

# methods whose confidence is re-derived from raw_text
REPARSE = {"temperature_0", "verbal_probability"}


def reparse_file(src: Path, dst: Path) -> dict:
    stats = {"rows": 0, "reparsed": 0, "now_none": 0, "changed": 0, "correct_changed": 0}
    out_lines = []
    for line in src.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if "__schema__" in row:
            out_lines.append(json.dumps(row))
            continue
        stats["rows"] += 1
        method = row.get("method", "")
        if method in REPARSE:
            before_conf = row.get("confidence")
            before_correct = row.get("correct")
            _, conf, _ = _parse_answer_and_confidence(row.get("raw_text") or "")
            row["confidence"] = conf
            stats["reparsed"] += 1
            if conf is None:
                stats["now_none"] += 1
            if conf != before_conf:
                stats["changed"] += 1
            # accuracy must be untouched
            if row.get("correct") != before_correct:
                stats["correct_changed"] += 1
        out_lines.append(json.dumps(row))
    dst.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return stats


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    in_dir, out_dir = Path(argv[1]), Path(argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(in_dir.glob("*.jsonl"))
    if not files:
        print(f"no .jsonl under {in_dir}")
        return 2
    total = {"rows": 0, "reparsed": 0, "now_none": 0, "changed": 0, "correct_changed": 0}
    for f in files:
        s = reparse_file(f, out_dir / f.name)
        for k in total:
            total[k] += s[k]
        print(f"  {f.name:<46} rows={s['rows']:<5} reparsed={s['reparsed']:<5} "
              f"changed={s['changed']:<5} none={s['now_none']}")
    print(f"\n  TOTAL rows={total['rows']} reparsed={total['reparsed']} "
          f"changed={total['changed']} unparseable={total['now_none']}")
    if total["correct_changed"]:
        print(f"\n  FAILED: `correct` changed on {total['correct_changed']} rows. "
              "Confidence must not affect accuracy.")
        return 1
    print("  OK: `correct` unchanged on every row, as required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
