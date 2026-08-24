# PR draft: sinaptik-ai/awesome-medical-ml (or best-current-fork)

> **Verify target before forking.** As of 2026-08 confirm the most-active
> fork; check https://github.com/topics/awesome-medical-ml.

## Target repo (verify current)

- URL: `https://github.com/sinaptik-ai/awesome-medical-ml`
  (or replace with current maintained fork)
- Section to edit: `## Benchmarks` (preferred). If the list separates
  "datasets" from "benchmarks", put it under benchmarks — the point
  of AdverseMed-500 is *evaluation*, not training.

## Markdown to add

Insert alphabetically:

```markdown
- [AdverseMed-500](https://github.com/calnugget/adversemed-500) — 500 hand-verified false-premise medical multiple-choice questions where the correct action is abstention. Four failure categories (contraindication, drug–drug interaction, impossible timing, physiological impossibility) with CDC / FDA / clinical-guideline references per item. Measures LLM calibration on clinical-safety edge cases. MIT (code) + CC-BY-4.0 (data). [DOI](https://doi.org/10.5281/zenodo.21961771) · [HF Datasets](https://huggingface.co/datasets/calnugget/adversemed-500) · [OSF preregistration](https://osf.io/mehu4).
```

## PR title

```
Add: AdverseMed-500 (hand-verified false-premise medical benchmark)
```

## PR body

```
Adds a hand-verified false-premise medical benchmark under
Benchmarks.

**Why it belongs**:
- Rare medical benchmark whose correct action is *abstention* rather
  than choosing an MCQ answer — targets a real clinical-safety failure
  mode (LLM confidently answering a question with a false premise).
- 500 items, hand-verified, with CDC / FDA / clinical-guideline
  references per item for downstream auditability.
- Fully open: MIT code + CC-BY-4.0 data + Zenodo archive + HF Datasets
  + OSF preregistration.

**Repo**:     https://github.com/calnugget/adversemed-500
**DOI**:      https://doi.org/10.5281/zenodo.21961771
**HF**:       https://huggingface.co/datasets/calnugget/adversemed-500
**OSF**:      https://osf.io/mehu4

Alphabetized within the section. Verified no duplicate entry.

---

Author: Dyuthi Vallamsetty (first author). No CoI beyond authorship.
```

## Step-by-step for Dyuthi

```bash
# 0. Confirm the target URL is still the most-active fork.
# 1. Fork the target repo to calnugget.
# 2. Clone your fork.
GH_CONFIG_DIR=/Users/uday/.config/gh-dyuthi gh repo clone calnugget/awesome-medical-ml
cd awesome-medical-ml
git remote add upstream https://github.com/<target-org>/awesome-medical-ml.git
git fetch upstream && git merge upstream/main --ff-only

# 3. Edit README.md.
# 4. Commit + push + PR.
git checkout -b add-adversemed-500
git add README.md
git commit -m 'Add: AdverseMed-500 (hand-verified false-premise medical benchmark)'
git push -u origin add-adversemed-500
GH_CONFIG_DIR=/Users/uday/.config/gh-dyuthi gh pr create \
  --repo <target-org>/awesome-medical-ml \
  --title 'Add: AdverseMed-500 (hand-verified false-premise medical benchmark)' \
  --body "$(cat promotion/awesome-list-PRs/awesome-medical-ml.md | sed -n '/^```$/,/^```$/p')"
```
