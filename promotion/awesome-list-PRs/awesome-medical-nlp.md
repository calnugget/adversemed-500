# PR draft: healthnlp/awesome-medical-nlp (or best-current-fork)

> **Verify target before forking.**

## Target repo (verify current)

- URL: `https://github.com/healthnlp/awesome-medical-nlp`
- Section to edit: `## Datasets & Benchmarks` (this is the most direct
  fit for AdverseMed-500).

## Markdown to add

```markdown
- [AdverseMed-500](https://github.com/calnugget/adversemed-500) — 500 hand-verified false-premise medical multiple-choice questions across four failure categories. Correct action = abstention. CDC / FDA / clinical-guideline references per item. Companion 5-model × 4-elicitation-method calibration results. MIT + CC-BY-4.0. [DOI](https://doi.org/10.5281/zenodo.21961771) · [HF Datasets](https://huggingface.co/datasets/calnugget/adversemed-500).
```

## PR title

```
Add: AdverseMed-500 (hand-verified false-premise medical MCQ benchmark)
```

## PR body

```
Adds a hand-verified false-premise medical MCQ benchmark to the
Datasets & Benchmarks section.

**Why it belongs in awesome-medical-nlp**:
- 500 clinically-plausible MCQ vignettes with an unusual gold label
  (`abstain`), targeting a well-documented medical-LLM failure mode.
- Ground-truth verification by the sole author, a high-school student
  researcher, against published clinical guidelines, with CDC / FDA /
  clinical-guideline references per item — auditable. No physician
  reviewed the items.
- Fully open (MIT + CC-BY-4.0 + Zenodo + HF Datasets + OSF
  preregistration).
- Includes companion generator (`adversemed-gen`) for extending the
  benchmark; medical-NLP researchers can add domain-specific patterns.

**Repo**:  https://github.com/calnugget/adversemed-500
**DOI**:   https://doi.org/10.5281/zenodo.21961771
**HF**:    https://huggingface.co/datasets/calnugget/adversemed-500

Placed alphabetically. Verified no duplicate entry.

---

Author: Dyuthi Vallamsetty (first author).
```

## Step-by-step for Dyuthi

Same as `awesome-medical-ml.md`. Branch `add-adversemed-500`.
