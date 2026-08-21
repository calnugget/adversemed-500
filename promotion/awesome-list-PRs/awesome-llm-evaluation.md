# PR draft: onejune2018/awesome-llm-eval (or best-current-fork)

> **Verify target before forking.**

## Target repo (verify current)

- URL: `https://github.com/onejune2018/Awesome-LLM-Eval`
- Section to edit: `## Benchmarks` and/or `## Calibration` and/or
  `## Safety` (whichever subsections match — this benchmark touches
  all three).

## Markdown to add

```markdown
- **AdverseMed-500** — 500 physician-verified false-premise medical MCQs where the correct action is *abstention*. Includes 5-model × 4-elicitation-method calibration results (ECE, AURC, abstention-rate) and a reusable generator (`adversemed-gen`) for constructing more items. MIT + CC-BY-4.0. · [repo](https://github.com/calnugget/adversemed-500) · [DOI](https://doi.org/10.5281/zenodo.21961771) · [HF](https://huggingface.co/datasets/calnugget/adversemed-500) · [OSF](https://osf.io/mehu4).
```

## PR title

```
Add: AdverseMed-500 — physician-verified calibration/abstention benchmark for medical LLMs
```

## PR body

```
Adds a calibration + abstention benchmark to the Benchmarks / Calibration
section.

**Why it's a good fit**:
- Directly measures **calibration** (ECE, AURC) and **abstention
  behavior** — both under-served in the current benchmark landscape,
  especially in a high-consequence domain (medical).
- Physician-verified ground truth with CDC / FDA / clinical-guideline
  citations per item.
- Ships companion inference pipeline that already reports results for
  5 frontier LLMs across 4 elicitation methods (temperature-0,
  log-probability, verbal probability, self-consistency), so downstream
  users can plug in their own model and compare directly.
- Fully open: MIT code + CC-BY-4.0 data + Zenodo + HF Datasets + OSF.

**Repo**:  https://github.com/calnugget/adversemed-500
**DOI**:   https://doi.org/10.5281/zenodo.21961771
**HF**:    https://huggingface.co/datasets/calnugget/adversemed-500

Placed alphabetically. Verified no duplicate entry.

---

Author: Dyuthi Vallamsetty (first author).
```

## Step-by-step for Dyuthi

Same as `awesome-medical-ml.md`. Branch `add-adversemed-500`.
