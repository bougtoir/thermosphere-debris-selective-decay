"""Shared Sobol' response function and sampling driver.

The response is the extra delta-v imparted to the case-A target under the
idealized tracking upper bound. Two cost reductions make a converged
Saltelli design affordable on a 2-core machine; both are exact or verified,
not approximations of convenience:

1. The propagation horizon is the perturbation window. Extra drag impulse is
   accumulated only while a delta window is active (`fastprop.decay_lifetime`),
   so integrating beyond the window adds exactly zero to the response.
2. The fine exposure step is 60 s rather than 10 s. For the tracking geometry
   the object sits permanently at the patch centre, so the integrand is
   smooth: mean(rho*delta) changes by < 1e-6 relative between 5 s and 60 s
   steps, and the end-to-end response by < 2e-4 over the design (checks in
   docs/SOBOL_AUDIT.md), far below the index confidence intervals. The 10 s
   default is
   kept everywhere else, where short transits through a fixed patch require
   it.

Used by scripts/phase10_uncertainty.py (production indices) and
scripts/audit_sobol.py (convergence ladder).
"""
from __future__ import annotations

import multiprocessing as mp
import os

import numpy as np
import pandas as pd
from SALib.analyze import sobol
from SALib.sample import sobol as sobol_sample

from ..atmosphere.lookup import build_lookup, rho_fn_from_lookup
from ..experiment import make_object, simulate
from ..intervention.models import TrackingPerturbation
from ..utils import load_config, repo_root

PROBLEM = {
    "num_vars": 6,
    "names": ["delta_max", "sigma_h_km", "sigma_v_km", "rho_scale",
              "B_scale", "duration_h"],
    "bounds": [[2.0, 10.0], [100.0, 400.0], [15.0, 60.0],
               [0.85, 1.15], [0.9, 1.1], [4.0, 24.0]],
}

FINE_DT_S = 60.0
N_BASE = 1024          # converged base size, see docs/SOBOL_AUDIT.md

_G: dict = {}


def init_worker():
    cfg = load_config()
    lu = build_lookup(cfg["atmosphere"]["regimes"])
    cases = pd.read_csv(os.path.join(repo_root(),
                                     "data/processed/cases.csv"))
    c = cases[(cases["case"].str.startswith("A"))
              & (cases["obj_type"] == "target")].iloc[0]
    _G["obj"] = make_object(c["case"], c["alt_km"], c["inc_deg"], c["B"],
                            e=c["e"], raan=c["raan"], argp=c["argp"],
                            M0=c["M0"], obj_type="target")
    _G["rho_fn"] = rho_fn_from_lookup(lu, "moderate")


def evaluate(x):
    """Target extra delta-v (m/s) for one design point."""
    if not _G:
        init_worker()
    d, sh, sv, rs, bs, dur_h = x
    dur = float(dur_h) * 3600.0
    obj = dict(_G["obj"])
    obj["B"] = obj["B"] * bs
    trk = TrackingPerturbation(obj["el"], d, sh, sv, 0.0, dur)
    res = simulate(obj, _G["rho_fn"], dur, dt_day=0.25,
                   delta_windows=[(0.0, dur)], delta_fn=trk.delta,
                   rho_scale=rs, fine_dt_s=FINE_DT_S)
    return res["extra_deltav_ms"]


def sample(n_base, seed=None):
    """Saltelli design (calc_second_order=False) -> n_base*(d+2) points."""
    kw = {"calc_second_order": False}
    if seed is not None:
        kw["seed"] = int(seed)
    return sobol_sample.sample(PROBLEM, int(n_base), **kw)


def run(n_base, pool=None, seed=None):
    """Return (X, Y, Si) for a Saltelli base of n_base."""
    X = sample(n_base, seed=seed)
    pts = [list(x) for x in X]
    if pool is None:
        Y = np.array([evaluate(x) for x in pts])
    else:
        Y = np.array(pool.map(evaluate, pts, chunksize=8))
    if not np.all(np.isfinite(Y)):
        raise RuntimeError("non-finite Sobol' response; refusing to analyse")
    return X, Y, sobol.analyze(PROBLEM, Y, calc_second_order=False)


def make_pool():
    return mp.Pool(processes=max(mp.cpu_count(), 1), initializer=init_worker)


def indices_frame(si):
    return pd.DataFrame(dict(param=PROBLEM["names"], S1=si["S1"],
                             ST=si["ST"], S1_conf=si["S1_conf"],
                             ST_conf=si["ST_conf"]))
