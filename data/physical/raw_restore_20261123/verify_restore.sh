#!/bin/bash
cd /home/ubuntu/models
echo "start $(date -u +%FT%TZ)"
( cd runs && sha256sum -c <(sed 's#  ./#  #' ../_dl/RAW_FILES_SHA256.txt) 2>&1 | grep -v ': OK$' > ../_dl/VERIFY_RUNS_NOT_OK.txt; echo "runs_not_ok=$(wc -l < ../_dl/VERIFY_RUNS_NOT_OK.txt)" )
sha256sum -c _dl/GITM_BUILD_TREE_SHA256.txt 2>&1 | grep -v ': OK$' > _dl/VERIFY_BUILD_NOT_OK.txt; echo "build_not_ok=$(wc -l < _dl/VERIFY_BUILD_NOT_OK.txt)"
bad=0; while IFS=$'\t' read -r l t; do got=$(readlink "runs/${l#./}"); [ "$got" = "$t" ] || { bad=$((bad+1)); echo "$l $t $got" >> _dl/VERIFY_SYMLINKS_BAD.txt; }; done < _dl/RAW_SYMLINKS.tsv; echo "symlinks_bad=$bad"
echo "regular_files_runs=$(find runs -type f | wc -l) symlinks_runs=$(find runs -type l | wc -l)"
echo "done $(date -u +%FT%TZ)"
