# Submission checklist

- [x] Manuscript builds from code only: `python3 scripts/build_manuscript.py`
      (every number injected from results/tables CSVs)
- [x] Figures separate files (results/figures/*.png, 200 dpi), all cited
      in manuscript text
- [x] Supplement: supplement/supplement.docx with full tables
- [x] References: 16/16 verified (DOI resolved or institutional source);
      Vancouver numbering in order of first appearance;
      font-based superscripts (no Unicode superscripts) in docx
- [x] Synthetic data only, labeled; no operational spacecraft targeted
- [x] Reproducibility: `make quick` smoke run; `make all` full pipeline;
      deterministic seed in config; pinned requirements
- [x] QC audits: TRACEABILITY_AUDIT.md, REPRODUCIBILITY_AUDIT.md,
      CONSISTENCY_AUDIT.md — all PASS
- [x] Phase handoffs: docs/PHASE_1..13_HANDOFF.md
- [x] Gate records: GATE 1 (phase 1), GATE 2 (phase 2 validation)
- [x] Cover letter, highlights, journal audit, decision log,
      limitations (manuscript §5), reviewer-risk assessment
- [x] Final clean-environment rebuild verified: `make clean && make all
      && make quick` completed end-to-end, QC all pass
      (results/full_rebuild.log)
