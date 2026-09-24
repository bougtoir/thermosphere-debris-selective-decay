"""Sobol' convergence audit (revision Phase 2).

Three steps, in order:

1. EXACT REPRODUCTION of the frozen `results/tables/phase10_sobol.csv`,
   re-running the original code path (legacy `SALib.sample.saltelli`,
   Saltelli base N=32, 40-day horizon, 10 s fine exposure step) and
   comparing index-by-index against the frozen file.

2. RESPONSE-EQUIVALENCE CHECK of the cost-reduced response used for the
   convergence ladder (window-length horizon, 60 s fine step) against the
   original response on the same design points. Extra impulse accrues only
   inside the perturbation window, so the horizon truncation is exact; the
   step change is verified numerically here.

3. CONVERGENCE LADDER at Saltelli bases N = 32, 256, 512, 1024, 2048
   (8N model evaluations each) with the production sampler
   (`SALib.sample.sobol`, scrambled, seeded from config), reporting S1, ST,
   their bootstrap confidence intervals and any ordering violation
   (S1 - ST exceeding the combined CI). Indices are never clipped.

Writes results/tables/sobol_convergence.csv and
results/tables/sobol_reproduction_check.csv.
"""
from __future__ import annotations

import os
import sys
import time
import warnings

import numpy as np
import pandas as pd
from SALib.analyze import sobol as sobol_analyze

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.atmosphere.lookup import build_lookup, rho_fn_from_lookup  # noqa: E402
from src.experiment import make_object, simulate  # noqa: E402
from src.intervention.models import TrackingPerturbation  # noqa: E402
from src.uq import sobol_response as sr  # noqa: E402
from src.utils import load_config, repo_root  # noqa: E402

N_LADDER = [32, 256, 512, 1024, 2048]
LEGACY_HORIZON_S = 40 * 86400.0
LEGACY_FINE_DT_S = 10.0


def legacy_response(x, obj, rho_fn):
    """The frozen Phase-10 response: 40-day horizon, 10 s fine step."""
    d, sh, sv, rs, bs, dur_h = x
    o = dict(obj)
    o["B"] = obj["B"] * bs
    trk = TrackingPerturbation(o["el"], d, sh, sv, 0.0, dur_h * 3600.0)
    res = simulate(o, rho_fn, LEGACY_HORIZON_S, dt_day=0.25,
                   delta_windows=[(0.0, dur_h * 3600.0)],
                   delta_fn=trk.delta, rho_scale=rs,
                   fine_dt_s=LEGACY_FINE_DT_S)
    return res["extra_deltav_ms"]


def main():
    cfg = load_config()
    root = repo_root()
    lu = build_lookup(cfg["atmosphere"]["regimes"])
    rho_fn = rho_fn_from_lookup(lu, "moderate")
    cases = pd.read_csv(os.path.join(root, "data/processed/cases.csv"))
    c = cases[(cases["case"].str.startswith("A"))
              & (cases["obj_type"] == "target")].iloc[0]
    obj = make_object(c["case"], c["alt_km"], c["inc_deg"], c["B"],
                      e=c["e"], raan=c["raan"], argp=c["argp"],
                      M0=c["M0"], obj_type="target")

    # ---- step 1: exact reproduction of the frozen indices ----
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from SALib.sample import saltelli
        X0 = saltelli.sample(sr.PROBLEM, 32, calc_second_order=False)
    t0 = time.time()
    Y_legacy = np.array([legacy_response(x, obj, rho_fn) for x in X0])
    si0 = sobol_analyze.analyze(sr.PROBLEM, Y_legacy,
                                calc_second_order=False)
    frozen = pd.read_csv(os.path.join(root,
                                      "results/tables/phase10_sobol.csv"))
    rep = frozen.merge(sr.indices_frame(si0), on="param",
                       suffixes=("_frozen", "_rerun"))
    rep["S1_abs_diff"] = (rep["S1_frozen"] - rep["S1_rerun"]).abs()
    rep["ST_abs_diff"] = (rep["ST_frozen"] - rep["ST_rerun"]).abs()

    # ---- step 2: response equivalence of the cost-reduced evaluation ----
    sr.init_worker()
    Y_fast = np.array([sr.evaluate(x) for x in X0[:64]])
    rel = np.abs(Y_fast - Y_legacy[:64]) / np.maximum(Y_legacy[:64], 1e-300)
    rep["max_response_rel_diff"] = float(rel.max())
    rep.to_csv(os.path.join(root,
                            "results/tables/sobol_reproduction_check.csv"),
               index=False)
    print(rep.to_string(index=False))
    print(f"legacy reproduction: {time.time() - t0:.0f}s, "
          f"max |S1 diff| = {rep['S1_abs_diff'].max():.2e}, "
          f"max response rel diff = {rel.max():.2e}", flush=True)

    # ---- step 3: convergence ladder ----
    rows = []
    with sr.make_pool() as pool:
        for N in N_LADDER:
            t = time.time()
            X, Y, si = sr.run(N, pool=pool, seed=cfg["seed"])
            dt = time.time() - t
            for j, name in enumerate(sr.PROBLEM["names"]):
                s1, st = si["S1"][j], si["ST"][j]
                rows.append(dict(
                    N_base=N, n_model_evals=len(X), param=name,
                    S1=s1, S1_conf=si["S1_conf"][j],
                    ST=st, ST_conf=si["ST_conf"][j],
                    S1_minus_ST=s1 - st,
                    ordering_violation=bool(
                        s1 - st > si["S1_conf"][j] + si["ST_conf"][j]),
                    sum_S1=float(np.sum(si["S1"])),
                    y_mean=float(Y.mean()), y_std=float(Y.std()),
                    wall_s=dt))
            print(f"N={N} evals={len(X)} {dt:.0f}s "
                  f"max(S1-ST)={max(si['S1'] - si['ST']):+.3f} "
                  f"sumS1={np.sum(si['S1']):.3f}", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(root, "results/tables/sobol_convergence.csv"),
              index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
