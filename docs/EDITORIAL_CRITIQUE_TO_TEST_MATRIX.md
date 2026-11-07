# Editorial critique → test matrix (Gate 0)

Authoritative decision: AISR-D-26-03405 (desk rejection; same project as AISR-S-26-05628).
The verbatim decision letter is not stored in the repository. This matrix uses the four grounds given in the
author's rebuild brief: (E1) insufficient novelty, (E2) insufficient quantitative support, (E3) technical
writing, and (E4) figure/table quality. Baseline: `main@ac67802` (see `docs/PHYSICAL_REBUILD_BASELINE.md`).

## A. Mapping of each criticism

| ID | Editorial ground | Diagnosis in the baseline paper | Response type | Falsifiable test / action (gate) | Pass criterion fixed before running |
|---|---|---|---|---|---|
| E1a | Novelty | The headline "drag impulse scales as (1+delta)" is the drag equation itself (tautological; baseline Sect. 3.3). | Experiment | Replace the prescribed multiplier delta(r,t) with the density response of an established self-consistent I-T model (GITM) to an abstract heat source; test whether the response is *not* reproducible by any Gaussian multiplier (sign changes, displaced maxima, remote responses) (G3). | Novelty is claimed only if the physical response differs from the best-fitting Gaussian patch by more than the numerical-resolution uncertainty in a quantity that changes an orbital conclusion (G4/G5). |
| E1b | Novelty | The exposure/occupancy gap decomposition is geometric bookkeeping. | Manuscript (if GO) / limitation | Keep as an idealized comparator only; do not present it as a result. | n/a |
| E1c | Novelty | No comparison with the closest prior *model-experiment* studies (thermospheric heating responses, TADs/TIDs, storm-time density). | Literature (G5) | Nearest-prior table with concrete methods/results. | Each headline claim has ≥1 directly comparable prior study listed with the difference stated. |
| E2a | Quantitative support | delta was an imposed input; nothing tied delta to an energy input except a hydrostatic lower bound. | Experiment | Paired control/perturbed GITM runs with explicit source normalization (W, W m^-3, J), giving density anomaly per unit deposited energy at orbital altitudes (G3). | Energy deposited by the hook equals the configured source to <1% (diagnostic integral). |
| E2b | Quantitative support | Transport persistence came from a diffusion/advection/relaxation surrogate with prescribed coefficients (11/27 combinations). | Experiment | Measure anomaly spread, drift, relaxation and sign from GITM fields; compare to the surrogate's kappa/u/tau (G3). | Physical e-folding time and spread reported with resolution sensitivity (two grids). |
| E2c | Quantitative support | The energy figure (~5.8e7 W) was a thermodynamic lower bound with no dynamics. | Experiment | Compare the GITM energy required for a given density anomaly at 400 km with the hydrostatic lower bound (G3/G5). | Ratio reported with uncertainty; lower bound must not exceed the physical value (consistency check). |
| E2d | Quantitative support | Orbital outcomes used the prescribed field only. | Experiment | Feed the GITM density (and wind) anomaly into the existing validated propagator for synthetic objects; compare with the Gaussian comparator (G4). | Interpolation/frame/time-resolution uncertainty quantified and smaller than the reported difference, otherwise reported as unresolved. |
| E2e | Quantitative support | No independent benchmark of the background atmosphere beyond MSIS. | Validation | Unmodified GITM regression benchmark (upstream reference solution) and GITM-vs-NRLMSISE-00 background comparison (G2). | Tolerances in `docs/PHYSICAL_MODEL_VALIDATION.md`, fixed before comparison. |
| E3 | Technical writing | Dense numeric prose, many caveats, idealized and simulated arms intertwined. | Manuscript (only if GO) | Rewrite around the physical-model result (G6). | Hostile-review pass (G7). |
| E4 | Figure/table quality | 8 figures + 8 tables + 4 S-figures + 9 S-tables, many low information density. | Manuscript (only if GO) | Redesign from canonical CSVs (G6). | Each figure carries one claim; all cited in order (G7). |

## B. Claims already established by prior computation (kept, not re-run)

| Claim | Status | Why it stands without new physics |
|---|---|---|
| Drag impulse along a co-located enhancement scales as (1+delta) | Established, but tautological | Drag equation identity; not a result. |
| Earth-fixed patch sampled for ~4.4% of a 2 h window | Established geometry | Orbital kinematics. |
| Fast propagator agrees with Cowell to 0.062% (10 d) | Established validation | Numerical check, independent of the atmosphere model. |
| Natural decay lifetimes from NRLMSISE-00 | Established, empirical | Background climatology control. |

## C. Claims that need new physical evidence

| Claim in baseline | Needed evidence | Gate |
|---|---|---|
| "In situ heating lowers the local density" | Self-consistent response at and above the heated level | G3 |
| Patch persistence vs winds/diffusion (11/27) | Physical relaxation/spread under resolved dynamics | G3 |
| ~5.8e7 W lower bound for delta=5 at 400 km | Density anomaly per deposited power in a dynamical model | G3 |
| Selectivity vs collateral | Remote/global response (waves, composition) reaching protected orbits | G3/G4 |

## D. Explicitly unresolved limitations (carried forward unless closed)
- No real energy-deposition mechanism (abstract heat source only; no hardware, no targeting).
- Sub-grid scales: anything below ~4 grid cells of the chosen model resolution is unresolved.
- Single background regime per pilot unless compute allows more.
