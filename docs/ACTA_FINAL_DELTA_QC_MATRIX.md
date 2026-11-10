# Acta final delta — QC matrix (Gate 14)

Baseline: `23add38`. Code/results commit of the delta: `8aa5205` (branch `devin/1794047620-physical-model-rebuild`,
PR #9). Only affected artifacts were regenerated (`make physical-qc` = bootstrap + figures + manuscript + QC); no
GITM run, no `make all`.

| # | Gate / item | Check | Evidence | Result |
|---|---|---|---|---|
| 1 | Baseline | HEAD, SHA-256 of all deliverables, source map, prior QC | `docs/ACTA_FINAL_DELTA_BASELINE.md` | PASS |
| 2 | Fig. 1 saturation | Range vs colour limits; exact 400 km | `physical_fig1_panel_ranges.csv`: max 1.94 < 2.0, min −0.030 > −0.05, 0 cells out of range | PASS (caption: no saturation) |
| 3 | Fig. 3 300 km interval | Rule from definition, no tuned threshold | `physical_fig3_illconditioned_interval.csv`: 30 min | PASS |
| 4 | Fig. 5 discrete | Markers at 3 altitudes, guides labelled | figure + caption | PASS |
| 5 | Fig. 2/4 | Units, area weighting, native/remapped, 18 comparator cells vs CSV | semantic checks #3, #4, #8 | PASS |
| 6 | Claim calibration | No single-mechanism attribution; no "bounds"/"maximises"/"robust to resolution" | `docs/ACTA_CLAIM_CALIBRATION_AUDIT.md` (16 edits) | PASS |
| 7 | Preregistration wording | No `pre-?regist` in any DOCX; chronology with commit c93bf8c | QC check; audit §2 | PASS |
| 8 | Data availability | Statement truthful; minimal dataset deposited (draft); SHA-256/MD5 match | `docs/ACTA_DATA_AVAILABILITY_AUDIT.md` | PASS for statement; **OPEN**: record unpublished |
| 8b | Public reproduction | Fresh clone: fails without NPZ; byte-identical outputs with NPZ | `docs/ACTA_PUBLIC_REPRODUCTION_CHECK.md` | PASS (with NPZ); simulation not re-run |
| 9 | Cover letter | First person, no ASR paragraph, limitations, no invented facts | QC check "no ASR rejection paragraph"; rendered PDF read | PASS |
| 10 | Format | TNR styles, 12 pt body, 10 pt captions, black, no theme fonts, no docGrid, ≥ 2 OMML equations, no tracked changes/comments, single author placeholder | `results/qc_physical_manuscript.csv` (34/34 PASS) | PASS |
| 10b | Rendering | LibreOffice PDF: 21 pages, no tofu/replacement glyphs, equations render | `pdffonts`: Liberation Serif substituted for Times New Roman (not installed on the VM); Word on the author's machine will use TNR | PASS with noted substitution |
| 10c | References | 23 numbered, cited in order, all DOIs Crossref-verified earlier; figure/table order | QC checks | PASS |
| 11 | TIFF | 600 dpi, RGB, LZW, sizes, SHA-256 | `docs/ACTA_FIGURE_EXPORT_AUDIT.md` | PASS |
| 12 | Semantic | 325 independent checks | `results/tables/acta_semantic_checks.csv` | PASS (one derived value corrected: 1.3% → 1.1%) |
| 13 | Hostile review | 5 perspectives | `docs/ACTA_FINAL_HOSTILE_REVIEW.md` | No invalidating defect; 1 blocking item (archive) |
| 14 | Tests / lint | `pytest -q` 34 passed; flake8 clean on changed scripts | console | PASS |
| 15 | Canonical results unchanged | `git diff 23add38 HEAD` on `results/tables/physical_*` (pre-existing), `physical_model_vs_prescribed_patch.csv`, processed NPZ, manifests | no change; `manuscript_physical_values.csv` only gains 8 new rows, no existing row altered | PASS |
| 16 | Raw data preserved | `/home/ubuntu/models/runs` untouched; manifests unchanged | — | PASS |

Corrections in this delta (all display/derivation, none to canonical numbers): Fig. 1 altitude (390.6 → 400 km) and
neutral-bin colour; Fig. 3 interval marking; Fig. 5 line semantics; coarse/fine difference computed from unrounded S
(1.3% → 1.1%); raw-output size in prose (30 → 54 GB, from manifest); data statement; title and causal wording.
