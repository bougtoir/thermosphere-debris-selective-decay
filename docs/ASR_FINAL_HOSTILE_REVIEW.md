# ASR FINAL hostile review — targeted fifth sweep (submission-relevant only)

Five skeptical-reviewer passes over the CURRENT regenerated docx
(55c65e7b…), restricted to unresolved submission-relevant flaws; prior
reviews (HOSTILE_REVIEW_INDEPENDENT/FINAL) stand and are not repeated.

## Findings
- F1 (MAJOR→FIXED): Supplementary data tables had headings but no S-
  numbering and were never cited in the main text — an ASR/Elsevier
  desk-screen risk ("every display item cited"). Now numbered Table S1–S9
  and cited at first-relevant mention (§3.2/§3.4/§3.5/§3.6/§3.7/§3.9).
- F2 (MINOR→FIXED): Markdown-italic residue `*localized*`, `*intervention*`
  rendered literally; `make all`/`delta_max` kept backticks. Now real Word
  italics / plain text.
- F3 (MINOR→FIXED): 12 substantive equations were plain ASCII (subscripts
  like v_rel, σ_h, Π, fractions). Converted to native OMML equation
  objects (editable in Word); verified rendering in the PDF.
- F4 (COSMETIC, residual): last supplementary table column wraps
  "transport_limited" mid-token at 7 pt; legible, not a defect. Kept.
- Verified claims re-checked (no regression): tracking bound stated as
  mathematical upper bound (§3.3), 41% = surveyed-grid fraction not
  probability (§3.5), extreme selectivity ratios reported undefined for
  Gaussian-tail/no-encounter denominators (§3.4/Table 4), negative result
  honestly bounded (§4/§5/§6). No new scientific issues found.
