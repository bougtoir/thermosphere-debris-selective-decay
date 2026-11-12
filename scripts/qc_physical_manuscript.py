"""G7: mechanical QC of manuscript/physical/* against the Acta Astronautica guide and the traceability rules.

Checks: numbered citations in order of first appearance and 1:1 with the reference list; figures/tables cited and
first cited in numeric order; captions present for every figure; no hard line breaks inside paragraphs; highlights
3-5 items of <= 85 characters; <= 6 keywords; word count <= 13,000 (references and 300 words per display item
included); every number in the body either injected from results/manuscript_physical_values.csv or a declared
design constant. Writes results/qc_physical_manuscript.csv and exits non-zero on any FAIL.
"""
from __future__ import annotations

import os
import re
import sys

import pandas as pd
from docx import Document
from docx.oxml.ns import qn

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
M = os.path.join(ROOT, "manuscript/physical")
DESIGN = {  # experiment-design constants and identifiers stated in Methods/captions, not results
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "14", "20", "30", "36", "45", "50", "70", "72",
    "97", "100", "107", "150", "250", "300", "400", "500", "600", "1000", "2002", "21", "4.1.2", "11.4", "2.5",
    "0.05", "0.2", "0.1", "0.3", "1/3", "2.0", "−2", "2002-03-21", "10.7", "1.5", "1/2", "−1", "−1/2", "−2", "2×2", "9×9",
    "4×4", "8×8", "36×36", "72×72", "100–107", "5–100", "0.05–0.2", "0.1–3", "0.3–3", "1–4", "0.5–2", "1–3",
    "10°×5°", "5°×2.5°", "PR1–PR12", "0.01", "−0.01", "+2", "13,000", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "00", "315", "95", "10°×5", "5°×2.5",
}


def paras(path):
    return [p.text for p in Document(path).paragraphs]


def main():
    rows = []

    def chk(name, ok, detail=""):
        rows.append(dict(check=name, result="PASS" if ok else "FAIL", detail=detail))

    P = paras(os.path.join(M, "manuscript.docx"))
    i_ref = P.index("References")
    i_cap = P.index("Figure captions")
    body, refs, caps = P[:i_ref], [p for p in P[i_ref + 1:i_cap] if p.strip()], P[i_cap + 1:]
    text = "\n".join(body)
    cited = []
    for m in re.finditer(r"\[(\d+(?:[–,]\d+)*)\]", text):
        for part in m.group(1).split(","):
            a, _, b = part.partition("–")
            cited += list(range(int(a), int(b or a) + 1))
    first = list(dict.fromkeys(cited))
    chk("citations numbered in order of first appearance", first == list(range(1, len(first) + 1)), str(first[:30]))
    nref = [int(re.match(r"\[(\d+)\]", r).group(1)) for r in refs]
    chk("reference list numbered 1..N", nref == list(range(1, len(nref) + 1)), f"N={len(nref)}")
    chk("every reference cited and every citation listed", set(first) == set(nref), f"{set(first) ^ set(nref)}")
    chk("no citation in abstract", not re.search(r"\[\d", body[body.index("Abstract") + 1]))
    figs = []
    for m in re.finditer(r"Figs?\. (\d+)(?:[–-](\d+))?", text):
        figs += list(range(int(m.group(1)), int(m.group(2) or m.group(1)) + 1))
    ff = list(dict.fromkeys(figs))
    capn = [int(re.match(r"Fig\. (\d+)\.", c).group(1)) for c in caps if c.startswith("Fig.")]
    chk("figures first cited in order", ff == list(range(1, len(ff) + 1)), str(ff))
    chk("caption for every cited figure and vice versa", sorted(ff) == capn, f"{ff} vs {capn}")
    tabs = list(dict.fromkeys(int(x) for x in re.findall(r"Table (\d+)", text)))
    ntab = len(Document(os.path.join(M, "manuscript.docx")).tables)
    chk("tables first cited in order and all present", tabs == list(range(1, ntab + 1)), f"{tabs}; tables={ntab}")
    for name in ("manuscript.docx", "manuscript_review_inline.docx", "tables.docx", "highlights.docx",
                 "cover_letter.docx"):
        d = Document(os.path.join(M, name))
        hard = sum(p.text.count("\n") + len(p._p.xpath(".//w:br")) for p in d.paragraphs)
        chk(f"no hard line breaks in paragraphs: {name}", hard == 0, str(hard))
    hl = [p.text for p in Document(os.path.join(M, "highlights.docx")).paragraphs if p.style.name == "List Bullet"]
    chk("highlights 3-5 items", 3 <= len(hl) <= 5, str(len(hl)))
    chk("highlights <= 85 characters", all(len(h) <= 85 for h in hl), str([len(h) for h in hl]))
    kw = [p for p in body if p.startswith("Keywords:")][0]
    chk("<= 6 keywords", len(kw.split(":", 1)[1].split(";")) <= 6, kw)
    words = len(" ".join(P[:i_cap]).split()) + 300 * (ntab + len(capn))
    chk("word count <= 13000 (incl. refs, 300 per display item)", words <= 13000, str(words))
    for n in capn:
        chk(f"figure file Fig{n}.tif present", os.path.exists(os.path.join(M, "figures", f"Fig{n}.tif")))
    vals = pd.read_csv(os.path.join(ROOT, "results/manuscript_physical_values.csv"))
    known = set(vals.formatted.astype(str)) | DESIGN
    for x in list(vals.formatted.astype(str)):
        known |= set(re.findall(r"[−+]?\d[\d.,×°/–-]*\d|[−+]?\d", re.sub(r"[\^_]\{([^}]*)\}", r"\1", x)))
    known |= {x.lstrip("+") for x in known}
    unk = []
    scan = "\n".join(body[body.index("Abstract"):]) + "\n" + "\n".join(caps)
    scan = re.sub(r"https?://\S+", "", scan)
    scan = re.sub(r"\[\d+(?:[–,]\d+)*\]", "", scan)
    scan = re.sub(r"(?:Fig|Figs|Table|Section|PR)\.? ?\d+[a-z]?(?:[–-]\d+)?", "", scan)
    for tok in re.findall(r"[−+]?\d[\d.,×°/–-]*\d|[−+]?\d", scan):
        t = tok.rstrip(".,")
        parts = re.split(r"[–]", t) if "–" in t and t not in known else [t]
        for q in parts:
            if q and q not in known and q.rstrip("%") not in known:
                unk.append(q)
    chk("every body number injected or a declared design constant", not unk, " ".join(sorted(set(unk))))
    names = ("manuscript.docx", "manuscript_review_inline.docx", "tables.docx", "highlights.docx", "cover_letter.docx")
    docs = {n: Document(os.path.join(M, n)) for n in names}
    alltext = {}
    for n, d in docs.items():
        cells = [c.text for t in d.tables for r in t.rows for c in r.cells]
        alltext[n] = "\n".join([p.text for p in d.paragraphs] + cells)
    chk("no 'preregistered' terminology (no external registry exists)",
        not any(re.search(r"pre-?regist", t, re.I) for t in alltext.values()))
    chk("cover letter has no prior-journal rejection paragraph",
        not re.search(r"Advances in Space Research|AISR|declined", alltext["cover_letter.docx"]))
    bad_font, bad_col, theme = [], [], []
    for n, d in docs.items():
        for st in ("Normal", "Heading 1", "Heading 2"):
            if st not in [x.name for x in d.styles]:
                continue
            x = d.styles[st]
            rf = x.element.rPr.rFonts if x.element.rPr is not None else None
            if x.font.name != "Times New Roman":
                bad_font.append(f"{n}:{st}")
            if rf is not None and any(rf.get(qn(f"w:{a}")) for a in ("asciiTheme", "hAnsiTheme")):
                theme.append(f"{n}:{st}")
            if x.font.color.rgb not in (None, ) and str(x.font.color.rgb) != "000000":
                bad_col.append(f"{n}:{st}")
        for r in d.element.body.iter(qn("w:color")):
            if r.get(qn("w:val")) not in ("000000", "auto"):
                bad_col.append(f"{n}:run")
    chk("Times New Roman in Normal/Heading styles", not bad_font, " ".join(bad_font))
    chk("no theme-font override in Normal/Heading styles", not theme, " ".join(theme))
    chk("all text black", not bad_col, " ".join(sorted(set(bad_col))))
    md = docs["manuscript.docx"]
    chk("body text 12 pt", md.styles["Normal"].font.size.pt == 12)
    capsz = [r.font.size.pt if r.font.size else None for p in md.paragraphs
             if re.match(r"(Fig|Table) \d+\. ", p.text) for r in p.runs]
    chk("figure and table captions 10 pt", capsz and all(x == 10 for x in capsz), str(sorted(set(capsz))))
    xml = md.element.xml
    chk("displayed equations are editable OMML (>= 2)", xml.count("<m:oMath ") + xml.count("<m:oMath>") >= 2,
        str(xml.count("<m:oMath")))
    chk("no document-grid snapping", "w:docGrid" not in xml)
    chk("no tracked changes or comments", not re.search(r"<w:(ins|del|commentReference)\b", xml))
    ph = re.findall(r"\[[^\]]*to be (?:entered|completed)[^\]]*\]", alltext["manuscript.docx"])
    chk("only author-side placeholder is the affiliation detail", len(ph) <= 1, "; ".join(ph))
    da = body[body.index("Data availability") + 1]
    chk("data statement does not claim processed fields are on GitHub",
        "processed fields" not in da.split("Raw GITM")[0].split("github.com")[0] and
        ("Zenodo" in da or "not yet in a public archive" in da), da[:120])
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(ROOT, "results/qc_physical_manuscript.csv"), index=False)
    print(out.to_string())
    sys.exit(int((out.result == "FAIL").any()))


if __name__ == "__main__":
    main()
