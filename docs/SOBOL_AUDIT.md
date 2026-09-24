# Sobol' sensitivity audit (Phase 2)

Addresses hostile-review item **C1**: the frozen `phase10_sobol.csv`
reported `S1 = 0.830 > ST = 0.548` for `delta_max`, which is impossible for
a deterministic model, and `sum(S1) = 1.26 > 1`.

Artefacts: `results/tables/sobol_reproduction_check.csv`,
`results/tables/sobol_convergence.csv`, driver
`scripts/audit_sobol.py`, shared response `src/uq/sobol_response.py`.

## 1. Exact reproduction of the frozen result

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

| N base | evaluations | max(S1 - ST) | sum S1 | max S1 CI | wall (s) |
|---:|---:|---:|---:|---:|---:|
| 32 | 256 | +0.202 | 1.258 | 0.304 | 12 |
| 256 | 2048 | +0.0002 | 0.929 | 0.116 | 103 |
| 512 | 4096 | -0.0000 | 0.952 | 0.092 | 203 |
| 1024 | 8192 | +0.0000 | 0.921 | 0.055 | 391 |
| 2048 | 16384 | -0.0000 | 0.919 | 0.043 | 760 |

Stopping rule (declared before the run): stop when (i) no ordering violation
persists outside its confidence interval, (ii) `sum(S1)` is stable, and
(iii) every S1 confidence interval is below 0.06, i.e. small compared with
the separation between the two dominant parameters and the rest. N = 1024
satisfies all three and N = 2048 changes no index by more than 0.003, so
**N = 1024 (8192 evaluations) is adopted for production**
(`src/uq/sobol_response.N_BASE`), and `scripts/phase10_uncertainty.py` now
uses this pathway instead of the N = 32 design.

## 5. Converged indices (N = 1024)

| parameter | S1 | S1 CI | ST | ST CI |
|---|---:|---:|---:|---:|
| delta_max | 0.414 | 0.055 | 0.488 | 0.053 |
| duration_h | 0.478 | 0.054 | 0.553 | 0.055 |
| rho_scale | 0.020 | 0.014 | 0.028 | 0.003 |
| B_scale | 0.008 | 0.010 | 0.013 | 0.002 |
| sigma_h_km | ~0 (-8e-7) | 2e-6 | ~0 (3e-10) | 1e-10 |
| sigma_v_km | ~0 (1e-9) | 6e-9 | ~0 (8e-15) | 4e-15 |

Interpretation, which is *unchanged in direction but corrected in
magnitude*: the response is controlled almost equally by enhancement
amplitude and by the duration over which the enhancement stays on the
target (S1 ~ 0.41 and ~0.48; `sum S1 = 0.92`, so interactions account for
~8%). Environmental density scaling and ballistic coefficient contribute a
few percent each within their stated ranges. Patch dimensions have
*identically zero* influence in this configuration - not because size does
not matter physically, but because the tracking bound keeps the object at
the patch centre by construction, where the Gaussian value is `delta_max`
regardless of sigma. This is a direct diagnostic of the idealization, and is
now stated as such in the manuscript rather than as a physical insensitivity
to patch size. The transit-limited fixed-patch results (Phase 6) show the
opposite: there, geometry dominates.

## 6. Effect of the corotation fix

The corotation correction added to `fastprop` (see
`docs/SCALING_LAW_AUDIT.md`) multiplies this response by a constant factor
`(v_rel/v)^2 = 0.9215` (case-A target, 400 km, 51.6 deg): the orbit and
inclination are fixed across the Sobol design, so the factor is the same for
every design point. Sobol' indices are invariant under a constant positive
scaling of the response, so the converged indices above are unaffected; only
the response mean and standard deviation scale (`y_mean` 5.24e-3 ->
4.83e-3 m/s). The production rerun in the Phase-18 rebuild confirms this.
