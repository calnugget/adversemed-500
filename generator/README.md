# adversemed-gen

An LLM-assisted generator for adversarial medical multiple-choice questions where the correct behavior is *abstention*. Produces additional questions calibrated to a user-specified baseline model, giving benchmarks like [AdverseMed-500](../adversemed-500/) a self-hardening durability profile as frontier models improve.

**Status:** v0.1 (alpha) — in active development for the [AdverseMed-500 paper](https://osf.io/mehu4)
**License:** MIT (planned — repo currently private during embargo)
**Related paper:** Vallamsetty, D. (2026). *AdverseMed-500: A Benchmark to Help Researchers Vet Medical LLMs.* NeurIPS ML4H 2026 workshop submission.

## What it does

The generator turns a MedQA-style seed question into a question with a **medically-impossible premise** and confirms the mutation is (a) hard enough to fool a frontier baseline model and (b) unambiguously impossible per multi-model consensus verification against authoritative clinical sources.

Four-step pipeline per question:

1. **Mutate** — LLM re-drafts the seed to embed a false premise from one of four categories (contraindication, drug-drug interaction, impossible timing, physiological impossibility) using patterns catalogued in [`../adversemed-500/PATTERNS.md`](../adversemed-500/PATTERNS.md).
2. **Adversarial filter** — submit the mutated question to a target baseline model; keep only mutations that fool the baseline into picking a listed option (or into low-confidence abstention).
3. **Multi-model consensus verify** — 3 non-baseline verifier models must independently agree the premise is medically impossible per the cited authoritative source.
4. **Emit** — YAML matching the hand-verified AdverseMed-500 item schema, with full generation trace as sidecar for auditability.

## Usage

```bash
pip install -e .

adversemed-gen \
  --seed-pool ../datasets/adversemed_seed_pool_n500.jsonl \
  --patterns ../adversemed-500/PATTERNS.md \
  --baseline claude-sonnet-4-bedrock \
  --verifiers gpt-5.4-mini,gemini-2.5-pro,deepseek-chat \
  --n-questions 200 \
  --output-dir generated_questions/ \
  --seed 20260801
```

## Why "self-hardening"

Traditional benchmarks are fixed corpora that grow stale as frontier models train against them (contamination) or exceed their difficulty ceiling (saturation). The generator gives every future user the ability to produce a fresh, uncontaminated, difficulty-matched test set for their own baseline model. The specific 500 hand-verified questions in AdverseMed-500 serve as reference/citation anchor; the generator keeps the benchmark useful as frontier models improve.

## Design docs

- [`DESIGN.md`](DESIGN.md) — architecture, prompt design decisions, verifier-consensus rationale
- [`../PROTOCOL.md`](../PROTOCOL.md) §3 — original paper design + Experiment B validation plan

## Validation

Experiment B (per PROTOCOL §3): 200 generator-produced questions vs a matched 200-question sample from the hand-verified AdverseMed-500 reference set. Compared distributions:

- Per-model failure rate (5 frontier LLMs)
- Category distribution (χ² test)
- Reference density
- Inter-annotator agreement of verifier models (Fleiss' κ)

Results in [`experiments/experiment_b_report.md`](experiments/experiment_b_report.md) *(pending — TASK_22 §4.6)*.

## Citation

*(To be filled at Zenodo DOI mint — TASK_22 §4.7.)*
