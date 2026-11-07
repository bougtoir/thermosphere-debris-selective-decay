"""Gate 3: paired control/perturbed GITM diagnostics.

usage: python3 scripts/physical_g3_paired.py <control_run> <perturbed_run> <label>
Writes results/tables/physical_g3_<label>_timeseries.csv and
data/physical/processed/<label>_slices.npz (rho/winds 200-700 km, both runs).
"""
from __future__ import annotations

import csv
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "physical", "gitm"))
import gitm_io  # noqa: E402

R_E = 6372.0e3   # GITM ModEarth R_Earth [m]
KB = 1.380649e-23
ALTS = (150.0, 200.0, 300.0, 400.0, 500.0)
MONO = ("[O(!U3!NP)", "[N(!U4!NS)", "[He", "[N(!U2!ND)", "[N(!U2!NP)", "[H]", "[O(!U1!ND)")
DIAT = ("[O!D2!N", "[N!D2!N", "[NO]")


def var(s, start):
    for k, v in s.items():
        if isinstance(k, str) and k.replace(" ", "").startswith(start.replace(" ", "")):
            return v
    raise KeyError(start)


def interp(field, z, zz):
    i = np.searchsorted(z, zz)
    w = (zz - z[i - 1]) / (z[i] - z[i - 1])
    return (1 - w) * field[:, :, i - 1] + w * field[:, :, i]


def geometry(s):
    lon, lat, z = np.radians(s["lon_deg"]), np.radians(s["lat_deg"]), s["alt_km"] * 1e3
    dz = np.gradient(z)
    dl, dp = np.gradient(lon).mean(), np.gradient(lat).mean()
    r = R_E + z
    return (r[None, None, :] ** 2 * np.cos(lat)[None, :, None] * dl * dp * dz[None, None, :]
            * np.ones((lon.size, 1, 1)))


def enthalpy(s):
    n = sum(2.5 * var(s, k) for k in MONO) + sum(3.5 * var(s, k) for k in DIAT)
    return KB * s["Temperature"] * n   # J m^-3


def gc_km(lat0, lon0, lat, lon, z0):
    a, b = np.radians(lat0), np.radians(lon0)
    la, lo = np.radians(lat)[None, :], np.radians(lon)[:, None]
    c = np.sin(a) * np.sin(la) + np.cos(a) * np.cos(la) * np.cos(lo - b)
    return (R_E / 1e3 + z0) * np.arccos(np.clip(c, -1, 1))


def main():
    cdir, pdir, label = sys.argv[1:4]
    heat = json.load(open(os.path.join(pdir, "case_manifest.json")))["case"]["heating"] \
        if os.path.exists(os.path.join(pdir, "case_manifest.json")) else \
        [float(x) for x in open(os.path.join(pdir, "UA/DataIn/user_heating.in")).read().split()]
    p0, lat0, lon0, z0 = heat[:4]
    elog = np.loadtxt(os.path.join(pdir, "UA/data/user_heating_log.dat")) if p0 > 0 else None
    cs = {os.path.basename(p): p for p in gitm_io.snapshots(os.path.join(cdir, "UA/data"))}
    ps = {os.path.basename(p): p for p in gitm_io.snapshots(os.path.join(pdir, "UA/data"))}
    keys = sorted(set(cs) & set(ps))
    rows, slab = [], {}
    t_first = None
    for k in keys:
        c, p = gitm_io.read_snapshot(cs[k]), gitm_io.read_snapshot(ps[k])
        h = c["header"]
        tsec = h["Hour"] * 3600 + h["Minute"] * 60 + h["Second"] + 86400 * (h["Day"] - 21)
        t_first = tsec if t_first is None else t_first
        z, lon, lat = c["alt_km"], c["lon_deg"], c["lat_deg"]
        dV = geometry(c)
        dH = float(((enthalpy(p) - enthalpy(c)) * dV).sum())
        dM_above = {}
        for zz in (300.0, 400.0):
            m = z >= zz
            dM_above[zz] = float(((p["Rho"] - c["Rho"]) * dV)[:, :, m].sum())
        ecum = 0.0
        if elog is not None and elog.size:
            sel = elog[elog[:, 0] <= tsec - t_first + 1e-6]
            ecum = float(sel[-1, 3]) if len(sel) else 0.0
        wA = np.cos(np.radians(lat))[None, :] * np.ones((lon.size, 1))
        for zz in ALTS:
            rc, rp = interp(c["Rho"], z, zz), interp(p["Rho"], z, zz)
            d = (rp - rc) / rc
            tc, tp = interp(c["Temperature"], z, zz), interp(p["Temperature"], z, zz)
            ve = interp(var(p, "V!Dn!N(east)") - var(c, "V!Dn!N(east)"), z, zz)
            vn = interp(var(p, "V!Dn!N(north)") - var(c, "V!Dn!N(north)"), z, zz)
            vu = interp(var(p, "V!Dn!N(up)") - var(c, "V!Dn!N(up)"), z, zz)
            on2c = interp(var(c, "[O(!U3!NP)") / var(c, "[N!D2!N"), z, zz)
            on2p = interp(var(p, "[O(!U3!NP)") / var(p, "[N!D2!N"), z, zz)
            dist = gc_km(lat0, lon0, lat, lon, zz)
            i, j = np.unravel_index(np.argmax(np.abs(d)), d.shape)
            area = wA / wA.sum()
            far = dist > 3000.0
            rows.append(dict(
                snapshot=k, t_s=tsec - t_first, alt_km=zz, E_cum_J=ecum, dH_total_J=dH,
                dM_above300_kg=dM_above[300.0], dM_above400_kg=dM_above[400.0],
                max_abs_drho_rel=float(d[i, j]), lat_of_max=float(lat[j]), lon_of_max=float(lon[i]),
                dist_of_max_km=float(dist[i, j]), min_drho_rel=float(d.min()), max_drho_rel=float(d.max()),
                area_frac_gt_1pct=float(area[np.abs(d) > 0.01].sum()),
                area_frac_gt_0p1pct=float(area[np.abs(d) > 0.001].sum()),
                area_frac_neg_lt_m0p1pct=float(area[d < -0.001].sum()),
                global_mean_drho_rel=float((d * wA).sum() / wA.sum()),
                global_mean_drho_abs=float(((rp - rc) * wA).sum() / wA.sum()),
                remote_mean_abs_drho_rel=float((np.abs(d) * wA)[far].sum() / wA[far].sum()),
                remote_max_abs_drho_rel=float(np.abs(d)[far].max()),
                max_dT_K=float((tp - tc).max()), min_dT_K=float((tp - tc).min()),
                max_dvh_ms=float(np.hypot(ve, vn).max()), max_abs_dvu_ms=float(np.abs(vu).max()),
                dOn2_rel_at_max=float(on2p[i, j] / on2c[i, j] - 1),
                min_dOn2_rel=float((on2p / on2c - 1).min()), max_dOn2_rel=float((on2p / on2c - 1).max()),
            ))
        m = (z >= 200) & (z <= 700)
        for nm, s in (("c", c), ("p", p)):
            for v, key in (("rho", "Rho"), ("ve", "V!Dn!N(east)"), ("vn", "V!Dn!N(north)"), ("vu", "V!Dn!N(up)")):
                arr = s[key] if key == "Rho" else var(s, key)
                slab.setdefault(f"{nm}_{v}", []).append(arr[:, :, m].astype(np.float32))
        slab.setdefault("t_s", []).append(tsec - t_first)
        print(k, flush=True)
    os.makedirs("results/tables", exist_ok=True)
    out = f"results/tables/physical_g3_{label}_timeseries.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    os.makedirs("data/physical/processed", exist_ok=True)
    np.savez_compressed(f"data/physical/processed/{label}_slices.npz",
                        lon_deg=lon, lat_deg=lat, alt_km=z[m], heating=np.array(heat),
                        **{k2: np.array(v2) for k2, v2 in slab.items()})
    print("wrote", out)


if __name__ == "__main__":
    main()
