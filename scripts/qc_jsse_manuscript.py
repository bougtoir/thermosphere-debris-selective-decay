"""Mechanical and semantic QC of manuscript/JSSE/* (Journal of Space Safety Engineering submission).

Runs the generic manuscript checks of scripts/qc_physical_manuscript.py on manuscript/JSSE (citation order, figure and
table order, captions, hard breaks, highlights, keywords, injected numbers, fonts, OMML, data statement), then adds
JSSE-specific checks: frozen canonical values unchanged, identical value ledgers for the JSSE and physical
manuscripts, calibrated safety language (exposure is not hazard), synthetic-sample qualifier on the aggregate share,
author metadata, abbreviated journal titles, figure files and resolution, declarations, cover letter voice.
Writes results/qc_jsse_manuscript.csv and exits non-zero on any FAIL.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

import pandas as pd
from docx import Document
from PIL import Image
from pptx import Presentation

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
M = os.path.join(ROOT, "manuscript/JSSE")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from build_jsse_manuscript import AUTHOR, ISO4, REPO_TAG, TITLE  # noqa: E402

# Frozen headline values (handoff; Acta-final state, tag gitm-orbit-selectivity-v1.1): name -> (lo, hi) inclusive.
FROZEN = {
    "S12_p11_z300_36x36_400": (1.45, 1.55), "S12_p11_z300_36x36_500": (1.95, 2.05),
    "S12_p11_z300_36x36_300": (0.9, 1.1), "S12_p11_z300_fine12_72x72_400": (1.45, 1.55),
    "S12_p11_z300_fine12_72x72_500": (1.95, 2.05),
    "nontarget_share_p11_z300_36x36_400": (84, 85), "nontarget_share_p11_z300_fine12_72x72_400": (84, 85),
    "nontarget_share_p11_z300_36x36_500": (77, 77), "nontarget_share_p11_z300_fine12_72x72_500": (77, 77),
    "gauss_over_gitm_min_12.0h_400.0": (1.5, 1.5), "gauss_over_gitm_max_12.0h_400.0": (1.7, 1.7),
    "gauss_over_gitm_min_12.0h_500.0": (2.8, 2.8), "gauss_over_gitm_max_12.0h_500.0": (3.6, 3.6),
    "src1000_over_gitm_min_400.0": (4.7, 4.7), "src1000_over_gitm_max_400.0": (5.8, 5.8),
    "src1000_over_gitm_min_500.0": (8.0, 8.0), "src1000_over_gitm_max_500.0": (8.5, 8.5),
    "S12_fine_vs_coarse_max_diff_400_500_pct": (0, 1.1),
    "peak_drho_p11_z300_400": (204, 204), "peak_drho_p11_z300_500": (983, 983),
    "max_global_mean_drho_p11_z300_400": (11.6, 11.6),
    "target_extra_dv_400": (6.6, 6.6), "target_extra_over_natural_400": (3.7, 3.7),
    "lifetime_base_400_d": (129, 129), "delta_lifetime_target_400_d": (0.01, 0.01),
    "peak400_ratio_10GW_over_100GW": (0.31, 0.31), "peak400_ratio_z150_over_z300": (0.16, 0.16),
}


def text_of(path):
    d = Document(path)
    cells = [c.text for t in d.tables for r in t.rows for c in r.cells]
    return [p.text for p in d.paragraphs] + cells


def main():
    env = dict(os.environ, QC_MANUSCRIPT_DIR=M, QC_OUT=os.path.join(ROOT, "results/qc_jsse_manuscript_generic.csv"),
               QC_VALUES=os.path.join(ROOT, "results/manuscript_jsse_values.csv"))
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts/qc_physical_manuscript.py")], env=env,
                   stdout=subprocess.DEVNULL)
    rows = [dict(r, check="generic: " + r["check"]) for r in
            pd.read_csv(env["QC_OUT"]).fillna("").to_dict("records")]

    def chk(name, ok, detail=""):
        rows.append(dict(check=name, result="PASS" if ok else "FAIL", detail=str(detail)[:300]))

    jv = pd.read_csv(os.path.join(ROOT, "results/manuscript_jsse_values.csv"))
    pv = pd.read_csv(os.path.join(ROOT, "results/manuscript_physical_values.csv"))
    chk("JSSE value ledger identical to physical (Acta-final) value ledger",
        jv[["name", "formatted"]].equals(pv[["name", "formatted"]]), f"{len(jv)} vs {len(pv)} values")
    vals = jv.drop_duplicates("name").set_index("name").formatted.astype(str)
    for k, (lo, hi) in FROZEN.items():
        x = float(vals[k].replace("−", "-").replace("+", ""))
        chk(f"frozen value {k} in [{lo}, {hi}]", lo <= x <= hi, vals[k])

    names = ("manuscript.docx", "manuscript_review_inline.docx", "tables.docx", "highlights.docx", "cover_letter.docx")
    T = {n: text_of(os.path.join(M, n)) for n in names}
    alltext = "\n".join("\n".join(v) for v in T.values())
    P = T["manuscript.docx"]
    body = P[:P.index("References")]
    refs = [p for p in P[P.index("References") + 1:P.index("Figure captions")] if p.strip()]
    bodytext = "\n".join(body)

    bad = re.findall(r"\b(unsafe|catastroph\w*|first[- ]ever|for the first time|novel|unprecedented|"
                     r"proves?|validated deployment|safe to deploy)\b", alltext, re.I)
    chk("no overclaiming / alarm vocabulary", not bad, bad)
    chk("no previous-journal or rejection reference",
        not re.search(r"Acta Astronautica|Advances in Space Research|AA-D-|desk|declin|reject", alltext),
        re.findall(r"Acta Astronautica|Advances in Space Research|AA-D-|declin\w*|reject\w*", alltext))
    sents = re.split(r"(?<=[.;])\s+", "\n".join(body + T["cover_letter.docx"] + T["highlights.docx"]))
    risky = [s for s in sents if re.search(r"collision|conjunction|manoeuvre burden|maneuver burden|operational "
                                           r"(risk|hazard)|mission safety", s, re.I)]
    neg = r"\b(not|no|none|nor|without|requires?|require|cannot|separate)\b"
    unneg = [s for s in risky if not re.search(neg, s, re.I)
             and not re.search(r"collisions among orbiting objects can sustain", s)]
    chk("every collision/conjunction/hazard mention is negated or framed as not assessed", not unneg, unneg)
    share = [s for s in sents if re.search(r"(sharec_|non-targets? (receive|get|account)|of (the )?(total )?extra "
                                           r"(Δv|drag)[^.]*\d+%)", s) and re.search(r"\d+%", s)]
    chk("every aggregate-share percentage is qualified by the synthetic sample",
        all("synthetic" in s for s in share) and len(share) >= 3, [s[:80] for s in share if "synthetic" not in s])
    chk("title is the JSSE title", P[0] == TITLE, P[0])
    tp = "\n".join(P[:4])
    chk("title page: author, affiliation with postal address, e-mail, ORCID",
        all(x in tp for x in (AUTHOR["name"], AUTHOR["affiliation"], AUTHOR["email"], AUTHOR["orcid"])), tp[:200])
    chk("no square-bracket placeholders", not re.search(r"\[(?:[^\]\d–,][^\]]*)\]", alltext.replace("[dataset]", "")),
        re.findall(r"\[(?:[^\]\d–,][^\]]*)\]", alltext)[:5])
    full = [k for k, v in ISO4.items() if k != v]
    unabbr = [r for r in refs for k in full if re.search(rf", {re.escape(k)} \d", r)]
    chk("journal titles abbreviated (ISSN LTWA) in reference list", not unabbr, unabbr[:3])
    heads = [p for p in body if re.match(r"^\d+(\.\d+)?\. ", p)]
    chk("numbered section headings 1-5 present",
        all(any(h.startswith(f"{i}. ") for h in heads) for i in range(1, 6)), heads[:6])
    for h in ("Abstract", "Declaration of competing interest", "Funding", "CRediT authorship contribution statement",
              "Data availability",
              "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process"):
        chk(f"section present: {h}", h in P)
    chk("keywords present (1-6)", any(p.startswith("Keywords:") for p in body))
    da = P[P.index("Data availability") + 1]
    tags = subprocess.run(["git", "-C", ROOT, "tag", "-l", REPO_TAG], capture_output=True, text=True).stdout.split()
    chk("data statement cites the existing public release tag and Zenodo DOI",
        REPO_TAG in da and tags == [REPO_TAG] and "10.5281/zenodo." in da, da[:160])
    cl = "\n".join(T["cover_letter.docx"])
    chk("cover letter single-author voice (no we/our/us)", not re.search(r"\b(we|our|us|We|Our)\b", cl),
        re.findall(r"\b(?:we|our|us|We|Our)\b", cl))
    chk("cover letter addressed to JSSE", "Journal of Space Safety Engineering" in cl)
    nmain = len(Document(os.path.join(M, "manuscript.docx")).inline_shapes)
    ninl = len(Document(os.path.join(M, "manuscript_review_inline.docx")).inline_shapes)
    chk("main manuscript has no embedded figures; inline review copy has all five", nmain == 0 and ninl == 5,
        f"{nmain}/{ninl}")
    prs = Presentation(os.path.join(M, "figures.pptx"))
    pics = [sum(sh.shape_type == 13 for sh in s.shapes) for s in prs.slides]
    chk("editable PPTX: five slides with one figure each", pics == [1] * 5, pics)
    for n in range(1, 6):
        f = os.path.join(M, "figures", f"Fig{n}.tif")
        im = Image.open(f)
        dpi = im.info.get("dpi", (0, 0))
        bg = im.convert("RGB").getpixel((2, 2))
        chk(f"Fig{n}.tif >= 600 dpi, RGB, opaque white corner", min(dpi) >= 599 and im.mode == "RGB" and bg ==
            (255, 255, 255), f"{dpi} {im.mode} {bg}")

    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(ROOT, "results/qc_jsse_manuscript.csv"), index=False)
    print(out.to_string())
    print(f"\n{(out.result == 'PASS').sum()}/{len(out)} PASS")
    sys.exit(int((out.result == "FAIL").any()))


if __name__ == "__main__":
    main()
