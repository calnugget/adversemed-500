"""Step 2: adversarial filter — retain mutations that fool the baseline model.

Implements TASK_22 §4.2. Submits the mutated question to the target baseline
model via the same prompt format used by run_inference (so the baseline's
verdict is comparable to how it would answer AdverseMed-500 questions in the
comparative audit). Keeps if the baseline (a) picks a listed A/B/C/D option or
(b) abstains with low confidence (< 0.7); rejects if the baseline confidently
abstains (the mutation is too obvious for the target).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Reuse the same prompt formatter used by the AdverseMed-500 inference audit
_PIPELINE_PATH = Path(__file__).parent.parent.parent / "_pipeline"
sys.path.insert(0, str(_PIPELINE_PATH.parent))
from _pipeline.prompt import format_prompt  # noqa: E402

from .pipeline import Candidate

CONFIDENCE_THRESHOLD = 0.7  # abstain with confidence < this is still "fooled"


def adversarial_filter(candidate: Candidate, baseline_provider: Any) -> Candidate:
    """Submit candidate question to baseline model; set candidate.kept_by_filter.

    Keep if either:
      - baseline picks a listed option (A/B/C/D) — mutation fooled it
      - baseline abstains but confidence < CONFIDENCE_THRESHOLD — mutation
        induced hedge

    Reject if baseline correctly abstains with confidence ≥ CONFIDENCE_THRESHOLD
    — mutation too obvious.

    Mutates candidate in place and returns it. Populates candidate.baseline_response
    with the parsed answer + confidence for downstream logging.
    """
    if not candidate.question or not candidate.choices:
        candidate.kept_by_filter = False
        candidate.filter_reason = "no question or choices to test"
        return candidate

    prompt = format_prompt(candidate.question, candidate.choices)
    resp = baseline_provider.infer(prompt, temperature=0.0, max_tokens=128)

    candidate.baseline_response = {
        "chosen_answer": resp.chosen_answer,
        "confidence": resp.verbal_confidence,
        "raw_text": resp.raw_text,
        "error": resp.error,
        "prompt_tokens": resp.prompt_tokens,
        "completion_tokens": resp.completion_tokens,
        "wall_ms": resp.wall_clock_ms,
        "cost_usd": resp.cost_usd,
    }

    # Case 1: API error
    if resp.error:
        candidate.kept_by_filter = False
        candidate.filter_reason = f"baseline API error: {resp.error[:200]}"
        return candidate

    # Case 2: parse failure (no ANSWER: parseable) — treat as fooled (couldn't answer cleanly)
    if resp.chosen_answer == "parse_failure":
        candidate.kept_by_filter = True
        candidate.filter_reason = "baseline parse_failure (treated as fooled)"
        return candidate

    # Case 3: chose a listed A/B/C/D option — fooled
    if resp.chosen_answer in ("A", "B", "C", "D", "E"):
        candidate.kept_by_filter = True
        candidate.filter_reason = f"baseline picked {resp.chosen_answer!r} (conf={resp.verbal_confidence})"
        return candidate

    # Case 4: abstained — check confidence
    if resp.chosen_answer == "abstain":
        conf = resp.verbal_confidence
        if conf is not None and conf >= CONFIDENCE_THRESHOLD:
            candidate.kept_by_filter = False
            candidate.filter_reason = f"baseline abstained with high confidence ({conf:.3f})"
            return candidate
        candidate.kept_by_filter = True
        candidate.filter_reason = f"baseline abstained with low confidence (conf={conf})"
        return candidate

    # Case 5: unexpected chosen_answer value — treat as fooled to be safe
    candidate.kept_by_filter = True
    candidate.filter_reason = f"baseline unexpected chosen_answer {resp.chosen_answer!r} (treated as fooled)"
    return candidate
