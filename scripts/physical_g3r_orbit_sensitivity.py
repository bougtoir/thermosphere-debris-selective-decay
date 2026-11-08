"""G3R/G4T: orbital post-processing sensitivity and Gaussian-comparator matching criteria.

usage: python3 scripts/physical_g3r_orbit_sensitivity.py <label> [<label> ...]
Environment:
  G3R_TMAX_S=<s>   only use atmosphere output up to t_case <= value (for coarse vs 3-h fine-grid comparison)
  G3R_COARSEN=k    conservative k x k remap of the fields before coupling (diagnostic-grid test)
Reads data/physical/processed/<label>_slices.npz; no atmospheric simulation is rerun.
Writes/updates results/orbit_interpolation_sensitivity.csv and results/tables/physical_g4t_gaussian_matching.csv.
Object population, B, seed and target definition are identical to scripts/physical_g4_orbit_coupling.py.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import physical_g4_orbit_coupling as g4  # noqa: E402
from physical_g3r_spread import cell_area_unit, coarsen  # noqa: E402
from src.orbits.elements import OMEGA_E, R_EARTH  # noqa: E402

SIGMAS = (250.0, 500.0, 1000.0, 1500.0, 2000.0, 3000.0, 5000.0)
TGT_RADII = (0.5, 1.0, 2.0)


def gc_km(lat1, lon1, la, lo):
    return (R_EARTH / 1e3) * np.arccos(np.clip(
        np.sin(np.radians(lat1)) * np.sin(np.radians(la)) + np.cos(np.radians(lat1)) * np.cos(np.radians(la))
        * np.cos(np.radians(lo - lon1)), -1, 1))


def load(label):
    z = dict(np.load(f"data/physical/processed/{label}_slices.npz"))
    t = z["t_s"].astype(float)
    tmax = os.environ.get("G3R_TMAX_S")
    if tmax:
        m = t <= float(tmax) + 1.0
        for k in [k for k in z if k[:2] in ("c_", "p_")]:
            z[k] = z[k][m]
        z["t_s"] = z["t_s"][m]
    k = int(os.environ.get("G3R_COARSEN", "1"))
    grid = f"{z['lon_deg'].size}x{z['lat_deg'].size}"
    if k > 1:
        wsr = cell_area_unit(z["lon_deg"], z["lat_deg"])
        lon, lat = z["lon_deg"], z["lat_deg"]
        for key in [k2 for k2 in z if k2[:2] in ("c_", "p_")]:
            z[key], lo2, la2, _ = coarsen(z[key].astype(float), lon, lat, k, wsr)
        z["lon_deg"], z["lat_deg"] = lo2, la2
        grid = f"remapped_{k}_{lo2.size}x{la2.size}"
    if tmax:
        grid += f"_tmax{int(float(tmax))}"
    return z, grid


def drag_acc(z, tag, t, T, lon360, la, altq, v_corot, th, method="linear", winds=True, log=True,
             tsnap=False, lon_shift=0):
    lon, lat, alt = z["lon_deg"], z["lat_deg"], z["alt_km"]
    rho = z[f"{tag}_rho"].astype(float)
    W = [z[f"{tag}_{c}"].astype(float) for c in ("ve", "vn", "vu")]
    if lon_shift:
        # move the periodic seam: relabel grid AND query longitudes by the same offset (field unchanged)
        lon = np.mod(lon + lon_shift, 360.0)
        o = np.argsort(lon)
        lon, rho, W = lon[o], rho[:, o], [w[:, o] for w in W]
        lonq = np.mod(lon360 + lon_shift, 360.0)
    else:
        lonq = lon360
    Tq = T
    if tsnap:
        Tq = t[np.clip(np.searchsorted(t, T - 0.5 * np.diff(t).mean()), 0, t.size - 1)]
    if not log:
        f = g4.grid_interp(t, lon, lat, alt, rho, False, method)
    else:
        f = g4.grid_interp(t, lon, lat, alt, rho, True, method)
    r = f(Tq, lonq, la, altq)
    vr = v_corot
    if winds:
        w = [g4.grid_interp(t, lon, lat, alt, x, False, method)(Tq, lonq, la, altq) for x in W]
        vr = v_corot - g4.wind_eci(la, lon360, th, *w)
    return r * np.sum(vr ** 2, -1) / (2 * g4.B_REF)


def geometry(z, dt_orbit):
    t = z["t_s"].astype(float)
    obj = g4.orbits(np.random.default_rng(g4.SEED))
    tq = np.arange(t[0] + dt_orbit / 2, t[-1], dt_orbit)
    r, v, a = g4.states(obj, tq)
    la, lo, rm, th = g4.geo(r, tq, g4.gmst_rad(g4.T0))
    T = np.broadcast_to(tq[None, :], la.shape)
    omega_x_r = np.stack([-OMEGA_E * r[..., 1], OMEGA_E * r[..., 0], 0 * r[..., 2]], -1)
    return dict(obj=obj, t=t, tq=tq, la=la, lo=lo, rm=rm, th=th, T=T, lon360=np.mod(lo, 360.0),
                v_corot=v - omega_x_r)


def summarize(label, grid, variant, obj, extra, natural, targets, rows):
    for h in g4.ALTS:
        m = obj[:, 0] == h
        for rad, tg in targets.items():
            a, b = extra[m & tg], extra[m & ~tg]
            if a.size == 0 or b.size == 0:
                continue
            rows.append(dict(label=label, grid=grid, variant=variant, alt_km=h, target_radius_sigma=rad,
                             n_target=int(a.size), n_nontarget=int(b.size),
                             target_dv_mean=float(a.mean()), nontarget_dv_mean=float(b.mean()),
                             target_dv_median=float(np.median(a)), nontarget_dv_median=float(np.median(b)),
                             nontarget_dv_p95=float(np.percentile(b, 95)), nontarget_dv_max=float(b.max()),
                             selectivity_mean=float(a.mean() / b.mean()),
                             selectivity_median=float(np.median(a) / np.median(b)),
                             sum_extra_dv_all=float(extra[m].sum()),
                             natural_dv_mean=float(natural[m].mean())))


def run(label, rows, grows):
    z, grid = load(label)
    heat = z["heating"]
    p0, lat0, lon0, z0, sig_h, sig_z, t_on, dur = heat[:8]
    t_on = t_on - float(z["t_case0_s"])
    cache = {}
    variants = {
        "nominal": dict(dt=10.0),
        "orbit_dt_5s": dict(dt=5.0),
        "orbit_dt_30s": dict(dt=30.0),
        "cadence_1200s": dict(dt=10.0, tstride=2),
        "cadence_1800s": dict(dt=10.0, tstride=3),
        "nearest_space_time": dict(dt=10.0, method="nearest"),
        "nearest_time_only": dict(dt=10.0, tsnap=True),
        "linear_rho_not_log": dict(dt=10.0, log=False),
        "lon_seam_moved_93deg": dict(dt=10.0, lon_shift=93.0),
        "alt_ref_6378km": dict(dt=10.0, alt_ref=R_EARTH),
        "no_winds": dict(dt=10.0, winds=False),
    }
    only = os.environ.get("G3R_VARIANTS")
    if only:
        variants = {k: v for k, v in variants.items() if k == "nominal" or k in only.split(",")}
    for name, vv in variants.items():
        dto = vv.get("dt", 10.0)
        if dto not in cache:
            cache[dto] = geometry(z, dto)
        G = cache[dto]
        s = slice(None, None, vv.get("tstride", 1))
        zz = {k: (v[s] if k[:2] in ("c_", "p_") else v) for k, v in z.items()}
        t = G["t"][s]
        altq = (G["rm"] - vv.get("alt_ref", g4.R_GITM)) / 1e3
        kw = dict(method=vv.get("method", "linear"), winds=vv.get("winds", True), log=vv.get("log", True),
                  tsnap=vv.get("tsnap", False), lon_shift=vv.get("lon_shift", 0))
        ac = drag_acc(zz, "c", t, G["T"], G["lon360"], G["la"], altq, G["v_corot"], G["th"], **kw)
        ap = drag_acc(zz, "p", t, G["T"], G["lon360"], G["la"], altq, G["v_corot"], G["th"], **kw)
        extra, natural = (ap - ac).sum(1) * dto, ac.sum(1) * dto
        on = (G["T"] >= t_on) & (G["T"] <= t_on + dur)
        dmin = np.where(on, gc_km(lat0, lon0, G["la"], G["lo"]), np.inf).min(1)
        targets = {r: dmin <= r * sig_h for r in TGT_RADII}
        summarize(label, grid, name, G["obj"], extra, natural, targets, rows)
        if name == "nominal":
            nom = dict(extra=extra, ac=ac, targets=targets)
        print(label, grid, name, flush=True)
    # Gaussian comparators (static; idealized diagnostic baseline, not a realizable intervention)
    G = cache[10.0]
    t, la, lo, T, obj = G["t"], G["la"], G["lo"], G["T"], G["obj"]
    lon, lat, alt = z["lon_deg"], z["lat_deg"], z["alt_km"]
    d_rel = z["p_rho"].astype(float) / z["c_rho"].astype(float) - 1.0
    wsr = cell_area_unit(lon, lat)
    sp = pd.read_csv("results/tables/physical_g3r_spread_metrics.csv")
    for h in g4.ALTS:
        m = obj[:, 0] == h
        ia = int(np.argmin(np.abs(alt - (h + (R_EARTH - g4.R_GITM) / 1e3))))
        fp = g4.fit_patch(d_rel, lon, lat, ia)
        ser = fp["series"]
        above = np.where(ser >= 0.5 * ser.max())[0]
        half = 0.5 * float(np.median(np.diff(t)))
        w0, w1 = t[above[0]] - half, t[above[-1]] + half
        win = (T[m] >= w0) & (T[m] <= w1)
        acc = nom["ac"][m]
        gitm_all = float(nom["extra"][m].mean())
        # time-integrated excess mass per unit height at this altitude level (GITM), over the window
        r2 = (g4.R_GITM + alt[ia] * 1e3) ** 2
        drho = (z["p_rho"][:, :, :, ia].astype(float) - z["c_rho"][:, :, :, ia].astype(float))
        dtk = np.gradient(t)
        int_gitm = float((drho * wsr[None] * r2 * dtk[:, None, None]).sum())
        rho_c = z["c_rho"][:, :, :, ia].astype(float)
        sel = sp[(sp.label == label) & (sp.alt_km == h) & (sp.grid == f"{lon.size}x{lat.size}")]
        kpk = fp["k_peak"]
        tpk = t[kpk] - t_on
        srow = sel.iloc[(sel.t_after_onset_s - tpk).abs().argsort()[:1]] if len(sel) else None
        defs = {"peak_matched_fit": (fp["dmax"], fp["sigma_h_km"], fp["lat"], fp["lon"], "amp")}
        defs["source_centred_sigma_src_peak_amp"] = (fp["dmax"], sig_h, lat0, lon0, "amp")
        if srow is not None and len(srow) and np.isfinite(srow.radius_of_gyration_km.values[0]):
            defs["width_matched_rg_centroid"] = (fp["dmax"], float(srow.radius_of_gyration_km.values[0]) / np.sqrt(2),
                                                 float(srow.centroid_lat_deg.values[0]),
                                                 float(srow.centroid_lon_deg.values[0]), "amp")
        defs["integrated_density_matched_sigma_src"] = (None, sig_h, lat0, lon0, "int")
        defs["orbit_exposure_matched_sigma_src"] = (None, sig_h, lat0, lon0, "orbit")
        for s_ in SIGMAS:
            defs[f"sigma_scan_{int(s_)}km_source_centred"] = (fp["dmax"], s_, lat0, lon0, "amp")
        for name, (amp, sg, clat, clon, mode) in defs.items():
            shape = np.exp(-gc_km(clat, clon, la[m], lo[m]) ** 2 / (2 * sg ** 2)) * win
            unit = (acc * shape).sum(1) * 10.0
            if mode == "amp":
                A = amp
            elif mode == "orbit":
                A = gitm_all / unit.mean()
            else:
                LA, LO = np.meshgrid(lat, lon)
                gsh = np.exp(-gc_km(clat, clon, LA, LO) ** 2 / (2 * sg ** 2))
                wt = ((t >= w0) & (t <= w1)) * dtk
                A = int_gitm / float((rho_c * gsh[None] * wsr[None] * r2 * wt[:, None, None]).sum())
            ex = A * unit
            tg = nom["targets"][1.0][m]
            grows.append(dict(label=label, grid=grid, alt_km=h, comparator=name, amplitude=float(A), sigma_km=sg,
                              centre_lat=clat, centre_lon=clon, window_s=f"{w0:.0f}-{w1:.0f}",
                              target_dv_mean=float(ex[tg].mean()), nontarget_dv_mean=float(ex[~tg].mean()),
                              selectivity_mean=float(ex[tg].mean() / ex[~tg].mean()),
                              gitm_target_dv_mean=float(nom["extra"][m][tg].mean()),
                              gitm_nontarget_dv_mean=float(nom["extra"][m][~tg].mean()),
                              gitm_selectivity_mean=float(nom["extra"][m][tg].mean() / nom["extra"][m][~tg].mean()),
                              fit_lat_offset_from_source_deg=float(fp["lat"] - lat0)))


def update(path, new, labels, grids, key=None):
    df = pd.DataFrame(new)
    if os.path.exists(path):
        old = pd.read_csv(path)
        drop = old.label.isin(labels) & old.grid.isin(grids)
        if key:
            drop &= old[key].isin(df[key].unique())
        old = old[~drop]
        df = pd.concat([old, df], ignore_index=True)
    df.to_csv(path, index=False)


def main():
    rows, grows = [], []
    for label in sys.argv[1:]:
        run(label, rows, grows)
    grids = sorted({r["grid"] for r in rows})
    update("results/orbit_interpolation_sensitivity.csv", rows, sys.argv[1:], grids, key="variant")
    update("results/tables/physical_g4t_gaussian_matching.csv", grows, sys.argv[1:], grids)
    print("done", len(rows), len(grows))


if __name__ == "__main__":
    main()
