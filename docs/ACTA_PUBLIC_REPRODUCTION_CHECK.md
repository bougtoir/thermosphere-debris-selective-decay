# Acta final delta — public reproduction check (Gate 8)

Test: fresh `git clone` of the public repository https://github.com/bougtoir/thermosphere-debris-selective-decay,
branch `devin/1794047620-physical-model-rebuild` at commit `827042b` (first delta push), into `/home/ubuntu/pubclone`.
No files copied from the working repository except, in step B, the five NPZ files taken from the deposition package
(`/home/ubuntu/deposit/gitm-selectivity-processed-v1/processed/`, SHA-256 identical to `data/physical/PROCESSED_MANIFEST.csv`).

## A. Public clone only (what a reader can do today)

| Step | Result |
|---|---|
| `python3 -m pytest -q` | 34 passed |
| `make physical-qc` | **FAILS** at `physical-figures`: `FileNotFoundError: data/physical/processed/p11_z300_fine12_slices.npz` |
| Manuscript text/values from committed CSVs | possible (builder reads only CSVs) but `make physical-qc` stops at the figure step first |

Conclusion: the public GitHub repository alone does **not** reproduce the figures or the G3/G4 tables.

## B. Public clone + processed fields from the deposition package (what a reader can do once the Zenodo record is public)

| Step | Command | Result |
|---|---|---|
| Bootstrap, figures, manuscript, QC | `make physical-qc` | exit 0; `results/manuscript_physical_values.csv`, `physical_selectivity_bootstrap.csv`, `physical_fig1_panel_ranges.csv`, `physical_fig3_illconditioned_interval.csv`, `qc_physical_manuscript.csv` **byte-identical**; all five figure TIFF/PNG **byte-identical** (no git diff); DOCX/PPTX differ only in package timestamps |
| G3R spread metrics | `python3 scripts/physical_g3r_spread.py` | values identical (max relative difference 2.7e-16; row order differs) |
| Selectivity evolution | `python3 scripts/physical_g4t_selectivity_evolution.py` | identical (max relative difference 2.3e-16; row order differs) |
| Orbit sensitivity / Gaussian matching (12 h) | `G3R_TMAX_S=43200 G3R_VARIANTS=nominal python3 scripts/physical_g3r_orbit_sensitivity.py p11_z300 p11_z300_fine12` (+ `G3R_COARSEN=2 … p11_z300_fine12`) | `physical_g4t_gaussian_matching.csv` byte-identical |
| Gaussian decomposition | `python3 scripts/physical_g4t_gaussian_decomposition.py p11_z300 p11_z300_fine12 43200` | byte-identical |
| GITM–orbit coupling | `python3 scripts/physical_g4_orbit_coupling.py <label>` for p11_z300, p10_z300, p11_z150 | `physical_model_vs_prescribed_patch.csv` and per-object files byte-identical |

The exact command sequence used for the 12 h products is in `physical/gitm/post_fine12.sh` (its raw-output steps,
`merge_fine12.sh` and `physical_g3_paired.py`, need the raw runs and were not repeated).

## C. Not reproduced

- Regenerating the NPZ files from raw GITM output (`physical_g3_paired.py`) — needs the ~54 GB raw run directories,
  which are not deposited (manifest with SHA-256 is public).
- Re-running GITM (source commit `c4fc3150aca274e0e0496ba415696a57d0703e00`, heating hook, `apply_patch.py`, case
  definitions in `physical/gitm/cases/`). This was not attempted in the delta and has not been independently repeated.
  Reproducing figures and tables from processed fields (B) is not evidence that the simulation is reproducible.
