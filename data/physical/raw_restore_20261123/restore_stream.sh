#!/bin/bash
# Disk-limited restore: download each part, verify SHA-256, stream into zstd|tar, delete part.
set -euo pipefail
cd /home/ubuntu/models/_dl
REL=thermosphere-gitm-raw-2026-11-23
rm -f fifo; mkfifo fifo
( cd /home/ubuntu/models && zstd -d -q < _dl/fifo | tar -x ) &
TARPID=$!
exec 3>fifo
for p in $(awk '{print $2}' ARCHIVE_PARTS_SHA256.txt); do
  for try in 1 2 3; do
    rm -f "$p"; gh release download $REL -R bougtoir/wip -p "$p" && break || sleep 10
  done
  exp=$(grep " $p\$" ARCHIVE_PARTS_SHA256.txt | awk '{print $1}')
  got=$(sha256sum "$p" | awk '{print $1}')
  echo "$(date -u +%FT%TZ) $p size=$(stat -c%s $p) sha=$got $( [ "$exp" = "$got" ] && echo OK || echo FAIL)" >> PART_VERIFY.log
  [ "$exp" = "$got" ] || { echo "SHA FAIL $p"; exit 1; }
  cat "$p" >&3
  rm -f "$p"
done
exec 3>&-
wait $TARPID
echo "$(date -u +%FT%TZ) EXTRACT_DONE rc=$?" >> PART_VERIFY.log
