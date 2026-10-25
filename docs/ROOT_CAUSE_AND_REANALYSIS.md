# Root-cause investigation and reanalysis (Gate 3)

Date: 2026-10-17.

## Reproductions and root causes

1. **Stale "0.12%" (B1)** — phase2_validation.csv `fastprop_vs_cowell_250km`
   = 6.23e-4 = 0.062%. Root cause: value typed into prose before the
   corotation fix improved the agreement; not injected. Fix: inject from CSV.
2. **Stale slope/R^2 (C1)** — recomputed `phase11_scaling.py` on the current
   tree: slope=1.016, R^2=0.9984 (vs typed 1.01/0.9995). Root cause: the fit
   was written only to a log/handoff doc, never to a canonical CSV, and the
   prose was frozen. Fix: phase11 now writes
   `results/tables/phase11_scaling_fit.csv`; build aborts if it is missing;
   values injected.
3. **Pi distribution (C2)** — mean 1.062 +- 0.260 is dominated by 7 rows at
   B <= 10 kg/m^2 and 350-400 km where induced drag drifts the object
   relative to the co-located patch most strongly (Pi up to 4.29). Median
   1.022, IQR 0.037. Fix: report median/IQR and the outlier regime in 3.8.
4. **Pi formula (H07)** — text defined Pi = dv B/(rho delta v_rel^2 T)
   (expected 1/2) while the code defines Pi_benefit = 2 dv B/(...) with
   collapse to 1. Fix: formula corrected to include the factor 2.
5. **750 km negative-control wording (C6)** — natural drag at 750 km is far
   below the reported control impulse; "small compared with natural drag"
   was false there. Reworded to "small in absolute terms".
6. **Numbering (E1)** — Table 6 and Figure 7 were cited before Tables 3-5 /
   Figures 4-6; supplement S4 before S1-S3. Renumbered all captions and
   in-text citations to first-appearance order (verified in rendered docx).
7. **Author block (E2)** — "[Authors] T. Onishi et al." implied coauthors;
   corrected to single-author form and first person singular.

## Density-unit revalidation (special priority item)

- `src/atmosphere/msis.py` returns `out[0][5] * 1.0e3` (g/cm^3 -> kg/m^3);
  index 5 is total mass density per the nrlmsise00 gtd7 interface.
- `test_atmosphere_units.py` anchors the profile against published
  magnitudes at 200/400/500 km (factor-of-5 band); both tests pass.
- Downstream uses: density_lookup builds kg/m^3 once; drag, heating and
  energy code all consume kg/m^3 with SI units throughout. No residual
  g/cm^3 path found; no double application of the 1000x factor (single
  conversion point at the model boundary).
- Regime values after correction (moderate): 2.9e-12 kg/m^3 at 400 km,
  consistent with Emmert (2015) climatology.

## `inf` lifetimes

21/396 baseline grid cells are right-censored at the integration horizon;
the text states this and excludes them from statistics. No multi-century
lifetime is claimed anywhere.

## What was rerun vs preserved

- Rerun: `phase11_scaling.py` (only analysis whose prose values had gone
  stale), `build_manuscript.py` (all artifacts).
- Preserved: all other canonical CSVs (validated state; no scientific
  defect required re-computation).
- Effect on conclusions: none — the gap decomposition, selectivity and
  energy results are unchanged; the revision is presentational/provenance.
