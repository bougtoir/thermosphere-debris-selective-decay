# Final claim-correction and merge QC

Date: 2026-11-19 (UTC). Targeted QC after the prior-literature wording correction
(`docs/FINAL_PRIOR_LITERATURE_CLAIM_DELTA.md`) and the merge-target audit (`docs/PR_MERGE_TARGET_AUDIT.md`).

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Affected artifacts regenerated with the canonical builder | PASS | `python3 scripts/build_physical_manuscript.py`: manuscript, review copy and cover letter changed; highlights, tables, PPTX reverted to the committed versions (timestamp-only differences) |
| 2 | Principal numerical values unchanged | PASS | `results/manuscript_physical_values.csv` (164 values) byte-identical before/after; DOCX text diff = 3 manuscript paragraphs + 1 cover-letter paragraph + cover-letter word count (7260 → 7296) |
| 3 | Figure and table references | PASS | manuscript QC 34/34 (citation order, figure/table order, captions); Fig1–Fig5 TIFF and tables.docx unchanged |
| 4 | Citation integrity | PASS | 23 references, numbering in order of first appearance (QC); no reference added or removed |
| 5 | No new unsupported novelty claim | PASS | the added sentences are qualified absence statements ("a targeted literature search found no published study …"), matching `docs/PRIOR_KNOWLEDGE_MATRIX.md` rows 6 and 14; no "first" claim; grep for "Screening studies", "earlier screening", "usually screened", "Proposals to" → 0 hits in manuscript, cover letter, highlights |
| 6 | Data availability points to the public release | PASS | text unchanged: repository URL + tag `gitm-orbit-selectivity-v1`, https://doi.org/10.5281/zenodo.24101202 |
| 7 | Targeted tests and QC | PASS | `pytest -q` 34 passed; manuscript QC 34/34; `acta_semantic_checks.py` 325/325; flake8 on the builder clean |
| 8 | No new GITM simulation | PASS | no GITM process started; raw run directory not written (no new files under `~/models/runs` since 2026-11-10) |
| 9 | Published processed-data archive unchanged | PASS (by action) / re-query blocked | Devin made no Zenodo API call that writes in this step. A fresh re-query on 2026-11-19 was refused by Zenodo with HTTP 403 ("unusual traffic", IP rate limit) for the API and landing page; the DOI resolver still returns 302. Last full verification: 2026-11-18 (`docs/ZENODO_PUBLICATION_AUDIT.md`) |
| 10 | Release tag not moved | PASS | `git ls-remote` after the push: `refs/tags/gitm-orbit-selectivity-v1` = tag object `9040e4e2…` → `61478a11…` (unchanged) |
