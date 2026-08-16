# High-Yield Impossibility Patterns

These are approximately **60 well-known medical impossibilities** organized by category. You can pattern-match seed questions against them and mutate accordingly.

Every pattern here is:
- Well-established in first-year medical school curricula
- Verifiable via Tier 1 references (FDA labels, CDC, society guidelines)
- Unambiguous — >95% of practicing physicians would agree

Cite the reference next to your YAML `reference:` field.

## Contraindications (target ~150 verified from these patterns)

### Drug-allergy contraindications

| Drug | Contraindication | Reference |
|---|---|---|
| Any penicillin (amoxicillin, ampicillin, piperacillin) | Documented anaphylaxis to penicillins | FDA label §Contraindications |
| Any cephalosporin (cefazolin, ceftriaxone) | Documented anaphylaxis to cephalosporins | FDA label §Contraindications |
| Sulfonamide antibiotics (TMP-SMX, sulfasalazine) | Documented sulfa allergy | FDA label |
| NSAIDs (ibuprofen, naproxen, aspirin) | Aspirin-exacerbated respiratory disease with asthma | AAFP consensus |
| Latex-containing products | Latex allergy | Any latex product package insert |
| Contrast media (iodinated) | Prior anaphylactoid reaction | ACR Manual on Contrast Media |

### Drug-condition contraindications

| Drug | Contraindicated condition | Reference |
|---|---|---|
| Metformin | GFR < 30 mL/min/1.73m² | ADA Standards §9 |
| ACE inhibitors / ARBs | Pregnancy (any trimester) | FDA Category X labels |
| Warfarin | Pregnancy | FDA label (teratogenic) |
| Isotretinoin | Pregnancy | iPLEDGE program mandatory |
| NSAIDs | Active GI bleed / peptic ulcer | UpToDate |
| Beta-blockers (non-selective) | Severe reactive airway disease | UpToDate |
| Verapamil / diltiazem | Wolff-Parkinson-White with atrial fibrillation | ACC/AHA WPW guidelines |
| Digoxin | Ventricular tachycardia | UpToDate |
| Contrast media (gadolinium) | GFR < 30 mL/min/1.73m² | ACR guidance |
| Live vaccines | Severe immunocompromise or pregnancy | CDC ACIP |
| Nitrates | Recent phosphodiesterase-5 inhibitor use (sildenafil) | FDA label |
| Tetracyclines / doxycycline | Pregnancy or children < 8 years | FDA label |
| Fluoroquinolones | Children (unless specific indication) | FDA label |
| Aminoglycosides | Myasthenia gravis | UpToDate |
| Bisphosphonates | Esophageal disorders (achalasia, stricture) | FDA label |
| High-dose steroids | Untreated systemic fungal infection | FDA label |
| Metformin (extended-release form) | Any dialysis-dependent renal failure | FDA label |
| Carbamazepine | HLA-B*15:02 positive in a carbamazepine-naive patient | CPIC 2017 guideline + FDA carbamazepine label |
| Rasburicase (Elitek) | G6PD deficiency | FDA Elitek label §4 / boxed warning |
| Dapsone / primaquine / nitrofurantoin | Severe G6PD deficiency | FDA labels §Contraindications or explicit do-not-use hemolysis language |
| VARIVAX / live varicella vaccine | Severe immunosuppression, including HIV with CD4 < 200 | FDA VARIVAX label §4.2 |
| S1P receptor modulators (ozanimod, ponesimod) | Recent MI/stroke/unstable angina or Mobitz II/third-degree AV block without pacemaker | FDA ozanimod/ponesimod labels §Contraindications |

## Drug-Drug Interactions (target ~125 verified)

### Absolutely-contraindicated pairs

| Drug A | Drug B | Consequence | Reference |
|---|---|---|---|
| MAOIs | SSRIs/SNRIs | Serotonin syndrome (potentially fatal) | FDA labels |
| MAOIs | Meperidine (Demerol) | Serotonin syndrome | FDA label |
| Warfarin | Trimethoprim-sulfamethoxazole (Bactrim) | Major INR spike, bleeding | Lexicomp Category X |
| Warfarin | Fluconazole (high-dose) | Major INR spike, bleeding | Lexicomp |
| Warfarin | Amiodarone | 30–50% warfarin dose reduction required | UpToDate |
| Statins | Fibrates (esp. gemfibrozil + statin) | Rhabdomyolysis risk | FDA label |
| Simvastatin | Amiodarone / diltiazem / verapamil | Rhabdomyolysis risk | FDA label |
| ACE inhibitor | Potassium-sparing diuretic (spironolactone) | Hyperkalemia | UpToDate |
| Digoxin | Amiodarone | Digoxin toxicity | Lexicomp |
| Nitrates | Sildenafil / tadalafil / vardenafil | Severe hypotension | FDA labels |
| Methotrexate (high-dose) | NSAIDs | Methotrexate toxicity | FDA label |
| Lithium | Thiazides / ACE inhibitors | Lithium toxicity | UpToDate |
| Clopidogrel | Omeprazole (some evidence) | Reduced antiplatelet effect | FDA labeling change |
| Rifampin | Almost anything metabolized by CYP3A4 | Loss of efficacy | UpToDate |
| Grapefruit juice | Statins / calcium channel blockers | Elevated drug levels | FDA labels |
| SSRIs | Tramadol | Serotonin syndrome | UpToDate |
| Warfarin | Direct-oral anticoagulant (concurrent) | Bleeding | Never combine |
| Aspirin | Ketorolac | Additive bleeding + GI risk | FDA label |
| Colchicine | Strong CYP3A4/P-gp inhibitor in renal or hepatic impairment | Life-threatening/fatal colchicine toxicity | FDA colchicine label §4/§7 |
| Clarithromycin | Simvastatin or lovastatin | Myopathy, including rhabdomyolysis | FDA clarithromycin label §4.5 |
| Paxlovid (nirmatrelvir/ritonavir) | Eplerenone / salmeterol / sildenafil for PAH / St. John's wort | Hyperkalemia, arrhythmia, hypotension, or loss of antiviral efficacy | FDA Paxlovid label §Contraindications |
| Praziquantel | Rifampin or other strong CYP3A inducers | Therapeutic failure from loss of praziquantel exposure | FDA praziquantel/Biltricide label §Contraindications |
| Paxlovid (nirmatrelvir/ritonavir) | Oral midazolam / triazolam / sirolimus / everolimus | Respiratory depression or severe immunosuppressant toxicity | FDA Paxlovid label §Contraindications |
| Apomorphine | 5-HT3 antagonists (ondansetron, granisetron, dolasetron, palonosetron) | Profound hypotension and loss of consciousness | FDA apomorphine/5-HT3 labels §Contraindications |
| Lurasidone | Strong CYP3A4 inhibitors or inducers | Toxicity or loss of efficacy | FDA lurasidone label §Contraindications |
| Pimozide | Strong CYP3A4 inhibitors/macrolides | QT prolongation and torsades risk | FDA pimozide label §Contraindications |

## Impossible Timing (target ~100 verified)

| Measles MMR PEP | MMR within 72 hours of exposure | MMR at day 5 for current-exposure PEP in non-high-risk adult | CDC/ACIP measles PEP |
| Varicella VariZIG PEP | within 10 days of exposure | VariZIG at day 14 | CDC VariZIG guidance |
| Postpartum RhIG | within 72 hours, possible residual benefit up to 28 days | 3 months postpartum for same delivery | ACOG Rh alloimmunization guidance |
| TXA for postpartum hemorrhage | within 3 hours of bleeding onset | 5 hours after onset with resolved bleeding | WOMAN trial / WHO PPH guidance |

| Hepatitis A post-exposure prophylaxis | <= 2 weeks from exposure | 6 weeks after exposure | CDC/ACIP HAV PEP guidance |
| Maternal GBS intrapartum antibiotic prophylaxis | Before/during delivery with placental transfer | Postpartum maternal dosing after delivery | ACOG/CDC GBS prevention guidance |
| Antithrombotics after IV alteplase | Wait at least 24 hours after thrombolysis and follow-up imaging | Therapeutic anticoagulation at 18 hours post-tPA | AHA/ASA acute ischemic stroke guidance |

### Time-sensitive interventions with rigid windows

| Intervention | Window | Wrong scenario | Reference |
|---|---|---|---|
| IV tPA (alteplase) for ischemic stroke | ≤ 4.5 hrs from symptom onset | Given at 8+ hrs | AHA/ASA stroke guidelines |
| Endovascular thrombectomy for large-vessel stroke | ≤ 24 hrs (with imaging criteria) | Given at 48+ hrs | AHA/ASA |
| Rabies PEP | Before clinical rabies symptoms | Given after hydrophobia/spasms | CDC ACIP |
| HIV PEP (nPEP) | ≤ 72 hrs from exposure | Given at 5+ days | CDC guidelines |
| Antiviral for HSV encephalitis (acyclovir) | Early in course | Delayed after neurologic damage established | UpToDate |
| Post-exposure smallpox vaccine | ≤ 4 days from exposure | Given at day 10+ | CDC |
| RhoGAM (Rh immunoglobulin) | ≤ 72 hrs from delivery/exposure | Given at 1 week | ACOG guidelines |
| Iron chelation for acute iron poisoning | Early | Delayed after multi-organ failure established | UpToDate |
| Percutaneous coronary intervention for STEMI | ≤ 90 min door-to-balloon | Delayed 6+ hrs | AHA/ACC STEMI guidelines |
| Tetanus immunoglobulin | Post-injury before immunization course | Days after wound closed | CDC |
| Levothyroxine for cretinism | Neonatal period | Started at age 5+ years | AAP guidelines |
| N-acetylcysteine for acetaminophen overdose | ≤ 8–10 hrs from ingestion | Started at 48+ hrs | UpToDate |
| Fomepizole for methanol/ethylene glycol | Early in course | Delayed after coma/death imminent | UpToDate |
| Corticosteroids for antenatal lung maturation | 24–34 wks gestation | Given at 20 wks or > 36 wks | ACOG |
| Palivizumab RSV prophylaxis | Monthly season prophylaxis for qualifying high-risk infants | Given as post-exposure prophylaxis days after a known exposure | AAP/CDC RSV immunoprophylaxis guidance |

### Vaccine timing (typical false-premise mutations)

- Live vaccine (MMR, varicella, yellow fever) given in pregnancy → wrong
- Live vaccine given to severely immunocompromised → wrong
- Rotavirus vaccine started at age 15+ months → wrong (first dose max 14 wks 6 days)
- Menactra given at age 65+ → wrong (use MPSV23 or Menveo)

## Physiological Impossibilities (target ~125 verified)
- TTP treated with prophylactic platelet transfusion despite no life-threatening bleeding [ISTH/ASH TTP guidance]
- Thyroid storm treated with beta-blocker monotherapy instead of simultaneous thionamide/iodine/steroid support [ATA thyroid storm guidance]
- Iron overdose treated with activated charcoal despite poor adsorption [AACT/EAPCCT activated charcoal position statement]
- Wrong reversal agent: heparin bleeding treated with vitamin K instead of protamine [CHEST / DailyMed]
- Wrong reversal agent: warfarin bleeding treated with protamine instead of vitamin K/PCC [CHEST / DailyMed]
- Hydroxyethyl starch resuscitation in septic shock/critical illness [FDA boxed warning / Surviving Sepsis]
- Activated charcoal for lithium overdose (lithium is not meaningfully adsorbed) [AACT/AAPCC toxicology guidance]
- Therapeutic anticoagulation immediately after acute intracerebral hemorrhage stabilization window [AHA/ASA ICH guideline]

### Endocrine
- Type 1 diabetes → oral hypoglycemics only (no insulin) [ADA Standards §9]
- DKA → oral hypoglycemics only (no insulin) [ADA]
- Adrenal crisis → steroid taper (no stress dose) [Endocrine Society]
- Hypothyroidism → no thyroid hormone (waiting to see if it resolves) [ATA]
- Central diabetes insipidus → no desmopressin (dietary restriction alone) [Endocrine Society]

### Nephrology / renal
- Anephric patient → dose adjustment as if normal renal function
- Anuric ESRD patient → loop diuretic to induce urination (won't work)
- Dialysis-dependent patient → drug with 90% renal clearance at normal dose

### Cardiology
- V-fib arrest → single beta-blocker dose without defibrillation [ACLS]
- Complete heart block → beta-blocker to "slow the rate" [ACC/AHA]
- Cardiogenic shock → beta-blocker [ACC/AHA HF guidelines]

### Hematology
- Hemophilia A bleed → platelets alone (needs Factor VIII)
- ITP → transfusion of platelets prophylactically (won't help, they're destroyed)
- Anticoagulant reversal → wrong reversal agent (warfarin → protamine instead of vitamin K/PCC)
- Hemophilia A bleed → platelet transfusion plan without factor VIII replacement [CDC hemophilia treatment: replace missing clotting factor]

### Infectious disease
- Purely viral infection → antibiotics only
- Fungal infection (candidemia) → antibiotic monotherapy (no antifungal)
- Asymptomatic candiduria in non-neutropenic, non-urologic-procedure patient → antifungal therapy [IDSA candidiasis guideline]
- Latent TB requiring treatment → BCG vaccine "to boost immunity" (not therapeutic)

### Gastroenterology
- PEG/electrolytes bowel prep in known/suspected mechanical bowel obstruction [FDA DailyMed PEG/electrolytes label]
- Complete bowel obstruction → oral bowel prep [surgery textbook]
- Fulminant C. diff colitis → oral vancomycin only, no IV metronidazole, no surgery consult

### Pulmonology
- PE with hemodynamic instability → outpatient DOAC + follow-up [CHEST/AHA]
- LABA monotherapy in persistent asthma without inhaled corticosteroid [FDA boxed warning / NHLBI-GINA asthma guidance]
- Tension pneumothorax → chest X-ray to confirm before needle decompression [ATLS]

### Pregnancy / OB
- Preeclampsia with severe features → oral labetalol at home discharge (needs IV / hospital)
- Postpartum hemorrhage → observation for spontaneous resolution

### Immunocompromise
- Neutropenic fever → outpatient oral antibiotics + wait 48hrs
- Post-splenectomy fever → outpatient antibiotic prophylaxis + reassurance

## How to use this file when writing a question

1. **Open** the seed pool JSONL file.
2. **Scan a seed** for keywords that match any pattern above (drug name, disease name, timing phrase).
3. **Pick a pattern** that fits — you'll mutate the seed to embed that pattern's impossibility.
4. **Reference:** copy the reference column into your YAML `reference:` field.
5. **Verify:** open the actual FDA label / society guideline / UpToDate page to confirm before you save.

Do not fabricate references. Every reference must be one you have actually opened.

## Batch 9 Closeout Patterns (final verified additions)

### Contraindications
- Rotavirus vaccine in an infant with prior intussusception [FDA DailyMed RotaTeq §Contraindications].
- Yellow fever vaccine in a patient with thymus disorder/history of thymectomy or thymoma [CDC/ACIP yellow fever contraindications].
- ACAM2000/vaccinia vaccine in eczema/atopic dermatitis, pregnancy, severe immunocompromise, or household severe immunocompromise [FDA DailyMed ACAM2000 label].
- Endothelin receptor antagonists or soluble guanylate cyclase stimulators in pregnancy: ambrisentan, macitentan, riociguat [FDA DailyMed boxed warnings/§Contraindications].
- Capecitabine in known complete DPD deficiency [FDA DailyMed XELODA §Contraindications/current capecitabine boxed warning].

### Drug-Drug Interactions
- Linezolid with MAOI therapy [FDA DailyMed linezolid label].
- Tolvaptan with strong CYP3A inhibitors [FDA DailyMed tolvaptan §Contraindications].
- Oral midazolam with ketoconazole/itraconazole/voriconazole-class strong CYP3A inhibition [FDA DailyMed azole/midazolam contraindication language].
- Cabenuva/rilpivirine/doravirine/Biktarvy-family antiretroviral regimens with strong enzyme inducers such as carbamazepine, phenobarbital, phenytoin, rifampin, or St. John's wort when label uses contraindicated/coadministration-prohibited language.
- Dihydroergotamine with clarithromycin or other potent CYP3A4 inhibitors [FDA DailyMed DHE/clarithromycin §Contraindications].

### Impossible Timing
- Live vaccines too close to solid-organ transplant or too early after HSCT [CDC/IDSA transplant immunization guidance].
- Neuraxial anesthesia too soon after high-dose apixaban exposure [ASRA antithrombotic neuraxial guideline].
- Postpartum hemorrhage TXA beyond 3 hours after birth [WHO PPH/TXA recommendation].
- Chemoprophylaxis for meningococcal contact after the effective exposure window has passed [CDC meningococcal guidance].

### Physiological Impossibilities
- Wrong-antidote patterns: methylene blue for CO poisoning, hyperbaric oxygen without methylene blue for methemoglobinemia, naloxone for propofol/benzodiazepine overdose, flumazenil for barbiturate overdose, cyproheptadine for anticholinergic toxicity, activated charcoal for cyanide or methanol.
- Confirmed HIT treated by continuing UFH/LMWH or starting warfarin monotherapy before platelet recovery [ASH HIT guidelines].
- Cardiac tamponade treated with anti-inflammatory therapy alone rather than drainage [cardiology/pericardial disease guidance].
- HSV encephalitis treated with antibacterial therapy instead of empiric IV acyclovir [IDSA encephalitis guidance].
