# Paper 1 — High-Level Thesis

*"AdverseMed-500: A Benchmark to Help Researchers Vet Medical LLMs"*

**Author:** Dyuthi Vallamsetty · **Target venue:** NeurIPS ML4H 2026 · **Deadline:** September 1, 2026 · **OSF pre-registration:** [osf.io/mehu4](https://osf.io/mehu4/) (minted 2026-07-06, embargoed)

---

## The one-sentence pitch

**AdverseMed-500 is a *self-hardening* benchmark of medical questions embedded with clinically-impossible premises — contraindications, drug-drug interactions, impossible timing, and physiological impossibilities — that lets a researcher answer a simple question before using a medical LLM in their own work: "will this model catch when the premise itself is wrong, or will it confidently answer something dangerous?" The paper releases both a hand-verified reference set of 500 questions AND an open-source generator that produces fresh adversarial questions calibrated to any current-frontier model, so the benchmark stays as strong as the models it evaluates.**

## What "self-hardening" means

Most benchmarks age badly. MMLU, MMLU-Pro, GPQA-Diamond, and MultiMedQA are all clustered near saturation by 2026 — top models within 1–2 points of each other. Fixed test sets also contaminate: Johns Hopkins found 29% of MMLU items memorized by frontier models. A benchmark released today as a static set of 500 questions has a shelf life of about 2–3 years.

AdverseMed-500 avoids this by releasing **two artifacts together**:

1. **A reference set** — 500 hand-verified questions with clinical citations. Serves as the demonstration set, the citation anchor, and the quality reference for the generator.
2. **A generator** (`adversemed-gen`) — an open-source Python tool that takes a baseline LLM, a seed pool of MedQA questions, and a pattern library, and produces fresh adversarial questions that *specifically fool the baseline*. As models get better, the generator's adversarial filter produces harder questions, keeping the benchmark aligned with the frontier.

The mechanism: for each generated candidate, the pipeline (a) drafts a false-premise mutation, (b) tests the target baseline model, (c) keeps only mutations the baseline fails to flag, (d) verifies the impossibility via multi-model consensus. As the baseline improves, only harder mutations survive.

## Why this benchmark exists

Researchers across biomedicine, epidemiology, and clinical AI increasingly rely on LLMs as research tools — for literature review, hypothesis generation, data annotation, and analytic reasoning. But no existing benchmark helps a researcher decide **when an LLM's answer to a domain question can be trusted for their work**. Every current medical LLM benchmark (MedQA, MMLU-Med, PubMedQA, MedHELM) evaluates LLMs against *well-formed* clinical questions. None of them test whether a model catches an *impossible* premise — the failure mode most likely to slip into a research pipeline, because a researcher won't always notice when the LLM has quietly answered a broken question.

That gap is the point of Paper 1. Dyuthi built this benchmark because she uses LLMs in her own research (scoring, drafting, ideation) and couldn't find the tool she needed. If she needs it, other researchers do too.

## What the reference set is

**500 medical multiple-choice questions**, each embedded with a false premise from one of four clinical categories:

1. **Contraindications** (~150 questions) — drug-allergy conflicts, drug-condition conflicts
2. **Drug-drug interactions** (~125 questions) — combinations that should not be co-prescribed
3. **Impossible timing** (~100 questions) — vaccines after exposure window, meds outside therapeutic windows
4. **Physiological impossibilities** (~125 questions) — treatment plans that ignore mandatory prerequisites (e.g., insulin-absent care for T1D)

Each question is hand-verified by Dyuthi against clinical references so the false premise is unambiguous — a physician would catch it, and a well-calibrated LLM should either flag the premise or refuse to answer. Every question also carries a **difficulty tier** (obvious / subtle / expert) so metrics can be reported per tier — a durable evaluation that keeps discriminating as models saturate the easier tiers first.

## What the paper delivers

1. **AdverseMed-500 — the hand-verified reference set** — 500 questions, open license, on GitHub + Zenodo (with DOI). Citable, reproducible, the paper's most concrete artifact.
2. **`adversemed-gen` — the self-hardening generator** — open-source Python tool. Users can run it against any LLM API to produce their own adversarial set calibrated to their target model. This is the paper's most *durable* contribution — it keeps the benchmark alive as models evolve.
3. **The "Calibration Gap" metric** — a per-model deployment-risk score defined as ECE on AdverseMed-500 minus ECE on standard MedQA. Reusable across benchmark pairs; survives even when individual questions saturate.
4. **Difficulty-tier framework** — obvious / subtle / expert stratification. Enables per-tier reporting so saturation of easier tiers doesn't kill the benchmark's discriminative power.
5. **Validation study on 5 frontier LLMs** — Claude Opus 4.7, Claude Haiku 4.5, GPT-5.4-mini, Gemini 2.5 Pro, DeepSeek-Chat. Demonstrates the reference set discriminates, and validates that generator-produced questions have comparable properties.
6. **Usage guide** — how future researchers should run AdverseMed-500 (or generated variants) on their own model of interest, what confidence-elicitation method to use, and how to interpret the results.

## What we deliberately are NOT doing

To keep scope tight for an 8-week workshop paper:

- Not fine-tuning any model to fix the calibration problem — that's a follow-up paper
- Not building an agent framework — this is a benchmark paper, not an intervention paper
- Not requiring physician-expert review — Dyuthi hand-verifies against clinical references
- Not measuring free-form generation calibration — multiple-choice only in v1
- Not extending to other medical languages — English only in v1
- Not community-maintaining the generator — v1 release is a working reference implementation; long-term governance is future work

## Constraints this paper honors

- **Public data only** — MedQA seed, no restricted datasets
- **Best-fit statistical analysis** — ECE, Brier, reliability diagrams, coverage-risk curves, standard peer-reviewed methods
- **No medical judgment as data source** — Dyuthi verifies the premise, but the "correctness" of a response is scored programmatically
- **Low compute cost** — API-only inference; all 5 models run through commercial batch APIs; ~$180 for the reference-set experiments; ~$100 additional for the generator validation study
- **8-week runway to ML4H Sept 1**

## The narrative arc with Paper 0

**Paper 0** — showed that AI Scientist v2 silently fails 79% of the time on manuscript-writing tasks.

**Paper 1** — extends the trustworthiness question to a wider tool: general-purpose medical LLMs used by researchers. Provides the community both a reference benchmark AND a durable framework for continuing to check any model's answer-integrity on impossible clinical premises.

**Later papers (master plan P2–P12)** — extend the trust-measurement framework: FAERS DDI hypotheses (P3), retraction detection (P4), pediatric cancer disparities (P5), Alzheimer's multimodal (P10), and so on.

Together this is the beginning of Dyuthi's research program on **measurable trustworthiness for AI in medicine**. AdverseMed-500 is the first standing benchmark the community can adopt — and, uniquely, the first that grows in difficulty alongside the models it measures.
