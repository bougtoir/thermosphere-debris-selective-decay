import numpy as np

from src.analysis.exposure_class import instrument, instrument_decaying
from src.energy.bounds import expansion_temperature_fraction
from src.intervention.models import TrackingPerturbation
from src.orbits import fastprop
from src.orbits.elements import R_EARTH


def test_expansion_fraction_is_exact_not_first_order():
    """eps must solve eps/(1+eps) = q exactly, not eps = q."""
    delta, H, L = 5.0, 60e3, 400e3 - 120e3
    q = np.log1p(delta) * H / L
    eps = expansion_temperature_fraction(delta, 400e3, 120e3, H)
    assert eps == np.float64(q / (1 - q)) or abs(eps - q / (1 - q)) < 1e-12
    assert eps > q  # first order understates the heating
    # the exact eps reproduces the requested multiplier
    got = np.exp(L / H - L / (H * (1 + eps)))
    assert abs(got / (1 + delta) - 1.0) < 1e-10


def test_expansion_fraction_unattainable_when_q_ge_one():
    # a short column with a large scale height cannot be heated enough
    assert np.isinf(expansion_temperature_fraction(5.0, 200e3, 120e3, 80e3))
    assert np.isinf(expansion_temperature_fraction(1e6, 400e3, 120e3, 60e3))


def _case_a_target():
    el = fastprop.init_elements(R_EARTH + 400e3, 0.001, np.radians(51.6),
                                0.0, 0.0, 0.0)
    return dict(el=el, B=20.0)


def test_drift_aware_exposure_below_perfect_bound():
    """Perfect co-location is an upper bound: the induced drag drifts the
    object out of a patch centred on the unperturbed ephemeris."""
    obj = _case_a_target()
    rho_fn = lambda r, t: 1e-11  # noqa: E731
    win = 86400.0
    trk = TrackingPerturbation(obj["el"], 5.0, 200.0, 30.0, 0.0, win)
    bound = instrument(obj, rho_fn, trk.delta, 5.0, 0.0, win,
                       fine_dt_s=60.0)
    drift = instrument_decaying(obj, rho_fn, trk.delta, 5.0, 0.0, win,
                                fine_dt_s=60.0)
    assert bound["ephemeris"] == "unperturbed"
    assert drift["ephemeris"] == "drag_updated"
    assert 0.0 < drift["extra_dv_ms"] < bound["extra_dv_ms"]
    assert drift["time_fraction_in_patch"] <= bound["time_fraction_in_patch"]


def test_active_step_refinement_converges():
    """Halving the active step must change the drift-aware impulse by far
    less than the coarse-step error, i.e. the production step is resolved."""
    obj = _case_a_target()
    rho_fn = lambda r, t: 1e-11  # noqa: E731
    win = 86400.0
    trk = TrackingPerturbation(obj["el"], 5.0, 200.0, 30.0, 0.0, win)

    def run(dt_active):
        _, hist = fastprop.decay_lifetime(
            obj["el"], rho_fn, obj["B"], win, dt_day=0.5,
            delta_windows=[(0.0, win)], delta_fn=trk.delta, fine_dt_s=60.0,
            dt_day_active=dt_active)
        return hist["extra_drag_impulse_ms"]

    coarse, prod, fine = run(0.1), run(0.01), run(0.005)
    assert abs(prod - fine) < 0.1 * abs(coarse - prod)
