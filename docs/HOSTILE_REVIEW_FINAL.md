# Hostile review — FINAL, post-lock pass (Gate 1 + Gate 5)

Date: 2026-10-17 (third independent sweep, on the FINAL_AUDITED revision).
Prior reports were treated as claims to challenge, not conclusions.

## New defects found by this sweep (independence evidence)

| ID | Severity | Evidence | Status |
|----|----------|----------|--------|
| F1 | MAJOR (render) | Rendered docx §3.8 contained a literal `{len(p11)}` placeholder — a non-f-string segment inside an f-string paragraph (build_manuscript.py L742). None of the prior audits caught it because they grepped *numeric* literals, not braces. | FIXED: value now injected as `n_pi_total` = 480 from phase11_scaling_fit.csv; new regression test fails on any `{...}` leftover in any of the three docx. |
| F2 | MINOR (render) | Supplement tables broke mid-word in portrait layout ("froz/en", "ero_w/ind"). | FIXED: supplement switched to landscape + 7pt table font; re-rendered and inspected. |

## Claims re-verified this sweep (not adopted from prior reports)

- Density units: `msis.py` applies ×1e3 exactly once at the g/cm3→kg/m3
  boundary; `test_atmosphere_units.py` anchors 200/400/500 km magnitudes;
  no downstream double-correction. VERIFIED.
- Propagator check: `phase2_validation.csv` fastprop_vs_cowell_250km =
  6.23e-4 → text shows 0.06% (injected). VERIFIED.
- Scaling: `phase11_scaling_fit.csv` slope=1.016, R²=0.9984,
  Pi=1.062±0.260, median 1.022, IQR 0.037, n=480, 7 low-B outliers —
  all rendered values match (formatted). VERIFIED.
- "2000-object", "~15%", "0.12*" table values, "et al." in references —
  each hit traced to an injected value or legitimate citation/substring;
  NOT defects. Documented in hardcode_findings.csv.
- 11/27 phrased as design-grid fraction, not probability. VERIFIED.
- Right-censored lifetimes excluded from statistics; n_censored injected.
- J2, Cowell comparison, corotation, Sobol S1/ST convergence — all traced
  to committed canonical CSVs; nothing changed this pass.
- Scaling collapse declared as internal-consistency check (shared drag
  equation), not independent validation — honest framing retained.
- Tracking 3.53 m/s described as idealized upper bound; no realizable-
  technology overclaim. VERIFIED.
- Author block single-author "T. Onishi"; first-person singular.

## Irreducible limitations (declared in manuscript, not defects)

MSIS climatology uncertainty (~15% declared), idealized co-location
upper bound, transport design-grid fractions, shared-equation scaling
collapse, discretized timesteps.

## DECISION

**SUBMIT.** No unresolved CRITICAL/MAJOR defect; essential
provenance/reproducibility tests pass (26/26 + make quick). The paper is
a quantitatively bounded infeasibility result — a legitimate negative
claim with declared limitations.

## Evidence-pass addendum (third sweep, after full `make all`)

- The 39-minute full rerun reproduced every phase; the only diffs are
  ulp-level FP noise and bootstrap CI resampling — plus it exposed the
  `n_outlier`/`n_outlier_gt_1p5` schema mismatch, which was fixed. No
  new scientific objection. Verdict stands: **SUBMIT**.
