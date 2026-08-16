# Programmatic Assistance Options

You are the author of record on Paper 1. The OSF pre-registration §Additional Blinding §4 commits you to hand-verification of every AdverseMed-500 question. That commitment is **non-negotiable** — every question must be verified by you against a real clinical reference before it goes in.

However — there's a legitimate question about who *drafts* the initial mutation. You have three modes, ranked from most manual to most assisted:

## Mode A — Fully manual (recommended for first ~30 questions)

You do every step yourself:

1. Read the seed
2. Choose the category
3. Design the mutation from scratch
4. Verify against references
5. Write the YAML

**Value:** you build up genuine clinical pattern recognition. By question 30, you'll be seeing "amoxicillin + allergy" and knowing exactly what the mutation is. This is your intellectual capital as an author. Don't skip this phase.

**Pace:** ~5–8 questions per hour initially, ramping to ~15/hour as you gain fluency.

## Mode B — AI-assisted drafting (recommended after question 30)

You use me (Claude) as a research assistant to draft candidate mutations. The workflow:

1. You pick the seed and category
2. You ask me: *"Draft 3 contraindication mutations for seed at index 5471. The seed is about a patient with pneumonia. Use PATTERNS.md."*
3. I generate 3 candidate mutations following the schema, referencing PATTERNS.md
4. You review all 3 → reject the ones you don't like, pick the best one
5. **You verify the reference yourself** (open UpToDate / DailyMed / society guideline)
6. **You edit the language, prose, and clinical detail** to make sure it reads like a question YOU wrote — not a template
7. You save as YAML

**Value:** ~2–3x throughput. Legitimate research assistance, standard AI-tool disclosure.

**Non-negotiables in Mode B:**
- You reject at least some candidates every time (if you accept everything I draft, you're not really engaging — slow down)
- You verify the reference yourself, every question, every time
- You edit the language so it doesn't read like an AI template
- The AI disclosure section of your manuscript names Claude as a drafting assistant (this is Paper 0's precedent already)

## Mode C — Full-batch drafting (NOT recommended)

I generate 500 candidate mutations all at once, you verify them in bulk.

**Why this is not recommended:**
- It converges to rubber-stamping — you'll feel pressure to accept and lose the hand-verification quality
- OSF §Additional Blinding item 4 commits to hand-verification, which implies engagement per question
- The paper's authenticity as YOUR work weakens
- If a reviewer finds a bad question, they'll ask how many others slipped through — and they'll be right

**When Mode C might be OK:** if you're at question 480, deadline is Friday, and you're rushing to fill the last 20. But that's a failure mode, not the plan.

## Practical example — what a Mode B request looks like

You (in Claude Code chat window, on your laptop):

> Draft 3 contraindication mutations for seed at index 5471, which describes a 55-year-old man with community-acquired pneumonia. Prefer patterns from PATTERNS.md. Include the reference field with the exact FDA label / society guideline citation from PATTERNS.md.

Me:

> Here are 3 candidate mutations …
>
> **Candidate 1:** Amoxicillin + documented penicillin anaphylaxis (see PATTERNS.md row 1). Reference: DailyMed Amoxicillin label §Contraindications. …
>
> **Candidate 2:** Ceftriaxone + documented cephalosporin allergy. Reference: DailyMed Ceftriaxone label §Contraindications. …
>
> **Candidate 3:** Levofloxacin in a 3-year-old child. Reference: FDA label §Warnings, tendon rupture in pediatrics. …

You:

> I'll take Candidate 1. Let me verify the DailyMed label ...
>
> [opens DailyMed, reads the label]
>
> Verified. Reference confirmed. I'll edit the question slightly to reference our local emergency department rather than "ED" for consistency with other questions I've written. Saving as `verified/023_amoxicillin_penicillin_anaphylaxis.yaml`.

That's Mode B done well. Notice you:
- Picked one candidate and rejected two
- Verified the reference yourself
- Edited for consistency
- Owned the final artifact

## Recommendation

- **Questions 1–30:** Mode A. Build fluency.
- **Questions 31–450:** Mode B. Ramp throughput to ~20/hour.
- **Questions 451–500:** Mix — go back to Mode A for the last stretch to make sure quality doesn't drift.

Ping me when you want to switch to Mode B and I'll walk you through drafting the first one interactively.
