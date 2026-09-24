"""Abstract density-perturbation models delta(r, t) and spreading surrogates.

delta is a fractional enhancement: rho'(r,t) = rho_background(r,t) * (1+delta).

Perturbation centers are defined in the co-rotating frame (geodetic lat/lon/alt)
and carried back to ECI for evaluation against satellite positions.
"""
from __future__ import annotations

import numpy as np

from ..orbits.elements import (
    ecef_approx, ecef_unit_from_latlon, ecef_to_eci_unit, ground_distance_km,
    R_EARTH, OMEGA_E,
)


class Perturbation:
    """Base: returns delta given (r_eci_m, t_s)."""

    def delta(self, r_eci_m, t_s):
        raise NotImplementedError


class GaussianPatch(Perturbation):
    """delta = delta_max exp(-d_h^2/2 sigma_h^2) exp(-(h-h0)^2/2 sigma_v^2) * w(t)

    Center at geodetic (lat0, lon0, h0). temporal window w(t) is a smooth
    boxcar (cosine-tapered edges) over [t0, t0+duration].
    Spreading: sigma_h(t)^2 = sigma_h0^2 + 2 kappa_h * (t - t0); amplitude can
    relax with exp(-(t-t0)/tau) when tau is set (Model 2 surrogate).
    """

    def __init__(self, lat0_deg, lon0_deg, h0_km, delta_max,
                 sigma_h_km, sigma_v_km, t0_s=0.0, duration_s=3600.0,
                 kappa_h_m2s=0.0, advection_east_ms=0.0,
                 advection_north_ms=0.0, tau_s=None):
        self.lat0 = lat0_deg
        self.lon0 = lon0_deg
        self.h0_km = h0_km
        self.delta_max = delta_max
        self.sigma_h_km = sigma_h_km
        self.sigma_v_km = sigma_v_km
        self.t0 = t0_s
        self.dur = duration_s
        self.kappa_h = kappa_h_m2s
        self.u_e = advection_east_ms
        self.u_n = advection_north_ms
        self.tau = tau_s

    def _window(self, t):
        if t < self.t0 or t > self.t0 + self.dur:
            return 0.0
        # cosine taper over the first/last 5% of the duration
        edge = 0.05 * self.dur
        x = t - self.t0
        w = 1.0
        if x < edge:
            w = 0.5 * (1 - np.cos(np.pi * x / edge))
        elif x > self.dur - edge:
            w = 0.5 * (1 - np.cos(np.pi * (self.dur - x) / edge))
        return w

    def delta(self, r_eci_m, t_s):
        w = self._window(t_s)
        if w == 0.0:
            return 0.0
        lat, lon = ecef_approx(r_eci_m, t_s)
        # advection shifts the patch center over time
        dt = max(t_s - self.t0, 0.0)
        r_km = R_EARTH / 1000.0 + self.h0_km
        lon_c = self.lon0 + np.degrees(self.u_e * dt / (r_km * 1000.0))
        lat_c = self.lat0 + np.degrees(self.u_n * dt / (r_km * 1000.0))
        d_h = ground_distance_km(lat, lon, lat_c, lon_c)  # km
        alt_km = np.linalg.norm(r_eci_m) / 1000.0 - R_EARTH / 1000.0
        sig_h2 = self.sigma_h_km**2 + 2.0 * self.kappa_h * dt / 1e6  # km^2
        sh = np.exp(-d_h**2 / (2.0 * sig_h2))
        sv = np.exp(-(alt_km - self.h0_km) ** 2 / (2.0 * self.sigma_v_km**2))
        amp = self.delta_max
        # conserve approximately-integrated perturbation when spreading:
        # peak amplitude decays as sigma0^2/sigma(t)^2 for diffusion
        if self.kappa_h > 0:
            amp *= self.sigma_h_km**2 / sig_h2
        if self.tau is not None and self.tau > 0:
            amp *= np.exp(-dt / self.tau)
        return amp * sh * sv * w


class TopHatCylinder(Perturbation):
    """Cylindrical top-hat: delta = delta_max inside a horizontal radius R_h
    and vertical half-thickness sigma_v, zero outside."""

    def __init__(self, lat0_deg, lon0_deg, h0_km, delta_max,
                 radius_h_km, half_thickness_km, t0_s=0.0, duration_s=3600.0):
        self.lat0, self.lon0, self.h0 = lat0_deg, lon0_deg, h0_km
        self.delta_max = delta_max
        self.R = radius_h_km
        self.dv = half_thickness_km
        self.t0 = t0_s
        self.dur = duration_s

    def delta(self, r_eci_m, t_s):
        if t_s < self.t0 or t_s > self.t0 + self.dur:
            return 0.0
        lat, lon = ecef_approx(r_eci_m, t_s)
        d_h = ground_distance_km(lat, lon, self.lat0, self.lon0)
        alt_km = np.linalg.norm(r_eci_m) / 1000.0 - R_EARTH / 1000.0
        if d_h <= self.R and abs(alt_km - self.h0) <= self.dv:
            return self.delta_max
        return 0.0


class MovingPerturbation(Perturbation):
    """Gaussian patch whose center follows a constant-velocity ground track,
    or can be retargeted per scheduled time list (simplified as linear sweep)."""

    def __init__(self, lat0_deg, lon0_deg, h0_km, delta_max,
                 sigma_h_km, sigma_v_km, t0_s, duration_s,
                 dlat_degps=0.0, dlon_degps=0.0):
        self.g = GaussianPatch(lat0_deg, lon0_deg, h0_km, delta_max,
                               sigma_h_km, sigma_v_km, t0_s, duration_s)
        self.dlat = dlat_degps
        self.dlon = dlon_degps

    def delta(self, r_eci_m, t_s):
        dt = t_s - self.g.t0
        self.g.lat0_t = self.g.lat0 + self.dlat * dt
        self.g.lon0_t = self.g.lon0 + self.dlon * dt
        lat, lon = ecef_approx(r_eci_m, t_s)
        if t_s < self.g.t0 or t_s > self.g.t0 + self.g.dur:
            return 0.0
        d_h = ground_distance_km(lat, lon, self.g.lat0_t, self.g.lon0_t)
        alt_km = np.linalg.norm(r_eci_m) / 1000.0 - R_EARTH / 1000.0
        sh = np.exp(-d_h**2 / (2.0 * self.g.sigma_h_km**2))
        sv = np.exp(-(alt_km - self.g.h0) ** 2 / (2.0 * self.g.sigma_v_km**2))
        return self.g.delta_max * sh * sv


class CombinedPerturbation(Perturbation):
    def __init__(self, parts):
        self.parts = list(parts)

    def delta(self, r_eci_m, t_s):
        return sum(p.delta(r_eci_m, t_s) for p in self.parts)


def make_delta_fn(perturbations):
    """Return a callable delta_fn(r_eci_m, t_s). None -> 0."""
    if not perturbations:
        return lambda r, t: 0.0
    comb = CombinedPerturbation(perturbations)
    return comb.delta
