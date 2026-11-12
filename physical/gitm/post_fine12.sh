#!/usr/bin/env bash
# Post-process the 0-12 h fine pair (c8b + c8x) once c8x_p11_z300 has finished. The 3-h products
# (label p11_z300_fine, results/grid_sensitivity_metrics.csv) are not touched; the 12-h label is p11_z300_fine12.
set -eux
R=$HOME/models/runs
cd "$(dirname "$0")/../.."
while [ ! -f "$R/c8x_p11_z300/GITM.DONE" ]; do sleep 60; done
grep -q '"exit_code": 0' "$R/c8x_ctrl/case_manifest.json"
grep -q '"exit_code": 0' "$R/c8x_p11_z300/case_manifest.json"
physical/gitm/merge_fine12.sh
python3 scripts/physical_g3_paired.py "$R/c8f_ctrl" "$R/c8f_p11_z300" p11_z300_fine12
python3 scripts/physical_g3r_spread.py p11_z300_fine12
G3R_COARSEN=2 python3 scripts/physical_g3r_spread.py p11_z300_fine12
G3R_TMAX_S=43200 G3R_VARIANTS=nominal python3 scripts/physical_g3r_orbit_sensitivity.py p11_z300 p11_z300_fine12
G3R_TMAX_S=43200 G3R_VARIANTS=nominal G3R_COARSEN=2 python3 scripts/physical_g3r_orbit_sensitivity.py p11_z300_fine12
python3 scripts/physical_g3r_grid.py p11_z300 p11_z300_fine12 43200
python3 scripts/physical_g4t_gaussian_decomposition.py p11_z300 p11_z300_fine12 43200
python3 scripts/physical_g4t_selectivity_evolution.py p11_z300 p11_z300_fine12
G3R_COARSEN=2 python3 scripts/physical_g4t_selectivity_evolution.py p11_z300_fine12
echo POST_FINE12_DONE
