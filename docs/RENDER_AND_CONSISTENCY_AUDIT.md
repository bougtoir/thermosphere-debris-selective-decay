# Render and consistency audit (Gate 5)

Date: 2026-10-17. Rendered `manuscript/manuscript_inline.docx` -> PDF
(LibreOffice headless), 20 pages, spot-checked pages 1, 13 and table pages.

## Findings

- Title page: single author "T. Onishi", corresponding email present, no
  invented affiliation.
- Abstract numbers render correctly (6.87 m/s bound, 3.53 m/s drift-aware,
  3.98e-3 m/s fixed pulse, 1726x gap with 12x/22.5x/6.3x decomposition,
  11/27 transport survivors, ~5.8e7 W lower bound).
- Figures: 8 embedded, all legible, log axes readable, no empty/cropped
  figures; captions match content, Figure 1-8 sequential.
- Tables: 8 present, sequential, 7pt body font renders without overflow
  at this page size; "undefined" shown for non-physical ratios.
- Figure S1-S4 in supplement in citation order; 9 supplement tables render.
- No duplicate captions, no missing citation numbers, references in
  first-appearance order with DOIs.
- Consistent units and notation throughout.

## Residual

- None blocking.
