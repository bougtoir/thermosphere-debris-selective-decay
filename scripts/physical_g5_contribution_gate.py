"""Apply the frozen fine-grid decision rule (docs/SCIENTIFIC_CONTRIBUTION_GATE.md §3) to the generated tables.

Rule (a): GITM selectivity at 400 and 500 km below the peak-fitted static Gaussian and <= 3, and PR8 bounds met.
Rule (c): fine selectivity >= prescribed, or >= 3 at 400 km. Evaluated for the 0-3 h and the 0-12 h windows, for
every fit-ingredient variant of results/tables/physical_g4t_gaussian_decomposition.csv. Thresholds are the frozen
ones; nothing is tuned. Writes results/tables/physical_contribution_gate_checks.csv.
"""
import pandas as pd

D = "results/tables/physical_g4t_gaussian_decomposition.csv"
P = "results/tables/physical_prediction_outcomes.csv"
OUT = "results/tables/physical_contribution_gate_checks.csv"
SEL_MAX = 3.0


def main():
    d = pd.read_csv(D)
    p = pd.read_csv(P).set_index("prediction")
    rows = []
    for (tmax, alt, run), q in d[d.alt_km.isin([400.0, 500.0])].groupby(["tmax_s", "alt_km", "run"]):
        sg = float(q.gitm_selectivity.iloc[0])
        r = q.gitm_over_gaussian
        rows.append(dict(window_h=tmax / 3600, alt_km=alt, run=run, gitm_selectivity=sg,
                         n_variants=len(q), gitm_over_gaussian_min=r.min(), gitm_over_gaussian_max=r.max(),
                         gitm_below_gaussian_all_variants=bool((r < 1).all()),
                         gitm_below_gaussian_own_fit=bool(q[q.variant == "own_fit"].gitm_over_gaussian.iloc[0] < 1),
                         gitm_selectivity_le_3=sg <= SEL_MAX))
    g = pd.DataFrame(rows)
    for w, ids in ((3.0, ("PR8a", "PR8b")), (12.0, ("PR8a_12h", "PR8b_12h"))):
        pr8 = all(i in p.index and p.loc[i, "verdict"] == "CONFIRMED" for i in ids)
        x = g[g.window_h == w]
        a = bool(x.gitm_below_gaussian_all_variants.all() and x.gitm_selectivity_le_3.all() and pr8)
        own = bool(x.gitm_below_gaussian_own_fit.all() and x.gitm_selectivity_le_3.all() and pr8)
        rev = bool((x.gitm_over_gaussian_min >= 1).any() or (x[x.alt_km == 400.0].gitm_selectivity >= SEL_MAX).any())
        rows.append(dict(window_h=w, run="ALL", pr8_confirmed=pr8, rule_a_all_variants=a, rule_a_own_fit=own,
                         rule_c_reversal=rev,
                         verdict_rule=("a: CONDITIONAL GO" if a else ("c: investigate" if rev or not own
                                                                      else "a (own fit only)"))))
    out = pd.concat([g, pd.DataFrame(rows[len(g):])], ignore_index=True)
    out.to_csv(OUT, index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
