"""OpenAI (GPT) provider. GPT-5.4-mini."""
from __future__ import annotations

import time

from .base import InferenceResponse, Provider
from .deepseek import _extract_answer_logprob, _parse_answer_and_confidence  # reuse parsers


class GPT54MiniProvider(Provider):
    """GPT-5.4-mini — OpenAI's cost-efficient frontier model."""
    model_id = "GPT-5.4-mini"
    provider_id = "OpenAI"
    # Estimates 2026-07-06 (openai.com/pricing) — adjust in PROTOCOL.md §11 if provider updates
    input_cost_per_1k_usd = 0.00015
    output_cost_per_1k_usd = 0.00060
    supports_logprobs = True  # OpenAI Chat Completions API supports logprobs

    _api_model = "gpt-5.4-mini"

    def __init__(self, api_key: str):
        from openai import OpenAI
        self._client = OpenAI(api_key=api_key)

    def infer(
        self,
        prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 128,
        return_logprobs: bool = False,
    ) -> InferenceResponse:
        t_start = time.perf_counter()
        try:
            kwargs: dict = {
                "model": self._api_model,
                "messages": [{"role": "user", "content": prompt}],
                # GPT-5.x uses max_completion_tokens; the legacy max_tokens is rejected.
                "max_completion_tokens": max_tokens,
            }
            # GPT-5.x models only accept the default temperature=1 for reasoning models.
            # We pass temperature only when the model accepts it (legacy GPT-4x path).
            if temperature is not None and not self._api_model.startswith("gpt-5"):
                kwargs["temperature"] = temperature
            if return_logprobs:
                kwargs["logprobs"] = True
                kwargs["top_logprobs"] = 5
            resp = self._client.chat.completions.create(**kwargs)
        except Exception as e:
            wall_ms = int((time.perf_counter() - t_start) * 1000)
            return InferenceResponse(
                raw_text="", chosen_answer="parse_failure", wall_clock_ms=wall_ms, error=repr(e)
            )
        wall_ms = int((time.perf_counter() - t_start) * 1000)

        choice = resp.choices[0]
        raw_text = choice.message.content or ""
        answer_letter, verbal_conf, raw_token = _parse_answer_and_confidence(raw_text)

        log_prob = None
        if return_logprobs and choice.logprobs and choice.logprobs.content:
            log_prob = _extract_answer_logprob(choice.logprobs.content, raw_token)

        prompt_tokens = resp.usage.prompt_tokens if resp.usage else 0
        completion_tokens = resp.usage.completion_tokens if resp.usage else 0
        cost = (
            prompt_tokens / 1000 * self.input_cost_per_1k_usd
            + completion_tokens / 1000 * self.output_cost_per_1k_usd
        )

        return InferenceResponse(
            raw_text=raw_text,
            chosen_answer=answer_letter,
            verbal_confidence=verbal_conf,
            log_probability=log_prob,
            wall_clock_ms=wall_ms,
            cost_usd=cost,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            raw_metadata={"finish_reason": choice.finish_reason},
        )
