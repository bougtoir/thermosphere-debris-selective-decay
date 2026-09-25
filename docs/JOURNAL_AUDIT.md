# Journal audit

Decision recorded after the results existed (Phase 13), per protocol.
Re-verified against the live ASR Guide for Authors during the final
revision (Phase 13 of the revision plan).

## Candidate venues considered

| Venue | Fit | Verdict |
|---|---|---|
| Advances in Space Research | Publishes modelling/feasibility studies of the space environment, thermospheric density, debris. Emmert 2015 (our key density review) is ASR. Broad readership for boundary/negative results. | **Selected** |
| Acta Astronautica | Strong ADR/mission-concept venue, but the paper is deliberately *not* a mission concept; ASR is a better tonal fit. | Backup |
| Journal of Spacecraft and Rockets | Drag/dynamics focus; possible, but the thermosphere-transport emphasis fits ASR better. | Backup |
| Journal of Geophysical Research (Space Physics) | Would demand fuller atmospheric-transport physics than this boundary study provides. | Rejected |

## Scope verification (authoritative sources)

Verified from the ASR journal pages on ScienceDirect (aims and scope,
guide for authors) and the Elsevier ASR author guide PDF:

- ASR is the official COSPAR journal and explicitly lists "upper
  atmospheres ... including reference atmospheres", "space debris" and
  "space weather" within scope. All three are central to this
  manuscript, so the scope match is direct rather than argued.
- Peer review is single anonymized; two reviewers minimum.
- Life-science manuscripts are out of scope (not applicable here).

Sources consulted (accessed 2026-09-24 UTC):

- `https://www.sciencedirect.com/journal/advances-in-space-research/publish/guide-for-authors`
- `https://www.sciencedirect.com/journal/advances-in-space-research/about/aims-and-scope`
- `https://legacyfileshare.elsevier.com/promis_misc/JASRGuideforAuthorsDec2016.pdf`
  (ASR-specific submission instructions, Editorial Manager workflow)

## Fit statement

The manuscript is a quantitative feasibility/boundary study. Its
contribution is an exclusion map with sharp quantitative edges: it
separates drag response (which is not limiting), exposure geometry,
transport persistence, collateral selectivity and thermodynamic
energy lower bounds into four independent gates and locates the
boundary of each. The novelty claimed is *not* "more density means
more drag" (elementary) and *not* a deployable technology; it is the
quantified boundary between where selective drag could work in
principle and where orbital geometry, atmospheric transport,
energetics or collateral effects close it.

## Positioning against existing literature

| Existing line of work | Relation to this manuscript |
|---|---|
| Storm-time density enhancement and satellite drag (Bruinsma 2006; Emmert 2015; Berger 2023; Parker & Linares 2024, Gannon storm) | These document the *uniform* control realized by nature: global delta of order unity to several, with measurable operational consequences. We use them to justify the delta range and to argue that the achievable natural analogue is global, not selective. |
| Traveling atmospheric disturbances (Bruinsma & Forbes 2007) | Observational evidence that localized thermospheric disturbances propagate at 460-730 m/s rather than remaining in place. Directly constrains our transport gate. |
| Thermospheric winds (Drob et al. 2015, HWM14) | Observational magnitudes for the advection/flushing survey (tens to >100 m/s). |
| Thermospheric energy budget (Knipp et al. 2004) | Provides the comparator (~464 GW solar, ~95 GW Joule globally) for our thermodynamic lower bound on a single patch. |
| Differential drag / drag augmentation devices | Achieve selective decay by changing the ballistic coefficient of the object rather than the density of the atmosphere. Section 3.4 and 4.5 make the comparison explicit: the B-side requires no sustained energy input and is intrinsically co-located. |
| Active debris removal, laser and ion-beam shepherd concepts (Shan 2016; Phipps 2012; Liou & Johnson 2006; IADC 2021) | Contact and non-contact removal baselines against which an atmospheric-side concept must be judged. |

No prior study we located quantifies the *joint* boundary set by
exposure geometry, transport persistence and collateral selectivity
for a localized density perturbation, nor supplies the dimensionless
group that lets the boundary be re-evaluated for arbitrary parameter
choices. That gap is the stated contribution.

## Compliance notes

- Manuscript file: title, authors, affiliation/corresponding contact,
  abstract, keywords, body, references. Two renderings are produced:
  `manuscript.docx` (figure placeholders, figures submitted
  separately) and `manuscript_inline.docx` (figures and tables placed
  in the text, per the ASR instruction to prepare one manuscript file
  with figures and tables inside).
- Abstract: single paragraph, factual, states purpose, principal
  results and major conclusions. Supplied as a separate file for the
  Editorial Manager copy-paste step.
- Highlights: optional but recommended; provided as a separate file,
  short sentences with the core results (`docs/HIGHLIGHTS.md`).
- Figures: separate 200 dpi PNG files under `results/figures/`,
  regenerable via `make figures`, each cited in the text.
- Supplementary material: `supplement.docx` with the full result
  tables and supplementary figures.
- References: verified (DOI resolved or institutional source),
  Vancouver numbering in order of appearance; ledger in
  `references/references_verified.csv`.
- Declarations: competing interests, funding, generative-AI use and
  data/code availability statements are provided in
  `docs/DECLARATIONS.md` and included in the submission package.
- No named operational spacecraft are targeted; synthetic objects only
  - stated in Methods and Limitations (dual-use mitigation).
