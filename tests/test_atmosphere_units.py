"""Absolute-magnitude checks on the atmosphere model.

NRLMSISE-00 returns total mass density in g/cm^3; the wrapper converts to
kg/m^3. Every drag result scales linearly with this factor, so the model is
anchored against published thermospheric densities rather than only against
internal consistency.

Reference values (moderate solar activity, F10.7 ~ 140): roughly
2-4e-10 kg/m^3 at 200 km, 2-6e-12 kg/m^3 at 400 km and 4e-13 kg/m^3 at
500 km (Vallado & Finkleman 2014, Table 4; US Standard Atmosphere 1976
exponential fits). A factor-of-5 tolerance absorbs the diurnal, seasonal
and solar-cycle spread while still excluding a unit error.
"""
import datetime

import pytest

from src.atmosphere.msis import density_kgm3

EPOCH = datetime.datetime(2020, 6, 21, 12, 0, 0)
EXPECTED_KG_M3 = {200.0: 3.0e-10, 400.0: 4.0e-12, 500.0: 5.0e-13}
TOL_FACTOR = 5.0


@pytest.mark.parametrize("alt_km,rho_ref", sorted(EXPECTED_KG_M3.items()))
def test_density_magnitude_matches_published_thermosphere(alt_km, rho_ref):
    rho = density_kgm3(alt_km, 0.0, 0.0, EPOCH, 140.0, 140.0, 15.0)
    assert rho_ref / TOL_FACTOR < rho < rho_ref * TOL_FACTOR


def test_density_decreases_with_altitude():
    rhos = [density_kgm3(a, 0.0, 0.0, EPOCH, 140.0, 140.0, 15.0)
            for a in (200.0, 300.0, 400.0, 500.0, 600.0)]
    assert all(b < a for a, b in zip(rhos, rhos[1:]))
