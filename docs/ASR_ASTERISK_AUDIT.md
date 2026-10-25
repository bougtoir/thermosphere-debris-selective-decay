# Asterisk / markdown-residue audit

Scan of every w:t run + headers/footers in all three docx (before/after).

Before: 3 runs containing '*'
- "*localized*" (§1) — markdown-italic residue -> FIXED: real italics.
- "*intervention*" (§3.4) — markdown-italic residue -> FIXED: real italics.
- "rho*delta*v_rel^2*T/(2B)" (Fig 5 caption) — genuine multiplication,
  now a native OMML equation (no literal asterisk remains).
Also stripped markdown backticks around `make all`, `make quick`,
`delta_max` (now plain text).

After: 0 runs containing '*' or '`' in all three docx (document.xml,
headers, footers). Legitimate-asterisk count: 0 required — no significance
stars, wildcard syntax or footnote symbols are used in this manuscript.
Note: the editable PPTX deck keeps ASCII math text by design (a slide deck,
not the submitted manuscript); not a defect.
