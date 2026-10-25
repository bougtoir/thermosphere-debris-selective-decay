# Line spacing / character-grid audit

OOXML inspection of all three docx:
- w:docGrid present in sectPr as `<w:docGrid w:linePitch="360"/>` — the
  DEFAULT (no character grid) spec; no type="lines"/"linesAndChars" grid is
  enabled. No w:snapToGrid="1|true" anywhere in document.xml or styles.xml.
- Line spacing is paragraph-line-based: Normal style w:line="276"
  w:lineRule="auto" (≈1.15 spacing) with w:after=200; headings use
  line=240/before=480. No character-count-based line advance.
- After the rebuild, rendered pages checked (no clipped lines, no
  overlaps). Nothing to disable: PASS, no changes required.
