# Final decision log (ASR revision)

Every scientific decision taken during the revision, with the reason and the
artefact that records it. Decisions are listed in the order they were taken.
Where a decision changed a reported number, the regenerating command is
given; no manuscript number is hand-edited.

## Freeze and provenance

| # | Decision | Reason | Artefact |
|---|---|---|---|
| 1 | Freeze the merged pre-revision state at tag `pre-revision-checkpoint` and never rewrite it. | Pre-correction results must remain inspectable and clearly separable from corrected results. | `docs/PRE_REVISION_STATE.md`, git tag |
| 2 | Conduct the hostile review *before* any manuscript editing. | Prevents the revision from being shaped to defend existing prose. | `docs/HOSTILE_REVIEW_PRE.md` |

## Physics and numerics

| # | Decision | Reason | Artefact / command |
|---|---|---|---|
| 3 | Convert NRLMSISE-00 total mass density from g/cm^3 to kg/m^3 and add magnitude regression tests. | `gtd7` output index 5 is g/cm^3; consuming it as kg/m^3 understated every density by 1e3. | `src/atmosphere/msis.py`, `tests/test_atmosphere_units.py` |
| 4 | Regenerate **all** density-dependent outputs rather than patching affected numbers. | Partial regeneration would leave internally inconsistent tables. | `make clean && make all` |
| 5 | Use atmosphere-relative velocity consistently in the fast propagator via `corotation_factor()`. | The fast propagator used inertial velocity while the Cowell cross-check used relative velocity (~8% inconsistency). | `src/orbits/fastprop.py`; fast/Cowell agreement 1.4e-3 |
| 6 | Report finite-horizon non-reentering lifetimes as right-censored lower bounds, never as `inf` or as physical lifetimes. | The values are integrator/horizon caps, not physics. | Methods + Table 1 censoring marks |
| 7 | Keep the exposure integral at a 10 s fine step everywhere except the tracking Sobol' response (60 s), with the refinement check reported. | Transits of a fixed patch last minutes; the tracking integrand is smooth (rel. difference < 2e-4). | `docs/SOBOL_AUDIT.md` section 3 |

## Statistics and uncertainty

| # | Decision | Reason | Artefact |
|---|---|---|---|
| 8 | Converge Sobol' indices over N = 32, 256, 512, 1024, 2048 with a declared stopping rule; report at N = 1024. | The frozen N = 32 design gave CIs wider than the indices and an impossible `S1 > ST` ordering. | `results/tables/sobol_convergence.csv` |
| 9 | Never clip, reorder or post-hoc constrain sensitivity indices; report violations as computed. | A constrained index is not an estimate. | `docs/SOBOL_AUDIT.md` section 2 |
| 10 | Separate historical bit-exact pre-correction reproduction from corrected-physics results in the Sobol' audit. | After decision 3 the frozen indices cannot be reproduced by construction; conflating the two would read as a reproduction failure or, worse, as a silent overwrite. | `docs/SOBOL_AUDIT.md` scope note |
| 11 | Report the newly non-zero horizontal patch-scale sensitivity with its mechanism instead of suppressing it. | Under corrected density the induced drag drifts the target off an ephemeris-following patch centre; this is an additional limit on co-location, not a benefit. | `docs/SOBOL_AUDIT.md` section 5, Section 3.6 |

## Interpretation and claims

| # | Decision | Reason | Artefact |
|---|---|---|---|
| 12 | Classify every exposure record and flag selectivity ratios as meaningful only for physically exposed protected objects. | Ratios against Gaussian tails or non-encounters are float arithmetic below physical resolution (the former 1.2e80 headline). | `src/analysis/exposure_class.py`, `results/tables/numerical_zero_audit.csv` |
| 13 | Lead with absolute target benefit, absolute protected collateral and encounter status; demote ratios to diagnostics. | Absolute quantities are what remediation and protection decisions depend on. | Results, Table 3 |
| 14 | State the transport result as "41% of surveyed parameter combinations" (11 of 27) and publish the grid-choice sensitivity (8.3%-55.6%). | No distribution over transport parameters was assumed; the number moves with the grid. | `results/tables/transport_boundary_sensitivity.csv`, Fig. S4 |
| 15 | Label the tracking configuration an idealized mathematical upper bound at every occurrence and decompose its gap to the fixed pulse. | The bound dominates every favourable number; quoting it unlabelled alongside physical results is misleading. | `results/tables/gap_decomposition*.csv` |
| 16 | Report three matching conventions (target exposure, intervention spacetime, thermal energy) rather than equal `delta_max` alone. | "Localization buys selectivity" is partly a statement about the matching convention. | `results/tables/matched_exposure.csv` |
| 17 | Add a hydrostatic column-expansion energy bound alongside the in-situ bound, and label both strict thermodynamic lower bounds. | The in-situ bound understates the requirement by a factor ~168 at 400 km; neither is a delivered engineering energy. | `results/tables/energy_bounds_audit.csv` |
| 18 | Describe the Pi collapse as internal consistency / dimensional reduction, not validation. | Predictor and simulator evaluate the same drag law. | `docs/SCALING_LAW_AUDIT.md`, Results |
| 19 | Make no feasibility, hardware, deployment or targeting claim anywhere, and use only synthetic objects. | The study quantifies an exclusion boundary; it does not propose an intervention. | `docs/DECLARATIONS.md`, `data/processed/cases.csv` |

## Reporting and reproducibility

| # | Decision | Reason | Artefact |
|---|---|---|---|
| 20 | Inject every manuscript number from a generated CSV and fail the build on any unmapped value. | Hard-coded numbers drift from the analysis. | `results/manuscript_value_provenance.csv` |
| 21 | Emit citation order provenance and require every citation to resolve to the verified ledger, numbered in order of first appearance. | Vancouver-style numbering must be checkable mechanically. | `results/manuscript_citations.csv`, `references/references_verified.csv` |
| 22 | Submit figures as separate files and also provide an inline-figure reading copy and an editable English deck. | ASR submits figures separately; reviewers and co-authors still need a readable copy. | `manuscript/manuscript.docx`, `manuscript_inline.docx`, `manuscript_figures.pptx` |
| 23 | Verify the pipeline from a clean tree (`make clean && make all && make quick`) before packaging. | Reproducibility claims must be exercised, not asserted. | `docs/REPRODUCIBILITY_AUDIT.md` |
| 24 | Exclude caches, credentials, internal-only material and irrelevant binaries from the submission ZIP, with a SHA-256 manifest. | Submission hygiene and verifiability. | `submission/ASR_final_submission.zip`, `MANIFEST.md` |

## Explicitly rejected alternatives

- **Rescaling affected numbers by 1e3 instead of regenerating.** Rejected:
  the response is not linear in density once induced decay moves the object
  relative to the patch (decision 11).
- **Dropping the pre-correction Sobol' reproduction section.** Rejected:
  deleting it would hide that the frozen indices are superseded.
- **Keeping the 1.2e80 selectivity as a "formal" result.** Rejected: it is
  below numerical resolution, not a physical ratio.
- **Presenting the Pi collapse as validation.** Rejected as circular.
- **Quoting a delivered-power requirement.** Rejected: only lower bounds are
  defensible from this model.
