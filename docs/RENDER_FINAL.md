# Final render verification (Gate 4)

Date: 2026-10-17. LibreOffice headless renders:

- `manuscript.docx` -> 14 pages: title block, abstract, 8 tables all
  bounded, captions sequential, references in order. Checked pages 1, 7.
- `manuscript_inline.docx` -> 20 pages: 8 embedded figures legible,
  log axes readable, Figure 1-8 order confirmed.
- `supplement.docx` -> 34 pages after landscape + 7pt font fix;
  previously mid-word-wrapped table columns now render cleanly.

## Defects fixed at render stage

- `{len(p11)}` literal placeholder in §3.8 (both manuscript docx).
- Supplement portrait table overflow/mid-word wrap.

## Verified

- No unsubstituted `{...}` in any docx (regression test).
- Citation order sequential (Vancouver); figure/table citations 1-8 + S1-S4.
- No stale literals in rendered text (grep sweep + injected-value spot checks).
