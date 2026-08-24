# PR draft: safellms/awesome-ml-safety (or best-current-fork)

> **Verify target before forking.**

## Target repo (verify current)

- URL: `https://github.com/safellms/awesome-ml-safety`
- Section to edit: `## Benchmarks` or `## Abstention / Refusal`
  (whichever exists). If neither exists, propose the addition in the
  most-safety-relevant subsection and mention that an "Abstention"
  subsection would be a good long-term add.

## Markdown to add

```markdown
- [AdverseMed-500](https://github.com/calnugget/adversemed-500) — 500 hand-verified false-premise medical MCQs where the correct behavior is **abstention / refusal**. Directly probes LLM behavior on adversarial inputs in a high-consequence (medical) domain. Companion calibration analysis for 5 frontier LLMs × 4 elicitation methods. MIT + CC-BY-4.0. [DOI](https://doi.org/10.5281/zenodo.21961771) · [HF Datasets](https://huggingface.co/datasets/calnugget/adversemed-500) · [OSF](https://osf.io/mehu4).
```

## PR title

```
Add: AdverseMed-500 — adversarial medical benchmark where the correct behavior is abstention
```

## PR body

```
Adds an adversarial medical benchmark specifically designed to probe
**abstention / refusal** behavior in a high-consequence domain.

**Why it's a fit for awesome-ml-safety**:
- Explicitly targets a safety-relevant failure mode: LLMs confidently
  answering questions with false clinical premises.
- Every item has a *wrong-by-construction* set of A/B/C/D options, so
  any non-abstention answer is measurably a safety failure — no
  ambiguous scoring.
- Companion analysis quantifies which elicitation methods
  (temperature-0, log-probability, verbal probability, self-consistency)
  trigger abstention on which frontier LLMs.
- Fully open (MIT + CC-BY-4.0 + Zenodo + HF Datasets + OSF
  preregistration).

**Repo**:  https://github.com/calnugget/adversemed-500
**DOI**:   https://doi.org/10.5281/zenodo.21961771
**HF**:    https://huggingface.co/datasets/calnugget/adversemed-500

Placed alphabetically. Verified no duplicate entry.

---

Author: Dyuthi Vallamsetty (first author).
```

## Step-by-step for Dyuthi

Same as `awesome-medical-ml.md`. Branch `add-adversemed-500-abstention`.
