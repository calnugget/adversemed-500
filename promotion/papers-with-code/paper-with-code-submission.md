# Papers with Code — Submission Draft (AdverseMed-500)

Copy the fields below into the form at https://paperswithcode.com/submit
once the Zenodo record is public and (ideally) the arXiv/venue posting is
live.

Because AdverseMed-500 is a *dataset + benchmark*, we submit **both** a
paper entry and a dataset entry.

---

## Paper submission

- **Title**
  AdverseMed-500: A Hand-Verified False-Premise Benchmark for
  Measuring Miscalibration in Medical Language Models

- **Authors**
  Dyuthi Vallamsetty (The Harker School, San Jose, CA, USA)

- **Publication date**
  2026

- **Paper URL** (Zenodo permalink until arXiv is live)
  https://doi.org/10.5281/zenodo.21961771

- **arXiv ID**
  *(fill in after arXiv upload)*

- **Venue**
  *(fill in after acceptance; targeting NeurIPS ML4H Sept 2026 per plan)*

- **OSF preregistration**
  https://osf.io/mehu4

## Abstract (paste)

> We introduce AdverseMed-500, a hand-verified benchmark of 500
> false-premise multiple-choice medical questions where the correct
> action is abstention. Each item embeds an invalid clinical premise
> (contraindication, drug–drug interaction, impossible timing, or
> physiological impossibility) drawn from a 65-pattern library and grounded
> in CDC / FDA / clinical-guideline references. We evaluate five frontier
> LLMs (Claude Haiku 4.5, Claude Opus 4.7, DeepSeek-Chat, Gemini 2.5 Pro,
> GPT-5.4-mini) across four elicitation methods (temperature-0,
> log-probability, verbal probability, self-consistency) and find [KEY
> RESULT PLACEHOLDER — update from manuscript §6]. All 500 verified
> items, per-question ground-truth YAML with references, the raw
> 5×4=20 model-response JSONLs, the generator pipeline (`adversemed-gen`),
> and the calibration-analysis code are released for full reproducibility.

## Repository / code

- **Official implementation**:
  https://github.com/calnugget/adversemed-500
- **Framework**: PyTorch / other (inference-only, provider APIs)
- **License**: MIT (code), CC-BY-4.0 (dataset)

## Dataset submission (separate step)

Click "Add Dataset" from the paper page after paper submission is
accepted.

- **Dataset name**: AdverseMed-500
- **Description** (paste):
  > 500 hand-verified false-premise medical multiple-choice
  > questions across four failure categories (contraindication,
  > drug–drug interaction, impossible timing, physiological
  > impossibility). Correct behavior is abstention. Ground-truth
  > verification cites CDC / FDA / clinical guidelines.
- **Homepage**: https://github.com/calnugget/adversemed-500
- **Paper**: link the paper submission above
- **Hugging Face URL**:
  `https://huggingface.co/datasets/calnugget/adversemed-500` (add
  after HF push completes)
- **Zenodo DOI**: 10.5281/zenodo.21961771
- **License**: CC-BY-4.0
- **Size**: 500 items (~700 KB JSONL)
- **Tasks**: `question-answering`, `multiple-choice-qa`,
  `clinical-decision-making`, `abstention-detection`
- **Modalities**: text
- **Languages**: English
- **Tags**: `medical`, `clinical-safety`, `calibration`, `false-premise`,
  `abstention`, `LLM-safety`, `adverse-medication`, `benchmark`,
  `adversarial`

## Tasks

Best-fit PwC task pages:
- **Question Answering** (primary, always accepted).
- **Multiple Choice Question Answering** (secondary).
- **Medical Question Answering** (secondary).
- **Calibration** (secondary).
- **Safe Reinforcement Learning / LLM Safety** (tertiary, if PwC has a
  matching page — check at submission time).

If none match "abstention" specifically, request a new task page
"Abstention / Refusal in LLMs" via PwC's task-suggestion UI.

## Methods

The paper does NOT propose a new method. The generator (`adversemed-gen`)
is a construction pipeline, not a modeled method. Do **not** create a
method page for `adversemed-gen`. Only link the paper + dataset entries.

## Results / benchmarks (SOTA leaderboard)

**Populate this** — AdverseMed-500 is designed as a leaderboard-eligible
benchmark. Add one row per (model, elicitation-method) pair from
manuscript §6. Metric = **abstention rate** (higher is better under this
benchmark's convention, since abstention is the correct action).

Rows to add:
| Model              | Method               | Abstention rate (%) |
| ------------------ | -------------------- | ------------------- |
| Claude Opus 4.7    | verbal_probability   | *[fill from §6]*    |
| Claude Opus 4.7    | self_consistency     | *[fill from §6]*    |
| Claude Opus 4.7    | temperature_0        | *[fill from §6]*    |
| Claude Opus 4.7    | log_probability      | *[fill from §6]*    |
| Claude Haiku 4.5   | verbal_probability   | *[fill from §6]*    |
| ...                | ...                  | ...                 |
| GPT-5.4-mini       | log_probability      | *[fill from §6]*    |

Also add:
- Secondary metric: **ECE (Expected Calibration Error)** — lower is better.
- Secondary metric: **AURC (Area Under the Risk-Coverage curve)** — lower
  is better.

Set the "official" split = `test` (only split exists).

## Tags / keywords

`medical LLM`, `benchmark`, `calibration`, `false premise`,
`clinical safety`, `hallucination`, `abstention`, `adversarial`,
`hand-verified`.

## Notes for the reviewer

- Fully reproducible: dataset + code + raw responses on GitHub + Zenodo +
  HF Datasets.
- Pre-registered on OSF before benchmark construction started
  (osf.io/mehu4) with Amendment #1 on file.
- No PHI; all vignettes synthetic.
- Hand-verified by the sole author (Dyuthi Vallamsetty), a high-school student
  researcher, against published clinical guidelines, with independent
  per-batch review. **No physician reviewed the items.** Sole-author
  verification is documented as a limitation.
