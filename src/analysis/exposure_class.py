"""Exposure diagnostics and classification of near-zero collateral drag.

A Gaussian enhancement has no compact support, so an object that never
approaches the patch still receives an arithmetically nonzero - and
physically meaningless - extra delta-v (the frozen results contained values
of order 1e-84 m/s, producing selectivity ratios of 1e80). These helpers
record *why* a collateral delta-v is small and label it accordingly, so
figures and tables can report absolute quantities and suppress ratios that
are not measurements.

Thresholds are justified in docs/NUMERICAL_ZERO_AUDIT.md.
"""
from __future__ import annotations

import numpy as np

from ..orbits import fastprop
from ..orbits.elements import MU

N_SIGMA_NO_ENCOUNTER = 6.0
REL_NUMERICAL_FLOOR = 1e-12
REL_PHYSICAL = 1e-3

RATIO_STATUS = {
    "physical_exposure": "physical",
    "gaussian_tail": "tail_limited",
    "below_numerical_resolution": "below_resolution",
    "no_encounter": "undefined_no_encounter",
}


def instrument(obj, rho_fn, delta_fn, delta_max, t0, t1, fine_dt_s=10.0):
    """Exposure metrics plus the diagnostic geometry of the encounter,
    measured along the *unperturbed* ephemeris.

    Holding the trajectory fixed while the intervention acts is the perfect
    co-location convention: it is an upper bound, because the induced drag
    itself moves the object relative to an intervention centred on the
    unperturbed orbit. Use instrument_decaying() for the drift-aware value.
    """
    peak = 0.0

    def probe(r, t):
        nonlocal peak
        d = delta_fn(r, t)
        if d > peak:
            peak = d
        return d

    m = fastprop.exposure_metrics(obj["el"], rho_fn, probe, t0, t1,
                                  fine_dt_s=fine_dt_s)
    if peak <= 0.0:
        n_sigma = np.inf
    else:
        ratio = min(peak / delta_max, 1.0)
        n_sigma = float(np.sqrt(max(-2.0 * np.log(ratio), 0.0)))
    a = obj["el"]["a"]
    v_rel = np.sqrt(MU / a) * fastprop.corotation_factor(a, obj["el"]["inc"])
    k = v_rel ** 2 / (2.0 * obj["B"]) * (t1 - t0)
    dv_extra = m["mean_rho_delta"] * k
    dv_natural = m["mean_rho"] * k
    return dict(peak_delta=peak, n_sigma_closest=n_sigma,
                encounter_count=m["encounter_count"],
                time_fraction_in_patch=m["time_fraction_in_patch"],
                extra_dv_ms=dv_extra, natural_dv_ms=dv_natural,
                rel_to_natural=dv_extra / dv_natural if dv_natural > 0
                else np.nan,
                ephemeris="unperturbed")


def instrument_decaying(obj, rho_fn, delta_fn, delta_max, t0, t1,
                        fine_dt_s=10.0, dt_day=0.25):
    """As instrument(), but with the exposure measured along the trajectory
    the drag itself produces.

    instrument() samples the unperturbed ephemeris, which is the perfect
    co-location limit: the intervention is assumed to stay centred on the
    object no matter how the object moves. Here the semi-major axis is
    integrated while the intervention is active, so an intervention whose
    centre follows the unperturbed ephemeris loses the object as the
    induced drag drifts it along track. Returns the same keys plus
    'ephemeris' identifying the convention.
    """
    peak = 0.0

    def probe(r, t):
        nonlocal peak
        d = delta_fn(r, t)
        if d > peak:
            peak = d
        return d

    _, hist = fastprop.decay_lifetime(
        obj["el"], rho_fn, obj["B"], t1, dt_day=dt_day,
        delta_windows=[(t0, t1)], delta_fn=probe, fine_dt_s=fine_dt_s)
    if peak <= 0.0:
        n_sigma = np.inf
    else:
        ratio = min(peak / delta_max, 1.0)
        n_sigma = float(np.sqrt(max(-2.0 * np.log(ratio), 0.0)))
    a = obj["el"]["a"]
    v_rel = np.sqrt(MU / a) * fastprop.corotation_factor(a, obj["el"]["inc"])
    k = v_rel ** 2 / (2.0 * obj["B"]) * (t1 - t0)
    dv_extra = hist["extra_drag_impulse_ms"]
    dv_natural = hist["mean_rho"] * k
    return dict(peak_delta=peak, n_sigma_closest=n_sigma,
                encounter_count=hist["encounter_count"],
                time_fraction_in_patch=hist["time_fraction_in_patch"],
                extra_dv_ms=dv_extra, natural_dv_ms=dv_natural,
                rel_to_natural=dv_extra / dv_natural if dv_natural > 0
                else np.nan,
                ephemeris="drag_updated")


def classify(d):
    """Label one exposure record; see module docstring."""
    if d["n_sigma_closest"] > N_SIGMA_NO_ENCOUNTER or d["peak_delta"] <= 1e-6:
        return "no_encounter"
    r = d["rel_to_natural"]
    if not np.isfinite(r) or r < REL_NUMERICAL_FLOOR:
        return "below_numerical_resolution"
    if r < REL_PHYSICAL:
        return "gaussian_tail"
    return "physical_exposure"


def ratio_status(exposure_class):
    """Whether a selectivity ratio built on this exposure is a measurement."""
    return RATIO_STATUS.get(exposure_class, "unknown")
