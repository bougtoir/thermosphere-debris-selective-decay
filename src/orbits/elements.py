"""Keplerian elements <-> Cartesian state (ECI), and helpers."""
from __future__ import annotations

import numpy as np

MU = 3.986004418e14      # m^3 s^-2
R_EARTH = 6378136.3      # m
J2 = 1.08262668e-3
OMEGA_E = 7.2921150e-5   # rad s^-1


def elements_to_state(a, e, inc, raan, argp, nu, mu=MU):
    """Classical elements (m, rad) -> (r, v) ECI vectors."""
    p = a * (1.0 - e**2)
    rmag = p / (1.0 + e * np.cos(nu))
    r_pf = np.array([rmag * np.cos(nu), rmag * np.sin(nu), 0.0])
    v_pf = np.array([
        -np.sqrt(mu / p) * np.sin(nu),
        np.sqrt(mu / p) * (e + np.cos(nu)),
        0.0,
    ])
    ci, si = np.cos(inc), np.sin(inc)
    co, so = np.cos(raan), np.sin(raan)
    cw, sw = np.cos(argp), np.sin(argp)
    # R3(raan) R1(inc) R3(argp)
    R = np.array([
        [co * cw - so * sw * ci, -co * sw - so * cw * ci, so * si],
        [so * cw + co * sw * ci, -so * sw + co * cw * ci, -co * si],
        [sw * si, cw * si, ci],
    ])
    return R @ r_pf, R @ v_pf


def state_to_elements(r, v, mu=MU):
    """(r, v) ECI -> dict of classical elements."""
    r = np.asarray(r, float)
    v = np.asarray(v, float)
    rmag = np.linalg.norm(r)
    h = np.cross(r, v)
    hmag = np.linalg.norm(h)
    n = np.cross([0, 0, 1.0], h)
    nmag = np.linalg.norm(n)
    e_vec = np.cross(v, h) / mu - r / rmag
    e = np.linalg.norm(e_vec)
    energy = 0.5 * np.dot(v, v) - mu / rmag
    a = -mu / (2.0 * energy) if abs(energy) > 0 else np.inf
    inc = np.arccos(np.clip(h[2] / hmag, -1, 1))
    raan = np.arccos(np.clip(n[0] / nmag, -1, 1)) if nmag > 1e-12 else 0.0
    if nmag > 1e-12 and n[1] < 0:
        raan = 2 * np.pi - raan
    argp = 0.0
    if nmag > 1e-12 and e > 1e-12:
        argp = np.arccos(np.clip(np.dot(n, e_vec) / (nmag * e), -1, 1))
        if e_vec[2] < 0:
            argp = 2 * np.pi - argp
    nu = 0.0
    if e > 1e-12:
        nu = np.arccos(np.clip(np.dot(e_vec, r) / (e * rmag), -1, 1))
        if np.dot(r, v) < 0:
            nu = 2 * np.pi - nu
    else:
        # circular: use argument of latitude
        if nmag > 1e-12:
            nu = np.arccos(np.clip(np.dot(n, r) / (nmag * rmag), -1, 1))
            if r[2] < 0:
                nu = 2 * np.pi - nu
    return {"a": a, "e": e, "inc": inc, "raan": raan, "argp": argp,
            "nu": nu, "h": hmag, "energy": energy}


def orbital_period(a, mu=MU):
    return 2 * np.pi * np.sqrt(a**3 / mu)


def circular_velocity(r):
    return np.sqrt(MU / r)


def ecef_approx(r_eci, t_s, theta0=0.0):
    """Approximate geodetic lat/lon of an ECI position using a rotating frame
    (adequate for sampling a horizontal density patch; oblateness ignored here
    as the perturbation models are defined in the same approximation)."""
    theta = theta0 + OMEGA_E * t_s
    c, s = np.cos(theta), np.sin(theta)
    Rz = np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]])
    rf = Rz @ np.asarray(r_eci, float)
    rmag = np.linalg.norm(rf)
    lat = np.arcsin(np.clip(rf[2] / rmag, -1, 1))
    lon = np.arctan2(rf[1], rf[0])
    return np.degrees(lat), np.degrees(lon)


def ecef_unit_from_latlon(lat_deg, lon_deg):
    lat, lon = np.radians(lat_deg), np.radians(lon_deg)
    return np.array([
        np.cos(lat) * np.cos(lon),
        np.cos(lat) * np.sin(lon),
        np.sin(lat),
    ])


def ecef_to_eci_unit(u_ecef, t_s, theta0=0.0):
    theta = theta0 + OMEGA_E * t_s
    c, s = np.cos(theta), np.sin(theta)
    Rz = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
    return Rz @ np.asarray(u_ecef, float)


def ground_distance_km(lat1, lon1, lat2, lon2, r_km=R_EARTH / 1000.0):
    """Great-circle distance in km."""
    la1, lo1, la2, lo2 = np.radians([lat1, lon1, lat2, lon2])
    d = r_km * np.arccos(np.clip(
        np.sin(la1) * np.sin(la2) + np.cos(la1) * np.cos(la2) * np.cos(lo1 - lo2),
        -1, 1))
    return d
