# ASR Editorial Targeted QC (no pipeline rerun)

| Check | Result | Evidence |
|---|---|---|
| Native OMML equations (12) | PASS | document.xml count = 12 m:oMath; unchanged from pre-correction |
| No markdown residue (*, `) | PASS | regex over extracted text: 0 hits (test) |
| No char-grid line snapping | PASS | no snapToGrid in document/styles; docGrid linePitch only, no charLine |
| Times New Roman body | PASS | Normal style TNR; body 12 pt; headings TNR black |
| Captions/legends 10 pt | PASS | table + figure captions emitted with explicit 10 pt runs |
| Figures/Tables all cited, order | PASS | unchanged from ASR_FIGURE_TABLE_CITATION_ORDER_AUDIT (Fig 1–8, Table 1–8, S1–S4, S1–S9); no caption content edited |
| Frozen numeric values match CSVs | PASS | build aborts on unmapped values; no scientific CSV touched; test_numeric_provenance passes |
| Single-author voice | PASS | "I" retained; no "we/our" introduced |
| Bounded negative finding intact | PASS | abstract/conclusions text untouched |
| Reference list unnumbered + alphabetical | PASS | test_reference_list_unnumbered_alphabetical |
| In-text style consistent | PASS | all 24 instances author–year parenthetical; 0 numeric |
| Only allowed sections between Conclusions and References | PASS | "Data availability" only |
| Continuous native line numbers | PASS | lnNumType in XML; rendered margins 1→46+ continuous |
| Tests | 34/34 PASS | pytest tests/ |
| Render | PASS | manuscript 16 pp, inline 20 pp, supplement 34 pp via LibreOffice |
