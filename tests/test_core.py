import numpy as np

from src.orbits.elements import (MU, R_EARTH, elements_to_state,
                                 state_to_elements, orbital_period)
from src.orbits import fastprop
from src.orbits.propagator import propagate, j2_accel
from src.intervention.models import (GaussianPatch, TopHatCylinder,
                                     make_delta_fn)
from src.energy.bounds import patch_air_mass, min_thermal_energy


def test_elements_roundtrip():
    r0, v0 = elements_to_state(R_EARTH + 400e3, 0.01, np.radians(51.6),
                               0.5, 0.2, 1.0)
    el = state_to_elements(r0, v0)
    r1, v1 = elements_to_state(el["a"], el["e"], el["inc"], el["raan"],
                               el["argp"], el["nu"])
    assert np.linalg.norm(r1 - r0) < 1e-3
    assert np.linalg.norm(v1 - v0) < 1e-3


def test_energy_conserved_no_pert():
    a0 = R_EARTH + 400e3
    r0, v0 = elements_to_state(a0, 0.001, np.radians(51.6), 0, 0, 0)
    T = orbital_period(a0)
    sol = propagate(r0, v0, (0, 2 * T), drag_on=False, j2_on=False,
                    max_step_s=60.0)
    E = 0.5 * np.sum(sol.y[3:]**2, axis=0) \
        - MU / np.linalg.norm(sol.y[:3], axis=0)
    assert np.abs(E - E[0]).max() / abs(E[0]) < 1e-10


def test_j2_direction():
    r = np.array([R_EARTH + 400e3, 0, 0])
    a = j2_accel(r)
    assert a[0] < 0  # equatorial bulge adds inward pull at equator


def test_gaussian_patch_decay_with_distance():
    g = GaussianPatch(0.0, 0.0, 400.0, delta_max=5.0,
                      sigma_h_km=100.0, sigma_v_km=20.0,
                      t0_s=0.0, duration_s=3600.0)
    # evaluate near t=0 so the ECEF rotation is small relative to sigma_h
    r = np.array([R_EARTH + 400e3, 0, 0])
    d_c = g.delta(r, 5.0)
    theta = 100.0 / 6378.1363
    r2 = np.array([(R_EARTH + 400e3) * np.cos(theta),
                   (R_EARTH + 400e3) * np.sin(theta), 0])
    d_edge = g.delta(r2, 5.0)
    assert d_c > 0
    assert d_edge < d_c
    assert g.delta(r, 7200.0) == 0.0  # outside window


def test_tophat():
    th = TopHatCylinder(0.0, 0.0, 400.0, 3.0, 200.0, 30.0, 0.0, 3600.0)
    r = np.array([R_EARTH + 400e3, 0, 0])
    assert th.delta(r, 100.0) == 3.0
    r2 = np.array([0, 0, R_EARTH + 400e3])  # north pole above center
    assert th.delta(r2, 100.0) == 0.0


def test_decay_monotonic():
    el = fastprop.init_elements(R_EARTH + 300e3, 0.0005, np.radians(51.6),
                                0.0, 0.0, 0.0)
    rho_fn = lambda r, t: 1e-12  # noqa: E731
    L, hist = fastprop.decay_lifetime(el, rho_fn, 30.0, 50 * 86400.0)
    assert L > 0
    assert np.all(np.diff(hist["a_m"]) <= 1e-9)


def test_energy_bounds():
    m = patch_air_mass(1e-12, 1e5, 2e4)
    assert m > 0
    E = min_thermal_energy(m, 100.0)
    assert E > 0


def test_delta_fn_combination():
    g1 = GaussianPatch(0, 0, 400, 1.0, 50, 10, 0, 1000)
    g2 = TopHatCylinder(0, 0, 400, 2.0, 100, 30, 0, 1000)
    fn = make_delta_fn([g1, g2])
    r = np.array([R_EARTH + 400e3, 0, 0])
    assert fn(r, 5.0) > 2.0
    fn0 = make_delta_fn([])
    assert fn0(r, 0.0) == 0.0
