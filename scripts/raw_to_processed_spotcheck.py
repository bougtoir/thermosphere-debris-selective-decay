"""Spot-check processed NPZ fields against the retained raw GITM 3DALL block files.

Independent of physical/gitm/gitm_io.py: own header parser and block assembly. Writes
results/provenance/raw_to_processed_spotcheck.csv. Requires the raw run directories (not deposited).
"""
import glob
import os
import re

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.expanduser("~/models/runs")
PAIRS = {"p11_z300": ("c4_ctrl", "c4_p11_z300r"), "p10_z300": ("c4_ctrl", "c4_p10_z300"),
         "p11_z150": ("c4_ctrl", "c4_p11_z150"), "p11_z300_fine": ("c8b_ctrl", "c8b_p11_z300"),
         "p11_z300_fine12": ("c8f_ctrl", "c8f_p11_z300")}
VARS = {"rho": "Rho", "ve": "V!Dn!N (east)", "vn": "V!Dn!N (north)", "vu": "V!Dn!N (up)"}


def header(path):
    txt = open(path).read()
    num = {k: int(v) for v, k in re.findall(r"^\s*(\d+)\s+(n\w+|Day|Hour|Minute|Second)\s*$", txt, re.M)}
    vl = txt.split("VARIABLE LIST")[1]
    names = [ln.split(None, 1)[1].strip() for ln in vl.strip().splitlines()
             if re.match(r"^\s*\d+\s+\S", ln)][:num["nvars"]]
    return num, names


def assemble(prefix):
    num, names = header(prefix + ".header")
    nv, na, nla, nlo = num["nvars"], num["nAltitudes"], num["nLatitudes"], num["nLongitudes"]
    bl = []
    for f in sorted(glob.glob(prefix + ".b????")):
        raw = np.fromfile(f, dtype=np.uint8)
        rec = raw.reshape(-1, 8 + 8 * nv)[:, 4:4 + 8 * nv].copy().view("<f8").reshape(na, nla, nlo, nv)
        bl.append(rec[2:-2, 2:-2, 2:-2])
    nbx, nby = num["nBlocksLon"], num["nBlocksLat"]
    g = np.concatenate([np.concatenate(bl[j * nbx:(j + 1) * nbx], axis=2) for j in range(nby)], axis=1)
    g = np.transpose(g, (2, 1, 0, 3))  # lon, lat, alt, var
    t = num["Hour"] * 3600 + num["Minute"] * 60 + num["Second"] + 86400 * (num["Day"] - 21)
    return {n.replace("  ", " "): g[..., k] for k, n in enumerate(names)}, t


def main():
    rows = []
    for label, (cd, pd_) in PAIRS.items():
        z = np.load(os.path.join(ROOT, f"data/physical/processed/{label}_slices.npz"))
        heat = np.array(open(os.path.join(RUNS, pd_, "UA/DataIn/user_heating.in")).read().split(), float)
        pre = {}
        for tag, d in (("c", cd), ("p", pd_)):
            pre[tag] = sorted(p[:-7] for p in glob.glob(os.path.join(RUNS, d, "UA/data/3DALL_t*.header")))
        ts = z["t_s"]
        for i in sorted({0, len(ts) // 2, len(ts) - 1}):
            for tag in ("c", "p"):
                hit = None
                for pf in pre[tag]:
                    num = header(pf + ".header")[0]
                    t = num["Hour"] * 3600 + num["Minute"] * 60 + num["Second"] + 86400 * (num["Day"] - 21)
                    if t == ts[i]:
                        hit = pf
                        break
                g, t = assemble(hit)
                alt = g["Altitude"][0, 0, :] / 1e3
                m = (alt >= 200) & (alt <= 700)
                for v, key in VARS.items():
                    ref = g[key][:, :, m].astype(np.float32)
                    a = z[f"{tag}_{v}"][i]
                    rel = np.abs(a.astype(float) - ref) / np.maximum(np.abs(ref), 1e-30)
                    rows.append(dict(label=label, run=cd if tag == "c" else pd_, snapshot=os.path.basename(hit),
                                     t_s=int(ts[i]), var=v, max_abs_diff=float(np.abs(a - ref).max()),
                                     max_rel_diff_rho=float(rel.max()) if v == "rho" else np.nan,
                                     exact=bool(np.array_equal(a, ref)),
                                     alt_match=bool(np.allclose(alt[m], z["alt_km"])),
                                     heating_match=bool(np.array_equal(heat, z["heating"]))))
        print(label, flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(ROOT, "results/provenance/raw_to_processed_spotcheck.csv"), index=False)
    print(df.groupby("label")[["exact", "alt_match", "heating_match"]].all().to_string())
    print("all exact:", df.exact.all(), "n=", len(df))


if __name__ == "__main__":
    main()
