"""G4T: time evolution of cumulative target / non-target extra delta-v and selectivity.

usage: python3 scripts/physical_g4t_selectivity_evolution.py <label> [<label> ...]
Environment: G3R_COARSEN=k (conservative k x k remap before coupling), G3R_TMAX_S (truncate).
Same object population, B, seed, target definition (ground track within 1 sigma_h during heating) and
interpolation as the nominal variant of physical_g3r_orbit_sensitivity.py. Cumulative sums are reported at
every atmosphere output time after onset. Writes/updates results/tables/physical_g4t_selectivity_evolution.csv.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import physical_g3r_orbit_sensitivity as osn  # noqa: E402
import physical_g4_orbit_coupling as g4  # noqa: E402

OUT = "results/tables/physical_g4t_selectivity_evolution.csv"


def run(label):
    z, grid = osn.load(label)
    G = osn.geometry(z, 10.0)
    p0, lat0, lon0, z0, sig_h, sig_z, t_on, dur = z["heating"][:8]
    t_on = t_on - float(z["t_case0_s"])
    altq = (G["rm"] - g4.R_GITM) / 1e3
    args = (G["t"], G["T"], G["lon360"], G["la"], altq, G["v_corot"], G["th"])
    ac = osn.drag_acc(z, "c", *args)
    ap = osn.drag_acc(z, "p", *args)
    on = (G["T"] >= t_on) & (G["T"] <= t_on + dur)
    tg = np.where(on, osn.gc_km(lat0, lon0, G["la"], G["lo"]), np.inf).min(1) <= sig_h
    cum_x = np.cumsum(ap - ac, 1) * 10.0
    cum_n = np.cumsum(ac, 1) * 10.0
    rows = []
    for tt in G["t"][G["t"] > t_on]:
        j = int(np.searchsorted(G["tq"], tt)) - 1
        if j < 0:
            continue
        for h in g4.ALTS:
            m = G["obj"][:, 0] == h
            a, b = cum_x[m & tg, j], cum_x[m & ~tg, j]
            rows.append(dict(label=label, grid=grid, alt_km=h, t_after_onset_s=float(tt - t_on),
                             n_target=int(a.size), n_nontarget=int(b.size),
                             target_cum_dv_mean=float(a.mean()), nontarget_cum_dv_mean=float(b.mean()),
                             selectivity_mean=float(a.mean() / b.mean()) if b.mean() else np.nan,
                             nontarget_share_of_total_extra=float(b.sum() / (a.sum() + b.sum())),
                             natural_cum_dv_mean=float(cum_n[m, j].mean())))
    print(label, grid, flush=True)
    return rows, grid


def main():
    rows, grids = [], set()
    for lab in sys.argv[1:]:
        r, g = run(lab)
        rows += r
        grids.add(g)
    df = pd.DataFrame(rows)
    if os.path.exists(OUT):
        old = pd.read_csv(OUT)
        df = pd.concat([old[~(old.label.isin(sys.argv[1:]) & old.grid.isin(grids))], df], ignore_index=True)
    df.to_csv(OUT, index=False)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
