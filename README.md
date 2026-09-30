# AdverseMed-500

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.21961770-blue)](https://doi.org/10.5281/zenodo.21961770)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI: adversemed-gen](https://img.shields.io/badge/pypi-adversemed--gen-orange)](https://pypi.org/project/adversemed-gen/)
[![HF Datasets](https://img.shields.io/badge/%F0%9F%A4%97%20datasets-AdverseMed--500-yellow)](https://huggingface.co/datasets/calnugget/adversemed-500)
[![OSF Preregistered](https://img.shields.io/badge/OSF-preregistered-green)](https://osf.io/mehu4)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/calnugget/adversemed-500/blob/main/notebooks/quickstart.ipynb)

An adversarial medical-QA benchmark of **500 hand-verified false-premise
questions** designed to stress-test large-language-model calibration on
clinical-safety edge cases.

Companion release for:

> Vallamsetty, D. (2026). *AdverseMed-500: A Hand-Verified False-Premise
> Benchmark for Measuring Miscalibration in Medical Language Models.*
> The Harker School, San Jose, CA, USA.
> Pre-registered at OSF: https://osf.io/mehu4

## What is in the benchmark

Each of the 500 questions embeds a **false clinical premise** in one of four
failure categories:

| Category                        | N   |
|---------------------------------|-----|
| Contraindication                | 150 |
| Drug–drug interaction           | 125 |
| Impossible timing               | 100 |
| Physiological impossibility     | 125 |

Difficulty distribution: 108 obvious / 183 subtle / 209 expert.

The **correct action** on every AdverseMed-500 item is `abstain` (i.e. flag
the false premise), not to pick any listed A–D option. A well-calibrated
model should refuse.

Every question was independently reviewed and locked by the first author on
2026-07-23; see `benchmark/verified_yaml/` for the per-question ground truth
including references to CDC / FDA / clinical-guideline sources.

**Dataset integrity**:

```
SHA-256(adversemed_500.jsonl) =
  26cae9e190bc96a96814241ef4e0c779f2ff7de51dd811dcdb425a8af1c586a9
```

See `benchmark/SHA256SUMS`.

## Quickstart

```bash
# 1. Clone
git clone https://github.com/calnugget/adversemed-500.git && cd adversemed-500

# 2. Load the 500-item benchmark
python -c "import json; \
  items = [json.loads(l) for l in open('benchmark/adversemed_500.jsonl')]; \
  print(f'{len(items)} items | first stem:', items[0]['stem'][:80])"

# 3. (Optional) install the generator to mine new adversarial items
pip install -e generator/   # or: pip install adversemed-gen  (once published)
```

Colab: click the "Open in Colab" badge above for a runnable demo notebook.

## Repo layout

```
adversemed-500/
├── README.md                              # you are here
├── LICENSE                                # MIT (code)
├── LICENSE-DATA                           # CC BY 4.0 (dataset + analysis outputs)
├── CORRECTIONS.md                         # what changed in the published numbers, and when
├── REPRODUCING.md                         # how to regenerate the papers' tables
├── CITATION.cff                           # for citation-manager tools
├── .gitignore
├── PROTOCOL.md                            # full study protocol
├── THESIS.md                              # thesis statement + design rationale
├── benchmark/
│   ├── adversemed_500.jsonl               # the 500 questions (v1.1, the published corpus)
│   ├── adversemed_500_v1.2.jsonl          # v1.2: adds `contestable`, softens 25 premises
│   ├── adversemed_500_control_v1.jsonl    # 285-item control set (§5.2, Table 7)
│   ├── adversemed_500_control_v1.preshuffle.jsonl
│   ├── contraindication_subtypes.json     # sub-type classification of the 150 items
│   ├── twin_review_log.jsonl              # twin-review adjudication log
│   ├── manifest.json                      # SHA + row counts + category splits (generated)
│   ├── SHA256SUMS
│   ├── PATTERNS.md                        # 65-pattern failure library
│   ├── CATEGORIES.md                      # category definitions
│   ├── RUBRIC.md                          # rubric for item verification
│   ├── SOURCES.md                         # seed benchmarks and citation policy
│   ├── WORKFLOW.md                        # construction workflow
│   ├── PROGRESS.md                        # construction log
│   ├── PROGRAMMATIC.md                    # programmatic-verification notes
│   ├── BENCHMARK_README.md                # extra README from construction dir
│   └── verified_yaml/                     # per-question ground truth (500 files)
│       ├── 001_mmr_pregnancy_contraindication.yaml
│       ├── ...
│       └── 500_*.yaml
├── generator/                             # adversemed-gen: mutate → filter → verify
│   ├── README.md
│   ├── DESIGN.md
│   ├── V0_1_LIMITATIONS.md
│   ├── setup.py
│   ├── cli.py                             # entry point
│   ├── pipeline.py                        # mutate-filter-verify orchestration
│   ├── mutate.py                          # premise-mutator patterns
│   ├── filter.py                          # heuristic filtering
│   ├── verify.py                          # LLM-assisted verification pass
│   ├── emit.py                            # writer to JSONL
│   ├── patterns.py                        # 65-pattern library (as Python data)
│   ├── __init__.py
│   └── prompts/                           # mutator / verifier / self-test prompts
├── inference_pipeline/                    # code to run models on the benchmark
│   ├── run_inference.py                   # main runner
│   ├── analyze.py                         # score outputs → calibration metrics
│   ├── prompt.py                          # per-elicitation-method prompt formatting
│   ├── elicitation.py                     # elicitation methods (temp0, log-prob, verbal, self-consistency)
│   ├── build_adversemed.py                # build script for the benchmark JSONL
│   ├── download_benchmarks.py             # fetch MedQA / MMLU-med / PubMedQA seeds
│   ├── smoke_test.py / smoke_test_v2.py
│   ├── secrets_helper.py                  # fetches API keys from GCP Secret Manager (NO secrets in file)
│   ├── requirements.txt
│   └── providers/                         # anthropic, openai, google, deepseek, bedrock_proxy
├── inference_summaries/                   # per-model per-method summary JSONs (20 files)
│   ├── claude-haiku-4-5__temperature_0.summary.json
│   ├── ...
│   └── gpt-5.4-mini__self_consistency.summary.json
└── scoring/
    └── analysis_outputs/                  # calibration-analysis JSONs used in the paper
        ├── summary.md                     # the 20-row table; Cost differs from the paper (see REPRODUCING.md)
        └── difficulty_breakdown.json      # obvious/subtle/expert accuracy per (model x method)
        ├── summary.md
        └── <model>__<method>.analysis.json
```

## What is on Zenodo (not in this repo)

The full replication package (raw model responses for all 5 models × 4
elicitation methods = 20 JSONL files) is on Zenodo. **Cite the concept DOI**,
which always resolves to the newest version:

- **Concept DOI**: [10.5281/zenodo.21961770](https://doi.org/10.5281/zenodo.21961770)

Earlier version DOIs point at specific snapshots. `10.5281/zenodo.21961771`
is v1.0.0 and contains **no** inference outputs; `10.5281/zenodo.22088174`
is v1.1.0 and carries the raw and re-parsed logs.

The analysis JSONs in `scoring/analysis_outputs/` regenerate the paper's
Table 6 from the **re-parsed** inference logs. To reproduce them from the raw
responses you need the Zenodo archive plus `inference_pipeline/reparse_confidence.py`;
see `REPRODUCING.md`. A correction was applied to these outputs on 2026-08-24
and is documented in [`CORRECTIONS.md`](CORRECTIONS.md) — the numbers published
here before 2026-09-28 disagreed with the paper in six of twenty cells.

## Models evaluated

- Claude Haiku 4.5 (Anthropic)
- Claude Opus 4.7 (Anthropic)
- DeepSeek-Chat
- Gemini 2.5 Pro (Google)
- GPT-5.4-mini (OpenAI)

Each model was run with four elicitation methods: `temperature_0`,
`log_probability`, `verbal_probability`, `self_consistency`.

## How to reproduce

1. Clone this repo and (optionally) download the Zenodo raw-response tarball.
2. Create a Python 3.11 virtualenv:
   ```bash
   python3.11 -m venv .venv && source .venv/bin/activate
   pip install -r inference_pipeline/requirements.txt
   ```
3. Provide API keys for the providers you want to re-run
   (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`,
   `GEMINI_API_KEY`). See `inference_pipeline/secrets_helper.py` — the
   file itself contains **no secrets**; it looks up keys from GCP Secret
   Manager if `PROJECT_ID` is set, or you can just export env vars.
4. Run inference for one model / method:
   ```bash
   python inference_pipeline/run_inference.py \
     --model claude-opus-4-7 \
     --method verbal_probability \
     --benchmark benchmark/adversemed_500.jsonl \
     --out inference_outputs/
   ```
5. Score:
   ```bash
   python inference_pipeline/analyze.py \
     --input inference_outputs/claude-opus-4-7__verbal_probability.jsonl \
     --benchmark benchmark/adversemed_500.jsonl \
     --out analysis_outputs/
   ```

## Pre-registration

- **OSF project**: https://osf.io/mehu4
- **Amendment #1** (accepted 2026-07-21): extended construction deadline to
  2026-08-30, N held at 500.
- Construction locked 2026-07-23, 38 days ahead of amended deadline.

## Citation

If you use this benchmark or code, please cite both the paper (once posted)
and this repository via the `CITATION.cff` file. Please also cite the
seed-benchmark sources (MedQA, MMLU-med, PubMedQA) as documented in
`benchmark/SOURCES.md`.

### BibTeX

```bibtex
@software{vallamsetty2026adversemed500,
  author       = {Vallamsetty, Dyuthi},
  title        = {{AdverseMed-500: A Hand-Verified False-Premise
                   Benchmark for Measuring Miscalibration in Medical
                   Language Models}},
  year         = 2026,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.21961770},
  url          = {https://doi.org/10.5281/zenodo.21961770},
  note         = {Concept DOI; always resolves to the newest archived version}
}
```

### APA

Vallamsetty, D. (2026). *AdverseMed-500: A Hand-Verified False-Premise Benchmark for Measuring Miscalibration in Medical Language Models* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.21961770

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to add adversarial patterns,
improve the scoring pipeline, or report issues with a specific benchmark item.

## License

**Code is MIT, data is CC BY 4.0.** The generator, inference pipeline and
scoring/analysis code are under the MIT License (`LICENSE`). The benchmark
corpus, the per-item YAML verification records and the analysis outputs are
under Creative Commons Attribution 4.0 International (`LICENSE-DATA`).

This split is the conventional one for a release that is both a dataset and a
toolchain, and it matches the Hugging Face dataset card. Before 2026-09-29
this file said MIT for the data too; `LICENSE-DATA` records that correction
and confirms that no MIT grant already received is revoked.

If you reuse material derived from the MedQA / MMLU-Med / PubMedQA seed
corpora, cite those sources under their own terms as well.
