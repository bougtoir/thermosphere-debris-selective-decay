"""G4T: canonical power-effect-selectivity table and pairwise power-contrast ratios.

usage: python3 scripts/physical_g4t_tradeoff.py
Inputs (all generated): results/tables/physical_g3_summary.csv, results/physical_model_vs_prescribed_patch.csv,
results/tables/physical_g3r_spread_metrics.csv. Writes results/power_effect_selectivity.csv.
Statistic definitions: target/non-target extra delta-v = MEAN over objects of each group (median also given);
selectivity = mean(target) / mean(non-target); same 256-object population per shell, B = 30 kg m^-2,
evaluation window = full GITM run of the case (12 h for coarse-grid cases).
"""
import os

import numpy as np
import pandas as pd

R = os.path.join(os.path.dirname(__file__), "..")
S = pd.read_csv(os.path.join(R, "results/tables/physical_g3_summary.csv"))
C = pd.read_csv(os.path.join(R, "results/physical_model_vs_prescribed_patch.csv"))
SP = pd.read_csv(os.path.join(R, "results/tables/physical_g3r_spread_metrics.csv"))
rows = []
for (lab, h), c in C.groupby(["label", "alt_km"]):
    tg, nt = c[c.group == "target"].iloc[0], c[c.group == "nontarget"].iloc[0]
    s = S[(S.label == lab) & (S.alt_km == h)]
    if s.empty:
        continue
    s = s.iloc[0]
    sp = SP[(SP.label == lab) & (SP.alt_km == h) & (SP.grid == SP[SP.label == lab].grid.iloc[0])]
    E = float(s.E_total_J)
    rows.append(dict(
        label=lab, P0_W=float(tg.P0_W), z0_km=float(tg.z0_km), alt_km=h, E_input_J=E,
        target_dv_mean_ms=float(tg.gitm_extra_dv_mean), nontarget_dv_mean_ms=float(nt.gitm_extra_dv_mean),
        target_dv_median_ms=float(tg.gitm_extra_dv_median), nontarget_dv_median_ms=float(nt.gitm_extra_dv_median),
        selectivity_mean=float(tg.gitm_extra_dv_mean / nt.gitm_extra_dv_mean),
        selectivity_median=float(tg.gitm_extra_dv_median / nt.gitm_extra_dv_median),
        prescribed_selectivity_mean=float(tg.prescribed_extra_dv_mean / nt.prescribed_extra_dv_mean),
        target_dv_per_J=float(tg.gitm_extra_dv_mean) / E, nontarget_dv_per_J=float(nt.gitm_extra_dv_mean) / E,
        local_peak_drho_rel=float(s.peak_drho_rel), max_global_mean_drho_rel=float(s.max_global_mean_drho_rel),
        max_int_drho_kg_per_m=float(sp.int_drho_kg_m.max()),
        time_int_drho_kg_s_per_m=float(np.trapezoid(sp.int_drho_kg_m, sp.t_after_onset_s)),
        max_area_frac_abs_gt_1pct=float(s.max_area_frac_gt_1pct),
        participation_area_frac_at_peak_int=float(sp.participation_area_frac.values[np.nanargmax(sp.int_drho_kg_m)]),
        delta_lifetime_target_d=float(tg.delta_lifetime_d), lifetime_base_d=float(tg.lifetime_base_d),
        lifetime_censored=bool(tg.lifetime_censored), n_target=int(tg.n_objects), n_nontarget=int(nt.n_objects)))
T = pd.DataFrame(rows)
T["row_type"] = "case"
ratios = []
z300 = T[T.z0_km == 300.0]
labs = sorted(z300.label.unique(), key=lambda x: z300[z300.label == x].P0_W.iloc[0])
for lo_, hi_ in zip(labs[:-1], labs[1:]):
    for h in sorted(T.alt_km.unique()):
        a = T[(T.label == lo_) & (T.alt_km == h)].iloc[0]
        b = T[(T.label == hi_) & (T.alt_km == h)].iloc[0]
        r = dict(row_type="ratio_high_over_low", label=f"{hi_}/{lo_}", alt_km=h, P0_W=b.P0_W / a.P0_W,
                 E_input_J=b.E_input_J / a.E_input_J)
        for k in ("target_dv_mean_ms", "nontarget_dv_mean_ms", "target_dv_median_ms", "nontarget_dv_median_ms",
                  "target_dv_per_J", "nontarget_dv_per_J", "local_peak_drho_rel", "max_global_mean_drho_rel",
                  "max_int_drho_kg_per_m", "time_int_drho_kg_s_per_m", "max_area_frac_abs_gt_1pct"):
            r[k] = b[k] / a[k]
        r["selectivity_mean"] = b.selectivity_mean - a.selectivity_mean      # difference, not ratio
        r["selectivity_median"] = b.selectivity_median - a.selectivity_median
        r["prescribed_selectivity_mean"] = b.prescribed_selectivity_mean - a.prescribed_selectivity_mean
        ratios.append(r)
out = pd.concat([T, pd.DataFrame(ratios)], ignore_index=True)
out.to_csv(os.path.join(R, "results/power_effect_selectivity.csv"), index=False)
print(out.round(4).to_string())
