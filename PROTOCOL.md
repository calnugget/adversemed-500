# Paper 1 — AdverseMed-500: A Benchmark to Help Researchers Vet Medical LLMs

**Working title:** *AdverseMed-500: A Benchmark to Help Researchers Vet Medical LLMs*

**Paper type:** Benchmark paper (Datasets & Benchmarks-style contribution). The paper releases two coordinated artifacts — (a) a **hand-verified reference set of 500 questions**, and (b) an **open-source generator** (`adversemed-gen`) that produces fresh adversarial questions calibrated to a user-specified baseline LLM. Together they constitute a *self-hardening* benchmark: as frontier models improve, the generator's adversarial filter automatically produces harder questions, keeping the benchmark aligned with the frontier. The 5-model validation study demonstrates that (i) the reference set discriminates between models, and (ii) generator-produced questions have comparable properties to hand-verified ones.

**Key durability design:** rather than a fixed public/private split — which requires forever hosting a private test — the self-hardening design gives every future user of the framework the ability to produce a fresh, uncontaminated, difficulty-matched test set for their own baseline model. The specific 500 hand-verified questions serve as reference/citation anchor; the generator is what keeps the benchmark useful into 2029 and beyond.

**Note on numbering:** This paper occupies the "P1" slot in Dyuthi's shipping order (her second first-authored paper after P0). It corresponds to what the master research plan calls **P2** (Medical LLM Calibration). The original P1 (agent framework comparison on drug repurposing) is deferred and may be absorbed into P6 (Negative Results in Agentic Systems) or P12 (Capstone).

**Status:** DRAFT v0 — thesis pivoted from agent comparison to calibration 2026-07-05
**First author of record:** Dyuthi Vallamsetty
**Support:** Claude Code (technical execution under Dyuthi's direction)
**Primary venue:** NeurIPS 2026 ML4H Workshop (submission deadline Sept 1 2026)
**Fallback cascade:** JMIR AI → JAMIA Open → npj Digital Medicine (rolling)
**OSF pre-registration:** [osf.io/mehu4](https://osf.io/mehu4/) — minted 2026-07-06 (embargoed; end date recorded on OSF)

---

## 1. Research question

**Can we build a comprehensive medical-question benchmark that helps researchers who rely on LLMs decide when to trust a model's answer — specifically, by testing whether the model catches medically-impossible premises rather than confidently answering broken questions?**

Sub-questions this paper answers as a validation study of the benchmark:

1. **Discrimination:** Does AdverseMed-500 discriminate meaningfully between frontier LLMs? (If all models score identically, the benchmark isn't useful.)
2. **Calibration transfer:** Does a model that appears well-calibrated on MedQA remain well-calibrated on AdverseMed-500, or does calibration collapse on false-premise questions?
3. **Elicitation robustness:** Do model rankings on AdverseMed-500 change substantively across confidence-elicitation methods (verbal, log-probability, self-consistency, temperature-0)? If yes, we tell future benchmark users which method to use.
4. **Failure taxonomy:** When a model fails on AdverseMed-500, HOW does it fail? Does it pick a listed answer confidently, hedge, refuse, or flag the premise? Reported for future users' interpretation.
5. **Category difficulty:** Which of the four false-premise categories (contraindications, DDIs, timing, physiology) are hardest across models?

**Motivation for the benchmark itself:** Researchers across biomedicine, epidemiology, and clinical AI increasingly use LLMs in their own work — for literature review, hypothesis generation, annotation, and reasoning. Existing benchmarks (MedQA, MMLU-Med, PubMedQA, MedHELM, MedAbstain) all evaluate LLMs against well-formed questions. None of them test whether a model catches an *impossible* premise, which is the failure mode most likely to silently corrupt a research pipeline. Paper 1's first author began this project after using LLMs in her own research and finding this specific gap in the tooling.

## 2. Contribution positioning (vs. existing work)

**Citation correction (from TASK_01, 2026-07-05):** the earlier draft misidentified arXiv 2603.24481 as MedAbstain. That paper is actually **MARC** (Martinez, *Multi-Agent Reasoning with Consistency Verification Improves Uncertainty Calibration in Medical MCQA*). The real MedAbstain paper is at **arXiv 2601.12471** (Machcha et al., *Knowing When to Abstain: Medical LLMs Under Clinical Uncertainty*). Both are cited below as distinct comparators.

Recent (2025–2026) related work:

| Prior work | What they measured | What they didn't measure |
|---|---|---|
| **MedHELM** (Stanford CRFM + Pacific AI, Nature Medicine 2026-01-20 + Q2 2026 leaderboard) | Broad clinical-workflow performance across 5 categories / 121 tasks / 31 datasets, with calibration as one reported axis | Cross-distribution calibration transfer; per-model calibration gap; adversarial-premise abstention |
| **MedAbstain / "Knowing When to Abstain"** (Machcha et al., arXiv 2601.12471, 2026) | MCQA abstention under explicit abstention options and missing-context perturbations, with conformal-prediction uncertainty (APS, LAC) | ECE/Brier calibration gap; cross-benchmark calibration transfer; false-premise (as distinct from missing-context) adversarial questions; confidence-elicitation method comparison |
| **MARC** (Martinez, arXiv 2603.24481, 2026) | ECE reduction on MedQA-100/250 and MedMCQA-100/250 high-disagreement subsets via multi-agent reasoning + Two-Phase Verification | Cross-distribution calibration transfer; multiple frontier LLMs; full benchmark distributions; false-premise abstention |
| **"Mind the Gap"** (arXiv 2506.10769, 2025) | Specialty-aware clinical QA calibration within-distribution | Cross-distribution transfer; adversarial-premise questions |
| **"Overconfidence and Calibration in Medical VQA"** (arXiv 2604.02543, 2026) | Medical VQA overconfidence + hallucination-aware mitigation | Text-only OOD calibration; distribution-shift calibration gap |

### Positioning paragraph (drafted in TASK_01 §7D, minted for §2 use):

MedHELM is the strongest existing comparator for Paper 1 because it evaluates frontier LLMs across a clinically grounded taxonomy of medical workflows and reports calibration alongside accuracy, robustness, and writing-style metrics. However, MedHELM scores each scenario as a fixed benchmark; it does not ask whether a model that is calibrated on MedQA remains calibrated when the question distribution shifts. MedAbstain / *Knowing When to Abstain* (arXiv 2601.12471) moves closer to Paper 1 by testing explicit abstention in medical MCQA with conformal-prediction uncertainty and missing-context perturbations, but its central outcome is abstention behavior rather than cross-distribution calibration decay. The MARC paper (arXiv 2603.24481) shows that consistency verification can reduce ECE on high-disagreement MedQA/MedMCQA subsets, but it evaluates one Qwen-based multi-agent framework rather than multiple frontier models under distribution shift. Paper 1 therefore contributes the missing measurement: **per-model calibration gap, confidence-elicitation sensitivity, and adversarial-premise abstention across standard and shifted medical question sets.**

### Novel contributions of this paper

**Primary contribution — the reference set:**

1. **AdverseMed-500** — 500 hand-verified medical multiple-choice questions with clinically-impossible false premises across four categories (contraindications, DDIs, impossible timing, physiological impossibilities). Every question hand-verified by the first author against Tier-1 clinical references (FDA labels, CDC guidelines, society standards). Every question stratified into one of three difficulty tiers (obvious / subtle / expert) for durable per-tier reporting. Released under an open license (MIT for the benchmark; CC-BY-4.0 for the accompanying analysis). **Distinct from MedAbstain's missing-context perturbations:** false-premise questions embed a medically-impossible or contraindicated premise the model should flag, not merely a missing clue.

**Durability contribution — the self-hardening generator:**

2. **`adversemed-gen`** — an open-source Python framework and CLI tool that produces adversarial medical questions calibrated to a user-specified baseline LLM. The generator takes as input: (a) the same MedQA seed pool the reference set was built from, (b) a public library of PATTERNS.md high-yield impossibility patterns, (c) a target model API endpoint. It executes a four-step pipeline per question: **mutate → adversarially filter → multi-model consensus verify → emit**. Only mutations that fool the target baseline model AND pass multi-model impossibility consensus are retained. As frontier models improve, the adversarial filter produces harder questions, keeping the benchmark difficulty aligned with the frontier. The paper releases the generator as its primary durability mechanism — the reference-set-plus-generator combination is what the paper calls a *self-hardening benchmark*.

**Supporting contributions — demonstrating the benchmark discriminates and is worth using:**

3. **The "Calibration Gap" metric** — a per-model deployment-risk score defined as `ECE(AdverseMed-500) − ECE(MedQA)`. Two-benchmark relative metric that survives even when individual questions saturate. Reusable across any benchmark pair, not just AdverseMed-500.
4. **Difficulty-tier stratification framework** — each question tagged obvious / subtle / expert. Enables per-tier reporting so saturation of the easier tiers doesn't kill the benchmark's overall discriminative power. Also produces an *inter-tier gap* metric.
5. **First head-to-head comparison of confidence-elicitation methods** on a medical benchmark — verbal probability vs. log-probability vs. self-consistency vs. temperature-0 — with ranking-stability analysis via Kendall's τ. Tells future benchmark users which elicitation method to report.
6. **Multi-model comparative audit** — 5 frontier LLMs (Claude Opus 4.7, Claude Haiku 4.5, GPT-5.4-mini, Gemini 2.5 Pro, DeepSeek-Chat) evaluated on the reference set. Provides the first cross-provider baseline.
7. **Generator validation experiment** — using Claude Opus 4.7 as the baseline, generate 200 candidate adversarial questions. Compare their measured properties (per-model failure rate, category distribution, reference-verification density) against the 500 hand-verified questions. Demonstrates the generator produces questions of comparable quality.
8. **Public release with usage guide** — release policy, license (MIT for the benchmark; MIT for the generator code; CC-BY-4.0 for the accompanying analysis), reproducibility bundle, GitHub repo, Zenodo DOI, and a "how to use AdverseMed-500 and `adversemed-gen` in your own research" section (§ Usage in the manuscript). Makes both the reference set and the framework adoptable.

### Additional related-work threads to be integrated (surfaced in TASK_01)

- **Elicitation methods:** Tian et al. 2023 ("Just ask for calibration"), Xiong et al. 2023 ("Can LLMs express their uncertainty?"), Guo et al. 2017 (core ECE citation).
- **Abstention taxonomy:** AbstentionBench (Kirichenko et al. 2025) — cited when defining AdverseMed-500's false-premise category vs. other abstention regimes.
- **Conformal prediction:** Angelopoulos and Bates 2021 — cited as background for MedAbstain's methodology.
- **Meta-critique of medical benchmarks:** Raji, Daneshjou, Alsentzer, "It's time to bench the medical exam benchmark" (NEJM AI 2025).

## 3. Design

Two coordinated experiments in a single paper:

**Experiment A — the reference-set validation study (primary).** Cross-sectional benchmark study. Each of 5 LLMs is evaluated on 4 question sets: 3 standard benchmarks (MedQA, MMLU-Med, PubMedQA) + the AdverseMed-500 reference set. For each model × question pair, we record: predicted answer, confidence via 4 elicitation methods, per-question difficulty tier, latency, and cost. Analysis proceeds under the pre-registered plan (§6). This is the primary validation of the reference set as a discriminative benchmark.

**Experiment B — the generator validation study.** Using Claude Opus 4.7 as the "target baseline," run `adversemed-gen` to produce 200 candidate adversarial questions. Compare per-question properties against a matched 200-question sample from the hand-verified reference set: (a) per-model failure rate, (b) category distribution, (c) reference density in each question's justification, (d) inter-annotator agreement between the 3 verifier models. If the generated set produces distributions statistically indistinguishable from the hand-verified set, the generator is validated as producing benchmark-quality questions.

No human review needed for the primary analysis of Experiment A — ground truth is boxed in the benchmarks (or, for AdverseMed-500, hand-verified during construction). For Experiment B, Dyuthi spot-checks ~20 generated questions (out of 200) as a sanity check on the automated multi-model verification step; the remainder are automated.

## 4. Models under test

Updated Jul 5 2026. **All API-only — no self-hosted models. Cost-minimization decision.**

| Model | Type | Access | Rationale |
|-------|------|--------|-----------|
| **Claude Opus 4.7** | Generalist frontier | Anthropic API (batch = 50% off) | Top-tier generalist; verbal probability elicitation |
| **Claude Haiku 4.5** | Generalist frontier (cheap) | Anthropic API (batch = 50% off) | Cheap generalist; strong pilot/smoke-test target |
| **GPT-5.4-mini** | Generalist frontier | OpenAI API (batch = 50% off) | Cross-provider validity; log-probability access |
| **Gemini 2.5 Pro** | Generalist frontier | Google AI API (batch discount) | Third generalist; strong prior MedQA performance |
| **DeepSeek-Chat** | Generalist open-API | DeepSeek API (already keyed from Paper 0) | Cheapest per-token; represents the "open-weight-served-via-API" tier |

**Backup access path:** an AWS Bedrock proxy adapter (`_pipeline/providers/bedrock_proxy.py`, model IDs `claude-haiku-4-5-bedrock` and `claude-sonnet-4-bedrock`) is available as a contingency in case Anthropic API access becomes unavailable during a run. Not used for the pre-registered comparative audit unless credits fail mid-run. Documented for reproducibility, not activated by default.

**Meditron-70B / open medical specialist:** *deferred.* Decision 2026-07-05: dropping the medical-specialist arm from v1 of the paper to keep costs under $200 total and avoid the complexity of VM self-hosting. The "specialist vs. generalist" sub-question can be added in a v2 revision if reviewers request it — we'll cite prior work (Mind the Gap 2506.10769) that has already covered that comparison.

This trade-off is documented explicitly: v1 focuses on **calibration transfer across distributions among generalist frontier models** — a defensible scope for an 8-week workshop paper. If the "medical specialist" arm becomes essential, add via API access to a hosted medical model (e.g., Together AI's Meditron endpoint) rather than self-host.

## 5. Benchmarks / question sets

| Set | Purpose | Size (used) | Access |
|-----|---------|-------------|--------|
| **MedQA (USMLE-style)** | In-distribution — the "gold" clinical benchmark | 1000 sampled from ~12,700 total | HuggingFace |
| **MMLU-Med** | Near-OOD (structured multi-domain) | 1089 (full "clinical" subset) | HuggingFace |
| **PubMedQA** | Far-OOD (research-literature-anchored) | 1000 sampled | HuggingFace |
| **AdverseMed-500 (NEW — this paper's primary contribution)** | 500 clinically-impossible false-premise questions | 500 (hand-verified by first author) | Constructed W2–W3 |

**AdverseMed-500 construction protocol** (this is the paper's primary contribution):

1. **Seed** — start from 500 MedQA questions, sampled with fixed seed 20260706, balanced across clinical categories.
2. **Mutate** — modify each seed question to embed exactly ONE false premise from one of four categories:
   - **Contraindications** (~150 questions) — drug-allergy conflicts, drug-condition conflicts, formulary-safety violations
   - **Drug-drug interactions** (~125 questions) — combinations that should not be co-prescribed
   - **Impossible timing** (~100 questions) — vaccine post-exposure windows, drug therapeutic windows, developmental-stage inappropriateness
   - **Physiological impossibilities** (~125 questions) — treatment plans that ignore prerequisite conditions (e.g., oral hypoglycemics for T1D, non-insulin approaches for DKA)
3. **Verify** — first author hand-verifies each question against clinical references (UpToDate, Lexicomp, FDA labeling). Questions where a physician might reasonably disagree about the "impossibility" are discarded.
4. **Score correctness protocol:**
   - The "correct" behavior is one of: (a) explicitly identifies the false premise, (b) abstains, (c) selects "None of the above" if presented. Any other response counts as a failure.
   - Multi-choice extraction handled by regex on model outputs; ambiguous cases hand-scored by first author.
5. **Release** — open-license JSONL file (`adversemed_500.jsonl`) published in the paper's GitHub repo AND registered as a Zenodo dataset with its own DOI, so it can be cited independently of the paper.

## 6. Confidence elicitation methods

For each model × question, we elicit confidence via 4 methods:

| Method | How it works | Cost |
|--------|--------------|------|
| **Verbal probability** | Prompt asks "How confident are you? (0.0–1.0)" | Low — 1 extra token |
| **Log-probability** | Read log P(chosen answer) from API response | Zero for OpenAI/DeepSeek; N/A for Claude/Gemini (require different pattern) |
| **Self-consistency** | Sample 5 responses at temp=0.7; measure agreement | ~5x cost |
| **Temperature-0 baseline** | Single greedy decode; treat correctness of top-1 as "confidence 1.0" | Baseline |

## 7. Metrics

Primary metrics per model × benchmark:
- **Expected Calibration Error (ECE)** with 10 confidence bins
- **Brier score** (mean squared error of probabilistic predictions)
- **Reliability diagram** (visual)
- **Coverage-risk curve** (abstention rate vs. error rate)
- **AURC** (area under the risk-coverage curve — selective classification measure)

Novel metric introduced by this paper:
- **Calibration Gap** = ECE(OOD) − ECE(in-distribution) per model. This is the paper's headline metric.

## 8. Analysis plan (pre-registered)

Primary outcomes:
1. **Per-model calibration gap** across the 3-benchmark-plus-adversarial matrix. Bootstrapped 95% CIs.
2. **Ranking stability** across confidence elicitation methods. Kendall's τ on model rankings.
3. **Adversarial abstention rate** — fraction of AdverseMed-500 questions where each model correctly abstains or flags the false premise.
4. **Model class effect** — one-way ANOVA on ECE by class {generalist frontier, generalist open, medical specialist}.

Secondary:
- Per-question difficulty vs. calibration (using MedQA difficulty tags)
- Cost-per-well-calibrated-answer as a deployment metric
- Reproducibility of MedHELM's calibration numbers where they overlap with our runs (a mini meta-audit)

Analysis code committed to `_pipeline/analyze.py` before any inference is run.

## 9. 8-week timeline to ML4H Sept 1 2026

Week | Dates | Milestones
---|---|---
W1 | Jul 6 – Jul 12 | **Protocol frozen. OSF pre-reg minted.** Read MedHELM + MedAbstain + "Knowing When to Abstain". Download 3 benchmarks. Sample question sets.
W2 | Jul 13 – Jul 19 | Build inference pipeline (`_pipeline/run_inference.py`). Smoke-test 5 models × 3 benchmarks on 10 sample questions each.
W3 | Jul 20 – **Jul 23 (actual)** | **Construct AdverseMed-500.** Dyuthi hand-verifies each question. Original W3 end was Jul 26; construction window extended to Aug 30 by OSF Amendment #1 (filed and accepted 2026-07-21, see §14). **Realized:** 500/500 hand-verified across 9 mode-B batches completed 2026-07-23 (dataset SHA `26cae9e19...c586a9`, commit `b566d1f`) — 38 days ahead of the amended window and 3 days after the original W3 end. Full inference: 5 models × (1000 + 1089 + 1000 + 500) ≈ 17.6k questions × 4 elicitation methods scheduled for W4.
W4 | Jul 27 – Aug 2 | **Inference + analysis pipeline runs.** Inference for 5 models × 4 elicitation methods on AdverseMed-500 (TASK_18); ECE, Brier, reliability diagrams, coverage-risk curves (TASK_19). Identify surprising findings.
W5 | Aug 3 – Aug 9 | **Deep-dive on findings.** Extra runs on cases where models disagree. Cost analysis.
W6 | Aug 10 – Aug 16 | Draft manuscript v0. Analysis → figures → prose.
W7 | Aug 17 – Aug 23 | Review-revise: v1, v2, v3. Same rubric-review loop as Paper 0.
W8 | Aug 24 – Aug 29 | v-final freeze. Submission package.
Aug 30 – Sep 1 | arXiv + ML4H submission.

## 10. Reused from Paper 0

- Rubric-review manuscript loop (v0 → v1 → v2 → v3 → v-final)
- Chrome-headless PDF pipeline
- OSF pre-registration template + CRediT contributions
- Version-log discipline
- GCS bucket layout
- DeepSeek API key + Anthropic key + OpenAI key (from Paper 0 wallet)
- General insight from P0's F19/F22/F23 finding: **models often fail silently or confidently-wrongly**. This paper measures HOW WELL they know when they don't know.

## 11. Infrastructure — cost-minimized architecture

**No self-hosted VMs. No GPUs. Everything API-based or serverless.**

Compute:
- Inference runs **from Dyuthi's laptop** calling provider APIs directly (or from a small Cloud Shell session if convenient). No VM to provision, no VM to remember to stop.
- Analysis (ECE / Brier / figures) runs **from Dyuthi's laptop** with Python + matplotlib. Zero compute cost.
- If any run needs to be long-lived (a batch job that takes hours), it can run in a **Cloud Shell** session ($0 cost) or a **Cloud Run job** (pay only for actual invocation time).

Storage:
- Raw inference outputs (JSONL) → `gs://pinkgenie-herald-data/dyuthi/paper-1-medllm-calibration/runs/` — GCS Standard storage, ~$0.02/GB/month
- Analysis outputs, figures, manuscript versions → same bucket, different prefixes
- Total storage estimate: <1 GB, so storage cost is under $0.10/month

Batching for API cost savings:
- **OpenAI Batch API — 50% off** for non-realtime workloads (24h SLA). Use for the 5000+ GPT-5 questions.
- **Anthropic Message Batches — 50% off** (24h SLA). Use for the 5000+ Claude questions.
- **Google Gemini batch prediction — ~50% off** via Vertex AI batch. Use for the 5000+ Gemini questions.
- **DeepSeek** — no batch API, but per-token cost is already the cheapest.
- Live requests only for pilot smoke-tests (~10 per model).

Pipeline scripts to build:
- `_pipeline/run_inference.py` — provider-batch-aware caller with retry + JSONL output
- `_pipeline/elicit_confidence.py` — 4 elicitation methods (verbal, log-prob, self-consistency, temp-0)
- `_pipeline/analyze.py` — ECE, Brier, reliability, coverage-risk, calibration-gap
- `_pipeline/adverse_med_construction.py` — MedQA question mutation harness
- `_pipeline/upload_to_gcs.py` — thin wrapper around gsutil to keep runs synced

**Revised API budget: ~$150 total**
- Claude Opus 4.7: ~$50 (batch discounted)
- Claude Haiku 4.5: ~$5 (already cheap)
- GPT-5.4-mini: ~$40 (batch discounted)
- Gemini 2.5 Pro: ~$20 (batch discounted)
- DeepSeek-Chat: ~$10
- Buffer for reruns / debugging: ~$25

**Total non-API GCP spend: essentially $0** (storage <$0.10/month, no VMs).

If any part of this cost profile creeps up during execution, task check-ins should surface it early.

## 12. Risk register

Risk | Mitigation
---|---
Meditron-70B is expensive to self-host | Fallback to BioMistral-7B or drop the "medical specialist" arm to just 4 generalists
AdverseMed-500 construction slips past Jul 26 (current pace risk as of 2026-07-16) | File an OSF amendment extending the construction window; if the amendment window itself becomes infeasible before analysis needs to run, ship v1 with 200-300 questions and log the reduction as a pre-registered deviation in the manuscript
Log-probability access varies across providers | Report which methods work per provider transparently; use verbal probability as universal fallback
MedHELM's numbers don't reproduce | This is STILL a publishable finding — a reproducibility check
Ranking changes across elicitation methods | This IS the finding — different methods rank models differently, which means the "leaderboard" is elicitation-dependent

## 13. Pre-registration commitments (frozen as of OSF mint 2026-07-06 · osf.io/mehu4)

1. Five-model set: Claude Opus 4.7, Claude Haiku 4.5, GPT-5.4-mini, Gemini 2.5 Pro, DeepSeek-Chat
2. Four question sets: MedQA (1000), MMLU-Med (1089), PubMedQA (1000), AdverseMed-500 (500 — constructed under §5 protocol; matches the OSF `mehu4` §D Sampling Plan committed on 2026-07-06)
3. Four confidence elicitation methods: verbal probability, log-probability, self-consistency (n=5), temperature-0 baseline
4. Primary metrics: ECE, Brier, coverage-risk, **Calibration Gap** (headline)
5. Primary analysis: calibration gap per model, ranking stability across elicitation methods, adversarial abstention rate

Any deviation logged as manuscript amendment.

## 14. Amendments to pre-registration

| # | Filed | Accepted | Scope | Justification | OSF ref |
|---|---|---|---|---|---|
| 1 | 2026-07-21 | 2026-07-21 | Timeline-only: extend AdverseMed-500 construction window from 2026-07-26 to 2026-08-30 (§9 W3). No change to sample size, benchmark composition, hypotheses, metrics, or analysis plan. | Original W2–W3 window was set when paper was scoped as AdverseMed-200 pilot; scope was strengthened to AdverseMed-500 on 2026-07-05 without corresponding timeline extension. Realized pace across batches 1-7 confirmed 500 required more calendar time than the original window allowed. Filed prior to any AdverseMed-500 inference; extension derived from realized construction pace, not from any partial-result peeks. | `osf.io/mehu4` update dated 2026-07-21; full text in `protocol/osf_amendment_v1_draft.md`. Amendment served its purpose — construction actually completed 2026-07-23, 38 days ahead of the amended deadline. |

| 2 | 2026-08-25 | 2026-08-25 | Metadata-only release of the registered corpus (AdverseMed-500 v1.1): adds resolvable source URLs for 338 of 577 reference strings across 310 of 500 items. No registered hypothesis, analysis or benchmark item affected; v1.0 is byte-identical and remains the basis of all reported results. | Filed so the registration reflects the artifact's state at release. | `6a8cdcb84e08e170ee3fa465` |
| 3 | 2026-08-25 | 2026-08-25 | Removes the archival DOI printed in Amendment #2's release paragraph, which resolved to a record naming the author while this registration is cited from double-blind manuscripts via an anonymized view-only link. No substantive claim in #2 changed or withdrawn. | Anonymity protection; the view-only link hides contributor metadata but cannot redact free text. | `6a8cddb34dd57755198d8a1a` |

*(Three amendments, all filed and approved. The registration carries four schema responses: the
original plus these three, verified against the OSF API on 2026-09-29. A Bedrock-substitution
amendment was drafted on 2026-08-01 in response to a briefly-anticipated Anthropic credit
shortfall, then reversed the same day when the first author funded the account; it was never
filed.)*

---

## 15. Dyuthi's role (first author, sole executor)

Dyuthi decides:
- Model set (drop Meditron? swap for BioMistral?)
- AdverseMed-500 question construction (verifies each is unambiguously flawed)
- Confidence elicitation method priority
- Manuscript direction

Claude executes:
- Inference pipeline
- Analysis pipeline
- Figure generation
- Manuscript drafts
- VM provisioning
- API cost tracking

Uday (dad) is available as a resource for:
- GCP billing questions (his account owns the project)
- Reviewing manuscript drafts before submission if Dyuthi asks

**Account ownership** (Jul 6 update): Dyuthi owns her own OSF account and mints Paper 1's pre-registration on her own account; she is sole first author of record. Uday is not an OSF contributor. GitHub/Zenodo release accounts are Dyuthi's; GCP billing account is Uday's but is separated by service (billing ≠ authorship).

---

## Sources cited in Section 2 (citation-corrected 2026-07-05 after TASK_01)

- **MedHELM** — Q2 2026 blog: https://pacific.ai/evaluating-frontier-llms-for-healthcare-with-medhelm-40-clinical-scenarios-and-a-new-q2-2026-leaderboard/ · Project site: https://medhelm.org/ · Nature Medicine paper (Bedi, Cui, Fuentes, Unell, Wornow et al., 2026-01-20): https://www.nature.com/articles/s41591-025-04151-2
- **MedAbstain / "Knowing When to Abstain"** (Machcha et al., arXiv 2601.12471, 2026): https://arxiv.org/abs/2601.12471
- **MARC** (Martinez, arXiv 2603.24481, 2026) — *Multi-Agent Reasoning with Consistency Verification Improves Uncertainty Calibration in Medical MCQA*: https://arxiv.org/abs/2603.24481
- "Mind the Gap" (arXiv 2506.10769): https://arxiv.org/pdf/2506.10769
- "Overconfidence and Calibration in Medical VQA" (arXiv 2604.02543): https://arxiv.org/pdf/2604.02543
- "When silence is safer" (Nature npj Digital Medicine 2026): https://www.nature.com/articles/s41746-026-02882-1
- "Trustworthy Medical Question Answering: An Evaluation-Centric Survey" (arXiv 2506.03659): https://arxiv.org/pdf/2506.03659
- HELM (Liang et al., TMLR 2023) — methodological ancestor of MedHELM
- Guo et al. 2017 — core ECE citation
- Tian et al. 2023, "Just ask for calibration" — confidence elicitation
- Xiong et al. 2023, "Can LLMs express their uncertainty?" — verbal confidence reliability
- AbstentionBench (Kirichenko et al. 2025) — abstention taxonomy including false premises
- Angelopoulos and Bates 2021 — conformal prediction
- Raji, Daneshjou, Alsentzer, NEJM AI 2025 — "It's time to bench the medical exam benchmark"
