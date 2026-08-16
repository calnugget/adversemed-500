# AdverseMed-500 Working Directory

**Goal:** 500 hand-verified false-premise medical questions, released with Paper 1.

**Author of record:** Dyuthi Vallamsetty (I hand-verify every question).

**Deadline:** All 500 verified by end of Week 3 (2026-07-26).

## How this works

Every question is a **YAML file** in `verified/`. One file = one question. You append them at your own pace.

At any time, run `python3 _pipeline/build_adversemed.py` to compile all `verified/*.yaml` files into the single `datasets/adversemed_500.jsonl` that the inference pipeline consumes.

## Directory layout

```
adversemed-500/
├── README.md              (this file) — start here
├── CATEGORIES.md          The 4 false-premise categories with definitions
├── RUBRIC.md              10-check yes/no rubric — every question must pass all 10
├── SOURCES.md             All authoritative references you can use (annotated, all free)
├── PATTERNS.md            ~60 well-known medical impossibilities to pattern-match against
├── WORKFLOW.md            Prescriptive 10-step loop, do this exactly
├── PROGRAMMATIC.md        3 modes (manual, AI-assisted, batch) + recommendation
├── EXAMPLES/              4 fully-worked examples — pattern-match on these
├── verified/              Your verified questions land here (currently empty)
└── PROGRESS.md            Running progress tracker
```

## Read order

1. `CATEGORIES.md` (15 min) — the 4 categories with definitions and signals
2. `RUBRIC.md` (10 min) — the 10 checks every question must pass
3. `EXAMPLES/` (15 min) — read all 4 example YAMLs end-to-end
4. `PATTERNS.md` (10 min skim) — high-yield impossibilities you'll pattern-match
5. `WORKFLOW.md` (10 min) — the exact 10-step loop
6. `SOURCES.md` (5 min skim) — bookmark the reference URLs
7. `PROGRAMMATIC.md` (5 min) — the 3 assistance modes

Total onboarding time: **~70 minutes**. Then you're ready to write your first question.

## The workflow, one question at a time

1. **Open** `adversemed_seed_pool_n500.jsonl` in `../datasets/` and pick a seed question you haven't used yet.
2. **Decide** which of the 4 categories (see `CATEGORIES.md`) you're mutating into.
3. **Design** the false premise — what medically-impossible thing will you embed?
4. **Verify** the impossibility against a clinical reference (UpToDate, Lexicomp, FDA labeling). If a physician might reasonably disagree it's impossible, skip and pick a different seed.
5. **Write** a YAML file in `verified/` following the example pattern.
6. **Update** `PROGRESS.md` (increment the count for that category).
7. Repeat.

## Cadence + estimate

At ~15 verified questions per focused hour, 500 questions = ~33 hours of work across Weeks 2–3.

- Do 20–25 per session, then rest — mental fatigue drops accuracy fast
- Track your actual pace in `PROGRESS.md` — helps future paper-plan estimates

## Compile to final JSONL

When you want to see how the pipeline sees your work:

```bash
cd papers/paper-1-medllm-calibration
source .venv/bin/activate
python3 _pipeline/build_adversemed.py
```

Output: `datasets/adversemed_500.jsonl` + fresh SHA-256 in `datasets/manifest.json`. The manifest is what reviewers reproduce against.
