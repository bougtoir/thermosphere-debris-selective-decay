# Phase 2 handoff

Gate 2: PASS

| check                               | metric                                                      |        value |     tol | passed   |
|:------------------------------------|:------------------------------------------------------------|-------------:|--------:|:---------|
| energy_conservation_j2_5orbits      | max |dE/E|                                                  |  4.05038e-15 |   1e-07 | True     |
| angmom_conservation_twobody_5orbits | max |dh/h|                                                  |  2.00987e-15 |   1e-09 | True     |
| convergence_rtol_1e-07              | endpoint |dr| [m]                                           |  6.61942e-08 | nan     | True     |
| convergence_rtol_1e-09              | endpoint |dr| [m]                                           |  3.48637e-08 | nan     | True     |
| convergence_rtol_1e-11              | endpoint |dr| [m]                                           |  1.09901e-07 | nan     | True     |
| circular_orbit_closure              | closure error [m] after 1 period                            |  1.39648e-05 |   0.01  | True     |
| j2_raan_rate_consistency            | RAAN rate [deg/day]                                         | -5.00233     | nan     | True     |
| fastprop_vs_cowell_250km            | relative 10-day altitude-drop difference (drag-only, no J2) |  0.0808358   |   0.1   | True     |
| decay_scales_inverse_B              | drop(B=60)/drop(B=30) at 250 km storm, 30 d                 |  0.5         | nan     | True     |

Notes: RAAN rate compared via the SGP4-standard secular formula; semi-analytic decay cross-checked against the Cowell propagator (DOP853) for a strong-decay case.
