# Sobol' sensitivity audit (Phase 2)

Addresses hostile-review item **C1**: the frozen `phase10_sobol.csv`
reported `S1 = 0.830 > ST = 0.548` for `delta_max`, which is impossible for
a deterministic model, and `sum(S1) = 1.26 > 1`.

Artefacts: `results/tables/sobol_reproduction_check.csv`,
`results/tables/sobol_convergence.csv`, driver
`scripts/audit_sobol.py`, shared response `src/uq/sobol_response.py`.

> **Scope note after the NRLMSISE-00 unit correction.** Sections 1-3 were
> executed *before* the density-unit defect was found (commit `6c4a442`)
> and document the bit-exact reproduction of the frozen pre-revision
> indices. After the correction every density-dependent number changed, so
> those frozen indices are by construction no longer reproducible: the
> legacy code path now reproduces the *corrected* production run to within
> the sampler/sample-size difference between legacy N = 32 and production
> N = 1024 (`max |S1 diff| = 1.9e-1`, bounded by the N = 32 rung of the
> ladder in section 4), while the response-equivalence check of the cost
> reductions is unaffected (`max rel diff = 2.3e-4`). Sections 4-6 below
> report the corrected physics.

## 1. Exact reproduction of the frozen result (pre-correction, historical)

| item | value |
|---|---|
| SALib | 1.6.0 (`SALib.__version__` is absent; version from `pip show`) |
| sampler in frozen code | `SALib.sample.saltelli.sample` (deprecated shim, unscrambled, no seed) |
| design | `calc_second_order=False`, d = 6, N = 32 -> N(d+2) = 256 evaluations |
| estimator | `SALib.analyze.sobol`, Jansen/Saltelli estimators, 100 bootstrap resamples, 95% CI |
| response | extra delta-v of the case-A target under the idealized tracking bound, 40 d horizon, 10 s exposure step |
| distributions | independent uniforms on the stated bounds; no transformations |
| determinism | response is deterministic; no stochastic term, no failed runs, all 256 responses finite |

Rerunning the frozen code path reproduces `phase10_sobol.csv` to
**max |S1 diff| = 8.0e-17, max |ST diff| = 3.6e-17** (floating-point
equality). Parameter order, column order and the `S1`/`ST` mapping were
checked element-by-element: there is no misalignment, no parsing error, no
NaN handling issue. **The frozen numbers are exactly what the frozen code
computes; the defect is statistical, not clerical.**

## 2. Why S1 > ST appeared

The frozen confidence intervals are enormous: `S1 = 0.830 +/- 0.384`,
`ST = 0.548 +/- 0.312`. With 256 evaluations for 6 parameters, the Jansen
estimators are dominated by sampling noise, and nothing prevents a noisy S1
from exceeding a noisy ST. The violation (+0.20 at N = 32) is inside one
confidence interval and is not evidence of a model pathology.

No index was ever clipped, reordered or forced to satisfy `S1 <= ST`.

## 3. Cost reductions used for the convergence study (both verified)

1. **Horizon = perturbation window.** `fastprop.decay_lifetime` accumulates
   extra drag impulse only inside an active delta window, so propagating for
   40 days instead of the window adds exactly zero to the response. Verified
   by construction and by the response comparison below.
2. **60 s exposure step instead of 10 s.** For the tracking geometry the
   object stays at the patch centre, so the integrand is smooth. Direct
   step-refinement of `mean(rho*delta)`:

   | fine_dt_s | mean(rho*delta) |
   |---|---|
   | 5 | 1.4671466123e-14 |
   | 10 | 1.4671466110e-14 |
   | 30 | 1.4671465893e-14 |
   | 60 | 1.4671465064e-14 |
   | 120 | 1.4671460612e-14 |

   End-to-end, over the first 64 frozen design points the fast response
   differs from the 40-day/10 s response by at most **1.8e-4 relative** -
   three orders of magnitude below the index confidence intervals. The 10 s
   default is kept everywhere else, where objects transit a fixed patch in
   minutes.

## 4. Convergence ladder

Seeded (`seed` from `config/default.yaml`) scrambled Sobol' sequence via the
modern `SALib.sample.sobol` API. (The deprecated `saltelli` shim is retained
*only* for the bit-exact reproduction in section 1; the two generate
different point sets and must not be interchanged silently.)

Corrected-physics ladder (`results/tables/sobol_convergence.csv`):

| N base | evaluations | max(S1 - ST) | sum S1 | max S1 CI | wall (s) |
|---:|---:|---:|---:|---:|---:|
| 32 | 256 | +0.225 | 1.266 | 0.329 | 11 |
| 256 | 2048 | +0.006 | 0.957 | 0.128 | 84 |
| 512 | 4096 | -0.000 | 0.960 | 0.082 | 164 |
| 1024 | 8192 | -0.000 | 0.929 | 0.054 | 329 |
| 2048 | 16384 | -0.000 | 0.939 | 0.043 | 679 |

(Wall times are from the clean rebuild on a 2-core machine and are the only
non-deterministic entries in the table.)

Stopping rule (declared before the run): stop when (i) no ordering violation
persists outside its confidence interval, (ii) `sum(S1)` is stable, and
(iii) every S1 confidence interval is below 0.06, i.e. small compared with
the separation between the two dominant parameters and the rest. N = 1024
satisfies all three and N = 2048 changes no index by more than 0.006, so
**N = 1024 (8192 evaluations) is adopted for production**
(`src/uq/sobol_response.N_BASE`), and `scripts/phase10_uncertainty.py` now
uses this pathway instead of the N = 32 design.

## 5. Converged indices (N = 1024, corrected physics)

| parameter | S1 | S1 CI | ST | ST CI |
|---|---:|---:|---:|---:|
| delta_max | 0.564 | 0.054 | 0.598 | 0.050 |
| duration_h | 0.224 | 0.045 | 0.270 | 0.038 |
| sigma_h_km | 0.107 | 0.028 | 0.160 | 0.019 |
| rho_scale | 0.024 | 0.014 | 0.025 | 0.002 |
| B_scale | 0.010 | 0.010 | 0.011 | 0.001 |
| sigma_v_km | -0.000 | 0.001 | 0.000 | 0.000 |

Interpretation. Amplitude dominates (`ST = 0.60`), followed by the duration
over which the enhancement is sustained (`0.27`); `sum S1 = 0.93`, so
interactions account for ~7%. Density scaling and ballistic coefficient
contribute a few percent each within their stated ranges.

The horizontal patch scale is **no longer inert**, and this is a direct
consequence of the density-unit correction rather than a sampling artefact.
With the correct (1000x larger) density the induced drag is large enough
that the target drifts along-track relative to the unperturbed ephemeris
the tracking patch centre follows, so a small patch loses the object within
the window. A direct scan at `delta = 10`, 24 h confirms the mechanism:
the response rises monotonically from 3.47 m/s at `sigma_h = 100 km` to
4.35 m/s at 200 km and 6.17 m/s at 400 km. Perfect co-location therefore
requires continuous re-targeting or a patch large enough to absorb the
drift - the same size/selectivity conflict transport imposes. This is now
stated in the manuscript (Section 3.6). The vertical scale remains inert
because the orbit is circular and stays at the patch mid-plane.

## 6. Effect of the corotation fix

The corotation correction added to `fastprop` (see
`docs/SCALING_LAW_AUDIT.md`) multiplies this response by a constant factor
`(v_rel/v)^2 = 0.9215` (case-A target, 400 km, 51.6 deg): the orbit and
inclination
are fixed across the Sobol design, so the factor is the same for
every design point. Sobol' indices are invariant under a constant positive
scaling of the response, so the corotation fix alone leaves the indices
unchanged and only rescales the response.

The density-unit correction is *not* of this form. It is also a constant
multiplicative factor on rho, but the response is not linear in rho once
the induced decay is large enough to move the object relative to the
tracked patch centre; this is exactly why `sigma_h_km` acquires a non-zero
index above while the response mean rises to `y_mean = 3.04 m/s`.
