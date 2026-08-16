"""Phase 2 smoke test.

Runs all 4 elicitation methods on 2 MedQA questions across all 5 providers
(Claude Opus 4.7, Claude Haiku 4.5, GPT-5.4-mini, Gemini 2.5 Pro, DeepSeek-Chat).

Total: 5 providers × 2 questions × (verbal + logprob + self_consistency(n=5) + temp0) API calls
     = 5 × 2 × 8 = 80 API calls, ~$0.10 estimated.

Usage (from ~/dyuthi-research/papers/paper-1-medllm-calibration):
  source .venv/bin/activate
  python3 -m _pipeline.smoke_test
"""
from __future__ import annotations

import json
import traceback
from pathlib import Path

from _pipeline.elicitation import (
    elicit_log_probability,
    elicit_self_consistency,
    elicit_temperature_0,
    elicit_verbal_probability,
)
from _pipeline.prompt import format_prompt
from _pipeline.providers.anthropic import ClaudeHaikuProvider, ClaudeOpusProvider
from _pipeline.providers.deepseek import DeepSeekProvider
from _pipeline.providers.google import Gemini25ProProvider
from _pipeline.providers.openai import GPT54MiniProvider
from _pipeline.secrets_helper import get_secret

DATASETS = Path(__file__).parent.parent / "datasets"
N_QUESTIONS = 2


def load_providers() -> list:
    """Instantiate all 5 providers with secrets from Secret Manager."""
    return [
        ClaudeOpusProvider(get_secret("anthropic")),
        ClaudeHaikuProvider(get_secret("anthropic")),
        GPT54MiniProvider(get_secret("openai")),
        Gemini25ProProvider(get_secret("gemini")),
        DeepSeekProvider(get_secret("deepseek")),
    ]


def load_questions(n: int) -> list[dict]:
    questions: list[dict] = []
    with (DATASETS / "medqa_test_n1000.jsonl").open() as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            questions.append(json.loads(line))
    return questions


def run_one(provider, prompt: str, method_name: str, method_fn) -> tuple[str, float, str]:
    """Run ONE elicitation method on ONE question; return short status line."""
    try:
        out = method_fn(provider, prompt)
        # Structural N/A: log-probability method on a provider that doesn't support it
        if out.method == "log_probability" and not provider.supports_logprobs:
            return method_name, 0.0, f"N/A (structural — provider {provider.provider_id} lacks logprobs)"
        conf_str = f"{out.confidence:.3f}" if out.confidence is not None else "None"
        return method_name, out.total_cost_usd, (
            f"answer={out.chosen_answer!r} conf={conf_str} "
            f"({out.n_calls}calls, {out.total_wall_ms}ms, ${out.total_cost_usd:.6f})"
        )
    except Exception as e:
        return method_name, 0.0, f"ERROR: {type(e).__name__}: {str(e)[:120]}"


def main() -> int:
    print("Loading all 5 providers (fetching secrets from Secret Manager)…")
    providers = load_providers()
    print(f"  loaded: {[p.model_id for p in providers]}\n")

    questions = load_questions(N_QUESTIONS)
    print(f"Loaded {len(questions)} MedQA questions.\n")

    methods = [
        ("verbal_probability", elicit_verbal_probability),
        ("log_probability", elicit_log_probability),
        ("self_consistency(n=5)", elicit_self_consistency),
        ("temperature_0", elicit_temperature_0),
    ]

    total_cost = 0.0
    for provider in providers:
        print(f"═══ {provider.provider_id} / {provider.model_id} ═══")
        for q_idx, q in enumerate(questions, 1):
            print(f"  Q{q_idx} ({q['question_id']}) — ground truth: {q.get('ground_truth')}")
            prompt = format_prompt(q["question"], q["choices"])
            for method_name, method_fn in methods:
                _, cost, status = run_one(provider, prompt, method_name, method_fn)
                total_cost += cost
                print(f"    {method_name:24s}: {status}")
        print()

    print("=" * 60)
    print(f"PHASE 2 SMOKE TEST DONE. Total spend across all providers: ${total_cost:.4f}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
