# Final render + regression QC (targeted, no pipeline rerun)

- python3 scripts/build_manuscript.py -> exit 0; 3 docx + pptx regenerated.
- pytest tests/ -x -q -> 26/26 PASS (incl. provenance, fail-loud,
  placeholder and perturbation-propagation tests).
- LibreOffice render: manuscript 14 pp, inline 20 pp, supplement 34 pp;
  page images checked at pp 1,2,5,9,10 — equations, italics, tables,
  captions, page breaks all clean; no clipped lines or overlaps.
- Scientific values unchanged (formatting-only diff verified by the
  provenance tests + 47-literal spot check).
- XML integrity: all docx reopen via python-docx; oMath objects well-formed.
- Residual cosmetic: one supplementary table column wraps "transport_
  limited" mid-token; legible, accepted.
