# Public reproduction — final report

Date: 2026-11-18 (UTC). **Verdict: PASS** — all figures, tables, manuscript values, grid-sensitivity and Gaussian
metrics, selectivity results and the prediction scorecard were regenerated from public material only.

## 1. Inputs (public only)

| Input | Identifier | Check |
|---|---|---|
| Code | anonymous `git clone` (empty global git config, no credentials) of https://github.com/bougtoir/thermosphere-debris-selective-decay, branch `devin/1794047620-physical-model-rebuild` at `e5ac28580ec72bc1863762e310c4cee49acf283f` (same analysis code as tag `gitm-orbit-selectivity-v1`) | GitHub API HTTP 200 without token |
| Data | the 5 npz files downloaded without login from https://doi.org/10.5281/zenodo.24101202 (`results/provenance/zenodo_public_download_manifest.json`) | size and MD5 = Zenodo; SHA-256 = `data/physical/PROCESSED_MANIFEST.csv` |
| Environment | new `python3 -m venv` (Python 3.10.12, Ubuntu 22.04), `pip install -r requirements.txt`: numpy 2.2.6, scipy 1.15.3, pandas 2.3.3, matplotlib 3.10.9, python-docx 1.2.0, python-pptx 1.0.2, Pillow 12.3.0, PyYAML 6.0.2 | no packages from the working environment |

No raw GITM output, working-repository file or VM path was used (`scripts/public_reproduction_run.sh`).

## 2. Commands

`scripts/public_reproduction_run.sh` (24 steps, all exit 0, 8 min wall time; the largest step used about 1.8 GB RAM; log
`results/provenance/public_reproduction_steps.log`): pytest; `physical_g3r_spread.py` (5 labels, fine also remapped
2×2); `physical_g3r_orbit_sensitivity.py` (11 coarse variants; 3 h and 12 h nominal, fine native and remapped);
`physical_g3r_grid.py` (3 h, 12 h); `physical_g4_orbit_coupling.py p11_z300 p10_z300 p11_z150`;
`physical_g4t_gaussian_decomposition.py` (3 h, 12 h); `physical_g4t_selectivity_evolution.py` (native, remapped);
`physical_g3_summary.py`; `physical_g4t_tradeoff.py`; `physical_g5_prediction_check.py`;
`physical_g5_contribution_gate.py`; `make physical-qc` (bootstrap, figures, manuscript, QC);
`acta_semantic_checks.py`.

## 3. Comparison with the committed canonical outputs

`scripts/public_reproduction_compare.py` → `results/provenance/public_reproduction_compare.csv`. 110 tracked output
files in `results/` and `manuscript/physical/` were compared with the committed versions.

| Output | Result |
|---|---|
| Figures 1–5 (TIFF 600 dpi and PNG, `manuscript/physical/figures/`, `results/figures/physical/`) | byte-identical |
| Tables 1–4 (`tables.docx`) and table sources | text and all cells identical; source CSVs byte-identical |
| Manuscript value ledger (`results/manuscript_physical_values.csv`, 164 values in the text) | byte-identical |
| Manuscript, review copy, highlights, cover letter (DOCX) | text identical; files differ only in package timestamps |
| Figures PPTX | same shapes and embedded images; package timestamps differ |
| Grid-sensitivity metrics, G3R spread metrics, selectivity evolution, bootstrap intervals, G4 coupling tables | byte-identical |
| `orbit_interpolation_sensitivity.csv`, `physical_g3_summary.csv` | row order only; values identical (max difference 0) |
| `physical_g4t_gaussian_matching.csv`, `acta_semantic_checks.csv` | row order; max absolute difference 2.7e-15 (floating-point summation order) |
| Prediction scorecard (`physical_prediction_outcomes.csv`) | byte-identical: 15 confirmed, 7 falsified, 4 outside range without falsification |
| Manuscript QC / semantic checks | 34/34 PASS / 325/325 PASS |
| `results/power_effect_selectivity.csv` | existing 9 rows identical; 3 rows for the 150-km case added (see below) |

Tolerances: CSV values must agree within 1e-12 relative (actual maximum 4.0e-16); figures must agree pixel by pixel;
DOCX text and tables must be identical. All met.

Examples of principal values regenerated (value ledger): 12 h selectivity at 400/500 km 1.51/2.03 (coarse), 1.49/2.04
(fine); non-target share of extra drag at 400 km 84% (coarse) and 85% (fine); peak density response at 400 km +204%;
target extra Δv at 400 km 6.6 mm/s; lifetime change 0.010 d of 129 d; 10/100 GW peak ratio 0.31; 150/300 km peak ratio 0.16.

**Stale intermediate found:** the committed `results/power_effect_selectivity.csv` (2026-11-08 00:32Z) predated the
150-km orbit coupling (01:55Z) and lacked its three rows. The file feeds only the G4T trade-off document, not the
manuscript, figures or tables. The regenerated file (identical in the working repository) is now committed.

## 4. Not reproduced

- Processed npz from raw GITM output: needs the 54 GB raw runs (not deposited). Instead, 120 arrays from all five npz
  were checked bit-for-bit against the retained raw files (`docs/RAW_SIMULATION_PROVENANCE_AUDIT.md`).
- GITM simulations: not rerun. Reproducing results from processed fields does not show that the simulations are
  reproducible.
- The Zenodo code snapshot (commit 8aa5205) pins PyYAML 5.4.1, which fails to build in a clean venv; the test used the
  repository's corrected pin (6.0.2). PyYAML is not used by the physical-model scripts.
