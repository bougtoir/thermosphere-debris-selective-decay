"""Step-size convergence of the drift-aware tracking exposure.

The drift-aware arms measure exposure along the trajectory the induced drag
produces, so their delta-v depends on how accurately the along-track phase
is integrated: the decay lowers the semi-major axis, the mean motion rises,
and the object walks out of a patch centred on the predicted orbit. That
makes the step size a numerical parameter of the *result*, not only of the
lifetime, and it has to be reported.

The integrator takes each step with the midpoint rule (rate and sampling
ephemeris evaluated at the predicted mid-step semi-major axis), which is
second order in the step; steps overlapping an intervention window are
shortened to fastprop.DT_DAY_ACTIVE. This script runs the case-A tracking
scenario over a ladder of active step sizes and records the extra delta-v,
its change between rungs and the observed order of convergence.

Writes results/tables/orbit_step_convergence.csv.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.atmosphere.lookup import build_lookup, rho_fn_from_lookup  # noqa: E402,E501
from src.experiment import make_object  # noqa: E402
from src.intervention.models import TrackingPerturbation  # noqa: E402
from src.orbits import fastprop  # noqa: E402
from src.utils import load_config, repo_root  # noqa: E402

WIN = 86400.0
DELTA_MAX = 5.0
SIG_H = 200.0
SIG_V = 30.0
FINE_DT_S = 60.0
LADDER = [0.25, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002]


def main():
    cfg = load_config()
    root = repo_root()
    lu = build_lookup(cfg["atmosphere"]["regimes"])
    rho_fn = rho_fn_from_lookup(lu, "moderate")
    cases = pd.read_csv(os.path.join(root, "data/processed/cases.csv"))
    row = cases[(cases["case"].str.startswith("A"))
                & (cases["obj_type"] == "target")].iloc[0]
    obj = make_object(row["case"], row["alt_km"], row["inc_deg"], row["B"],
                      e=row["e"], raan=row["raan"], argp=row["argp"],
                      M0=row["M0"], obj_type=row["obj_type"])
    trk = TrackingPerturbation(obj["el"], DELTA_MAX, SIG_H, SIG_V, 0.0, WIN)

    rows = []
    for dt_active in LADDER:
        _, hist = fastprop.decay_lifetime(
            obj["el"], rho_fn, obj["B"], WIN, dt_day=0.5,
            delta_windows=[(0.0, WIN)], delta_fn=trk.delta,
            fine_dt_s=FINE_DT_S, dt_day_active=dt_active)
        rows.append(dict(dt_day_active=dt_active,
                         n_steps=int(round(WIN / (dt_active * 86400.0))),
                         extra_dv_ms=hist["extra_drag_impulse_ms"],
                         mean_rho_delta=hist["mean_rho_delta"],
                         encounter_count=hist["encounter_count"]))
    df = pd.DataFrame(rows)
    ref = float(df["extra_dv_ms"].iloc[-1])
    df["rel_error_vs_finest"] = (df["extra_dv_ms"] - ref) / ref
    df["order_estimate"] = np.nan
    e = df["extra_dv_ms"].to_numpy()
    h = df["dt_day_active"].to_numpy()
    for k in range(2, len(e)):
        num = abs(e[k - 2] - e[k - 1])
        den = abs(e[k - 1] - e[k])
        if den > 0 and num > 0:
            df.loc[k, "order_estimate"] = float(
                np.log(num / den) / np.log(h[k - 2] / h[k - 1]))
    df["production_step"] = df["dt_day_active"] == fastprop.DT_DAY_ACTIVE
    df.to_csv(os.path.join(root,
                           "results/tables/orbit_step_convergence.csv"),
              index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
