# Reanalysis plan (revision Phase 14)

Written after the root-cause audits (Phases 2-12) and before the
manuscript was resynchronized. It lists every defect found, what it
affected, what had to be recomputed, and what it cost. All pre-revision
outputs remain reachable at tag `pre-revision-checkpoint` (commit
`67f6a72`); nothing historical was deleted or silently overwritten.

## D1 - NRLMSISE-00 mass density interpreted in the wrong units

**Defect.** `src/atmosphere/msis.py` returned `gtd7` output index 5
(total mass density, **g/cm^3**) as if it were kg/m^3, so every density
in the study was low by a factor of 1000.

**Detection.** The energy audit produced patch masses and column masses
that were three orders of magnitude below published thermospheric
values; the `pymsis`/NRLMSISE-00 documentation confirms the output unit.

**Affected code.** `src/atmosphere/msis.py` (wrapper and
`density_profile`), and through the lookup table every phase script.

**Affected results.** All of them. Lifetimes, delta-v, selectivity,
Monte Carlo, Sobol, scaling, negative controls, energy bounds.

**Affected claims.** Every numerical statement in the manuscript,
abstract, highlights, cover letter and slide deck.

**Correction.** Multiply by 1e3 at the single point of conversion; add
`tests/test_atmosphere_units.py`, which checks the profile at 200, 400
and 500 km against published thermospheric magnitudes (within a factor
of five) and checks monotonic decrease with altitude.

**Recompute.** `make clean && make all` - full pipeline, ~35 min
wall clock; plus `make audit-sobol` (~30 min) for the convergence
ladder, which is not part of `all`.

**Verification.** Gate-2 validation suite rerun and passing; the
regression test now fails loudly if the unit convention regresses.

## D2 - Corotation (atmosphere-relative velocity) missing from the fast propagator

**Defect.** The semi-analytic propagator used inertial circular
velocity in the drag law while the Cowell reference used the
atmosphere-relative velocity, giving 8.08% disagreement on the
ten-day drag-only decay test.

**Correction.** `corotation_factor(a, i) = 1 - Omega_E a cos(i)/v`
applied to both `da/dt` and the extra-impulse accumulator in
`src/orbits/fastprop.py`.

**Recompute.** Same full pipeline as D1 (done in the same run).

**Verification.** Fast-vs-Cowell 10-day altitude-drop difference is now
1.4e-3 (0.14%), inside a tightened 1% gate.

## D3 - Selectivity ratios reported without an exposure criterion

**Defect.** Ratios of order 1e6 were reported for protected objects
whose "exposure" was the Gaussian tail of a patch several sigma away,
i.e. a property of the assumed patch shape rather than a physical
result. Cases with no encounter at all produced `inf`/undefined ratios.

**Correction.** `src/analysis/exposure_class.py` classifies every
exposure record as `physical_exposure`, `gaussian_tail`,
`below_numerical_resolution` or `no_encounter` (closest approach beyond
6 patch sigmas or peak delta <= 1e-6), and the ratio carries a
`ratio_status`/`ratio_meaningful` flag. The manuscript now leads with
absolute target benefit and absolute protected collateral; ratios are
secondary and are declared undefined when the denominator is not a
physical exposure.

**Recompute.** Phase 7 and the numerical-zero audit; no additional cost
beyond the full rerun.

## D4 - "41% of plausible combinations" read as a probability

**Defect.** The transport survival fraction was stated in a way that
invites a probabilistic reading, although no probability distribution
over thermospheric transport parameters was ever assumed.

**Correction.** `scripts/audit_transport_boundary.py` re-derives the
fraction over grid variants; the manuscript now says "N of M surveyed
(sigma_h, kappa, u) design combinations", quotes the range over grid
variants, and leads with the conditional statement (selective patch
plus 100 m/s wind), which is robust to the grid choice.

**Recompute.** Audit script only (seconds).

## D5 - Idealized tracking presented too close to a mechanism

**Defect.** "On-target tracking" language could be read as a proposed
capability.

**Correction.** Methods now separates three fidelity levels explicitly
(mathematical perfect-localization upper bound; transport-constrained
surrogate; self-consistent neutral/plasma dynamics, out of scope), and
the bound is labelled in the abstract, methods, results, discussion,
limitations and conclusions as an upper bound that is not hardware, not
a demonstrated atmospheric process, not a feasible control mechanism
and not evidence that co-location can be achieved.

**Recompute.** None (framing only).

## D6 - "Localization changes collateral, not benefit" was convention-dependent

**Defect.** True under matched target exposure; false under a matched
intervention budget.

**Correction.** `scripts/audit_matched_exposure.py` computes all four
conventions (localized bound, matched target exposure, matched enhanced
spacetime volume, matched lower-bound thermal energy) and the
manuscript states the dependence explicitly.

**Recompute.** Audit script (~1 min).

## D7 - Energy bound computed for in-situ heating only

**Defect.** `E_min = m c_p dT` for the patch understates the real
thermodynamic requirement, because heating air *at* a fixed altitude
lowers its density there; raising density at altitude z requires
expanding the column below.

**Correction.** `expansion_temperature_fraction()` in
`src/energy/bounds.py` plus `scripts/audit_energy.py`; both bounds are
reported and both are labelled thermodynamic lower bounds, not
delivered engineering energy (no deposition efficiency, coupling or
loss budget is modelled).

**Recompute.** Audit script (seconds).

## D8 - Sobol sample size not justified; scaling collapse over-claimed

**Defect.** The production Sobol run used N=32 with no convergence
evidence, and the dimensionless collapse was described as validation.

**Correction.** `scripts/audit_sobol.py` runs the ladder N = 32, 256,
512, 1024, 2048 (8N evaluations each) and the production size is now
N=1024, justified by the disappearance of ordering violations, stable
S1 sums, CI below ~0.06, and no important index moving by more than
0.003 at the next rung. The collapse is described as a dimensional
reduction and internal-consistency check, since simulator and predictor
share the same drag equation; the expected constant is 1/2 from
a = rho v_rel^2/(2B).

**Recompute.** `make audit-sobol`, ~30 min; phase 10 rerun in the full
pipeline.

## D9 - Finite-horizon non-decays treated as lifetimes

**Correction.** Objects that do not reach reentry inside the horizon
are reported as right-censored lower bounds and excluded from any
statistic that would treat the horizon as a measured lifetime; the
count of censored cells is reported in Methods and Results.

**Recompute.** None beyond the full rerun (reporting change).

## Total computational cost

| Step | Wall clock |
|---|---|
| `make clean && make all` (full corrected pipeline, figures, tables, manuscript, QC, submission) | ~35 min |
| `make audit-sobol` (convergence ladder, 8N evaluations at 5 rungs) | ~30 min |
| `make quick` (smoke reproduction) | ~2 min |
| `pytest` | <1 min |

All runs are single-machine, deterministic given the seeds in
`config/default.yaml`.
