"""Score the frozen predictions (docs/PRIOR_PREDICTIONS_FROZEN.md) against the
Gate 3/4 tables. Ranges are copied from that file; nothing is tuned here.
Writes results/tables/physical_prediction_outcomes.csv.
"""
import os

import numpy as np
import pandas as pd

G3 = "results/tables/physical_g3_summary.csv"
G4 = "results/physical_model_vs_prescribed_patch.csv"
REF, LOW, Z150, FINE = "p11_z300", "p10_z300", "p11_z150", "c8_p11_z300"


def ts(label):
    p = f"results/tables/physical_g3_{label}_timeseries.csv"
    return pd.read_csv(p) if os.path.exists(p) else None


def verdict(x, lo, hi, flo=None, fhi=None):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "PENDING"
    if lo <= x <= hi:
        return "CONFIRMED"
    if flo is not None and flo <= x <= fhi:
        return "OUTSIDE_RANGE_NOT_FALSIFIED"
    return "FALSIFIED"


def main():
    s = pd.read_csv(G3).set_index(["label", "alt_km"])
    g = pd.read_csv(G4).set_index(["label", "alt_km", "group"])
    have = set(s.index.get_level_values(0))
    r = []

    def add(pid, q, val, v, note=""):
        r.append(dict(prediction=pid, quantity=q, value=val, verdict=v, note=note))

    a = s.loc[(REF, 400.0)]
    add("PR1", "peak drho/rho 400 km (1e11 W, z0 300)", a.peak_drho_rel, verdict(a.peak_drho_rel, 0.05, 1.0),
        "falsified if <0.05 or >1")
    if LOW in have:
        b = s.loc[(LOW, 400.0)]
        add("PR2", "peak ratio 1e10/1e11 at 400 km", b.peak_drho_rel / a.peak_drho_rel,
            verdict(b.peak_drho_rel / a.peak_drho_rel, 0.05, 0.2))
    else:
        add("PR2", "peak ratio 1e10/1e11 at 400 km", np.nan, "PENDING")
    tp = a.t_peak_after_onset_s / 3600
    add("PR3", "time of 400-km peak after onset [h]", tp, verdict(tp, 0.5, 2.0, 0.25, 3.0))
    neg = -a.min_drho_rel / a.peak_drho_rel
    add("PR4", "|min|/peak drho at 400 km; min O/N2 change", neg,
        "CONFIRMED" if (0 < neg <= 1 / 3 and a.min_dOn2_rel < 0) else ("FALSIFIED" if neg <= 0 or neg > 1 else
                                                                       "OUTSIDE_RANGE_NOT_FALSIFIED"),
        f"min dO/N2 = {a.min_dOn2_rel:.3f}")
    x = ts(REF)
    zr = np.load(f"data/physical/processed/{REF}_slices.npz")
    t_on = float(zr["heating"][6]) - float(zr["t_case0_s"])
    x4 = x[(x.alt_km == 400) & (x.t_s <= t_on + 3 * 3600)]
    rem = float(x4.remote_max_abs_drho_rel.max())
    add("PR5", "max |drho/rho| beyond 3000 km within 3 h of onset, 400 km", rem,
        "CONFIRMED" if rem > 0.01 else ("FALSIFIED" if rem < 0.001 else "OUTSIDE_RANGE_NOT_FALSIFIED"))
    ef = a.efold_peak_after_off_s / 3600
    add("PR6a", "e-folding of local 400-km peak after switch-off [h]", ef, verdict(ef, 1.0, 4.0, 0.5, 8.0))
    eg = a.efold_globalmean_after_off_s / 3600
    add("PR6b", "e-folding of global-mean 400-km drho after switch-off [h]", eg,
        "CONFIRMED" if eg > 3 else "FALSIFIED")
    if Z150 in have:
        c = s.loc[(Z150, 400.0)]
        q = c.peak_drho_rel / a.peak_drho_rel
        add("PR7", "peak 400-km drho ratio z0=150 / z0=300", q, verdict(q, 1 / 3, 3.0))
    else:
        add("PR7", "peak 400-km drho ratio z0=150 / z0=300", np.nan, "PENDING")
    f = ts(FINE)
    if f is not None:
        tmax = f.t_s.max()
        cc = x[(x.alt_km == 400) & (x.t_s <= tmax)]
        ff = f[f.alt_km == 400]
        dpk = ff.max_drho_rel.max() / cc.max_drho_rel.max() - 1
        m = pd.merge(cc[["t_s", "dM_above400_kg"]], ff[["t_s", "dM_above400_kg"]], on="t_s", suffixes=("_c", "_f"))
        m = m[m.dM_above400_kg_c > 0]
        dm = float(np.max(np.abs(m.dM_above400_kg_f / m.dM_above400_kg_c - 1))) if len(m) else np.nan
        add("PR8a", "fine/coarse peak drho at 400 km - 1 (t<=3h)", dpk, verdict(abs(dpk), 0, 0.3, 0, 0.5))
        add("PR8b", "max |fine/coarse mass excess above 400 km - 1|", dm, verdict(dm, 0, 0.2, 0, 0.5))
    else:
        add("PR8", "grid convergence", np.nan, "PENDING")
    t4 = g.loc[(REF, 400.0, "target")]
    n4 = g.loc[(REF, 400.0, "nontarget")]
    fr = t4.gitm_extra_dv_mean / t4.natural_dv_12h_mean
    add("PR9", "target extra dv / natural dv, 400 km, 12 h", fr, verdict(fr, 0.001, 0.03, 0.0001, 0.1))
    for h in (300.0, 400.0, 500.0):
        t, n = g.loc[(REF, h, "target")], g.loc[(REF, h, "nontarget")]
        sg = t.gitm_extra_dv_mean / n.gitm_extra_dv_mean
        sp = t.prescribed_extra_dv_mean / n.prescribed_extra_dv_mean
        add(f"PR10@{int(h)}", "selectivity GITM vs prescribed (prescribed/GITM)", sp / sg,
            "CONFIRMED" if sp / sg >= 3 else ("FALSIFIED" if sg >= sp else "OUTSIDE_RANGE_NOT_FALSIFIED"),
            f"GITM {sg:.3f}, prescribed {sp:.3f}")
        rt = t.gitm_extra_dv_mean / t.prescribed_extra_dv_mean
        add(f"PR11@{int(h)}", "target extra dv GITM / prescribed", rt, verdict(rt, 0.3, 3.0, 0.1, 10.0))
    add("PR12", "peak drho at 400 km for 1e11 W (falsified if >=1)", a.peak_drho_rel,
        "FALSIFIED" if a.peak_drho_rel >= 1 else "CONFIRMED", "δ≥1 reached; see area/duration in G3 summary")
    del n4
    out = pd.DataFrame(r)
    out.to_csv("results/tables/physical_prediction_outcomes.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
