"""Assemble the journal submission package (submission/ + zip).

Collects the manuscript (journal version with figures as separate files,
plus an inline-figure reading copy), the editable English slide deck, the
supplement, standalone figure files, tables, verified references and the
submission documentation, then writes a manifest with SHA-256 checksums
and a single zip archive.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import sys
import zipfile
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.utils import repo_root  # noqa: E402

ITEMS = [
    ("manuscript/manuscript.docx", "01_manuscript/manuscript.docx"),
    ("manuscript/manuscript_inline.docx",
     "01_manuscript/manuscript_inline_figures.docx"),
    ("manuscript/manuscript_figures.pptx",
     "01_manuscript/manuscript_figures_editable.pptx"),
    ("supplement/supplement.docx", "02_supplement/supplement.docx"),
    ("docs/COVER_LETTER.md", "03_submission_docs/COVER_LETTER.md"),
    ("docs/HIGHLIGHTS.md", "03_submission_docs/HIGHLIGHTS.md"),
    ("docs/SUBMISSION_CHECKLIST.md",
     "03_submission_docs/SUBMISSION_CHECKLIST.md"),
    ("docs/JOURNAL_AUDIT.md", "03_submission_docs/JOURNAL_AUDIT.md"),
    ("docs/ADVERSARIAL_REVIEW.md",
     "03_submission_docs/ADVERSARIAL_REVIEW.md"),
    ("docs/REVIEWER_RISK.md", "03_submission_docs/REVIEWER_RISK.md"),
    ("docs/DECISION_LOG.md", "03_submission_docs/DECISION_LOG.md"),
    ("docs/TRACEABILITY_AUDIT.md",
     "03_submission_docs/TRACEABILITY_AUDIT.md"),
    ("docs/REPRODUCIBILITY_AUDIT.md",
     "03_submission_docs/REPRODUCIBILITY_AUDIT.md"),
    ("docs/CONSISTENCY_AUDIT.md",
     "03_submission_docs/CONSISTENCY_AUDIT.md"),
    ("references/references_verified.csv",
     "05_references/references_verified.csv"),
    ("data/processed/DATA_DICTIONARY.md",
     "06_data/DATA_DICTIONARY.md"),
    ("data/processed/cases.csv", "06_data/cases.csv"),
    ("README.md", "README.md"),
    ("CITATION.cff", "CITATION.cff"),
    ("LICENSE", "LICENSE"),
    ("requirements.txt", "07_code/requirements.txt"),
    ("environment.yml", "07_code/environment.yml"),
    ("Makefile", "07_code/Makefile"),
    ("config/default.yaml", "07_code/config/default.yaml"),
]

FIG_DIR = "results/figures"
TAB_DIR = "results/tables"
CODE_DIRS = ["src", "scripts", "tests"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    root = repo_root()
    out = os.path.join(root, "submission")
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)

    pairs = []
    for src, dst in ITEMS:
        sp = os.path.join(root, src)
        if not os.path.exists(sp):
            print(f"WARNING: missing {src}")
            continue
        pairs.append((sp, dst))

    for fn in sorted(os.listdir(os.path.join(root, FIG_DIR))):
        if fn.endswith(".png") and not fn.startswith("quick_"):
            pairs.append((os.path.join(root, FIG_DIR, fn),
                          f"04_figures/{fn}"))
    for fn in sorted(os.listdir(os.path.join(root, TAB_DIR))):
        if fn.endswith(".csv"):
            pairs.append((os.path.join(root, TAB_DIR, fn),
                          f"06_data/tables/{fn}"))
    for d in CODE_DIRS:
        for dirpath, _, files in os.walk(os.path.join(root, d)):
            if "__pycache__" in dirpath:
                continue
            for fn in files:
                if fn.endswith((".py", ".yaml", ".md")):
                    sp = os.path.join(dirpath, fn)
                    rel = os.path.relpath(sp, root)
                    pairs.append((sp, f"07_code/{rel}"))

    for sp, dst in pairs:
        dp = os.path.join(out, dst)
        os.makedirs(os.path.dirname(dp), exist_ok=True)
        shutil.copy2(sp, dp)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# Submission package manifest",
        "",
        f"Generated (UTC): {stamp}",
        "Repository: https://github.com/bougtoir/"
        "thermosphere-debris-selective-decay",
        "",
        "Contents:",
        "",
        "- `01_manuscript/manuscript.docx` — journal version; figures are "
        "supplied as separate files (placeholders + caption list in text).",
        "- `01_manuscript/manuscript_inline_figures.docx` — same text with "
        "all figures and tables placed inline for reading/review.",
        "- `01_manuscript/manuscript_figures_editable.pptx` — editable "
        "English slide deck of all figures and key results.",
        "- `02_supplement/` — supplementary figures and tables.",
        "- `03_submission_docs/` — cover letter, highlights, checklist, "
        "journal audit, adversarial review, QC audits.",
        "- `04_figures/` — standalone figure files (PNG, 200 dpi).",
        "- `05_references/` — verified reference list with DOIs.",
        "- `06_data/` — data dictionary, case definitions, all result "
        "tables (CSV).",
        "- `07_code/` — full analysis code, config and environment files; "
        "`make all` regenerates every number, figure and table.",
        "",
        "All quantitative statements in the manuscript are written from "
        "the CSVs in `06_data/tables/` by `07_code/scripts/"
        "build_manuscript.py`; no scientific number is hard-coded.",
        "",
        "## Checksums (SHA-256)",
        "",
        "| file | bytes | sha256 |",
        "| --- | --- | --- |",
    ]
    for _, dst in sorted(pairs, key=lambda p: p[1]):
        dp = os.path.join(out, dst)
        lines.append(f"| {dst} | {os.path.getsize(dp)} | {sha256(dp)} |")
    with open(os.path.join(out, "MANIFEST.md"), "w") as f:
        f.write("\n".join(lines) + "\n")

    zip_path = os.path.join(
        root, "submission/thermosphere-debris-selective-decay_"
              "submission.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, files in os.walk(out):
            for fn in files:
                sp = os.path.join(dirpath, fn)
                if os.path.abspath(sp) == os.path.abspath(zip_path):
                    continue
                z.write(sp, os.path.relpath(sp, out))
    print(f"submission package: {len(pairs) + 1} files -> {zip_path} "
          f"({os.path.getsize(zip_path) / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
