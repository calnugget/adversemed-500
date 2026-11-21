# Reproducing the tables in the papers

## TL;DR

**The raw inference logs are not in this repository.** They are in the Zenodo archive; this repo
carries the corpus, the pipeline and the analysis outputs. Get the logs first:

```bash
# 1. Fetch the archive. The concept DOI always resolves to the newest version.
#    https://doi.org/10.5281/zenodo.21961770
#    Unpack it; the raw logs are the per-run *.jsonl files.

#    In v1.2.1 the pristine logs are inference_outputs/adversemed_500_raw/.

# 2. Re-parse confidence out of the raw responses   (expect: 1,813 rows changed)
python3 inference_pipeline/reparse_confidence.py <raw-logs-dir> <reparsed-dir>

# 3. Repair the out-of-range log-probability confidences   (expect: 26 repaired, 0 rejected)
#    Not optional: skip it and gpt-5.4-mini log-probability comes out 474/500, ECE 0.148.
python3 inference_pipeline/fix_logprob_confidences.py <reparsed-dir> <lpfix-dir>

# 4. Lay the repaired runs over the re-parsed ones, then summarize.
cp -R <reparsed-dir> <final-dir>
cp <lpfix-dir>/*.jsonl <final-dir>/
python3 inference_pipeline/analyze.py summarize --input-dir <final-dir> --output /tmp/summary.md

# 5. Compare against the published summary. This should print nothing.
diff <(tail -n +2 /tmp/summary.md) <(tail -n +2 scoring/analysis_outputs/summary.md)
# Line 1 is skipped because it records your local input path.
```

`scoring/analysis_outputs/summary.md` is the output of exactly those commands; this was checked on
2026-11-21. Every column matches the paper except Cost (see the note below).

To check that AURC and Risk@90 do not depend on row order, unpack the archive's
`inference_outputs/adversemed_500_final/` at the repository root and run
`python3 inference_pipeline/test_coverage_risk_ties.py`. It should report 17 real runs
shuffle-invariant; without the logs it runs only the synthetic check.

### The Cost column: two price tables, and how to get the paper's

`analyze.py` sums the `cost_usd` recorded on each row at run time, from price constants that were
in the code when the run executed. Those constants went stale -- notably Opus, which carried legacy
Claude-3-era pricing at three times the published rate. The papers instead reprice the same token
counts at published list prices retrieved 2026-08-24.

**Both numbers are now reproducible here.** The price table is printed in the paper and implemented
in `inference_pipeline/reprice.py`:

```bash
python3 inference_pipeline/reprice.py <reparsed-dir> --expect-total 12.63
```

It prints repriced and logged cost side by side per model, and refuses to run on a model it has no
price for rather than letting it contribute a silent zero. The token counts both figures rest on
(`prompt_tokens`, `completion_tokens`) are in the raw logs and are not in dispute.

Three caveats ship with the table. `deepseek-chat` is absent from DeepSeek's price list and uses the
nearest successor rate; DeepSeek has since renamed and repriced again, so that row is no longer
obtainable from a current vendor page. Gemini's logged completion count excludes billed thinking
tokens, so its cost cells are lower bounds rather than estimates. And the table is dated
2026-08-24 while the runs executed on 1-2 August 2026 (UTC), so a vendor reprice between those
dates is unmodelled.

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

In the Zenodo archive, `inference_outputs/adversemed_500_raw/` is the untouched log and
`inference_outputs/adversemed_500_final/` is what the analysis consumes. Both ship so the
correction is auditable rather than assumed. Two later corrections, to the log-probability
derivation (2026-09-28) and to ties in the coverage-risk curve (2026-10-01), are described in
`CORRECTIONS.md`.

**Accuracy is unaffected.** `correct` is `chosen_answer == ground_truth` and does not depend on
confidence. `reparse_confidence.py` asserts this and exits non-zero if any row's `correct`
changes.

## Which corpus version the results use

- `benchmark/adversemed_500.jsonl` — **v1.0**, SHA-256
  `26cae9e190bc96a96814241ef4e0c779f2ff7de51dd811dcdb425a8af1c586a9`.
  **Every published result was computed on this file.**
- `benchmark/adversemed_500_v1.2.jsonl` — an **annotated** copy. Questions, choices, ground
  truth, category and tier are byte-identical to v1.0. It adds source URLs to all 500
  items, a `contestable` flag on the 150 contraindication items (25 marked contestable), and
  softer wording in 25 `false_premise_description` fields. It is provided for readers who want
  to follow the citations, and is **not** the analysis basis.

## Known limitation

`temperature_0` shares its API call with `verbal_probability` — identical prompt, identical
temperature, identical parser — so after the re-parse the two are a test-retest replicate
rather than independent methods. The papers report three elicitation methods plus a replicate,
and exclude temp-0 from the rank-correlation analysis for this reason.
