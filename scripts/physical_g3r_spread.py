"""G3R: threshold sensitivity, threshold-free spread metrics and anomaly-centroid transport.

usage: python3 scripts/physical_g3r_spread.py <label> [<label> ...]
Reads data/physical/processed/<label>_slices.npz. Environment:
  G3R_COARSEN=k   conservatively remap (area-weighted k x k cell means of rho) before differencing;
                  rows are tagged grid="<native>" or "remapped_k".
Writes/updates results/threshold_sensitivity.csv and results/tables/physical_g3r_spread_metrics.csv.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

R_E = 6372.0e3
ALTS = (300.0, 400.0, 500.0)
THRS = (0.005, 0.01, 0.02, 0.05, 0.10)


def edges(c):
    e = np.empty(c.size + 1)
    e[1:-1] = 0.5 * (c[1:] + c[:-1])
    e[0], e[-1] = c[0] - 0.5 * (c[1] - c[0]), c[-1] + 0.5 * (c[-1] - c[-2])
    return e


def cell_area_unit(lon, lat):
    le, pe = np.radians(edges(lon)), np.clip(np.radians(edges(lat)), -np.pi / 2, np.pi / 2)
    return np.diff(le)[:, None] * np.diff(np.sin(pe))[None, :]       # steradian


def coarsen(arr, lon, lat, k, wsr):
    """area-weighted k x k block mean over axes (lon, lat) = (-3, -2) for arr[t, lon, lat, alt]."""
    nt, nl, na, nz = arr.shape
    a = (arr * wsr[None, :, :, None]).reshape(nt, nl // k, k, na // k, k, nz).sum((2, 4))
    w = wsr.reshape(nl // k, k, na // k, k).sum((1, 3))
    return a / w[None, :, :, None], lon.reshape(-1, k).mean(1), lat.reshape(-1, k).mean(1), w


def alt_interp(f, z, zz, log=False):
    i = np.searchsorted(z, zz)
    w = (zz - z[i - 1]) / (z[i] - z[i - 1])
    if log:
        return np.exp((1 - w) * np.log(f[..., i - 1]) + w * np.log(f[..., i]))
    return (1 - w) * f[..., i - 1] + w * f[..., i]


def run(label, k):
    z = np.load(f"data/physical/processed/{label}_slices.npz")
    lon, lat, alt, t = z["lon_deg"], z["lat_deg"], z["alt_km"], z["t_s"].astype(float)
    heat = z["heating"]
    t_on = heat[6] - float(z["t_case0_s"])
    lat0, lon0 = heat[1], heat[2]
    wsr = cell_area_unit(lon, lat)
    rc, rp = z["c_rho"].astype(float), z["p_rho"].astype(float)
    ve, vn = z["p_ve"].astype(float), z["p_vn"].astype(float)
    dve, dvn = ve - z["c_ve"].astype(float), vn - z["c_vn"].astype(float)
    grid = f"{lon.size}x{lat.size}"
    if k > 1:
        rc, lo2, la2, w2 = coarsen(rc, lon, lat, k, wsr)
        rp = coarsen(rp, lon, lat, k, wsr)[0]
        ve, vn, dve, dvn = (coarsen(x, lon, lat, k, wsr)[0] for x in (ve, vn, dve, dvn))
        lon, lat, wsr = lo2, la2, w2
        grid = f"remapped_{k}_{lon.size}x{lat.size}"
    LO, LA = np.radians(lon)[:, None], np.radians(lat)[None, :]
    ux, uy, uz = np.cos(LA) * np.cos(LO), np.cos(LA) * np.sin(LO), np.sin(LA) * np.ones_like(LO)
    thr_rows, sp_rows = [], []
    for zz in ALTS:
        r = R_E + zz * 1e3
        dA = wsr * r ** 2
        A = dA.sum()
        C = alt_interp(rc, alt, zz, log=True)
        P = alt_interp(rp, alt, zz, log=True)
        VE, VN = alt_interp(ve, alt, zz), alt_interp(vn, alt, zz)
        DVE, DVN = alt_interp(dve, alt, zz), alt_interp(dvn, alt, zz)
        prev = None
        for it in range(t.size):
            d = P[it] / C[it] - 1
            dr = P[it] - C[it]
            tt = t[it] - t_on
            for th in THRS:
                thr_rows.append(dict(label=label, grid=grid, alt_km=zz, t_after_onset_s=tt, threshold=th,
                                     area_frac_pos=float(dA[d > th].sum() / A),
                                     area_frac_neg=float(dA[d < -th].sum() / A),
                                     area_frac_abs=float(dA[np.abs(d) > th].sum() / A)))
            pos = np.clip(dr, 0, None)
            mp = float((pos * dA).sum())
            row = dict(label=label, grid=grid, alt_km=zz, t_after_onset_s=tt,
                       mean_drho_rel=float((d * dA).sum() / A), mean_abs_drho_rel=float((np.abs(d) * dA).sum() / A),
                       int_drho_kg_m=float((dr * dA).sum()), int_abs_drho_kg_m=float((np.abs(dr) * dA).sum()),
                       int_pos_drho_kg_m=mp, int_neg_drho_kg_m=float((np.clip(dr, None, 0) * dA).sum()),
                       peak_drho_rel=float(d.max()), min_drho_rel=float(d.min()),
                       max_abs_dvh_ms=float(np.hypot(DVE[it], DVN[it]).max()))
            if mp > 0:
                # participation-ratio area of the positive anomaly (threshold-free spread)
                row["participation_area_frac"] = float(mp ** 2 / (pos ** 2 * dA).sum() / A)
                wt = pos * dA / mp
                cx, cy, cz = (wt * ux).sum(), (wt * uy).sum(), (wt * uz).sum()
                clat, clon = np.arctan2(cz, np.hypot(cx, cy)), np.arctan2(cy, cx)
                cosg = np.clip(np.sin(clat) * np.sin(LA) + np.cos(clat) * np.cos(LA) * np.cos(LO - clon), -1, 1)
                g = r * np.arccos(cosg)
                row.update(centroid_lat_deg=float(np.degrees(clat)), centroid_lon_deg=float(np.degrees(clon)),
                           radius_of_gyration_km=float(np.sqrt((wt * g ** 2).sum()) / 1e3),
                           anomaly_wt_vE_ms=float((wt * VE[it]).sum()), anomaly_wt_vN_ms=float((wt * VN[it]).sum()),
                           anomaly_wt_dvE_ms=float((wt * DVE[it]).sum()), anomaly_wt_dvN_ms=float((wt * DVN[it]).sum()),
                           anomaly_wt_abs_dvh_ms=float((wt * np.hypot(DVE[it], DVN[it])).sum()),
                           centroid_dist_from_source_km=float(r * np.arccos(np.clip(
                               np.sin(clat) * np.sin(np.radians(lat0)) + np.cos(clat) * np.cos(np.radians(lat0))
                               * np.cos(clon - np.radians(lon0)), -1, 1)) / 1e3))
                if prev is not None:
                    dt_ = tt - prev["t"]
                    pla, plo = prev["lat"], prev["lon"]
                    row["centroid_vE_ms"] = float(r * np.cos(0.5 * (clat + pla))
                                                  * (((clon - plo + np.pi) % (2 * np.pi)) - np.pi) / dt_)
                    row["centroid_vN_ms"] = float(r * (clat - pla) / dt_)
                    row["rg_growth_ms"] = float((row["radius_of_gyration_km"] - prev["rg"]) * 1e3 / dt_)
                prev = dict(t=tt, lat=clat, lon=clon, rg=row["radius_of_gyration_km"])
            sp_rows.append(row)
    return thr_rows, sp_rows


def update(path, new, labels, grids):
    df = pd.DataFrame(new)
    if os.path.exists(path):
        old = pd.read_csv(path)
        old = old[~(old.label.isin(labels) & old.grid.isin(grids))]
        df = pd.concat([old, df], ignore_index=True)
    df.to_csv(path, index=False)


def main():
    k = int(os.environ.get("G3R_COARSEN", "1"))
    thr, sp = [], []
    for label in sys.argv[1:]:
        a, b = run(label, k)
        thr += a
        sp += b
    grids = sorted({r["grid"] for r in thr})
    update("results/threshold_sensitivity.csv", thr, sys.argv[1:], grids)
    update("results/tables/physical_g3r_spread_metrics.csv", sp, sys.argv[1:], grids)
    print("rows", len(thr), len(sp), grids)


if __name__ == "__main__":
    main()
