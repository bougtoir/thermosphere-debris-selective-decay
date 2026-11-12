"""Independent semantic checks of the principal estimands (Acta final delta, Gate 12).

Recomputes each estimand from a lower-level canonical output or from a synthetic field with a known answer, and
compares with the value used in the manuscript. No GITM run; reads results/ and data/physical/processed/.
Writes results/tables/acta_semantic_checks.csv and exits non-zero on any FAIL.
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from physical_g3r_spread import alt_interp, cell_area_unit, coarsen  # noqa: E402


def rd(x):
    return pd.read_csv(os.path.join(ROOT, x))


rows = []


def chk(area, name, expected, got, tol, note=""):
    ok = bool(np.isclose(got, expected, rtol=tol, atol=0)) if tol is not None else bool(got)
    rows.append(dict(area=area, check=name, expected=expected, got=got, rel_tol=tol, result="PASS" if ok else "FAIL",
                     note=note))


vals = rd("results/manuscript_physical_values.csv").set_index("name").value

# 1 density anomaly sign and normalization
z = np.load(os.path.join(ROOT, "data/physical/processed/p11_z300_fine12_slices.npz"))
t_on = float(z["heating"][6]) - float(z["t_case0_s"])
k = int(np.argmin(np.abs(z["t_s"] - t_on - 3000)))
P = alt_interp(z["p_rho"], z["alt_km"], 400.0, log=True)[k]
C = alt_interp(z["c_rho"], z["alt_km"], 400.0, log=True)[k]
rel = P / C - 1
lon, lat = z["lon_deg"], z["lat_deg"]
i0, j0 = np.unravel_index(np.argmax(rel), rel.shape)
chk("1 anomaly", "Δρ/ρ = ρ_heated/ρ_control − 1 > 0 at the 50 min maximum", 1,
    float(rel.max() > 0), None)
chk("1 anomaly", "50 min maximum lies within 15° lat of the 45°N source", 1, float(abs(lat[j0] - 45) <= 15), None,
    f"lat={lat[j0]:.1f}")
chk("1 anomaly", "Fig. 1 panel maximum (recomputed) vs ledger", float(vals["fig1_max_drho_rel"]),
    float(rel.max()), 1e-6)

# 2 heating power and energy: cosine ramps of TRamp on a TDur window -> E = P0 (TDur - TRamp)
P0, TDur, TRamp = 1e11, 3600.0, 600.0
tt = np.linspace(0, TDur, 360001)
Pt = np.full_like(tt, P0)
Pt[tt < TRamp] = P0 * 0.5 * (1 - np.cos(np.pi * tt[tt < TRamp] / TRamp))
m = tt > TDur - TRamp
Pt[m] = P0 * 0.5 * (1 - np.cos(np.pi * (TDur - tt[m]) / TRamp))
E_hand = float(np.sum((Pt[1:] + Pt[:-1]) / 2 * np.diff(tt)))
ts = rd("results/tables/physical_g3_p11_z300r_timeseries.csv") if os.path.exists(
    os.path.join(ROOT, "results/tables/physical_g3_p11_z300r_timeseries.csv")) else rd(
    "results/tables/physical_g3_p11_z300_timeseries.csv")
chk("2 heating", "hand-integrated taper energy = P0 (TDur − TRamp)", P0 * (TDur - TRamp), E_hand, 1e-6)
chk("2 heating", "GITM cumulative deposited energy vs hand value", E_hand, float(ts.E_cum_J.max()), 0.01)
f = rd("results/tables/physical_g3r_realized_forcing.csv")
for _, q in f.iterrows():
    chk("2 heating", f"realized grid power {q.label}", q.P0_W, q.realized_power_W, 0.01)

# 3 area weighting
for nlon, nlat in ((36, 36), (72, 72)):
    lo = (np.arange(nlon) + 0.5) * 360 / nlon
    la = -90 + (np.arange(nlat) + 0.5) * 180 / nlat
    w = cell_area_unit(lo, la)
    chk("3 area", f"cell solid angles sum to 4π ({nlon}x{nlat})", 4 * np.pi, float(w.sum()), 1e-6)
    # participation area of a uniform positive anomaly on a polar cap equals the cap fraction
    pos = np.where(la[None, :] > 30, 1.0, 0.0) * np.ones((nlon, 1))
    mp = (pos * w).sum()
    pa = mp ** 2 / (pos ** 2 * w).sum() / w.sum()
    chk("3 area", f"participation area of uniform cap = cap area fraction ({nlon}x{nlat})",
        float((w * (pos > 0)).sum() / w.sum()), float(pa), 1e-9)

# 4 fine-to-coarse remap conserves the area integral
lo = (np.arange(72) + 0.5) * 5
la = -90 + (np.arange(72) + 0.5) * 2.5
w = cell_area_unit(lo, la)
rng = np.random.default_rng(1)
fld = rng.random((1, 72, 72, 1))
cf, lo2, la2, w2 = coarsen(fld, lo, la, 2, w)
chk("4 remap", "2×2 area-weighted remap conserves ∫f dA", float((fld[0, :, :, 0] * w).sum()),
    float((cf[0, :, :, 0] * w2).sum()), 1e-9)
chk("4 remap", "remapped grid is 36×36", 36 * 36, float(cf[0, :, :, 0].size), 0)

# 5-7 target classification, cumulative Δv, selectivity (object-level recomputation)
ob = rd("results/tables/physical_g4_p11_z300_objects.csv")
ev = rd("results/tables/physical_g4t_selectivity_evolution.csv")
for h in (300, 400, 500):
    o = ob[ob.alt_km == h]
    x = ev[(ev.label == "p11_z300") & (ev.grid == "36x36") & (ev.alt_km == h)].sort_values("t_after_onset_s").iloc[-1]
    chk("5 targets", f"n_target {h} km (objects file vs evolution table)", float(x.n_target), float(o.target.sum()), 0)
    s_obj = o[o.target].gitm_extra_dv_ms.mean() / o[~o.target].gitm_extra_dv_ms.mean()
    chk("7 selectivity", f"S(12 h) {h} km = mean target / mean non-target extra Δv", float(x.selectivity_mean),
        float(s_obj), 0.02, "evolution table integrates to the last 10-min output; objects file to case end")
    sh = o[~o.target].gitm_extra_dv_ms.sum() / o.gitm_extra_dv_ms.sum()
    chk("7 selectivity", f"non-target share {h} km is a share of the total, not a ratio of means",
        float(x.nontarget_share_of_total_extra), float(sh), 0.02)
# 6 drag formula: a = ρ |v_rel|^2 / (2B), Δv = Σ a dt  (hand value for a 7.67 km/s object)
rho, v, B, dt = 3e-12, 7670.0, 30.0, 10.0
chk("6 Δv", "hand drag acceleration ρv²/(2B) for ρ=3e-12, v=7.67 km/s, B=30", 2.94e-6, rho * v ** 2 / (2 * B), 0.01)
pm = rd("results/physical_model_vs_prescribed_patch.csv")
pm = pm[(pm.label == "p11_z300") & (pm.group != "all")]
for h in (400, 500):
    a = pm[pm.alt_km == h].set_index("group")
    s_nom = a.loc["target", "gitm_extra_dv_mean"] / a.loc["nontarget", "gitm_extra_dv_mean"]
    s_nw = a.loc["target", "gitm_extra_dv_mean_no_winds"] / a.loc["nontarget", "gitm_extra_dv_mean_no_winds"]
    chk("6 Δv", f"wind term changes S by ≤ ledger orbit sensitivity at {h} km (bounds comparator wind asymmetry)",
        1, float(100 * abs(s_nw / s_nom - 1) <= float(vals["orbit_sensitivity_max_pct"])
                 if "orbit_sensitivity_max_pct" in vals else abs(s_nw / s_nom - 1) <= 0.05), None,
        f"|ΔS/S|={100 * abs(s_nw / s_nom - 1):.2f}%")

# 8 Gaussian comparators: both exceed GITM in all 9 grid-altitude cells at 12 h except where reported otherwise
g = rd("results/tables/physical_g4t_gaussian_matching.csv")
for _, q in g.iterrows():  # every comparator variant, incl. sensitivity scans
    recomputed = q.target_dv_mean / q.nontarget_dv_mean
    chk("8 Gaussian", f"{q.grid} {q.alt_km:.0f} km {q.comparator}: S = target/non-target", q.selectivity_mean,
        recomputed, 1e-9)
g = g[g.grid.str.endswith("tmax43200") & g.comparator.isin(["peak_matched_fit", "source_centred_sigma_src_peak_amp"])]
r = g.selectivity_mean / g.gitm_selectivity_mean
chk("8 Gaussian", "Fig. 4 cells: 2 comparators × 3 grids × 3 altitudes at 12 h", 18, float(len(g)), 0)
for h in (400, 500):
    chk("8 Gaussian", f"both Fig. 4 comparators exceed GITM S at {h} km", 1, float((r[g.alt_km == h] > 1).all()), None,
        f"min ratio {r[g.alt_km == h].min():.2f}")

# 9 bootstrap units
bs = rd("results/tables/physical_selectivity_bootstrap.csv")
for _, q in bs.iterrows():
    chk("9 bootstrap", f"{q.label} {q.alt_km:.0f} km CI brackets point estimate", 1,
        float(q.ci95_lo <= q.selectivity <= q.ci95_hi), None, f"n_boot={q.n_boot}, units=objects")

# 10 coarse/fine
sc = ev[(ev.label == "p11_z300") & (ev.grid == "36x36")].groupby("alt_km").tail(1).set_index("alt_km").selectivity_mean
sf = ev[(ev.label == "p11_z300_fine12") & (ev.grid == "72x72")].groupby("alt_km").tail(1).set_index(
    "alt_km").selectivity_mean
d = max(100 * abs(sf[h] / sc[h] - 1) for h in (400.0, 500.0))
chk("10 grids", "max 12 h fine/coarse S difference at 400/500 km vs ledger",
    float(vals["S12_fine_vs_coarse_max_diff_400_500_pct"]), float(d), 1e-9)

# 11 frozen predictions
po = rd("results/tables/physical_prediction_outcomes.csv")
chk("11 predictions", "every outcome has a verdict", 1, float(po.verdict.notna().all()), None,
    str(po.verdict.value_counts().to_dict()))

out = pd.DataFrame(rows)
out.to_csv(os.path.join(ROOT, "results/tables/acta_semantic_checks.csv"), index=False)
print(out[["area", "check", "expected", "got", "result", "note"]].to_string())
sys.exit(int((out.result == "FAIL").any()))
