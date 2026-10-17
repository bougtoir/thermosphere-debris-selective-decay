# Data-text-figure consistency audit (Gate 2/5)

Date: 2026-10-17.

## Checks performed

- Abstract/Results/Discussion/Conclusions numbers all render from `n[...]`
  injected values; perturbed-input test proves propagation.
- Figure/table numbering renumbered to citation order and verified in the
  rendered docx: main figures 1-8 sequential, tables 1-8 sequential,
  supplement figures S1-S4 in citation order (transport-grid = S1,
  MC = S2, Sobol = S3, negative controls = S4).
- Captions match figure files; the non-inline manuscript keeps figure
  placeholders + caption list per ASR separate-figure convention; the
  inline docx embeds the same figures with the same captions.
- Selectivity ratios: undefined for tail-limited/no-encounter denominators
  in both text and Table 4 (rendered "undefined").
- Censored lifetimes: `inf` cells reported as right-censored, excluded
  from statistics (n_censored injected).
- Units: kg/m^3 (NRLMSISE-00 x1e3), km, m/s, J, W, days, verified against
  test_atmosphere_units.py magnitudes.
- References: Vancouver order by first appearance via cite(); only cited
  keys emitted; DOIs from references_verified.csv.
- Supplement tables pulled from the same canonical CSVs as the text.
- Title block: single author "T. Onishi"; first person singular.

## Known residual (honest limitations, not errors)

- Pi mean is inflated by 7 low-B outliers; now reported with median/IQR.
- Transport survival fractions are design-grid fractions, not probabilities
  (already stated in text).
