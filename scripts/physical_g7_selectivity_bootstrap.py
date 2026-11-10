"""G7: object-resampling uncertainty of the 12-h selectivity (coarse-grid cases).

Resamples target and non-target objects separately with replacement (fixed seed) from
results/tables/physical_g4_<label>_objects.csv and writes results/tables/physical_selectivity_bootstrap.csv
(percentile 95% interval of S = mean target extra dv / mean non-target extra dv). This measures sampling
uncertainty of the synthetic orbit population only, not model uncertainty.
"""
import os

import numpy as np
import pandas as pd

R = os.path.join(os.path.dirname(__file__), "..")
N_BOOT = 10000
SEED = 20261110


def main():
    rng = np.random.default_rng(SEED)
    rows = []
    for lab in ("p11_z300", "p10_z300", "p11_z150"):
        d = pd.read_csv(os.path.join(R, f"results/tables/physical_g4_{lab}_objects.csv"))
        for h, g in d.groupby("alt_km"):
            t = g[g.target].gitm_extra_dv_ms.to_numpy()
            n = g[~g.target].gitm_extra_dv_ms.to_numpy()
            bt = rng.choice(t, (N_BOOT, t.size)).mean(1)
            bn = rng.choice(n, (N_BOOT, n.size)).mean(1)
            s = bt / bn
            rows.append(dict(label=lab, alt_km=h, n_target=t.size, n_nontarget=n.size, selectivity=t.mean() / n.mean(),
                             ci95_lo=np.percentile(s, 2.5), ci95_hi=np.percentile(s, 97.5), n_boot=N_BOOT, seed=SEED))
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(R, "results/tables/physical_selectivity_bootstrap.csv"), index=False)
    print(out.to_string())


if __name__ == "__main__":
    main()
