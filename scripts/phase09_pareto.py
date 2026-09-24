"""Phase 9 — Pareto frontier: target benefit vs protected collateral.

For the case-A pair, sweep the tracking-bound design space
(delta_max x sigma_h x duration) and record target extra delta-v against
protected extra delta-v. The Pareto frontier marks designs where target
benefit cannot increase without increasing collateral.

Also sweeps sigma_v and altitude for context rows. Output:
results/tables/phase9_pareto.csv, docs/PHASE_9_HANDOFF.md.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.intervention.models import TrackingPerturbation  # noqa: E402
from src.experiment import make_object, simulate  # noqa: E402
from src.atmosphere.lookup import build_lookup, rho_fn_from_lookup  # noqa: E402
from src.utils import load_config, repo_root  # noqa: E402

HORIZON_S = 40 * 86400.0
SIG_V = 30.0


def build_obj(c):
    return make_object(c["case"], c["alt_km"], c["inc_deg"], c["B"],
                       e=c["e"], raan=c["raan"], argp=c["argp"],
                       M0=c["M0"], obj_type=c["obj_type"])


def pareto_front(df):
    """Rows where max target_dv at each collateral level is not dominated."""
    pts = df.sort_values("protected_dv_ms")
    front = []
    best = -np.inf
    for _, r in pts.iterrows():
        if r["target_dv_ms"] > best:
            front.append(r)
            best = r["target_dv_ms"]
    return pd.DataFrame(front)


def main():
    cfg = load_config()
    root = repo_root()
    df_lu = build_lookup(cfg["atmosphere"]["regimes"])
    cases = pd.read_csv(os.path.join(root, "data/processed/cases.csv"))
    rho_fn = rho_fn_from_lookup(df_lu, "moderate")

    pair = cases[cases["case"].str.startswith("A")]
    objs = {c["case"]: build_obj(c) for _, c in pair.iterrows()}
    tgt = objs[[k for k in objs if "target" in k][0]]

    rows = []
    for delta_max in [1.0, 2.0, 5.0, 10.0, 20.0]:
        for sig_h in [50.0, 100.0, 200.0, 400.0]:
            for dur in [4 * 3600.0, 12 * 3600.0, 86400.0]:
                trk = TrackingPerturbation(tgt["el"], delta_max, sig_h,
                                           SIG_V, 0.0, dur)
                rec = dict(delta_max=delta_max, sigma_h_km=sig_h,
                           duration_s=dur)
                for k, obj in objs.items():
                    res = simulate(obj, rho_fn, HORIZON_S, dt_day=0.25,
                                   delta_windows=[(0.0, dur)],
                                   delta_fn=trk.delta)
                    key = ("target" if objs[k]["obj_type"] == "target"
                           else "protected")
                    rec[f"{key}_dv_ms"] = res["extra_deltav_ms"]
                    rec[f"{key}_a_drop_km"] = (res["start_a_km"]
                                               - res["final_a_km"])
                rec["selectivity"] = (rec["target_dv_ms"]
                                      / rec["protected_dv_ms"]
                                      if rec["protected_dv_ms"] > 0
                                      else np.inf)
                rows.append(rec)

    df = pd.DataFrame(rows)
    df["on_pareto_front"] = False
    front = pareto_front(df)
    df.loc[front.index, "on_pareto_front"] = True
    df.to_csv(os.path.join(root, "results/tables/phase9_pareto.csv"),
              index=False)

    with open(os.path.join(root, "docs/PHASE_9_HANDOFF.md"), "w") as f:
        f.write("# Phase 9 handoff\n\n")
        f.write(f"{len(front)} of {len(df)} designs lie on the "
                "target-benefit vs protected-collateral Pareto front.\n\n")
        f.write(front[["delta_max", "sigma_h_km", "duration_s",
                       "target_dv_ms", "protected_dv_ms",
                       "selectivity"]].to_markdown(index=False))
    print(front[["delta_max", "sigma_h_km", "duration_s", "target_dv_ms",
                 "protected_dv_ms", "selectivity"]].to_string(index=False))


if __name__ == "__main__":
    main()
