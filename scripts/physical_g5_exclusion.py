"""Gate 5 / candidate C5: energy-anchored comparison of the GITM-coupled drag
with the baseline (prescribed-field) outcomes.

usage: physical_g5_exclusion.py LABEL [LABEL ...]
Reads results/physical_model_vs_prescribed_patch.csv (B = B_kg_m2 there) and the
baseline results/tables/phase6_outcomes.csv (moderate regime, 400 km, case
A_target_highAm_400). Drag dv scales as 1/B, so GITM dv is rescaled to the
baseline object's B. Required energy assumes dv proportional to energy, which
is only defensible inside the tested range (checked with the 1e10/1e11 pair).
Writes results/tables/physical_g5_exclusion.csv.
"""
import sys

import numpy as np
import pandas as pd


def main():
    g = pd.read_csv("results/physical_model_vs_prescribed_patch.csv")
    base = pd.read_csv("results/tables/phase6_outcomes.csv")
    b = base[(base.regime == "moderate") & (base.case == "A_target_highAm_400")].set_index("scenario")
    b_obj = float(b.loc["tracking", "B"])
    rows = []
    for label in sys.argv[1:]:
        x = g[g.label == label]
        e = float(x.P0_W.iloc[0] * (x.duration_s.iloc[0] - 600.0))  # cosine ramps: 2 x half of 600 s lost
        for h, y in x.groupby("alt_km"):
            t = y[y.group == "target"].iloc[0]
            n = y[y.group == "nontarget"].iloc[0]
            a = y[y.group == "all"].iloc[0]
            scale = float(t.B_kg_m2) / b_obj
            dv_t = float(t.gitm_extra_dv_mean) * scale
            dv_n = float(n.gitm_extra_dv_mean) * scale
            v = np.sqrt(3.986004418e14 / (6378136.3 + h * 1e3))
            row = dict(label=label, alt_km=h, E_input_J=e, B_ref_kg_m2=b_obj,
                       target_dv_ms_at_Bref=dv_t, nontarget_dv_ms_at_Bref=dv_n,
                       selectivity_gitm=dv_t / dv_n,
                       nontarget_share_of_extra_drag=float(1 - t.gitm_extra_dv_mean * t.n_objects /
                                                           (a.gitm_extra_dv_mean * a.n_objects)),
                       target_dv_per_J=dv_t / e,
                       specific_orbital_energy_removed_J_per_kg=v * dv_t,
                       baseline_fixed_pulse_dv_ms=float(b.loc["fixed_pulse", "extra_deltav_ms"]),
                       baseline_tracking_dv_ms=float(b.loc["tracking", "extra_deltav_ms"]))
            row["gitm_over_baseline_fixed_pulse"] = dv_t / row["baseline_fixed_pulse_dv_ms"]
            row["E_for_baseline_tracking_dv_J_linear"] = row["baseline_tracking_dv_ms"] / row["target_dv_per_J"]
            row["equiv_continuous_power_1day_W_linear"] = row["E_for_baseline_tracking_dv_J_linear"] / 86400.0
            rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv("results/tables/physical_g5_exclusion.csv", index=False)
    print(out.T.to_string())


if __name__ == "__main__":
    main()
