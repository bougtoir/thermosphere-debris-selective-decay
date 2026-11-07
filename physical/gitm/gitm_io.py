"""Read GITM per-block 3DALL output (UA/data/3DALL_tYYMMDD_HHMMSS.bNNNN + .header).

Each block file holds one Fortran sequential record per grid point (real*8,
nVars values), looped alt (outer) -> lat -> lon (inner), including 2 ghost
cells on every side (output_common.f90: output_3dall).
"""
from __future__ import annotations

import glob
import os
import re

import numpy as np


def read_header(path: str) -> dict:
    lines = [ln.strip() for ln in open(path)]
    h: dict = {"vars": []}
    i = 0
    while i < len(lines):
        s = lines[i]
        m = re.match(r"^(-?\d+)\s+(\S.*)$", s)
        if m:
            key = m.group(2)
            val = int(m.group(1))
            if key in ("nBlocksAlt", "nBlocksLat", "nBlocksLon", "nvars", "nAltitudes",
                       "nLatitudes", "nLongitudes", "Year", "Month", "Day", "Hour",
                       "Minute", "Second", "Millisecond"):
                h[key] = val
            elif "nvars" in h and len(h["vars"]) < h["nvars"]:
                h["vars"].append(key)
        i += 1
    return h


def read_snapshot(prefix: str, ghost: int = 2) -> dict:
    """prefix = '.../3DALL_t020320_000000'. Returns dict var -> (nLon, nLat, nAlt) arrays
    on the assembled global grid (ghost cells removed), plus lon/lat in degrees, alt in km."""
    h = read_header(prefix + ".header")
    nv, na, nla, nlo = h["nvars"], h["nAltitudes"], h["nLatitudes"], h["nLongitudes"]
    files = sorted(glob.glob(prefix + ".b[0-9][0-9][0-9][0-9]"))
    nbx, nby = h["nBlocksLon"], h["nBlocksLat"]
    assert len(files) == nbx * nby, (len(files), nbx, nby)
    rec = np.dtype([("m0", "<i4"), ("v", "<f8", (nv,)), ("m1", "<i4")])
    blocks = []
    for f in files:
        a = np.fromfile(f, dtype=rec)
        assert a.size == na * nla * nlo and np.all(a["m0"] == nv * 8), f
        v = a["v"].reshape(na, nla, nlo, nv)[ghost:-ghost, ghost:-ghost, ghost:-ghost, :]
        blocks.append(np.transpose(v, (2, 1, 0, 3)))  # lon, lat, alt, var
    # GITM block ordering: iBlock = iLon + (iLat-1)*nBlocksLon (lon fastest)
    rows = [np.concatenate(blocks[j * nbx:(j + 1) * nbx], axis=0) for j in range(nby)]
    g = np.concatenate(rows, axis=1)
    out = {name: g[..., k] for k, name in enumerate(h["vars"])}
    out["lon_deg"] = np.degrees(out["Longitude"][:, 0, 0])
    out["lat_deg"] = np.degrees(out["Latitude"][0, :, 0])
    out["alt_km"] = out["Altitude"][0, 0, :] / 1e3
    out["header"] = h
    return out


def snapshots(datadir: str) -> list[str]:
    return sorted({os.path.splitext(p)[0] for p in glob.glob(os.path.join(datadir, "3DALL_t*.header"))})
