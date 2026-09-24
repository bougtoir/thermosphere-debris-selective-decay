"""Phase 10 — uncertainty propagation and mandatory negative controls.

Part 1: Monte Carlo over intervention and environment parameters for the
tracking-bound scenario on the case-A pair (40-day horizon, extra delta-v
as response). n from config montecarlo.n_samples.

Part 2: Sobol' first/total-order indices via SALib (same response), with
a small Saltelli base justified by the semi-analytic propagator's cost.

Part 3: mandatory negative controls — cases where selective decay should
NOT work; each is simulated, not just asserted:
  * high altitude (F pair, 750 km)
  * high B (synthetic B=200 object at 400 km)
  * near-identical target/protected trajectories (collateral == benefit)
  * diffuse perturbation (sigma_h = 3000 km)
  * very short perturbation (60 s)
  * poor timing (fixed pulse where target never transits the site)

Writes results/tables/phase10_montecarlo.csv, phase10_sobol.csv,
phase10_negative_controls.csv, docs/PHASE_10_HANDOFF.md.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from SALib.sample import saltelli
from SALib.analyze import sobol

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.intervention.models import (  # noqa: E402
    GaussianPatch, TrackingPerturbation, make_delta_fn)
from src.orbits import fastprop  # noqa: E402
from src.orbits.elements import ecef_approx  # noqa: E402
from src.experiment import make_object, simulate  # noqa: E402
from src.atmosphere.lookup import build_lookup, rho_fn_from_lookup  # noqa: E402
from src.utils import load_config, rng, repo_root  # noqa: E402

HORIZON_S = 40 * 86400.0

PROBLEM = {
    "num_vars": 6,
    "names": ["delta_max", "sigma_h_km", "sigma_v_km", "rho_scale",
              "B_scale", "duration_h"],
    "bounds": [[2.0, 10.0], [100.0, 400.0], [15.0, 60.0],
               [0.85, 1.15], [0.9, 1.1], [4.0, 24.0]],
}


def build_obj(c):
    return make_object(c["case"], c["alt_km"], c["inc_deg"], c["B"],
                       e=c["e"], raan=c["raan"], argp=c["argp"],
                       M0=c["M0"], obj_type=c["obj_type"])


def eval_design(x, objs, tgt_el, rho_fn, rho_scale):
    """extra dv of target and of protected under a tracking design x."""
    d, sh, sv, rs, bs, dur_h = x
    trk = TrackingPerturbation(tgt_el, d, sh, sv, 0.0, dur_h * 3600.0)
    out = {}
    for k, obj in objs.items():
        obj_s = dict(obj)
        obj_s["B"] = obj["B"] * bs
        res = simulate(obj_s, rho_fn, HORIZON_S, dt_day=0.25,
                       delta_windows=[(0.0, dur_h * 3600.0)],
                       delta_fn=trk.delta, rho_scale=rs)
        out[k] = res["extra_deltav_ms"]
    return out


def main():
    cfg = load_config()
    root = repo_root()
    r = rng()
    df_lu = build_lookup(cfg["atmosphere"]["regimes"])
    cases = pd.read_csv(os.path.join(root, "data/processed/cases.csv"))
    rho_fn = rho_fn_from_lookup(df_lu, "moderate")

    pairA = cases[cases["case"].str.startswith("A")]
    objs = {c["case"]: build_obj(c) for _, c in pairA.iterrows()}
    tgt_key = [k for k in objs if "target" in k][0]
    tgt_el = objs[tgt_key]["el"]

    # ---- part 1: Monte Carlo ----
    n_mc = int(cfg["montecarlo"]["n_samples"])
    mc_rows = []
    for i in range(n_mc):
        x = [r.uniform(*b) for b in PROBLEM["bounds"]]
        out = eval_design(x, objs, tgt_el, rho_fn, x[3])
        rec = dict(zip(PROBLEM["names"], x))
        rec["target_dv_ms"] = out[tgt_key]
        rec["protected_dv_ms"] = out[[k for k in objs if k != tgt_key][0]]
        mc_rows.append(rec)
    mc = pd.DataFrame(mc_rows)
    mc.to_csv(os.path.join(root, "results/tables/phase10_montecarlo.csv"),
              index=False)

    # ---- part 2: Sobol' (small Saltelli base; semi-analytic keeps it
    # affordable, and phase-11 scaling already shows near-linear response)
    N = 32
    X = saltelli.sample(PROBLEM, N, calc_second_order=False)
    Y = np.empty(len(X))
    for i, x in enumerate(X):
        out = eval_design(x, objs, tgt_el, rho_fn, x[3])
        Y[i] = out[tgt_key]
    si = sobol.analyze(PROBLEM, Y, calc_second_order=False)
    sob = pd.DataFrame(dict(param=PROBLEM["names"], S1=si["S1"], ST=si["ST"],
                            S1_conf=si["S1_conf"], ST_conf=si["ST_conf"]))
    sob.to_csv(os.path.join(root, "results/tables/phase10_sobol.csv"),
               index=False)

    # ---- part 3: negative controls ----
    neg = []

    def add_neg(name, obj, delta_fn, windows, rho_scale=1.0, B_scale=1.0):
        o = dict(obj)
        o["B"] = obj["B"] * B_scale
        res = simulate(o, rho_fn, HORIZON_S, dt_day=0.25,
                       delta_windows=windows, delta_fn=delta_fn,
                       rho_scale=rho_scale)
        neg.append(dict(control=name, case=obj["name"],
                        extra_deltav_ms=res["extra_deltav_ms"],
                        a_drop_km=res["start_a_km"] - res["final_a_km"],
                        encounter_count=res["encounter_count"]))

    # (a) high altitude: F pair under tracking bound
    for _, c in cases[cases["case"].str.startswith("F")].iterrows():
        o = build_obj(c)
        trk = TrackingPerturbation(o["el"], 5.0, 200.0, 30.0,
                                   0.0, 86400.0)
        add_neg("high_altitude_750km", o, trk.delta, [(0.0, 86400.0)])

    # (b) high B: synthetic B=200 object at 400 km, tracked
    hb = make_object("neg_highB", 400.0, 51.6, 200.0, e=0.001, raan=0.0,
                     argp=0.0, M0=0.0, obj_type="target")
    trk = TrackingPerturbation(hb["el"], 5.0, 200.0, 30.0, 0.0, 86400.0)
    add_neg("high_B_200", hb, trk.delta, [(0.0, 86400.0)])

    # (c) near-identical trajectories: protected co-orbital twin of A target
    twin = make_object("neg_twin", 400.0, 51.6, 80.0, e=0.001, raan=0.0,
                       argp=0.0, M0=0.005, obj_type="protected")
    trk = TrackingPerturbation(objs[tgt_key]["el"], 5.0, 200.0, 30.0,
                               0.0, 86400.0)
    add_neg("near_identical_trajectory", twin, trk.delta, [(0.0, 86400.0)])

    # (d) diffuse perturbation sigma_h=3000 km
    trk = TrackingPerturbation(objs[tgt_key]["el"], 5.0, 3000.0, 30.0,
                               0.0, 86400.0)
    for k, o in objs.items():
        add_neg("diffuse_3000km", o, trk.delta, [(0.0, 86400.0)])

    # (e) very short perturbation: 60 s tracking burst
    trk = TrackingPerturbation(objs[tgt_key]["el"], 5.0, 200.0, 30.0,
                               0.0, 60.0)
    add_neg("short_60s", objs[tgt_key], trk.delta, [(0.0, 60.0)])

    # (f) poor timing: patch sited on the target's ground position at
    # t_pass=40000 but activated during [0, 7200] when the target is far away
    r_t, _ = fastprop.position_at(tgt_el, 40000.0)
    lat0, lon0 = ecef_approx(r_t, 40000.0)
    g = GaussianPatch(lat0, lon0, 400.0, 5.0, 200.0, 30.0,
                      t0_s=0.0, duration_s=7200.0, kappa_h_m2s=1e5,
                      advection_east_ms=100.0)
    add_neg("poor_timing_fixed_pulse", objs[tgt_key], make_delta_fn([g]),
            [(0.0, 7200.0)])

    ndf = pd.DataFrame(neg)
    ndf.to_csv(os.path.join(
        root, "results/tables/phase10_negative_controls.csv"), index=False)

    with open(os.path.join(root, "docs/PHASE_10_HANDOFF.md"), "w") as f:
        f.write("# Phase 10 handoff\n\n## Monte Carlo summary\n\n")
        f.write(mc[["target_dv_ms", "protected_dv_ms"]].describe()
                .to_markdown())
        f.write("\n\n## Sobol indices (target dv)\n\n")
        f.write(sob.to_markdown(index=False))
        f.write("\n\n## Negative controls\n\n")
        f.write(ndf.to_markdown(index=False))
    print(sob.to_string(index=False))
    print(ndf.to_string(index=False))


if __name__ == "__main__":
    main()
