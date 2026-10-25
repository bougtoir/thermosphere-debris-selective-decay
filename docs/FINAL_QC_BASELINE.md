# Final QC baseline (Gate 0, evidence pass)

Date: 2026-10-17.

- Input ZIP: `ASR_SUBMISSION_FINAL_LOCK.zip`,
  sha256 `52a198d8f64bfc8230defb0bfb90237f715f11362fe246bc17de6b8740d4dea7`
  (recorded in logs/zip_baseline.sha256).
- Git: branch `devin/1792228606-asr-hostile-hardcode-revision`,
  commit `ef02a98` (clean tree at start of this pass).
- Canonical working tree == zip contents (verified last pass: embedded
  docx sha256 matched working tree byte-for-byte; zip not rebuilt since).
- Canonical analysis outputs: `results/tables/*.csv`, `data/processed/`,
  `results/figures/` — committed, unchanged since lock.
- This pass performs no scientific modification; `make all` rerun only
  for reproduction evidence (outputs compared to canonical after run).
