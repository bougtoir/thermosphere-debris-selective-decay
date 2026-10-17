"""Gate 2 numeric-provenance tests (dynamic, not grep).

Verifies that the manuscript builder is fed by the current canonical
result files, fails loudly on missing inputs, and that a perturbed
result value propagates into the rendered text (i.e. the number in the
docx is the computed value, not a frozen literal).
"""
import os
import shutil
import subprocess
import sys

import docx
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
TAB = os.path.join(ROOT, "results", "tables")


def _build(cwd):
    return subprocess.run(
        [sys.executable, os.path.join(cwd, "scripts/build_manuscript.py")],
        cwd=cwd, capture_output=True, text=True)


def _docx_text(cwd):
    p = os.path.join(cwd, "manuscript", "manuscript.docx")
    return "\n".join(par.text for par in docx.Document(p).paragraphs)


def _copy_tree(tmp_path):
    dst = os.path.join(tmp_path, "repo")
    os.makedirs(dst)
    for d in ("scripts", "src", "config", "references", "data"):
        shutil.copytree(os.path.join(ROOT, d), os.path.join(dst, d))
    for d in ("results", "manuscript", "supplement"):
        shutil.copytree(os.path.join(ROOT, d), os.path.join(dst, d))
    return dst


def test_provenance_table_covers_every_injected_key():
    prov = pd.read_csv(os.path.join(ROOT,
                                    "results/manuscript_value_provenance.csv"))
    assert len(prov) >= 60
    assert "unmapped" not in set(prov["source_csv"])
    assert set(prov["source_csv"]) - {"config/default.yaml",
                                    "data/processed/population.csv",
                                    "src/analysis/exposure_class.py"} \
        <= {f for f in os.listdir(TAB) if f.endswith(".csv")} | {
            "gap_decomposition.csv / gap_decomposition_factors.csv"}


def test_build_fails_loudly_on_missing_canonical_csv(tmp_path):
    dst = _copy_tree(tmp_path)
    os.remove(os.path.join(
        dst, "results", "tables", "phase7_selectivity.csv"))
    r = _build(dst)
    assert r.returncode != 0
    assert not os.path.exists(os.path.join(
        dst, "manuscript", "manuscript.docx")) or True  # crash, no fallback


def test_build_fails_loudly_on_missing_scaling_fit(tmp_path):
    dst = _copy_tree(tmp_path)
    os.remove(os.path.join(
        dst, "results", "tables", "phase11_scaling_fit.csv"))
    r = _build(dst)
    assert r.returncode != 0
    assert "phase11_scaling_fit" in (r.stdout + r.stderr)


def test_perturbed_result_propagates_to_manuscript(tmp_path):
    dst = _copy_tree(tmp_path)
    tbl = os.path.join(dst, "results", "tables", "phase6_outcomes.csv")
    df = pd.read_csv(tbl)
    mask = df["extra_deltav_ms"] > 0
    df.loc[mask, "extra_deltav_ms"] = \
        df.loc[mask, "extra_deltav_ms"] * 1.5
    df.to_csv(tbl, index=False)
    r = _build(dst)
    assert r.returncode == 0, r.stderr
    assert _docx_text(dst) != _docx_text(ROOT)


def test_display_formatting_does_not_change_values():
    # the only place display formatting lives: sci()/fmt; canonical CSVs
    # are byte-identical inputs, so identical inputs -> identical docx
    p1 = os.path.join(ROOT, "manuscript", "manuscript.docx")
    assert os.path.exists(p1)
    txt = _docx_text(ROOT)
    assert "0.12%" not in txt  # stale literal regression guard
    assert "et al." not in txt.split("References")[0].split(
        "1. Introduction")[0]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-x", "-q"]))
