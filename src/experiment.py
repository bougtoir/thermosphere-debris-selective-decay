"""Shared experiment engine for Phases 3-12.

An *object* is a dict of orbital elements + ballistic coefficient + label.
An *intervention* is a list of perturbation instances with an activation
window list [(t_start, t_end)]. Outcomes come from the fast semi-analytic
decay integrator; per-window fine sampling resolves encounters.
"""
from __future__ import annotations

import numpy as np

from .orbits import fastprop
from .orbits.elements import MU, R_EARTH, orbital_period
from .intervention.models import make_delta_fn


def make_object(name, alt_km, inc_deg, B, e=0.001, raan=0.0, argp=0.0,
                M0=0.0, obj_type="target", mass_kg=None):
    el = fastprop.init_elements(R_EARTH + alt_km * 1000.0, e,
                                np.radians(inc_deg), raan, argp, M0)
    return dict(name=name, el=el, alt_km=alt_km, inc_deg=inc_deg, B=B, e=e,
                raan=raan, argp=argp, M0=M0, obj_type=obj_type,
                mass_kg=mass_kg)


def simulate(obj, rho_fn, t_max_s, delta_windows=None, delta_fn=None,
             reentry_alt_m=120e3, dt_day=0.25, rho_scale=1.0,
             fine_dt_s=10.0):
    """Return outcome dict for one object. rho_scale multiplies the
    background density (uncertainty propagation)."""
    if rho_scale != 1.0:
        base_fn = rho_fn
        rho_fn = lambda r, t: rho_scale * base_fn(r, t)  # noqa: E731
    L, hist = fastprop.decay_lifetime(
        obj["el"], rho_fn, obj["B"], t_max_s,
        reentry_alt_m=reentry_alt_m, dt_day=dt_day,
        delta_windows=delta_windows, delta_fn=delta_fn,
        fine_dt_s=fine_dt_s)
    out = dict(
        name=obj["name"], obj_type=obj["obj_type"], alt_km=obj["alt_km"],
        inc_deg=obj["inc_deg"], B=obj["B"], e=obj["e"], raan=obj["raan"],
        argp=obj["argp"], M0=obj["M0"], lifetime_days=L,
        encounter_count=hist["encounter_count"],
        extra_drag_impulse_ms=hist["extra_drag_impulse_ms"],
        final_a_km=hist["a_m"][-1] / 1000.0,
        start_a_km=hist["a_m"][0] / 1000.0,
    )
    # orbital energy removed during intervention (per kg): from extra impulse
    v = np.sqrt(MU / (obj["alt_km"] * 1000.0 + R_EARTH))
    out["extra_deltav_ms"] = hist["extra_drag_impulse_ms"]
    out["reentry"] = bool(hist["a_m"][-1] <= R_EARTH + reentry_alt_m + 1.0)
    return out


def campaign_windows(t0, duration_s, repeat_every_s=None, n_repeats=1):
    """List of activation windows for an intervention."""
    if repeat_every_s is None or n_repeats == 1:
        return [(t0, t0 + duration_s)]
    return [(t0 + k * repeat_every_s, t0 + k * repeat_every_s + duration_s)
            for k in range(n_repeats)]
