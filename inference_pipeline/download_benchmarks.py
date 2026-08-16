"""
download_benchmarks.py — TASK_03

Downloads the three seed benchmarks (MedQA, MMLU-Med, PubMedQA) from HuggingFace
and materializes the exact sampled subsets committed in the OSF pre-registration
osf.io/mehu4:
- MedQA: 1000 questions sampled with seed 20260706 from the ~12,700 test partition
- MMLU-Med: 1089 questions (full 6-subject clinical subset — no sampling)
- PubMedQA: 1000 questions sampled with seed 20260706 from the labeled test partition
- AdverseMed-500 seed pool: 500 additional MedQA questions from a DISJOINT index range,
  drawn with the same seed, used later as the mutation base for AdverseMed-500.

Outputs are written as JSONL under datasets/ with a manifest recording per-file
row count and SHA-256 for reproducibility.

Usage:
  python3 _pipeline/download_benchmarks.py
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

SEED = 20260706
OUT_DIR = Path(__file__).parent.parent / "datasets"
OUT_DIR.mkdir(exist_ok=True)

# MMLU subjects that constitute the standard "MMLU-Med" clinical subset
# (matches MedHELM's convention; N ≈ 1089 across the 6 subjects)
MMLU_MED_SUBJECTS = [
    "anatomy",
    "clinical_knowledge",
    "college_biology",
    "college_medicine",
    "medical_genetics",
    "professional_medicine",
]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_jsonl(rows: list[dict], out: Path) -> None:
    with out.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def download_medqa() -> tuple[list[dict], list[dict]]:
    """Returns (calibration_sample_1000, adversemed_seed_pool_500).

    Calibration is sampled from MedQA test split (the standard clinical-benchmark
    convention). AdverseMed-500 mutation seeds are drawn from the MedQA train
    split — larger pool, and guaranteed disjoint from the test-split calibration
    sample per OSF pre-reg §7's data-leakage constraint.
    """
    from datasets import load_dataset

    print("  → MedQA: loading GBaker/MedQA-USMLE-4-options ...")
    test_ds = load_dataset("GBaker/MedQA-USMLE-4-options", split="test")
    train_ds = load_dataset("GBaker/MedQA-USMLE-4-options", split="train")
    print(f"    test partition:  {len(test_ds)} questions (source for calibration sample)")
    print(f"    train partition: {len(train_ds)} questions (source for AdverseMed-500 seeds)")

    def to_row(rec: dict, source_index: int, split: str) -> dict:
        return {
            "question_id": f"medqa_{split}_{source_index}",
            "source_split": split,
            "source_index": source_index,
            "benchmark_source": "MedQA",
            "question": rec.get("question") or rec.get("sent1"),
            "choices": rec.get("options") or rec.get("choices"),
            "ground_truth": rec.get("answer_idx") if "answer_idx" in rec else rec.get("label"),
        }

    # Calibration sample — sample 1000 from test split with seed
    rng_test = random.Random(SEED)
    test_indices = list(range(len(test_ds)))
    rng_test.shuffle(test_indices)
    calibration_indices = test_indices[:1000]
    calibration = [to_row(test_ds[i], i, "test") for i in calibration_indices]

    # AdverseMed-500 seed pool — sample 500 from train split with same seed (different pool -> different draw)
    rng_train = random.Random(SEED)
    train_indices = list(range(len(train_ds)))
    rng_train.shuffle(train_indices)
    seed_pool_indices = train_indices[:500]
    seed_pool = [to_row(train_ds[i], i, "train") for i in seed_pool_indices]

    return calibration, seed_pool


def download_mmlu_med() -> list[dict]:
    """Full 6-subject clinical subset of MMLU. No sampling."""
    from datasets import load_dataset

    print(f"  → MMLU-Med: loading {len(MMLU_MED_SUBJECTS)} clinical subjects ...")
    rows: list[dict] = []
    for subject in MMLU_MED_SUBJECTS:
        ds = load_dataset("cais/mmlu", subject, split="test")
        print(f"    {subject}: {len(ds)} questions")
        for idx in range(len(ds)):
            rec = ds[idx]
            rows.append({
                "question_id": f"mmlu_{subject}_{idx}",
                "source_index": idx,
                "benchmark_source": "MMLU_Med",
                "subject": subject,
                "question": rec["question"],
                "choices": rec["choices"],
                "ground_truth": rec["answer"],  # int 0-3
            })
    return rows


def download_pubmedqa() -> list[dict]:
    """1000 questions sampled from PubMedQA labeled test with seed."""
    from datasets import load_dataset

    print("  → PubMedQA: loading qiaojin/PubMedQA (pqa_labeled) ...")
    ds = load_dataset("qiaojin/PubMedQA", "pqa_labeled", split="train")
    # PubMedQA "labeled" split is usually named "train" in HF but is the labeled question pool
    total = len(ds)
    print(f"    total labeled questions: {total}")

    rng = random.Random(SEED)
    indices = list(range(total))
    rng.shuffle(indices)
    selected = indices[:1000]

    rows: list[dict] = []
    for idx in selected:
        rec = ds[idx]
        rows.append({
            "question_id": f"pubmedqa_{idx}",
            "source_index": idx,
            "benchmark_source": "PubMedQA",
            "question": rec.get("question"),
            "context": rec.get("context"),
            "long_answer": rec.get("long_answer"),
            "ground_truth": rec.get("final_decision"),  # "yes"/"no"/"maybe"
        })
    return rows


def main() -> int:
    print(f"seed = {SEED}")
    print(f"output dir = {OUT_DIR.resolve()}")
    print()

    manifest: dict[str, dict] = {"seed": SEED, "files": {}}

    # MedQA + AdverseMed-500 seed pool
    medqa_calibration, adversemed_seed = download_medqa()
    write_jsonl(medqa_calibration, OUT_DIR / "medqa_test_n1000.jsonl")
    write_jsonl(adversemed_seed, OUT_DIR / "adversemed_seed_pool_n500.jsonl")

    # MMLU-Med
    mmlu_med = download_mmlu_med()
    write_jsonl(mmlu_med, OUT_DIR / "mmlu_med_n1089.jsonl")

    # PubMedQA
    pubmedqa = download_pubmedqa()
    write_jsonl(pubmedqa, OUT_DIR / "pubmedqa_test_n1000.jsonl")

    # Build manifest
    for name in [
        "medqa_test_n1000.jsonl",
        "adversemed_seed_pool_n500.jsonl",
        "mmlu_med_n1089.jsonl",
        "pubmedqa_test_n1000.jsonl",
    ]:
        p = OUT_DIR / name
        with p.open() as f:
            row_count = sum(1 for _ in f)
        manifest["files"][name] = {"rows": row_count, "sha256": sha256_of(p)}

    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print()
    print("=" * 60)
    print("DONE. Manifest:")
    for name, meta in manifest["files"].items():
        print(f"  {name}: {meta['rows']} rows · sha256 {meta['sha256'][:16]}...")
    print()
    print(f"Manifest written: {OUT_DIR / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
