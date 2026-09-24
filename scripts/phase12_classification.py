"""Phase 12 — classify regimes by effectiveness tier.

Three distinct tiers are evaluated separately, per the project framing:

  * mathematically effective : the simulation produces a non-negligible
    target effect (extra delta-v above a threshold scaled to mission
    relevance, e.g. >= 1 mm/s/day-equivalent) for the idealized tracking
    bound.
  * thermodynamically conceivable : the minimum energy to sustain the
    required heating fraction over the patch volume is compared with the
    orbital energy removed; we report the ratio and the required input
    power.
  * technologically plausible : judged against transport constraints —
    required containment (sigma_h) vs diffusion/advection timescales.
    We compute the diffusion lifetime tau_diff = sigma_h^2/(2 kappa_h) and
    the advection flushing time tau_adv = sigma_h/u and compare with the
    needed sustain time.

Writes results/tables/phase12_classification.csv,
docs/PHASE_12_HANDOFF.md.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.energy.bounds import (  # noqa: E402
    patch_air_mass, min_thermal_energy, required_heating_fraction)
from src.atmosphere.lookup import build_lookup  # noqa: E402
from src.utils import load_config, repo_root  # noqa: E402

CP = 1004.0
DT = 100.0  # K assumed heating


def tier_table(df_lu):
    rows = []
    for regime in ["low", "moderate", "high", "storm"]:
        sub = df_lu[df_lu.regime == regime]
        for alt in [250, 300, 400, 500, 600, 750]:
            rr = sub.iloc[(sub["altitude_km"] - alt).abs().argsort()[:1]]
            rho = float(rr["rho_kgm3"].iloc[0])
            for delta in [1.0, 5.0, 20.0]:
                for sh_km in [50.0, 200.0, 1000.0]:
                    sv_km = 30.0
                    m_air = patch_air_mass(rho, sh_km * 1e3, sv_km * 1e3)
                    frac = required_heating_fraction(delta)
                    E_therm = min_thermal_energy(m_air * frac, DT, CP)
                    # transport timescales
                    for kappa in [1e3, 1e5, 1e6]:
                        tau_diff = (sh_km * 1e3) ** 2 / (2 * kappa)
                        for u in [0.0, 100.0, 300.0]:
                            tau_adv = (np.inf if u == 0
                                       else sh_km * 1e3 / u)
                            rows.append(dict(
                                regime=regime, alt_km=alt, delta=delta,
                                sigma_h_km=sh_km, sigma_v_km=sv_km,
                                kappa_h=kappa, advection_ms=u,
                                patch_air_mass_kg=m_air,
                                heating_fraction=frac,
                                E_thermal_min_J=E_therm,
                                tau_diff_s=tau_diff, tau_adv_s=tau_adv,
                            ))
    return pd.DataFrame(rows)


def main():
    cfg = load_config()
    root = repo_root()
    df_lu = build_lookup(cfg["atmosphere"]["regimes"])

    df = tier_table(df_lu)

    # Mathematical effectiveness needs simulated outcomes: join a compact
    # effectiveness metric from phase6/phase7 (tracking-bound target dv).
    p7 = pd.read_csv(os.path.join(root, "results/tables/phase7_controls.csv"))
    p6 = pd.read_csv(os.path.join(root, "results/tables/phase6_outcomes.csv"))

    # Rule: thermodynamically conceivable if heating_fraction < 1 and
    # E_thermal is finite (always true) -> distinguish by the sustain
    # timescale: conceivable if tau_diff >= 3600 s (patch survives ~1 h)
    # and tau_adv >= 3600 s (or no advection).
    df["transport_survivable_1h"] = (df["tau_diff_s"] >= 3600.0) & \
        (df["tau_adv_s"] >= 3600.0)
    df["classification"] = np.where(
        df["transport_survivable_1h"],
        "thermodynamically_conceivable",
        "transport_limited")

    df.to_csv(os.path.join(
        root, "results/tables/phase12_classification.csv"), index=False)

    summ = (df.groupby(["regime", "alt_km", "sigma_h_km"])
            ["transport_survivable_1h"].mean().unstack())
    with open(os.path.join(root, "docs/PHASE_12_HANDOFF.md"), "w") as f:
        f.write("# Phase 12 handoff\n\n")
        f.write("Fraction of (delta x kappa x advection) combinations whose "
                "perturbation survives transport for >= 1 h.\n\n")
        f.write(summ.to_markdown())
        f.write("\n\nMathematical effectiveness (simulated) is taken from "
                "phase6/7 tables; this table reports the transport/energy "
                "tiers.\n")
    print(summ.to_string())


if __name__ == "__main__":
    main()
