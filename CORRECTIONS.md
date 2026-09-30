# Corrections to the released analysis outputs

**Published 2026-09-29** in commit `567b4bb` of `github.com/calnugget/adversemed-500`.

This file records a correction applied to the AdverseMed-500 analysis on **2026-08-24**, after the
inference runs had been logged and after the first public release. The public GitHub repository
still carries the **pre-correction** numbers; this document and the regenerated outputs beside it
replace them.

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

## How to reproduce this

From the repository root. **The raw inference logs are not in this repository** — fetch them from
the Zenodo archive first (concept DOI `10.5281/zenodo.21961770`, which resolves to the newest
version; v1.0.0 carries no inference logs). Unpack them somewhere and point the first command at
that directory:

```
python3 inference_pipeline/reparse_confidence.py <raw-logs-dir> <reparsed-dir>
python3 inference_pipeline/analyze.py summarize --input-dir <reparsed-dir> --output scoring/analysis_outputs/summary.md
```

The raw logs are left untouched; corrected copies are written to a separate directory so the archive
carries both the pristine log and the analysed input.

## Verification performed 2026-09-28

All 20 analysis files and `summary.md` were regenerated from the re-parsed inputs and compared cell
by cell against the paper's Table 6, on `n_use`, accuracy, ECE, Brier, AURC and Risk@90.

**All 17 rows the paper prints match exactly.** The three runs not compared are
`claude-haiku-4-5`, `claude-opus-4-7` and `gemini-2.5-pro` on `log_probability`, which have 0 of 500
usable rows and are not printed as table rows in the paper.

## Also corrected on 2026-09-28

**A corpus filename collision.** A local file named `adversemed_500_v1.1.jsonl`
(SHA `6ea91511…`) was a *different* corpus from the published `adversemed_500_v1.1.jsonl`
(SHA `ab0ce969…`): it added the `contestable` flag on 150 items and softened 25 premise
descriptions. It has been renamed **`adversemed_500_v1.2.jsonl`** so that the published identifier
keeps its meaning. `benchmark/RELEASE_NOTES_v1.1.md` continues to describe the published file and its
hash, which is correct.

**A miscount in the paper.** §3.3 states that a filter matching only the full word returns **77**
items. Recomputed from the released corpus: **76** of the 150 contraindication items quote a passage
lacking the `contraindicat` stem, of which **55** carry the abbreviated heading `§ Contra` and **21**
carry neither. 55 + 21 = 76. A case-*insensitive* `contra` search returns 56 rather than 55, because
`adversemed_010` quotes the word "contraceptives"; the heading match must therefore be stated as
case-sensitive. A literal full-word `contraindication` filter finds the word absent on **79** items.
The paper's 77 reconciles with nothing and must be corrected to 76 with the exact filter published.
