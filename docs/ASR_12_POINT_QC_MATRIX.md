# ASR 12-point QC matrix (format/citation pass, no make all)

| # | Item | Status | Evidence | Corrections |
|---|------|--------|----------|-------------|
| 1 | Hostile review | PASS | ASR_FINAL_HOSTILE_REVIEW.md (F1–F4) | S-numbering+italics+OMML fixes |
| 2 | No scientific-result hardcoding | PASS | ASR_FINAL_HARDCODE_AUDIT.md; 26 tests | none needed |
| 3 | Public code reproducibility | NOT RERUN IN THIS TASK — prior evidence only | logs/make_all.log (39m, prior pass) | — |
| 4 | All references real | PASS | references/ASR_REFERENCE_QC.csv (17/17) | none |
| 5 | Every reference cited | PASS | citation-order script: 17/17 in text | none |
| 6 | Every figure/table cited | PASS | ASR_FIGURE_TABLE_CITATION_ORDER_AUDIT.md | Tables S1–S9 numbered+cited |
| 7 | Numeric consistency text/figs/tables | PASS | ASR_FINAL_DATA_TEXT_FIGURE_AUDIT.md (47-literal check) | none |
| 8 | Fig/table numbering = first appearance | PASS | same audit; 1–8 + S1–S9 sequential | S-numbering added |
| 9 | Refs numbered by first appearance | PASS | script: order == numbering for 1–17 | none |
| 10 | Word-native OMML equations | PASS | ASR_OMML_AUDIT.md; 12 oMath objects | 12 ASCII equations converted |
| 11 | No stray formatting asterisks | PASS | ASR_ASTERISK_AUDIT.md; 0 residues | 2 italics +1 equation fixed |
| 12 | No character-grid line spacing | PASS | ASR_LINE_SPACING_AUDIT.md; default docGrid only | none |

Verdict: SUBMIT. Residual risks: cosmetic column wrap in one supplementary
table; reproducibility item relies on the prior pass's make-all evidence by
scope decision.
