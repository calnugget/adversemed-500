"""Pipeline orchestrator + shared dataclasses. Chains mutate → filter → verify → emit."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Candidate:
    """Intermediate object flowing through the 4 steps.

    After mutate: question/choices/premise_description/reference populated.
    After filter: baseline_response populated; kept flag set.
    After verify: verifier_responses populated; passed_consensus flag set.
    After emit: yaml_path populated.
    """
    seed_index: int
    category: str                                    # contraindication | drug_drug_interaction | impossible_timing | physiological_impossibility
    difficulty: str                                  # obvious | subtle | expert (initial guess; refined post-verify)
    pattern_name: str                                # from PATTERNS.md
    question: str = ""
    choices: dict[str, str] = field(default_factory=dict)
    premise_description: str = ""
    reference_suggestion: str = ""

    baseline_response: dict = field(default_factory=dict)  # {"chosen_answer": ..., "confidence": ..., "raw_text": ...}
    kept_by_filter: Optional[bool] = None
    filter_reason: Optional[str] = None

    verifier_responses: list[dict] = field(default_factory=list)  # per-verifier: {"model": ..., "verdict": YES/NO, "raw_text": ...}
    passed_consensus: Optional[bool] = None
    consensus_reason: Optional[str] = None

    yaml_path: Optional[str] = None
    generation_trace_path: Optional[str] = None


@dataclass
class GenerationTrace:
    """Full audit trail persisted alongside each generated question.

    Written as JSON sidecar next to the YAML output. Lets any downstream user
    re-verify a generated question end-to-end without re-running the pipeline.
    """
    candidate: dict                                  # asdict(Candidate)
    mutate_prompt_hash: str
    mutate_prompt_version: str
    baseline_model_id: str
    baseline_provider: str
    baseline_call_wall_ms: int
    verifier_prompt_hash: str
    verifier_prompt_version: str
    verifiers: list[dict]                            # per-verifier: model_id, provider, wall_ms
    seed: int
    generator_version: str
    generated_at: str                                # ISO


def generate_one(
    seed_row: dict,
    pattern: dict,
    baseline_provider: Any,
    verifier_providers: list[Any],
    category: str,
    difficulty_hint: str = "subtle",
    seed: int = 20260801,
) -> Candidate:
    """Full 4-step pipeline for one question.

    Args:
        seed_row: one row from adversemed_seed_pool_n500.jsonl
        pattern: one pattern dict parsed from PATTERNS.md (has .name, .template, .category_hint)
        baseline_provider: a Provider instance (from _pipeline/providers/)
        verifier_providers: list of 3 Provider instances (must not include baseline)
        category: target false-premise category
        difficulty_hint: initial difficulty target; refined post-verify

    Returns: a Candidate with all pipeline-step fields populated. Even rejected
    candidates are returned (with kept_by_filter=False or passed_consensus=False)
    so the caller can log rejection rates.

    NOT YET IMPLEMENTED — will fill in TASK_22 §4.1-4.4.
    """
    from .mutate import mutate_seed
    from .filter import adversarial_filter
    from .verify import consensus_verify
    from .emit import emit_yaml

    cand = mutate_seed(seed_row, pattern, category, difficulty_hint, baseline_provider, seed=seed)
    if not cand.question:
        return cand
    adversarial_filter(cand, baseline_provider)
    if not cand.kept_by_filter:
        return cand
    consensus_verify(cand, verifier_providers)
    if not cand.passed_consensus:
        return cand
    emit_yaml(cand, output_dir="generated_questions/")
    return cand


def generate_batch(
    seed_pool: list[dict],
    patterns: list[dict],
    mutator_provider: Any,
    baseline_provider: Any,
    verifier_providers: list[Any],
    n_questions: int,
    output_dir: str,
    seed: int = 20260801,
    progress_stream: Any = None,
) -> list[Candidate]:
    """Generate up to n_questions by cycling through (seed × pattern) combos.

    Args:
        seed_pool: list of MedQA rows (from adversemed_seed_pool_n500.jsonl)
        patterns: list of pattern dicts (from patterns.PATTERNS)
        baseline_provider: Provider for the adversarial filter step
        verifier_providers: 3 non-baseline Providers for consensus verify
        n_questions: target count of ACCEPTED (verified) questions
        output_dir: where to write accepted YAMLs + trace sidecars
        seed: RNG seed for shuffling
        progress_stream: file-like for progress prints (default stderr)

    Returns: list of ALL attempted candidates (accepted + rejected). Caller
    can inspect acceptance rate + rejection reasons.

    Progress: prints one line per attempt to progress_stream. Writes
    accepted YAMLs incrementally so progress survives crashes.
    """
    import random
    import sys as _sys

    from .emit import emit_yaml
    from .filter import adversarial_filter
    from .mutate import mutate_seed
    from .verify import consensus_verify

    if progress_stream is None:
        progress_stream = _sys.stderr

    rng = random.Random(seed)
    verifier_model_ids = [p.model_id for p in verifier_providers]
    baseline_model_id = baseline_provider.model_id

    attempts: list[Candidate] = []
    n_accepted = 0
    max_attempts = n_questions * 5  # 20% expected accept rate ceiling; abort if we exceed

    # Shuffle so we don't always pick the same seed × pattern early
    seed_indices = list(range(len(seed_pool)))
    pattern_indices = list(range(len(patterns)))
    rng.shuffle(seed_indices)
    rng.shuffle(pattern_indices)

    idx = 0
    while n_accepted < n_questions and idx < max_attempts:
        seed_row = seed_pool[seed_indices[idx % len(seed_pool)]]
        pattern = patterns[pattern_indices[idx % len(patterns)]]
        category = pattern["category"]
        difficulty_hint = "subtle"  # default; could be pattern-driven or randomized
        idx += 1

        print(
            f"[gen {idx}/{max_attempts}] pattern={pattern['name']:32s} "
            f"seed={seed_row.get('question_id', '?'):24s} accepted={n_accepted}/{n_questions}",
            file=progress_stream,
            flush=True,
        )

        # Step 1: mutate (via mutator_provider — typically the strongest available model)
        cand = mutate_seed(seed_row, pattern, category, difficulty_hint, mutator_provider, seed=seed)
        attempts.append(cand)
        if not cand.question:
            print(f"  → mutate DECLINE: {cand.premise_description[:100]}", file=progress_stream)
            continue

        # Step 2: adversarial filter
        adversarial_filter(cand, baseline_provider)
        if not cand.kept_by_filter:
            print(f"  → filter REJECT: {cand.filter_reason}", file=progress_stream)
            continue

        # Step 3: consensus verify
        consensus_verify(cand, verifier_providers)
        if not cand.passed_consensus:
            print(f"  → verify REJECT: {cand.consensus_reason}", file=progress_stream)
            continue

        # Step 4: emit
        try:
            path = emit_yaml(cand, output_dir, baseline_model_id, verifier_model_ids)
            n_accepted += 1
            print(f"  → ACCEPTED (yaml: {path.name})", file=progress_stream)
        except Exception as e:
            print(f"  → emit ERROR: {e!r}", file=progress_stream)

    return attempts
