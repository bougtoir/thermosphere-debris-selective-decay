#!/usr/bin/env bash
# Post-process the fine-grid pair (c8b_ctrl / c8b_p11_z300) once it has finished. Order matters.
set -eux
R=$HOME/models/runs
cd "$(dirname "$0")/../.."
while [ ! -f "$R/c8b_p11_z300/GITM.DONE" ]; do sleep 60; done
python3 scripts/physical_g3_paired.py "$R/c8b_ctrl" "$R/c8b_p11_z300" p11_z300_fine
python3 scripts/physical_g3r_forcing.py p11_z300_fine "$R/c8b_p11_z300"
python3 scripts/physical_g3r_spread.py p11_z300_fine
G3R_COARSEN=2 python3 scripts/physical_g3r_spread.py p11_z300_fine
G3R_TMAX_S=10800 G3R_VARIANTS=nominal python3 scripts/physical_g3r_orbit_sensitivity.py p11_z300_fine
G3R_TMAX_S=10800 G3R_VARIANTS=nominal G3R_COARSEN=2 python3 scripts/physical_g3r_orbit_sensitivity.py p11_z300_fine
python3 scripts/physical_g3r_grid.py p11_z300 p11_z300_fine 10800
python3 scripts/physical_g5_prediction_check.py
python3 scripts/physical_g3_audit_doc.py
python3 scripts/physical_g3r_g4t_docs.py
echo POST_FINE_DONE
