"""Phase 9 audit — is the uniform/localized comparison fairly matched?

The frozen control matches the *target's* exposure: uniform delta = 5
everywhere versus an on-target patch of peak delta = 5. Under that
convention localization cannot increase target benefit by construction, so
the reported gain is entirely collateral reduction. This script adds two
budget-matched conventions, under which the uniform arm is far weaker and
localization does buy target benefit:

  matched_target_exposure  uniform delta = delta_max (frozen convention)
  matched_spacetime        uniform delta_u with delta_u * V_shell =
                           delta_max * V_patch, V_patch = (2 pi)^{3/2}
                           sigma_h^2 sigma_v, V_shell a global shell at the
                           target altitude of equivalent thickness
                           sqrt(2 pi) sigma_v
  matched_thermal_energy   uniform delta_u with equal isobaric heating
                           energy, i.e. [delta_u/(1+delta_u)] * M_shell =
                           [delta_max/(1+delta_max)] * M_patch (same rho at
                           a common altitude, so this reduces to the same
                           volume ratio with the saturating delta/(1+delta)
                           weighting)

All three arms are run for the same 1-day window against the same
target/protected pairs, and absolute delta-v is reported for both objects.
Exposure is measured along the trajectory the drag itself produces (the
semi-major axis is integrated while the intervention is active), so the
localized arm is not credited with co-location it loses as the induced
drag drifts the object along track; the uniform arms are insensitive to
that drift by construction.

Writes results/tables/matched_exposure.csv.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.analysis.exposure_class import (  # noqa: E402
    classify, instrument_decaying)
from src.atmosphere.lookup import build_lookup, rho_fn_from_lookup  # noqa: E402
from src.experiment import make_object  # noqa: E402
from src.intervention.models import TrackingPerturbation  # noqa: E402
from src.orbits.elements import R_EARTH  # noqa: E402
from src.utils import load_config, repo_root  # noqa: E402

WIN = 86400.0
DELTA_MAX = 5.0
SIG_H = 200.0
SIG_V = 30.0
PAIRS = ["A", "D", "E", "G"]


def build_obj(c):
    return make_object(c["case"], c["alt_km"], c["inc_deg"], c["B"],
                       e=c["e"], raan=c["raan"], argp=c["argp"],
                       M0=c["M0"], obj_type=c["obj_type"])


def uniform_delta(delta):
    def fn(r, t):
        return delta
    return fn


def volume_ratio(alt_km, sigma_h_km, sigma_v_km):
    """V_patch / V_shell for a global shell of equivalent thickness."""
    sh = sigma_h_km * 1e3
    sv = sigma_v_km * 1e3
    v_patch = (2.0 * np.pi) ** 1.5 * sh ** 2 * sv
    r_a = R_EARTH + alt_km * 1e3
    v_shell = 4.0 * np.pi * r_a ** 2 * (np.sqrt(2.0 * np.pi) * sv)
    return v_patch / v_shell


def main():
    cfg = load_config()
    root = repo_root()
    lu = build_lookup(cfg["atmosphere"]["regimes"])
    rho_fn = rho_fn_from_lookup(lu, "moderate")
    cases = pd.read_csv(os.path.join(root, "data/processed/cases.csv"))

    rows = []
    for prefix in PAIRS:
        grp = cases[cases["case"].str.startswith(prefix)]
        tgt_row = grp[grp["obj_type"] == "target"].iloc[0]
        tgt = build_obj(tgt_row)
        fv = volume_ratio(tgt_row["alt_km"], SIG_H, SIG_V)
        d_spacetime = DELTA_MAX * fv
        # equal isobaric heating energy: x/(1+x) scales with volume
        w = DELTA_MAX / (1.0 + DELTA_MAX) * fv
        d_energy = w / (1.0 - w)
        trk = TrackingPerturbation(tgt["el"], DELTA_MAX, SIG_H, SIG_V,
                                   0.0, WIN)
        arms = [("localized_tracking", trk.delta, DELTA_MAX),
                ("matched_target_exposure", uniform_delta(DELTA_MAX),
                 DELTA_MAX),
                ("matched_spacetime", uniform_delta(d_spacetime),
                 d_spacetime),
                ("matched_thermal_energy", uniform_delta(d_energy),
                 d_energy)]
        for _, c in grp.iterrows():
            obj = build_obj(c)
            for name, fn, d_used in arms:
                d = instrument_decaying(obj, rho_fn, fn,
                                        max(d_used, 1e-300), 0.0, WIN)
                rows.append(dict(
                    pair=prefix, matching=name, case=c["case"],
                    obj_type=c["obj_type"], alt_km=c["alt_km"],
                    ephemeris=d["ephemeris"],
                    volume_ratio=fv, delta_uniform=d_used,
                    extra_dv_ms=d["extra_dv_ms"],
                    natural_dv_ms=d["natural_dv_ms"],
                    rel_to_natural=d["rel_to_natural"],
                    exposure_class=classify(d)))

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(root, "results/tables/matched_exposure.csv"),
              index=False)

    piv = df.pivot_table(index=["pair", "matching"], columns="obj_type",
                         values="extra_dv_ms", aggfunc="sum")
    print(piv.to_string())


if __name__ == "__main__":
    main()
