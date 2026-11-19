#!/usr/bin/env bash
# Run GITM cases sequentially (2 vCPU VM). usage: run_queue.sh case1 case2 ...
set -u
D=$(cd "$(dirname "$0")" && pwd)
while [ ! -f "$HOME/models/runs/spin4/GITM.DONE" ]; do sleep 60; done
for c in "$@"; do
  echo "$(date -u +%FT%TZ) start $c"
  python3 "$D/run_case.py" "$D/cases/$c.json"
  echo "$(date -u +%FT%TZ) end $c"
done
