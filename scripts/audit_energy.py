"""Phase 10 audit — energy lower bounds for a localized density increase.

The frozen Phase 1 bound heats only the air inside the patch and converts
delta to a temperature change through the isobaric relation rho'/rho =
T/T'. That relation says a density *increase* at fixed pressure requires
*cooling*: the frozen number is a magnitude proxy for "changing the state
of the patch air", not the cost of the mechanism that actually raises
density at a fixed altitude.

Thermospheric density at a fixed altitude rises when the column below is
heated and expands (the storm mechanism). This script computes that
alternative bound:

    eps    = ln(1+delta) * H(z) / (z - z_base)        (required dT/T)
    E_col  = A * cp * eps * int_{z_base}^{z} T(z') rho(z') dz'

with z_base = 120 km, A = 2 pi sigma_h^2 the patch footprint and T, rho
from NRLMSISE-00. Both bounds are thermodynamic lower bounds: they ignore
radiative and conductive losses, deposition efficiency, and the work done
against gravity in lifting the column, all of which increase the true
cost. Neither is an engineering energy estimate.

Writes results/tables/energy_bounds_audit.csv.
"""
from __future__ import annotations

import datetime
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.atmosphere.msis import density_profile  # noqa: E402
from src.energy.bounds import (  # noqa: E402
    CP_AIR, expansion_temperature_fraction, min_thermal_energy,
    orbital_energy_rate, patch_air_mass, required_heating_fraction)
from src.orbits.elements import MU, R_EARTH  # noqa: E402
from src.utils import load_config, repo_root  # noqa: E402

Z_BASE_KM = 120.0
EPOCH = datetime.datetime(2020, 6, 21, 12, 0, 0)
ALTS_KM = [300.0, 400.0, 500.0, 600.0]
SIGMA_H_KM = [100.0, 200.0, 1000.0]
SIGMA_V_KM = 30.0
DELTAS = [1.0, 5.0, 20.0]
B_REF = 30.0
WINDOW_S = 86400.0


def column_profile(regime, z_top_km, step_km=5.0):
    """(alt_km, rho, T_local) between Z_BASE_KM and z_top_km."""
    alts = np.arange(Z_BASE_KM, z_top_km + step_km, step_km)
    rho, temp = [], []
    for a in alts:
        p = density_profile(float(a), 0.0, 0.0, EPOCH, regime["f107a"],
                            regime["f107"], regime["ap"])
        rho.append(p["rho_kgm3"])
        temp.append(p["t_local_K"])
    return alts, np.array(rho), np.array(temp)


def main():
    cfg = load_config()
    root = repo_root()
    regime = cfg["atmosphere"]["regimes"]["moderate"]

    rows = []
    for alt in ALTS_KM:
        alts, rho_c, t_c = column_profile(regime, alt)
        rho_top = float(rho_c[-1])
        t_top = float(t_c[-1])
        # local scale height from the profile slope near the top
        lnrho = np.log(rho_c[-4:])
        slope = np.polyfit(alts[-4:] * 1e3, lnrho, 1)[0]
        H_m = -1.0 / slope
        # mass- and temperature-weighted column integral per unit area
        col_cp_T_rho = float(np.trapezoid(rho_c * t_c, alts * 1e3))
        col_mass = float(np.trapezoid(rho_c, alts * 1e3))

        a_orb = R_EARTH + alt * 1e3
        v = np.sqrt(MU / a_orb)
        da_dt = rho_top * a_orb * v / B_REF
        e_orb_rate = MU / (2 * a_orb ** 2) * da_dt  # W per kg of debris

        for sig_h in SIGMA_H_KM:
            area = 2.0 * np.pi * (sig_h * 1e3) ** 2
            for delta in DELTAS:
                m_patch = patch_air_mass(rho_top, sig_h * 1e3,
                                         SIGMA_V_KM * 1e3)
                dT_insitu = required_heating_fraction(delta) * t_top
                e_insitu = min_thermal_energy(m_patch, dT_insitu)

                eps = expansion_temperature_fraction(
                    delta, alt * 1e3, Z_BASE_KM * 1e3, H_m)
                e_col = area * CP_AIR * eps * col_cp_T_rho / 1.0
                rows.append(dict(
                    altitude_km=alt, sigma_h_km=sig_h,
                    sigma_v_km=SIGMA_V_KM, delta=delta,
                    rho_top_kgm3=rho_top, T_top_K=t_top,
                    H_km=H_m / 1e3,
                    patch_air_mass_kg=m_patch,
                    column_mass_kg=area * col_mass,
                    dT_insitu_K=dT_insitu,
                    E_insitu_J=e_insitu,
                    eps_column=eps,
                    dT_column_at_top_K=eps * t_top,
                    E_column_expansion_J=e_col,
                    ratio_column_to_insitu=e_col / e_insitu,
                    E_column_per_day_W=e_col / WINDOW_S,
                    orbital_removal_W_per_kg=e_orb_rate,
                ))

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(root,
                           "results/tables/energy_bounds_audit.csv"),
              index=False)
    cols = ["altitude_km", "sigma_h_km", "delta", "eps_column",
            "E_insitu_J", "E_column_expansion_J", "ratio_column_to_insitu",
            "E_column_per_day_W"]
    print(df[df.sigma_h_km == 200.0][cols].to_string(index=False))


if __name__ == "__main__":
    main()
