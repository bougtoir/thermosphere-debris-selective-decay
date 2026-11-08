"""G3R: coarse vs fine grid comparison over the common window.

usage: python3 scripts/physical_g3r_grid.py <coarse_label> <fine_label> [tmax_s]
Requires (all generated beforehand):
  results/tables/physical_g3r_spread_metrics.csv  rows for coarse (36x36), fine native and fine remapped_2
  results/threshold_sensitivity.csv              same grids
  results/orbit_interpolation_sensitivity.csv     nominal rows with grid tags "<grid>_tmax<tmax>"
  results/tables/physical_g3_<label>_timeseries.csv for both labels (native-grid extremes of T, winds, O/N2)
Writes results/grid_sensitivity_metrics.csv: one row per metric x altitude with coarse, fine_native,
fine_remapped values, A = fine_remapped/coarse - 1 (model discretization) and
B = fine_native/fine_remapped - 1 (diagnostic grid).
"""
import sys

import numpy as np
import pandas as pd

coarse, fine = sys.argv[1:3]
tmax = float(sys.argv[3]) if len(sys.argv) > 3 else 10800.0
SP = pd.read_csv("results/tables/physical_g3r_spread_metrics.csv")
TH = pd.read_csv("results/threshold_sensitivity.csv")
OI = pd.read_csv("results/orbit_interpolation_sensitivity.csv")


def pick(df, lab, kind):
    q = df[df.label == lab]
    if kind == "remapped":
        return q[q.grid.str.startswith("remapped_")]
    return q[~q.grid.str.startswith("remapped_")]


SETS = {"coarse": (coarse, "native"), "fine_native": (fine, "native"), "fine_remapped": (fine, "remapped")}
rows = []


def add(metric, alt, vals, note=""):
    c, fn, fr = (vals.get(k, np.nan) for k in ("coarse", "fine_native", "fine_remapped"))
    rows.append(dict(metric=metric, alt_km=alt, coarse=c, fine_native=fn, fine_remapped=fr,
                     A_model_discretization_rel=fr / c - 1 if np.isfinite(fr) and c else np.nan,
                     B_diagnostic_grid_rel=fn / fr - 1 if np.isfinite(fr) and fr else np.nan,
                     fine_native_vs_coarse_rel=fn / c - 1 if c else np.nan, note=note))


for alt in (300.0, 400.0, 500.0):
    v = {}
    for name, (lab, kind) in SETS.items():
        q = pick(SP, lab, kind)
        v[name] = q[(q.alt_km == alt) & (q.t_after_onset_s > 0)]
    common_t = set.intersection(*[set(np.round(q.t_after_onset_s / 60).astype(int)) for q in v.values()])
    for name in v:
        v[name] = v[name][np.round(v[name].t_after_onset_s / 60).astype(int).isin(common_t)]
    for m, f in (("peak_drho_rel_max", lambda q: q.peak_drho_rel.max()),
                 ("t_of_peak_after_onset_s", lambda q: q.t_after_onset_s.values[q.peak_drho_rel.values.argmax()]),
                 ("min_drho_rel_min", lambda q: q.min_drho_rel.min()),
                 ("mean_drho_rel_max", lambda q: q.mean_drho_rel.max()),
                 ("int_drho_kg_m_max", lambda q: q.int_drho_kg_m.max()),
                 ("int_neg_drho_kg_m_min", lambda q: q.int_neg_drho_kg_m.min()),
                 ("participation_area_frac_end", lambda q: q.participation_area_frac.values[-1]),
                 ("radius_of_gyration_km_end", lambda q: q.radius_of_gyration_km.values[-1]),
                 ("rg_growth_ms_mean_after_30min",
                  lambda q: np.polyfit(q.t_after_onset_s[q.t_after_onset_s >= 1800],
                                       q.radius_of_gyration_km[q.t_after_onset_s >= 1800] * 1e3, 1)[0]),
                 ("centroid_lat_deg_end", lambda q: q.centroid_lat_deg.values[-1]),
                 ("centroid_lon_deg_end", lambda q: q.centroid_lon_deg.values[-1]),
                 ("centroid_dist_from_source_km_end", lambda q: q.centroid_dist_from_source_km.values[-1]),
                 ("max_abs_dvh_ms_max", lambda q: q.max_abs_dvh_ms.max()),
                 ("anomaly_wt_abs_dvh_ms_max", lambda q: q.anomaly_wt_abs_dvh_ms.max())):
        add(m, alt, {k: float(f(q)) for k, q in v.items() if len(q)},
            "common snapshots after onset (fine run ends at tmax case time)")
    for thr in (0.005, 0.01, 0.02, 0.05, 0.10):
        vals = {}
        for name, (lab, kind) in SETS.items():
            q = pick(TH, lab, kind)
            q = q[(q.alt_km == alt) & (q.threshold == thr) & (q.t_after_onset_s > 0)
                  & (np.round(q.t_after_onset_s / 60).astype(int).isin(common_t))]
            if len(q):
                vals[name] = float(q.area_frac_pos.max())
        add(f"area_frac_pos_gt_{thr:g}_max", alt, vals)
    tag = f"_tmax{int(tmax)}"
    for m in ("target_dv_mean", "nontarget_dv_mean", "selectivity_mean", "selectivity_median"):
        vals = {}
        for name, (lab, kind) in SETS.items():
            q = OI[(OI.label == lab) & (OI.variant == "nominal") & (OI.alt_km == alt) & (OI.target_radius_sigma == 1.0)
                   & OI.grid.str.endswith(tag)]
            q = q[q.grid.str.startswith("remapped_")] if kind == "remapped" else q[~q.grid.str.startswith("remapped_")]
            if len(q):
                vals[name] = float(q[m].iloc[0])
        add(f"orbit_{m}", alt, vals, f"orbit coupling over the first {tmax / 3600:g} h of the case")
for alt in (300.0, 400.0, 500.0):
    vals = {}
    for name, lab in (("coarse", coarse), ("fine_native", fine)):
        ts = pd.read_csv(f"results/tables/physical_g3_{lab}_timeseries.csv")
        vals[name] = ts
    for m in ("max_dT_K", "max_dvh_ms", "max_abs_dvu_ms", "min_dOn2_rel"):
        out = {}
        for k, ts in vals.items():
            q = ts[(ts.alt_km == alt) & (ts.t_s <= tmax + 1)]
            out[k] = float(q[m].min() if m.startswith("min") else q[m].max())
        add(f"native_extreme_{m}", alt, out, "grid-point extreme on each native grid; not remappable from slices")
pd.DataFrame(rows).to_csv("results/grid_sensitivity_metrics.csv", index=False)
print(pd.DataFrame(rows).round(4).to_string())
