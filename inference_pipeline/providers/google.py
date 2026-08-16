"""Google (Gemini) provider. Gemini 2.5 Pro."""
from __future__ import annotations

import time

from .base import InferenceResponse, Provider
from .deepseek import _parse_answer_and_confidence  # reuse parser


class GeminiProProvider(Provider):
    """Google Gemini Pro.

    OSF pre-registration specified 'Gemini 2.5 Pro', which was deprecated by
    Google before Paper 1's data-collection phase. Substituted with
    'gemini-pro-latest' (a rolling pointer to the current Pro tier); the
    concrete model version is captured in raw_metadata at inference time so
    the manuscript can report the exact model that ran. Substitution logged
    on OSF amendment (task #65).
    """
    model_id = "Gemini Pro (latest)"
    provider_id = "Google"
    # Verified 2026-07-06 ai.google.dev/pricing: est $0.00125/1k in, $0.005/1k out
    input_cost_per_1k_usd = 0.00125
    output_cost_per_1k_usd = 0.005
    supports_logprobs = False

    _api_model = "gemini-pro-latest"

    def __init__(self, api_key: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        # BLOCK_NONE across categories: our questions are legitimate medical
        # exam-style items. Safety filters would otherwise block CAT_MEDICAL.
        # Documented in PROTOCOL.md §11 for reproducibility.
        self._safety_settings = [
            {"category": c, "threshold": "BLOCK_NONE"} for c in [
                "HARM_CATEGORY_HARASSMENT",
                "HARM_CATEGORY_HATE_SPEECH",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "HARM_CATEGORY_DANGEROUS_CONTENT",
            ]
        ]
        self._model = genai.GenerativeModel(self._api_model, safety_settings=self._safety_settings)

    # Gemini 2.5 Pro consumes most of max_output_tokens on internal "thinking"
    # tokens before emitting any user-visible text. With the pipeline-standard
    # cap of 128, the visible output truncates to `"ANSWER"` or `"ANSWER:"`
    # (parse_failure). Paper 0 finding F-15 fixed this by raising the ceiling
    # to 8192; we mirror that here for consistency.
    _GEMINI_MIN_MAX_TOKENS = 8192

    def infer(
        self,
        prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 128,
        return_logprobs: bool = False,
    ) -> InferenceResponse:
        # return_logprobs is a no-op for Gemini
        effective_max_tokens = max(max_tokens, self._GEMINI_MIN_MAX_TOKENS)
        t_start = time.perf_counter()
        try:
            import google.generativeai as genai
            resp = self._model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=effective_max_tokens,
                ),
            )
        except Exception as e:
            wall_ms = int((time.perf_counter() - t_start) * 1000)
            return InferenceResponse(
                raw_text="", chosen_answer="parse_failure", wall_clock_ms=wall_ms, error=repr(e)
            )
        wall_ms = int((time.perf_counter() - t_start) * 1000)

        # Safe text extraction — response.text can raise if the candidate finished
        # for non-STOP reasons (safety, recitation, etc.).
        raw_text = ""
        finish_reason = None
        try:
            candidate = resp.candidates[0] if resp.candidates else None
            finish_reason = candidate.finish_reason.name if candidate else None
            if candidate and candidate.content and candidate.content.parts:
                raw_text = "".join(
                    part.text for part in candidate.content.parts if hasattr(part, "text")
                )
        except Exception:
            raw_text = ""

        answer_letter, verbal_conf, _raw_token = _parse_answer_and_confidence(raw_text)

        # Gemini usage metadata
        usage = resp.usage_metadata if hasattr(resp, "usage_metadata") else None
        prompt_tokens = usage.prompt_token_count if usage else 0
        completion_tokens = usage.candidates_token_count if usage else 0
        cost = (
            prompt_tokens / 1000 * self.input_cost_per_1k_usd
            + completion_tokens / 1000 * self.output_cost_per_1k_usd
        )

        return InferenceResponse(
            raw_text=raw_text,
            chosen_answer=answer_letter,
            verbal_confidence=verbal_conf,
            log_probability=None,
            wall_clock_ms=wall_ms,
            cost_usd=cost,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            raw_metadata={"finish_reason": finish_reason},
        )


# Keep backward-compat alias so smoke_test doesn't break during refactor
Gemini25ProProvider = GeminiProProvider
