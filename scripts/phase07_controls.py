"""Phase 7 — matched-exposure controls.

Tests whether localization itself provides value. For representative
target/protected pairs (A, D, E, G) compare, over the same 1-day window:

  * baseline   : natural drag
  * uniform    : spatially uniform density enhancement delta=5 everywhere
                 (same integrated target exposure as the tracking bound,
                 since tracking holds ~delta_max on target continuously)
  * localized  : idealized on-target tracking perturbation (Phase 6 bound)
  * optimized  : tracking perturbation with (t0, duration) optimized by
                 differential evolution to maximize target delta-v minus a
                 collateral penalty (case A pair only — the expensive case)

Output: results/tables/phase7_controls.csv, docs/PHASE_7_HANDOFF.md.
Selectivity ratios are always reported next to absolute collateral delta-v.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.intervention.models import TrackingPerturbation  # noqa: E402
from src.experiment import make_object, simulate  # noqa: E402
from src.atmosphere.lookup import build_lookup, rho_fn_from_lookup  # noqa: E402
from src.utils import load_config, repo_root  # noqa: E402

WIN = 86400.0
DELTA_MAX = 5.0
SIG_H = 200.0
SIG_V = 30.0
W_COLLATERAL = 10.0   # penalty weight on protected-object delta-v
T_HORIZON_D = 5 * 365.25

PAIRS = ["A", "D", "E", "G"]


def build_obj(c):
    return make_object(c["case"], c["alt_km"], c["inc_deg"], c["B"],
                       e=c["e"], raan=c["raan"], argp=c["argp"],
                       M0=c["M0"], obj_type=c["obj_type"])


def uniform_delta(delta_max, t0, dur):
    def fn(r, t):
        return delta_max if t0 <= t <= t0 + dur else 0.0
    return fn



def main():
    cfg = load_config()
    root = repo_root()
    df_lu = build_lookup(cfg["atmosphere"]["regimes"])
    cases = pd.read_csv(os.path.join(root, "data/processed/cases.csv"))
    rho_fn = rho_fn_from_lookup(df_lu, "moderate")

    rows = []
    for prefix in PAIRS:
        tgt_row = cases[(cases["case"].str.startswith(prefix))
                        & (cases["obj_type"] == "target")].iloc[0]
        tgt = build_obj(tgt_row)

        for _, c in cases[cases["case"].str.startswith(prefix)].iterrows():
            obj = build_obj(c)
            base = simulate(obj, rho_fn, T_HORIZON_D * 86400.0, dt_day=0.5)
            uni = simulate(obj, rho_fn, T_HORIZON_D * 86400.0, dt_day=0.5,
                           delta_windows=[(0.0, WIN)],
                           delta_fn=uniform_delta(DELTA_MAX, 0.0, WIN))
            trk = TrackingPerturbation(tgt["el"], DELTA_MAX, SIG_H, SIG_V,
                                       0.0, WIN)
            loc = simulate(obj, rho_fn, T_HORIZON_D * 86400.0, dt_day=0.5,
                           delta_windows=[(0.0, WIN)], delta_fn=trk.delta)
            for scen, res in [("baseline", base), ("uniform", uni),
                              ("localized_tracking", loc)]:
                rows.append(dict(scenario=scen, case=c["case"],
                                 obj_type=c["obj_type"], pair=prefix,
                                 delta_a_km=base["final_a_km"]
                                 - res["final_a_km"],
                                 a_drop_km=res["start_a_km"]
                                 - res["final_a_km"],
                                 extra_deltav_ms=res["extra_deltav_ms"],
                                 encounter_count=res["encounter_count"],
                                 delta_lifetime_d=base["lifetime_days"]
                                 - res["lifetime_days"]))

    # --- optimized localized: case A pair, optimize (t0, dur) ---
    pairA = cases[cases["case"].str.startswith("A")]
    objs = {c["case"]: build_obj(c) for _, c in pairA.iterrows()}
    tgt = objs[[k for k in objs if "target" in k][0]]
    keys = list(objs)

    def objective(x):
        t0, dur = x
        trk = TrackingPerturbation(tgt["el"], DELTA_MAX, SIG_H, SIG_V,
                                   t0, dur)
        tgt_dv = prot_dv = 0.0
        for k in keys:
            res = simulate(objs[k], rho_fn, 2 * WIN, dt_day=0.25,
                           delta_windows=[(t0, t0 + dur)],
                           delta_fn=trk.delta)
            if objs[k]["obj_type"] == "target":
                tgt_dv += res["extra_deltav_ms"]
            else:
                prot_dv += res["extra_deltav_ms"]
        return -(tgt_dv - W_COLLATERAL * prot_dv)

    opt = differential_evolution(
        objective, bounds=[(0.0, WIN), (3600.0, WIN)],
        maxiter=12, popsize=6, seed=cfg["seed"], polish=True)
    t0_o, dur_o = opt.x
    trk_o = TrackingPerturbation(tgt["el"], DELTA_MAX, SIG_H, SIG_V,
                                 t0_o, dur_o)
    for k in keys:
        c = pairA[pairA["case"] == k].iloc[0]
        res = simulate(objs[k], rho_fn, T_HORIZON_D * 86400.0, dt_day=0.5,
                       delta_windows=[(t0_o, t0_o + dur_o)],
                       delta_fn=trk_o.delta)
        rows.append(dict(scenario="optimized_localized", case=k,
                         obj_type=c["obj_type"], pair="A",
                         delta_a_km=np.nan,
                         a_drop_km=res["start_a_km"] - res["final_a_km"],
                         extra_deltav_ms=res["extra_deltav_ms"],
                         encounter_count=res["encounter_count"],
                         delta_lifetime_d=np.nan))

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(root, "results/tables/phase7_controls.csv"),
              index=False)

    # selectivity summary: ratio next to absolute collateral
    summ = []
    for scen in ["uniform", "localized_tracking", "optimized_localized"]:
        sub = df[df.scenario == scen]
        for prefix in sub["pair"].unique():
            p = sub[sub.pair == prefix]
            t = p[p.obj_type == "target"]["extra_deltav_ms"].sum()
            pr = p[p.obj_type == "protected"]["extra_deltav_ms"].sum()
            summ.append(dict(scenario=scen, pair=prefix,
                             target_dv_ms=t, protected_dv_ms=pr,
                             selectivity_ratio=t / pr if pr > 0 else np.inf))
    sdf = pd.DataFrame(summ)
    sdf.to_csv(os.path.join(root, "results/tables/phase7_selectivity.csv"),
               index=False)

    with open(os.path.join(root, "docs/PHASE_7_HANDOFF.md"), "w") as f:
        f.write("# Phase 7 handoff\n\n")
        f.write(f"Optimized localized (case A): t0={t0_o:.0f} s, "
                f"dur={dur_o:.0f} s, objective={-opt.fun:.4g}\n\n")
        f.write(sdf.to_markdown(index=False))
    print(sdf.to_string(index=False))


if __name__ == "__main__":
    main()
