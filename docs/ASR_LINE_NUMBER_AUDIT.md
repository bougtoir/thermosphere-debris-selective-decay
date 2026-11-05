# ASR Continuous Line-Number Audit

- Implemented natively: `<w:lnNumType w:countBy="1" w:start="0" w:distance="240" w:restart="continuous"/>` inserted into w:sectPr before w:cols (schema-correct position) in scripts/build_manuscript.py `_add_line_numbers`, applied to every section of both manuscript.docx and manuscript_inline.docx.
- Not applied to supplement/supplement.docx (editorial request scoped to manuscript text).
- Margin placement (distance 240 twips ≈ 0.42 cm from text edge); numbers are layout artifacts, not paragraph text — they do not alter captions, equations or editable content.
- XML verification: lnNumType present exactly once per document sectPr, single section each.
- Render verification (LibreOffice→PDF): page 1 margin shows 1–32, page 2 continues 33–46 — continuous across the page boundary, no reset.
- Regression test: tests/test_editorial_format.py::test_continuous_line_numbering.
