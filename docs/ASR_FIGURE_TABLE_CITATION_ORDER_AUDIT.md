# Figure/table coverage and citation order audit

Programmatic scan of the regenerated docx:

- Main Figures 1–8: first appearances in text order 1,2,3,4,5,6,7,8.
  Every figure is cited (parenthetical "(Fig. n)" + "[Figure n near here]"
  placeholder), every citation resolves.
- Main Tables 1–8: first-appearance order 1,2,3,4,5,6,7,8; all cited.
- Supplementary Figures S1–S4: all cited (Fig. S1 §3.5, S2–S3 §3.6, S4 §3.7);
  supplement numbering internally consistent with figS*.png files.
- Supplementary Tables: FIXED — now Table S1–S9 in first-citation order
  (S1 §3.2, S2 §3.4, S3+S4 §3.5, S5 §3.6, S6 §3.7, S7–S9 §3.9), headings
  carry the numbers, all cited. Previously unnumbered/uncited.
- No gaps, inversions, duplicates or main/supplement numbering confusion.
- Captions/legends numeric claims verified against canonical CSVs (see
  DATA_TEXT_FIGURE audit). Rendered PDFs: no caption/data overlap, figures
  legible at 6.0 in width (checked pages 1,2,5,9,10).
