"""Energy accounting: thermodynamic lower bounds vs orbital energy removed."""
from __future__ import annotations

import numpy as np

from ..orbits.elements import MU, R_EARTH

CP_AIR = 1004.0  # J/kg/K


def patch_air_mass(rho_kgm3, sigma_h_m, sigma_v_m):
    """Mass of air inside a 3-D Gaussian perturbation footprint (kg).

    For a horizontal Gaussian (2-D) times vertical Gaussian:
        M = rho * (2 pi sigma_h^2) * (sqrt(2 pi) sigma_v)
    """
    return rho_kgm3 * (2.0 * np.pi * sigma_h_m**2) * (np.sqrt(2.0 * np.pi) * sigma_v_m)


def min_thermal_energy(m_air_kg, delta_T_K, cp=CP_AIR):
    """Optimistic lower bound E_min = m_air cp dT (J)."""
    return m_air_kg * cp * delta_T_K


def orbital_energy(a1_m, a2_m, m_kg, mu=MU):
    """Orbital energy change m*( -mu/2a2 + mu/2a1 ) removed (positive = loss)."""
    return 0.5 * m_kg * mu * (1.0 / a2_m - 1.0 / a1_m)


def orbital_energy_rate(a_m, da_dt_ms, m_kg, mu=MU):
    """dE_orb/dt = (mu m / 2 a^2) * |da/dt| (W) for decay da/dt<0."""
    return m_kg * mu * abs(da_dt_ms) / (2.0 * a_m**2)


def required_heating_fraction(delta, cp=CP_AIR):
    """Fractional density increase delta related to a uniform temperature
    increase of the same air mass at fixed pressure: rho' / rho = T / T'.
    delta = T/T' - 1 -> dT/T = delta/(1+delta)."""
    return delta / (1.0 + delta)
