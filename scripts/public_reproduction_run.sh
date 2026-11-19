#!/usr/bin/env bash
# Clean-environment reproduction from public GitHub clone + public Zenodo NPZ (no raw GITM data).
set -u
cd /home/ubuntu/repro_final/clone
export PATH=/home/ubuntu/repro_final/venv/bin:/usr/bin:/bin MPLBACKEND=Agg PYTHONHASHSEED=0
mkdir -p data/physical/processed
cp ../zenodo/*_slices.npz data/physical/processed/
run() { local t0=$(date +%s); echo "### $*"; env "$@" > /dev/null 2> ../logs/err_$(date +%s%N).txt; local rc=$?; echo "rc=$rc dt=$(( $(date +%s)-t0 ))s :: $*" | tee -a ../steps.log; }
mkdir -p ../logs; : > ../steps.log
sha256sum data/physical/processed/*.npz > ../npz_sha256.txt
run python -m pytest -q
run python scripts/physical_g3r_spread.py p11_z300 p10_z300 p11_z150
run python scripts/physical_g3r_spread.py p11_z300_fine
run G3R_COARSEN=2 python scripts/physical_g3r_spread.py p11_z300_fine
run python scripts/physical_g3r_spread.py p11_z300_fine12
run G3R_COARSEN=2 python scripts/physical_g3r_spread.py p11_z300_fine12
run python scripts/physical_g3r_orbit_sensitivity.py p11_z300 p10_z300
run G3R_TMAX_S=10800 G3R_VARIANTS=nominal python scripts/physical_g3r_orbit_sensitivity.py p11_z300 p11_z300_fine
run G3R_TMAX_S=10800 G3R_VARIANTS=nominal G3R_COARSEN=2 python scripts/physical_g3r_orbit_sensitivity.py p11_z300_fine
run G3R_TMAX_S=43200 G3R_VARIANTS=nominal python scripts/physical_g3r_orbit_sensitivity.py p11_z300 p11_z300_fine12
run G3R_TMAX_S=43200 G3R_VARIANTS=nominal G3R_COARSEN=2 python scripts/physical_g3r_orbit_sensitivity.py p11_z300_fine12
run python scripts/physical_g3r_grid.py p11_z300 p11_z300_fine 10800
run python scripts/physical_g3r_grid.py p11_z300 p11_z300_fine12 43200
run python scripts/physical_g4_orbit_coupling.py p11_z300 p10_z300 p11_z150
run python scripts/physical_g4t_gaussian_decomposition.py p11_z300 p11_z300_fine 10800
run python scripts/physical_g4t_gaussian_decomposition.py p11_z300 p11_z300_fine12 43200
run python scripts/physical_g4t_selectivity_evolution.py p11_z300 p11_z300_fine12
run G3R_COARSEN=2 python scripts/physical_g4t_selectivity_evolution.py p11_z300_fine12
run python scripts/physical_g3_summary.py
run python scripts/physical_g4t_tradeoff.py
run python scripts/physical_g5_prediction_check.py
run python scripts/physical_g5_contribution_gate.py
run make physical-qc PY=python
run python scripts/acta_semantic_checks.py
git status --short > ../git_status_after.txt
echo REPRO_DONE
