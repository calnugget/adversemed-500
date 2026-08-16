# Sources of Truth — Where to Verify

Every question in `verified/` must have at least ONE authoritative reference. Below are all the sources you can use, all free and accessible without a medical school subscription.

## Tier 1 — Highest authority (regulatory / society guidelines)

These are the strongest possible references. Prefer them when available.

### FDA drug labels via DailyMed
- **URL:** https://dailymed.nlm.nih.gov
- **What's there:** every FDA-approved drug's official prescribing information, including §Contraindications, §Warnings and Precautions, §Drug Interactions.
- **How to use:** Search by drug name (generic or brand). Open the label. Look at §Contraindications for absolute no-goes. §Drug Interactions for DDIs.
- **When to cite:** contraindications, DDIs, dosing questions. This is the most defensible reference for a US-focused benchmark.

### CDC (Centers for Disease Control)
- **URL:** https://www.cdc.gov
- **What's there:** infectious disease guidelines, immunization schedules, post-exposure prophylaxis protocols, epidemiologic references.
- **How to use:** For rabies PEP, HIV PEP, tetanus prophylaxis, ACIP vaccination recommendations, meningococcal exposure protocols. Direct-URL each specific guideline.
- **When to cite:** impossible-timing questions involving infectious diseases and PEP.

### IDSA (Infectious Diseases Society of America)
- **URL:** https://www.idsociety.org/practice-guideline/
- **What's there:** antibiotic guidelines, community-acquired pneumonia, UTI, sepsis, endocarditis, etc.
- **How to use:** Free full-text guidelines. Cite specific line or section.

### American Diabetes Association Standards of Care
- **URL:** https://diabetesjournals.org/care/issue/49/Supplement_1 (annual January supplement — free)
- **What's there:** T1D and T2D management standards.
- **When to cite:** anything about diabetes drug selection, especially T1D + oral hypoglycemics.

### American Heart Association / American College of Cardiology
- **URL:** https://www.acc.org/guidelines
- **What's there:** cardiovascular management guidelines.

### WHO Model List of Essential Medicines
- **URL:** https://www.who.int/publications/i/item/WHO-MHP-HPS-EML-2023.02
- **When to cite:** international/global-health flavor when relevant.

## Tier 2 — Point-of-care summaries (widely accepted as authoritative)

### UpToDate
- **URL:** https://www.uptodate.com
- **Access:** subscription required. Your school may provide it via library. Ask.
- **How to use:** Search a topic; use §Contraindications, §Drug interactions, §Approach sections.
- **When to cite:** cite by article title + subsection ("UpToDate: 'X' → 'Drug interactions'").

### Merck Manuals Professional Version
- **URL:** https://www.merckmanuals.com/professional
- **Access:** completely free.
- **What's there:** essentially a physician-level textbook covering all major topics.
- **When to cite:** great fallback when UpToDate isn't accessible.

### Lexicomp
- **URL:** https://online.lexi.com
- **Access:** subscription (often provided by school or hospital library). Also available inside the free Wolters Kluwer app on some platforms.
- **What's there:** drug entries with contraindications, interactions, dosing.
- **When to cite:** drug-specific claims.

### MedlinePlus (NIH)
- **URL:** https://medlineplus.gov
- **Access:** completely free.
- **What's there:** patient-level and clinician-friendly summaries. Good for cross-checking basic facts.

### DrugBank
- **URL:** https://go.drugbank.com
- **Access:** free with academic registration.
- **What's there:** structured drug data including interactions and contraindications.

### PubChem (NIH)
- **URL:** https://pubchem.ncbi.nlm.nih.gov
- **Access:** free.
- **What's there:** chemical + pharmacologic data. Good for verifying mechanism claims.

## Tier 3 — Primary literature and clinical calculators

### PubMed
- **URL:** https://pubmed.ncbi.nlm.nih.gov
- **Access:** free.
- **What's there:** every published biomedical paper. Cite by PMID when possible.
- **Use case:** for landmark trials that establish standard-of-care.

### Cochrane Library
- **URL:** https://www.cochranelibrary.com
- **Access:** free for many countries including US.
- **What's there:** systematic reviews.

### MDCalc
- **URL:** https://www.mdcalc.com
- **What's there:** clinical calculators (CHA₂DS₂-VASc, Wells score, etc.).
- **Use case:** helpful when a question involves a risk-score / dosing calculation.

### Drugs.com (professional side)
- **URL:** https://www.drugs.com/pro/
- **Access:** free.
- **What's there:** consolidated drug info drawn from FDA labels and other sources.

## Tier 4 — Starting-point references (use to orient, then upgrade)

### Wikipedia
- **When acceptable:** to get oriented on a topic and find the primary sources it cites.
- **When NOT acceptable:** as your ONLY citation. Every claim you make in your `reference:` field must trace back to a Tier 1 or Tier 2 source.

### RxList / Drugs.com consumer pages
- Same rule as Wikipedia — use to orient, then find the underlying FDA label or society guideline.

## Reference-formatting cheat sheet

When you fill in the `reference:` field in your YAML file, format it like this:

```yaml
reference:
  - "Lexicomp: Warfarin — Interactions: Trimethoprim-sulfamethoxazole (Category X)"
  - "UpToDate: 'Warfarin and drug interactions' — 'Cotrimoxazole' section"
  - "FDA DailyMed: Warfarin sodium tablets label §7 Drug Interactions"
  - "IDSA Community-Acquired Pneumonia Guidelines 2019 — Table 3 (β-lactam alternatives)"
  - "ADA Standards of Care 2026 §9.1 (Insulin Therapy in Type 1 Diabetes)"
  - "CDC ACIP Rabies PEP recommendations MMWR Vol 57 §Post-exposure prophylaxis timing"
  - "PubMed PMID: 33852020 — 'Bactrim and warfarin: a case-control study' (2021)"
```

Multiple references per question is fine — often stronger.

## Access hacks

- **UpToDate access:** Ask your school librarian if they provide it. Many Harker-tier private schools do. If not, ask a family friend who's in healthcare — most doctors have institutional access.
- **Lexicomp access:** Same as UpToDate — usually institutional.
- **PubMed full-text:** Many articles are open-access. If you hit a paywall, try Sci-Hub (technically a gray area but widely used in academia) or the "PubMed Central" version of the article.
- **When you're stuck:** the FDA label via DailyMed and the Merck Manuals Professional Version cover 95% of contraindications, DDIs, and standard-of-care claims. Free. Just use those.
