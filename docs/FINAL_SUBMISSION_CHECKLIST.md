# Final ASR submission checklist (post-revision)

Supersedes `SUBMISSION_CHECKLIST.md`, which records the pre-revision state.
Every box is checked against a generated artefact in this tree, not against
prose.

## Journal fit and policy

- [x] Scope: space debris, thermosphere / reference atmospheres, space
      weather - all within Advances in Space Research scope
      (`docs/JOURNAL_AUDIT.md`)
- [x] Single-anonymized review assumed; no author-identifying content in the
      manuscript body
- [x] Structure: title, authors, abstract, keywords, main text, figure
      captions, tables, references, supplementary material
- [x] Abstract concise and factual; no feasibility or capability claim
- [x] Highlights provided (`docs/HIGHLIGHTS.md`)
- [x] Cover letter provided (`docs/COVER_LETTER.md`)
- [x] Declarations: competing interests, funding, generative-AI use, ethics
      and dual-use, authorship, CRediT (`docs/DECLARATIONS.md`)
- [x] Data and code availability statement with public repository URL
      (`docs/DATA_CODE_AVAILABILITY.md`)

## Manuscript integrity

- [x] Manuscript generated only by `scripts/build_manuscript.py`; no
      hand-edited numbers
- [x] Every injected numeric value maps to a generated results CSV; the build
      fails on any unmapped value (`results/manuscript_value_provenance.csv`,
      68 values)
- [x] Every citation resolves to the verified ledger and is numbered in order
      of first appearance (`results/manuscript_citations.csv`,
      `references/references_verified.csv`, 18 verified records)
- [x] Font-based superscripts in the DOCX (no Unicode superscript glyphs)
- [x] All figures (1-8) and supplementary figures (S1-S4) cited in the text
- [x] All tables cited in the text
- [x] Figures submitted as separate files at 200 dpi; an inline-figure
      reading copy and an editable English deck are provided in addition
      (`manuscript/manuscript.docx`, `manuscript_inline.docx`,
      `manuscript_figures.pptx`)
- [x] Supplement provided (`supplement/supplement.docx`)

## Scientific claims

- [x] Idealized tracking configuration labelled a mathematical upper bound in
      abstract, methods, results, discussion, limitations and conclusions
- [x] Fixed-pulse / tracking gap decomposed into duration, occupancy and
      amplitude factors with the closure error reported
- [x] Absolute target benefit and absolute protected-object collateral lead
      the reporting; selectivity ratios are secondary diagnostics
- [x] Every selectivity ratio carries an exposure classification and is
      flagged meaningful only for physically exposed protected objects
- [x] Finite-horizon lifetimes reported as right-censored lower bounds
- [x] Transport result stated as "41% of surveyed parameter combinations"
      (11 of 27) with grid-choice sensitivity (8.3%-55.6%) and an explicit
      statement that no distribution was assumed
- [x] Matching-convention dependence stated; three conventions reported
- [x] Energy values labelled strict thermodynamic lower bounds (in-situ and
      column-expansion); no delivered engineering energy claimed
- [x] Pi collapse described as internal consistency / dimensional reduction,
      not independent validation
- [x] Sensitivity indices reported as computed, with CIs, never clipped
- [x] All mandatory negative controls reported, including the co-orbital twin

## Reproducibility

- [x] Deterministic seed in `config/default.yaml`; pinned `requirements.txt`
      and `environment.yml`
- [x] `make clean && make all && make quick` completed end-to-end from a
      clean tree (`results/full_rebuild.log`, exit 0; QC all pass per
      `docs/REPRODUCIBILITY_AUDIT.md` and `docs/TRACEABILITY_AUDIT.md`)
- [x] Test suite passes (`make test`)
- [x] Atmosphere magnitude regression tests guard the density units
      (`tests/test_atmosphere_units.py`)
- [x] No absolute paths, credential-like strings or hidden local files in
      tracked outputs (`scripts/qc_traceability.py`)
- [x] Pre-revision state preserved and documented (tag
      `pre-revision-checkpoint`, `docs/PRE_REVISION_STATE.md`)

## Review record

- [x] Pre-revision hostile review (`docs/HOSTILE_REVIEW_PRE.md`)
- [x] Post-revision hostile review with zero open CRITICAL and no actionable
      open MAJOR (`docs/HOSTILE_REVIEW_POST.md`)
- [x] Reanalysis plan (`docs/REANALYSIS_PLAN.md`)
- [x] Decision log for the revision (`docs/FINAL_DECISION_LOG.md`)
- [x] Audits: Sobol', numerical-zero/exposure, transport boundary, scaling
      law, traceability, reproducibility

## Package

- [x] `submission/ASR_final_submission.zip` built by
      `scripts/build_submission_package.py`, which exits non-zero if any
      required input is missing
- [x] ZIP contains manuscript, separate figures, tables, supplement, cover
      letter, highlights, declarations, data/code availability, verified
      references, audits, reproducibility bundle, README and a SHA-256
      manifest
- [x] ZIP excludes caches, credentials, secrets, virtual environments and
      irrelevant binaries
