"""Phase 6 — per-object outcomes for cases A-G under three scenarios.

Scenarios per object (moderate regime):
  * baseline       : natural background drag only
  * fixed_pulse    : one ECEF-fixed Gaussian patch (delta=5, sigma_h=200 km,
                     sigma_v=30 km, 2 h window, kappa=1e5 m^2/s, 100 m/s
                     eastward advection) centered on the case target's ground
                     position mid-window
  * tracking       : idealized upper bound — a Gaussian enhancement that
                     follows the case target for 1 day (same delta, sigmas)

Outcomes per object x scenario: lifetime, delta lifetime, final semimajor
axis change, encounter count, extra drag impulse, equivalent delta-v,
orbital energy removed per kg, reentry flag. Selectivity ratios are only
meaningful paired with absolute collateral — computed in Phase 7.

Writes results/tables/phase6_outcomes.csv, docs/PHASE_6_HANDOFF.md.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.intervention.models import (  # noqa: E402
    GaussianPatch, TrackingPerturbation, make_delta_fn)
from src.orbits import fastprop  # noqa: E402
from src.orbits.elements import ecef_approx, R_EARTH, MU  # noqa: E402
from src.experiment import make_object, simulate  # noqa: E402
from src.atmosphere.lookup import build_lookup, rho_fn_from_lookup  # noqa: E402
from src.utils import load_config, repo_root  # noqa: E402

T_MAX_D = 5 * 365.25   # 5-year horizon
DELTA_MAX = 5.0
SIG_H = 200.0
SIG_V = 30.0
PULSE_T0 = 1200.0
PULSE_DUR = 7200.0
TRACK_T0 = 0.0
TRACK_DUR = 86400.0


def build_obj(c):
    return make_object(c["case"], c["alt_km"], c["inc_deg"], c["B"],
                       e=c["e"], raan=c["raan"], argp=c["argp"],
                       M0=c["M0"], obj_type=c["obj_type"])


def main():
    cfg = load_config()
    root = repo_root()
    df_lu = build_lookup(cfg["atmosphere"]["regimes"])
    cases = pd.read_csv(os.path.join(root, "data/processed/cases.csv"))

    rows = []
    for regime in ["moderate"]:
        rho_fn = rho_fn_from_lookup(df_lu, regime)
        for _, c in cases.iterrows():
            obj = build_obj(c)
            prefix = c["case"].split("_")[0]
            tgt_row = cases[(cases["case"].str.startswith(prefix))
                            & (cases["obj_type"] == "target")].iloc[0]
            tgt = build_obj(tgt_row)

            base = simulate(obj, rho_fn, T_MAX_D * 86400.0, dt_day=0.5)

            # --- fixed ECEF pulse on the target's ground track ---
            t_pass = PULSE_T0 + PULSE_DUR / 2.0
            r_t, _ = fastprop.position_at(tgt["el"], t_pass)
            lat0, lon0 = ecef_approx(r_t, t_pass)
            g = GaussianPatch(lat0, lon0, tgt_row["alt_km"], DELTA_MAX,
                              SIG_H, SIG_V, t0_s=PULSE_T0,
                              duration_s=PULSE_DUR, kappa_h_m2s=1e5,
                              advection_east_ms=100.0)
            dfn = make_delta_fn([g])
            pulse = simulate(obj, rho_fn, T_MAX_D * 86400.0, dt_day=0.5,
                             delta_windows=[(PULSE_T0,
                                             PULSE_T0 + PULSE_DUR)],
                             delta_fn=dfn)

            # --- idealized tracking bound ---
            trk = TrackingPerturbation(tgt["el"], DELTA_MAX, SIG_H, SIG_V,
                                       TRACK_T0, TRACK_DUR)
            track = simulate(obj, rho_fn, T_MAX_D * 86400.0, dt_day=0.5,
                             delta_windows=[(TRACK_T0,
                                             TRACK_T0 + TRACK_DUR)],
                             delta_fn=trk.delta)

            for scen, res in [("baseline", base), ("fixed_pulse", pulse),
                              ("tracking", track)]:
                E_orb = 0.5 * MU * (1.0 / (res["final_a_km"] * 1000.0)
                                    - 1.0 / (base["final_a_km"] * 1000.0))
                rows.append(dict(
                    regime=regime, scenario=scen,
                    case=c["case"], obj_type=c["obj_type"],
                    alt_km=c["alt_km"], inc_deg=c["inc_deg"], B=c["B"],
                    lifetime_d=res["lifetime_days"],
                    delta_lifetime_d=base["lifetime_days"]
                    - res["lifetime_days"],
                    delta_a_km=base["final_a_km"] - res["final_a_km"],
                    encounter_count=res["encounter_count"],
                    extra_impulse_ms=res["extra_drag_impulse_ms"],
                    extra_deltav_ms=res["extra_deltav_ms"],
                    orbital_energy_removed_J_perkg=E_orb,
                    reentry=res["reentry"],
                ))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(root, "results/tables/phase6_outcomes.csv"),
              index=False)
    with open(os.path.join(root, "docs/PHASE_6_HANDOFF.md"), "w") as f:
        f.write("# Phase 6 handoff\n\n")
        f.write("Scenarios: baseline / fixed_pulse (ECEF-fixed 2 h patch) / "
                "tracking (idealized on-target bound, 1 day).\n\n")
        f.write(df.to_markdown(index=False))
    print(df[df.scenario != "baseline"][[
        "scenario", "case", "obj_type", "delta_lifetime_d", "delta_a_km",
        "encounter_count", "extra_deltav_ms"]].to_string(index=False))


if __name__ == "__main__":
    main()
