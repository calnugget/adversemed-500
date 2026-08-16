"""adversemed-gen — LLM-assisted adversarial medical MCQ generator.

Public API (importable as `from adversemed_gen import ...`):
    generate_one     — full 4-step pipeline for a single question
    generate_batch   — batch driver
    Candidate        — the intermediate dataclass carried between steps
    GenerationTrace  — full per-question audit trail (mutator + baseline + verifier responses)
    __version__

CLI (`adversemed-gen ...`) — see `cli.py`.
"""
from __future__ import annotations

__version__ = "0.1.0"

from .pipeline import Candidate, GenerationTrace, generate_batch, generate_one

__all__ = ["Candidate", "GenerationTrace", "generate_batch", "generate_one", "__version__"]
