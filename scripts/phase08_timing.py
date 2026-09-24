"""Phase 8 — timing sensitivity of localized interventions.

How much does the outcome depend on *when* a localized perturbation is
applied? Two experiments, both on the case-A pair (400 km, i=51.6):

  1. Fixed ECEF pulse: sweep the pulse center time t_pass across one day.
     Since the patch is Earth-fixed, the target only transits it when its
     ground track crosses the patch site -> outcome is strongly phasing
     dependent. For each t_pass the patch is re-centered on the target's
     ground position at t_pass (best-case siting), so the sweep isolates
     pure timing/duration sensitivity rather than siting error.

  2. Tracking bound: sweep t0 of a fixed 4 h tracking window across a day.
     The residual sensitivity measures how much background-density
     variation along the orbit modulates the achievable effect.

Writes results/tables/phase8_timing.csv, docs/PHASE_8_HANDOFF.md.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.intervention.models import (  # noqa: E402
    GaussianPatch, TrackingPerturbation, make_delta_fn)
from src.orbits import fastprop  # noqa: E402
from src.orbits.elements import ecef_approx  # noqa: E402
from src.experiment import make_object, simulate  # noqa: E402
from src.atmosphere.lookup import build_lookup, rho_fn_from_lookup  # noqa: E402
from src.utils import load_config, repo_root  # noqa: E402

DELTA_MAX = 5.0
SIG_H = 200.0
SIG_V = 30.0
PULSE_DUR = 7200.0
TRACK_DUR = 4 * 3600.0
HORIZON_S = 40 * 86400.0   # short horizon: measure altitude drop + dv


def build_obj(c):
    return make_object(c["case"], c["alt_km"], c["inc_deg"], c["B"],
                       e=c["e"], raan=c["raan"], argp=c["argp"],
                       M0=c["M0"], obj_type=c["obj_type"])


def main():
    cfg = load_config()
    root = repo_root()
    df_lu = build_lookup(cfg["atmosphere"]["regimes"])
    cases = pd.read_csv(os.path.join(root, "data/processed/cases.csv"))
    rho_fn = rho_fn_from_lookup(df_lu, "moderate")

    pair = cases[cases["case"].str.startswith("A")]
    objs = {c["case"]: build_obj(c) for _, c in pair.iterrows()}
    tgt = objs[[k for k in objs if "target" in k][0]]
    tgt_alt = pair[pair.obj_type == "target"]["alt_km"].iloc[0]

    rows = []
    # --- experiment 1: fixed pulse, best-case re-sited at each t_pass ---
    for t_pass in np.arange(3600.0, 86400.0, 3600.0):
        r_t, _ = fastprop.position_at(tgt["el"], t_pass)
        lat0, lon0 = ecef_approx(r_t, t_pass)
        g = GaussianPatch(lat0, lon0, tgt_alt, DELTA_MAX, SIG_H, SIG_V,
                          t0_s=t_pass - PULSE_DUR / 2, duration_s=PULSE_DUR,
                          kappa_h_m2s=1e5, advection_east_ms=100.0)
        dfn = make_delta_fn([g])
        for k, obj in objs.items():
            res = simulate(obj, rho_fn, HORIZON_S, dt_day=0.25,
                           delta_windows=[(t_pass - PULSE_DUR / 2,
                                           t_pass + PULSE_DUR / 2)],
                           delta_fn=dfn)
            rows.append(dict(experiment="fixed_pulse_bestcase_site",
                             t_s=t_pass, case=k,
                             obj_type=objs[k]["obj_type"],
                             extra_deltav_ms=res["extra_deltav_ms"],
                             encounter_count=res["encounter_count"],
                             a_drop_km=res["start_a_km"]
                             - res["final_a_km"]))

    # --- experiment 2: tracking window start-time sweep ---
    for t0 in np.arange(0.0, 86400.0, 7200.0):
        trk = TrackingPerturbation(tgt["el"], DELTA_MAX, SIG_H, SIG_V,
                                   t0, TRACK_DUR)
        for k, obj in objs.items():
            res = simulate(obj, rho_fn, HORIZON_S, dt_day=0.25,
                           delta_windows=[(t0, t0 + TRACK_DUR)],
                           delta_fn=trk.delta)
            rows.append(dict(experiment="tracking_4h_window",
                             t_s=t0, case=k,
                             obj_type=objs[k]["obj_type"],
                             extra_deltav_ms=res["extra_deltav_ms"],
                             encounter_count=res["encounter_count"],
                             a_drop_km=res["start_a_km"]
                             - res["final_a_km"]))

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(root, "results/tables/phase8_timing.csv"),
              index=False)

    summ = (df[df.obj_type == "target"]
            .groupby("experiment")["extra_deltav_ms"]
            .agg(["min", "max", "mean", "std"]))
    summ["spread_ratio"] = summ["max"] / summ["mean"]
    with open(os.path.join(root, "docs/PHASE_8_HANDOFF.md"), "w") as f:
        f.write("# Phase 8 handoff\n\n")
        f.write("Target extra delta-v sensitivity to intervention timing.\n\n")
        f.write(summ.to_markdown())
    print(summ.to_string())


if __name__ == "__main__":
    main()
