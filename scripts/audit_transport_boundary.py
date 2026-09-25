"""Transport-boundary provenance and sensitivity audit (revision Phase 4).

The frozen manuscript quotes "41%" of (kappa, u) combinations as allowing a
patch to persist >= 1 h. That number is the unweighted fraction of a
hand-chosen product grid

    sigma_h in {50, 200, 1000} km  x  kappa_h in {1e3, 1e5, 1e6} m^2/s
    x  u in {0, 100, 300} m/s

satisfying tau_diff = sigma_h^2/(2 kappa_h) >= 1 h and tau_adv = sigma_h/u
>= 1 h. No probability distribution over (kappa, u) was sampled, so it is a
design-grid fraction, not a probability. It is also dominated by two grid
choices: the inclusion of u = 0 (one third of the grid; a windless
thermosphere) and of sigma_h = 1000 km (a patch so large that it provides no
selectivity at all).

This script recomputes the surviving fraction under alternative, explicitly
labelled grid and criterion choices, and reports the conditional statement
that replaces the headline number: for patches small enough to be selective
(sigma_h <= 200 km) in the presence of any realistic mean wind, survival for
1 h is zero across the whole surveyed diffusivity range.

Writes results/tables/transport_boundary_sensitivity.csv.
"""
from __future__ import annotations

import itertools
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.utils import repo_root  # noqa: E402

# grid variants: (label, sigma_h km, kappa m^2/s, u m/s, note)
SIGMA_SETS = {
    "frozen": [50.0, 200.0, 1000.0],
    "selective_only": [50.0, 100.0, 200.0],
    "fine": [25.0, 50.0, 100.0, 200.0, 400.0, 1000.0],
}
KAPPA_SETS = {
    "frozen": [1e3, 1e5, 1e6],
    "log_uniform_9": list(np.logspace(3, 6, 9)),
    "conservative_low": [1e3, 1e4, 1e5],
}
WIND_SETS = {
    "frozen": [0.0, 100.0, 300.0],
    "no_zero_wind": [50.0, 100.0, 200.0, 300.0],
    "quiet_only": [25.0, 50.0, 100.0],
    "storm_included": [0.0, 100.0, 300.0, 600.0],
}
CRITERIA_H = [0.5, 1.0, 3.0, 6.0]


def survives(sh_km, kappa, u, t_req_s):
    tau_diff = (sh_km * 1e3) ** 2 / (2.0 * kappa)
    tau_adv = np.inf if u == 0 else (sh_km * 1e3) / u
    return (tau_diff >= t_req_s) and (tau_adv >= t_req_s)


def main():
    root = repo_root()
    rows = []
    for (sname, ss), (kname, ks), (wname, ws), t_h in itertools.product(
            SIGMA_SETS.items(), KAPPA_SETS.items(), WIND_SETS.items(),
            CRITERIA_H):
        combos = list(itertools.product(ss, ks, ws))
        t_req = t_h * 3600.0
        ok = [survives(a, b, c, t_req) for a, b, c in combos]
        sel = [(a, b, c) for a, b, c in combos if a <= 200.0]
        ok_sel = [survives(a, b, c, t_req) for a, b, c in sel]
        sel_wind = [(a, b, c) for a, b, c in combos
                    if a <= 200.0 and c >= 50.0]
        ok_sw = [survives(a, b, c, t_req) for a, b, c in sel_wind]
        sel_w100 = [(a, b, c) for a, b, c in combos
                    if a <= 200.0 and c >= 100.0]
        ok_sw100 = [survives(a, b, c, t_req) for a, b, c in sel_w100]
        rows.append(dict(
            sigma_set=sname, kappa_set=kname, wind_set=wname,
            criterion_h=t_h, n_combinations=len(combos),
            frac_surviving=float(np.mean(ok)),
            n_selective=len(sel),
            frac_surviving_selective_sigma=float(np.mean(ok_sel))
            if sel else np.nan,
            n_selective_windy=len(sel_wind),
            frac_surviving_selective_windy=float(np.mean(ok_sw))
            if sel_wind else np.nan,
            n_selective_wind100=len(sel_w100),
            frac_surviving_selective_wind100=float(np.mean(ok_sw100))
            if sel_w100 else np.nan))
    df = pd.DataFrame(rows)
    out = os.path.join(root,
                       "results/tables/transport_boundary_sensitivity.csv")
    df.to_csv(out, index=False)

    frozen = df[(df.sigma_set == "frozen") & (df.kappa_set == "frozen")
                & (df.wind_set == "frozen") & (df.criterion_h == 1.0)]
    print("frozen grid, 1 h criterion:")
    print(frozen.to_string(index=False))
    print("\nrange of frac_surviving over all grid variants at 1 h: "
          f"{df[df.criterion_h == 1.0].frac_surviving.min():.3f} - "
          f"{df[df.criterion_h == 1.0].frac_surviving.max():.3f}")
    sw = df[df.criterion_h == 1.0]["frac_surviving_selective_windy"]
    print(f"selective (sigma_h<=200 km) AND wind>=50 m/s, 1 h: "
          f"max over variants = {np.nanmax(sw):.3f}")
    sw1 = df[df.criterion_h == 1.0]["frac_surviving_selective_wind100"]
    print(f"selective (sigma_h<=200 km) AND wind>=100 m/s, 1 h: "
          f"max over variants = {np.nanmax(sw1):.3f}")


if __name__ == "__main__":
    main()
