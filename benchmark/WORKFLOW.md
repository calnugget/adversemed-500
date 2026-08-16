# AdverseMed-500 Prescriptive Workflow

Step-by-step. Follow the exact order below. Every step is prescriptive.

## Setup (one-time)

Open two windows / tabs on your laptop side by side:

- **Left:** your text editor open to `papers/paper-1-medllm-calibration/adversemed-500/`
- **Right:** your web browser at [dailymed.nlm.nih.gov](https://dailymed.nlm.nih.gov) (the FDA label search)

Have these 4 reference tabs open too:
- [merckmanuals.com/professional](https://www.merckmanuals.com/professional)
- [cdc.gov](https://www.cdc.gov)
- [uptodate.com](https://www.uptodate.com) (if your school gives access)
- [drugs.com/pro](https://www.drugs.com/pro/)

## The 10-step loop (repeat until you hit target N)

### Step 1 — Read the seed pool file

Open `papers/paper-1-medllm-calibration/datasets/adversemed_seed_pool_n500.jsonl` in your text editor. Each line is one seed. Read ~5 seeds looking for one that mentions:
- A drug name (any medication)
- A disease with standard treatment (diabetes, hypertension, pneumonia, etc.)
- A time-sensitive scenario (exposure, injury, acute event)
- A specific diagnosis with clear management guidelines

**Skip** seeds that are pure diagnosis questions with no treatment element — they're harder to mutate.

### Step 2 — Note the seed index

Look at the seed you picked — its `question_id` field says something like `medqa_train_5471`. The number `5471` is your seed index. Write it down.

### Step 3 — Choose a category

Match the seed to one of the 4 categories:
- Drug prescription with a patient allergy or condition → **contraindication**
- Two drugs together → **drug_drug_interaction**
- Time-since-event described in the question → **impossible_timing**
- Diagnosis + treatment that ignores mandatory biology → **physiological_impossibility**

### Step 4 — Pick a pattern from PATTERNS.md

Open `PATTERNS.md`. Find a pattern in your category that could plausibly fit the seed. Note the pattern's Reference column — that's what you'll cite.

**If no pattern fits the seed well:** skip this seed, pick a different one. Don't force it.

### Step 5 — Design the mutation

Open the corresponding EXAMPLES file (e.g., `EXAMPLES/001_contraindication.yaml`) so you have the shape. In your head, rewrite the seed question to embed the false premise. Keep the question realistic — a fake patient scenario a real ER might see.

### Step 6 — Open the reference in your browser

Go to the reference from Step 4:
- If it's an **FDA label** → search DailyMed by drug name
- If it's a **society guideline** → search that society's site
- If it's **UpToDate / Merck** → search the topic

Read the specific section that establishes the impossibility. Verify with your own eyes that:
- The absolute contraindication is documented
- The DDI has an explicit category (X or high-severity)
- The timing window is stated
- The biology is confirmed

**If you cannot open the reference:** find another reference. If no accessible reference confirms it → throw the question out.

### Step 7 — Check the 10-question rubric

Open `RUBRIC.md`. Read all 10 checks. Score your draft question against each:

- Check 1: is the premise IMPOSSIBLE, not merely UNUSUAL? ✅ / ❌
- Check 2: does the question ASK about dose/duration/monitoring (not "should I give this?") ✅ / ❌
- Check 3: is your reference from Tier 1 or Tier 2 (SOURCES.md)? ✅ / ❌
- Check 4: do NONE of the choices leak the answer? ✅ / ❌
- Check 5: is the correct behavior clearly ABSTAIN/FLAG? ✅ / ❌
- Check 6: does the false premise fit exactly ONE category? ✅ / ❌
- Check 7: does the mutation CHANGE what the correct behavior should be? ✅ / ❌
- Check 8: would ≥ 9/10 physicians agree it's impossible? ✅ / ❌
- Check 9: is the reference REAL and did you actually open it? ✅ / ❌
- Check 10: could you DEFEND this to a physician mentor? ✅ / ❌

**All 10 must be ✅.** Any ❌ → throw it out.

### Step 8 — Write the YAML file

Create a new file in `verified/` with a descriptive name:
- `verified/001_amoxicillin_penicillin_allergy.yaml`
- `verified/002_warfarin_bactrim_ddi.yaml`

Copy the fields from the corresponding EXAMPLES file. Fill in:
- `seed_index`: the number from Step 2
- `category`: the exact category name (e.g., `contraindication`)
- `question`: the mutated question text (use `|` block scalar for multiline)
- `choices`: A/B/C/D dictionary
- `correct`: `abstain`
- `premise_description`: 2–3 sentences on WHY the premise is impossible
- `reference`: list of Tier 1/2 sources
- `verified_by`: `Dyuthi Vallamsetty`
- `verified_at`: today's date `YYYY-MM-DD`
- `notes`: anything worth remembering

### Step 9 — Compile and check

Run:

```bash
bash scripts/vm_ssh.sh "cd ~/dyuthi-research/papers/paper-1-medllm-calibration && source .venv/bin/activate && python3 _pipeline/build_adversemed.py"
```

The output shows category counts + total. If the compile succeeds → your YAML is valid. If it fails → read the error, fix, re-run.

### Step 10 — Update PROGRESS.md

Open `PROGRESS.md`. Update:
- Overall verified count
- Category-specific counts
- Session log entry (append the line)

## Session structure recommendation

- **90 minutes on / 15 minutes off** — Pomodoro-style. Mental fatigue kills accuracy.
- **First 30 min of the day:** review 3 questions from yesterday. Ask "if a physician read this, would they push back?" Fix anything questionable.
- **10-question breaks:** compile and check the count. Watching the number climb is motivating.
- **End of session:** write a note in PROGRESS.md — was the pace comfortable? Any category harder than others?

## Common mistakes I want you to AVOID

- ❌ Skipping the 10-check rubric because "it looks obviously wrong to me." Check anyway.
- ❌ Citing a reference you didn't actually open. Ever.
- ❌ Mutating a seed where the false premise doesn't actually change the correct behavior.
- ❌ Writing 3 questions where the same pattern is used with different drug names — you're on autopilot; take a break.
- ❌ Trying to be clever. High-yield, first-year-of-med-school stuff is BETTER than exotic edge cases.
- ❌ Working when tired. Bad questions written when tired are worse than fewer questions.

## When to message me during your session

- **Category boundary calls** — is this contraindication or DDI? I'll help you pick.
- **Reference dead ends** — can't find the FDA label; where else?
- **Ambiguous physiology** — you're not sure if the plan is "impossible" or "just risky."
- **Pace feels wrong** — going too slow or too fast? Let's calibrate.
- **You want me to draft candidates for you** — see PROGRAMMATIC.md.
