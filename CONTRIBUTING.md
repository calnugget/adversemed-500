# Contributing to AdverseMed-500

Thank you for your interest in AdverseMed-500. This repo ships both a
**frozen benchmark** (the 500 verified questions used in the paper) and
an **active generator** (`generator/`, the `adversemed-gen` PyPI
package). Contribution rules differ between the two.

## What we welcome

### Benchmark issues (`benchmark/`)

- **Item-level errata**: if you believe a specific item's ground truth
  is wrong, open an issue titled
  `[Item adversemed_NNN] Ground-truth challenge` with:
  1. The question ID.
  2. Why you believe the premise is *not* actually false, or why the
     abstain-only rationale is unsound.
  3. Citation(s) to CDC / FDA / peer-reviewed guideline that support
     your alternative interpretation.

  Well-supported challenges will be triaged for a v1.1 (post-publication)
  errata release; the v1.0 benchmark is frozen for the paper.
- **Reference-link drift**: if a URL in `verification.reference` is
  dead, open an issue with the archived (wayback) URL as a replacement.

### Generator improvements (`generator/`)

We welcome PRs for:

- **New adversarial patterns** — add to `generator/patterns.py` and
  `benchmark/PATTERNS.md`. Every new pattern needs:
  - Category (`contraindication` | `drug_drug_interaction` |
    `impossible_timing` | `physiological_impossibility`).
  - Justification (why is this a distinct adversarial mode?).
  - At least one example question stem that exhibits the pattern.
- **Prompt improvements** for `generator/prompts/*.md` (mutator,
  verifier, self-test).
- **Provider additions** for `inference_pipeline/providers/*.py`.
- **New elicitation methods** in `inference_pipeline/elicitation.py`.
- **Analysis improvements** in the scoring / analysis scripts.
- **Bug fixes** anywhere.

### Analysis + downstream reuse

- Downstream calibration analyses using the released dataset are
  welcome and encouraged. Please cite the paper + Zenodo DOI +
  seed sources (MedQA / MMLU-med / PubMedQA per
  `benchmark/SOURCES.md`).
- Extensions of the generator to non-medical domains: welcomed as
  *forks*, not PRs (the AdverseMed-500 name is scoped to medical
  content). Link back and we'll boost.

## What we do NOT accept

- Changes to `benchmark/adversemed_500.jsonl` — this is the frozen
  benchmark. Errata are collected for a future v1.1 release, not
  applied to v1.0.
- Changes to `benchmark/verified_yaml/*.yaml` for questions in
  v1.0 — same reason.
- New questions added to the 500 (would break `manifest.json` SHA
  checksum). Additional questions land in future
  `adversemed_v1.1_delta.jsonl` after verification.
- PRs that change any reported result in the manuscript before the
  paper is published (would violate the OSF preregistration
  osf.io/mehu4).

## Reporting a bug

Open an issue at
https://github.com/calnugget/adversemed-500/issues with:

1. Which module and what command line you ran.
2. Python version + `pip freeze | grep -E "adversemed|httpx|pyyaml"`.
3. Full error traceback.
4. What you expected to happen.

## Proposing a code change

1. Fork the repo (using your GitHub identity).
2. Create a feature branch: `git checkout -b add-pattern-qt-prolongation`.
3. Make the smallest change that addresses the issue.
4. If you added a new adversarial pattern, add a matching entry in
   `benchmark/PATTERNS.md` AND include at least one example that
   passes the mutator → filter → verify pipeline. Do NOT auto-add
   the generated items to `adversemed_500.jsonl`.
5. Run the notebook (`notebooks/quickstart.ipynb`) end-to-end.
6. Commit with a descriptive message.
7. Open a PR against `main` with:
   - Summary of the change.
   - Link to the issue this addresses.
   - Test evidence (notebook output, `pytest` if the module has
     tests).

## Adding a new adversarial pattern (worked example)

```python
# 1. Add to generator/patterns.py
{
    "name": "qt_prolongation_stacking",
    "category": "drug_drug_interaction",
    "difficulty_hint": "expert",
    "trigger_terms": ["QT", "ondansetron", "methadone", "sotalol"],
    "example_stem_seed": "A patient on methadone is prescribed ...",
    "justification": (
        "Additive QT prolongation when 2+ QT-prolonging drugs are "
        "co-prescribed; correct action is to avoid the combination or "
        "monitor ECG, not to answer any dosing question about the pair."
    ),
},
```

```markdown
# 2. Add to benchmark/PATTERNS.md under the drug_drug_interaction section

### qt_prolongation_stacking
- Category: drug_drug_interaction
- Difficulty hint: expert
- Rationale: additive QT prolongation risk when 2+ QT-prolonging drugs
  are co-prescribed. Correct behavior: avoid combination or ECG monitor.
- Example seed: "A patient on methadone is prescribed ..."
```

```bash
# 3. Verify the pipeline still parses PATTERNS.md
python -c "from generator.patterns import PATTERNS; print(len(PATTERNS), 'patterns loaded')"
```

## Physician verification

We take physician verification seriously. If you are a physician (MD,
DO, PharmD, or clinician-in-training) and want to help re-verify items
for a v1.1 release, please email `28dyuthiv@students.harker.org`. We'll
share the verification protocol + rubric and credit you in the v1.1
release notes.

## Code style

- Python 3.10+.
- `black` with default settings for auto-formatting.
- Docstrings for anything more complex than a 5-line function.
- Prefer stdlib; new deps need justification in the PR.
- Do NOT vendor API keys in fixtures or tests — use
  `secrets_helper.py` or env vars.

## Security

If you find a security issue (e.g., a prompt-injection vulnerability in
the verifier that could poison future generations), email
`28dyuthiv@students.harker.org` privately rather than opening a public
issue. Response within 7 days and credit in the fix commit.

## Governance

Sole maintainer: Dyuthi Vallamsetty. PR reviews may take 1–2 weeks
during school term.

## Code of conduct

Be kind. This is a solo-author student research project. Constructive
critique of the generator design or the benchmark methodology is
welcome; personal attacks are not.
