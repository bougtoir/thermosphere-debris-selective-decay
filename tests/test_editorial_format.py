"""Regression tests for the ASR editorial technical correction:
unnumbered alphabetical bibliography, author-year in-text citations,
section-order constraint between Conclusions and References, native
Word continuous line numbering, typography and OMML preservation.
"""
import os
import re
import zipfile

import pandas as pd

from src.utils import repo_root


def _doc_xml(name="manuscript/manuscript.docx"):
    p = os.path.join(repo_root(), name)
    assert os.path.exists(p), f"{name} not built"
    return zipfile.ZipFile(p).read("word/document.xml").decode("utf-8")


def _text(x):
    return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", x))


def _reference_block(x):
    """Paragraph texts after the References heading, before Figure
    captions."""
    paras = re.findall(r"<w:p[ >].*?</w:p>", x, re.S)
    texts = ["".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))
             for p in paras]
    i = texts.index("References")
    j = next(k for k in range(i + 1, len(texts))
             if texts[k].startswith("Figure captions"))
    return [t for t in texts[i + 1:j] if t.strip()]


def test_reference_list_unnumbered_alphabetical():
    refs = _reference_block(_doc_xml())
    assert len(refs) == 17
    for r in refs:
        assert not re.match(r"^\s*\d+[.\)]", r), f"numbered entry: {r}"
    keys = [re.split(r"[,(]", r)[0].strip().lower() for r in refs]
    assert keys == sorted(keys), f"not alphabetical: {keys}"


def test_no_numeric_intext_citations():
    t = _text(_doc_xml())
    body = t.split("References")[0]
    assert not re.search(r"\[\s*\d+[\d,;\s\-]*\]", body), \
        "dangling numeric [n] citation remains"


def test_intext_citations_bijective():
    x = _doc_xml()
    t = _text(x)
    refs = _reference_block(x)
    # every listed reference is cited: (FirstSurname ..., Year) in text
    for r in refs:
        surname = r.split(" (")[0].split(",")[0].strip()
        year = re.search(r"\((\d{4})\)", r).group(1)
        assert re.search(re.escape(surname) + r"[^()]*" + year,
                         t.split("References")[0]), \
            f"uncited reference: {r[:60]}"
    # every parenthetical author-year group in body resolves to a ref
    mapping = pd.read_csv(os.path.join(
        repo_root(), "results/ASR_REFERENCE_MAPPING.csv"))
    assert (mapping.in_text_occurrences >= 1).all()
    for _, row in mapping.iterrows():
        label = row.author_year_label
        assert label in t, f"in-text label missing: {label}"
        assert any(row.citation_key and surname_ok(row, r)
                   for r in refs), f"no listed ref for {label}"


def surname_ok(row, ref_line):
    first = ref_line.split(" (")[0].split(",")[0].strip().lower()
    return first in row.author_year_label.lower()


def test_section_order_conclusion_to_references():
    x = _doc_xml()
    heads = re.findall(
        r'w:val="Heading\d".*?<w:t[^>]*>([^<]*)</w:t>', x)
    i = heads.index("6. Conclusions")
    j = heads.index("References")
    allowed = {"Data availability", "Acknowledgements"}
    between = set(heads[i + 1:j])
    assert between <= allowed | {"Appendix"} or \
        all(h.startswith("Appendix") for h in between
            if h not in allowed), f"illegal sections: {between}"


def test_continuous_line_numbering():
    for name in ("manuscript/manuscript.docx",
                 "manuscript/manuscript_inline.docx"):
        x = _doc_xml(name)
        m = re.search(r"<w:lnNumType[^>]*/>", x)
        assert m, f"{name}: no lnNumType"
        tag = m.group(0)
        assert 'w:countBy="1"' in tag
        assert 'w:restart="continuous"' in tag


def test_omml_equations_preserved():
    assert _doc_xml().count("<m:oMath") == 12


def test_no_markdown_residue():
    t = _text(_doc_xml())
    assert not re.search(r"\*[^*]+\*", t)
    assert "`" not in t


def test_typography_normal_12pt_caption_10pt():
    styles = zipfile.ZipFile(
        os.path.join(repo_root(), "manuscript/manuscript.docx")
    ).read("word/styles.xml").decode("utf-8")
    normal = re.search(
        r'w:styleId="Normal".*?</w:style>', styles, re.S).group(0)
    assert "Times New Roman" in normal
    assert '<w:sz w:val="24"' in normal  # 12 pt = 24 half-points
    assert "snapToGrid" not in styles
    x = _doc_xml()
    assert "snapToGrid" not in x
    assert "charLine" not in x
