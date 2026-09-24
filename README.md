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

## License

MIT (code). Manuscript text: CC-BY-4.0.
