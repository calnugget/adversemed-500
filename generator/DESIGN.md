# adversemed-gen — design

Design decisions and rationale for the 4-step pipeline.

## Overall architecture

```
                                Seed pool           Pattern library
                                (MedQA)             (PATTERNS.md)
                                     \                /
                                      \              /
                                       v            v
              [Step 1: mutate]  ──── LLM (Sonnet 4 default) ─────┐
                                                                 v
                                              candidate {question, choices, ...}
                                                                 |
                                                                 v
              [Step 2: adversarial filter] ─── baseline model call ──┐
                                                                     |
                                     BASELINE fooled?               |
                                     (picked A/B/C/D                |
                                      OR abstained w/ low conf)     |
                                        yes ─────┐                  |
                                        no  ─────┘─→ REJECT         |
                                                                     v
              [Step 3: multi-model consensus verify] ─── 3 verifier calls ─┐
                                                                            |
                                        ALL 3 verifiers agree              |
                                        premise is impossible?             |
                                        yes ─────┐                         |
                                        no  ─────┘─→ REJECT                |
                                                                            v
              [Step 4: emit] ─── YAML matching hand-verified schema + trace sidecar
```

## Why these four steps, in this order

**Mutate first, then filter.** A single-shot "generate an adversarial question" call from one LLM is noisy — most direct outputs are either (a) not actually impossible, or (b) impossible but obvious. Separating mutation (creative) from filter (adversarial-hardness gate) makes each step more auditable. If accept rate drops, we can diagnose whether the mutator or the filter is the failure point.

**Adversarial filter before verify.** Verifying every mutation is expensive (3 verifier calls per question). Filtering first by "did this fool a frontier baseline?" is cheap (1 baseline call) and eliminates the majority of easy mutations. Only questions that pass the hardness gate consume verifier budget.

**Multi-model consensus verify, not single-model verify.** A single verifier model shares failure modes with the baseline model (if both are the same family, they might make correlated errors). Requiring **all 3 non-baseline verifiers to agree** on impossibility is a much stronger correctness signal than any single-model verification and mirrors the "3 physicians would agree" criterion from the hand-verification rubric (see [`../adversemed-500/RUBRIC.md`](../adversemed-500/RUBRIC.md) check 8).

**Emit as YAML with full trace sidecar.** Every question output has an accompanying JSON sidecar with the mutator response, baseline response, and all 3 verifier responses. This lets any downstream user audit any question end-to-end without re-running the pipeline. Critical for reproducibility given the paper's pre-registration commitment.

## Baseline vs verifier model selection

- **Baseline** (default: Claude Sonnet 4 via Bedrock proxy per Amendment #2): the "target" whose blind spots we're mining. In principle, any frontier model can be the baseline. PROTOCOL §3 originally specified Opus 4.7; Amendment #2 substituted to Sonnet 4.
- **Verifiers** (default: GPT-5.4-mini + Gemini 2.5 Pro + DeepSeek-Chat): three non-baseline models from three different provider families. Provider-family diversity reduces the chance of correlated verification errors. If the baseline is a Claude model, verifiers must not be Claude models — this keeps the "adversarial filter fooled Claude, then non-Claude models confirm impossibility" story clean.

## Pattern-driven mutation vs open-ended mutation

We use PATTERNS.md (the pattern library that grew across the 9 hand-verification batches) as a structured input to the mutator rather than asking the mutator to invent new adversarial patterns from scratch. Rationale:

1. **Pattern-driven mutation is auditable.** Every generated question traces back to a documented pattern class → easier to explain in the manuscript and easier to filter downstream.
2. **The pattern library is the paper's implicit contribution.** PATTERNS.md represents ~80 hours of the first author's hand-curation work; the generator amortizes that curation across future users.
3. **Open-ended mutation has more failure modes.** In pilots, ~50% of open-ended mutations were rejected as either "not actually impossible" or "impossibly obvious." Pattern-anchored mutation is more consistent.

Cost: the pattern library is finite (~30-40 patterns at time of paper). As the library grows via reference set updates, generator diversity grows too.

## Reference-URL handling

Mutator suggests a reference URL (e.g., DailyMed for a specific drug label). The generator does NOT auto-verify the URL is reachable and does NOT auto-verify the URL content matches the claim. This is deliberate:

- **What auto-verification would give up:** the pre-registration commitment that "every reference is opened by the first author, every YAML edited-then-saved by the first author" is what makes the hand-verified 500 the reference set. Generator-produced questions are marked as `verified_by: adversemed-gen v0.1 (...)` in the schema — this distinguishes them from `verified_by: Dyuthi Vallamsetty` and lets downstream users apply different trust levels.
- **What the multi-model consensus gives instead:** consensus that the *claim* is defensible, not that the specific URL is the right citation. If a user wants the URL-audited reference set, they use `../datasets/adversemed_500.jsonl`. If they want the self-hardening generator, they use adversemed-gen with the understanding that reference URLs are LLM-suggested rather than human-audited.

This is disclosed in the paper's §7 Limitations.

## Reproducibility

- Fixed seed via `--seed` flag propagates through mutator sampling
- Every model version pinned (Bedrock/API model IDs recorded in generator manifest)
- Every prompt file separately versioned; prompt hash logged per question
- Full generation trace sidecar per question (mutator + baseline + verifier responses)
- Container image with pinned dependencies (planned for Zenodo mint)

## Non-goals for v0.1

- Physician-audit study on generated questions → deferred to v2 revision
- Fine-tuning a specialized generator model → not committed in PROTOCOL
- Continuous CI hosting → post-paper
- Support for non-English clinical sources → out of scope for v1 (matches paper limitation)
- Support for non-MCQ formats → out of scope
