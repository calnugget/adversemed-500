"""DeepSeek provider — uses OpenAI-compatible API at api.deepseek.com."""
from __future__ import annotations

import re
import time
from typing import Optional

from .base import InferenceResponse, Provider


class DeepSeekProvider(Provider):
    model_id = "DeepSeek-Chat"
    provider_id = "DeepSeek"
    # Pricing verified 2026-07-06 (deepseek.com/pricing): $0.14 in, $0.28 out per 1M tokens = per 1k = $0.00014/$0.00028
    input_cost_per_1k_usd = 0.00014
    output_cost_per_1k_usd = 0.00028
    supports_logprobs = True

    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1", model: str = "deepseek-chat"):
        from openai import OpenAI  # DeepSeek uses OpenAI-compatible SDK
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._api_model = model

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
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
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

        # Log-probability of the chosen answer token if requested — pass the raw
        # token that actually appeared in the response (letter or "FLAG"), not the
        # semantic answer, because logprob tokens match the literal output.
        log_prob = None
        if return_logprobs and choice.logprobs and choice.logprobs.content:
            log_prob = _extract_answer_logprob(choice.logprobs.content, raw_token)

        # Cost
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


# --- Response parsing helpers ---------------------------------------------

_ANSWER_RE = re.compile(r"ANSWER:\s*([A-E]|FLAG)\b", re.IGNORECASE)
_CONF_RE = re.compile(r"CONFIDENCE:\s*(0\.\d+|1\.0|1|0)")


def _parse_answer_and_confidence(text: str) -> tuple[str, Optional[float], str]:
    """Extract ANSWER token and CONFIDENCE from a model response.

    Returns (semantic_answer, verbal_confidence, raw_token) where:
      - semantic_answer is the answer for scoring: "A"..."E" or "abstain" or "parse_failure"
      - raw_token is the literal string the model emitted after "ANSWER:" (letter or "FLAG"),
        used for locating the corresponding token in the API's logprobs stream. Empty if parse failed.
    """
    a_match = _ANSWER_RE.search(text)
    c_match = _CONF_RE.search(text)
    if not a_match:
        return "parse_failure", None, ""
    raw_token = a_match.group(1).upper()
    letter = "abstain" if raw_token == "FLAG" else raw_token
    conf: Optional[float] = None
    if c_match:
        try:
            conf = float(c_match.group(1))
            if conf < 0.0 or conf > 1.0:
                conf = None
        except ValueError:
            conf = None
    return letter, conf, raw_token


def _extract_answer_logprob(content_logprobs: list, raw_token: str) -> Optional[float]:
    """Find the token in the logprobs stream that matches the raw ANSWER token
    (letter A/B/C/D/E or "FLAG") and return its log-probability."""
    if not raw_token:
        return None
    for token_info in content_logprobs:
        tok = token_info.token.strip().upper()
        if tok == raw_token or tok.startswith(raw_token):
            return token_info.logprob
    return None
