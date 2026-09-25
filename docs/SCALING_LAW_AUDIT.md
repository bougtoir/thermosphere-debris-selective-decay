# Scaling-law audit (Phase 11)

Addresses hostile-review item **M4**: the frozen manuscript quoted
`Pi = dv*B/(rho*delta*v*T) -> 1` (dimensionally inconsistent, missing the
velocity square and the factor 1/2) and presented the collapse as validation.

## First-principles derivation

Ballistic coefficient `B = m/(Cd A)`. Drag acceleration on an object moving
at velocity `v_rel` relative to the atmosphere:

    a_drag = rho |v_rel|^2 / (2 B)

For a near-circular orbit the corotating-atmosphere correction is
essentially constant around the orbit,

    v_rel = v - omega_E a cos(i),   v = sqrt(mu / a)

(the out-of-plane component of omega x r contributes at second order). With
a fractional enhancement `delta` acting for a residence time `T_eff` in
which the object is continuously inside the enhanced volume, the *extra*
along-track impulse is

    dv_extra = integral rho delta v_rel^2 / (2 B) dt = rho delta v_rel^2 T_eff / (2 B)

so the correct dimensionless group is

    Pi_benefit = 2 dv_extra B / (rho delta v_rel^2 T)      -> 1 when T_eff = T.

The theoretical limit is therefore **exactly 1 with the factor 1/2 carried
inside the definition of Pi**, not 1/2. The frozen prose omitted `v^2`,
which is a typographical error in the manuscript, not in the code: the code
always used `rho * d * v**2 * T / (2 B)`.

The corresponding semi-major-axis rate follows from the energy equation,
`de/dt = v . a_drag` with `e = -mu/2a`:

    da/dt = -2 a^2 v a_drag / mu = -(a rho v / B) (v_rel / v)^2

which is the form now integrated in `src/orbits/fastprop.py`.

## Corotation defect found and fixed

The frozen semi-analytic propagator used the inertial speed `v` in both the
decay rate and the extra-impulse accumulator, while the Cowell reference
propagator (`src/orbits/propagator.py`) correctly used
`v_rel = v - omega x r`. The two therefore disagreed by
`(v/v_rel)^2 - 1`:

| inclination | 250 km | 400 km | 550 km |
|---|---|---|---|
| 28.5 deg | +11.9% | +12.4% | +12.8% |
| 51.6 deg | +8.2% | +8.5% | +8.8% |
| 97.6 deg | -1.6% | -1.7% | -1.7% |

This exactly accounts for the previously unexplained Gate-2 residual: the
frozen `fastprop_vs_cowell_250km` check (i = 51.6 deg) reported a 8.08%
relative difference against a 10% tolerance, versus a predicted 8.2%. After
adding `corotation_factor(a, inc)` to `fastprop`, the same check returns
**0.12%**, and the gate tolerance is tightened from 10% to 1%.

Consequences: all drag-derived quantities for prograde orbits decrease by
8-12% (and increase ~1.7% for the sun-synchronous retrograde cases), and all
lifetimes lengthen correspondingly. Every affected result is regenerated;
none of the qualitative conclusions depend on a 10% amplitude change, since
the study's boundaries are set by orders of magnitude (transit geometry,
transport timescales) rather than by this factor.

## Is the collapse evidence of anything?

Partly tautological, and the manuscript now says so. `Pi_benefit -> 1` for
the uniform-enhancement ensemble is guaranteed by construction because the
simulator accumulates `rho delta v_rel^2 /(2B) dt` and the predictor
evaluates the closed-form integral of the same expression. What the collapse
does test, and all that is now claimed:

1. **Internal consistency / dimensional reduction**: the 480-member ensemble
   (4 regimes x 120 objects x random delta) is described by a single
   dimensionless number, so response magnitude across altitude, ballistic
   coefficient, regime and enhancement amplitude can be read off one curve.
2. **Non-trivial residual dispersion**: deviations from 1 are not zero. They
   measure the difference between the orbit-averaged density actually
   sampled along the (J2-precessing, slightly eccentric) trajectory and the
   single-point equatorial density used in the closed form, plus the finite
   `dt_day` integration step. The dispersion is the useful output, not the
   mean.
3. It is **not** independent physical validation. Validation against an
   independent physics path is the Cowell cross-check in Gate 2, which is
   where the corotation defect above was in fact detected.

The manuscript wording is changed from "validates the scaling law" to
"reduces the response to a single dimensionless group and quantifies the
residual dispersion of the orbit-averaged approximation".
