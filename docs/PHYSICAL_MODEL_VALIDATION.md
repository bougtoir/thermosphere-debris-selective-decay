# Gate 2 — Physical model build and validation (GITM)

## 1. Build provenance

| Item | Value |
|---|---|
| Model | GITM, github.com/GITMCode/GITM |
| Science build | commit c4fc3150aca274e0e0496ba415696a57d0703e00 ("GITM Version 20260904.2"), Electrodynamics 3edb6622 |
| Reference-test build | GITM a76c88f + Electrodynamics 18a8264 (the pair at which `srcTests/auto_test/ref_solns` were generated) |
| Configure | `./Config.pl -install -earth -compiler=gfortran10`, then `make` |
| Compiler / MPI / netCDF | GNU Fortran 11.4.0, Open MPI 4.1.2, netCDF-Fortran 4.5.4 (Ubuntu apt) |
| Precision | `-fdefault-real-8 -fdefault-double-8` (Makefile.conf) |
| Grid per block | `ModSize.f90`: nLons = nLats = 9, nAlts = 50, nBlocksMax = 32 |
| MPI note | the VM's hwloc crashes (SIGFPE) unless `HWLOC_COMPONENTS=no_os,stop` is set; this does not touch model numerics |
| Local source changes | (1) `user_perturbation` replaced by `physical/gitm/user_perturbation_heating.f90`; (2) upstream bug fix: `initialize_fang_arrays` is called once per block and aborts with "Error allocating Fang arrays" when a rank owns more than one block — guarded with `if (allocated(Fang_Ci)) return`. Both applied by `physical/gitm/apply_patch.py`. Neither change alters physics when the heat source is zero. |

## 2. Acceptance tolerances (fixed before any spin-up output was inspected)

The unperturbed background is a controlled, synthetic regime (Gate 1 §4), so
there is no matching satellite data set. Validation therefore has three
levels: (a) the code reproduces its own reference solution, (b) the
background is stable and climatologically plausible against NRLMSISE-00 for
the same date and solar flux, (c) the heating hook conserves the configured
energy. Passing (a)–(c) establishes a *usable* model background; it is not an
observational validation of GITM, which is taken from the literature
(Ridley et al. 2006 and later GITM–CHAMP/GRACE comparisons).

| ID | Test | Acceptance |
|---|---|---|
| V1 | Upstream `UAM.in.00.default.test` vs stored reference (`DiffNum.pl`) | pass |
| V2 | 24-h spin-up stability: no NaN, Tn within [150, 3000] K everywhere, Δt not collapsing (>1 s) | pass |
| V3 | Quasi-steady background: global-mean ρ at ~400 km changes by <5% between hours 18 and 24 | pass |
| V4 | GITM/NRLMSISE-00 global-mean ρ ratio at 250, 400, 500 km (same date/UT, F10.7 = F10.7A = 150, Ap = 7) | within [0.67, 1.5] |
| V5 | Global-mean Tn at ~400 km vs NRLMSISE-00 | within ±150 K |
| V6 | Global-mean [O]/[N2] at ~300 km vs NRLMSISE-00 | within a factor of 2 |
| V7 | Plausibility (no reference model available offline): max horizontal neutral wind at ~300 km in [50, 600] m/s; peak Ne in [1e11, 5e12] m^-3 | pass (plausibility only) |
| V8 | Heating-hook energy closure: deposited power diagnostic vs configured P(t) | |ΔP|/P < 1% |
| V9 | Independent closure: Δ(∫ρ cp T dV) perturbed − control over the first heating minutes vs ∫P dt | within 20% (losses by conduction/radiation/advection start immediately) |
| V10 | Determinism: control run repeated with identical inputs and ranks | max relative ρ difference < 1e-6 (else report as noise floor) |

## 3. Results

(Filled in from `scripts`-generated tables only; see below.)
