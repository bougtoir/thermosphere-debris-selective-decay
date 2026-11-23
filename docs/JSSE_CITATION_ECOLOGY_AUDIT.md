# JSSE citation ecology audit

Scope: every reference in `manuscript/JSSE/manuscript.docx` (34 references, numbered in order of first citation; list
in `results/manuscript_jsse_citations.csv`). No systematic review was attempted (master prompt §12).

## Method

1. **Existence and metadata.** Every DOI resolves to an archived Crossref record in `data/physical/raw/crossref/`
   (authors, title, container, volume, pages, year); the reference list is rendered from these records by
   `scripts/build_jsse_manuscript.py`, not typed by hand. 23 references carry over from the Acta-final manuscript,
   whose 38-paper prior-knowledge audit is in `references/PRIOR_KNOWLEDGE_VERIFIED.csv`.
2. **Relevance of added references.** For the 11 references added for the space-safety framing
   (`references/JSSE_ADDED_REFERENCES.csv`), the publisher landing page was opened through the session browser and its
   text archived in `data/raw/citations/jsse_added/` (URL, UTC time, SHA-256 in `LEDGER.jsonl`). The abstract or
   highlights were read to confirm that the sentence citing the paper is supported. Two landing pages (AGU/Wiley for
   Kessler and Cour-Palais 1978; Science for Liou and Johnson 2006) returned HTTP 403; these are canonical,
   widely-cited papers and the citing statements (collisional cascade; growth of the LEO population and the need for
   remediation) match their established content, but full text was not re-read in this session.
3. **Order and formatting.** Numbered in order of first appearance; journal names abbreviated (ISSN LTWA) as the JSSE
   guide requires; every reference cited and every citation listed (QC `results/qc_jsse_manuscript.csv`).

## Added references and the statement each supports

| Key | Supports | Evidence read |
|---|---|---|
| kessler1978debrisbelt | collisions can sustain debris growth (Intro ¶1) | Crossref metadata; landing page 403 |
| liou2006risks | same; need for remediation (Intro ¶1) | Crossref metadata; landing page 403 |
| lewis2020population (JSSE) | long-term population growth under mitigation (Intro ¶1) | abstract: linear vs exponential growth under IADC guidelines |
| bonnal2013adr, shan2016adrreview, svotina2024removal (JSSE) | object-directed remediation methods (Intro ¶1) | abstracts/highlights: ADR reviews (capture, docking, harpoons, manipulators) |
| mcknight2016remediation (JSSE) | remediation judged by operational outcome (Intro ¶2) | abstract: debris risk management in an "operational success" framework |
| usovik2023mitigation (JSSE) | need to assess the environmental effect of mitigation/remediation measures (Intro ¶2) | abstract: "necessary to assess impact of various measures ... on space debris environment" |
| vallado2014dragassessment | density/drag uncertainty propagates into orbit prediction (Intro ¶2; §4.4) | highlights: "practical issues and their effect on propagation and orbit estimation" |
| gulde2016risk (JSSE), braun2020drama (JSSE) | examples of debris-risk assessment tools **not** applied here (§4.4) | abstracts: component-level failure-risk method; ESA DRAMA compliance tool suite |

Removed after review: `vallado2008drag` (conference version of vallado2014dragassessment; citing both was
redundant). Not used: Klinkrad 2017 (JSSE 2-page editorial; no specific support needed).

## Checks against citation-ecology failure modes

* **No fabricated comparator literature.** The manuscript states that a targeted search found no published
  selective-debris-decay study using static Gaussian patches, and calls the patch an idealized comparator "not ... a
  representation of prior work". No reference is cited as an example of static-patch practice.
* **No citation padding for the venue.** Six JSSE papers are cited, each for a specific statement; none is cited only to
  signal venue fit. JSSE papers on topics not used by the argument (space traffic management, insurance, ontology)
  were found in the Crossref search but not cited.
* **Physics citations preserved.** All thermosphere, GITM, driver and drag citations of the Acta-final version that are
  still cited in the text are retained unchanged.
* **Self-citation:** none.
* **Known metadata limitations (inherited from Crossref, unchanged from the Acta-final list):** Rubenchik et al. 2010
  (AIP Conf. Proc.) lacks a volume number in Crossref; Qian et al. 2014 is a book chapter rendered in journal style;
  Liou's given name renders as "J.C." (Crossref) rather than "J.-C.". These can be corrected at proof stage.

## Full reference table

| # | Key | Origin | First cited (section) | DOI | Crossref record | Landing page (added refs) | Role |
|---|---|---|---|---|---|---|---|
| 1 | kessler1978debrisbelt | added for JSSE | 1 | 10.1029/JA083iA06p02637 | yes | 403 | debris-environment risk: collisional cascade |
| 2 | liou2006risks | added for JSSE | 1 | 10.1126/science.1121337 | yes | 403 | debris-environment risk; need for remediation |
| 3 | lewis2020population | added for JSSE | 1 | 10.1016/j.jsse.2020.06.006 | yes | 200 | JSSE: debris population dynamics |
| 4 | bonnal2013adr | added for JSSE | 1 | 10.1016/j.actaastro.2012.11.009 | yes | 200 | ADR review: object-directed methods |
| 5 | shan2016adrreview | added for JSSE | 1 | 10.1016/j.paerosci.2015.11.001 | yes | 200 | ADR review: object-directed methods |
| 6 | svotina2024removal | added for JSSE | 1 | 10.1016/j.jsse.2024.04.002 | yes | 200 | JSSE: removal technology review |
| 7 | serfontein2021dragaug | Acta-final (38-paper audit) | 1 | 10.1016/j.actaastro.2021.05.038 | yes | — | passive drag augmentation predecessor |
| 8 | rhatigan2020deorbit | Acta-final (38-paper audit) | 1 | 10.1016/j.jsse.2020.07.026 | yes | — | as above |
| 9 | schall1991laser | Acta-final (38-paper audit) | 1 | 10.1016/0094-5765(91)90184-7 | yes | — | non-contact removal predecessor |
| 10 | rubenchik2010laser | Acta-final (38-paper audit) | 1 | 10.1063/1.3507120 | yes | — | as above |
| 11 | smith2020ionodrag | Acta-final (38-paper audit) | 1 | 10.1016/j.actaastro.2020.07.007 | yes | — | environment-mediated drag predecessor |
| 12 | mcknight2016remediation | added for JSSE | 1 | 10.1016/S2468-8967(16)30022-2 | yes | 200 | JSSE: evaluating remediation by operational outcome |
| 13 | usovik2023mitigation | added for JSSE | 1 | 10.1016/j.jsse.2022.12.001 | yes | 200 | JSSE: mitigation solutions review |
| 14 | vallado2014dragassessment | added for JSSE | 1 | 10.1016/j.actaastro.2013.10.005 | yes | 200 | drag/density modelling uncertainty for orbit prediction |
| 15 | bruinsma2006storm | Acta-final (38-paper audit) | 1 | 10.1029/2005ja011284 | yes | — | scale of natural density anomalies (cited by baseline) |
| 16 | sutton2009rapid | Acta-final (38-paper audit) | 1 | 10.1029/2008ja013667 | yes | — | prior for PR3/PR5 |
| 17 | emmert2015review | Acta-final (38-paper audit) | 1 | 10.1016/j.asr.2015.05.038 | yes | — | background (cited by baseline) |
| 18 | luhr2004cusp | Acta-final (38-paper audit) | 1 | 10.1029/2003gl019314 | yes | — | natural localized density anomalies of order delta~1 exist; prior for  |
| 19 | crowley2010cusp | Acta-final (38-paper audit) | 1 | 10.1029/2009gl042143 | yes | — | physics model reproduces localized anomaly |
| 20 | carlson2012cusp | Acta-final (38-paper audit) | 1 | 10.1029/2012gl053034 | yes | — | natural localized delta~1 at 400 km |
| 21 | deng2008nonhydro | Acta-final (38-paper audit) | 1 | 10.1029/2007gl032182 | yes | — | establishes that localized strong heating needs a non-hydrostatic solv |
| 22 | gardner2010tad | Acta-final (38-paper audit) | 1 | 10.1029/2009ja015129 | yes | — | transport of localized energy; prior for PR5 |
| 23 | liu2015substorm | Acta-final (38-paper audit) | 1 | 10.1002/2014ja020962 | yes | — | closest physical predecessor; prior for PR1-PR3 |
| 24 | oliveira2019drag | Acta-final (38-paper audit) | 1 | 10.1029/2019sw002287 | yes | — | established storm->drag->decay link |
| 25 | fang2022starlink | Acta-final (38-paper audit) | 1 | 10.1029/2022sw003193 | yes | — | established coupled chain energy->density->drag->reentry for natural s |
| 26 | baruah2024starlink | Acta-final (38-paper audit) | 1 | 10.1029/2023sw003716 | yes | — | as above |
| 27 | ridley2006gitm | Acta-final (38-paper audit) | 1 | 10.1016/j.jastp.2006.01.008 | yes | — | selected model |
| 28 | weimer2005 | Acta-final (38-paper audit) | 2.1 | 10.1029/2004ja010884 | yes | — | model driver |
| 29 | picone2002msis | Acta-final (38-paper audit) | 2.1 | 10.1029/2002ja009430 | yes | — | empirical control |
| 30 | gulde2016risk | added for JSSE | 4.4 | 10.1016/S2468-8967(17)30003-4 | yes | 200 | JSSE: satellite debris risk assessment (not used here) |
| 31 | braun2020drama | added for JSSE | 4.4 | 10.1016/j.jsse.2020.07.020 | yes | 200 | JSSE: collision-risk assessment tools (not used here) |
| 32 | richmond1992tiegcm | Acta-final (38-paper audit) | 4.5 | 10.1029/92gl00401 | yes | — | surveyed model |
| 33 | qian2014tiegcm | Acta-final (38-paper audit) | 4.5 | 10.1002/9781118704417.ch7 | yes | — | surveyed model |
| 34 | liu2018waccmx | Acta-final (38-paper audit) | 4.5 | 10.1002/2017ms001232 | yes | — | surveyed model |
