"""Phase 11 — dimensionless scaling collapse.

For the tracking-bound scenario the theory predicts, for a near-circular
orbit held inside a constant enhancement delta for time T:

    extra_dv = (rho * delta * v^2 / (2 B)) * T_eff

where T_eff is the in-patch residence time. Define the dimensionless
groups

    Pi_benefit = extra_dv * B / (rho * delta * v^2 * T)
    Pi_collateral = protected_dv / target_dv

and test collapse over a synthetic population sample: simulated extra_dv
under a uniform enhancement (where T_eff = T exactly) should collapse onto
Pi_benefit = 1 across altitudes, B, delta, regimes.

Writes results/tables/phase11_scaling.csv, docs/PHASE_11_HANDOFF.md.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.experiment import make_object, simulate  # noqa: E402
from src.atmosphere.lookup import build_lookup, rho_fn_from_lookup  # noqa: E402
from src.orbits.elements import MU, R_EARTH  # noqa: E402
from src.utils import load_config, rng, repo_root  # noqa: E402

HORIZON_S = 40 * 86400.0
T_ENH = 86400.0


def uniform_delta(d, dur):
    def fn(r, t):
        return d if 0.0 <= t <= dur else 0.0
    return fn


def main():
    cfg = load_config()
    root = repo_root()
    r = rng()
    df_lu = build_lookup(cfg["atmosphere"]["regimes"])
    pop = pd.read_csv(os.path.join(root, "data/processed/population.csv"))
    sample = pop.sample(n=120, random_state=cfg["seed"])

    rows = []
    for regime in ["low", "moderate", "high", "storm"]:
        rho_fn = rho_fn_from_lookup(df_lu, regime)
        for _, p in sample.iterrows():
            d = float(r.choice([0.5, 1.0, 2.0, 5.0]))
            obj = make_object(p["obj_id"], p["alt_km"], p["inc_deg"], p["B"],
                              e=p["e"], raan=p["raan"], argp=p["argp"],
                              M0=p["M0"], obj_type="target")
            res = simulate(obj, rho_fn, HORIZON_S, dt_day=0.25,
                           delta_windows=[(0.0, T_ENH)],
                           delta_fn=uniform_delta(d, T_ENH))
            a0 = R_EARTH + p["alt_km"] * 1000.0
            v = np.sqrt(MU / a0)
            rho = rho_fn(np.array([a0, 0.0, 0.0]), 0.0)
            pred = rho * d * v**2 * T_ENH / (2.0 * p["B"])
            rows.append(dict(regime=regime, obj_id=p["obj_id"],
                             alt_km=p["alt_km"], B=p["B"], delta=d,
                             rho=rho, v_ms=v, T_s=T_ENH,
                             extra_dv_sim=res["extra_deltav_ms"],
                             extra_dv_pred=pred,
                             Pi_benefit=(res["extra_deltav_ms"] / pred
                                         if pred > 0 else np.nan)))

    df = pd.DataFrame(rows)
    # collapse quality: dispersion of Pi_benefit around 1
    grp = df.groupby("regime")["Pi_benefit"].agg(["mean", "std", "count"])
    df.to_csv(os.path.join(root, "results/tables/phase11_scaling.csv"),
              index=False)

    logx = np.log10(df["extra_dv_pred"].clip(lower=1e-300))
    logy = np.log10(df["extra_dv_sim"].clip(lower=1e-300))
    mask = np.isfinite(logx) & np.isfinite(logy)
    slope, intercept = np.polyfit(logx[mask], logy[mask], 1)
    r2 = 1 - np.sum((logy[mask] - (slope * logx[mask] + intercept)) ** 2) \
        / np.sum((logy[mask] - logy[mask].mean()) ** 2)

    with open(os.path.join(root, "docs/PHASE_11_HANDOFF.md"), "w") as f:
        f.write("# Phase 11 handoff\n\n")
        f.write("Dimensionless collapse of simulated extra delta-v onto "
                "Pi_benefit = dv*B/(rho*delta*v*T) = 1 (uniform "
                "enhancement, T_eff = T).\n\n")
        f.write(grp.to_markdown())
        f.write(f"\n\nlog-log fit: slope={slope:.3f}, "
                f"intercept={intercept:.3f}, R2={r2:.4f}\n")
    print(grp.to_string())
    print(f"slope={slope:.3f} R2={r2:.4f}")


if __name__ == "__main__":
    main()
