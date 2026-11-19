"""Gate 2: GITM background checks (V2-V7) against NRLMSISE-00 for the same conditions.

usage: python3 scripts/physical_g2_validation.py <gitm_run_dir> [out_csv]
"""
from __future__ import annotations

import csv
import datetime as dt
import os
import sys

import numpy as np
import nrlmsise00

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "physical", "gitm"))
import gitm_io  # noqa: E402

F107 = F107A = 150.0
AP = 7.0
ALTS = (250.0, 300.0, 400.0, 500.0)


def var(s: dict, start: str) -> np.ndarray:
    return next(v for k, v in s.items() if isinstance(k, str) and k.replace(" ", "").startswith(start))


def at_alt(field: np.ndarray, alt_km: np.ndarray, z: float, log: bool) -> np.ndarray:
    i = np.searchsorted(alt_km, z)
    w = (z - alt_km[i - 1]) / (alt_km[i] - alt_km[i - 1])
    a, b = field[:, :, i - 1], field[:, :, i]
    return np.exp((1 - w) * np.log(a) + w * np.log(b)) if log else (1 - w) * a + w * b


def gmean(x: np.ndarray, lat: np.ndarray) -> float:
    w = np.cos(np.radians(lat))[None, :] * np.ones_like(x)
    return float((x * w).sum() / w.sum())


def snap_time(s: dict) -> dt.datetime:
    h = s["header"]
    return dt.datetime(h["Year"], h["Month"], h["Day"], h["Hour"], h["Minute"], h["Second"])


def msis_fields(t: dt.datetime, lon: np.ndarray, lat: np.ndarray, z: float):
    rho = np.empty((lon.size, lat.size))
    tn = np.empty_like(rho)
    o_n2 = np.empty_like(rho)
    for i, lo in enumerate(lon):
        for j, la in enumerate(lat):
            d, T = nrlmsise00.msise_model(t, z, float(la), float(lo), F107A, F107, AP)
            rho[i, j] = d[5] * 1e3
            tn[i, j] = T[1]
            o_n2[i, j] = d[1] / d[2]
    return rho, tn, o_n2


def main() -> None:
    run = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "results/tables/physical_g2_background_vs_msis.csv"
    rows = []
    snaps = gitm_io.snapshots(os.path.join(run, "UA", "data"))
    t0 = None
    for p in snaps:
        s = gitm_io.read_snapshot(p)
        t = snap_time(s)
        t0 = t0 or t
        hr = (t - t0).total_seconds() / 3600
        z, lon, lat = s["alt_km"], s["lon_deg"], s["lat_deg"]
        rho, tn = s["Rho"], s["Temperature"]
        o, n2 = var(s, "[O(!U3!NP)"), var(s, "[N!D2!N")
        ve, vn = var(s, "V!Dn!N(east)"), var(s, "V!Dn!N(north)")
        ne = var(s, "[e-")
        finite = bool(np.isfinite(rho).all() and np.isfinite(tn).all())
        for zz in ALTS:
            g_rho = at_alt(rho, z, zz, True)
            g_tn = at_alt(tn, z, zz, False)
            g_on2 = at_alt(o, z, zz, True) / at_alt(n2, z, zz, True)
            vh = np.hypot(at_alt(ve, z, zz, False), at_alt(vn, z, zz, False))
            m_rho, m_tn, m_on2 = msis_fields(t, lon, lat, zz)
            rows.append(dict(
                time_utc=t.isoformat(), hours_since_start=round(hr, 3), alt_km=zz,
                all_finite=finite, tn_min_K=float(tn.min()), tn_max_K=float(tn.max()),
                gitm_rho_mean=gmean(g_rho, lat), msis_rho_mean=gmean(m_rho, lat),
                rho_ratio=gmean(g_rho, lat) / gmean(m_rho, lat),
                gitm_tn_mean=gmean(g_tn, lat), msis_tn_mean=gmean(m_tn, lat),
                gitm_o_n2_mean=gmean(g_on2, lat), msis_o_n2_mean=gmean(m_on2, lat),
                gitm_vh_max=float(vh.max()), gitm_ne_max=float(ne.max()),
            ))
        print(t, "done", flush=True)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("wrote", out, len(rows))


if __name__ == "__main__":
    main()
