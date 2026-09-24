"""make quick — lightweight end-to-end smoke run.

Runs the full pipeline shape on one case pair (A) in the moderate regime:
density lookup (cached), baseline, fixed pulse, tracking bound, uniform
control, selectivity — and writes results/tables/quick_summary.csv plus
one figure. Intended to verify the toolchain end-to-end in ~1 minute,
not to produce publishable numbers.
"""
from __future__ import annotations

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.intervention.models import (  # noqa: E402
    GaussianPatch, TrackingPerturbation, make_delta_fn)
from src.orbits import fastprop  # noqa: E402
from src.orbits.elements import ecef_approx  # noqa: E402
from src.experiment import make_object, simulate  # noqa: E402
from src.atmosphere.lookup import build_lookup, rho_fn_from_lookup  # noqa: E402
from src.utils import load_config, repo_root  # noqa: E402

HORIZON_S = 40 * 86400.0


def main():
    cfg = load_config()
    root = repo_root()
    df_lu = build_lookup({"moderate": cfg["atmosphere"]["regimes"]
                          ["moderate"]})
    rho_fn = rho_fn_from_lookup(df_lu, "moderate")
    cases = pd.read_csv(os.path.join(root, "data/processed/cases.csv"))
    if not os.path.exists(os.path.join(root, "data/processed/cases.csv")):
        raise SystemExit("run `make phase4` first")

    pair = cases[cases["case"].str.startswith("A")]
    objs = {}
    for _, c in pair.iterrows():
        objs[c["case"]] = make_object(c["case"], c["alt_km"], c["inc_deg"],
                                      c["B"], e=c["e"], raan=c["raan"],
                                      argp=c["argp"], M0=c["M0"],
                                      obj_type=c["obj_type"])
    tgt_key = [k for k in objs if "target" in k][0]
    tgt = objs[tgt_key]

    rows = []
    t_pass = 3000.0
    r_t, _ = fastprop.position_at(tgt["el"], t_pass)
    lat0, lon0 = ecef_approx(r_t, t_pass)
    g = GaussianPatch(lat0, lon0, tgt["alt_km"], 5.0, 200.0, 30.0,
                      t0_s=t_pass - 1800.0, duration_s=7200.0,
                      kappa_h_m2s=1e5, advection_east_ms=100.0)
    trk = TrackingPerturbation(tgt["el"], 5.0, 200.0, 30.0, 0.0, 86400.0)

    def uniform(r, t):
        return 5.0 if 0.0 <= t <= 86400.0 else 0.0

    for k, obj in objs.items():
        for scen, dfn, win in [
                ("baseline", None, None),
                ("fixed_pulse", make_delta_fn([g]),
                 [(t_pass - 1800.0, t_pass + 5400.0)]),
                ("tracking", trk.delta, [(0.0, 86400.0)]),
                ("uniform", uniform, [(0.0, 86400.0)])]:
            res = simulate(obj, rho_fn, HORIZON_S, dt_day=0.25,
                           delta_windows=win, delta_fn=dfn)
            rows.append(dict(scenario=scen, case=k,
                             obj_type=obj["obj_type"],
                             extra_deltav_ms=res["extra_deltav_ms"],
                             a_drop_km=res["start_a_km"]
                             - res["final_a_km"],
                             encounter_count=res["encounter_count"]))
    df = pd.DataFrame(rows)
    out = os.path.join(root, "results/tables/quick_summary.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_csv(out, index=False)

    fig, ax = plt.subplots(figsize=(5, 3.5))
    piv = df.pivot(index="case", columns="scenario",
                   values="extra_deltav_ms")
    piv.clip(lower=1e-20).plot(kind="bar", ax=ax)
    ax.set_yscale("log")
    ax.set_ylabel("extra $\\Delta v$ [m/s]")
    fig.tight_layout()
    os.makedirs(os.path.join(root, "results/figures"), exist_ok=True)
    fig.savefig(os.path.join(root, "results/figures/quick_summary.png"),
                dpi=150)
    print(df.to_string(index=False))
    print("quick run complete ->", out)


if __name__ == "__main__":
    main()
