# ASR FINAL data–text–figure consistency audit

- Text vs tables: all 47 spot-checked printed values appear in the rendered
  docx and match results/tables/*.csv (list in logs/ASR_FINAL_TARGETED_QC.log).
- Text vs figures: caption claims (identity-line collapse, Pareto front,
  energy bounds ~5.8e7 W) match results/tables/phase11_scaling_fit.csv,
  phase9_pareto.csv, energy_bounds_audit.csv.
- Inline vs non-inline docx: same source content, rendered twice; hashes
  recorded in the baseline doc.
- Supplement: Table S1–S9 are unmodified dumps of canonical CSVs (values
  identical by construction — the builder writes them from the same frames).
- Cover letter / highlights (03_submission_docs markdown): re-checked the
  reported numbers — 6.87, 3.53, 1726x, 41%, ~5.8e7 W — consistent with the
  manuscript. Units, rounding, signs and CIs consistent.
