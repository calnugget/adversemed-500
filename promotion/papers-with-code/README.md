# Papers with Code — submission workflow (AdverseMed-500)

Papers with Code (PwC) is the canonical index for ML research + benchmarks.
For AdverseMed-500 specifically, PwC is a strong distribution channel
because it's a leaderboard-eligible benchmark.

## When to submit

Submit **after all** of the following:
1. The Zenodo record is public (already true — DOI 10.5281/zenodo.21961771).
2. The HF Datasets record is public (see `../../HF_DATASETS/push_to_hf_INSTRUCTIONS.md`).
3. Either arXiv OR a venue posting is live.

## Two submissions, in order

### 1. Submit the paper (5 minutes)

1. Sign in at https://paperswithcode.com/ using GitHub (`calnugget`).
2. Click "Submit" → "Paper".
3. Paste the arXiv ID (or PDF URL). PwC auto-fills title / authors /
   abstract. Correct anything wrong.
4. Copy fields from `paper-with-code-submission.md` into the form.
5. Submit. Moderators approve within 1–3 business days.

### 2. Submit the dataset (5 minutes, after paper is approved)

1. Navigate to the accepted paper page.
2. Click "Add Dataset" in the sidebar.
3. Copy the "Dataset submission" section from
   `paper-with-code-submission.md`.
4. Link back to the paper page and the HF Datasets page.
5. Submit.

### 3. Populate the leaderboard (10 minutes)

Once the dataset page is live:

1. Click "Add Results" on the dataset page.
2. Add one row per (model, elicitation-method) pair from manuscript §6.
3. Set metric = **Abstention rate (%)** (higher is better).
4. Add ECE and AURC as secondary metrics if PwC allows multi-metric
   leaderboards for the accepted task.
5. Attach the raw JSONL from Zenodo as the "results file" so other
   submitters can verify.

## After submission

Add PwC badges to the top of the main README:

```markdown
[![PWC-paper](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/adversemed-500/adversemed-500)](https://paperswithcode.com/paper/adversemed-500)
[![PWC-dataset](https://img.shields.io/badge/paperswithcode-AdverseMed--500-blue)](https://paperswithcode.com/dataset/adversemed-500)
```

## Do NOT

- Do not submit before the Zenodo record is public (dead links get
  rejected).
- Do not overstate SOTA claims — this is a benchmark whose *purpose* is
  to expose miscalibration; every model on the leaderboard is likely to
  score below the "correct" 100% abstention rate. That's the point.
- Do not create a "method" page for `adversemed-gen` — it's a
  construction pipeline, not a modeled method.
