"""CLI entry point: `adversemed-gen`.

Implements TASK_22 §4.5. Wires up baseline + verifier providers from Paper 1's
`_pipeline/providers/` registry, loads the seed pool + patterns, and drives
`generate_batch` to produce N verified questions.

Usage:
    adversemed-gen \
        --seed-pool ../datasets/adversemed_seed_pool_n500.jsonl \
        --baseline claude-opus-4-7 \
        --verifiers gpt-5.4-mini,gemini-2.5-pro,deepseek-chat \
        --n-questions 20 \
        --output-dir generated_questions/ \
        [--category contraindication] \
        [--seed 20260801]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .models import MODEL_REGISTRY
from .patterns import PATTERNS, get_patterns_by_category
from .pipeline import generate_batch


def _load_seed_pool(path: Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def _resolve_verifiers(csv: str, baseline: str) -> list[str]:
    verifier_ids = [v.strip() for v in csv.split(",") if v.strip()]
    if baseline in verifier_ids:
        raise SystemExit(f"Baseline {baseline!r} must not be in verifier list; provider-family diversity requires distinct baseline + verifiers.")
    for v in verifier_ids:
        if v not in MODEL_REGISTRY:
            raise SystemExit(f"Unknown verifier {v!r}. Known: {sorted(MODEL_REGISTRY)}")
    return verifier_ids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="adversemed-gen",
        description="LLM-assisted adversarial medical MCQ generator.",
    )
    parser.add_argument("--seed-pool", required=True, help="Path to seed pool JSONL")
    parser.add_argument("--baseline", required=True, choices=sorted(MODEL_REGISTRY),
                        help="Baseline (target) model — the one whose blind spots we're mining. This is the model the adversarial-filter step tries to fool.")
    parser.add_argument("--mutator", default=None, choices=sorted(MODEL_REGISTRY),
                        help="Mutator model — writes the adversarial questions. Typically the strongest available model. Defaults to same as --baseline if unspecified (self-adversarial), but for a strong baseline you almost always want a distinct mutator.")
    parser.add_argument("--verifiers", required=True,
                        help="Comma-separated verifier model IDs (must not include baseline or mutator)")
    parser.add_argument("--n-questions", type=int, required=True,
                        help="Target count of ACCEPTED (verified) questions")
    parser.add_argument("--output-dir", required=True,
                        help="Directory to write accepted YAMLs + trace sidecars")
    parser.add_argument("--category", choices=sorted({p["category"] for p in PATTERNS}),
                        default=None,
                        help="Restrict to patterns in this category (default: all 4 categories)")
    parser.add_argument("--seed", type=int, default=20260801, help="RNG seed")
    args = parser.parse_args(argv)

    # Resolve providers
    baseline_provider = MODEL_REGISTRY[args.baseline]()
    mutator_id = args.mutator or args.baseline
    mutator_provider = MODEL_REGISTRY[mutator_id]() if mutator_id != args.baseline else baseline_provider
    verifier_ids = _resolve_verifiers(args.verifiers, args.baseline)
    if mutator_id in verifier_ids:
        raise SystemExit(f"Mutator {mutator_id!r} must not be in verifier list.")
    verifier_providers = [MODEL_REGISTRY[v]() for v in verifier_ids]

    # Load seed pool + patterns
    seed_pool = _load_seed_pool(Path(args.seed_pool))
    if not seed_pool:
        raise SystemExit(f"Empty seed pool at {args.seed_pool}")
    patterns = get_patterns_by_category(args.category) if args.category else PATTERNS

    print(
        f"[adversemed-gen v0.1] mutator={mutator_id} baseline={args.baseline} verifiers={verifier_ids} "
        f"n_seed={len(seed_pool)} n_patterns={len(patterns)} target={args.n_questions} "
        f"out={args.output_dir}",
        file=sys.stderr,
    )

    # Run the pipeline
    attempts = generate_batch(
        seed_pool=seed_pool,
        patterns=patterns,
        mutator_provider=mutator_provider,
        baseline_provider=baseline_provider,
        verifier_providers=verifier_providers,
        n_questions=args.n_questions,
        output_dir=args.output_dir,
        seed=args.seed,
    )

    # Report acceptance rate + rejection breakdown
    n_accepted = sum(1 for c in attempts if c.passed_consensus)
    n_mutate_declined = sum(1 for c in attempts if not c.question)
    n_filter_rejected = sum(1 for c in attempts if c.kept_by_filter is False)
    n_verify_rejected = sum(1 for c in attempts if c.passed_consensus is False and c.kept_by_filter)
    accept_rate = n_accepted / len(attempts) if attempts else 0.0

    print(
        f"\n[adversemed-gen] complete: {n_accepted}/{args.n_questions} accepted "
        f"across {len(attempts)} attempts (accept rate {accept_rate:.1%})",
        file=sys.stderr,
    )
    print(
        f"  mutate declined: {n_mutate_declined} | filter rejected: {n_filter_rejected} | verify rejected: {n_verify_rejected}",
        file=sys.stderr,
    )
    print(f"  output: {args.output_dir}", file=sys.stderr)

    return 0 if n_accepted >= args.n_questions else 1


if __name__ == "__main__":
    raise SystemExit(main())
