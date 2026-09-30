"""Step 1: LLM-driven mutation of a seed question with an adversarial pattern.

Implements TASK_22 §4.1. Reads mutate_prompt.md (drafted by Dyuthi under TASK_23),
substitutes {{placeholder}} variables with the seed + pattern + category, calls
the mutator LLM (default Claude Opus 4.7), and parses the YAML block from the
response back into a populated Candidate.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .pipeline import Candidate

PROMPT_PATH = Path(__file__).parent / "prompts" / "mutate_prompt.md"


def _load_prompt() -> str:
    """Load the mutate_prompt.md text. Raises FileNotFoundError if missing."""
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Mutate prompt not found at {PROMPT_PATH}. Expected file authored under TASK_23."
        )
    return PROMPT_PATH.read_text()


def _substitute(prompt: str, mapping: dict[str, str]) -> str:
    """Replace {{key}} placeholders in the prompt with mapping values.

    Uses str.replace rather than str.format to avoid conflicts with braces in
    the prompt body. Any leftover {{...}} placeholder is left as-is (safer than
    silently failing on a typo)."""
    result = prompt
    for key, value in mapping.items():
        result = result.replace("{{" + key + "}}", str(value))
    return result


def _format_seed_choices(choices: Any) -> str:
    """Format seed choices as a multi-line 'A) ... B) ...' string."""
    if isinstance(choices, dict):
        return "\n".join(f"{letter}) {text}" for letter, text in choices.items())
    if isinstance(choices, list):
        return "\n".join(f"{chr(ord('A') + i)}) {c}" for i, c in enumerate(choices))
    return str(choices)


def _extract_yaml_block(raw_text: str) -> str:
    """Extract the YAML content from the mutator's response.

    The mutate_prompt.md tells the model to return YAML with no markdown fences
    and nothing before/after. In practice models sometimes add a leading
    explanation or a markdown code fence. Handle both:
      1. Strip ```yaml ... ``` fences if present
      2. Otherwise, find the first line starting with a top-level YAML key
         (question:, choices:, premise_description:, notes:) and take from there
    """
    # Case 1: markdown code fence
    fence_match = re.search(r"```(?:yaml|yml)?\s*\n(.*?)\n```", raw_text, re.DOTALL)
    if fence_match:
        return fence_match.group(1)
    # Case 2: find first top-level YAML key
    match = re.search(r"^(question:.*)", raw_text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1)
    return raw_text  # last resort, let yaml.safe_load complain


def mutate_seed(
    seed_row: dict,
    pattern: dict,
    category: str,
    difficulty_hint: str,
    mutator_provider: Any,
    seed: int = 20260801,
) -> Candidate:
    """Ask the mutator LLM to rewrite the seed to embed a false premise per the pattern.

    Args:
        seed_row: a row from adversemed_seed_pool_n500.jsonl. Expected keys:
                  question_id, question, choices, (optional) correct_answer.
        pattern: entry from patterns.PATTERNS. Expected keys: name, category,
                 description, source_hint, notes.
        category: target false-premise category (must match pattern['category']).
        difficulty_hint: obvious | subtle | expert.
        mutator_provider: Provider instance (from _pipeline/providers/).
        seed: RNG seed (currently unused; reserved for future sampling variants).

    Returns: Candidate with question / choices / premise_description /
    reference_suggestion populated. If the mutator DECLINEs or the response
    doesn't parse, Candidate.question stays empty and the failure reason is
    left in premise_description ("DECLINE: ...").
    """
    seed_index = int(str(seed_row.get("question_id", "0")).rsplit("_", 1)[-1] or 0)
    cand = Candidate(
        seed_index=seed_index,
        category=category,
        difficulty=difficulty_hint,
        pattern_name=pattern["name"],
    )

    # Load + substitute prompt
    template = _load_prompt()
    mapping = {
        "seed_question": seed_row.get("question", ""),
        "seed_choices": _format_seed_choices(seed_row.get("choices", {})),
        "seed_correct": str(seed_row.get("correct_answer", "unknown")),
        "target_category": category,
        "difficulty_hint": difficulty_hint,
        "pattern_name": pattern["name"],
        "pattern_description": pattern["description"],
        "pattern_notes": pattern.get("notes", ""),
    }
    prompt = _substitute(template, mapping)

    # Call the mutator (temp=0.7 for creative mutation; max_tokens generous for
    # a full YAML block with multi-line vignette).
    resp = mutator_provider.infer(prompt, temperature=0.7, max_tokens=2048)

    if resp.error or not resp.raw_text:
        cand.premise_description = f"DECLINE: mutator API error: {resp.error}"
        return cand

    # Extract + parse YAML
    yaml_text = _extract_yaml_block(resp.raw_text)
    try:
        parsed = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        cand.premise_description = f"DECLINE: mutator YAML parse error: {e!r}. Raw: {resp.raw_text[:300]!r}"
        return cand

    if not isinstance(parsed, dict):
        cand.premise_description = f"DECLINE: mutator returned non-dict YAML: {type(parsed).__name__}. Raw: {resp.raw_text[:300]!r}"
        return cand

    # Handle DECLINE case per Dyuthi's prompt convention (question="", DECLINE: in premise_description)
    question = parsed.get("question", "").strip()
    premise = parsed.get("premise_description", "").strip()
    if not question or premise.startswith("DECLINE:"):
        cand.premise_description = premise or "DECLINE: mutator returned empty question with no reason"
        return cand

    # Populate the Candidate
    cand.question = question
    cand.choices = parsed.get("choices", {})
    cand.premise_description = premise
    reference_suggestion = parsed.get("reference_suggestion", {}) or {}
    if isinstance(reference_suggestion, dict):
        # Flatten reference_suggestion to a single string for the Candidate field
        url = reference_suggestion.get("url", "")
        section = reference_suggestion.get("section", "")
        snippet = reference_suggestion.get("snippet", "")
        cand.reference_suggestion = f"{url} | {section} | {snippet}".strip(" |")
    else:
        cand.reference_suggestion = str(reference_suggestion)

    return cand
