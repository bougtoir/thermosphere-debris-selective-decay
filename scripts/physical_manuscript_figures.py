"""G6: manuscript figures for the GITM study, drawn only from canonical CSV/NPZ outputs.

Writes results/figures/physical/fig{1..5}_*.png (600 dpi) and .tif. Inputs:
data/physical/processed/p11_z300_fine12_slices.npz, results/tables/physical_g4t_selectivity_evolution.csv,
results/tables/physical_g3r_spread_metrics.csv, results/tables/physical_g4t_gaussian_matching.csv,
results/tables/physical_g4t_selectivity_evolution.csv (last common output time).
"""
from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "results/figures/physical")
RUNS = [("p11_z300", "36x36", "coarse 10°×5°", "C0", "-"),
        ("p11_z300_fine12", "72x72", "fine 5°×2.5° (native)", "C3", "--"),
        ("p11_z300_fine12", "remapped_2_36x36", "fine remapped to 10°×5°", "C2", ":")]
MAP_T_H = (50 / 60, 3.0, 6.0, 11.0)


def p(name):
    return os.path.join(ROOT, name)


def save(fig, stem):
    os.makedirs(OUT, exist_ok=True)
    for ext in ("png", "tif"):
        fig.savefig(os.path.join(OUT, f"{stem}.{ext}"), dpi=600, bbox_inches="tight",
                    **({"pil_kwargs": {"compression": "tiff_lzw"}} if ext == "tif" else {}))
    plt.close(fig)


def fig1_maps():
    z = np.load(p("data/physical/processed/p11_z300_fine12_slices.npz"))
    t_on = float(z["heating"][6]) - float(z["t_case0_s"])
    ia = int(np.argmin(np.abs(z["alt_km"] - 400.0)))
    lon, lat, ts = z["lon_deg"], z["lat_deg"], z["t_s"] - t_on
    lon_p = np.where(lon > 180, lon - 360, lon)
    o = np.argsort(lon_p)
    fig, axs = plt.subplots(2, 2, figsize=(7.2, 4.6), sharex=True, sharey=True, constrained_layout=True)
    levels = [-0.05, -0.01, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
    cmap = plt.get_cmap("RdBu_r", len(levels) - 1)
    norm = matplotlib.colors.BoundaryNorm(levels, cmap.N)
    for ax, th in zip(axs.flat, MAP_T_H):
        k = int(np.argmin(np.abs(ts - th * 3600)))
        r = z["p_rho"][k, :, :, ia] / z["c_rho"][k, :, :, ia] - 1.0
        im = ax.pcolormesh(lon_p[o], lat, r[o].T, cmap=cmap, norm=norm, shading="nearest")
        ax.plot(0, 45, marker="+", color="k", ms=8)
        ax.set_title(f"t − t_on = {ts[k] / 3600:.1f} h", fontsize=9)
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
    for ax in axs[1]:
        ax.set_xlabel("Longitude (°)")
    for ax in axs[:, 0]:
        ax.set_ylabel("Latitude (°)")
    fig.colorbar(im, ax=axs, label="Δρ/ρ at 400 km", ticks=levels, shrink=0.9)
    save(fig, "fig1_density_anomaly_maps_400km")


def fig2_selectivity():
    d = pd.read_csv(p("results/tables/physical_g4t_selectivity_evolution.csv"))
    fig, axs = plt.subplots(2, 3, figsize=(7.4, 4.6), sharex=True, constrained_layout=True)
    for j, h in enumerate((300.0, 400.0, 500.0)):
        for lab, g, name, c, ls in RUNS:
            x = d[(d.label == lab) & (d.grid == g) & (d.alt_km == h) & (d.t_after_onset_s > 0)].sort_values("t_after_onset_s")
            t = x.t_after_onset_s / 3600
            axs[0, j].plot(t, x.selectivity_mean, color=c, ls=ls, label=name)
            axs[1, j].plot(t, x.nontarget_share_of_total_extra, color=c, ls=ls)
        axs[0, j].axhline(1, color="0.6", lw=0.6)
        axs[0, j].set_yscale("log")
        axs[0, j].set_title(f"{h:.0f} km", fontsize=9)
        axs[1, j].set_ylim(0, 1)
        axs[1, j].set_xlabel("Time after onset (h)")
    axs[0, 0].set_ylabel("Selectivity S(t)")
    axs[1, 0].set_ylabel("Non-target share of extra Δv")
    axs[0, 0].legend(fontsize=6.5, frameon=False)
    save(fig, "fig3_selectivity_evolution")


def fig3_redistribution():
    d = pd.read_csv(p("results/tables/physical_g3r_spread_metrics.csv"))
    cols = (("int_drho_kg_m", "∫Δρ dA (kg m⁻¹)"), ("participation_area_frac", "Participation area fraction"),
            ("radius_of_gyration_km", "Radius of gyration (km)"))
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.6), constrained_layout=True)
    for ax, (col, lab) in zip(axs, cols):
        for run, g, name, c, ls in RUNS:
            x = d[(d.label == run) & (d.grid == g) & (d.alt_km == 400.0)].sort_values("t_after_onset_s")
            x = x[(x.t_after_onset_s > 0) & (x.t_after_onset_s <= 43200)]
            ax.plot(x.t_after_onset_s / 3600, x[col], color=c, ls=ls, label=name)
        ax.set_ylabel(lab, fontsize=8)
        ax.set_xlabel("Time after onset (h)")
    axs[0].legend(fontsize=6.5, frameon=False)
    save(fig, "fig2_redistribution_400km")


def fig4_comparators():
    g = pd.read_csv(p("results/tables/physical_g4t_gaussian_matching.csv"))
    sets = [("p11_z300", "36x36_tmax43200", "coarse"), ("p11_z300_fine12", "72x72_tmax43200", "fine native"),
            ("p11_z300_fine12", "remapped_2_36x36_tmax43200", "fine remapped")]
    comps = (("gitm", "GITM"), ("peak_matched_fit", "peak-matched Gaussian"),
             ("sigma_scan_1000km_source_centred", "source-centred σ = 1000 km"))
    alts = (300.0, 400.0, 500.0)
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.8), sharey=True, constrained_layout=True)
    w = 0.26
    for ax, (lab, grid, name) in zip(axs, sets):
        x = g[(g.label == lab) & (g.grid == grid)]
        for i, (c, cl) in enumerate(comps):
            vals = []
            for h in alts:
                q = x[(x.alt_km == h) & (x.comparator == ("peak_matched_fit" if c == "gitm" else c))].iloc[0]
                vals.append(q.gitm_selectivity_mean if c == "gitm" else q.selectivity_mean)
            ax.bar(np.arange(3) + (i - 1) * w, vals, w, label=cl, color=("k", "C1", "C4")[i])
        ax.set_xticks(range(3), [f"{h:.0f} km" for h in alts])
        ax.set_yscale("log")
        ax.axhline(1, color="0.6", lw=0.6)
        ax.set_title(name, fontsize=9)
    axs[0].set_ylabel("12-h selectivity")
    axs[0].legend(fontsize=6.5, frameon=False)
    save(fig, "fig4_gitm_vs_static_comparators")


def fig5_power_altitude():
    d = pd.read_csv(p("results/tables/physical_g4t_selectivity_evolution.csv"))
    d = d[d.grid == "36x36"].sort_values("t_after_onset_s").groupby(["label", "alt_km"]).tail(1)
    cases = (("p10_z300", "10 GW, z₀ = 300 km", "C0"), ("p11_z300", "100 GW, z₀ = 300 km", "C3"),
             ("p11_z150", "100 GW, z₀ = 150 km", "C2"))
    fig, ax = plt.subplots(figsize=(3.6, 2.8), constrained_layout=True)
    for lab, name, c in cases:
        x = d[d.label == lab].sort_values("alt_km")
        if x.empty:
            continue
        ax.plot(x.alt_km, x.selectivity_mean, "o-", color=c, label=name)
    ax.axhline(1, color="0.6", lw=0.6)
    ax.set_xlabel("Orbit altitude (km)")
    ax.set_ylabel("12-h selectivity (GITM, coarse)")
    ax.legend(fontsize=6.5, frameon=False)
    save(fig, "fig5_power_altitude_dependence")


def main():
    fig1_maps()
    fig3_redistribution()
    fig2_selectivity()
    fig4_comparators()
    fig5_power_altitude()


if __name__ == "__main__":
    main()
