"""Phase 13 — master results table, figures, and data dictionary.

Aggregates all phase tables into results/tables/master_results.csv
(long format with a `section` column), generates the main and supplement
figures, and writes data/processed/DATA_DICTIONARY.md.

All numbers come from the results/tables CSVs — nothing is hard-coded.
"""
from __future__ import annotations

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.utils import repo_root  # noqa: E402

FIG = "results/figures"
TAB = "results/tables"


def load(root, name):
    p = os.path.join(root, TAB, name)
    return pd.read_csv(p) if os.path.exists(p) else None


def main():
    root = repo_root()
    os.makedirs(os.path.join(root, FIG), exist_ok=True)

    tables = {
        "phase1_density": load(root, "phase1_density_table.csv"),
        "phase1_scale": load(root, "phase1_scale_calculations.csv"),
        "phase1_energy": load(root, "phase1_energy_bounds.csv"),
        "phase5_spreading": load(root, "phase5_spreading.csv"),
        "phase6_outcomes": load(root, "phase6_outcomes.csv"),
        "phase7_controls": load(root, "phase7_controls.csv"),
        "phase7_selectivity": load(root, "phase7_selectivity.csv"),
        "phase8_timing": load(root, "phase8_timing.csv"),
        "phase9_pareto": load(root, "phase9_pareto.csv"),
        "phase10_mc": load(root, "phase10_montecarlo.csv"),
        "phase10_sobol": load(root, "phase10_sobol.csv"),
        "phase10_negative": load(root, "phase10_negative_controls.csv"),
        "phase11_scaling": load(root, "phase11_scaling.csv"),
        "phase12_classification": load(root, "phase12_classification.csv"),
    }

    # ---- master results (long format) ----
    parts = []
    for sec, df in tables.items():
        if df is None:
            continue
        d = df.copy()
        d.insert(0, "section", sec)
        parts.append(d)
    master = pd.concat(parts, ignore_index=True, sort=False)
    master.to_csv(os.path.join(root, TAB, "master_results.csv"),
                  index=False)

    # ---- Figure 1: density profiles ----
    d = tables["phase1_density"]
    if d is not None:
        fig, ax = plt.subplots(figsize=(5, 4))
        for reg in d["regime"].unique():
            s = d[d.regime == reg]
            ax.semilogy(s["altitude_km"], s["rho_kgm3"], label=reg)
        ax.set_xlabel("Altitude [km]")
        ax.set_ylabel("Mass density [kg/m$^3$]")
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(root, FIG, "fig1_density_profiles.png"),
                    dpi=200)
        plt.close(fig)

    # ---- Figure 2: baseline lifetime map (alt x B, moderate) ----
    s = tables["phase1_scale"]
    if s is not None:
        sm = s[s.regime == "moderate"]
        piv = sm.pivot_table(index="B_kgm2", columns="altitude_km",
                             values="lifetime0_days", aggfunc="first")
        fig, ax = plt.subplots(figsize=(6, 4))
        im = ax.imshow(np.log10(piv.values), aspect="auto", origin="lower",
                       cmap="viridis")
        ax.set_xticks(range(len(piv.columns)), piv.columns)
        ax.set_yticks(range(len(piv.index)), piv.index)
        ax.set_xlabel("Altitude [km]")
        ax.set_ylabel("B [kg/m$^2$]")
        ax.set_title("log$_{10}$ baseline lifetime [days], moderate")
        fig.colorbar(im)
        fig.tight_layout()
        fig.savefig(os.path.join(root, FIG, "fig2_lifetime_map.png"),
                    dpi=200)
        plt.close(fig)

    # ---- Figure 3: selectivity (target vs protected dv) ----
    p7 = tables["phase7_selectivity"]
    if p7 is not None:
        fig, ax = plt.subplots(figsize=(6, 4))
        pairs = p7["pair"].unique()
        x = np.arange(len(pairs))
        w = 0.35
        for i, scen in enumerate(["uniform", "localized_tracking"]):
            ss = p7[p7.scenario == scen].set_index("pair").reindex(pairs)
            ax.bar(x + (i - 0.5) * w, ss["protected_dv_ms"], w,
                   label=f"{scen} (protected)")
        ax.set_yscale("log")
        ax.set_xticks(x, pairs)
        ax.set_ylabel("Protected-object extra $\\Delta v$ [m/s]")
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(root, FIG, "fig3_collateral.png"), dpi=200)
        plt.close(fig)

    # ---- Figure 4: timing sensitivity ----
    p8 = tables["phase8_timing"]
    if p8 is not None:
        fig, ax = plt.subplots(figsize=(6, 4))
        for exp, s in p8[p8.obj_type == "target"].groupby("experiment"):
            ax.plot(s["t_s"] / 3600.0, s["extra_deltav_ms"], "o-",
                    label=exp, markersize=3)
        ax.set_yscale("log")
        ax.set_xlabel("Intervention reference time [h]")
        ax.set_ylabel("Target extra $\\Delta v$ [m/s]")
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(root, FIG, "fig4_timing.png"), dpi=200)
        plt.close(fig)

    # ---- Figure 5: Pareto ----
    p9 = tables["phase9_pareto"]
    if p9 is not None:
        fig, ax = plt.subplots(figsize=(5.5, 4))
        sc = ax.scatter(p9["protected_dv_ms"], p9["target_dv_ms"],
                        c=np.log10(p9["sigma_h_km"]), cmap="plasma", s=30)
        fr = p9[p9.on_pareto_front]
        ax.plot(fr["protected_dv_ms"], fr["target_dv_ms"], "r-",
                lw=1, alpha=0.7, label="Pareto front")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Protected extra $\\Delta v$ [m/s]")
        ax.set_ylabel("Target extra $\\Delta v$ [m/s]")
        fig.colorbar(sc, label="log$_{10}$ $\\sigma_h$ [km]")
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(root, FIG, "fig5_pareto.png"), dpi=200)
        plt.close(fig)

    # ---- Figure 6: scaling collapse ----
    p11 = tables["phase11_scaling"]
    if p11 is not None:
        fig, ax = plt.subplots(figsize=(5, 4))
        for reg, s in p11.groupby("regime"):
            ax.scatter(s["extra_dv_pred"], s["extra_dv_sim"], s=8,
                       label=reg, alpha=0.6)
        lim = [p11["extra_dv_pred"].min(), p11["extra_dv_pred"].max()]
        ax.plot(lim, lim, "k--", lw=1)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Predicted $\\Delta v$ = $\\rho\\delta vT/2B$ [m/s]")
        ax.set_ylabel("Simulated $\\Delta v$ [m/s]")
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(root, FIG, "fig6_scaling_collapse.png"),
                    dpi=200)
        plt.close(fig)

    # ---- Supplement figures ----
    p10n = tables["phase10_negative"]
    if p10n is not None:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.barh(p10n["control"] + ":" + p10n["case"],
                p10n["extra_deltav_ms"].clip(lower=1e-20))
        ax.set_xscale("log")
        ax.set_xlabel("Extra $\\Delta v$ [m/s]")
        fig.tight_layout()
        fig.savefig(os.path.join(root, FIG, "figS1_negative_controls.png"),
                    dpi=200)
        plt.close(fig)

    mc = tables["phase10_mc"]
    sob = tables["phase10_sobol"]
    if mc is not None:
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.hist(np.log10(mc["target_dv_ms"].clip(lower=1e-20)), bins=30)
        ax.set_xlabel("log$_{10}$ target extra $\\Delta v$ [m/s]")
        ax.set_ylabel("count")
        fig.tight_layout()
        fig.savefig(os.path.join(root, FIG, "figS2_mc_hist.png"), dpi=200)
        plt.close(fig)
    if sob is not None:
        fig, ax = plt.subplots(figsize=(6, 4))
        x = np.arange(len(sob))
        ax.bar(x - 0.2, sob["S1"], 0.4, label="S1")
        ax.bar(x + 0.2, sob["ST"], 0.4, label="ST")
        ax.set_xticks(x, sob["param"], rotation=30, ha="right")
        ax.set_ylabel("Sobol index")
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(root, FIG, "figS3_sobol.png"), dpi=200)
        plt.close(fig)

    # ---- data dictionary ----
    dd = ["# Data dictionary\n",
          "Auto-generated column descriptions for results/tables CSVs.\n"]
    desc = {
        "lifetime_d": "simulated decay lifetime, days",
        "delta_lifetime_d": "baseline minus intervention lifetime, days",
        "delta_a_km": "baseline minus intervention final semimajor axis, km",
        "a_drop_km": "start minus final semimajor axis over horizon, km",
        "extra_deltav_ms": "equivalent extra delta-v from the perturbation, m/s",
        "extra_impulse_ms": "integrated extra drag impulse, m/s",
        "encounter_count": "number of contiguous in-patch crossings",
        "selectivity_ratio": "target extra dv / protected extra dv",
        "Pi_benefit": "dv*B/(rho*delta*v^2*T), collapses to 1",
        "E_thermal_min_J": "minimum thermal energy for required heating fraction",
        "heating_fraction": "delta/(1+delta), fraction of patch air heated",
        "tau_diff_s": "sigma_h^2/(2*kappa_h) horizontal diffusion lifetime",
        "tau_adv_s": "sigma_h/u advection flushing time",
    }
    for sec, df in tables.items():
        if df is None:
            continue
        dd.append(f"\n## {sec}\n")
        for c in df.columns:
            dd.append(f"- `{c}`: {desc.get(c, '(phase-specific column)')}")
    with open(os.path.join(root, "data/processed/DATA_DICTIONARY.md"),
              "w") as f:
        f.write("\n".join(dd))

    with open(os.path.join(root, "docs/PHASE_13_HANDOFF.md"), "w") as f:
        f.write("# Phase 13 handoff\n\nMaster results, figures and data "
                "dictionary generated from results/tables CSVs.\n")
    print(f"master_results rows: {len(master)}; figures written.")


if __name__ == "__main__":
    main()
