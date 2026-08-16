"""Common provider interface. Every model wrapper implements this."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class InferenceResponse:
    """One response from one API call. All fields populated by the provider."""
    raw_text: str
    chosen_answer: str            # "A"/"B"/... or "abstain" or "parse_failure"
    verbal_confidence: Optional[float] = None
    log_probability: Optional[float] = None  # log P(chosen answer token)
    wall_clock_ms: int = 0
    cost_usd: float = 0.0
    error: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    raw_metadata: dict = field(default_factory=dict)


class Provider(ABC):
    """Every provider adapter subclasses this."""
    model_id: str        # canonical model name we use in outputs (e.g. "DeepSeek-Chat")
    provider_id: str     # provider identifier ("Anthropic"/"OpenAI"/"Google"/"DeepSeek")
    # Provider-published $ per 1K tokens (as of protocol version — see PROTOCOL.md §11)
    input_cost_per_1k_usd: float
    output_cost_per_1k_usd: float
    supports_logprobs: bool

    @abstractmethod
    def infer(
        self,
        prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 128,
        return_logprobs: bool = False,
    ) -> InferenceResponse:
        """Submit ONE prompt, get ONE response back."""
        raise NotImplementedError
