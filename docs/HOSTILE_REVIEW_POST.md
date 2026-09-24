# Post-revision hostile review

Second adversarial review, conducted on the revised tree after the Phase
2-17 audits and reanalysis. The same five reviewer roles were used as in
`HOSTILE_REVIEW_PRE.md` (R1 orbital mechanics, R2 thermosphere/space
weather, R3 numerics/UQ, R4 skeptical debris remediation, R5 ASR
scope/novelty), each instructed to try to break the revised claims against
the generated CSVs rather than against the prose.

Severity definitions are unchanged.

## 1. Disposition of pre-revision issues

| ID | Sev | Status | Evidence in revised tree |
|---|---|---|---|
| C1 | CRITICAL | **resolved** | Convergence ladder N = 32, 256, 512, 1024, 2048 (`results/tables/sobol_convergence.csv`); at N = 2048 zero `S1 > ST` violations outside CIs, `max |dST|` between the two largest rungs = 0.005, `sum S1 = 0.94`. Production indices reported at N = 1024 with CIs. No index clipped or reordered (`docs/SOBOL_AUDIT.md`). |
| C2 | CRITICAL | **resolved** | Every selectivity record now carries an exposure class (`physical_exposure`, `gaussian_tail`, `below_numerical_resolution`, `no_encounter`) and a `ratio_meaningful` flag from the shared classifier `src/analysis/exposure_class.py`; QC enforces the flag/class consistency. Primary reporting is absolute target benefit, absolute protected-object collateral and encounter status; ratios are secondary diagnostics. The former 1.2e80 headline no longer appears: pairs D and G are reported as no-encounter with undefined ratios. |
| C3 | CRITICAL | **resolved** | Lifetimes are reported as right-censored lower bounds with the censoring policy stated in Methods and the censored cells marked in Table 1 (`n_censored` = 21 of 396 rows, injected from `phase1_scale_calculations.csv`). No `inf` is described as a physical lifetime. |
| M1 | MAJOR | resolved | Wording is "41% of surveyed parameter combinations" (11 of 27), with the explicit statement that no distribution over transport parameters was assumed, plus a grid-choice sensitivity table and figure (`transport_boundary_sensitivity.csv`, Fig. S4): the one-hour fraction ranges 8.3%-55.6% across grid variants. |
| M2 | MAJOR | resolved | Each diffusivity and wind bound is cited to thermospheric literature in `references/references_verified.csv`, and the boundary's sensitivity to those bounds is reported rather than asserted. |
| M3 | MAJOR | resolved | The tracking configuration is labelled an idealized mathematical upper bound in the abstract, methods, results, discussion, limitations and conclusions, and the fixed-pulse/tracking gap is decomposed into window duration (x12), fraction of window inside the patch (x22.5) and mean enhancement while inside (x6.3), closing the observed ratio to -1.5% (`gap_decomposition_factors.csv`). |
| M4 | MAJOR | resolved | Pi is derived from the drag law in Methods, the group is dimensionally correct, and the collapse (slope 1.010, R^2 = 0.9995, mean Pi = 1.041 +/- 0.102) is described as internal consistency / dimensional reduction, explicitly *not* independent validation. |
| M5 | MAJOR | resolved | `matched_exposure.csv` reports localized tracking, matched target exposure, matched intervention spacetime and matched thermal-energy conventions side by side; the manuscript states that both target benefit and protected collateral depend on the matching convention. |
| M6 | MAJOR | resolved | Framing is the quantitative exclusion boundary on five axes, positioned against differential drag, storm-drag, drag augmentation and ADR (`docs/JOURNAL_AUDIT.md`). No feasibility claim is made anywhere. |
| M7 | MAJOR | resolved | Energies are labelled strict thermodynamic lower bounds. Both the in-situ bound and the newly added hydrostatic column-expansion bound are reported (`energy_bounds_audit.csv`); the column bound exceeds the in-situ bound by a factor 168 at 400 km, and the text states delivered engineering energy cannot be inferred from either. |
| m1-m5, x1-x2 | MINOR/COSMETIC | resolved | Conventions (`B = m/(Cd A)`, co-rotating relative velocity) stated in Methods; the exposure-step refinement check is reported; 2-D dilution stated as a limitation; the co-orbital twin is a figure panel; captions made self-contained; notation unified; rendered tables rounded. |

## 2. New issues found in the revised tree

| ID | Sev | Reviewer | Issue | Resolution |
|---|---|---|---|---|
| N1 | CRITICAL | R2 | NRLMSISE-00 total mass density (`gtd7` output index 5) is returned in g/cm^3 but was consumed as kg/m^3, so every density-dependent result was low by 1e3. | Fixed in `src/atmosphere/msis.py` with an explicit `G_CM3_TO_KG_M3` conversion; magnitude regression tests added against published thermospheric densities (`tests/test_atmosphere_units.py`); **all** density-dependent outputs, figures, tables and manuscript numbers regenerated. Pre-correction results are preserved at tag `pre-revision-checkpoint` and documented in `docs/PRE_REVISION_STATE.md`. |
| N2 | MAJOR | R1 | The fast propagator used inertial velocity while the Cowell cross-check used atmosphere-relative velocity, a ~8% inconsistency that was inside no stated gate. | `corotation_factor()` added to `src/orbits/fastprop.py` and applied consistently to secular decay and extra impulse; fast/Cowell 10-day altitude-drop difference is now 1.4e-3 relative, inside the 1% gate. |
| N3 | MAJOR | R3 | After N1 the frozen pre-correction Sobol' indices can no longer be reproduced bit-exactly, so the reproduction check in `SOBOL_AUDIT.md` sections 1-3 reads as a failure. | The audit now separates three distinct comparisons - historical bit-exact pre-correction reproduction, the legacy code path under corrected physics, and the corrected convergence ladder - and says which is which. Nothing is claimed as reproduced that is not. |
| N4 | MINOR | R3 | Under corrected density the horizontal patch scale is no longer inert in the tracking bound (ST = 0.16), contradicting the pre-revision statement that patch size has identically zero influence. | Mechanism identified and reported: the patch centre follows the unperturbed ephemeris, so the drag the intervention itself induces drifts the object towards the edge of a small patch within a day (direct scan: 3.47 -> 4.35 -> 6.17 m/s for sigma_h = 100, 200, 400 km). Stated in Section 3.6 and `docs/SOBOL_AUDIT.md` section 5 as a further limit on perfect co-location, not as a benefit. |

## 3. Reviewer verdicts on the revised tree

**R1.** Censoring, conventions and the corotation fix remove my two blocking
objections. The fast/Cowell agreement at the 1e-3 level is now a real check
rather than a coincidence of two different velocity conventions.

**R2.** The density-unit defect was the single most damaging thing in the
tree and it is now fixed with a magnitude test that would catch a recurrence.
I still regard the prescribed multiplicative enhancement as a surrogate, not
a thermospheric response, and the paper now says exactly that at every
fidelity level. The two energy bounds together make the energetic
implausibility unavoidable without overclaiming a delivered-energy number.

**R3.** Indices are converged, CIs are reported, nothing is clipped, and the
one surprising change (patch scale becoming active) has an identified
mechanism rather than a rationalization. The provenance CSVs let me check
any manuscript number against a generated table in one step.

**R4.** The paper now leads with the absolute per-event impulse and the
co-orbital failure, which is the honest reading of this dataset. Matched
exposure is settled three ways instead of one.

**R5.** In scope and the novelty claim is now an exclusion boundary rather
than textbook drag physics. No sentence in the revised manuscript implies
technological feasibility.

## 4. Final tally

- CRITICAL open: **0** (C1-C3 resolved; N1 found and fixed in this revision)
- MAJOR open: **0 actionable** (M1-M7, N2-N3 resolved)
- MINOR/COSMETIC open: 0 blocking

Remaining acknowledged limitations are scope limitations, stated in the
manuscript's Limitations section, not unresolved review findings: no
self-consistent neutral/plasma energy equation, no wind feedback, 2-D
amplitude dilution for a 3-D patch, synthetic object population, and no
delivery mechanism analysis.
