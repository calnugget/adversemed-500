"""Step 3: multi-model consensus verification.

Implements TASK_22 §4.3. For each of 3 non-baseline verifier models, load
verify_prompt.md, substitute the candidate fields, call the verifier LLM, parse
the structured VERDICT/CONFIDENCE/REASONING output, and require all 3 verifiers
to return YES for the candidate to pass consensus.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .pipeline import Candidate

PROMPT_PATH = Path(__file__).parent / "prompts" / "verify_prompt.md"

VERDICT_RE = re.compile(r"^\s*VERDICT:\s*(YES|NO)\b", re.MULTILINE | re.IGNORECASE)
CONF_RE = re.compile(r"^\s*CONFIDENCE:\s*(0\.\d+|1\.0|1|0)", re.MULTILINE)
REASONING_RE = re.compile(r"^\s*REASONING:\s*(.+?)(?:$|\n\n)", re.MULTILINE | re.DOTALL)


def _load_prompt() -> str:
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Verify prompt not found at {PROMPT_PATH}. Expected file authored under TASK_23."
        )
    return PROMPT_PATH.read_text()


def _substitute(prompt: str, mapping: dict[str, str]) -> str:
    result = prompt
    for key, value in mapping.items():
        result = result.replace("{{" + key + "}}", str(value))
    return result


def _format_choices(choices: Any) -> str:
    if isinstance(choices, dict):
        return "\n".join(f"{letter}) {text}" for letter, text in choices.items())
    if isinstance(choices, list):
        return "\n".join(f"{chr(ord('A') + i)}) {c}" for i, c in enumerate(choices))
    return str(choices)


def _parse_verifier_response(raw_text: str) -> dict:
    """Extract VERDICT / CONFIDENCE / REASONING from a verifier's response.

    Returns dict with keys: verdict (YES/NO/None), confidence (float/None),
    reasoning (str). None values indicate parse failure.
    """
    v = VERDICT_RE.search(raw_text)
    c = CONF_RE.search(raw_text)
    r = REASONING_RE.search(raw_text)
    verdict = v.group(1).upper() if v else None
    confidence = float(c.group(1)) if c else None
    reasoning = r.group(1).strip() if r else ""
    return {"verdict": verdict, "confidence": confidence, "reasoning": reasoning}


def _split_reference_suggestion(ref_string: str) -> tuple[str, str, str]:
    """Split the 'url | section | snippet' string set by mutate.py."""
    parts = [p.strip() for p in ref_string.split("|")]
    while len(parts) < 3:
        parts.append("")
    return parts[0], parts[1], parts[2]


def consensus_verify(candidate: Candidate, verifier_providers: list[Any]) -> Candidate:
    """Submit candidate to n non-baseline verifier models; set candidate.passed_consensus.

    Consensus rule: ALL verifiers must return VERDICT: YES with parseable output.
    Any verifier returning NO, parse failure, or API error → fails consensus.

    Mutates candidate in place and returns it. Populates
    candidate.verifier_responses with per-verifier details for the trace sidecar.
    """
    if not verifier_providers:
        candidate.passed_consensus = False
        candidate.consensus_reason = "no verifiers provided"
        return candidate

    template = _load_prompt()
    ref_url, ref_section, ref_snippet = _split_reference_suggestion(candidate.reference_suggestion)
    mapping = {
        "candidate_question": candidate.question,
        "candidate_choices": _format_choices(candidate.choices),
        "candidate_premise_description": candidate.premise_description,
        "candidate_reference_url": ref_url,
        "candidate_reference_section": ref_section,
        "candidate_reference_snippet": ref_snippet,
    }
    prompt = _substitute(template, mapping)

    all_yes = True
    reasons: list[str] = []

    for provider in verifier_providers:
        resp = provider.infer(prompt, temperature=0.0, max_tokens=256)
        row = {
            "model_id": provider.model_id,
            "provider_id": provider.provider_id,
            "raw_text": resp.raw_text,
            "wall_ms": resp.wall_clock_ms,
            "cost_usd": resp.cost_usd,
            "error": resp.error,
        }
        if resp.error:
            row["verdict"] = None
            row["confidence"] = None
            row["reasoning"] = f"API error: {resp.error[:200]}"
            all_yes = False
            reasons.append(f"{provider.model_id}: API error")
        else:
            parsed = _parse_verifier_response(resp.raw_text)
            row.update(parsed)
            if parsed["verdict"] != "YES":
                all_yes = False
                verdict_repr = parsed["verdict"] or "parse_failure"
                reasons.append(f"{provider.model_id}: {verdict_repr}")
        candidate.verifier_responses.append(row)

    candidate.passed_consensus = all_yes
    if all_yes:
        candidate.consensus_reason = f"all {len(verifier_providers)} verifiers YES"
    else:
        candidate.consensus_reason = f"consensus failed: {'; '.join(reasons)}"
    return candidate
