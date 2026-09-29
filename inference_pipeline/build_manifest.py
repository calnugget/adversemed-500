#!/usr/bin/env python3
"""Generate datasets/manifest.json mechanically from the files on disk, or verify it.

WHY THIS EXISTS
---------------
The manifest was previously maintained by hand, and a hand-edited manifest drifts: an entry can
record a row count or a hash that no file on disk has. That defect ships silently, because nothing
checks it. This script makes the manifest a derived artifact and gives CI a command that fails when
it disagrees with the files.

USAGE
    python3 build_manifest.py --check     # exit 1 on any drift; prints every mismatch
    python3 build_manifest.py --write     # regenerate the manifest from disk

--check is the one to run before any release. It never writes.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASETS = ROOT / "datasets"
MANIFEST = DATASETS / "manifest.json"

# Files the manifest tracks, in the order they appear. A file listed here that is missing from
# disk is an error; a .jsonl in datasets/ that is absent here is reported by --check as untracked.
TRACKED = [
    "medqa_test_n1000.jsonl",
    "adversemed_seed_pool_n500.jsonl",
    "mmlu_med_n1089.jsonl",
    "pubmedqa_test_n1000.jsonl",
    "adversemed_500.jsonl",
    "adversemed_500_v1.2.jsonl",
    "adversemed_500_control_v1.jsonl",
    "adversemed_500_control_v1.preshuffle.jsonl",
    "twin_review_log.jsonl",
]

SEED = 20260706


def digest(path: Path) -> tuple[int, str]:
    """Return (row count, sha256) for a JSONL file, streaming so large files are fine."""
    h = hashlib.sha256()
    rows = 0
    with path.open("rb") as fh:
        for line in fh:
            h.update(line)
            if line.strip():
                rows += 1
    return rows, h.hexdigest()


def breakdowns(path: Path) -> dict:
    """Category and difficulty counts, for the AdverseMed corpora only.

    The published manifest has always carried these for adversemed_500.jsonl. They are derived,
    not curated, so they are computed here rather than kept by hand.
    """
    import collections
    cats, diffs = collections.Counter(), collections.Counter()
    with path.open() as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("false_premise_category"):
                cats[row["false_premise_category"]] += 1
            if row.get("difficulty"):
                diffs[row["difficulty"]] += 1
    out = {}
    if cats:
        out["categories"] = dict(sorted(cats.items()))
    if diffs:
        out["difficulties"] = dict(sorted(diffs.items()))
    return out


def build() -> dict:
    files = {}
    missing = []
    for name in TRACKED:
        p = DATASETS / name
        if not p.exists():
            missing.append(name)
            continue
        rows, sha = digest(p)
        files[name] = {"rows": rows, "sha256": sha}
        if name.startswith("adversemed_500"):
            files[name].update(breakdowns(p))
    if missing:
        print("ERROR: tracked files absent from disk: " + ", ".join(missing), file=sys.stderr)
        raise SystemExit(2)
    return {"seed": SEED, "files": files}


def check() -> int:
    fresh = build()
    if not MANIFEST.exists():
        print("FAIL: %s does not exist" % MANIFEST, file=sys.stderr)
        return 1

    stored = json.loads(MANIFEST.read_text())
    problems = []

    if stored.get("seed") != fresh["seed"]:
        problems.append("seed: manifest=%r disk=%r" % (stored.get("seed"), fresh["seed"]))

    sf, ff = stored.get("files", {}), fresh["files"]
    for name in sorted(set(sf) | set(ff)):
        if name not in sf:
            problems.append("%s: on disk but NOT in the manifest" % name)
        elif name not in ff:
            problems.append("%s: in the manifest but NOT tracked or not on disk" % name)
        else:
            for field in ("rows", "sha256"):
                if sf[name].get(field) != ff[name][field]:
                    problems.append("%s %s: manifest=%s disk=%s"
                                    % (name, field, sf[name].get(field), ff[name][field]))

    # Anything in datasets/ that nobody tracks
    untracked = sorted(p.name for p in DATASETS.glob("*.jsonl") if p.name not in TRACKED)
    for name in untracked:
        problems.append("%s: present in datasets/ but not in TRACKED (add it or explain why not)" % name)

    if problems:
        print("MANIFEST CHECK FAILED — %d problem(s):" % len(problems), file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        return 1

    print("manifest OK — %d files, every row count and hash matches disk" % len(ff))
    return 0


def write() -> int:
    fresh = build()
    MANIFEST.write_text(json.dumps(fresh, indent=2) + "\n")
    print("wrote %s — %d files" % (MANIFEST, len(fresh["files"])))
    for name, meta in fresh["files"].items():
        print("  %-44s %6d rows  %s" % (name, meta["rows"], meta["sha256"][:16] + "…"))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="fail if the manifest disagrees with disk")
    g.add_argument("--write", action="store_true", help="regenerate the manifest from disk")
    args = ap.parse_args()
    return check() if args.check else write()


if __name__ == "__main__":
    raise SystemExit(main())
