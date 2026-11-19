# Gate 1B/5 — Scientific contribution gate

Status: **VERDICT ISSUED 2026-11-08 after the 3-h fine-grid comparison (§4); condition resolved 2026-11-10 by the 12-h fine-grid continuation (§5).** Sections 1–3 were written after the three coarse
pairs (p11_z300, p10_z300, p11_z150) and before any fine-grid (spin8b /
c8b_ctrl / c8b_p11_z300) output exists. Per the G3R/G4T instruction no GO
verdict is issued until the coarse/fine comparison is evaluated. The decision
rule in §3 is frozen now, before the fine-grid result is seen.

Numbers are not restated here; they live in `results/tables/physical_prediction_outcomes.csv`,
`results/physical_model_vs_prescribed_patch.csv`, `results/power_effect_selectivity.csv`
and the generated audits (`docs/PERTURBATION_PHYSICS_AUDIT.md`,
`docs/G3R_RESOLUTION_DISCRETIZATION_AUDIT.md`, `docs/G4T_POWER_EFFECT_SELECTIVITY_TRADEOFF.md`).

## 1. Candidate contributions (from `docs/INCREMENTAL_NOVELTY_MAP.md`) — coarse-grid outcome

| Candidate | Coarse-grid outcome | Gate-1B class | Claim status (G4T vocabulary) |
|---|---|---|---|
| C1 physical-response boundary | 1e11 W over 1 h gives order-unity 400–500 km enhancement; 10× less power gives ~3× smaller peak; 150-km deposition gives ~6× smaller 400-km peak than 300-km deposition (PR1, PR2, PR7 falsified) | EXTENSION of natural-source GITM/TIE-GCM studies to a compact prescribed-energy source | MODEL-DEPENDENT |
| C2 GITM vs prescribed drag | target extra Δv from GITM exceeds the peak-fitted static Gaussian (PR11 confirmed), but the ratio depends strongly on the matching criterion (G4T §Gaussian matching) | MODEL-DEPENDENT OBSERVATION | MODEL-DEPENDENT |
| C3 selectivity boundary | target/non-target extra-Δv ratio ≈ 1–2 at 300–500 km for the 300-km source, ≈ 1 for the 150-km source; lower than every source-centred static Gaussian with σ below ~3.4–3.8 thousand km; decreases from 1e10 to 1e11 W in all 90 tested post-processing × target-radius combinations | NEW COUPLED RESULT (no prior quantification found) — but a *limiting/negative* one: it contradicts the baseline premise | QUALITATIVELY SUPPORTED (coarse grid only; G3R pending) |
| C4 scaling | non-linear in power; only two powers and two altitudes, no functional form | — | UNRESOLVED (no law claimed) |
| C5 energy-anchored exclusion | baseline tracking-case Δv would need ~1e11–1e12 W continuous for a day by linear extrapolation; sublinearity makes this optimistic | EXTENSION, extrapolated | MODEL-DEPENDENT |

## 2. Constraints that cap the verdict regardless of the fine-grid result

1. One physical model (GITM); TIE-GCM inputs inaccessible without Globus credentials — no inter-model spread.
2. One background (March 2002, F10.7 = 150, quiet) — solar/geomagnetic dependence untested (A13).
3. G2 background acceptance failed one predeclared criterion (minimum temperature 118 K vs 150 K, high-latitude 100–107 km); not relaxed.
4. Two horizontal resolutions only; coarse grid resolves σh = 1000 km with ~1.2–1.7 cells — formal convergence cannot be claimed.
5. No transport budget in GITM output: physical spreading vs numerical diffusion is not separated.
6. Heating is an abstract neutral-energy term; no engineering pathway (A14, A15 unsupported).
7. Synthetic circular orbits, one B, 12-h window.

Because of 1–3 and 6, **STRONG GO is excluded a priori** for this study.

## 3. Frozen decision rule for the fine-grid comparison (PR8 / G3R)

Quantities compared on a common 3-h window (onset + 2 h), fine grid remapped
area-conservatively to 10°×5° and also native: 400/500-km peak Δρ/ρ, integrated
mass excess, area-weighted mean anomaly, threshold-free spread (radius of
gyration, participation area), and target/non-target selectivity at 400 and
500 km for the identical object population.

| Fine-grid outcome | Verdict |
|---|---|
| (a) Direction preserved — GITM selectivity at 400 and 500 km stays below the peak-fitted static Gaussian, and the target/non-target ratio stays ≲ 3 — **and** PR8 magnitudes within the frozen bounds (peak change < 30 %, mass-excess change < 20 %) | **CONDITIONAL GO**: a single-model, quantitative-within-stated-limits coupled result ("self-consistent transport erodes the selectivity assumed by prescribed-patch studies; selectivity falls with power and vanishes for lower-thermosphere deposition") |
| (b) Direction preserved, magnitude changes beyond the PR8 bounds (in particular > 50 %) | **POSITIONING GO**: report as qualitative, model-dependent result; no quantitative boundary, no exclusion number in the abstract |
| (c) Direction reverses (fine selectivity ≥ prescribed, or ≳ 3 at 400 km) | investigate (forcing equivalence, decomposition, spin-up difference) before any manuscript work; if unresolved → **NO-GO** for C3, and the remaining C1/C5 alone are judged insufficient against the editorial "novelty" objection |

Known confounders to be reported with any outcome: the fine background was spun
up 6 h from MSIS at 18 UT versus 24 h for the coarse grid; the fine run uses 4
MPI ranks instead of 2 (same executable); the fine window is 3 h, so
persistence/e-folding (PR6) is assessed on the coarse grid only.

## 4. Fine-grid outcome and verdict

Sources: `results/grid_sensitivity_metrics.csv`, `docs/G3R_RESOLUTION_DISCRETIZATION_AUDIT.md` §6,
`results/tables/physical_g4t_gaussian_matching.csv` (rows `*_tmax10800`), PR8a/PR8b in
`results/tables/physical_prediction_outcomes.csv`.

**Magnitude (A-type, physical discretization).** PR8a and PR8b CONFIRMED (400-km peak −7 %, mass excess
≤ 2 %). 54 of 69 remappable metric×altitude rows change by ≤ 13 %, including GITM target/non-target
selectivity at 300–500 km (−3 %), affected-area fractions at every threshold, integrated anomaly, radius of
gyration and its growth rate (+2–5 %). Resolution-sensitive (|A| 0.3–0.7): negative-anomaly extremes and
integrals and sub-cell centroid offsets — none of these carries a claim. Diagnostic-grid (B-type) effects are
≤ 5 % except for the negative-anomaly metrics.

**Direction.** Against the frozen rule in §3:
* 500 km: GITM selectivity below the peak-fitted Gaussian on both grids (≈ 1.6–1.9×) — preserved.
* 400 km, 0–3 h window: GITM and the peak-fitted Gaussian are equal within ~12 %, and the sign of the small
  difference differs between grids (coarse GITM higher, fine GITM 1 % lower). The GITM side changed by −2 %;
  the change comes from the fitted comparator (σ and centre of the fit, +10 %), i.e. a B-type fitting
  dependence, not a change in the physics. Rule (a) is therefore **not met at 400 km** for the 3-h window,
  and the discrepancy was investigated as required by rule (c): it does not reverse the GITM result itself.
* The 400-km erosion relative to the peak-fitted Gaussian (×1.5) appears only over the 12-h window, i.e. after
  switch-off spreading, and is supported on the coarse grid only.
* Against the baseline-style source-centred σ = 1000 km patch, GITM selectivity is 2.8–4.4× lower at
  400–500 km on both grids (0–3 h) and 4.7–8.5× lower over 12 h (coarse) — preserved.

**Verdict: CONDITIONAL GO.** A potentially novel coupled result exists and its 0–3 h quantities are
resolution-robust to ~10 %: (i) self-consistent selectivity is O(1–4) and far below the baseline's
prescribed-patch selectivity; (ii) it decreases from 1e10 to 1e11 W and vanishes for 150-km deposition
(coarse only, two levels each, no functional form); (iii) most of the extra drag falls on non-target objects
after switch-off. STRONG GO is excluded (§2). The claim that self-consistent transport erodes selectivity
*relative to a static field with the same peak and width* is UNRESOLVED at 400 km and QUALITATIVELY
SUPPORTED at 500 km.

**The one specific additional analysis that would resolve the condition:** continue the fine pair
(c8b_ctrl, c8b_p11_z300) from their 3-h restarts to 12 h and repeat the 12-h orbit coupling and
Gaussian matching on the fine grid. Estimated cost on this VM ≈ 2 × 8 h wall, sequential. Without it, the
manuscript must restrict the peak-matched comparison at 400 km to "comparable during heating, lower after
switch-off on the coarse grid (model-dependent)".

## 5. Twelve-hour fine-grid continuation and final gate decision (2026-11-10)

The fine pair was continued from its 03:00 UT restart files to 12:00 UT (`c8x_ctrl`, `c8x_p11_z300`; same
executable, 8×8 grid, 4 ranks, identical heating parameters with the absolute onset unchanged; heating is off in
the continuation window). The 0–3 h products of §4 are unchanged; the 0–12 h fine pair has label
`p11_z300_fine12`. The §3 rule is applied unchanged, now to the 12-h window, by
`scripts/physical_g5_contribution_gate.py` → `results/tables/physical_contribution_gate_checks.csv`.

Sources: `results/grid_sensitivity_metrics_12h.csv` (G3R §7), `results/tables/physical_g4t_gaussian_decomposition.csv`
and `results/tables/physical_g4t_gaussian_matching.csv` (rows `tmax_s = 43200` / `*_tmax43200`),
`results/tables/physical_g4t_selectivity_evolution.csv` (G4T §6), `results/tables/physical_prediction_outcomes.csv`
(PR8a_12h, PR8b_12h, PR10@*_fine12_*).

**Magnitude (A-type).** 57 of 69 remappable metric×altitude rows belong to metrics with |A| ≤ 0.2 at every altitude over 12 h (largest 0.14; 60 rows individually satisfy |A| ≤ 0.2).
GITM 12-h selectivity changes by −2 % (400 km), +1 % (500 km) and −4 % (300 km); at every 10-min output after
the first hour the fine/coarse selectivity ratio stays within −3 %…+6 % at 400–500 km. Integrated 400-km
anomaly, affected area at every threshold, radius of gyration and its growth rate stay within the |A| ≤ 0.2
group. PR8 bounds hold over 12 h (PR8a_12h, PR8b_12h CONFIRMED). Resolution-sensitive rows are the
negative-anomaly metrics (as at 3 h) and end-of-run centroids of a near-global anomaly; neither carries a claim.
At 300 km (the source altitude) selectivity during the heating hour differs by up to ~40 % between grids,
converging to within 5 % after switch-off.

**Direction.** Over 0–12 h, GITM selectivity at 400 and 500 km is below the peak-fitted static Gaussian for
every fit-ingredient variant (own fit, coarse centre, coarse σ, coarse window, all three, sub-grid centre,
source centre) on the coarse, fine-native and fine-remapped grids, and is ≤ 3: rule (a) is met
(`rule_a_all_variants = True`). The 0–3 h 400-km indistinguishability of §4 is a property of the
during-heating window and of the half-maximum window discretization (G4T §4b), not a reversal; it does not
recur over 12 h. Against the baseline-style source-centred σ = 1000 km patch, GITM selectivity is ~5–6× lower
at 400 km and ~8× lower at 500 km on both grids.

**Calibration against the frozen magnitudes.** PR10 (prescribed/GITM ≥ 3) is met at 500 km on both grids but
not at 400 km, where the reduction is ~1.5–1.7× (OUTSIDE_RANGE_NOT_FALSIFIED), and it is falsified at 300 km
(no reduction). The claim is therefore worded as a factor of ~1.5 at 400 km and ~3 at 500 km relative to a
peak-matched static Gaussian, not as a uniform ≥ 3× erosion.

**Time evolution.** On both grids 400-km selectivity decreases monotonically after onset (≈ 5 at 1 h, ≈ 2 at
3 h, ≈ 1.5 at 11 h after onset) and the non-target share of the total extra Δv rises to ≈ 0.85 at 400 km and
≈ 0.77 at 500 km; this is the post-heating redistribution the claim rests on, and it is now supported on two
resolutions.

**Retained confounders and limits.** Unequal spin-up (fine 6 h, coarse 24 h) is part of the A-type
difference; two resolutions are not a convergence study; power and deposition-altitude dependence
(1e10 W, 150 km) remain coarse-grid only and two-level; all §2 constraints apply.

**Final verdict: CONDITIONAL GO — condition resolved; the scientific-contribution gate is satisfied for a
calibrated, single-model claim.** STRONG GO remains excluded (§2). Claim set carried to G6:

1. (C3, SUPPORTED within one model and two resolutions) A compact 1e11 W, 1-h neutral heat source at 300 km
   gives a target/non-target cumulative extra-Δv selectivity of ~1.5 (400 km) and ~2 (500 km) over 12 h, and
   ~1 at 300 km; most of the extra drag falls on non-target objects after switch-off.
2. (C3 vs C2, SUPPORTED at 400–500 km over 12 h; UNRESOLVED during heating at 400 km) Self-consistent
   selectivity is below that of a static Gaussian matched to the GITM peak (×~1.5 at 400 km, ×~3 at 500 km)
   and far below the baseline-style source-centred patch (×~5–8).
3. (QUALITATIVELY SUPPORTED / MODEL-DEPENDENT, coarse only, two levels) Selectivity is lower at 1e11 W than at
   1e10 W and vanishes for 150-km deposition; the peak response is sublinear in power.
4. (MODEL-DEPENDENT, extrapolated) Energy-anchored exclusion bound of §1 C5.

No engineering feasibility, scaling law, causal transport mechanism or observational validation is claimed.
