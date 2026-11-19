"""Gate 3 summary metrics per paired case from physical_g3_<label>_timeseries.csv.

usage: physical_g3_summary.py LABEL [LABEL ...]
Writes results/tables/physical_g3_summary.csv (one row per label and altitude).
Heating window is read from the matching processed slices file.
"""
import os
import sys

import numpy as np
import pandas as pd

OUT = "results/tables/physical_g3_summary.csv"


def efold(t, y, t_after):
    """Time after t_after for y to fall to 1/e of its post-t_after maximum (NaN if not reached)."""
    m = t >= t_after
    t, y = t[m], y[m]
    if len(y) == 0 or y.max() <= 0:
        return np.nan
    k = int(np.argmax(y))
    below = np.where(y[k:] <= y[k] / np.e)[0]
    return float(t[k + below[0]] - t[k]) if len(below) else np.nan


def main():
    rows = []
    for label in sys.argv[1:]:
        d = pd.read_csv(f"results/tables/physical_g3_{label}_timeseries.csv")
        z = np.load(f"data/physical/processed/{label}_slices.npz")
        heat = z["heating"]
        t_on = float(heat[6]) - float(z["t_case0_s"])
        t_off = t_on + float(heat[7])
        e_tot = d.E_cum_J.max()
        for alt, x in d.groupby("alt_km"):
            x = x.sort_values("t_s")
            t = x.t_s.values.astype(float)
            pk = int(np.argmax(x.max_drho_rel.values))
            first = x[x.E_cum_J > 0].iloc[0] if (x.E_cum_J > 0).any() else None
            rows.append(dict(
                label=label, P0_W=heat[0], z0_km=heat[3], sigma_h_km=heat[4], duration_s=heat[7], alt_km=alt,
                E_total_J=e_tot,
                closure_first_snapshot=float(first.dH_total_J / first.E_cum_J) if first is not None else np.nan,
                closure_end_heating=float(np.interp(t_off, t, x.dH_total_J) / e_tot) if e_tot > 0 else np.nan,
                closure_final=float(x.dH_total_J.iloc[-1] / e_tot) if e_tot > 0 else np.nan,
                peak_drho_rel=float(x.max_drho_rel.max()), t_peak_after_onset_s=float(t[pk] - t_on),
                dist_of_peak_km=float(x.dist_of_max_km.iloc[pk]),
                min_drho_rel=float(x.min_drho_rel.min()),
                efold_peak_after_off_s=efold(t, x.max_drho_rel.values, t_off),
                efold_globalmean_after_off_s=efold(t, x.global_mean_drho_rel.values, t_off),
                max_global_mean_drho_rel=float(x.global_mean_drho_rel.max()),
                final_global_mean_drho_rel=float(x.global_mean_drho_rel.iloc[-1]),
                max_area_frac_gt_1pct=float(x.area_frac_gt_1pct.max()),
                final_area_frac_gt_1pct=float(x.area_frac_gt_1pct.iloc[-1]),
                max_area_frac_neg=float(x.area_frac_neg_lt_m0p1pct.max()),
                max_remote_abs_drho_rel=float(x.remote_max_abs_drho_rel.max()),
                max_dT_K=float(x.max_dT_K.max()), min_dT_K=float(x.min_dT_K.min()),
                max_dvh_ms=float(x.max_dvh_ms.max()), max_abs_dvu_ms=float(x.max_abs_dvu_ms.max()),
                min_dOn2_rel=float(x.min_dOn2_rel.min()), max_dOn2_rel=float(x.max_dOn2_rel.max()),
                t_end_s=float(t[-1])))
    new = pd.DataFrame(rows)
    if os.path.exists(OUT):
        old = pd.read_csv(OUT)
        new = pd.concat([old[~old.label.isin(sys.argv[1:])], new])
    new.to_csv(OUT, index=False)
    print(new.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
