#!/usr/bin/env bash
# Build read-only "virtual" 0-12 h run directories for the fine pair by symlinking the 0-3 h outputs of
# c8b_* and the 3-12 h outputs of c8x_* (c8x's first snapshot at 03:00:03 duplicates c8b's 03:00:00 and is
# skipped). Heating input, manifest and heating log come from c8b (the hook is off after 02:00 UT, and the
# restarted c8x log restarts E_cum at 0). No original file is copied or modified.
set -eu
R=$HOME/models/runs
for k in ctrl p11_z300; do
  M=$R/c8f_$k
  mkdir -p "$M/UA/data" "$M/UA/DataIn"
  ln -sfn "$R/c8b_$k/UA/DataIn/user_heating.in" "$M/UA/DataIn/user_heating.in"
  ln -sfn "$R/c8b_$k/case_manifest.json" "$M/case_manifest.json"
  [ -f "$R/c8b_$k/UA/data/user_heating_log.dat" ] && ln -sfn "$R/c8b_$k/UA/data/user_heating_log.dat" "$M/UA/data/"
  for f in "$R/c8b_$k"/UA/data/3DALL_t*; do ln -sfn "$f" "$M/UA/data/"; done
  for f in "$R/c8x_$k"/UA/data/3DALL_t*; do
    case "$(basename "$f")" in 3DALL_t020321_030003*) continue;; esac
    ln -sfn "$f" "$M/UA/data/"
  done
  echo "$M: $(ls "$M"/UA/data/*.header | wc -l) snapshots"
done
