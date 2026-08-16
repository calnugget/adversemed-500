# adversemed-gen v0.1 — known limitations

## The pattern-difficulty vs baseline-strength gap

**Observed 2026-08-01 in the first live smoke test (15 attempts, contraindication category, Opus mutator, Haiku baseline):**

- 7 attempts declined by the mutator (Opus correctly refused patterns that didn't fit the seed vignette — desired behavior per prompt)
- 8 attempts passed the mutator but were rejected by the filter (Haiku abstained with 0.95 confidence on every mutation — correctly caught the impossibility)
- 0 attempts reached the verify step
- 0 questions emitted → 0% accept rate

**Root cause.** The v0.1 pattern library contains 19 hand-curated patterns, dominated by "obvious"-tier contraindications (MMR pregnancy, isotretinoin pregnancy, ACE-I pregnancy, dapsone+G6PD, etc.). These are exactly the patterns every frontier model has seen many times in training and catches with high confidence. When the baseline is a competent model (Haiku 80%+ on hand-verified obvious contras), the generator's adversarial-filter step correctly rejects nearly every mutation as "too obvious."

**This is the design working as intended, not a bug.** The generator is telling us: "the patterns you gave me are not adversarial against this baseline." That's a real signal for a benchmark-hardening pipeline.

## Three fixes for v0.2

To make adversemed-gen practically useful for hardening top-tier models (Opus, Gemini), one or more of these needs to happen:

### 1. Expand the pattern library toward subtle-and-expert tier

The 19 v0.1 patterns are ~80% "obvious" tier — the pharmacogenomic tail (DPYD deficiency + 5-FU; HLA-B*57:01 + abacavir; nevirapine + CD4>250 women), the pregnancy-Category-X ERAs (ambrisentan, macitentan, riociguat), the vaccinia-family contras, and other subtle patterns from `adversemed-500/PATTERNS.md` need to be added.

Estimated: add 40-60 patterns from the PATTERNS.md tail. Roughly 4 hours of manual curation.

### 2. Loosen the confidence threshold OR switch to answer-only

Current filter rule: reject if baseline abstains at confidence ≥ 0.7.

Alternative rule: reject only if baseline abstains at confidence ≥ 0.95, OR reject only if baseline picks the abstain option regardless of confidence. Different threshold changes the semantic definition of "fooled."

Estimated: 1-line change to `filter.py`. Trade-off: looser threshold accepts weaker mutations.

### 3. Iterative multi-turn mutation

The v0.1 mutator gets one shot per (seed × pattern) attempt. A v0.2 mutator could be told "your first mutation was caught by the baseline; here's the baseline's response — try again, harder." This produces stronger adversarial questions but 3-5× the API cost per accepted question.

Estimated: substantial refactor. Defer to v0.3+.

## Interim usage guidance

**For hardening a bottom-tier model** (DeepSeek, GPT-5.4-mini): v0.1 should work as-is. Their hand-verified accuracy is 72-78%, so mutations that Haiku catches at 0.95 confidence will likely fool them below the 0.7 threshold. Try:

```bash
adversemed-gen --seed-pool datasets/adversemed_seed_pool_n500.jsonl \
  --mutator claude-opus-4-7 \
  --baseline deepseek-chat \
  --verifiers gpt-5.4-mini,gemini-2.5-pro,claude-haiku-4-5 \
  --n-questions 20 \
  --output-dir generated_questions/deepseek_hardening/
```

**For hardening a top-tier model** (Opus, Gemini): v0.1 pattern library is insufficient. Wait for v0.2 with expanded patterns.

## Impact on Paper 1 Experiment B

PROTOCOL §3 originally called for Experiment B validation with Claude Opus 4.7 as target baseline. With v0.1 and Opus baseline, we'd need many hours of attempts to get 200 accepted questions — the accept rate is too low.

**Recommended Experiment B scope for v1 manuscript:**

- Baseline: **Claude Haiku 4.5** (representative mid-tier target — the smaller Claude, where adversemed-gen is most immediately practical)
- Mutator: Claude Opus 4.7
- Verifiers: GPT-5.4-mini + Gemini 2.5 Pro + DeepSeek-Chat
- Target: 200 accepted questions
- Estimated cost: $10-25 depending on final accept rate

Report in §5.7:
- Actual accept rate (data-driven; likely 5-15%)
- Per-model failure rate on gen-200 vs hand-verified-200 matched sample
- Category distribution χ² test
- Reference density
- Fleiss' κ across the 3 verifiers on both sets

Frame the accept-rate observation as a **methodology finding**: the v0.1 pattern library saturates on top-tier baselines but produces useful hardening data for mid-tier targets. v0.2 pattern expansion is future work.
