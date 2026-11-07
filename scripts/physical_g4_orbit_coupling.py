"""Gate 4: couple GITM control/perturbed density and winds to synthetic orbits.

usage: python3 scripts/physical_g4_orbit_coupling.py <label> [<label> ...]
Reads data/physical/processed/<label>_slices.npz (written by physical_g3_paired.py),
appends rows to results/physical_model_vs_prescribed_patch.csv and writes
results/tables/physical_g4_<label>_objects.csv.

Synthetic, abstract objects only (no real spacecraft). Circular orbits with J2
secular rates (same model as src/orbits/fastprop.py, vectorised for e = 0).
Extra drag dv = int (rho_p |v_rel,p|^2 - rho_c |v_rel,c|^2) / (2B) dt.
"""
from __future__ import annotations

import csv
import datetime as dt
import os
import sys

import numpy as np
from scipy.interpolate import RegularGridInterpolator

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.orbits.elements import MU, OMEGA_E, R_EARTH  # noqa: E402
from src.orbits.fastprop import j2_secular_rates, decay_lifetime, init_elements  # noqa: E402
from src.atmosphere.lookup import build_lookup, rho_fn_from_lookup  # noqa: E402
from src.utils import load_config  # noqa: E402

R_GITM = 6372.0e3
T0 = dt.datetime(2002, 3, 21)
ALTS = (300.0, 400.0, 500.0)
INCS = (30.0, 50.0, 70.0, 97.0)
N_PER = 64
B_REF = 30.0           # kg m^-2, config drag.b_cases.typical_debris
FINE_DT = 10.0
SEED = 20261107


def gmst_rad(t: dt.datetime) -> float:
    jd = 2440587.5 + t.replace(tzinfo=dt.timezone.utc).timestamp() / 86400.0
    return np.radians((280.46061837 + 360.98564736629 * (jd - 2451545.0)) % 360.0)


def grid_interp(t, lon, lat, alt, arr, log, method):
    lon_e = np.concatenate([lon[-1:] - 360.0, lon, lon[:1] + 360.0])
    a = np.concatenate([arr[:, -1:], arr, arr[:, :1]], axis=1).astype(np.float64)
    if log:
        a = np.log(a)
    f = RegularGridInterpolator((t, lon_e, lat, alt), a, method=method, bounds_error=False, fill_value=None)

    def ev(tq, lonq, latq, altq):
        pts = np.stack([tq, np.mod(lonq, 360.0), np.clip(latq, lat[0], lat[-1]), altq], -1)
        v = f(pts)
        return np.exp(v) if log else v
    return ev


def orbits(rng):
    objs = []
    for h in ALTS:
        for inc in INCS:
            for _ in range(N_PER):
                objs.append((h, inc, rng.uniform(0, 2 * np.pi), rng.uniform(0, 2 * np.pi)))
    return np.array(objs)


def states(obj, t):
    h, inc, raan0, u0 = obj[:, 0:1], np.radians(obj[:, 1:2]), obj[:, 2:3], obj[:, 3:4]
    a = R_EARTH + h * 1e3
    rd, ad, md = j2_secular_rates(a, 0.0, inc)
    raan = raan0 + rd * t[None, :]
    u = u0 + (ad + md) * t[None, :]
    cO, sO, ci, si = np.cos(raan), np.sin(raan), np.cos(inc), np.sin(inc)
    cu, su = np.cos(u), np.sin(u)
    P = np.stack([cO, sO, np.zeros_like(cO)], -1)
    Q = np.stack([-ci * sO, ci * cO, si * np.ones_like(cO)], -1)
    r = a[..., None] * (cu[..., None] * P + su[..., None] * Q)
    v = np.sqrt(MU / a)[..., None] * (-su[..., None] * P + cu[..., None] * Q)
    return r, v, a[:, 0]


def geo(r, t, th0):
    th = th0 + OMEGA_E * t[None, :]
    x = np.cos(th) * r[..., 0] + np.sin(th) * r[..., 1]
    y = -np.sin(th) * r[..., 0] + np.cos(th) * r[..., 1]
    rm = np.linalg.norm(r, axis=-1)
    return np.degrees(np.arcsin(r[..., 2] / rm)), np.degrees(np.arctan2(y, x)), rm, th


def wind_eci(lat, lon, th, ve, vn, vu):
    la, lo = np.radians(lat), np.radians(lon)
    e = np.stack([-np.sin(lo), np.cos(lo), 0 * lo], -1)
    n = np.stack([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)], -1)
    up = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)
    w = ve[..., None] * e + vn[..., None] * n + vu[..., None] * up
    c, s = np.cos(th), np.sin(th)
    return np.stack([c * w[..., 0] - s * w[..., 1], s * w[..., 0] + c * w[..., 1], w[..., 2]], -1)


def fit_patch(d, lon, lat, alt_idx):
    """Static Gaussian fitted to the GITM d rho/rho field (time of peak) at one altitude."""
    k = np.argmax(np.abs(d[:, :, :, alt_idx]).reshape(d.shape[0], -1).max(1))
    f = d[k, :, :, alt_idx]
    i, j = np.unravel_index(np.argmax(f), f.shape)
    dmax = float(f[i, j])
    wA = np.cos(np.radians(lat))[None, :] * np.ones((lon.size, 1))
    cell = (np.radians(lon[1] - lon[0]) * np.radians(lat[1] - lat[0]) * (R_GITM + 0) ** 2) * wA
    area = float(cell[f > dmax * np.exp(-0.5)].sum())
    sig = np.sqrt(area / np.pi) / 1e3
    series = np.abs(d[:, :, :, alt_idx]).reshape(d.shape[0], -1).max(1)
    return dict(dmax=dmax, lat=float(lat[j]), lon=float(lon[i]), sigma_h_km=sig, k_peak=int(k), series=series)


def run(label, rows_out, obj_rows):
    z = np.load(f"data/physical/processed/{label}_slices.npz")
    t, lon, lat, alt = z["t_s"].astype(float), z["lon_deg"], z["lat_deg"], z["alt_km"]
    heat = z["heating"]
    p0, lat0, lon0, z0, sig_h, sig_z, t_on, dur = heat[:8]
    rng = np.random.default_rng(SEED)
    obj = orbits(rng)
    tq = np.arange(t[0] + FINE_DT / 2, t[-1], FINE_DT)
    th0 = gmst_rad(T0)
    r, v, a = states(obj, tq)
    la, lo, rm, th = geo(r, tq, th0)
    T = np.broadcast_to(tq[None, :], la.shape)
    omega_x_r = np.stack([-OMEGA_E * r[..., 1], OMEGA_E * r[..., 0], 0 * r[..., 2]], -1)
    v_corot = v - omega_x_r
    lon360 = np.mod(lo, 360.0)
    dist = (R_EARTH / 1e3) * np.arccos(np.clip(
        np.sin(np.radians(lat0)) * np.sin(np.radians(la)) + np.cos(np.radians(lat0)) * np.cos(np.radians(la))
        * np.cos(np.radians(lo - lon0)), -1, 1))
    on = (T >= t_on) & (T <= t_on + dur)
    target = (np.where(on, dist, np.inf).min(1) <= sig_h)
    d_rel = z["p_rho"].astype(float) / z["c_rho"].astype(float) - 1.0
    variants = {
        "nominal": dict(method="linear", alt_ref=R_GITM, winds=True, tstride=1),
        "no_winds": dict(method="linear", alt_ref=R_GITM, winds=False, tstride=1),
        "nearest_interp": dict(method="nearest", alt_ref=R_GITM, winds=True, tstride=1),
        "alt_ref_6378km": dict(method="linear", alt_ref=R_EARTH, winds=True, tstride=1),
        "dt_1200s": dict(method="linear", alt_ref=R_GITM, winds=True, tstride=2),
    }
    out = {}
    for name, vv in variants.items():
        s = slice(None, None, vv["tstride"])
        altq = (rm - vv["alt_ref"]) / 1e3
        res = {}
        for tag in ("c", "p"):
            rho = grid_interp(t[s], lon, lat, alt, z[f"{tag}_rho"][s], True, vv["method"])(T, lon360, la, altq)
            vr = v_corot.copy()
            if vv["winds"]:
                w = [grid_interp(t[s], lon, lat, alt, z[f"{tag}_{c}"][s], False, vv["method"])(T, lon360, la, altq)
                     for c in ("ve", "vn", "vu")]
                vr = vr - wind_eci(la, lon360, th, *w)
            res[tag] = rho * np.sum(vr ** 2, -1) / (2 * B_REF)
        out[name] = dict(extra=(res["p"] - res["c"]).sum(1) * FINE_DT, natural=res["c"].sum(1) * FINE_DT)
    # prescribed static Gaussian comparator fitted to GITM at each object altitude
    altq = (rm - R_GITM) / 1e3
    rho_c = grid_interp(t, lon, lat, alt, z["c_rho"], True, "linear")(T, lon360, la, altq)
    acc_c = rho_c * np.sum(v_corot ** 2, -1) / (2 * B_REF)
    presc = np.zeros(obj.shape[0])
    fits = {}
    for h in ALTS:
        ia = int(np.argmin(np.abs(alt - (h + (R_EARTH - R_GITM) / 1e3))))
        fp = fit_patch(d_rel, lon, lat, ia)
        fits[h] = fp
        ser = fp["series"]
        above = np.where(ser >= 0.5 * ser.max())[0]
        half = 0.5 * float(np.median(np.diff(t)))
        w0, w1 = t[above[0]] - half, t[above[-1]] + half
        m = obj[:, 0] == h
        dd = (R_EARTH / 1e3) * np.arccos(np.clip(
            np.sin(np.radians(fp["lat"])) * np.sin(np.radians(la[m])) + np.cos(np.radians(fp["lat"]))
            * np.cos(np.radians(la[m])) * np.cos(np.radians(lo[m] - fp["lon"])), -1, 1))
        delta = fp["dmax"] * np.exp(-dd ** 2 / (2 * fp["sigma_h_km"] ** 2)) * ((T[m] >= w0) & (T[m] <= w1))
        presc[m] = (acc_c[m] * delta).sum(1) * FINE_DT
        fp.update(w0=float(w0), w1=float(w1))
    nom = out["nominal"]
    for k in range(obj.shape[0]):
        obj_rows.append(dict(label=label, obj=k, alt_km=obj[k, 0], inc_deg=obj[k, 1], target=bool(target[k]),
                             natural_dv_ms=nom["natural"][k], gitm_extra_dv_ms=nom["extra"][k],
                             prescribed_extra_dv_ms=presc[k],
                             **{f"extra_dv_{n}": out[n]["extra"][k] for n in variants if n != "nominal"}))
    cfg = load_config()
    lut = build_lookup(cfg["atmosphere"]["regimes"])
    rho_bg = rho_fn_from_lookup(lut, "moderate")
    t_max = cfg["orbits"]["lifetime_criterion"]["max_years"] * 365.25 * 86400
    for h in ALTS:
        m = obj[:, 0] == h
        a0 = R_EARTH + h * 1e3
        vc = np.sqrt(MU / a0)
        el = init_elements(a0, 0.0, np.radians(50.0), 0.0, 0.0, 0.0)
        L0, _ = decay_lifetime(el, rho_bg, B_REF, t_max)
        for grp, gm in (("target", m & target), ("nontarget", m & ~target), ("all", m)):
            if gm.sum() == 0:
                continue
            row = dict(label=label, P0_W=p0, z0_km=z0, sigma_h_km=sig_h, duration_s=dur, alt_km=h, group=grp,
                       n_objects=int(gm.sum()), B_kg_m2=B_REF,
                       natural_dv_12h_mean=float(nom["natural"][gm].mean()),
                       gitm_extra_dv_mean=float(nom["extra"][gm].mean()),
                       gitm_extra_dv_median=float(np.median(nom["extra"][gm])),
                       gitm_extra_dv_max=float(nom["extra"][gm].max()),
                       gitm_extra_dv_min=float(nom["extra"][gm].min()),
                       prescribed_extra_dv_mean=float(presc[gm].mean()),
                       prescribed_extra_dv_max=float(presc[gm].max()),
                       ratio_gitm_to_prescribed_mean=float(nom["extra"][gm].mean() / presc[gm].mean())
                       if presc[gm].mean() != 0 else np.nan,
                       fit_dmax=fits[h]["dmax"], fit_sigma_h_km=fits[h]["sigma_h_km"],
                       fit_lat=fits[h]["lat"], fit_lon=fits[h]["lon"],
                       fit_window_s=f"{fits[h]['w0']:.0f}-{fits[h]['w1']:.0f}")
            for n in variants:
                if n != "nominal":
                    row[f"gitm_extra_dv_mean_{n}"] = float(out[n]["extra"][gm].mean())
            da = -2 * a0 * row["gitm_extra_dv_mean"] / vc
            el1 = init_elements(a0 + da, 0.0, np.radians(50.0), 0.0, 0.0, 0.0)
            L1, _ = decay_lifetime(el1, rho_bg, B_REF, t_max)
            row.update(delta_a_m=da, lifetime_base_d=L0, lifetime_after_d=L1, delta_lifetime_d=L1 - L0,
                       lifetime_censored=bool(L0 >= t_max / 86400 - 1))
            rows_out.append(row)
            print(label, h, grp, f"{row['gitm_extra_dv_mean']:.3e}", f"{row['prescribed_extra_dv_mean']:.3e}",
                  flush=True)


def main():
    rows, objr = [], []
    for label in sys.argv[1:]:
        run(label, rows, objr)
        with open(f"results/tables/physical_g4_{label}_objects.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(objr[0]))
            w.writeheader()
            w.writerows([o for o in objr if o["label"] == label])
    out = "results/physical_model_vs_prescribed_patch.csv"
    old = list(csv.DictReader(open(out))) if os.path.exists(out) else []
    old = [o for o in old if o["label"] not in sys.argv[1:]]
    allr = old + rows
    keys = list(rows[0])
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(allr)
    print("wrote", out, len(allr))


if __name__ == "__main__":
    main()
