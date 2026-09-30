"""Step 4: emit YAML matching hand-verified schema + JSON trace sidecar.

Implements TASK_22 §4.4. For candidates that passed both filter and consensus,
write a YAML file to output_dir matching the AdverseMed-500 hand-verified
schema, plus a JSON sidecar with the full generation trace (mutator response +
baseline response + all verifier responses) for downstream reproducibility.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

from . import __version__
from .pipeline import Candidate, GenerationTrace


def _slugify(text: str, max_len: int = 40) -> str:
    """Turn 'A 32-year-old woman ...' into 'a_32_year_old_woman' for filenames."""
    s = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    s = re.sub(r"[\s-]+", "_", s)
    return s[:max_len].rstrip("_")


def _filename_for(candidate: Candidate) -> str:
    """Return 'gen_<seed_index>_<slug>' base name (no extension)."""
    first_line = (candidate.question or "gen").splitlines()[0]
    slug = _slugify(first_line) or "gen"
    return f"gen_{candidate.seed_index:04d}_{slug}"


def emit_yaml(
    candidate: Candidate,
    output_dir: str | Path,
    baseline_model_id: str = "",
    verifier_model_ids: list[str] | None = None,
) -> Path:
    """Write candidate as YAML matching AdverseMed-500 schema; write .trace.json sidecar.

    Args:
        candidate: a Candidate that passed both filter and consensus.
        output_dir: directory to write into. Created if missing.
        baseline_model_id: name of the baseline used (for verified_by field).
        verifier_model_ids: names of verifiers used (for verified_by field).

    Returns: Path to the written YAML file. Sidecar is at same path with
    `.trace.json` extension.
    """
    if not candidate.passed_consensus:
        raise ValueError(
            f"emit_yaml called on candidate that did not pass consensus "
            f"(kept_by_filter={candidate.kept_by_filter}, passed_consensus={candidate.passed_consensus})"
        )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    basename = _filename_for(candidate)
    yaml_path = output_dir / f"{basename}.yaml"
    trace_path = output_dir / f"{basename}.trace.json"

    # Reference field: use whatever reference_suggestion the mutator produced,
    # noting via the verified_by field that this is generator-produced (not
    # hand-verified against the URL).
    verifier_str = ",".join(verifier_model_ids or [])
    now = datetime.now(timezone.utc).date().isoformat()

    yaml_content = {
        "seed_index": candidate.seed_index,
        "category": candidate.category,
        "difficulty": candidate.difficulty,
        "question": candidate.question,
        "choices": candidate.choices,
        "correct": "abstain",
        "premise_description": candidate.premise_description,
        "reference": [candidate.reference_suggestion or "no reference suggested"],
        "verified_by": f"adversemed-gen v{__version__} (baseline={baseline_model_id}, verifiers={verifier_str})",
        "verified_at": now,
        "generator_metadata": {
            "pattern_name": candidate.pattern_name,
            "baseline_response": {
                "chosen_answer": candidate.baseline_response.get("chosen_answer"),
                "confidence": candidate.baseline_response.get("confidence"),
            },
            "verifier_verdicts": [
                {
                    "model_id": v.get("model_id"),
                    "verdict": v.get("verdict"),
                    "confidence": v.get("confidence"),
                }
                for v in candidate.verifier_responses
            ],
        },
    }

    with yaml_path.open("w") as f:
        yaml.safe_dump(yaml_content, f, sort_keys=False, allow_unicode=True, default_flow_style=False)

    # Trace sidecar — full raw responses for reproducibility
    trace_content = asdict(GenerationTrace(
        candidate=asdict(candidate),
        mutate_prompt_hash=_hash_of("prompts/mutate_prompt.md"),
        mutate_prompt_version="v0.1",
        baseline_model_id=baseline_model_id,
        baseline_provider=candidate.baseline_response.get("error", "").__class__.__name__ if candidate.baseline_response.get("error") else "",
        baseline_call_wall_ms=int(candidate.baseline_response.get("wall_ms", 0)),
        verifier_prompt_hash=_hash_of("prompts/verify_prompt.md"),
        verifier_prompt_version="v0.1",
        verifiers=[
            {
                "model_id": v.get("model_id"),
                "provider_id": v.get("provider_id"),
                "wall_ms": v.get("wall_ms"),
            }
            for v in candidate.verifier_responses
        ],
        seed=0,
        generator_version=__version__,
        generated_at=datetime.now(timezone.utc).isoformat(),
    ))
    with trace_path.open("w") as f:
        json.dump(trace_content, f, indent=2, default=str)

    candidate.yaml_path = str(yaml_path)
    candidate.generation_trace_path = str(trace_path)
    return yaml_path


def _hash_of(rel_path: str) -> str:
    """SHA-256 of a file relative to the adversemed-gen root, for reproducibility."""
    path = Path(__file__).parent / rel_path
    if not path.exists():
        return f"missing:{rel_path}"
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]
