"""Gate 2: evaluate the pre-declared acceptance tests V2-V7 on the spin-up.

usage: physical_g2_acceptance.py RUN_DIR [validation_csv]
Writes results/tables/physical_g2_acceptance.csv and prints a Markdown table.
"""
import csv
import glob
import sys

import pandas as pd


def main() -> None:
    run = sys.argv[1]
    v = pd.read_csv(sys.argv[2] if len(sys.argv) > 2 else "results/tables/physical_g2_background_vs_msis.csv")
    dts = []
    for f in glob.glob(f"{run}/UA/data/log*.dat"):
        for line in open(f):
            p = line.split()
            if len(p) > 8 and p[0].isdigit():
                dts.append(float(p[8]))
    late = v[v.hours_since_start >= 18]
    a = {z: late[late.alt_km == z] for z in sorted(v.alt_km.unique())}
    s400 = a[400].sort_values("hours_since_start")
    drift = abs(s400.gitm_rho_mean.iloc[-1] / s400.gitm_rho_mean.iloc[0] - 1)
    rows = [
        ("V2a", "no NaN", bool(v.all_finite.all()), "all finite" if v.all_finite.all() else "NaN present"),
        ("V2b", "Tn within [150,3000] K", bool(v.tn_min_K.min() >= 150 and v.tn_max_K.max() <= 3000),
         f"min {v.tn_min_K.min():.1f} K, max {v.tn_max_K.max():.1f} K"),
        ("V2c", "dt > 1 s", min(dts) > 1, f"min dt {min(dts):.3f} s over {len(dts)} log records"),
        ("V3", "|rho400(24h)/rho400(18h)-1| < 5%", drift < 0.05, f"{100 * drift:.2f}%"),
    ]
    for z in (250, 400, 500):
        r = a[z].rho_ratio
        rows.append((f"V4@{z}", "GITM/MSIS rho in [0.67,1.5]", bool(r.between(0.67, 1.5).all()),
                     f"{r.min():.3f}-{r.max():.3f}"))
    dT = a[400].gitm_tn_mean - a[400].msis_tn_mean
    rows.append(("V5", "Tn400 - MSIS within 150 K", bool((dT.abs() <= 150).all()),
                 f"{dT.min():+.1f} to {dT.max():+.1f} K"))
    q = a[300].gitm_o_n2_mean / a[300].msis_o_n2_mean
    rows.append(("V6", "O/N2 at 300 km within x2", bool(q.between(0.5, 2).all()), f"ratio {q.min():.3f}-{q.max():.3f}"))
    w = a[300].gitm_vh_max
    ne = late.gitm_ne_max
    rows.append(("V7a", "max |Vh| at 300 km in [50,600] m/s", bool(w.between(50, 600).all()),
                 f"{w.min():.0f}-{w.max():.0f} m/s"))
    rows.append(("V7b", "peak Ne in [1e11,5e12] m^-3", bool(ne.between(1e11, 5e12).all()),
                 f"{ne.min():.2e}-{ne.max():.2e} m^-3"))
    with open("results/tables/physical_g2_acceptance.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["test", "criterion", "pass", "value"])
        wr.writerows(rows)
    print("| Test | Criterion | Result | Value |\n|---|---|---|---|")
    for t, c, p, val in rows:
        print(f"| {t} | {c} | {'PASS' if p else 'FAIL'} | {val} |")


if __name__ == "__main__":
    main()
