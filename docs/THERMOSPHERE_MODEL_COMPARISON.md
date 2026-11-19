# Gate 1 — Thermosphere model comparison and selection

Date (UTC): 2026-11-07. Branch `devin/1794047620-physical-model-rebuild`.
Sources: cloned source trees (pinned below), official documentation snapshots in
`data/physical/raw/model_docs/`, and the model-description papers in
`references/verified_model_literature.csv` (Crossref records retained in
`data/physical/raw/crossref/`). Items marked *(inferred)* are my estimates, not
documented facts.

## 1. Candidates

| Item | NCAR TIE-GCM | GITM | WACCM-X | NRLMSISE-00 / NRLMSIS 2.0 / JB2008 |
|---|---|---|---|---|
| Official source | github.com/NCAR/tiegcm | github.com/GITMCode/GITM (+ GITMCode/Electrodynamics) | CESM (escomp/CESM), WACCM-X component | empirical codes (nrlmsise00 Python package already used by baseline) |
| Version inspected | TIEGCM-3.0.1, commit f93028a (2026-10-23) | commit c4fc315 ("20260904.2"); Electrodynamics 3edb662; reference-solution pair a76c88f / 18a8264 | not installed (Liu et al. 2018, doi:10.1002/2017MS001232) | NRLMSISE-00 (Picone et al. 2002) |
| License | NCAR TIE-GCM Open Source Academic Research License (LICENSE file) | Apache-2.0 (LICENSE file) | CESM open source (not re-verified here) | public |
| Governing equations | first-principles 3D nonlinear neutral + ion momentum, energy, continuity; self-consistent dynamo (Richmond et al. 1992; Qian et al. 2014; Wu et al. 2025) | 3D neutral and ion continuity, momentum (incl. full vertical momentum, non-hydrostatic) and energy, per-species vertical velocities (Ridley et al. 2006; Deng et al. 2008) | whole-atmosphere (0 to upper thermosphere) CAM physics + thermosphere/ionosphere extension, self-consistent electrodynamics, O+ transport (Liu et al. 2018) | none — climatological fits |
| Neutral–plasma coupling | coupled ion drag, Joule heating, dynamo | coupled ion drag, Joule heating; high-latitude potential from empirical model (Weimer 2005 used here) or coupled | coupled | none |
| Energy equation | neutral, ion, electron temperatures | neutral (UserHeatingRate term enters directly, `add_sources.f90`), ion, electron | neutral, ion, electron | none |
| Vertical grid | pressure levels; lower boundary ~97 km, upper ~500–700 km (solar-activity dependent), half or quarter scale height | altitude grid, 50 levels from 100 km to ~600–750 km (here 100–744 km), stretched ~1/3 scale height; MSIS lower BC | hybrid pressure, surface to ~500–700 km | n/a |
| Horizontal grid | 5° standard (docs); v3.0 increases horizontal and vertical resolution (Wu et al. 2025) | user set: blocks of 9×9 cells (`ModSize.f90`), global or regional; here 10°×5° (4×4 blocks) and 5°×2.5° (8×8 blocks) | ~1.9°×2.5° typical *(inferred from paper)* | continuous |
| Time step / CFL | fixed sub-minute step, semi-implicit | explicit, CFL-limited (CFL 0.75 used, Δt ≈ 4.3 s at 10°×5°) | ~minutes *(inferred)* | n/a |
| Localized forcing hook | none generic; must edit energy-source routines | `user_perturbation` + `UserHeatingRate` already wired into the neutral energy equation (`advance.f90`, `add_sources.f90`) | must edit CAM physics | n/a (prescribed patches only) |
| Benchmarks | benchmark page in the official docs; runs require the official input data set | `srcTests/auto_test` with stored reference solutions | CESM test suite | published statistical comparisons |
| Drivers | F10.7, F10.7A, Kp or IMF/SW, HP, CPCP | F10.7, F10.7A, IMF/solar wind, SME/AE (or HPI), optional FISM | as TIE-GCM plus lower atmosphere | F10.7, F10.7A, Ap |
| Validation data | CHAMP/GRACE density, ISR, TEC (literature) | CHAMP/GRACE density and others (literature) | as left | statistical fits to drag/accelerometer/ISR data |
| Outputs | density, Tn, Ti, Te, winds, composition, potentials (netCDF) | Rho, 11 neutral species, Tn, Te, Ti, neutral and ion winds, ion species, Ne (binary per block) | full atmosphere | ρ, T, species |
| Install on this VM (2 vCPU, 7.6 GB RAM) | source builds (gfortran/MPI/netCDF available), but required initial-condition/source-history data are only distributed via an authenticated Globus endpoint (anonymous access returned `AuthenticationFailed`) | built; upstream reference test passes at a76c88f/18a8264; science build at c4fc315 runs | CESM build plus large input data; HPC-scale | already in baseline |
| Runtime here | not testable without data | 10°×5°: ≈ 8 min wall per simulated hour on 2 ranks (measured) | not feasible *(inferred)* | seconds |
| Orbit-code coupling | interpolation of netCDF ρ(lon,lat,p→z,t) | interpolation of ρ(lon,lat,z,t) on altitude grid (reader `physical/gitm/gitm_io.py`) | as TIE-GCM | already coupled |

SAMI3 and similar ionosphere-only codes were excluded because they do not solve
the neutral energy/momentum equations that control mass density. The empirical
models are retained only as controls: they cannot respond to an imposed heat
source.

## 2. Weighted decision matrix (scores 1–5)

Weights fixed before scoring.

| Criterion | Weight | TIE-GCM | GITM | WACCM-X |
|---|---|---|---|---|
| Physical self-consistency for a localized neutral heat source (energy-equation access, non-hydrostatic response) | 0.25 | 4 | 5 | 4 |
| Installability and data access on this VM, reproducibly | 0.25 | 1 | 5 | 1 |
| Usable resolution within compute budget | 0.20 | 2 (untestable) | 3 | 1 |
| Reproducible upstream benchmark available here | 0.15 | 1 | 4 | 1 |
| Output and orbit-coupling convenience | 0.10 | 4 | 4 | 3 |
| License clarity for redistribution of configs/results | 0.05 | 4 | 5 | 4 |
| **Weighted score** | 1.00 | **2.40** | **4.40** | **2.15** |

## 3. Decision

**GITM is selected** as the primary physical model. Reasons: an existing hook
adds a heating term directly to the neutral energy equation; the solver is
non-hydrostatic, which matters for strong localized heating (Deng et al. 2008);
it builds and passes its own reference test on this VM; it is Apache-2.0.

TIE-GCM would be the preferred independent model cross-check, but it cannot be
run without the authenticated data set. This is a recorded limitation: Gate 2
has no second physical model, so model-structure uncertainty is bounded only by
(a) NRLMSISE-00 for the unperturbed background and (b) published GITM/TIE-GCM
behaviour quoted from the literature, not by new TIE-GCM runs.

## 4. Consequences for later gates

* Resolution: the horizontal grid on 2 cores is 10°×5° (≈ 1100×550 km at the
  equator) with a 5°×2.5° convergence case. Any source narrower than about two
  cells is unresolved; source widths are chosen accordingly and sub-grid
  sources are out of scope.
* Background: one controlled background (equinox, F10.7 = F10.7A = 150,
  constant IMF Bz = −2 nT, Vsw = 400 km/s, SME = 150 nT) — a deliberately
  limited regime that is documented as such.
