# Corrections to the released analysis outputs

**Published 2026-09-29** in commit `567b4bb` of `github.com/calnugget/adversemed-500`.

This file records the corrections applied to the AdverseMed-500 analysis after the inference runs
had been logged and after the first public release: a confidence re-parse (2026-08-24), a
log-probability fix (2026-09-28) and a coverage-risk tie fix (2026-10-01). Since **2026-11-21** the
outputs in `scoring/analysis_outputs/` carry all three.

## What was wrong

Two parsing defects, both in how a model's stated confidence was read out of its response. **No
model was re-run, and no raw response was altered.** Only the parsing was wrong, so the fix is
applied by re-reading each row's verbatim `raw_text`.

1. **DeepSeek's misspelling was silently discarded.** The confidence regex in
   `providers/deepseek.py` matched only `CONFIDENCE:`. DeepSeek-Chat writes `CONFIDANCE:` on some
   rows, so a stated confidence was dropped on **166 of 500** temperature-0 rows and **77 of 500**
   verbal-probability rows. This corrupted published verbal-probability numbers.

2. **Temperature-0 recorded a constant confidence of 1.0.** `elicitation.py::elicit_temperature_0`
   set confidence to 1.0 whenever an answer parsed, per the registered protocol §6. That makes
   ECE = Brier = 1 − accuracy identically, so three of the four reported statistics for that method
   were restatements of accuracy. Re-reading the in-band stated confidence is a **deviation from the
   registered plan** and is disclosed as such in the paper.

## What changed

Re-parsing touched **1,813 of 10,000 rows** across the 20 runs. Two rows were unparseable and are
recorded as having no confidence.

`correct` is `chosen_answer == ground_truth` and does not depend on confidence. The re-parse script
asserts this and fails loudly if any row's `correct` changes. **It did not change on any row**, so
every accuracy figure is unaffected.

Rows changed, by run:

| Run | Rows re-parsed | Changed |
|---|---|---|
| claude-opus-4-7 · temperature_0 | 500 | 499 |
| gpt-5.4-mini · temperature_0 | 500 | 499 |
| deepseek-chat · temperature_0 | 500 | 166 |
| deepseek-chat · verbal_probability | 500 | 77 |
| gemini-2.5-pro · temperature_0 | 500 | 72 |
| claude-haiku-4-5 · temperature_0 | 500 | (included in total) |
| all other runs | — | 0 |

The six cells whose published metrics move are the five temperature-0 ECE/Brier pairs and
DeepSeek's verbal-probability row. The DeepSeek row is the one most likely to be misread: the
pre-correction code yields **423/500** usable rows where the corrected analysis yields **500/500**.
That difference is a **fixed parser**, not a suppressed exclusion.

## A second correction, applied 2026-09-28: log-probability derivation

A reviewer objected that *filtering* out-of-range confidences is insufficient. It was. The analysis
dropped any row whose derived confidence fell outside 0 to 1, which on GPT-5.4-mini's
log-probability run silently removed **26 of 500 rows** — and specifically the most confident ones,
which is the worst possible direction for a calibration statistic. Of those 26, 15 were confidently
wrong and 11 confidently right, so the filter was flattering the model.

The cause was established from the data rather than assumed: every out-of-range implied
log-probability is an exact positive multiple of 2^-18, which is a serialization grid, not a
measurement. The derivation now clamps a positive log-probability inside that quantization tolerance
to a confidence of exactly 1.0, and rejects anything beyond it.

Effect on the published numbers, GPT-5.4-mini log-probability:

| | Before | After |
|---|---|---|
| Usable rows | 474/500 | **500/500** |
| ECE | 0.148 | **0.171** |
| Brier | 0.170 | **0.192** |

Accuracy is unchanged, because `correct` does not depend on confidence. The correction moves the
result **against** the model.

**A related defect that cannot be repaired.** The answer-extraction code matched the chosen option by
prefix, so the answer "A" also matched the format keyword "ANSWER". All 59 GPT rows answering A carry
a confidence at or above 0.99994, while B, C and D reach down to 0.017. The matcher is fixed for
future runs, but only the derived scalar was ever stored, not the token stream, so the logged rows
cannot be re-derived. The paper discloses that this column rests on a faulty match for 11.8% of rows
and that no conclusion depends on it.

## A third correction, applied 2026-10-01: ties in the coverage-risk curve

AURC and Risk@90 sort rows by confidence. The old `analyze.py` broke ties by input row order, so the
result depended on the order of the rows in the log file. That matters most for self-consistency,
whose confidence takes only 3 or 4 distinct values over 500 items: shuffling the rows moved AURC by
up to 0.05. A number that changes when you reorder the file is not a well-defined statistic.

`analyze.py` now averages risk within each group of equal confidence, which gives the expected value
over all orderings of that group and does not depend on row order. The best-case and worst-case
orderings are reported alongside as an envelope. `inference_pipeline/test_coverage_risk_ties.py`
checks that AURC and Risk@90 do not move when the rows are shuffled. With the inference logs present
(see below) it checks all 17 runs that have usable confidences; without them it runs only the
synthetic check.

Only AURC and Risk@90 change. n_use, accuracy, ECE and Brier do not use an ordering and are
unchanged. Cells that moved (old → new):

| Model | Method | AURC | Risk@90 |
|---|---|---|---|
| claude-haiku-4-5 | self_consistency | 0.147 → 0.160 | 0.160 → 0.159 |
| claude-haiku-4-5 | temperature_0 | 0.027 → 0.030 | |
| claude-haiku-4-5 | verbal_probability | 0.028 → 0.031 | |
| claude-opus-4-7 | self_consistency | 0.049 → 0.064 | 0.060 → 0.065 |
| claude-opus-4-7 | temperature_0 | 0.032 → 0.031 | 0.051 → 0.049 |
| claude-opus-4-7 | verbal_probability | 0.032 → 0.031 | 0.049 → 0.050 |
| deepseek-chat | self_consistency | 0.202 → 0.196 | 0.240 → 0.239 |
| deepseek-chat | temperature_0 | 0.067 → 0.056 | |
| deepseek-chat | verbal_probability | 0.071 → 0.059 | |
| gemini-2.5-pro | self_consistency | 0.022 → 0.037 | 0.031 → 0.037 |
| gemini-2.5-pro | temperature_0 | 0.003 → 0.006 | 0.016 → 0.017 |
| gemini-2.5-pro | verbal_probability | 0.006 → 0.008 | 0.016 → 0.021 |
| gpt-5.4-mini | log_probability | 0.328 → 0.338 | |
| gpt-5.4-mini | self_consistency | 0.138 → 0.141 | 0.162 → 0.166 |
| gpt-5.4-mini | temperature_0 | 0.093 → 0.092 | 0.162 → 0.163 |
| gpt-5.4-mini | verbal_probability | 0.093 → 0.098 | 0.167 → 0.165 |

**This repository was late.** The fix was made on 2026-10-01 and went into Zenodo v1.2.1 the same
day, but this repository kept the old `analyze.py` and the old AURC and Risk@90 values until
2026-11-21. During that time this file said the outputs matched the paper exactly. That was true of
n_use, accuracy, ECE and Brier, but not of AURC and Risk@90.

## How to reproduce this

From the repository root. **The raw inference logs are not in this repository.** Fetch them from
the Zenodo archive first (concept DOI `10.5281/zenodo.21961770`, which resolves to the newest
version; v1.0.0 carries no inference logs). Unpack them somewhere and point step 1 at that
directory. There are four steps, and step 2 is not optional: without it gpt-5.4-mini's
log-probability row comes out at 474/500 and ECE 0.148 instead of 500/500 and 0.171.

```
# 1. re-read confidence from each row's raw_text   (expect: 1,813 rows changed)
python3 inference_pipeline/reparse_confidence.py <raw-logs-dir> <reparsed-dir>

# 2. repair the out-of-range log-probability confidences   (expect: 26 repaired, 0 rejected)
python3 inference_pipeline/fix_logprob_confidences.py <reparsed-dir> <lpfix-dir>

# 3. the analysed input is the re-parsed logs with the repaired runs laid over them
cp -R <reparsed-dir> <final-dir>
cp <lpfix-dir>/*.jsonl <final-dir>/

# 4. analyse and compare with what is shipped here
python3 inference_pipeline/analyze.py summarize --input-dir <final-dir> --output /tmp/summary.md
diff <(tail -n +2 /tmp/summary.md) <(tail -n +2 scoring/analysis_outputs/summary.md)
```

The diff should print nothing. The first line of `summary.md` only records the input directory's
name, which is why it is skipped.

The raw logs are left untouched; corrected copies are written to a separate directory so the archive
carries both the pristine log and the analysed input.

## Verification performed 2026-11-21

The four steps above were run from this repository's own scripts on the raw logs. The resulting
`summary.md` is identical to the one shipped here (apart from the first line). That summary was then
compared cell by cell with the paper's per-run table (Table 7 of the current manuscript) on `n_use`,
accuracy, ECE, Brier, AURC and Risk@90: **120 of 120 cells match**, including the zero-usable
log-probability rows. The Cost column differs because the paper reprices at list prices retrieved
2026-08-24; `inference_pipeline/reprice.py` reproduces the paper's $12.63.

An earlier version of this section, dated 2026-09-28, said all printed rows matched. It was written
before the tie fix and stopped being true for AURC and Risk@90 on 2026-10-01 (see above).

## Also corrected on 2026-09-28

**A corpus filename collision.** A local file named `adversemed_500_v1.1.jsonl`
(SHA `6ea91511…`) was a *different* corpus from the published `adversemed_500_v1.1.jsonl`
(SHA `ab0ce969…`): it added the `contestable` flag on 150 items and softened 25 premise
descriptions. It has been renamed **`adversemed_500_v1.2.jsonl`** so that the published identifier
keeps its meaning.

**A miscount in the paper.** §3.3 states that a filter matching only the full word returns **77**
items. Recomputed from the released corpus: **76** of the 150 contraindication items quote a passage
lacking the `contraindicat` stem, of which **55** carry the abbreviated heading `§ Contra` and **21**
carry neither. 55 + 21 = 76. A case-*insensitive* `contra` search returns 56 rather than 55, because
`adversemed_010` quotes the word "contraceptives"; the heading match must therefore be stated as
case-sensitive. A literal full-word `contraindication` filter finds the word absent on **79** items.
The paper's 77 reconciles with nothing and must be corrected to 76 with the exact filter published.
