#!/usr/bin/env bash
# Create a GITM run directory (same layout as GITM's `make rundir`).
# usage: setup_run.sh <rundir> [<restart_source_dir>]
set -euo pipefail
GITM=${GITM_DIR:-$HOME/models/GITM}
R=$1
mkdir -p "$R/UA/data" "$R/UA/restartOUT" "$R/UA/restartIN"
cp -a "$GITM/srcData/." "$R/UA/DataIn/" 2>/dev/null || cp -a "$HOME/models/runs/timing/UA/DataIn/." "$R/UA/DataIn/"
ln -sfn "$GITM/ext/Electrodynamics/data/ext" "$R/UA/extIE"
ln -sfn "$GITM/src/GITM.exe" "$R/GITM.exe"
cd "$R"
for l in DataIn data extIE restartIN restartOUT; do ln -sfn "UA/$l" "$l"; done
if [ $# -ge 2 ]; then cp -a "$2/UA/restartOUT/." UA/restartIN/; fi
