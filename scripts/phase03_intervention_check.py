"""Phase 3 — intervention model sanity checks.

Verifies each perturbation class reproduces its analytic amplitude/shape and
that the encounter machinery finds crossings. Writes
results/tables/phase3_intervention_checks.csv and docs/PHASE_3_HANDOFF.md.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.intervention.models import (GaussianPatch, TopHatCylinder,  # noqa: E402
                                     MovingPerturbation, make_delta_fn)
from src.orbits import fastprop  # noqa: E402
from src.orbits.elements import R_EARTH, elements_to_state, ecef_approx  # noqa: E402
from src.experiment import make_object  # noqa: E402
from src.utils import repo_root  # noqa: E402


def main():
    root = repo_root()
    rows = []

    g = GaussianPatch(0.0, 0.0, 400.0, delta_max=5.0,
                      sigma_h_km=100.0, sigma_v_km=20.0,
                      t0_s=0.0, duration_s=3600.0)
    # peak value near center at small t
    r = np.array([R_EARTH + 400e3, 0.0, 0.0])
    val = g.delta(r, 1.0)
    w = 0.5 * (1 - np.cos(np.pi * 1.0 / 180.0))
    expect = 5.0 * w
    rows.append(dict(model="gaussian_peak", expected=expect, got=val,
                     passed=abs(val - expect) / expect < 0.05))
    # vertical falloff: 1 sigma_v up
    r_up = np.array([R_EARTH + 420e3, 0.0, 0.0])
    # at t small, lon shift negligible
    v2 = g.delta(r_up, 1.0) / w
    exp2 = 5.0 * np.exp(-0.5)
    rows.append(dict(model="gaussian_vertical", expected=exp2, got=v2,
                     passed=abs(v2 - exp2) / exp2 < 0.05))

    th = TopHatCylinder(0, 0, 400, 2.0, 200.0, 30.0, 0, 3600)
    rows.append(dict(model="tophat_inside", expected=2.0,
                     got=th.delta(r, 10.0), passed=th.delta(r, 10.0) == 2.0))
    rpole = np.array([0.0, 0.0, R_EARTH + 400e3])
    rows.append(dict(model="tophat_outside", expected=0.0,
                     got=th.delta(rpole, 10.0),
                     passed=th.delta(rpole, 10.0) == 0.0))

    mv = MovingPerturbation(0, 0, 400, 1.5, 50, 10, 0, 3600,
                            dlon_degps=0.0, dlat_degps=0.0)
    rows.append(dict(model="moving_static_equiv", expected=1.5,
                     got=mv.delta(r, 5.0) > 0, passed=mv.delta(r, 5.0) > 0))

    # encounter check: object at 400 km, inc 51.6, patch on its ground track.
    # place patch at lat/lon where a pass occurs: sample trajectory for a
    # day, pick a point, center patch there.
    obj = make_object("tgt", 400.0, 51.6, 30.0, M0=0.0)
    rho_fn = lambda r, t: 1e-15  # noqa: E731
    # find a trajectory point at t_pass
    r_pass, _ = fastprop.position_at(obj["el"], 5000.0)
    lat_p, lon_p = ecef_approx(r_pass, 5000.0)
    g2 = GaussianPatch(lat_p, lon_p, 400.0, delta_max=3.0,
                       sigma_h_km=200.0, sigma_v_km=30.0,
                       t0_s=4000.0, duration_s=4000.0)
    delta_fn = make_delta_fn([g2])
    m = fastprop.exposure_metrics(obj["el"], rho_fn, delta_fn,
                                  4000.0, 8000.0, fine_dt_s=10.0)
    rows.append(dict(model="encounter_detected",
                     expected="mean_rho_delta>0",
                     got=m["mean_rho_delta"],
                     passed=m["mean_rho_delta"] > 0))
    rows.append(dict(model="encounter_count",
                     expected=">=1", got=m["encounter_count"],
                     passed=m["encounter_count"] >= 1))

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(root, "results/tables/phase3_intervention_checks.csv"),
              index=False)
    ok = bool(df["passed"].all())
    with open(os.path.join(root, "docs/PHASE_3_HANDOFF.md"), "w") as f:
        f.write("# Phase 3 handoff\n\n")
        f.write(f"Intervention model checks: {'all pass' if ok else 'FAILURES'}\n\n")
        f.write(df.to_markdown(index=False))
    print(df.to_string(index=False))
    print("phase3:", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    main()
