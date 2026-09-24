"""Altitude-only climatological density lookup, built once from NRLMSISE-00.

The lookup averages density over latitude, longitude, and local solar time so
that phases that only need orbit-averaged exposure do not pay for a full
MSIS call at every sample. Persisted as CSV under data/processed/ so
downstream phases reuse it (cache of an expensive computation).
"""
from __future__ import annotations

import datetime
import os

import numpy as np
import pandas as pd

from .msis import density_kgm3, local_scale_height_km

LOOKUP_PATH = os.path.join(os.path.dirname(__file__), "..", "..",
                           "data", "processed", "density_lookup.csv")

ALT_MIN_KM = 100.0
ALT_MAX_KM = 900.0
ALT_STEP_KM = 1.0

# coarse climatological sampling grid
_LATS = [-80.0, -40.0, 0.0, 40.0, 80.0]
_LONS = [-180.0, -90.0, 0.0, 90.0]
_HOURS = [0, 6, 12, 18]


def build_lookup(regimes: dict, force: bool = False) -> pd.DataFrame:
    """regimes: {name: {f107, f107a, ap}}. Returns DataFrame with columns
    altitude_km, regime, rho_kgm3, H_km."""
    if os.path.exists(LOOKUP_PATH) and not force:
        df = pd.read_csv(LOOKUP_PATH)
        if set(regimes).issubset(set(df["regime"].unique())):
            return df
    rows = []
    alts = np.arange(ALT_MIN_KM, ALT_MAX_KM + ALT_STEP_KM, ALT_STEP_KM)
    epoch = datetime.datetime(2020, 6, 21, 12, 0, 0)
    for name, rg in regimes.items():
        for alt in alts:
            rhos = []
            for lat in _LATS:
                for lon in _LONS:
                    for h in _HOURS:
                        t = epoch + datetime.timedelta(hours=h)
                        rhos.append(density_kgm3(alt, lat, lon, t,
                                                 rg["f107a"], rg["f107"], rg["ap"]))
            rho = float(np.exp(np.mean(np.log(np.maximum(rhos, 1e-30)))))
            H = local_scale_height_km(alt, 0.0, 0.0, epoch,
                                      rg["f107a"], rg["f107"], rg["ap"])
            rows.append((alt, name, rho, H))
    df = pd.DataFrame(rows, columns=["altitude_km", "regime", "rho_kgm3", "H_km"])
    os.makedirs(os.path.dirname(LOOKUP_PATH), exist_ok=True)
    df.to_csv(LOOKUP_PATH, index=False)
    return df


def rho_fn_from_lookup(df: pd.DataFrame, regime: str):
    """Return rho_fn(r_eci_m, t_s) using altitude interpolation of the
    climatological lookup (background density, no perturbation)."""
    sub = df[df["regime"] == regime].sort_values("altitude_km")
    alt = sub["altitude_km"].to_numpy()
    rho = sub["rho_kgm3"].to_numpy()
    Re_km = 6378.1363

    def fn(r_eci_m, t_s):
        alt_km = np.linalg.norm(r_eci_m) / 1000.0 - Re_km
        return float(np.interp(alt_km, alt, rho, left=rho[0], right=rho[-1]))

    return fn
