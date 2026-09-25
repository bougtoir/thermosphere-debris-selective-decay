"""Fast semi-analytic orbit propagation for lifetime studies.

Two-level scheme:
  * Trajectory: osculating elements propagated by Kepler + J2 secular rates
    (valid for near-circular LEO; e < 0.1 regime covered by sampling the
    instantaneous radius rather than assuming a constant one).
  * Decay: semi-major axis integrated with the orbit-averaged drag
    da/dt = -(a * v_circ / B) * <rho> * f_rel^2, where <rho> is the mean
    density experienced along one orbit (K sample points) and f_rel is the
    corotating-atmosphere velocity factor (see corotation_factor).

Intervention density fields delta(r, t) are sampled finely (fine_dt_s) while
active and contribute extra orbit-averaged density for their duration.

As a decays, the secular rates (mean motion above all) change, so the
element set is re-based at every decay step: the secular phases are
accumulated across steps and the epoch angles are shifted accordingly.
Without that re-basing the sampled ephemeris jumps in along-track phase by
delta_n * t whenever a changes, which overstates the drag-induced
along-track drift by roughly a factor of two.
"""
from __future__ import annotations

import numpy as np

from .elements import (
    MU, R_EARTH, J2, OMEGA_E, orbital_period, elements_to_state,
)

K_ORBIT = 72          # samples per orbit for mean-density evaluation
DAY = 86400.0
# step used while an intervention window is active: the drag-induced
# along-track drift relative to the intervention centre needs a finer step
# than the background decay. Costs almost nothing, because the number of
# delta(r, t) evaluations is set by fine_dt_s, not by the step size.
DT_DAY_ACTIVE = 0.01


def corotation_factor(a, inc):
    """|v_rel| / |v| for a circular orbit in a rigidly corotating atmosphere.

    The atmospheric velocity omega x r projects onto the along-track
    direction as omega * a * cos(inc), essentially constant around a
    circular orbit, so v_rel = v - omega a cos(inc). Prograde low-inclination
    orbits see up to ~12% less dynamic pressure than the inertial-velocity
    approximation; retrograde orbits see ~2% more.
    """
    v = np.sqrt(MU / a)
    return 1.0 - OMEGA_E * a * np.cos(inc) / v


def j2_secular_rates(a, e, inc):
    """J2 secular drifts (rad/s) for RAAN, argp, mean motion correction."""
    p = a * (1.0 - e**2)
    n = np.sqrt(MU / a**3)
    f = 1.5 * J2 * (R_EARTH / p) ** 2 * n
    raan_dot = -f * np.cos(inc)
    argp_dot = f * (2.0 - 2.5 * np.sin(inc) ** 2)
    # J2 mean-motion correction (Kozai): n -> n * (1 + f2)
    m_dot = n * (1.0 + f * (1 - 1.5 * np.sin(inc) ** 2) * np.sqrt(1 - e**2) / n)
    return raan_dot, argp_dot, m_dot


def position_at(elements, t_s, theta0=0.0):
    """ECI position at time t for elements dict at t=0 (J2 secular)."""
    a, e, inc = elements["a"], elements["e"], elements["inc"]
    raan = elements["raan"] + elements["raan_dot"] * t_s
    argp = elements["argp"] + elements["argp_dot"] * t_s
    M = elements["M0"] + elements["M_dot"] * t_s
    # solve Kepler for E
    E = M
    for _ in range(12):
        E = E - (E - e * np.sin(E) - M) / (1.0 - e * np.cos(E))
    nu = 2.0 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2),
                          np.sqrt(1 - e) * np.cos(E / 2))
    r, v = elements_to_state(a, e, inc, raan, argp, nu)
    return r, v


def init_elements(a, e, inc, raan, argp, M0):
    el = {"a": a, "e": e, "inc": inc, "raan": raan, "argp": argp, "M0": M0}
    rd, ad, md = j2_secular_rates(a, e, inc)
    el["raan_dot"], el["argp_dot"], el["M_dot"] = rd, ad, md
    return el


def orbit_mean_density(elements, rho_fn, t0_s, n_samples=K_ORBIT):
    """Mean background density along one full orbit starting at t0_s.

    Fast path: for near-circular orbits (e < 0.02) the radius is essentially
    constant, so a single evaluation at the mean radius is representative.
    """
    if elements["e"] < 0.02:
        r, _ = position_at(elements, t0_s)
        return rho_fn(r, t0_s)
    T = orbital_period(elements["a"])
    rho_sum = 0.0
    el = dict(elements)
    for k in range(n_samples):
        t = t0_s + (k + 0.5) * T / n_samples
        M = el["M0"] + el["M_dot"] * t
        E = M
        for _ in range(8):
            E = E - (E - el["e"] * np.sin(E) - M) / (1 - el["e"] * np.cos(E))
        nu = 2.0 * np.arctan2(np.sqrt(1 + el["e"]) * np.sin(E / 2),
                              np.sqrt(1 - el["e"]) * np.cos(E / 2))
        r, _ = elements_to_state(el["a"], el["e"], el["inc"],
                                 el["raan"] + el["raan_dot"] * t,
                                 el["argp"] + el["argp_dot"] * t, nu)
        rho_sum += rho_fn(r, t)
    return rho_sum / n_samples


def exposure_metrics(elements, rho_fn, delta_fn, t_start, t_end,
                     fine_dt_s=10.0):
    """Integrate density exposure of the object against an active perturbation
    over [t_start, t_end]. Returns dict with mean <rho>, <rho*delta>,
    encountered-time fraction, and number of encounters (contiguous in-patch
    crossings). The window is covered exactly: the sample spacing is the
    window length divided by the nearest integer number of fine_dt_s
    samples, so no part of a short step is left unsampled."""
    span = t_end - t_start
    n = max(int(round(span / fine_dt_s)), 1)
    dt = span / n
    rho_sum = 0.0
    rho_d_sum = 0.0
    in_t = 0.0
    n_enc = 0
    prev_in = False
    first_in = False
    el = dict(elements)
    for k in range(n):
        t = t_start + (k + 0.5) * dt
        r, v = position_at(el, t)
        rho = rho_fn(r, t)
        d = delta_fn(r, t)
        rho_sum += rho
        rho_d_sum += rho * d
        inside = d > 1e-6
        if inside:
            in_t += dt
            if not prev_in:
                n_enc += 1
        if k == 0:
            first_in = inside
        prev_in = inside
    n_ = n
    return {
        "mean_rho": rho_sum / n_,
        "mean_rho_delta": rho_d_sum / n_,
        "time_fraction_in_patch": in_t / max(t_end - t_start, 1e-9),
        "encounter_count": n_enc,
        "starts_inside": first_in,
        "ends_inside": prev_in,
    }


def _rebased(el0, a, m_phase, raan_phase, argp_phase, t):
    """Element set with semi-major axis a whose secular phases equal the
    accumulated (m_phase, raan_phase, argp_phase) at time t."""
    el = dict(el0)
    el["a"] = a
    rd, ad, md = j2_secular_rates(a, el["e"], el["inc"])
    el["raan_dot"], el["argp_dot"], el["M_dot"] = rd, ad, md
    el["M0"] = m_phase - md * t
    el["raan"] = raan_phase - rd * t
    el["argp"] = argp_phase - ad * t
    return el


def decay_lifetime(el0, rho_fn, B, t_max_s, reentry_alt_m=120e3,
                   dt_day=0.25, n_samples=K_ORBIT,
                   delta_windows=None, delta_fn=None, fine_dt_s=10.0,
                   dt_day_active=DT_DAY_ACTIVE):
    """Integrate semi-major-axis decay until reentry or t_max.

    delta_windows: list of (t_start, t_end) during which delta_fn is active;
    the extra orbit-averaged density is added during those windows.

    Each step is taken with the midpoint rule: the decay rate and the
    ephemeris used to sample the intervention are evaluated at the
    predicted mid-step semi-major axis, which makes the along-track drift
    caused by the induced drag second-order rather than first-order in
    the step size. Steps overlapping an intervention window are shortened
    to dt_day_active (see docs/ORBIT_CONVERGENCE.md).

    Returns (lifetime_days, history_dict).
    """
    t = 0.0
    a = el0["a"]
    hist_a = [a]
    hist_t = [0.0]
    total_enc = 0
    total_extra_impulse = 0.0  # integral of extra drag deceleration (m/s)
    exp_window = 0.0
    exp_rho = 0.0
    exp_rho_delta = 0.0
    exp_in_t = 0.0

    # secular phases accumulated along the decaying trajectory
    m_phase, raan_phase, argp_phase = el0["M0"], el0["raan"], el0["argp"]
    da_prev = None
    was_inside = False

    while t < t_max_s:
        alt = a - R_EARTH
        if alt <= reentry_alt_m:
            break
        step_s = dt_day * DAY
        if delta_windows and delta_fn is not None and any(
                min(te, t + step_s) - max(ts, t) > 0 for ts, te in
                delta_windows):
            step_s = min(step_s, dt_day_active * DAY)
        if da_prev is None:
            el_p = _rebased(el0, a, m_phase, raan_phase, argp_phase, t)
            rho_p = orbit_mean_density(el_p, rho_fn, t, n_samples)
            f_p = corotation_factor(a, el0["inc"])
            da_prev = -(a * np.sqrt(MU / a) / B) * rho_p * f_p**2
        a_mid = max(a + 0.5 * da_prev * step_s, R_EARTH + reentry_alt_m)
        el = _rebased(el0, a_mid, m_phase, raan_phase, argp_phase, t)
        rd, ad, md = el["raan_dot"], el["argp_dot"], el["M_dot"]
        f_rel = corotation_factor(a_mid, el0["inc"])

        rho_bg = orbit_mean_density(el, rho_fn, t, n_samples)
        rho_eff = rho_bg
        if delta_windows and delta_fn is not None:
            for (ts, te) in delta_windows:
                ovl = min(te, t + step_s) - max(ts, t)
                if ovl > 0:
                    m = exposure_metrics(el, rho_fn, delta_fn,
                                         max(ts, t), min(te, t + step_s),
                                         fine_dt_s=fine_dt_s)
                    # extra mean density applied only for the overlapping
                    # fraction of this step
                    rho_eff += m["mean_rho_delta"] * (ovl / step_s)
                    # a crossing spanning a step boundary is one encounter
                    total_enc += m["encounter_count"] - int(
                        was_inside and m["starts_inside"])
                    was_inside = m["ends_inside"]
                    v_rel = np.sqrt(MU / a_mid) * f_rel
                    total_extra_impulse += (m["mean_rho_delta"] * v_rel**2
                                            / (2.0 * B) * ovl)
                    exp_window += ovl
                    exp_rho += m["mean_rho"] * ovl
                    exp_rho_delta += m["mean_rho_delta"] * ovl
                    exp_in_t += m["time_fraction_in_patch"] * ovl

        da_dt = -(a_mid * np.sqrt(MU / a_mid) / B) * rho_eff * f_rel**2
        if da_dt >= 0:
            da_dt = 0.0
        da_prev = da_dt
        new_a = a + da_dt * step_s
        # sub-step if large decrement
        if new_a < R_EARTH + reentry_alt_m:
            # solve fraction of step to reach reentry
            frac = (a - (R_EARTH + reentry_alt_m)) / max(a - new_a, 1e-12)
            t += frac * step_s
            m_phase += md * frac * step_s
            raan_phase += rd * frac * step_s
            argp_phase += ad * frac * step_s
            a = R_EARTH + reentry_alt_m
            hist_a.append(a)
            hist_t.append(t)
            break
        a = new_a
        t += step_s
        m_phase += md * step_s
        raan_phase += rd * step_s
        argp_phase += ad * step_s
        hist_a.append(a)
        hist_t.append(t)
        if np.isnan(a):
            break

    return t / DAY, {
        "t_days": np.array(hist_t),
        "a_m": np.array(hist_a),
        "encounter_count": total_enc,
        "extra_drag_impulse_ms": total_extra_impulse,
        # exposure aggregates along the decaying trajectory
        "exposure_window_s": exp_window,
        "mean_rho": exp_rho / exp_window if exp_window > 0 else 0.0,
        "mean_rho_delta": (exp_rho_delta / exp_window
                           if exp_window > 0 else 0.0),
        "time_fraction_in_patch": (exp_in_t / exp_window
                                   if exp_window > 0 else 0.0),
    }


def propagate_elements(el0, t_s):
    """Return ECI (r,v) at t for elements dict initialized by init_elements."""
    return position_at(el0, t_s)
