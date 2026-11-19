# Acta final delta — semantic code audit (Gate 12)

Independent checks: `scripts/acta_semantic_checks.py` → `results/tables/acta_semantic_checks.csv`
(325 checks, all PASS). Each check recomputes an estimand from a lower-level canonical output, a hand calculation or a
synthetic field with a known answer; none reuses the code path being checked except where noted. No GITM run.

| # | Estimand | Definition (manuscript) | Implementation | Independent check | Result |
|---|---|---|---|---|---|
| 1 | Density anomaly | Δρ/ρ = ρ_heated/ρ_control − 1 (Fig. 1 caption, §3.1) | `physical_g3_paired.py` (raw → NPZ/time series, linear-in-z interpolation); `physical_g3r_spread.py` and Fig. 1 (`alt_interp`, log-linear in z) | Sign positive at the 50 min maximum; maximum within 15° of the 45°N source (38°N); Fig. 1 maximum recomputed = ledger 1.938 | PASS. Note: the two interpolations differ by ≈ 2.5% at the fine-grid peak (189% vs 194%); manuscript numbers each name their source |
| 2 | Heating power, energy | P0 = 100 GW, 1 h, 10 min cosine ramps; E = 3.0 × 10^14 J | `user_perturbation_heating.f90` (taper, MPI volume normalization) | Hand integral of the Fortran taper = P0(TDur − TRamp) = 3.0 × 10^14 J; GITM cumulative energy 2.999998 × 10^14 J; realized grid power = P0 to < 1% for all 6 heated runs | PASS |
| 3 | Area-weighted metrics | ∫Δρ dA (kg m⁻¹), participation area (∫Δρ+ dA)²/(A∫Δρ+² dA) | `physical_g3r_spread.py` (`cell_area_unit`, dA = Ω r²) | Cell solid angles sum to 4π on 36×36 and 72×72; participation area of a uniform polar cap equals its area fraction (0.25) exactly | PASS. Units: kg m⁻³ × m² = kg m⁻¹ |
| 4 | Fine→coarse remap | Area-weighted 2×2 means of ρ, then differencing | `coarsen` | Random field: ∫f dA conserved to 1e-9; output 36×36 | PASS |
| 5 | Target classification | Ground track within σh of the source centre while the source is on | `physical_g4_orbit_coupling.py`: `target = min(dist where on) ≤ sig_h` | Target counts identical between the object file and the evolution table (26/28/33 at 300/400/500 km) | PASS |
| 6 | Cumulative extra Δv | Eq. (1): Δv_i = (1/2B)∫[ρ_p|v_rel,p|² − ρ_c|v_rel,c|²]dt′, B = 30 kg m⁻², 10 s steps | `res = rho·Σvr²/(2B)`; `extra = Σ(p − c)·dt` | Hand acceleration for ρ = 3e-12, v = 7.67 km s⁻¹ matches ρv²/(2B); Eq. (1) (OMML) matches the code term by term | PASS |
| 7 | Selectivity, non-target share | Eq. (2): S = ⟨Δv⟩_T/⟨Δv⟩_N; share = ΣΔv_N/ΣΔv_all | `physical_g4t_selectivity_evolution.py` | Recomputed from per-object Δv: S(12 h) = 1.020/1.507/2.029 and shares 0.897/0.844/0.769 = table values (2% tolerance; object file integrates to case end, table to last 10 min output) | PASS. Manuscript keeps S (ratio of means) and share (fraction of total) distinct |
| 8 | Gaussian comparators | Peak-matched: amplitude, centre, e^−½ width at GITM peak, on while peak > ½ max; source-centred: σ = 1000 km, same amplitude/window | `physical_g3r_orbit_sensitivity.py` | S = target/non-target recomputed for all 282 comparator rows; the 18 Fig. 4 cells (2 comparators × 3 grids × 3 altitudes, 12 h) — both comparators exceed GITM at 400 and 500 km (min ratio 1.52, 3.03) | PASS |
| 9 | Uncertainty | 95% percentile intervals from resampling targets and non-targets separately (10,000 replicates) | `physical_g7_selectivity_bootstrap.py` | All 9 intervals bracket the point estimate; resampling unit = orbit object, so intervals describe orbit-sample uncertainty only, not model, forcing or grid uncertainty (stated in §3.2) | PASS |
| 10 | Coarse/fine difference | Max |S_fine/S_coarse − 1| at 400/500 km, 12 h | builder (`S12_fine_vs_coarse_max_diff_400_500_pct`) | Recomputed from unrounded table values = 1.05% | PASS after correction: the baseline computed this from rounded strings (1.3%) — fixed to use unrounded S; manuscript now says "at most 1.1%" |
| 11 | Frozen prediction scoring | PR1–PR12 verdicts against frozen ranges | `physical_g5_prediction_check.py` → `physical_prediction_outcomes.csv` | Every outcome has a verdict (15 confirmed, 7 falsified, 4 outside range); manuscript counts are read from this file | PASS |

## Findings that do not change results

- Comparator wind asymmetry: GITM Δv uses the velocity relative to the co-rotating atmosphere plus GITM winds;
  the static comparator multiplies the control drag computed without winds (`acc_c = ρ_c|v_corot|²/(2B)`) by the
  patch factor. Removing winds from GITM changes S by 0.33% at 400 km and 0.26% at 500 km (`gitm_extra_dv_mean_no_winds`), far below
  the 1.5–8.5× comparator differences, so the asymmetry does not affect any conclusion. Documented here; Methods
  state that winds enter the GITM calculation.
- Fig. 1 baseline plotted the nearest native level (390.6 km), not 400 km — corrected (figure export audit).
- Fig. 1 baseline colour map drew the neutral bin blue — corrected.
- Unit tests (`python3 -m pytest -q`, 34 passed) cover the legacy propagator and provenance; they are not counted as
  semantic evidence here.
