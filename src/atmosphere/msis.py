"""NRLMSISE-00 atmospheric density wrapper.

All densities returned in kg/m^3. Altitudes in km (as required by the
nrlmsise00 package), lat/lon in degrees.
"""
from __future__ import annotations

import datetime
from functools import lru_cache

import nrlmsise00

# gtd7 output index of total mass density (kg/m^3)
_RHO_INDEX = 5
_T_EXOSPHERIC = 0


def density_kgm3(
    alt_km: float,
    lat_deg: float = 0.0,
    lon_deg: float = 0.0,
    time: datetime.datetime | None = None,
    f107a: float = 140.0,
    f107: float = 140.0,
    ap: float = 15.0,
    lst: float | None = None,
) -> float:
    """Total mass density (kg/m^3) from NRLMSISE-00 (gtd7)."""
    if time is None:
        time = datetime.datetime(2020, 6, 1, 12, 0, 0)
    alt_km = max(float(alt_km), 80.0)  # model lower bound safety
    out = nrlmsise00.msise_model(
        time, alt_km, float(lat_deg), float(lon_deg),
        float(f107a), float(f107), float(ap), lst=lst,
    )
    return float(out[0][_RHO_INDEX])


def exospheric_temperature_k(
    alt_km: float,
    lat_deg: float = 0.0,
    lon_deg: float = 0.0,
    time: datetime.datetime | None = None,
    f107a: float = 140.0,
    f107: float = 140.0,
    ap: float = 15.0,
) -> float:
    if time is None:
        time = datetime.datetime(2020, 6, 1, 12, 0, 0)
    out = nrlmsise00.msise_model(
        time, float(alt_km), float(lat_deg), float(lon_deg),
        float(f107a), float(f107), float(ap),
    )
    return float(out[1][_T_EXOSPHERIC])


def density_profile(
    alt_km: float,
    lat_deg: float = 0.0,
    lon_deg: float = 0.0,
    time: datetime.datetime | None = None,
    f107a: float = 140.0,
    f107: float = 140.0,
    ap: float = 15.0,
) -> dict:
    """Return density, exospheric temperature, and mean molecular mass estimate."""
    if time is None:
        time = datetime.datetime(2020, 6, 1, 12, 0, 0)
    out = nrlmsise00.msise_model(
        time, float(alt_km), float(lat_deg), float(lon_deg),
        float(f107a), float(f107), float(ap),
    )
    d = out[0]
    # number densities cm^-3: He,O,N2,O2,Ar,H,N,anomalous O -> indices 0,1,2,3,4,6,7,8
    masses_u = {0: 4.0, 1: 16.0, 2: 28.0, 3: 32.0, 4: 40.0, 6: 1.0, 7: 14.0, 8: 16.0}
    n_tot = sum(d[i] for i in (0, 1, 2, 3, 4, 6, 7))
    if n_tot > 0:
        mw = sum(d[i] * masses_u[i] for i in (0, 1, 2, 3, 4, 6, 7)) / n_tot
    else:
        mw = 16.0
    return {
        "rho_kgm3": float(d[_RHO_INDEX]),
        "t_exo_K": float(out[1][0]),
        "t_local_K": float(out[1][1]),
        "mean_molecular_mass_u": float(mw),
    }


def local_scale_height_km(
    alt_km: float,
    lat_deg: float = 0.0,
    lon_deg: float = 0.0,
    time: datetime.datetime | None = None,
    f107a: float = 140.0,
    f107: float = 140.0,
    ap: float = 15.0,
    dh_km: float = 2.0,
) -> float:
    """Local density scale height H = -rho / (drho/dh) in km."""
    r1 = density_kgm3(alt_km + dh_km, lat_deg, lon_deg, time, f107a, f107, ap)
    r0 = density_kgm3(alt_km - dh_km, lat_deg, lon_deg, time, f107a, f107, ap)
    rm = density_kgm3(alt_km, lat_deg, lon_deg, time, f107a, f107, ap)
    drdh = (r1 - r0) / (2.0 * dh_km)
    return -rm / drdh
