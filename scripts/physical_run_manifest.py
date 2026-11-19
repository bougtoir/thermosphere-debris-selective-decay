"""Record every file of completed GITM runs (size, SHA-256) in
data/physical/GITM_RUN_MANIFEST.csv. Raw output stays on the VM under
~/models/runs (too large for git); this ledger makes it verifiable.

usage: physical_run_manifest.py RUN_DIR [RUN_DIR ...]   (appends/replaces rows per run)
"""
import csv
import datetime as dt
import hashlib
import os
import sys

OUT = "data/physical/GITM_RUN_MANIFEST.csv"
F = ["run", "relpath", "size_bytes", "sha256", "mtime_utc", "hashed_utc"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    runs = [os.path.abspath(r) for r in sys.argv[1:]]
    old = list(csv.DictReader(open(OUT))) if os.path.exists(OUT) else []
    old = [o for o in old if o["run"] not in runs]
    now = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    for r in runs:
        for d, _, fs in os.walk(r):
            for f in sorted(fs):
                p = os.path.join(d, f)
                if os.path.islink(p) or not os.path.isfile(p):
                    continue
                old.append(dict(run=r, relpath=os.path.relpath(p, r), size_bytes=os.path.getsize(p), sha256=sha(p),
                                mtime_utc=dt.datetime.utcfromtimestamp(os.path.getmtime(p)).strftime(
                                    "%Y-%m-%dT%H:%M:%SZ"), hashed_utc=now))
        print(r, flush=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=F)
        w.writeheader()
        w.writerows(old)


if __name__ == "__main__":
    main()
