"""G3R: realized (discretized) heating forcing on a GITM grid.

usage: python3 scripts/physical_g3r_forcing.py <label> <run_dir> [<heating.in or case json>]
Re-evaluates the hook's weights w on the model grid of the run's first output snapshot
(same formula as physical/gitm/user_perturbation_heating.f90), normalises with spherical
cell volumes and reports the realized forcing. Appends/replaces a row in
results/tables/physical_g3r_realized_forcing.csv.
"""
from __future__ import annotations

import csv
import json
import os
import sys

import numpy as np
from scipy.special import erf

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "physical", "gitm"))
import gitm_io  # noqa: E402

R_E = 6372.0e3
OUT = "results/tables/physical_g3r_realized_forcing.csv"


def edges(c):
    e = np.empty(c.size + 1)
    e[1:-1] = 0.5 * (c[1:] + c[:-1])
    e[0], e[-1] = c[0] - 0.5 * (c[1] - c[0]), c[-1] + 0.5 * (c[-1] - c[-2])
    return e


def heating_params(run_dir, src):
    if src and src.endswith(".json"):
        return [float(x) for x in json.load(open(src))["heating"]]
    f = src or os.path.join(run_dir, "UA/DataIn/user_heating.in")
    return [float(x) for x in open(f).read().split()]


def main():
    label, run_dir = sys.argv[1:3]
    heat = heating_params(run_dir, sys.argv[3] if len(sys.argv) > 3 else None)
    p0, lat0, lon0, z0, sh, sz = heat[:6]
    s = gitm_io.read_snapshot(gitm_io.snapshots(os.path.join(run_dir, "UA/data"))[0])
    if os.environ.get("G3R_SYNTH_GRID"):
        # pre-run check: same altitudes, uniform nlon x nlat cell centres, rho nearest-neighbour from run_dir
        nlo, nla = (int(x) for x in os.environ["G3R_SYNTH_GRID"].split("x"))
        lo = (np.arange(nlo) + 0.5) * 360.0 / nlo
        la = -90.0 + (np.arange(nla) + 0.5) * 180.0 / nla
        il = np.abs(((lo[:, None] - s["lon_deg"][None, :] + 180) % 360) - 180).argmin(1)
        ia = np.abs(la[:, None] - s["lat_deg"][None, :]).argmin(1)
        s = dict(lon_deg=lo, lat_deg=la, alt_km=s["alt_km"], Rho=s["Rho"][il][:, ia])
    lon, lat, z = np.radians(s["lon_deg"]), np.radians(s["lat_deg"]), s["alt_km"] * 1e3
    le, pe, ze = edges(lon), np.clip(edges(lat), -np.pi / 2, np.pi / 2), edges(z)
    re = R_E + ze
    dV = ((np.diff(le))[:, None, None] * np.diff(np.sin(pe))[None, :, None]
          * (np.diff(re ** 3) / 3.0)[None, None, :])
    a, b = np.radians(lat0), np.radians(lon0)
    cosd = np.clip(np.sin(a) * np.sin(lat)[None, :] + np.cos(a) * np.cos(lat)[None, :]
                   * np.cos(lon[:, None] - b), -1, 1)
    dh = (R_E + z0 * 1e3) * np.arccos(cosd)
    wz = np.exp(-(z - z0 * 1e3) ** 2 / (2 * (sz * 1e3) ** 2))
    w = np.exp(-dh[:, :, None] ** 2 / (2 * (sh * 1e3) ** 2)) * wz[None, None, :]
    W = float((w * dV).sum())
    q = p0 * w / W if p0 > 0 else w / W          # W m^-3 (or per watt if control)
    E = q * dV
    Et = float(E.sum())
    rho = s["Rho"]
    # energy-weighted centroid (unit-vector mean) and moments
    x = np.cos(lat)[None, :] * np.cos(lon)[:, None]
    y = np.cos(lat)[None, :] * np.sin(lon)[:, None]
    zz = np.sin(lat)[None, :] * np.ones((lon.size, 1))
    Eh = E.sum(2)
    cx, cy, cz = (Eh * x).sum() / Et, (Eh * y).sum() / Et, (Eh * zz).sum() / Et
    clat, clon = np.degrees(np.arctan2(cz, np.hypot(cx, cy))), np.degrees(np.arctan2(cy, cx))
    sig_h_eff = np.sqrt((Eh * dh ** 2).sum() / Et / 2.0) / 1e3
    Ez = E.sum((0, 1))
    zc = float((Ez * z).sum() / Et)
    sig_z_eff = float(np.sqrt((Ez * (z - zc) ** 2).sum() / Et)) / 1e3
    cont_vol = 2 * np.pi * (sh * 1e3) ** 2 * np.sqrt(2 * np.pi) * sz * 1e3
    zlo, zhi = ze[0], ze[-1]
    inside_z = 0.5 * (erf((zhi - z0 * 1e3) / (np.sqrt(2) * sz * 1e3)) - erf((zlo - z0 * 1e3) / (np.sqrt(2) * sz * 1e3)))
    spec = q / rho                                           # W kg^-1
    row = dict(
        label=label, run_dir=run_dir, n_lon=lon.size, n_lat=lat.size, n_alt=z.size,
        dlon_deg=float(np.degrees(np.diff(le).mean())), dlat_deg=float(np.degrees(np.diff(pe[1:-1]).mean())),
        dz_at_z0_km=float(np.interp(z0 * 1e3, z, np.gradient(z)) / 1e3),
        P0_W=p0, z0_km=z0, sigma_h_km=sh, sigma_z_km=sz,
        realized_power_W=Et if p0 > 0 else np.nan,
        sum_w_dV_over_continuous=W / cont_vol,
        continuous_fraction_inside_alt_domain=float(inside_z),
        centroid_lat_deg=float(clat), centroid_lon_deg=float(clon), centroid_alt_km=zc / 1e3,
        sigma_h_eff_km=float(sig_h_eff), sigma_z_eff_km=sig_z_eff,
        peak_q_W_m3=float(q.max()), effective_volume_m3=float(Et ** 2 / (q ** 2 * dV).sum()),
        n_cells_for_90pct_energy=int(np.searchsorted(np.cumsum(np.sort(E.ravel())[::-1]) / Et, 0.9) + 1),
        peak_specific_heating_W_kg=float(spec.max()),
        energy_weighted_specific_heating_W_kg=float((E * spec).sum() / Et),
        heated_mass_kg=float(Et ** 2 / (E * spec).sum()),
        cells_per_sigma_h_lat=float(sh * 1e3 / ((R_E + z0 * 1e3) * np.diff(pe[1:-1]).mean())),
        cells_per_sigma_h_lon_at_lat0=float(sh * 1e3 / ((R_E + z0 * 1e3) * np.cos(a) * np.diff(le).mean())),
        snapshot=os.path.basename(gitm_io.snapshots(os.path.join(run_dir, "UA/data"))[0]),
    )
    old = list(csv.DictReader(open(OUT))) if os.path.exists(OUT) else []
    old = [o for o in old if o["label"] != label]
    with open(OUT, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(row))
        wr.writeheader()
        wr.writerows(old + [row])
    for k, v in row.items():
        print(f"{k:42s} {v}")


if __name__ == "__main__":
    main()
