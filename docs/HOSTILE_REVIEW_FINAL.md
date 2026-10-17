# Hostile review — round 2, post-revision (Gate 7)

Date: 2026-10-17. Re-audit of the revised manuscript as an independent
ASR reviewer team. Precondition: assume nothing from round 1 is fixed.

## Attempted falsifications

| # | Attack | Result |
|---|--------|--------|
| R1 | Find any text number not traceable to a current file | None: 84/84 claims mapped in numeric_claim_traceability.csv; build aborts on missing keys |
| R2 | Show a stale number survived | Greps for old literals ("0.12", "0.9995", "et al.", "2000-object", "~15%", "six patch") -> all injected now; regression tests guard two of them |
| R3 | Perturb a canonical CSV, check text changes | test_numeric_provenance perturbs phase6 x1.5 -> rendered text changes accordingly |
| R4 | Unit error in density (x1000) | conversion at single boundary point; magnitude tests anchor values; reported as kg/m^3 consistently |
| R5 | Inf lifetimes smuggled into statistics | n_censored injected; text excludes censored cells |
| R6 | Numbering / citation-order violation | figures 1-8, tables 1-8, S1-S4 sequential in rendered docx |
| R7 | Overclaim: concept "impossible" | conclusion is bounded: excluded at all simulated amplitudes/spacetimes, mathematically open only in narrow corner — unchanged, still a defensible negative bound |
| R8 | Selectivity ~117 at 400 km hiding a viable corner | Pareto text already states high selectivity only when target gain itself is tiny; n_target_floor makes this explicit |
| R9 | Pi collapse is tautology | Pi outliers (7/480, low B) now reported, median/IQR shown; factor-2 in formula fixed |
| R10 | Single-author formatting | "T. Onishi" alone, first-person singular, no et al. |

## Reviewer verdicts

- Reviewer A (thermosphere): no new objection; unit path verified.
- Reviewer B (dynamics): tracking/impulse values consistent; wording fix for 750 km accepted.
- Reviewer C (numerics): hardcode surface eliminated; median/IQR added; PASS.
- Reviewer D (debris feasibility): selectivity/gap framing honest; negative bound stands.
- Editor (ASR): formatting and numbering now clean; references verified.

## Final decision

**SUBMIT-READY.** All round-1 majors are closed and no new defects were
found. The paper's claim is a quantitatively bounded infeasibility —
a legitimate negative result. Remaining honest caveats (model timesteps,
climatological MSIS, idealized co-location upper bound) are declared in
the manuscript's Conclusions.
