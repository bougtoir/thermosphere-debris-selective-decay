# ASR FINAL QC — Gate 0 baseline (format/citation pass, no make all)

Date: 2026-10-25. Branch: devin/1792916965-asr-final-qc, based on
`devin/1790845369-reentry-flag-reset` @ 5c595d5 (which contains merged PR #5).

## Important provenance finding (not a defect of content)
- PR #5 was merged into PR #4's **feature branch**, not `main`. The canonical
  default branch `main` @ e72c646 does **not** contain the audited package.
  This QC therefore works on the PR #4 branch tip (5c595d5), which is the
  state that produced ASR_SUBMISSION_EVIDENCE_VERIFIED_FINAL.zip. See
  FINAL_HANDOFF_ASR_QC.txt — publishing requires merging PR #4 to main.

## Frozen artifact hashes (this branch)
- manuscript/manuscript.docx 5fed815e… (pre-QC) -> regenerated 55c65e7b…
- manuscript/manuscript_inline.docx 4a2d6899… -> regenerated
- supplement/supplement.docx 471f1a3c… -> regenerated de0216a2…
- submission/ASR_final_submission.zip rebuilt, 151 files, 2.74 MB
- Canonical CSVs unchanged (no pipeline rerun in this pass, per scope).

## Latest zip vs branch
ASR_SUBMISSION_EVIDENCE_VERIFIED_FINAL.zip (sha256 ac8b4591…) was verified in
the previous pass to match the branch tree; only build_manuscript.py,
build outputs (3 docx + pptx), and the new audit docs differ after this QC.
