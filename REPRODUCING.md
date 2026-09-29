# Reproducing the tables in the papers

## TL;DR

```bash
cd scoring
python3 reparse_confidence.py ../inference_outputs_raw ../inference_outputs_reparsed
python3 analyze.py summarize --input-dir ../inference_outputs_reparsed --output summary.md
diff summary.md ../analysis_outputs/summary.md
# The only expected difference is the first line, which records your local input path.
# Every table row should match exactly.
```

`analysis_outputs/summary.md` in this archive is the output of exactly that command, and its
numbers are the ones printed in the papers.

## Why there is a re-parse step

Two **parsing** defects were found on 2026-08-24, after the inference runs were logged. No
model was re-run; the raw responses were always correct, and only the extraction of a
confidence value from them was wrong.

1. **DeepSeek-Chat misspells the keyword.** It writes `CONFIDANCE:` on a substantial minority
   of rows. The original regex required `CONFIDENCE:` exactly and silently discarded the
   stated value. This corrupted **published** `verbal_probability` numbers: DeepSeek's usable
   rows were 423/500 rather than 500/500, and its verbal ECE was reported as 0.273 where the
   correct figure is **0.247**.

2. **`temperature_0` recorded a constant confidence of 1.0.** This followed PROTOCOL §6, which
   defined the baseline that way. The consequence is that ECE, Brier and AURC on those rows
   were algebraic restatements of accuracy rather than independent measurements. The papers now
   use the confidence the model states in-band. **This is a deviation from the registered
   analysis plan, not a bug fix**, and it is disclosed as such in each paper's deviations
   appendix.

`inference_outputs_raw/` is the untouched log. `inference_outputs_reparsed/` is what the
analysis consumes. Both ship so the correction is auditable rather than assumed.

**Accuracy is unaffected.** `correct` is `chosen_answer == ground_truth` and does not depend on
confidence. `reparse_confidence.py` asserts this and exits non-zero if any row's `correct`
changes.

## Which corpus version the results use

- `benchmark/adversemed_500.jsonl` — **v1.0**, SHA-256
  `26cae9e190bc96a96814241ef4e0c779f2ff7de51dd811dcdb425a8af1c586a9`.
  **Every published result was computed on this file.**
- `benchmark/adversemed_500_v1.1.jsonl` — a **metadata-only** enrichment adding resolvable
  source URLs to 310 of the 500 items. Item content is byte-identical to v1.0. It is provided
  for readers who want to follow the citations, and is **not** the analysis basis.
  See `benchmark/RELEASE_NOTES_v1.1.md`, including the limits of what a resolving URL shows.

## Known limitation

`temperature_0` shares its API call with `verbal_probability` — identical prompt, identical
temperature, identical parser — so after the re-parse the two are a test-retest replicate
rather than independent methods. The papers report three elicitation methods plus a replicate,
and exclude temp-0 from the rank-correlation analysis for this reason.
