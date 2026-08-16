"""build_adversemed.py

Reads all verified question YAML files under adversemed-500/verified/ and
compiles them into datasets/adversemed_500.jsonl with a fresh SHA-256 in the
manifest. Run this whenever you want to refresh the JSONL that the inference
pipeline consumes.

Usage (from ~/dyuthi-research/papers/paper-1-medllm-calibration):
  source .venv/bin/activate
  python3 _pipeline/build_adversemed.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
VERIFIED_DIR = ROOT / "adversemed-500" / "verified"
OUT_FILE = ROOT / "datasets" / "adversemed_500.jsonl"
MANIFEST = ROOT / "datasets" / "manifest.json"

VALID_CATEGORIES = {
    "contraindication",
    "drug_drug_interaction",
    "impossible_timing",
    "physiological_impossibility",
}
VALID_DIFFICULTIES = {"obvious", "subtle", "expert"}
REQUIRED_FIELDS = {"seed_index", "category", "difficulty", "question", "choices", "correct",
                   "premise_description", "reference", "verified_by", "verified_at"}


def validate(yaml_doc: dict, path: Path) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_FIELDS - set(yaml_doc.keys())
    if missing:
        errors.append(f"missing fields: {sorted(missing)}")
    cat = yaml_doc.get("category")
    if cat and cat not in VALID_CATEGORIES:
        errors.append(f"invalid category {cat!r}; must be one of {sorted(VALID_CATEGORIES)}")
    difficulty = yaml_doc.get("difficulty")
    if difficulty and difficulty not in VALID_DIFFICULTIES:
        errors.append(
            f"invalid difficulty {difficulty!r}; must be one of {sorted(VALID_DIFFICULTIES)}"
        )
    choices = yaml_doc.get("choices")
    if choices and not isinstance(choices, dict):
        errors.append("choices must be a dict {A: text, B: text, ...}")
    return errors


def to_jsonl_row(yaml_doc: dict, question_id: str) -> dict:
    """Normalize a verified YAML into the JSONL schema the inference pipeline expects."""
    return {
        "question_id": question_id,
        "benchmark_source": "AdverseMed_500",
        "source_seed_index": yaml_doc["seed_index"],
        "false_premise_category": yaml_doc["category"],
        "difficulty": yaml_doc["difficulty"],
        "question": yaml_doc["question"].strip(),
        "choices": yaml_doc["choices"],
        "ground_truth": yaml_doc["correct"],
        "false_premise_description": yaml_doc["premise_description"].strip(),
        "verification": {
            "verified_by": yaml_doc["verified_by"],
            "verified_at": str(yaml_doc["verified_at"]),
            "reference": yaml_doc["reference"],
        },
    }


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not VERIFIED_DIR.exists():
        VERIFIED_DIR.mkdir(parents=True)
    yaml_files = sorted(VERIFIED_DIR.glob("*.yaml"))
    if not yaml_files:
        print(f"No verified questions found in {VERIFIED_DIR}")
        print("Nothing to build. Add YAML files under verified/ and re-run.")
        return 0

    all_errors: list[str] = []
    rows: list[dict] = []
    category_counts: Counter = Counter()
    difficulty_counts: Counter = Counter()

    for i, yf in enumerate(yaml_files, start=1):
        try:
            doc = yaml.safe_load(yf.read_text())
        except yaml.YAMLError as e:
            all_errors.append(f"{yf.name}: YAML parse error — {e}")
            continue
        errors = validate(doc, yf)
        if errors:
            for e in errors:
                all_errors.append(f"{yf.name}: {e}")
            continue

        question_id = f"adversemed_{i:03d}"
        rows.append(to_jsonl_row(doc, question_id))
        category_counts[doc["category"]] += 1
        difficulty_counts[doc["difficulty"]] += 1

    if all_errors:
        print("VALIDATION ERRORS:")
        for e in all_errors:
            print(f"  {e}")
        return 1

    # Write JSONL
    OUT_FILE.parent.mkdir(exist_ok=True)
    with OUT_FILE.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Update manifest
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text())
    else:
        manifest = {"seed": 20260706, "files": {}}
    manifest["files"]["adversemed_500.jsonl"] = {
        "rows": len(rows),
        "sha256": sha256_of(OUT_FILE),
        "categories": dict(category_counts),
        "difficulties": dict(difficulty_counts),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")

    # Report
    print(f"Compiled {len(rows)} verified questions to {OUT_FILE}")
    print()
    print("Category counts (targets: contra 150 / ddi 125 / timing 100 / physio 125):")
    for cat in sorted(VALID_CATEGORIES):
        target = {"contraindication": 150, "drug_drug_interaction": 125,
                  "impossible_timing": 100, "physiological_impossibility": 125}[cat]
        n = category_counts.get(cat, 0)
        pct = 100 * n / target if target else 0
        print(f"  {cat:32s}: {n:>3d} / {target}  ({pct:.0f}%)")
    print()
    print("Difficulty counts:")
    for difficulty in ("obvious", "subtle", "expert"):
        n = difficulty_counts.get(difficulty, 0)
        pct = 100 * n / len(rows) if rows else 0
        print(f"  {difficulty:8s}: {n:>3d}  ({pct:.0f}%)")
    print()
    print(f"Total: {len(rows)} / 500 ({100 * len(rows) / 500:.0f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
