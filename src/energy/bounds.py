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


def expansion_temperature_fraction(delta, z_m, z_base_m, H_m):
    """Fractional temperature rise of the column below z needed to raise the
    density at z by a factor (1+delta) through hydrostatic expansion.

    For an isothermal hydrostatic layer rho(z) = rho(z_base)
    exp(-(z - z_base)/H); scaling T (and hence H) by (1 + eps) multiplies
    the density at z by exp[L eps / (H (1 + eps))] with L = z - z_base.
    Writing q = ln(1+delta) H / L, the condition eps / (1 + eps) = q solves
    exactly to eps = q / (1 - q); the first-order form eps ~ q understates
    the required heating and is not used. q >= 1 means the density increase
    cannot be reached by uniform heating of this column at all, and inf is
    returned. This is the mechanism by which real thermospheric storms
    raise density at a fixed altitude; heating the air *at* z in situ
    lowers its density.
    """
    q = float(np.log1p(delta) * H_m / (z_m - z_base_m))
    if q >= 1.0:
        return float("inf")
    return q / (1.0 - q)


def required_heating_fraction(delta, cp=CP_AIR):
    """Fractional density increase delta related to a uniform temperature
    increase of the same air mass at fixed pressure: rho' / rho = T / T'.
    delta = T/T' - 1 -> dT/T = delta/(1+delta)."""
    return delta / (1.0 + delta)
