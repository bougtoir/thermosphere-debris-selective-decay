"""Cowell propagator in a pseudo-inertial frame: central gravity + J2 + drag.

Drag accelerations use a density model callable rho_fn(r_eci_m, t_s) -> kg/m^3
that may already include perturbations, plus a separate optional delta_fn
returning the fractional enhancement field delta(r, t).

The atmosphere co-rotates with Earth: v_rel = v - omega x r.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

from .elements import MU, R_EARTH, J2, OMEGA_E

OMEGA_VEC = np.array([0.0, 0.0, OMEGA_E])


def j2_accel(r, mu=MU, r_earth=R_EARTH, j2=J2):
    x, y, z = r
    rmag = np.linalg.norm(r)
    z2 = z * z
    r2 = rmag * rmag
    factor = -1.5 * j2 * mu * r_earth**2 / rmag**5
    ax = factor * x * (1.0 - 5.0 * z2 / r2)
    ay = factor * y * (1.0 - 5.0 * z2 / r2)
    az = factor * z * (3.0 - 5.0 * z2 / r2)
    return np.array([ax, ay, az])


def drag_accel(r, v, rho_kgm3, B):
    """a_drag = -rho * v_rel * |v_rel| / (2 B), with B = m/(Cd A) in kg/m^2."""
    v_rel = v - np.cross(OMEGA_VEC, r)
    vmag = np.linalg.norm(v_rel)
    if vmag < 1e-12:
        return np.zeros(3)
    return -rho_kgm3 * vmag * v_rel / (2.0 * B)


def rhs(t, y, rho_fn, B, j2_on=True, drag_on=True):
    r = y[:3]
    v = y[3:]
    rmag = np.linalg.norm(r)
    a = -MU * r / rmag**3
    if j2_on:
        a = a + j2_accel(r)
    if drag_on and rho_fn is not None:
        a = a + drag_accel(r, v, rho_fn(r, t), B)
    return np.concatenate([v, a])


def propagate(r0, v0, t_span, rho_fn=None, B=np.inf, j2_on=True,
              drag_on=True, rtol=1e-9, atol=1e-12, max_step_s=21600.0,
              reentry_alt_m=120e3, dense=None):
    """Propagate state [r,v] over t_span seconds. Returns SolveIVP result."""
    y0 = np.concatenate([np.asarray(r0, float), np.asarray(v0, float)])

    def reentry(t, y, *args):
        return np.linalg.norm(y[:3]) - (R_EARTH + reentry_alt_m)
    reentry.terminal = True
    reentry.direction = -1

    def f(t, y):
        return rhs(t, y, rho_fn, B, j2_on=j2_on, drag_on=drag_on)

    kw = {}
    if dense is not None:
        kw["t_eval"] = dense
    return solve_ivp(
        f, (t_span[0], t_span[1]), y0, method="DOP853",
        rtol=rtol, atol=atol, max_step=max_step_s,
        events=[reentry], **kw)


def lifetime_days_circular(r0, v0, rho_fn, B, t_max_s,
                           rtol=1e-9, atol=1e-12, max_step_s=86400.0 / 4,
                           reentry_alt_m=120e3):
    """Propagate until reentry event or t_max. Returns lifetime in days
    (t_max if no reentry) and the solve_ivp result."""
    sol = propagate(r0, v0, (0.0, t_max_s), rho_fn=rho_fn, B=B,
                    rtol=rtol, atol=atol, max_step_s=max_step_s,
                    reentry_alt_m=reentry_alt_m)
    if sol.t_events and len(sol.t_events[0]) > 0:
        return sol.t_events[0][0] / 86400.0, sol
    return t_max_s / 86400.0, sol
