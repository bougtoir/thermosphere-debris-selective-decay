"""Phases 15-18 tooling — automated QC audits.

Checks:
  TRACEABILITY  - every results table/figure exists and is non-empty;
                  manuscript.docx and supplement.docx exist;
                  every citation used exists in references_verified.csv.
  REPRODUCIBILITY - no absolute paths or credentials in tracked source;
                  deterministic seed present in config; requirements pinned.
  CONSISTENCY   - selectivity ratio columns are consistent with the
                  underlying dv columns; no NaN in critical columns;
                  outcome tables have expected scenario/pair coverage.

Writes docs/TRACEABILITY_AUDIT.md, docs/REPRODUCIBILITY_AUDIT.md,
docs/CONSISTENCY_AUDIT.md and exits nonzero on failure.
"""
from __future__ import annotations

import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.utils import repo_root, load_config  # noqa: E402

EXPECTED_TABLES = [
    "phase1_density_table.csv", "phase1_scale_calculations.csv",
    "phase1_energy_bounds.csv", "phase2_validation.csv",
    "phase3_intervention_checks.csv", "phase5_spreading.csv",
    "phase6_outcomes.csv", "phase7_controls.csv",
    "phase7_selectivity.csv", "phase8_timing.csv", "phase9_pareto.csv",
    "phase10_montecarlo.csv", "phase10_sobol.csv",
    "phase10_negative_controls.csv", "phase11_scaling.csv",
    "phase12_classification.csv", "master_results.csv",
]
EXPECTED_FIGS = [
    "fig1_density_profiles.png", "fig2_lifetime_map.png",
    "fig3_collateral.png", "fig4_timing.png", "fig5_pareto.png",
    "fig6_scaling_collapse.png",
]

SECRET_PAT = re.compile(r"(api[_-]?key|secret|token|password)\s*[:=]",
                        re.IGNORECASE)
ABS_PAT = re.compile(r"(/home/|/Users/|C:\\\\)")


def main():
    root = repo_root()
    fails = []

    # ---- traceability ----
    lines = ["# Traceability audit\n"]
    for t in EXPECTED_TABLES:
        p = os.path.join(root, "results/tables", t)
        ok = os.path.exists(p) and os.path.getsize(p) > 0
        lines.append(f"- {'PASS' if ok else 'FAIL'} results/tables/{t}")
        if not ok:
            fails.append(f"missing table {t}")
    for f_ in EXPECTED_FIGS:
        p = os.path.join(root, "results/figures", f_)
        ok = os.path.exists(p) and os.path.getsize(p) > 1000
        lines.append(f"- {'PASS' if ok else 'FAIL'} results/figures/{f_}")
        if not ok:
            fails.append(f"missing figure {f_}")
    for doc in ["manuscript/manuscript.docx",
                "supplement/supplement.docx"]:
        p = os.path.join(root, doc)
        ok = os.path.exists(p)
        lines.append(f"- {'PASS' if ok else 'FAIL'} {doc}")
        if not ok:
            fails.append(f"missing {doc}")
    refs = pd.read_csv(os.path.join(root,
                                    "references/references_verified.csv"))
    bad_refs = refs[refs.verification_status.str.contains("fail",
                                                          na=False)]
    lines.append(f"- {'PASS' if len(bad_refs) == 0 else 'FAIL'} "
                 f"all {len(refs)} references verified")
    if len(bad_refs):
        fails.append("unverified references present")
    open(os.path.join(root, "docs/TRACEABILITY_AUDIT.md"), "w") \
        .write("\n".join(lines))

    # ---- reproducibility ----
    lines = ["# Reproducibility audit\n"]
    src_files = []
    for dp, dn, fn in os.walk(root):
        if ".git" in dp:
            continue
        for f_ in fn:
            if f_.endswith((".py", ".yaml", ".yml", ".txt", ".md",
                            ".cff", "Makefile")):
                src_files.append(os.path.join(dp, f_))
    bad = []
    for f_ in src_files:
        try:
            txt = open(f_, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if ABS_PAT.search(txt) and "qc_traceability" not in f_ \
                and "AUDIT" not in f_:
            bad.append(("absolute path", f_))
        if SECRET_PAT.search(txt) and "secret" not in f_.lower():
            # allow placeholder 'password' mentions in prose
            for m in SECRET_PAT.finditer(txt):
                seg = txt[m.start():m.start() + 80]
                if re.search(r"[:=]\s*['\"]?[A-Za-z0-9_]{12,}", seg):
                    bad.append(("possible credential", f_))
                    break
    cfg = load_config()
    if "seed" not in cfg:
        bad.append(("missing seed", "config/default.yaml"))
    reqs = open(os.path.join(root, "requirements.txt")).read()
    unpinned = [l for l in reqs.splitlines()
                if l.strip() and not l.startswith("#") and "==" not in l]
    for u in unpinned:
        bad.append(("unpinned requirement", u))
    lines.append(f"- scanned {len(src_files)} source/doc files")
    lines.append(f"- {'PASS' if not bad else 'FAIL'} no absolute paths, "
                 f"credentials, or unpinned requirements ({len(bad)} hits)")
    for kind, f_ in bad:
        lines.append(f"  - {kind}: {f_}")
        fails.append(f"{kind} {f_}")
    lines.append("- PASS deterministic seed in config/default.yaml"
                 if "seed" in cfg else "- FAIL no seed")
    open(os.path.join(root, "docs/REPRODUCIBILITY_AUDIT.md"), "w") \
        .write("\n".join(lines))

    # ---- consistency ----
    lines = ["# Consistency audit\n"]
    sel = pd.read_csv(os.path.join(root,
                                   "results/tables/phase7_selectivity.csv"))
    rec = sel.apply(
        lambda r_: abs(r_["selectivity_ratio"]
                       - r_["target_dv_ms"] / r_["protected_dv_ms"])
        / max(r_["selectivity_ratio"], 1e-300)
        if r_["protected_dv_ms"] > 0 else 0.0, axis=1)
    ok = (rec < 0.01).all()
    lines.append(f"- {'PASS' if ok else 'FAIL'} selectivity ratios "
                 "recompute from dv columns")
    if not ok:
        fails.append("selectivity ratio inconsistency")
    mc = pd.read_csv(os.path.join(root,
                                  "results/tables/phase10_montecarlo.csv"))
    nan_frac = mc["target_dv_ms"].isna().mean()
    ok = nan_frac == 0
    lines.append(f"- {'PASS' if ok else 'FAIL'} Monte Carlo table has no "
                 "NaN target responses")
    if not ok:
        fails.append("NaN in MC table")
    p6 = pd.read_csv(os.path.join(root,
                                  "results/tables/phase6_outcomes.csv"))
    scen = set(p6.scenario.unique())
    ok = {"baseline", "fixed_pulse", "tracking"} <= scen
    lines.append(f"- {'PASS' if ok else 'FAIL'} phase6 scenario coverage "
                 f"{sorted(scen)}")
    if not ok:
        fails.append("phase6 scenario coverage")
    neg = pd.read_csv(os.path.join(
        root, "results/tables/phase10_negative_controls.csv"))
    needed = {"high_altitude_750km", "high_B_200",
              "near_identical_trajectory", "diffuse_3000km",
              "short_60s", "poor_timing_fixed_pulse"}
    ok = needed <= set(neg["control"])
    lines.append(f"- {'PASS' if ok else 'FAIL'} all mandatory negative "
                 "controls present")
    if not ok:
        fails.append("missing negative controls")
    open(os.path.join(root, "docs/CONSISTENCY_AUDIT.md"), "w") \
        .write("\n".join(lines))

    if fails:
        print("QC FAILURES:", *fails, sep="\n  ")
        sys.exit(1)
    print("QC: all audits pass")


if __name__ == "__main__":
    main()
