"""Phase 8 audit — where the fixed-pulse / idealized-bound gap comes from.

The frozen results report ~4.3e-6 m/s of extra delta-v for one Earth-fixed
Gaussian pulse and ~7.5e-3 m/s for one day of idealized on-target tracking,
a factor of ~1.7e3. Amplitude (delta_max), patch width, background density
and ballistic coefficient are identical in the two runs, so the gap cannot
come from the strength of the enhancement. This script measures the terms
of the exposure integral separately

    dv = (v_rel^2 / 2B) * <rho * delta>_t * T_window
       = (v_rel^2 / 2B) * rho_bar * delta_eff * f_in * T_window

where f_in is the fraction of the window spent inside the enhancement and
delta_eff the mean enhancement seen while inside, and checks that the
product of the measured factor ratios reproduces the observed delta-v
ratio. Writes results/tables/gap_decomposition.csv.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.analysis.exposure_class import instrument  # noqa: E402
from src.atmosphere.lookup import build_lookup, rho_fn_from_lookup  # noqa: E402
from src.experiment import make_object  # noqa: E402
from src.intervention.models import (  # noqa: E402
    GaussianPatch, TrackingPerturbation, make_delta_fn)
from src.orbits import fastprop  # noqa: E402
from src.orbits.elements import ecef_approx  # noqa: E402
from src.utils import load_config, repo_root  # noqa: E402

DELTA_MAX = 5.0
SIG_H = 200.0
SIG_V = 30.0
PULSE_T0 = 1200.0
PULSE_DUR = 7200.0
TRACK_DUR = 86400.0


def build_obj(c):
    return make_object(c["case"], c["alt_km"], c["inc_deg"], c["B"],
                       e=c["e"], raan=c["raan"], argp=c["argp"],
                       M0=c["M0"], obj_type=c["obj_type"])


def main():
    cfg = load_config()
    root = repo_root()
    lu = build_lookup(cfg["atmosphere"]["regimes"])
    rho_fn = rho_fn_from_lookup(lu, "moderate")
    cases = pd.read_csv(os.path.join(root, "data/processed/cases.csv"))
    tgt_row = cases[(cases["case"].str.startswith("A"))
                    & (cases["obj_type"] == "target")].iloc[0]
    tgt = build_obj(tgt_row)

    t_pass = PULSE_T0 + PULSE_DUR / 2.0
    r_t, _ = fastprop.position_at(tgt["el"], t_pass)
    lat0, lon0 = ecef_approx(r_t, t_pass)
    patch = GaussianPatch(lat0, lon0, tgt_row["alt_km"], DELTA_MAX,
                          SIG_H, SIG_V, t0_s=PULSE_T0,
                          duration_s=PULSE_DUR, kappa_h_m2s=1e5,
                          advection_east_ms=100.0)
    trk = TrackingPerturbation(tgt["el"], DELTA_MAX, SIG_H, SIG_V,
                               0.0, TRACK_DUR)

    scen = [("fixed_pulse", make_delta_fn([patch]), PULSE_T0,
             PULSE_T0 + PULSE_DUR),
            ("tracking_bound", trk.delta, 0.0, TRACK_DUR)]

    rows = []
    for name, fn, t0, t1 in scen:
        d = instrument(tgt, rho_fn, fn, DELTA_MAX, t0, t1, fine_dt_s=1.0)
        f_in = d["time_fraction_in_patch"]
        window = t1 - t0
        # mean enhancement while inside the patch
        delta_eff = ((d["extra_dv_ms"] / d["natural_dv_ms"] / f_in)
                     if f_in > 0 else np.nan)
        rows.append(dict(scenario=name, window_s=window,
                         time_fraction_in_patch=f_in,
                         time_in_patch_s=f_in * window,
                         peak_delta=d["peak_delta"],
                         delta_eff_in_patch=delta_eff,
                         encounter_count=d["encounter_count"],
                         extra_dv_ms=d["extra_dv_ms"],
                         natural_dv_ms=d["natural_dv_ms"]))

    df = pd.DataFrame(rows).set_index("scenario")
    p, t = df.loc["fixed_pulse"], df.loc["tracking_bound"]
    factors = pd.DataFrame([
        dict(factor="window duration",
             ratio=t["window_s"] / p["window_s"]),
        dict(factor="fraction of window inside patch",
             ratio=t["time_fraction_in_patch"]
             / p["time_fraction_in_patch"]),
        dict(factor="mean enhancement while inside",
             ratio=t["delta_eff_in_patch"] / p["delta_eff_in_patch"]),
    ])
    predicted = float(factors["ratio"].prod())
    observed = float(t["extra_dv_ms"] / p["extra_dv_ms"])
    factors = pd.concat([factors, pd.DataFrame([
        dict(factor="product of factors (predicted dv ratio)",
             ratio=predicted),
        dict(factor="observed dv ratio", ratio=observed),
        dict(factor="closure error", ratio=predicted / observed - 1.0),
    ])], ignore_index=True)

    out = df.reset_index()
    out.to_csv(os.path.join(root,
                            "results/tables/gap_decomposition.csv"),
               index=False)
    factors.to_csv(os.path.join(
        root, "results/tables/gap_decomposition_factors.csv"), index=False)
    print(out.to_string(index=False))
    print()
    print(factors.to_string(index=False))


if __name__ == "__main__":
    main()
