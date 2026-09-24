"""Phase 4 — synthetic populations and named cases A-F.

Writes data/processed/population.csv (factorial grid) and
data/processed/cases.csv (target debris vs protected spacecraft cases).
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.utils import load_config, rng, repo_root  # noqa: E402


def main():
    cfg = load_config()
    root = repo_root()
    r = rng()

    # Factorial population (synthetic debris-like distribution)
    alts = np.array([350, 400, 450, 500, 550, 600, 700, 800])
    incs = np.array([28.5, 51.6, 63.4, 87.4, 97.4, 98.7])
    Bs = np.array([3, 5, 10, 20, 30, 50, 80, 120, 200])
    n = 2000
    rows = []
    for i in range(n):
        rows.append(dict(
            obj_id=f"pop{i:04d}",
            alt_km=float(r.choice(alts)),
            inc_deg=float(r.choice(incs) + r.normal(0, 1.0)),
            e=float(abs(r.normal(0.002, 0.002))),
            raan=float(r.uniform(0, 2 * np.pi)),
            argp=float(r.uniform(0, 2 * np.pi)),
            M0=float(r.uniform(0, 2 * np.pi)),
            B=float(r.choice(Bs)),
        ))
    pop = pd.DataFrame(rows)
    pop.to_csv(os.path.join(root, "data/processed/population.csv"), index=False)

    # Cases A-F: target debris vs protected spacecraft
    cases = [
        # A: high-A/m debris ~400 km vs a protected satellite in similar orbit
        dict(case="A_target_highAm_400", obj_type="target", alt_km=400, inc_deg=51.6, B=5.0, raan=0.0, M0=0.0),
        dict(case="A_protected_400", obj_type="protected", alt_km=400, inc_deg=51.6, B=80.0, raan=0.0, M0=0.15),
        # B: compact high-B debris ~500 km
        dict(case="B_target_compact_500", obj_type="target", alt_km=500, inc_deg=97.4, B=120.0, raan=1.0, M0=2.0),
        dict(case="B_protected_500", obj_type="protected", alt_km=500, inc_deg=97.4, B=100.0, raan=1.1, M0=3.0),
        # C: synthetic breakup fragments around 450 km
        *[
            dict(case=f"C_frag_{k:02d}", obj_type="target", alt_km=450 + (k % 5) * 5,
                 inc_deg=97.4, B=float(8 + 3 * k), raan=0.5 + 0.01 * k,
                 M0=0.3 * k) for k in range(10)
        ],
        dict(case="C_protected_450", obj_type="protected", alt_km=450, inc_deg=97.4, B=90.0, raan=0.5, M0=2.2),
        # D: target sharing a shell with protected spacecraft
        dict(case="D_target_550", obj_type="target", alt_km=550, inc_deg=97.6, B=20.0, raan=2.0, M0=1.0),
        dict(case="D_protected_550", obj_type="protected", alt_km=550, inc_deg=97.6, B=85.0, raan=2.0, M0=1.6),
        # E: geometrically distinct target (different inclination/RAAN)
        dict(case="E_target_400_i28", obj_type="target", alt_km=400, inc_deg=28.5, B=15.0, raan=4.0, M0=0.5),
        dict(case="E_protected_400_i51", obj_type="protected", alt_km=400, inc_deg=51.6, B=70.0, raan=4.0, M0=0.5),
        # F: >700 km negative control
        dict(case="F_target_750", obj_type="target", alt_km=750, inc_deg=98.0, B=25.0, raan=1.5, M0=0.8),
        dict(case="F_protected_750", obj_type="protected", alt_km=750, inc_deg=98.0, B=100.0, raan=1.5, M0=1.8),
        # G: very low altitude where baseline decay is fast and intervention
        # outcomes are measurable within a short horizon
        dict(case="G_target_250", obj_type="target", alt_km=250, inc_deg=51.6, B=10.0, raan=3.0, M0=0.2),
        dict(case="G_protected_250", obj_type="protected", alt_km=250, inc_deg=51.6, B=80.0, raan=3.0, M0=0.8),
    ]
    cdf = pd.DataFrame(cases)
    for col, default in [("e", 0.001), ("argp", 0.0)]:
        cdf[col] = default
    cdf.to_csv(os.path.join(root, "data/processed/cases.csv"), index=False)

    with open(os.path.join(root, "docs/PHASE_4_HANDOFF.md"), "w") as f:
        f.write("# Phase 4 handoff\n\n")
        f.write(f"Synthetic population: {len(pop)} objects "
                "(factorial alt x inc x B + randomized phases).\n\n")
        f.write(f"Cases A-F: {len(cdf)} objects "
                f"({(cdf.obj_type == 'target').sum()} targets, "
                f"{(cdf.obj_type == 'protected').sum()} protected).\n\n"
                "All targets are synthetic; no named operational spacecraft "
                "are used.\n")
    print(f"population: {len(pop)}, cases: {len(cdf)}")


if __name__ == "__main__":
    main()
