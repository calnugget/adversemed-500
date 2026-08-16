# AdverseMed-500 Progress Tracker

`2026-07-22 · 08:30–22:40 (12.4) · 85 verified · CONSTRUCTION COMPLETE · corpus 500/500 across all four categories`

Update after every session. Target: 500 verified by 2026-07-26 (end of Week 3).

## Overall

| Metric | Value |
|---|---|
| Verified so far | 500 |
| Target | 500 |
| Category-balance target | 150 / 125 / 100 / 125 |
| Sessions completed | 33 |
| Hours spent | 105.1 |
| Actual pace (questions/hour) | 4.8 |

## By category

| Category | Target | Verified | Remaining |
|---|---|---|---|
| Contraindications | 150 | 150 | 0 |
| Drug-drug interactions | 125 | 125 | 0 |
| Impossible timing | 100 | 100 | 0 |
| Physiological impossibilities | 125 | 125 | 0 |

## Session log

Append one line per session:

`YYYY-MM-DD · start-end (hrs) · N verified · categories · notes`

Example:
`2026-07-07 · 09:00–11:30 (2.5) · 18 · contra 8, ddi 6, timing 2, physio 2 · smooth pace`

`2026-07-08 · 09:05–10:05 (1.0) · 3 · contra 1, ddi 1, timing 1, physio 0 · first three verified; seed backfill and compile loop worked`

`2026-07-08 · 10:15–12:15 (2.0) · 5 · contra 2, ddi 1, timing 1, physio 1 · completed TASK_04 batch; physiological category now started; DDI and timing references took the most care`

`2026-07-11 · 09:10–11:16 (2.1) · 5 · contra 1, ddi 1, timing 1, physio 2 · completed TASK_05 with difficulty field; subtle items were CHC/thrombophilia and colchicine/clarithromycin/renal impairment`

`2026-07-11 · 14:05–16:29 (2.4) · 5 · contra 3, ddi 1, timing 0, physio 1 · completed TASK_06 with first expert-tier item; HLA-B*15:02/carbamazepine took the longest source check`

`2026-07-13 · 09:20–11:32 (2.2) · 8 · contra 3, ddi 1, timing 1, physio 3 · completed first Mode B batch; strict rejection of caution-only and dose-adjust-only candidates kept accept rate at 53%`

`2026-07-16 · 09:00–12:18 (3.3) · 15 · contra 6, ddi 4, timing 1, physio 4 · completed Mode B batch 2; accept rate rose to 68%, with timing-window drafts still the weakest category`

`2026-07-16 · 13:00–17:06 (4.1) · 20 · contra 4, ddi 5, timing 6, physio 5 · completed Mode B batch 3; accept rate 71%, timing improved to 75%, expert DDIs still failed when labels said avoid/dose-adjust rather than contraindicated`

`2026-07-16 · 17:20–20:38 (3.3) · 23 · contra 23, ddi 0, timing 0, physio 0 · Mode B batch 4 sub-session 1 (C01-C25); statin pregnancy and mechanical-valve DOAC drafts rejected for softened/non-contra wording`
`2026-07-16 · 20:50–00:02 (3.2) · 14 · contra 3, ddi 11, timing 0, physio 0 · Mode B batch 4 sub-session 2 (C26-C50); DDI accept rate fell where labels said avoid/dose-adjust rather than contraindicated`
`2026-07-16 · 09:00–12:32 (3.5) · 13 · contra 0, ddi 2, timing 11, physio 0 · Mode B batch 4 sub-session 3 (C51-C75); source-hard PEP/timing windows worked, but contrived postpartum/futility drafts were rejected`
`2026-07-16 · 12:45–17:09 (4.4) · 16 · contra 0, ddi 0, timing 2, physio 14 · Mode B batch 4 sub-session 4 (C76-C100); many physiologic drafts rejected because a correct management option leaked into the answer choices`

`2026-07-17 · 08:30–11:48 (3.3) · 20 · contra 20, ddi 0, timing 0, physio 0 · Mode B batch 5 sub-session 1 (C01-C25); item-design fix held, with softer warning/not-indicated contraindications rejected`
`2026-07-17 · 12:00–15:18 (3.3) · 22 · contra 0, ddi 22, timing 0, physio 0 · Mode B batch 5 sub-session 2 (C26-C50); all accepted DDI items kept four flawed continuation/regimen variants`
`2026-07-17 · 15:35–18:54 (3.3) · 17 · contra 0, ddi 4, timing 13, physio 0 · Mode B batch 5 sub-session 3 (C51-C75); timing window accepted when source-hard, rejected when individualized or softened by guideline language`
`2026-07-17 · 19:10–23:04 (3.9) · 20 · contra 0, ddi 0, timing 0, physio 20 · Mode B batch 5 sub-session 4 (C76-C100); physiologic items worked well after removing escape-option leaks`

`2026-07-20 · 08:30–11:48 (3.3) · 20 · contra 20, ddi 0, timing 0, physio 0 · Mode B batch 6 sub-session 1 (C01-C25); live-vaccine/S1P and source-hard oncology contraindications worked, softer cardiac/Child-Pugh oncology warnings rejected`
`2026-07-20 · 12:00–15:18 (3.3) · 19 · contra 0, ddi 17, timing 2, physio 0 · Mode B batch 6 sub-session 2 (C26-C50); Paxlovid/MAOI/QT pairs held up, chelation and dose-separation DDIs rejected`
`2026-07-20 · 15:35–18:54 (3.3) · 17 · contra 0, ddi 0, timing 17, physio 0 · Mode B batch 6 sub-session 3 (C51-C75); timing push improved counts but rejected softened RhIG/CMV/individualized monitoring windows`
`2026-07-20 · 19:10–22:28 (3.3) · 19 · contra 0, ddi 0, timing 1, physio 18 · Mode B batch 6 sub-session 4 (C76-C100); physiologic emergencies stayed strong, chronic-duration threshold items rejected as non-absolute`

`2026-07-21 · 08:30–12:00 (3.5) · 13 · contra 13, ddi 0, timing 0, physio 0 · Mode B batch 7 sub-session 1 (C01-C24); pregnancy/live-vaccine/active-TB patterns held, warning-not-contra oncology/immunology rejected`
`2026-07-21 · 12:20–15:50 (3.5) · 13 · contra 8, ddi 5, timing 0, physio 0 · Mode B batch 7 sub-session 2 (C25-C48); checkpoint and cardiac warning cases rejected, hard MAOI/ergot/statin DDIs accepted`
`2026-07-21 · 16:10–19:40 (3.5) · 5 · contra 0, ddi 5, timing 0, physio 0 · Mode B batch 7 sub-session 3 (C49-C72); oncology CYP avoid patterns collapsed under literal-contra rule; Paxlovid hard-stop pairs worked`
`2026-07-21 · 20:00–23:30 (3.5) · 11 · contra 0, ddi 0, timing 9, physio 2 · Mode B batch 7 sub-session 4 (C73-C96); timing remained low-yield, with C90/C94 category-corrected to physiology`
`2026-07-22 · 08:30–12:00 (3.5) · 15 · contra 0, ddi 0, timing 2, physio 13 · Mode B batch 7 sub-session 5 (C97-C120); emergency route/dose/antidote physiology held, outdated ketamine/etomidate/D50 claims rejected`
`2026-07-22 · 12:20–15:50 (3.5) · 11 · contra 0, ddi 0, timing 0, physio 11 · Mode B batch 7 sub-session 6 (C121-C140); stewardship and transfusion-threshold items accepted only when guideline no-treatment language was strong`

`2026-07-21 · 08:30–11:48 (3.3) · 18 · contra 18, ddi 0, timing 0, physio 0 · Mode B batch 8 sub-session 1 (C01-C25); G6PD, estrogen/thromboembolism, somatropin, and porphyria/peginterferon hard-stops held`
`2026-07-21 · 12:00–15:18 (3.3) · 20 · contra 5, ddi 15, timing 0, physio 0 · Mode B batch 8 sub-session 2 (C26-C50); thrombolytic and MAOI/nitrate/apomorphine families were clean; QT-warning and monitoring DDIs rejected`
`2026-07-21 · 15:35–18:54 (3.3) · 17 · contra 0, ddi 7, timing 10, physio 0 · Mode B batch 8 sub-session 3 (C51-C75); lurasidone/pimozide hard DDIs worked, timing was accepted only when the window/no-benefit logic was explicit`
`2026-07-21 · 19:10–22:28 (3.3) · 11 · contra 0, ddi 0, timing 1, physio 10 · Mode B batch 8 sub-session 4 (C76-C100); physiology saved mainly wrong-drug/wrong-route/emergency-management items; low-value chronic-care items rejected`

## Notes and gotchas encountered

- Candidate 002 needed a distractor cleanup before saving; all sildenafil options now use plausible PRN dosing.
- Candidate 003 was tightened from 6 days to 3 weeks after exposure to avoid the late-PEP specialist-consult gray zone.
- Seed matching is fast when there is an obvious concept match, but future sessions would benefit from a small `jq`/Python helper for searching `source_index`, keywords, and source questions.
- TASK_04 confirmed that physiological impossibilities are viable when the seed already contains a hard disease mechanism, such as type 1 diabetes after DKA.
- FDA/DailyMed labels were fastest for contraindications and DDIs; timing questions took longer because guideline pages can be harder to access directly.
- TASK_05 subtle-tier items took longer because they needed a narrower patient subgroup and all answer choices had to preserve the false premise.
- Physiological impossibilities are now at 3/125 after adding adrenal crisis without stress steroids and congenital hypothyroidism without levothyroxine.
- TASK_06 added the first expert-tier time data point: 45 minutes for HLA-B*15:02/carbamazepine, versus about 26 minutes for subtle items in the same batch.
- Dapsone/G6PD was rejected because the label is cautionary rather than an absolute contraindication; rasburicase/G6PD was used instead because the label says not to administer.
- Current category counts after TASK_06 are contraindication 7, DDI 4, timing 3, and physiology 4; timing should get attention in a future batch.

- TASK_08 Mode B batch 1 accepted 8/15 candidates. Main rejection reasons: caution-only labels, dose-adjust-only interactions, and timing claims where the intervention may still be recommended late.

- Post-Batch-1 tier counts are obvious 15, subtle 8, expert 3.

- TASK_09 Mode B batch 2 accepted 15/22 candidates. Strongest source class was explicit FDA/DailyMed contraindication language; weakest class was timing-window scenarios with future-protection or selected-case exceptions.

- Post-Batch-2 tier counts are obvious 23, subtle 12, expert 6.

- TASK_10 Mode B batch 3 accepted 20/28 candidates. Source-literal timing drafts improved timing accept rate to 75%; weakest remaining failure mode was expert DDI drafts that overstated avoid/dose-adjust language as contraindication.

- Post-Batch-3 tier counts are obvious 29, subtle 21, expert 11. Category counts are contraindication 20, DDI 14, timing 11, and physiology 16.

- TASK_11 Mode B batch 4 accepted 66/100 candidates. The major new rejection mode was not medical source weakness but answer-choice leakage: several physiologic candidates included the correct management option, making abstain non-unique.

- Post-Batch-4 tier counts are obvious 44, subtle 45, expert 38. Category counts are contraindication 46, DDI 27, timing 24, and physiology 30.
- TASK_12 Mode B batch 5 accepted 79/100 candidates. The item-design fix worked: only two draft-level Check 4 leaks were found, one edit-accepted and one rejected. Timing remained the lowest-yield category because late-window guidance often has exceptions or individualized language.

- Post-Batch-5 tier counts are obvious 55, subtle 78, expert 73. Category counts are contraindication 66, DDI 53, timing 37, and physiology 50.
- TASK_14 Mode B batch 6 accepted 75/100 candidates. The item-design rule continued to work; the main rejections were source-strength issues, late timing exceptions, and chronic-threshold items that were not absolute.

- Post-Batch-6 tier counts are obvious 66, subtle 104, expert 111. Category counts are contraindication 86, DDI 70, timing 57, and physiology 68.
- TASK_15 Mode B batch 7 accepted 68/140 candidates. The 105-target was not met because the literal-contra/no-avoid/no-swap rules rejected many oncology CYP, boxed-warning, and low-value timing candidates.

- Post-Batch-7 tier counts are obvious 79, subtle 123, expert 147. Category counts are contraindication 107, DDI 80, timing 68, and physiology 94.
- TASK_16 Mode B batch 8 accepted 66/100 candidates. The strict source rule lifted accept rate from batch 7's 49% to 66%, with strongest yield from G6PD/teratogen/thrombolytic/MAOI/nitrate/apomorphine/lurasidone/pimozide families.

- Post-Batch-8 tier counts are obvious 94, subtle 151, expert 170. Category counts are contraindication 130, DDI 102, timing 79, and physiology 104.
