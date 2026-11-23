# JSSE final QC matrix

Branch `devin/1795426935-jsse-retarget` (from `main` d6817a1 = tag `gitm-orbit-selectivity-v1.1`). All checks run in
this session (2026-11-23 UTC). No GITM run; no change to analysis code, result tables or the Zenodo record.

| Area | Check | Result | Evidence |
|---|---|---|---|
| Baseline (unmodified main) | `make physical-qc PY=python` | **34/34 PASS**; `results/manuscript_physical_values.csv` unchanged | session log (baseline before any edit) |
| Processed data | 5 NPZ re-downloaded from Zenodo 10.5281/zenodo.24101202; SHA-256 vs `PROCESSED_MANIFEST.csv`; MD5 vs Zenodo | **5/5 match** | `data/physical/zenodo_retrieval/ZENODO_RETRIEVAL_LEDGER.csv` |
| Raw data (private) | 22 release parts SHA-256 | **22/22 OK** (43,587,555,110 bytes) | `data/physical/raw_restore_20261123/RAW_RESTORE_LEDGER.json`, `PART_VERIFY.log` |
| Raw data (private) | `runs/` files vs `RAW_FILES_SHA256.txt` | **23,945 OK, 0 mismatch** | `VERIFY_RESTORE.log` |
| Raw data (private) | `GITM/` build tree vs `GITM_BUILD_TREE_SHA256.txt` | **1,587 OK, 0 mismatch** | same |
| Raw data (private) | symlinks vs `RAW_SYMLINKS.tsv` | **9,567 OK, 0 mismatch** | same |
| Physical manuscript on branch | `make physical-qc PY=python` | **34/34 PASS**; value ledger = HEAD | session log |
| Semantic code audit | `scripts/acta_semantic_checks.py` (independent recomputation of estimands) | **325/325 PASS** | `results/tables/acta_semantic_checks.csv` |
| Unit tests | `python -m pytest -q` | **34 passed** | session log |
| JSSE manuscript | `make jsse-qc PY=python` (generic 34 + JSSE-specific 57 checks) | **91/91 PASS** | `results/qc_jsse_manuscript.csv` |
| Numerical invariance | JSSE value ledger byte-identical to Acta-final ledger; 27 frozen headline values within frozen ranges | **PASS** | `results/manuscript_jsse_values.csv`; QC rows "frozen value ..." |
| Clean public reproduction | fresh `git clone` of the pushed branch from GitHub + 5 Zenodo NPZ only → `make jsse-qc` | **PASS** (91/91 on head 7fba0c6); value ledger, citation list and the text of manuscript, tables, cover letter and highlights identical to the committed build | session log |
| Figures | 5 TIFF, 600 dpi, RGB, LZW, opaque white; editable PPTX (5 slides, every figure inside the slide); main manuscript has no embedded figures; inline review copy has 5 | **PASS** | QC rows |
| Tables file | `tables.docx` carries every manuscript caption and note; horizontal rules only | **PASS** | QC rows |
| Figure regeneration | regenerated PNG/TIFF vs committed | visually identical; anti-aliasing differences only (≈ 0.3% of pixels) | session comparison |
| Citations | 34 references; order of first appearance; 1:1 with list; ISO 4 journal abbreviations; Crossref record for every DOI | **PASS** | `docs/JSSE_CITATION_ECOLOGY_AUDIT.md` |
| Claims | safety-language lexicon, negated hazard terms, "synthetic sample" qualifier on every share, no priority words, no rejection history | **PASS** | QC rows; `docs/JSSE_CLAIM_EVIDENCE_AUDIT.md` |
| Formatting (JSSE guide) | Times New Roman 12 pt body, 10 pt captions, black text, no theme fonts, no docGrid, no tracked changes, OMML equations (3), numbered sections, tables without vertical rules/shading, no hard line breaks | **PASS** | QC rows |
| Declarations | competing interest, funding, CRediT, data availability, generative-AI declaration, keywords (6), highlights (5 × ≤ 85 characters) | **PASS** | QC rows |
| Title page | author, affiliation with postal address, e-mail, ORCID | **PASS** (content to be confirmed by the author) | QC row; ORCID record shows Shiga University, Hikone |
| Fees | subscription route: no APC; no submission/page charges; colour free online | **PASS** | `docs/JSSE_JOURNAL_FIT_AND_FEES.md` |
| Journal quartile | JCR Q1 | **Not verified** (Scimago Q2; JIF 1.8) | same |
| Code style | flake8 (max line 120) on new scripts | long-line warnings only in prose strings inherited from `build_physical_manuscript.py` (which has 26 such lines) | — |

## Verdict

**CONDITIONAL SUBMIT** — scientific content, data statement, reproducibility and files are complete; the remaining
items are author/administrative: confirm title-page metadata (name order, address romanisation), upload Elsevier's
competing-interest template, choose the subscription route and online-only colour at acceptance, and decide whether the
non-Q1 status (Scimago Q2) is acceptable for this submission.
