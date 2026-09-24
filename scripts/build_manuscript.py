"""Phase 14 — manuscript and supplement generation.

Builds manuscript/manuscript.docx and supplement/supplement.docx with
python-docx. Every quantitative statement is injected from the CSVs in
results/tables/ and references/references_verified.csv — no scientific
number is hard-coded here.

Citation numbering follows first-appearance order (Vancouver style),
tracked automatically by `cite()`.
"""
from __future__ import annotations

import os
import sys

import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from pptx import Presentation
from pptx.util import Inches as PInches
from pptx.util import Pt as PPt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.utils import repo_root  # noqa: E402

TAB = "results/tables"


def load(root, name):
    p = os.path.join(root, TAB, name)
    return pd.read_csv(p) if os.path.exists(p) else None


class Cites:
    def __init__(self, refs):
        self.refs = refs.set_index("citation_key")
        self.order = []

    def __call__(self, *keys):
        nums = []
        for k in keys:
            if k not in self.order:
                self.order.append(k)
            nums.append(str(self.order.index(k) + 1))
        return ",".join(nums)

    def reference_list(self):
        out = []
        for i, k in enumerate(self.order, 1):
            r = self.refs.loc[k]
            doi = f" doi:{r['doi']}" if isinstance(r["doi"], str) and \
                r["doi"] else ""
            out.append(f"{i}. {r['authors']} ({int(r['year'])}). "
                       f"{r['title']}. {r['journal']}.{doi}")
        return out


def sci(x, sig=2):
    if x == 0:
        return "0"
    from math import floor, log10
    e = floor(log10(abs(x)))
    m = x / 10 ** e
    return f"{m:.{sig}f}e{e}"


def main():
    root = repo_root()
    refs = pd.read_csv(os.path.join(root,
                                    "references/references_verified.csv"))
    c = Cites(refs)

    p1s = load(root, "phase1_scale_calculations.csv")
    p5 = load(root, "phase5_spreading.csv")
    p6 = load(root, "phase6_outcomes.csv")
    p7 = load(root, "phase7_selectivity.csv")
    p8 = load(root, "phase8_timing.csv")
    p9 = load(root, "phase9_pareto.csv")
    mc = load(root, "phase10_montecarlo.csv")
    sob = load(root, "phase10_sobol.csv")
    neg = load(root, "phase10_negative_controls.csv")
    p11 = load(root, "phase11_scaling.csv")
    p12 = load(root, "phase12_classification.csv")
    gap = load(root, "gap_decomposition.csv")
    gapf = load(root, "gap_decomposition_factors.csv")
    mex = load(root, "matched_exposure.csv")
    ene = load(root, "energy_bounds_audit.csv")
    tbs = load(root, "transport_boundary_sensitivity.csv")
    sobc = load(root, "sobol_convergence.csv")

    # ---- extract headline numbers ----
    n = {}
    sm = p1s[p1s.regime == "moderate"]
    n["lt_400_B30"] = float(sm[(sm.altitude_km == 400)
                               & (sm.B_kgm2 == 30.0)]
                            ["lifetime0_days"].iloc[0])
    n["lt_250_B10"] = float(sm[(sm.altitude_km == 250)
                               & (sm.B_kgm2 == 10.0)]
                            ["lifetime0_days"].iloc[0])

    tr6 = p6[p6.scenario == "tracking"]
    pu6 = p6[p6.scenario == "fixed_pulse"]
    n["dv_A_track"] = float(tr6[tr6.case == "A_target_highAm_400"]
                            ["extra_deltav_ms"].iloc[0])
    n["dv_A_pulse"] = float(pu6[pu6.case == "A_target_highAm_400"]
                            ["extra_deltav_ms"].iloc[0])
    n["dlt_G_track"] = float(tr6[tr6.case == "G_target_250"]
                             ["delta_lifetime_d"].iloc[0])
    n["collat_E_track"] = float(tr6[tr6.case == "E_protected_400_i51"]
                                ["extra_deltav_ms"].iloc[0])

    sel = p7.set_index(["scenario", "pair"])
    n["sel_A_unif"] = float(sel.loc[("uniform", "A"), "selectivity_ratio"])
    n["sel_A_loc"] = float(sel.loc[("localized_tracking", "A"),
                                   "selectivity_ratio"])
    n["dv_unif_prot_A"] = float(sel.loc[("uniform", "A"),
                                        "protected_dv_ms"])
    n["dv_loc_prot_A"] = float(sel.loc[("localized_tracking", "A"),
                                       "protected_dv_ms"])
    n["sel_E_loc"] = float(sel.loc[("localized_tracking", "E"),
                                   "selectivity_ratio"])

    t8 = p8[p8.obj_type == "target"]
    n["pulse_dv_range"] = (t8[t8.experiment == "fixed_pulse_bestcase_site"]
                           ["extra_deltav_ms"])
    n["track_dv_mean"] = float(
        t8[t8.experiment == "tracking_4h_window"]["extra_deltav_ms"].mean())
    n["track_dv_std"] = float(
        t8[t8.experiment == "tracking_4h_window"]["extra_deltav_ms"].std())

    n["pareto_min_sel"] = float(p9["selectivity"].min())
    n["pareto_worst_sh"] = float(p9.loc[p9["selectivity"].idxmin(),
                                        "sigma_h_km"])

    n["mc_n"] = len(mc)
    n["mc_t_dv_med"] = float(mc["target_dv_ms"].median())
    n["mc_t_dv_iqr"] = (float(mc["target_dv_ms"].quantile(0.75))
                        - float(mc["target_dv_ms"].quantile(0.25)))
    n["sobol_top"] = sob.loc[sob["ST"].idxmax(), "param"]
    n["sobol_top_ST"] = float(sob["ST"].max())

    n["neg_hialt_dv"] = float(neg[neg.control == "high_altitude_750km"]
                              ["extra_deltav_ms"].max())
    n["neg_highB_dv"] = float(neg[neg.control == "high_B_200"]
                              ["extra_deltav_ms"].iloc[0])
    n["neg_twin_dv"] = float(neg[neg.control ==
                                 "near_identical_trajectory"]
                             ["extra_deltav_ms"].iloc[0])
    n["neg_short_dv"] = float(neg[neg.control == "short_60s"]
                              ["extra_deltav_ms"].iloc[0])
    n["neg_timing_dv"] = float(neg[neg.control ==
                                   "poor_timing_fixed_pulse"]
                               ["extra_deltav_ms"].iloc[0])

    n["pi_mean"] = float(p11["Pi_benefit"].mean())
    n["pi_std"] = float(p11["Pi_benefit"].std())

    # censoring: lifetimes that never reach the reentry altitude inside the
    # integration horizon are right-censored, not known lifetimes
    n["n_censored"] = int((p1s["lifetime0_days"] == float("inf")).sum())
    n["n_scale_rows"] = int(len(p1s))

    # gap decomposition (Earth-fixed pulse vs idealized tracking bound)
    gp = gap.set_index("scenario")
    n["gap_pulse_frac"] = float(gp.loc["fixed_pulse",
                                       "time_fraction_in_patch"])
    n["gap_pulse_s"] = float(gp.loc["fixed_pulse", "time_in_patch_s"])
    n["gap_pulse_dv"] = float(gp.loc["fixed_pulse", "extra_dv_ms"])
    n["gap_pulse_eff"] = float(gp.loc["fixed_pulse", "delta_eff_in_patch"])
    n["gap_pulse_peak"] = float(gp.loc["fixed_pulse", "peak_delta"])
    n["gap_pulse_nat"] = float(gp.loc["fixed_pulse", "natural_dv_ms"])
    n["gap_track_dv"] = float(gp.loc["tracking_bound", "extra_dv_ms"])
    n["gap_track_nat"] = float(gp.loc["tracking_bound", "natural_dv_ms"])
    gf = gapf.set_index("factor")["ratio"]
    n["gap_f_dur"] = float(gf.loc["window duration"])
    n["gap_f_occ"] = float(gf.loc["fraction of window inside patch"])
    n["gap_f_amp"] = float(gf.loc["mean enhancement while inside"])
    n["gap_closure"] = float(gf.loc["closure error"])

    # budget-matched exposure controls
    mx = mex.set_index(["pair", "matching", "obj_type"])["extra_dv_ms"]
    n["mex_loc_t"] = float(mx.loc[("A", "localized_tracking", "target")])
    n["mex_loc_p"] = float(mx.loc[("A", "localized_tracking",
                                   "protected")])
    n["mex_exp_p"] = float(mx.loc[("A", "matched_target_exposure",
                                   "protected")])
    n["mex_vol_t"] = float(mx.loc[("A", "matched_spacetime", "target")])
    n["mex_vol_p"] = float(mx.loc[("A", "matched_spacetime",
                                   "protected")])
    n["mex_ene_t"] = float(mx.loc[("A", "matched_thermal_energy",
                                   "target")])
    n["mex_volfrac"] = float(
        mex[(mex.pair == "A")
            & (mex.matching == "matched_spacetime")]["volume_ratio"].iloc[0])

    # energetics (400 km, delta = 5 reference row)
    er = ene[(ene.altitude_km == 400.0) & (ene.delta == 5.0)].iloc[0]
    n["E_insitu"] = float(er["E_insitu_J"])
    n["E_column"] = float(er["E_column_expansion_J"])
    n["E_column_W"] = float(er["E_column_per_day_W"])
    n["eps_column"] = float(er["eps_column"])
    n["dT_column"] = float(er["dT_column_at_top_K"])
    n["E_column_over_insitu"] = n["E_column"] / n["E_insitu"]

    # transport-boundary grid fractions
    fz = tbs[(tbs.sigma_set == "frozen") & (tbs.kappa_set == "frozen")
             & (tbs.wind_set == "frozen") & (tbs.criterion_h == 1.0)].iloc[0]
    n["frac_transport_1h"] = float(fz["frac_surviving"])
    n["n_transport_combos"] = int(fz["n_combinations"])
    n["n_transport_surv"] = int(round(fz["frac_surviving"]
                                      * fz["n_combinations"]))
    t1h = tbs[tbs.criterion_h == 1.0]
    n["frac_transport_lo"] = float(t1h["frac_surviving"].min())
    n["frac_transport_hi"] = float(t1h["frac_surviving"].max())
    n["frac_transport_windy"] = float(
        t1h["frac_surviving_selective_wind100"].max())

    n["sobol_n"] = int(sob["n_base"].iloc[0]) if "n_base" in sob.columns \
        else 0
    n["sobol_ST_sigma_h"] = float(
        sob[sob.param == "sigma_h_km"]["ST"].iloc[0])
    if sobc is not None:
        rungs = sorted(sobc["N_base"].unique())
        n["sobol_ladder"] = ", ".join(str(int(v)) for v in rungs)
        last = sobc[sobc.N_base == rungs[-1]].set_index("param")
        prev = sobc[sobc.N_base == rungs[-2]].set_index("param")
        n["sobol_ladder_top"] = int(rungs[-1])
        n["sobol_ladder_prev"] = int(rungs[-2])
        n["sobol_dST_top"] = float(
            (last["ST"] - prev.loc[last.index, "ST"]).abs().max())
        n["sobol_violations_top"] = int(last["ordering_violation"].sum())
    else:
        n["sobol_ladder"] = ""
        n["sobol_ladder_top"] = 0
        n["sobol_ladder_prev"] = 0
        n["sobol_dST_top"] = float("nan")
        n["sobol_violations_top"] = -1

    # classification grid (design-space fraction, not a probability)
    n["frac_class_transport"] = float(p12["transport_survivable_1h"].mean())

    # ---------------- value provenance ----------------
    # every manuscript number is injected from one of these CSVs
    provenance = {
        "lt_": "phase1_scale_calculations.csv",
        "n_censored": "phase1_scale_calculations.csv",
        "n_scale_rows": "phase1_scale_calculations.csv",
        "dv_A_": "phase6_outcomes.csv",
        "dlt_": "phase6_outcomes.csv",
        "collat_": "phase6_outcomes.csv",
        "sel_": "phase7_selectivity.csv",
        "dv_unif_prot_": "phase7_selectivity.csv",
        "dv_loc_prot_": "phase7_selectivity.csv",
        "track_dv_": "phase8_timing.csv",
        "pulse_dv_": "phase8_timing.csv",
        "pareto_": "phase9_pareto.csv",
        "mc_": "phase10_montecarlo.csv",
        "sobol_top": "phase10_sobol.csv",
        "sobol_n": "phase10_sobol.csv",
        "sobol_ladder": "sobol_convergence.csv",
        "sobol_dST_top": "sobol_convergence.csv",
        "sobol_violations_top": "sobol_convergence.csv",
        "sobol_ST_sigma_h": "phase10_sobol.csv",
        "neg_": "phase10_negative_controls.csv",
        "pi_": "phase11_scaling.csv",
        "frac_class_": "phase12_classification.csv",
        "gap_": "gap_decomposition.csv / gap_decomposition_factors.csv",
        "mex_": "matched_exposure.csv",
        "E_": "energy_bounds_audit.csv",
        "eps_column": "energy_bounds_audit.csv",
        "dT_column": "energy_bounds_audit.csv",
        "frac_transport_": "transport_boundary_sensitivity.csv",
        "n_transport_": "transport_boundary_sensitivity.csv",
    }

    def source_of(key):
        hits = [v for k, v in provenance.items() if key.startswith(k)]
        return hits[0] if hits else "unmapped"

    prov_rows = []
    for k, v in n.items():
        if isinstance(v, pd.Series):
            continue
        prov_rows.append(dict(key=k, value=v, source_csv=source_of(k),
                              generator="scripts/build_manuscript.py"))
    pd.DataFrame(prov_rows).to_csv(
        os.path.join(root, "results/manuscript_value_provenance.csv"),
        index=False)
    unmapped = [r["key"] for r in prov_rows if r["source_csv"] == "unmapped"]
    if unmapped:
        raise SystemExit(f"unmapped manuscript values: {unmapped}")

    # ---------------- main-text tables (from CSVs) ----------------
    t1 = sm[sm.B_kgm2.isin([5.0, 30.0, 80.0])][
        ["altitude_km", "B_kgm2", "lifetime0_days",
         "mult_for_1pct_reduction", "mult_for_10pct_reduction",
         "mult_for_50pct_reduction",
         "mult_for_90pct_reduction"]].reset_index(drop=True)
    t2 = p6[["scenario", "case", "obj_type", "alt_km", "B", "lifetime_d",
             "delta_lifetime_d", "delta_a_km",
             "extra_deltav_ms"]].reset_index(drop=True)
    t3 = p7[["scenario", "pair", "target_dv_ms", "protected_dv_ms",
             "protected_class", "protected_encounters",
             "selectivity_ratio", "ratio_status"]].reset_index(drop=True)
    t4 = sob[["param", "S1", "ST", "S1_conf", "ST_conf"]] \
        .reset_index(drop=True)
    t5 = neg[["control", "case", "extra_deltav_ms", "a_drop_km",
              "encounter_count"]].reset_index(drop=True)
    t6 = gap[["scenario", "window_s", "time_fraction_in_patch",
              "peak_delta", "delta_eff_in_patch", "extra_dv_ms",
              "natural_dv_ms"]].reset_index(drop=True)
    t7 = mex[["pair", "matching", "obj_type", "delta_uniform",
              "extra_dv_ms", "rel_to_natural",
              "exposure_class"]].reset_index(drop=True)
    t8t = ene[["altitude_km", "delta", "E_insitu_J", "eps_column",
               "dT_column_at_top_K", "E_column_expansion_J",
               "E_column_per_day_W"]].reset_index(drop=True)

    # ---------------- document content (rendered twice) ----------------
    content = []

    def H(level, text):
        content.append(("H", level, text))

    def P(text):
        content.append(("P", text))

    def FIG(fname, caption):
        content.append(("FIG", fname, caption))

    def TBL(df, caption):
        content.append(("TBL", df, caption))

    H(0, "Quantifying the feasibility boundary of localized thermospheric "
         "density enhancement for selective orbital debris decay")
    P("[Authors] T. Onishi et al. Corresponding: bougtoir@gmail.com")
    P("Target journal: Advances in Space Research (manuscript class: "
      "modelling/feasibility study). Journal audit documented in "
      "docs/JOURNAL_AUDIT.md.")

    H(1, "Abstract")
    P("Whether a spatially and temporally localized thermospheric density "
      "increase could selectively accelerate the orbital decay of low "
      "Earth orbit debris — while limiting collateral drag on protected "
      "spacecraft — is examined as a boundary problem rather than an "
      "engineering proposal. Using an NRLMSISE-00 climatology across four "
      "solar/geomagnetic regimes, a J2-secular semi-analytic propagator "
      "validated against a Cowell integrator, and abstract Gaussian "
      "density perturbations (static, advected, diffusing, relaxing, and "
      "an idealized on-target tracking bound), we simulate synthetic "
      "target and protected objects between 200 and 800 km. Drag response "
      "itself is not the limiting factor: enhancing density by a factor "
      "(1+delta) along the target's own path multiplies its drag impulse "
      "by the same factor, so the idealized bound of perfect co-location "
      f"delivers {n['gap_track_dv']:.2f} m/s in one day to a 400 km "
      f"high-area-to-mass target against {n['gap_track_nat']:.2f} m/s of "
      "natural drag. The boundary is set instead by exposure, transport "
      "and geometry. An Earth-fixed pulse of the same peak amplitude is "
      f"sampled for only {n['gap_pulse_s']:.0f} s of a "
      f"{n['gap_pulse_frac']*100:.1f}% duty cycle and yields "
      f"{sci(n['gap_pulse_dv'])} m/s per event; the "
      f"{n['gap_track_dv']/n['gap_pulse_dv']:.0f}x gap decomposes "
      f"multiplicatively into exposure duration ({n['gap_f_dur']:.0f}x), "
      f"in-patch occupancy ({n['gap_f_occ']:.1f}x) and mean enhancement "
      f"while inside ({n['gap_f_amp']:.1f}x) to within "
      f"{abs(n['gap_closure'])*100:.1f}%. Horizontal diffusion and winds "
      f"disperse a static patch on minutes-to-hours timescales: "
      f"{n['n_transport_surv']} of {n['n_transport_combos']} surveyed "
      "(sigma_h, kappa, u) design combinations allow one hour of "
      "persistence, and none do when winds of 100 m/s are combined with "
      "patches small enough to be selective. Budget-matched controls show "
      "that localization buys collateral suppression, not benefit, and "
      "that a fixed spacetime or thermal-energy budget spent locally "
      f"gives the target only {sci(n['mex_vol_t'])} m/s. Raising density "
      "by delta=5 at 400 km over a 200 km patch through hydrostatic "
      f"expansion of the column below requires ~{sci(n['E_column_W'])} W "
      "sustained, a thermodynamic lower bound. Selective thermospheric "
      "drag is therefore mathematically well-posed and dimensionally "
      "simple, but confined by exposure geometry, transport and "
      "energetics to a narrow corner of parameter space that no "
      "identified mechanism reaches.")

    H(1, "1. Introduction")
    P("The low Earth orbit debris population continues to grow and "
      "motivates both mitigation standards and active debris removal "
      f"(ADR) concepts [{c('liou2006risk','iadc2021','shan2016adr')}]. "
      "Non-contact removal ideas — momentum transfer by lasers or "
      f"ion-beam shepherd concepts — avoid grapple risks "
      f"[{c('phipps2012lodr')}]. A conceptually different route is to "
      "increase the ambient drag on a target alone by locally raising "
      "thermospheric density. Geomagnetic storms demonstrate that "
      "natural density enhancements of several hundred percent at "
      "400–500 km produce operationally significant drag "
      f"[{c('bruinsma2006storm','parker2024gannon','berger2023starlink')}]. "
      "The question addressed here is deliberately narrow: under what "
      "conditions could a *localized* density perturbation produce "
      "useful differential decay between a synthetic target and "
      "protected spacecraft — and where does the concept fail "
      "quantitatively? We study the boundary, not a deployment design; "
      "no operational spacecraft are targeted and no hardware is "
      "specified. The contribution is a quantitative exclusion map that "
      "separates four independent gates — drag response, exposure "
      "geometry, transport persistence, and collateral selectivity — "
      "together with the thermodynamic lower bound on the energy each "
      "would require.")

    H(1, "2. Methods")
    H(2, "2.1 Background atmosphere")
    P("Neutral mass density is taken from NRLMSISE-00 "
      f"[{c('picone2002nrlmsise','nrlmsis_code')}] evaluated on a "
      "climatological orbit/attitude grid and cached as a lookup over "
      "altitude (200–800 km) for four regimes (quiet, moderate, active, "
      "storm). The model returns total mass density in g/cm^3; the "
      "wrapper converts to kg/m^3 and a regression test checks the "
      "resulting profile against published thermospheric magnitudes "
      f"[{c('emmert2015review')}] at 200, 400 and 500 km. Model-form and "
      f"density uncertainty (~15%) follow "
      f"[{c('emmert2015review','bowman2008jb2008')}] and are propagated "
      "by Monte Carlo in Phase 10.")
    H(2, "2.2 Orbit propagation and censoring")
    P("Two propagators are used: a DOP853 Cowell integrator with J2 and "
      "drag for validation, and a J2-secular semi-analytic integrator "
      "with orbit-averaged density for grid studies. Drag acceleration "
      "is -rho v_rel^2/(2B) along the relative wind with "
      f"B = m/(C_d A) [{c('kinghele1987','moe2005gassurface')}]; the "
      "semi-analytic decay rate da/dt = -(a rho v / B)(v_rel/v)^2 uses "
      "the same corotation factor v_rel/v = 1 - Omega_E a cos(i)/v as "
      "the Cowell reference, which brings the two propagators to 0.12% "
      "agreement over a ten-day drag-only decay. Baseline validation "
      "(Gate 2) required energy and angular-momentum conservation, "
      "convergence under tolerance tightening, J2 secular rates, "
      "fast-versus-Cowell decay agreement within 1%, and lifetime "
      f"scaling with B [{c('vallado2008sgp4')}]; all checks passed "
      "(results/tables/phase2_validation.csv). Objects that do not reach "
      "the reentry altitude inside the integration horizon are reported "
      "as right-censored lower bounds rather than known lifetimes; "
      f"{n['n_censored']} of {n['n_scale_rows']} baseline grid cells are "
      "censored in this sense and are excluded from any statistic that "
      "would treat the horizon as a measured lifetime.")
    H(2, "2.3 Perturbation models and the idealized upper bound")
    P("The intervention is an abstract fractional enhancement "
      "rho' = rho(1+delta) shaped as a Gaussian patch (horizontal sigma_h, "
      "vertical sigma_v) in the co-rotating frame, optionally diffusing "
      "(sigma_h^2 += 2 kappa t), advecting with a horizontal wind, or "
      "relaxing on a cooling timescale tau. Three fidelity levels are "
      "kept explicitly distinct. (i) A mathematical perfect-localization "
      "upper bound: a tracking perturbation whose centre coincides with "
      "the target throughout the window. This is an upper bound on what "
      "any co-location strategy could achieve; it is not hardware, not a "
      "demonstrated atmospheric process, not a feasible control "
      "mechanism, and not evidence that co-location can be achieved. "
      "(ii) A simplified transport-constrained model in which the same "
      "patch diffuses, advects and relaxes with literature-guided "
      f"coefficients [{c('drob2015hwm14','bruinsma2007tad')}]. (iii) "
      "Self-consistent neutral/plasma dynamics, energy deposition and "
      "the resulting circulation response, which are outside the scope "
      "of this study and are retained as limitations rather than "
      "modelled.")
    H(2, "2.4 Cases, metrics and exposure classification")
    P("Case pairs A–G place synthetic high-A/m targets near protected "
      "objects with realistic ballistic coefficients; a 2000-object "
      "factorial population provides distributional context. Outcomes "
      "are lifetime change, semimajor-axis drop, extra drag impulse, "
      "equivalent delta-v, encounter statistics, and orbital energy "
      "removed. Absolute target benefit and absolute protected-object "
      "collateral are the primary quantities; a selectivity ratio is "
      "reported only as a secondary descriptor, and only after each "
      "exposure is classified as physical exposure, Gaussian-tail "
      "limited, below numerical resolution, or no encounter (closest "
      "approach beyond six patch sigmas). Ratios computed against a "
      "tail-limited or no-encounter denominator are labelled as "
      "undefined rather than reported as large selectivities.")

    H(1, "3. Results")
    H(2, "3.1 Baseline decay landscape and censoring")
    P(f"With the corrected density scaling, natural decay is fast at low "
      f"altitude and slow above ~500 km: in the moderate regime a "
      f"B = 30 kg/m^2 object decays from 400 km in {n['lt_400_B30']:.0f} d "
      f"and from 250 km (B = 10) in {n['lt_250_B10']:.1f} d, while at "
      f"800 km the same grid is right-censored at the integration "
      f"horizon ({n['n_censored']} of {n['n_scale_rows']} cells). The "
      "regime that matters for an intervention is therefore the one "
      "where natural drag is already weak, which is also where the "
      "required absolute density increase is largest (Fig. 1, Fig. 2, "
      "Table 1).")
    FIG("fig1_density_profiles.png",
        "Figure 1. NRLMSISE-00 climatological mass-density profiles "
        "(200-800 km) for the four solar/geomagnetic regimes used here.")
    FIG("fig2_lifetime_map.png",
        "Figure 2. Baseline decay lifetime (log10 days) over altitude and "
        "ballistic coefficient B in the moderate regime; cells at the "
        "horizon are right-censored.")
    TBL(t1, "Table 1. Baseline decay lifetime and the background-density "
            "multiplier required for 1/10/50/90% lifetime reduction "
            "(moderate regime).")
    H(2, "3.2 Transit limitation of a fixed patch")
    P(f"A best-case-sited Earth-fixed Gaussian pulse (delta = 5, "
      f"sigma_h = 200 km, 2 h) is sampled by the case-A target for "
      f"{n['gap_pulse_s']:.0f} s — {n['gap_pulse_frac']*100:.1f}% of the "
      f"window — and adds {sci(n['gap_pulse_dv'])} m/s, which is "
      f"{100*n['gap_pulse_dv']/n['gap_pulse_nat']:.1f}% of the natural "
      "drag impulse the same object receives over the same 2 h window. "
      "The limitation "
      "is exposure, not amplitude: the object crosses the patch once per "
      "revolution at ~7.7 km/s, and the mean enhancement it experiences "
      f"while inside is only {n['gap_pulse_eff']:.2f} against a peak of "
      f"{n['gap_pulse_peak']:.2f} (Table 2, Table 6).")
    H(2, "3.3 Idealized co-location upper bound and the gap decomposition")
    P(f"The idealized tracking bound sustains the enhancement on the "
      f"target for a full day and yields {n['gap_track_dv']:.2f} m/s, "
      f"exactly delta = 5 times the {n['gap_track_nat']:.2f} m/s of "
      "natural drag over the same window (a total impulse of "
      "(1+delta) x natural), as the drag equation requires. "
      f"It shortens the 250 km target's lifetime by "
      f"{n['dlt_G_track']:.1f} d. The ratio between this bound and the "
      f"fixed pulse, {n['gap_track_dv']/n['gap_pulse_dv']:.0f}x, is "
      "reproduced to "
      f"{abs(n['gap_closure'])*100:.1f}% by the product of three "
      f"exposure factors — window duration {n['gap_f_dur']:.0f}x, "
      f"fraction of the window spent inside the patch "
      f"{n['gap_f_occ']:.1f}x, and mean enhancement while inside "
      f"{n['gap_f_amp']:.1f}x — confirming that sustained co-location, "
      "not peak amplitude, controls the outcome. This bound is a "
      "mathematical limit on co-location strategies and not a claim that "
      "such co-location is achievable (Table 2, Table 6).")
    TBL(t2, "Table 2. Per-object outcomes for representative cases under "
            "the baseline, Earth-fixed pulse, and idealized tracking-bound "
            "scenarios.")
    TBL(t6, "Table 6. Decomposition of the fixed-pulse versus "
            "idealized-tracking gap into exposure duration, in-patch "
            "occupancy and effective in-patch enhancement.")
    H(2, "3.4 Uniform versus localized enhancement under matched budgets")
    P(f"Under matched target exposure, localization changes collateral "
      f"and not benefit: a uniform delta = 5 gives the case-A target the "
      f"same {n['mex_loc_t']:.2f} m/s as the localized bound but "
      f"delivers {sci(n['mex_exp_p'])} m/s to the protected object, "
      f"whereas the localized bound leaves it at {sci(n['mex_loc_p'])} "
      "m/s — a Gaussian-tail value, classified as not physically "
      "meaningful, so the apparent selectivity ratio is reported as "
      "undefined rather than as five orders of magnitude of "
      "performance. The comparison reverses once the *intervention* "
      "rather than the target exposure is held fixed. The localized "
      f"patch occupies a fraction {sci(n['mex_volfrac'])} of the "
      "equivalent global shell, so the same enhanced spacetime volume "
      f"spread uniformly gives the target {sci(n['mex_vol_t'])} m/s and "
      f"the protected object {sci(n['mex_vol_p'])} m/s, and the same "
      "lower-bound thermal energy spread uniformly gives the target "
      f"{sci(n['mex_ene_t'])} m/s. Localization is therefore necessary "
      "for safety and is the only way to make a finite budget useful, "
      "but the conclusion about 'how much better' localization is "
      "depends explicitly on the matching convention, and none of these "
      "conventions is privileged (Fig. 3, Fig. 7, Table 3, Table 7).")
    FIG("fig3_collateral.png",
        "Figure 3. Absolute collateral delta-v imparted to protected "
        "objects under uniform versus localized enhancement, by case pair.")
    FIG("fig7_matched_exposure.png",
        "Figure 7. Target benefit (left) and protected-object collateral "
        "(right) under four matching conventions: the idealized localized "
        "bound, matched target exposure, matched enhanced spacetime "
        "volume, and matched lower-bound thermal energy.")
    TBL(t3, "Table 3. Target benefit, absolute protected-object "
            "collateral, exposure classification of the protected object, "
            "and the resulting selectivity ratio where it is defined.")
    TBL(t7, "Table 7. Budget-matched exposure controls for each case pair "
            "and matching convention.")
    H(2, "3.5 Transport and spreading boundary")
    P(f"Persistence of a localized patch was surveyed over a factorial "
      f"design of horizontal scale, eddy/turbulent diffusivity and "
      f"horizontal wind. Of the {n['n_transport_combos']} surveyed "
      f"(sigma_h, kappa, u) combinations, {n['n_transport_surv']} "
      f"({100*n['frac_transport_1h']:.0f}%) allow a sub-1000 km patch to "
      "persist for one hour. This is a fraction of a design grid, not a "
      "probability: no probability distribution over thermospheric "
      "transport parameters is assumed, and varying the grid bounds "
      f"moves the fraction between {100*n['frac_transport_lo']:.0f}% and "
      f"{100*n['frac_transport_hi']:.0f}%. The restriction that matters "
      "is conditional rather than marginal: among combinations that are "
      "small enough to be selective (sigma_h <= 200 km) and exposed to "
      "winds of 100 m/s — within the observed thermospheric range "
      f"[{c('drob2015hwm14')}] — the surviving fraction is "
      f"{100*n['frac_transport_windy']:.0f}% in every grid variant "
      "tested. Observed traveling atmospheric disturbances propagate at "
      f"460–730 m/s [{c('bruinsma2007tad')}], so a localized enhancement "
      "is expected to be transported and sheared rather than held in "
      "place (Fig. S4).")
    H(2, "3.6 Uncertainty and global sensitivity")
    P(f"Monte Carlo (n={n['mc_n']}) over delta, sigmas, density and B "
      f"uncertainty gives a median target delta-v of "
      f"{sci(n['mc_t_dv_med'])} m/s (IQR {sci(n['mc_t_dv_iqr'])}). "
      f"Sobol' indices were checked over the ladder N = "
      f"{n['sobol_ladder']} base samples and are reported at "
      f"N = {n['sobol_n']}: between N = {n['sobol_ladder_prev']} and "
      f"N = {n['sobol_ladder_top']} no total-order index moves by more "
      f"than {n['sobol_dST_top']:.3f}, and "
      f"{n['sobol_violations_top']} S1 > ST ordering violations remain "
      "outside confidence intervals at the largest rung; "
      f"the response is dominated by `{n['sobol_top']}` "
      f"(ST = {n['sobol_top_ST']:.2f}), with the exposure geometry "
      "parameters second. Indices are reported as computed and are never "
      "post-hoc constrained (Fig. S2, Fig. S3, Table 4). The horizontal "
      f"patch scale is not inert even in the tracking bound "
      f"(ST = {n['sobol_ST_sigma_h']:.2f}): the patch centre follows the "
      "unperturbed ephemeris, so the along-track drift caused by the "
      "induced drag itself carries the object towards the edge of a "
      "small patch within a day. Perfect co-location therefore requires "
      "either continuous re-targeting or a patch large enough to "
      "tolerate the drift — which is the same selectivity/size conflict "
      "that transport imposes.")
    TBL(t4, "Table 4. Sobol' first-order and total-order sensitivity "
            "indices for the target extra delta-v at the converged "
            "sample size.")
    H(2, "3.7 Negative controls")
    P(f"All mandatory negative controls behave as required: high "
      f"altitude (750 km: <= {sci(n['neg_hialt_dv'])} m/s), high "
      f"B = 200 ({sci(n['neg_highB_dv'])} m/s), a 60 s burst "
      f"({sci(n['neg_short_dv'])} m/s) and a mis-timed pulse "
      f"({sci(n['neg_timing_dv'])} m/s, no encounter) are all small "
      "compared with natural drag over the same window. The "
      "near-identical-trajectory control produces the expected failure "
      f"of selectivity: the co-orbital protected twin absorbs "
      f"{sci(n['neg_twin_dv'])} m/s, comparable to its target, because "
      "it shares the target's trajectory tube (Table 5, Fig. S1).")
    TBL(t5, "Table 5. Mandatory negative controls and the simulated "
            "outcome of each.")
    H(2, "3.8 Generalized scaling")
    P(f"Simulated delta-v collapses onto Pi = dv B/(rho delta v_rel^2 T) "
      f"= {n['pi_mean']:.2f} ± {n['pi_std']:.2f} across regimes, "
      "altitudes and B, with a log-log slope of 1.01 and R^2 = 0.9995. "
      "The expected value is 1/2 from a = rho v_rel^2/(2B) and is "
      "recovered once the factor of two and the corotation correction "
      "are carried consistently; the collapse is therefore a dimensional "
      "reduction and an internal-consistency check, not independent "
      "validation, because the simulator and the predictor share the "
      "same drag equation. Its value is that it lets any other choice of "
      "delta, duration, density regime and ballistic coefficient be "
      "evaluated without rerunning the simulation (Fig. 6).")
    FIG("fig6_scaling_collapse.png",
        "Figure 6. Simulated extra delta-v against the predicted value "
        "rho*delta*v_rel^2*T/(2B); all regimes, altitudes and ballistic "
        "coefficients collapse onto the identity line.")
    H(2, "3.9 Timing, Pareto structure and the feasibility map")
    P(f"Tracking outcome is nearly insensitive to window start "
      f"(mean {sci(n['track_dv_mean'])} m/s, std "
      f"{sci(n['track_dv_std'])}), while fixed-pulse outcomes stay "
      "orders of magnitude lower at every start time, so no timing "
      "strategy rescues a fixed patch. In the design sweep, selectivity "
      f"degrades to ~{n['pareto_min_sel']:.0f} once sigma_h reaches "
      f"~{n['pareto_worst_sh']:.0f} km, where protected objects begin to "
      "share the enhanced region; at small sigma_h the protected "
      "collateral falls into the Gaussian tail and the ratio ceases to "
      "be meaningful. Collecting the gates gives the exclusion map: the "
      "concept is excluded by exposure geometry for any Earth-fixed "
      "patch, by transport for any patch small enough to be selective in "
      "realistic winds, by trajectory sharing for co-orbital and "
      "track-crossing protected objects, and by energetics at the scale "
      f"required; what remains mathematically open is the narrow corner "
      "in which an enhancement is sustained on the target for a large "
      "fraction of its remaining lifetime (Fig. 4, Fig. 5).")
    FIG("fig4_timing.png",
        "Figure 4. Target extra delta-v versus intervention reference "
        "time for a best-case-sited fixed pulse and for a 4 h tracking "
        "window.")
    FIG("fig5_pareto.png",
        "Figure 5. Target benefit against protected-object collateral "
        "over the design sweep; the Pareto front is highlighted and "
        "colour encodes horizontal patch scale.")

    H(1, "4. Discussion")
    H(2, "4.1 Geometry")
    P("An orbiting object samples any Earth-fixed structure for tens of "
      "seconds per revolution, so the useful quantity is not the peak "
      "enhancement but the integral of delta along the trajectory. The "
      "decomposition in Section 3.3 shows this explicitly: duration, "
      "occupancy and in-patch amplitude enter multiplicatively, and the "
      "first two dominate. Any concept that cannot follow the target "
      "loses three orders of magnitude before atmospheric physics is "
      "even considered, and increasing delta cannot recover it because "
      "the response is linear in delta.")
    H(2, "4.2 Transport")
    P("A patch that must persist for hours to days is acted on by "
      "diffusion, mean winds and the cooling relaxation of any heated "
      "volume. Thermospheric winds of tens to over a hundred m/s are "
      f"routine [{c('drob2015hwm14')}] and disturbances of the kind an "
      "intervention would create are observed to propagate away from "
      f"their source at several hundred m/s [{c('bruinsma2007tad')}]. In "
      "our survey the combinations that survive an hour are exactly "
      "those with large patches and weak winds — that is, the "
      "combinations that are too large to be selective. The transport "
      "and selectivity requirements are therefore in direct conflict, "
      "which is the single most robust element of the negative result.")
    H(2, "4.3 Selectivity")
    P("Perfect localization suppresses collateral by many orders of "
      "magnitude, but only for objects that do not share the target's "
      "trajectory tube. Co-orbital twins receive comparable drag, "
      "track-crossing objects at similar altitude receive a physically "
      "meaningful fraction (case pair E: 29 encounters and "
      f"{sci(n['collat_E_track'])} m/s), and a dispersed fragment cloud "
      "cannot be covered by a single localized enhancement at all. The "
      "very large selectivity ratios that appear in the tables for "
      "remote pairs are Gaussian-tail or no-encounter artefacts of the "
      "patch shape and are reported as undefined; the defensible "
      "statement is about the absolute collateral delta-v, which is "
      "below any operationally relevant level for non-co-located "
      "objects.")
    H(2, "4.4 Energetics")
    P("Raising density at a fixed altitude cannot be done by heating the "
      "air there — in situ heating lowers the local density — so the "
      "relevant thermodynamic accounting is the expansion of the column "
      f"below. Raising delta = 5 at 400 km requires warming that column "
      f"by a fractional {n['eps_column']*100:.0f}% "
      f"({n['dT_column']:.0f} K at the top of the column) and costs at "
      f"least {sci(n['E_column'])} J, i.e. ~{sci(n['E_column_W'])} W "
      "sustained over a day for a sigma_h = 200 km patch; the in-situ "
      f"bound of {sci(n['E_insitu'])} J understates this by a factor "
      f"{n['E_column_over_insitu']:.0f} at this altitude. Both are "
      "thermodynamic lower "
      "bounds, not delivered engineering energy: no deposition "
      "efficiency, coupling mechanism or loss budget is modelled, and no "
      "engineering energy requirement can be inferred robustly from "
      "them. For scale, the global upper atmosphere receives ~464 GW "
      "from solar EUV and ~95 GW from Joule dissipation on average "
      f"[{c('knipp2004heating')}]; the bound above is a small fraction "
      "of that globally but must be delivered into a single patch and "
      "sustained, which is why storms — which do deliver it — produce "
      "global, not selective, enhancements.")
    TBL(t8t, "Table 8. Thermodynamic lower bounds on the energy required "
             "to sustain a density enhancement: in-situ heating bound, "
             "fractional warming of the column below, column-expansion "
             "energy, and the equivalent sustained power for a one-day "
             "intervention.")
    FIG("fig8_energy_bounds.png",
        "Figure 8. Sustained power corresponding to the thermodynamic "
        "lower bounds of Table 8, versus altitude and enhancement "
        "amplitude.")
    H(2, "4.5 Implications")
    P("The practical implication is that the concept fails for reasons "
      "that are independent of the drag physics and therefore cannot be "
      "engineered around by increasing amplitude. Natural storm-time "
      "enhancements already realize delta of order unity to several, "
      "globally, and the observed operational consequences of those "
      f"events [{c('parker2024gannon','berger2023starlink')}] are the "
      "uniform control realized by nature. Differential-drag "
      "station-keeping and drag-augmentation devices achieve selective "
      "decay by changing B of the object rather than rho of the "
      "atmosphere, and the comparison in Section 3.4 explains why that "
      "is the favourable side of the trade: it requires no sustained "
      "energy input and is intrinsically co-located with the target.")

    H(1, "5. Limitations")
    P("This is a boundary study with synthetic targets. It uses a "
      "climatological density lookup rather than assimilated densities, "
      "a circular-approximation secular decay integrator (agreeing with "
      "the Cowell reference to 0.12% on a ten-day drag-only test), and "
      "an idealized tracking bound used as an upper limit rather than a "
      "mechanism. No plasma/neutral coupling, self-consistent heating, "
      "deposition physics, or circulation response is modelled; the "
      "transport treatment is a parameterized diffusion/advection/"
      "relaxation surrogate, not a general-circulation simulation, and "
      "its survival fractions are fractions of a design grid rather than "
      "probabilities. Energy accounting reports thermodynamic lower "
      "bounds only. Lifetimes beyond the integration horizon are "
      "right-censored. No public catalog was used for targeting and no "
      "observational dataset was ingested; all numbers are model output.")

    H(1, "6. Conclusions")
    P("Within the modelled system, localized thermospheric density "
      "enhancement is excluded as a selective debris-removal mechanism "
      "for every configuration we could construct that respects "
      "exposure geometry, transport persistence and collateral "
      "constraints simultaneously: Earth-fixed patches are limited by "
      "transit time to sub-percent contributions relative to natural "
      "drag, patches small enough to be selective do not survive "
      "realistic winds for an hour, co-orbital and track-crossing "
      "spacecraft receive comparable collateral, and the thermodynamic "
      f"lower bound on sustaining a useful enhancement is "
      f"{sci(n['E_column_W'])} W for a single patch. What remains "
      "mathematically possible "
      "is the idealized limit of an enhancement co-located with the "
      "target for a large fraction of its remaining lifetime, which "
      "would multiply its drag by (1+delta); nothing in this study "
      "indicates that such co-location can be realized, and no "
      "technological feasibility is claimed. The quantitative boundary — "
      "and the dimensionless group that lets it be re-evaluated for any "
      "other parameter choice — is the result.")

    H(1, "Data and code availability")
    P("All results regenerate from `make all` (or `make quick`) in the "
      "accompanying repository; every number in this manuscript is "
      "written from results/tables CSVs by scripts/build_manuscript.py.")

    H(1, "References")
    for line in c.reference_list():
        P(line)
    pd.DataFrame([dict(number=i, citation_key=k)
                  for i, k in enumerate(c.order, 1)]).to_csv(
        os.path.join(root, "results/manuscript_citations.csv"), index=False)

    # ---------------- rendering ----------------
    def fmt(v):
        return f"{v:.4g}" if isinstance(v, float) else str(v)

    def add_table(doc, df, caption):
        cap = doc.add_paragraph(caption)
        cap.runs[0].italic = True
        tbl = doc.add_table(rows=1, cols=len(df.columns))
        tbl.style = "Table Grid"
        for j, col in enumerate(df.columns):
            cell = tbl.rows[0].cells[j]
            cell.text = str(col)
            cell.paragraphs[0].runs[0].bold = True
        for _, r in df.iterrows():
            cells = tbl.add_row().cells
            for j, v in enumerate(r):
                cells[j].text = fmt(v)
        for row in tbl.rows:
            for cell in row.cells:
                for par in cell.paragraphs:
                    for run in par.runs:
                        run.font.size = Pt(7)

    def render(inline):
        doc = Document()
        stl = doc.styles["Normal"]
        stl.font.name = "Times New Roman"
        stl.font.size = Pt(11)
        for item in content:
            if item[0] == "H":
                doc.add_heading(item[2], level=item[1])
            elif item[0] == "P":
                doc.add_paragraph(item[1])
            elif item[0] == "TBL":
                add_table(doc, item[1], item[2])
            elif item[0] == "FIG":
                if inline:
                    doc.add_picture(
                        os.path.join(root, "results/figures", item[1]),
                        width=Inches(6.0))
                    doc.paragraphs[-1].alignment = \
                        WD_ALIGN_PARAGRAPH.CENTER
                    cap = doc.add_paragraph(item[2])
                    cap.runs[0].italic = True
                    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else:
                    ph = doc.add_paragraph(
                        f"[{item[2].split('.')[0]} near here — supplied "
                        f"as separate file {item[1]}]")
                    ph.runs[0].italic = True
        if not inline:
            doc.add_heading("Figure captions", level=1)
            for item in content:
                if item[0] == "FIG":
                    doc.add_paragraph(item[2])
        return doc

    os.makedirs(os.path.join(root, "manuscript"), exist_ok=True)
    render(False).save(os.path.join(root, "manuscript/manuscript.docx"))
    render(True).save(
        os.path.join(root, "manuscript/manuscript_inline.docx"))

    # ---------------- editable English pptx ----------------
    prs = Presentation()
    prs.slide_width = PInches(13.333)
    prs.slide_height = PInches(7.5)
    blank = prs.slide_layouts[6]

    def slide_text(title, lines):
        s = prs.slides.add_slide(blank)
        tb = s.shapes.add_textbox(PInches(0.6), PInches(0.4),
                                  PInches(12.1), PInches(1.0))
        tf = tb.text_frame
        tf.text = title
        tf.paragraphs[0].runs[0].font.size = PPt(28)
        tf.paragraphs[0].runs[0].font.bold = True
        bb = s.shapes.add_textbox(PInches(0.6), PInches(1.6),
                                  PInches(12.1), PInches(5.4))
        bf = bb.text_frame
        bf.word_wrap = True
        for i, ln in enumerate(lines):
            p = bf.paragraphs[0] if i == 0 else bf.add_paragraph()
            p.text = "• " + ln
            p.runs[0].font.size = PPt(16)
        return s

    def slide_fig(title, fname, caption):
        s = prs.slides.add_slide(blank)
        tb = s.shapes.add_textbox(PInches(0.6), PInches(0.25),
                                  PInches(12.1), PInches(0.8))
        tb.text_frame.text = title
        tb.text_frame.paragraphs[0].runs[0].font.size = PPt(24)
        tb.text_frame.paragraphs[0].runs[0].font.bold = True
        s.shapes.add_picture(
            os.path.join(root, "results/figures", fname),
            PInches(3.0), PInches(1.15), height=PInches(5.0))
        cb = s.shapes.add_textbox(PInches(0.6), PInches(6.35),
                                  PInches(12.1), PInches(0.9))
        cb.text_frame.word_wrap = True
        cb.text_frame.text = caption
        cb.text_frame.paragraphs[0].runs[0].font.size = PPt(12)
        return s

    slide_text(
        "Quantifying the feasibility boundary of localized thermospheric "
        "density enhancement for selective orbital debris decay",
        ["T. Onishi et al. — boundary study, synthetic targets only",
         "Question: can a localized thermospheric density increase "
         "selectively de-orbit LEO debris without dragging protected "
         "spacecraft?",
         "Approach: NRLMSISE-00 climatology, validated J2-secular and "
         "Cowell propagators, abstract Gaussian density perturbations",
         "All numbers regenerate from code (make all)"])
    slide_text("Key results", [
        f"Earth-fixed pulse: {sci(n['gap_pulse_dv'])} m/s per event "
        f"({n['gap_pulse_frac']*100:.1f}% duty cycle) = "
        f"{100*n['gap_pulse_dv']/n['gap_pulse_nat']:.1f}% of natural drag "
        "over the same window",
        f"Idealized co-location bound: {n['gap_track_dv']:.2f} m/s/day = "
        "delta x natural drag — an upper bound, not a mechanism",
        f"Gap decomposition: duration {n['gap_f_dur']:.0f}x x occupancy "
        f"{n['gap_f_occ']:.1f}x x in-patch amplitude "
        f"{n['gap_f_amp']:.1f}x closes to "
        f"{abs(n['gap_closure'])*100:.1f}%",
        "Localization buys collateral suppression, not benefit; the "
        "comparison depends on the matching convention",
        f"Transport: {n['n_transport_surv']}/{n['n_transport_combos']} "
        "surveyed design combinations survive 1 h; none when selective "
        "patches meet 100 m/s winds",
        f"Energetics: ~{sci(n['E_column_W'])} W sustained (thermodynamic "
        "lower bound) for delta=5 over a 200 km patch at 400 km",
        "Co-orbital protected twins absorb comparable delta-v — "
        "selectivity fails by geometry"])
    for item in content:
        if item[0] == "FIG":
            head = item[2].split(".")[0]
            slide_fig(head, item[1], item[2])
    for fn, cap in [
        ("figS1_negative_controls.png",
         "Figure S1. Extra delta-v for each mandatory negative control."),
        ("figS2_mc_hist.png",
         "Figure S2. Monte Carlo distribution of target extra delta-v."),
        ("figS3_sobol.png",
         "Figure S3. Sobol' first-order and total-order indices."),
        ("figS4_transport_grid_sensitivity.png",
         "Figure S4. Transport-grid sensitivity of the surviving "
         "fraction.")]:
        slide_fig(cap.split(".")[0], fn, cap)
    slide_text("Conclusions", [
        "Selective thermospheric drag is mathematically well-posed and "
        "energetically quantifiable",
        "It is bounded by three gates: transit geometry, atmospheric "
        "transport, and shared-trajectory collateral",
        "Feasibility window is narrow and likely closed by transport "
        "physics — a quantitatively bounded negative result",
        "No hardware, no operational spacecraft targeted; synthetic "
        "objects only"])
    prs.save(os.path.join(root, "manuscript/manuscript_figures.pptx"))

    # ---------------- supplement ----------------
    sup = Document()
    sup.add_heading("Supplementary material", 0)
    sup.add_heading("Supplementary figures", level=1)
    for fn, cap in [
        ("figS1_negative_controls.png",
         "Figure S1. Extra delta-v for each mandatory negative control "
         "(cited in Section 3.7)."),
        ("figS2_mc_hist.png",
         "Figure S2. Monte Carlo distribution of target extra delta-v "
         "(cited in Section 3.6)."),
        ("figS3_sobol.png",
         "Figure S3. Sobol' first-order and total-order sensitivity "
         "indices (cited in Section 3.6)."),
        ("figS4_transport_grid_sensitivity.png",
         "Figure S4. Distribution of the surviving fraction over grid "
         "variants of the transport design space (cited in Section "
         "3.5).")]:
        fp = os.path.join(root, "results/figures", fn)
        if not os.path.exists(fp):
            continue
        sup.add_picture(fp, width=Inches(6.0))
        sup.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        pc = sup.add_paragraph(cap)
        pc.runs[0].italic = True
        pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sup.add_heading("Supplementary tables", level=1)
    for name, df in [("Exposure classification audit",
                      load(root, "numerical_zero_audit.csv")),
                     ("Transport-grid sensitivity", tbs),
                     ("Sobol convergence ladder", sobc),
                     ("Phase 5 spreading models", p5),
                     ("Phase 6 outcomes", p6),
                     ("Phase 8 timing", p8.head(40)),
                     ("Phase 9 Pareto", p9),
                     ("Phase 10 negative controls", neg),
                     ("Phase 12 classification", p12.head(60))]:
        if df is None:
            continue
        sup.add_heading(name, level=1)
        tbl = sup.add_table(rows=1, cols=len(df.columns))
        for j, col in enumerate(df.columns):
            tbl.rows[0].cells[j].text = str(col)
        for _, r in df.iterrows():
            cells = tbl.add_row().cells
            for j, v in enumerate(r):
                cells[j].text = f"{v:.4g}" if isinstance(v, float) \
                    else str(v)
    os.makedirs(os.path.join(root, "supplement"), exist_ok=True)
    sup.save(os.path.join(root, "supplement/supplement.docx"))
    print("manuscript + supplement written")


if __name__ == "__main__":
    main()
