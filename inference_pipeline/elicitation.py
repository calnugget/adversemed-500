"""Confidence-elicitation methods. Each returns a normalized confidence in [0,1].

Four methods are pre-registered (OSF §7B / §7F H4). This file will grow to hold
all four; tonight it implements verbal-probability + log-probability. Self-consistency
and temperature-0 baseline will be added in Phase 2.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Optional

from .providers.base import InferenceResponse, Provider


@dataclass
class ElicitationOutput:
    method: str                    # "verbal_probability" | "log_probability" | "self_consistency" | "temperature_0"
    chosen_answer: str
    confidence: Optional[float]    # normalized to [0,1]; None if method N/A for this provider
    n_calls: int                   # how many API calls this method consumed
    total_cost_usd: float
    total_wall_ms: int
    raw_responses: list[dict] = field(default_factory=list)  # for auditing


def elicit_verbal_probability(provider: Provider, prompt: str) -> ElicitationOutput:
    """Single temp=0 call; use the CONFIDENCE the model reports in-band."""
    resp = provider.infer(prompt, temperature=0.0)
    return ElicitationOutput(
        method="verbal_probability",
        chosen_answer=resp.chosen_answer,
        confidence=resp.verbal_confidence,
        n_calls=1,
        total_cost_usd=resp.cost_usd,
        total_wall_ms=resp.wall_clock_ms,
        raw_responses=[_response_snapshot(resp)],
    )


def elicit_log_probability(provider: Provider, prompt: str) -> ElicitationOutput:
    """Single temp=0 call; confidence = exp(log P(chosen answer token))."""
    if not provider.supports_logprobs:
        # Structural N/A per pre-reg §Missing Data: providers that don't expose
        # log-probabilities produce N/A for this method. Not an error.
        return ElicitationOutput(
            method="log_probability",
            chosen_answer="",
            confidence=None,
            n_calls=0,
            total_cost_usd=0.0,
            total_wall_ms=0,
        )
    resp = provider.infer(prompt, temperature=0.0, return_logprobs=True)
    confidence = _logprob_to_confidence(resp.log_probability)
    return ElicitationOutput(
        method="log_probability",
        chosen_answer=resp.chosen_answer,
        confidence=confidence,
        n_calls=1,
        total_cost_usd=resp.cost_usd,
        total_wall_ms=resp.wall_clock_ms,
        raw_responses=[_response_snapshot(resp)],
    )


def elicit_self_consistency(provider: Provider, prompt: str, n_samples: int = 5) -> ElicitationOutput:
    """n=5 temp=0.7 samples. Confidence = fraction agreeing with majority-vote answer."""
    from collections import Counter
    responses = [provider.infer(prompt, temperature=0.7) for _ in range(n_samples)]
    valid_answers = [r.chosen_answer for r in responses if r.chosen_answer not in ("parse_failure", "")]
    if not valid_answers:
        return ElicitationOutput(
            method="self_consistency",
            chosen_answer="parse_failure",
            confidence=None,
            n_calls=n_samples,
            total_cost_usd=sum(r.cost_usd for r in responses),
            total_wall_ms=sum(r.wall_clock_ms for r in responses),
            raw_responses=[_response_snapshot(r) for r in responses],
        )
    counts = Counter(valid_answers)
    majority_answer, majority_count = counts.most_common(1)[0]
    return ElicitationOutput(
        method="self_consistency",
        chosen_answer=majority_answer,
        confidence=majority_count / n_samples,
        n_calls=n_samples,
        total_cost_usd=sum(r.cost_usd for r in responses),
        total_wall_ms=sum(r.wall_clock_ms for r in responses),
        raw_responses=[_response_snapshot(r) for r in responses],
    )


def elicit_temperature_0(provider: Provider, prompt: str) -> ElicitationOutput:
    """Single temp=0 decode; uses the CONFIDENCE the model states in-band.

    DEVIATION from PROTOCOL Sec.6, which specified a constant 1.0. The constant made
    ECE = Brier = 1 - accuracy identically, so three of the four reported statistics
    were restatements of accuracy. Disclosed in the deviations appendix. Note this
    method shares its API call with verbal_probability, so it is reported as a
    reproducibility replicate rather than an independent elicitation method.
    """
    resp = provider.infer(prompt, temperature=0.0)
    confidence = resp.verbal_confidence
    return ElicitationOutput(
        method="temperature_0",
        chosen_answer=resp.chosen_answer,
        confidence=confidence,
        n_calls=1,
        total_cost_usd=resp.cost_usd,
        total_wall_ms=resp.wall_clock_ms,
        raw_responses=[_response_snapshot(resp)],
    )


# --- Helpers --------------------------------------------------------------

# Largest positive log-probability we treat as floating-point noise rather than a
# malformed response. Empirically every out-of-range value observed in the OpenAI
# log-probability runs was an exact integer multiple of 2**-18 (the serialization
# grid), the largest being 7 * 2**-18 = 2.67e-05. A tolerance of 2**-10 is ~39x
# the largest observed excess and still ~3 orders of magnitude below the width of
# the narrowest ECE bin (0.1), so it cannot move a row between bins.
_LOGPROB_POSITIVE_TOLERANCE = 2.0 ** -10


def _logprob_to_confidence(log_probability: Optional[float]) -> Optional[float]:
    """Derive a confidence in [0,1] from a token log-probability.

    A log-probability is mathematically non-positive, so exp() of it is at most 1.
    In practice provider APIs return log-probabilities quantized onto a binary grid,
    and a token whose true probability is 1.0 can serialize as a *small positive*
    number: exp() then yields e.g. 1.0000267, which is not a valid probability.

    The earlier pipeline computed a bare exp() and left such values in the row; the
    analysis stage then discarded them with a `0.0 <= conf <= 1.0` range filter.
    That silently dropped the most-confident rows, which is exactly the wrong
    direction for a calibration metric. We instead repair the derivation: a positive
    log-probability within the quantization tolerance is clamped to 0.0 (confidence
    exactly 1.0), which is the value the provider was trying to express. A positive
    log-probability *beyond* the tolerance is not noise and is rejected as None, so a
    genuinely malformed response still cannot masquerade as certainty.
    """
    if log_probability is None:
        return None
    if math.isnan(log_probability):
        return None
    if log_probability > _LOGPROB_POSITIVE_TOLERANCE:
        return None
    return math.exp(min(log_probability, 0.0))


def _response_snapshot(resp: InferenceResponse) -> dict:
    """A JSON-safe snapshot of the response for audit trails."""
    d = asdict(resp)
    d.pop("raw_metadata", None)  # optional, keep snapshots compact
    return d
