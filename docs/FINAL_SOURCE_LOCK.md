# Final source lock (Gate 0)

Date: 2026-10-17 (second pass).

## Revision identity

- Git: branch `devin/1792228606-asr-hostile-hardcode-revision`,
  base commit `0ece949` (hostile-review/hardcode-audit revision)
  on top of PR #4 head `d2d2b12`.
- Input ZIP: `ASR_submission_FINAL_AUDITED.zip` (130 files, 2.7 MB).
  Verified same-revision: `01_manuscript/manuscript.docx` inside the zip
  sha256 = `74dab026…` = working-tree `manuscript/manuscript.docx`.
  No cross-revision mixing.
- Working tree clean except the remediation of this pass.

## Key file hashes (sha256, first 16)

- manuscript/manuscript.docx        74dab026db6baaa5
- manuscript/manuscript_inline.docx 72e4af41650bc760
- supplement/supplement.docx        4673688a52cbf619

(Hashes of the regenerated artifacts are recorded in
FINAL_HANDOFF.txt after this pass's rebuild.)

## Prior validated state preserved

All canonical `results/tables/*.csv` and `data/` are unchanged; the only
reanalysis ever needed was `phase11_scaling.py` (previous pass). The
original AUDITED zip is kept in place untouched.
