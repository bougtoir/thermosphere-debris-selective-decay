# Localized Thermospheric Density Enhancement for Selective Orbital Debris Decay

A fully reproducible computational feasibility and boundary study: can a
spatially and temporally localized thermospheric density perturbation
selectively accelerate the decay of low-Earth-orbit (LEO) debris while
limiting collateral drag on protected spacecraft?

**Scope.** This is a feasibility/boundary study, not a hardware blueprint.
The intervention is modeled as an abstract, externally imposed density
perturbation. No directed-energy hardware, no operational procedures, and no
named operational spacecraft are modeled. Synthetic targets are used for all
optimization; public orbital catalogs inform population distributions only.

## Reproduction

```bash
pip install -r requirements.txt
make quick   # lightweight end-to-end smoke run (minutes)
make all     # complete reproduction of all reported numbers, figures, tables
```

All parameters live in `config/default.yaml`. Every phase script writes
machine-readable outputs to `results/` and `data/processed/`; the manuscript
is generated from those outputs (no hard-coded scientific values).

## Layout

- `src/atmosphere` — NRLMSISE-00 wrapper and background-density model
- `src/orbits` — equations of motion (gravity + J2 + drag), propagator, validation
- `src/intervention` — abstract density-perturbation models and spreading surrogates
- `src/energy` — thermodynamic lower-bound and energy-accounting calculations
- `src/optimization` — timing/scheduling optimization
- `src/uncertainty` — Monte Carlo and sensitivity analysis
- `scripts/phaseXX_*.py` — one script per study phase (see `docs/`)
- `tests/` — unit and validation tests
- `docs/` — feasibility audit, phase handoffs, QC audits, decision log
- `references/references_verified.csv` — verified bibliography ledger
- `manuscript/` — generated manuscript sources

## Physical-model (GITM) study

The current manuscript (*Self-consistent thermospheric response limits the orbital-drag selectivity of a localized
heat source: a coupled GITM–orbit study*) replaces the prescribed-Gaussian study above with paired heated/control
GITM simulations coupled to an orbit population. Its code is on tag `gitm-orbit-selectivity-v1`.

- Processed GITM fields (five NPZ files, about 0.4 GB): https://doi.org/10.5281/zenodo.24101202 — place them in
  `data/physical/processed/` (checksums in `data/physical/PROCESSED_MANIFEST.csv`).
- Reproduce figures, tables, manuscript and QC from the processed fields (no GITM needed; about 8 min, about 2 GB RAM):
  `pip install -r requirements.txt`, then the command sequence in `docs/PUBLIC_REPRODUCTION_FINAL_REPORT.md`
  (ends with `make physical-qc`).
- GITM runs: upstream https://github.com/GITMCode/GITM commit `c4fc3150aca274e0e0496ba415696a57d0703e00`,
  patched with `physical/gitm/apply_patch.py` (heating hook `physical/gitm/user_perturbation_heating.f90` and a
  block-allocation guard); case definitions in `physical/gitm/cases/`; execution records (case manifests, input
  files, logs) in `data/physical/run_records/`; raw-output SHA-256 manifest in `data/physical/GITM_RUN_MANIFEST.csv`.
  The raw output (about 54 GB) is not deposited and is available from the author on request.
- Provenance and reproduction audits: `docs/RAW_SIMULATION_PROVENANCE_AUDIT.md`,
  `docs/PUBLIC_REPRODUCTION_FINAL_REPORT.md`, `docs/ZENODO_PUBLICATION_AUDIT.md`,
  `docs/DATA_AVAILABILITY_FINAL_AUDIT.md`.

## License

MIT (code). Manuscript text: CC-BY-4.0.
