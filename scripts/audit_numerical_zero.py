"""Numerical-zero / selectivity audit (revision Phase 3).

The frozen selectivity table reports ratios up to 1.2e80 because the
protected object of pair D never encounters the patch: its delta-v of
1.3e-84 m/s is the far tail of a Gaussian evaluated tens of sigma away.
Such ratios are arithmetic, not physics. This script instruments the
exposure integral to record, for every object and scenario, *why* its
collateral delta-v is small, and classifies the outcome:

  no_encounter               min separation > 6 sigma (peak delta < 1.5e-8,
                             below the 1e-6 in-patch threshold): the object
                             never meets the patch.
  below_numerical_resolution extra delta-v < 1e-12 of the natural drag
                             delta-v over the same window: unresolvable
                             against the background integration.
  gaussian_tail              nonzero but < 1e-3 of natural drag: a
                             mathematical tail, physically negligible.
  physical_exposure          >= 1e-3 of the natural drag delta-v over the
                             same window: a real, if small, perturbation.

The ratio column is retained only for physically exposed pairs; elsewhere it
is reported as not meaningful. Absolute delta-v and encounter status are the
primary quantities.

Writes results/tables/numerical_zero_audit.csv.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.analysis.exposure_class import (  # noqa: E402
    classify, instrument, ratio_status)
from src.atmosphere.lookup import build_lookup, rho_fn_from_lookup  # noqa: E402
from src.experiment import make_object  # noqa: E402
from src.intervention.models import TrackingPerturbation  # noqa: E402
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


def uniform_delta(delta_max):
    def fn(r, t):
        return delta_max
    return fn


def main():
    cfg = load_config()
    root = repo_root()
    lu = build_lookup(cfg["atmosphere"]["regimes"])
    rho_fn = rho_fn_from_lookup(lu, "moderate")
    cases = pd.read_csv(os.path.join(root, "data/processed/cases.csv"))

    rows = []
    for prefix in PAIRS:
        tgt_row = cases[(cases["case"].str.startswith(prefix))
                        & (cases["obj_type"] == "target")].iloc[0]
        tgt = build_obj(tgt_row)
        trk = TrackingPerturbation(tgt["el"], DELTA_MAX, SIG_H, SIG_V,
                                   0.0, WIN)
        for _, c in cases[cases["case"].str.startswith(prefix)].iterrows():
            obj = build_obj(c)
            for scen, fn in [("uniform", uniform_delta(DELTA_MAX)),
                             ("localized_tracking", trk.delta)]:
                d = instrument(obj, rho_fn, fn, DELTA_MAX, 0.0, WIN)
                d.update(pair=prefix, case=c["case"],
                         obj_type=c["obj_type"], scenario=scen,
                         alt_km=c["alt_km"], inc_deg=c["inc_deg"],
                         B_kgm2=c["B"])
                d["exposure_class"] = classify(d)
                rows.append(d)

    df = pd.DataFrame(rows)[[
        "scenario", "pair", "case", "obj_type", "alt_km", "inc_deg",
        "B_kgm2", "peak_delta", "n_sigma_closest", "encounter_count",
        "time_fraction_in_patch", "extra_dv_ms", "natural_dv_ms",
        "rel_to_natural", "exposure_class"]]
    out = os.path.join(root, "results/tables/numerical_zero_audit.csv")
    df.to_csv(out, index=False)

    # pair-level selectivity with meaningfulness flag
    summ = []
    for scen in ["uniform", "localized_tracking"]:
        s = df[df.scenario == scen]
        for p in PAIRS:
            q = s[s.pair == p]
            t = q[q.obj_type == "target"]
            pr = q[q.obj_type == "protected"]
            tdv = float(t["extra_dv_ms"].sum())
            pdv = float(pr["extra_dv_ms"].sum())
            cls = pr["exposure_class"].iloc[0] if len(pr) else "none"
            status = ratio_status(cls)
            meaningful = status == "physical"
            summ.append(dict(
                scenario=scen, pair=p, target_dv_ms=tdv,
                protected_dv_ms=pdv,
                protected_class=cls,
                protected_n_sigma=float(pr["n_sigma_closest"].iloc[0])
                if len(pr) else np.nan,
                protected_encounters=int(pr["encounter_count"].iloc[0])
                if len(pr) else 0,
                selectivity_ratio=(tdv / pdv) if pdv > 0 else np.nan,
                ratio_status=status,
                ratio_meaningful=meaningful))
    sdf = pd.DataFrame(summ)
    sdf.to_csv(os.path.join(root,
                            "results/tables/selectivity_classified.csv"),
               index=False)
    print(df.to_string(index=False))
    print()
    print(sdf.to_string(index=False))


if __name__ == "__main__":
    main()
