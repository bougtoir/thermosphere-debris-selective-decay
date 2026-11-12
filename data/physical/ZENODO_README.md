# Processed GITM fields and analysis code: orbital-drag selectivity of a localized thermospheric heat source

Contents
- `processed/*.npz` — paired heated/control GITM slices (density, neutral winds, temperature, O/N2 at all model
  altitudes, 10-min outputs) extracted from the raw GITM 3DALL output by `scripts/physical_g3_paired.py`.
  `p11_z300` (100 GW, 300 km, coarse 10°×5°), `p10_z300` (10 GW), `p11_z150` (100 GW, 150 km),
  `p11_z300_fine` (fine 5°×2.5°, 0–3 h), `p11_z300_fine12` (fine, 0–12 h).
- `PROCESSED_MANIFEST.csv` — size and SHA-256 of each npz.
- `GITM_RUN_MANIFEST.csv` — file-level SHA-256 of the raw GITM run directories (about 54 GB = 50 GiB, not deposited; includes failed and test runs).
- `code/repository_snapshot.zip` — `git archive` of the analysis repository (GITM case configurations, heating hook
  `physical/gitm/user_perturbation_heating.f90`, run scripts, analysis/figure/manuscript scripts, canonical result
  tables, frozen predictions).

Reproduction
1. Unzip the snapshot, place the npz files in `data/physical/processed/`.
2. `pip install -r requirements.txt`; `make physical-qc` regenerates the bootstrap table, figures, manuscript and QC.
3. G3/G4 tables: `python3 scripts/physical_g3r_spread.py`; `python3 scripts/physical_g4_orbit_coupling.py <label>` for p11_z300, p10_z300, p11_z150; 12 h comparator and evolution steps as in `physical/gitm/post_fine12.sh` (skip its raw-output steps).
   (see `Makefile` and `docs/`).
4. Full simulations require GITM (https://github.com/GITMCode/GITM, commit c4fc3150aca274e0e0496ba415696a57d0703e00)
   with the heating hook and `physical/gitm/apply_patch.py`; cases are defined in `physical/gitm/cases/`.
   Regenerating the npz files from new GITM runs has not been repeated independently.

Licence: data CC BY 4.0; code MIT (see LICENSE in the snapshot).
