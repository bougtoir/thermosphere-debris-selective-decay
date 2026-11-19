"""G4T: why the 400-km peak-matched Gaussian comparison changes sign between grids.

usage: python3 scripts/physical_g4t_gaussian_decomposition.py <coarse_label> <fine_label> [tmax_s]
Recomputes the static peak-matched Gaussian comparator of physical_g3r_orbit_sensitivity.py while swapping
one fit ingredient at a time (centre, sigma, time window, control drag used as weight) between the coarse
fit, the fine fit and fixed references. Amplitude cancels in the selectivity ratio, so it is not varied.
Also evaluates a sub-grid centre (anomaly-weighted centroid of the cells above dmax*exp(-1/2)), which is not
quantized to a grid cell like the argmax centre. No atmospheric simulation is rerun.
Writes results/tables/physical_g4t_gaussian_decomposition.csv.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import physical_g3r_orbit_sensitivity as osn  # noqa: E402
import physical_g4_orbit_coupling as g4  # noqa: E402
from src.orbits.elements import R_EARTH  # noqa: E402


def subgrid_centre(d, lon, lat, k, ia):
    f = d[k, :, :, ia]
    thr = f.max() * np.exp(-0.5)
    LA, LO = np.meshgrid(lat, lon)
    w = np.where(f > thr, f, 0.0) * np.cos(np.radians(LA))
    x = (w * np.cos(np.radians(LA)) * np.cos(np.radians(LO))).sum()
    y = (w * np.cos(np.radians(LA)) * np.sin(np.radians(LO))).sum()
    zc = (w * np.sin(np.radians(LA))).sum()
    return float(np.degrees(np.arctan2(zc, np.hypot(x, y)))), float(np.degrees(np.arctan2(y, x)))


def prep(label, coarsen, tmax):
    os.environ["G3R_TMAX_S"] = str(tmax)
    os.environ["G3R_COARSEN"] = str(coarsen)
    z, grid = osn.load(label)
    G = osn.geometry(z, 10.0)
    heat = z["heating"]
    p0, lat0, lon0, z0, sig_h, sig_z, t_on, dur = heat[:8]
    t_on = t_on - float(z["t_case0_s"])
    altq = (G["rm"] - g4.R_GITM) / 1e3
    kw = dict(method="linear", winds=True, log=True, tsnap=False, lon_shift=0)
    args = (G["t"], G["T"], G["lon360"], G["la"], altq, G["v_corot"], G["th"])
    ac = osn.drag_acc(z, "c", *args, **kw)
    ap = osn.drag_acc(z, "p", *args, **kw)
    on = (G["T"] >= t_on) & (G["T"] <= t_on + dur)
    dmin = np.where(on, osn.gc_km(lat0, lon0, G["la"], G["lo"]), np.inf).min(1)
    tg = dmin <= sig_h
    d = z["p_rho"].astype(float) / z["c_rho"].astype(float) - 1.0
    lon, lat, alt = z["lon_deg"], z["lat_deg"], z["alt_km"]
    fits = {}
    for h in g4.ALTS:
        ia = int(np.argmin(np.abs(alt - (h + (R_EARTH - g4.R_GITM) / 1e3))))
        fp = g4.fit_patch(d, lon, lat, ia)
        ser, t = fp["series"], G["t"]
        above = np.where(ser >= 0.5 * ser.max())[0]
        half = 0.5 * float(np.median(np.diff(t)))
        sc = subgrid_centre(d, lon, lat, fp["k_peak"], ia)
        fits[h] = dict(lat=fp["lat"], lon=fp["lon"], sigma=fp["sigma_h_km"], w0=t[above[0]] - half,
                       w1=t[above[-1]] + half, sub_lat=sc[0], sub_lon=sc[1])
    return dict(grid=grid, G=G, ac=ac, extra=(ap - ac).sum(1) * 10.0, tg=tg, fits=fits, src=(lat0, lon0))


def sel(P, h, acc_from, lat_c, lon_c, sg, w0, w1):
    G = P["G"]
    m = G["obj"][:, 0] == h
    T = G["T"][m]
    shape = np.exp(-osn.gc_km(lat_c, lon_c, G["la"][m], G["lo"][m]) ** 2 / (2 * sg ** 2)) * ((T >= w0) & (T <= w1))
    ex = (acc_from["ac"][m] * shape).sum(1)
    tg = P["tg"][m]
    return float(ex[tg].mean() / ex[~tg].mean())


def main():
    cl, fl = sys.argv[1:3]
    tmax = float(sys.argv[3]) if len(sys.argv) > 3 else 10800.0
    C = prep(cl, 1, tmax)
    runs = {"fine_native": prep(fl, 1, tmax), "fine_remapped": prep(fl, 2, tmax)}
    rows = []
    for h in g4.ALTS:
        fc = C["fits"][h]
        gc = float(C["extra"][C["G"]["obj"][:, 0] == h][C["tg"][C["G"]["obj"][:, 0] == h]].mean()
                   / C["extra"][C["G"]["obj"][:, 0] == h][~C["tg"][C["G"]["obj"][:, 0] == h]].mean())
        rows.append(dict(alt_km=h, run="coarse", variant="own_fit", centre_lat=fc["lat"], centre_lon=fc["lon"],
                         sigma_km=fc["sigma"], window_s=f"{fc['w0']:.0f}-{fc['w1']:.0f}",
                         gaussian_selectivity=sel(C, h, C, fc["lat"], fc["lon"], fc["sigma"], fc["w0"], fc["w1"]),
                         gitm_selectivity=gc))
        rows.append(dict(alt_km=h, run="coarse", variant="subgrid_centre", centre_lat=fc["sub_lat"],
                         centre_lon=fc["sub_lon"], sigma_km=fc["sigma"], window_s=f"{fc['w0']:.0f}-{fc['w1']:.0f}",
                         gaussian_selectivity=sel(C, h, C, fc["sub_lat"], fc["sub_lon"], fc["sigma"], fc["w0"],
                                                  fc["w1"]), gitm_selectivity=gc))
        for name, F in runs.items():
            ff = F["fits"][h]
            m = F["G"]["obj"][:, 0] == h
            gf = float(F["extra"][m][F["tg"][m]].mean() / F["extra"][m][~F["tg"][m]].mean())
            same_time = C["G"]["T"].shape == F["G"]["T"].shape and np.allclose(C["G"]["T"], F["G"]["T"])
            V = {"own_fit": (F, ff["lat"], ff["lon"], ff["sigma"], ff["w0"], ff["w1"]),
                 "coarse_centre": (F, fc["lat"], fc["lon"], ff["sigma"], ff["w0"], ff["w1"]),
                 "coarse_sigma": (F, ff["lat"], ff["lon"], fc["sigma"], ff["w0"], ff["w1"]),
                 "coarse_window": (F, ff["lat"], ff["lon"], ff["sigma"], fc["w0"], fc["w1"]),
                 "coarse_centre_sigma_window": (F, fc["lat"], fc["lon"], fc["sigma"], fc["w0"], fc["w1"]),
                 "subgrid_centre": (F, ff["sub_lat"], ff["sub_lon"], ff["sigma"], ff["w0"], ff["w1"]),
                 "source_centre": (F, *C["src"], ff["sigma"], ff["w0"], ff["w1"])}
            if same_time:
                V["all_coarse_incl_control_drag"] = (C, fc["lat"], fc["lon"], fc["sigma"], fc["w0"], fc["w1"])
            for v, (acc, la_, lo_, sg, w0, w1) in V.items():
                rows.append(dict(alt_km=h, run=name, variant=v, centre_lat=la_, centre_lon=lo_, sigma_km=sg,
                                 window_s=f"{w0:.0f}-{w1:.0f}",
                                 gaussian_selectivity=sel(F, h, acc, la_, lo_, sg, w0, w1), gitm_selectivity=gf))
        print(h, flush=True)
    df = pd.DataFrame(rows)
    df["gitm_over_gaussian"] = df.gitm_selectivity / df.gaussian_selectivity
    df.insert(0, "tmax_s", tmax)
    out = "results/tables/physical_g4t_gaussian_decomposition.csv"
    if os.path.exists(out):
        old = pd.read_csv(out)
        df = pd.concat([old[old.tmax_s != tmax], df], ignore_index=True)
    df.to_csv(out, index=False)
    print("wrote", out)


if __name__ == "__main__":
    main()
