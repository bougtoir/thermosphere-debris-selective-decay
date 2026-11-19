"""G3R: background (unperturbed) state at the start of the fine/coarse paired window.

usage: python3 scripts/physical_g3r_background.py <coarse_spin_dir> <fine_spin_dir> [snapshot_tag]
Compares the final spin-up snapshots (default 3DALL_t020321_000000) after area-weighted 2x2 remapping
of the fine grid onto the coarse grid, at 300/400/500 km (log-density interpolation in altitude).
This is a confounder record: the fine background was spun up for 6 h, the coarse one for 24 h.
Writes results/tables/physical_g3r_background_fine_vs_coarse.csv.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "physical", "gitm"))
import gitm_io  # noqa: E402

ALTS = (300.0, 400.0, 500.0)


def at_alt(f, z, zz, log=False):
    """interpolate f[lon, lat, alt] with per-column altitude z[lon, lat, alt] to zz km."""
    out = np.empty(f.shape[:2])
    for i in range(f.shape[0]):
        for j in range(f.shape[1]):
            v = np.log(f[i, j]) if log else f[i, j]
            out[i, j] = np.interp(zz, z[i, j], v)
    return np.exp(out) if log else out


def remap(a, lat, k):
    w = np.cos(np.radians(lat))[None, :] * np.ones_like(a)
    nl, na = a.shape
    s = (a * w).reshape(nl // k, k, na // k, k).sum((1, 3))
    return s / w.reshape(nl // k, k, na // k, k).sum((1, 3))


def main():
    cdir, fdir = sys.argv[1:3]
    tag = sys.argv[3] if len(sys.argv) > 3 else "3DALL_t020321_000000"
    c = gitm_io.read_snapshot(os.path.join(cdir, "UA/data", tag))
    f = gitm_io.read_snapshot(os.path.join(fdir, "UA/data", tag))
    k = f["Rho"].shape[0] // c["Rho"].shape[0]
    wc = np.cos(np.radians(c["lat_deg"]))[None, :] * np.ones(c["Rho"].shape[:2])
    rows = []
    for zz in ALTS:
        for var, log in (("Rho", True), ("Temperature", False)):
            cv = at_alt(c[var], c["Altitude"] / 1e3, zz, log)
            fv = at_alt(f[var], f["Altitude"] / 1e3, zz, log)
            fr = np.exp(remap(np.log(fv), f["lat_deg"], k)) if log else remap(fv, f["lat_deg"], k)
            if log:
                d = fr / cv - 1
                gm = (fr * wc).sum() / (cv * wc).sum() - 1
            else:
                d = fr - cv
                gm = ((fr - cv) * wc).sum() / wc.sum()
            rows.append(dict(alt_km=zz, var=var, metric="fine_remapped_over_coarse_minus_1" if log else
                             "fine_remapped_minus_coarse_K", global_mean=gm,
                             area_rms=float(np.sqrt((d ** 2 * wc).sum() / wc.sum())),
                             min=float(d.min()), max=float(d.max()), snapshot=tag, k=k))
    df = pd.DataFrame(rows)
    df.to_csv("results/tables/physical_g3r_background_fine_vs_coarse.csv", index=False)
    print(df.round(4).to_string())


if __name__ == "__main__":
    main()
