# JSSE journal fit and fee gate

Target: **Journal of Space Safety Engineering (JSSE)**, Elsevier, on behalf of the International Association for the
Advancement of Space Safety (IAASS). ISSN 2468-8967 (online), 2468-8975 (print).

Evidence was captured from the official ScienceDirect journal pages on 2026-11-23 (UTC) through the session browser
and archived unmodified in `data/raw/journal/jsse/` (text and HTML; URL, UTC time, size and SHA-256 of each file in
`data/raw/journal/jsse/LEDGER.jsonl`; capture script `fetch_jsse_pages.py`). An earlier capture of the guide
(`data/raw/journal/jsse_guide_20261109.txt`) and the Scimago record (`data/raw/journal/scimago_jsse_sid21100871641_20261110.txt`)
are also used.

| Source | URL | Archived file |
|---|---|---|
| Journal home | https://www.sciencedirect.com/journal/journal-of-space-safety-engineering | `journal_home.txt` |
| Aims and scope | https://www.sciencedirect.com/journal/journal-of-space-safety-engineering/about/aims-and-scope | `aims_scope.txt` |
| Guide for authors | https://www.sciencedirect.com/journal/journal-of-space-safety-engineering/publish/guide-for-authors | `guide_for_authors.txt` |
| Open access options | https://www.sciencedirect.com/journal/journal-of-space-safety-engineering/publish/open-access-options | `open_access.txt` |
| Journal insights | https://www.sciencedirect.com/journal/journal-of-space-safety-engineering/about/insights | `insights.txt` |
| Elsevier journal page | https://www.elsevier.com/journals/journal-of-space-safety-engineering/2468-8967 (redirects to the ScienceDirect home) | `elsevier_page.txt` |

## 1. Aims and scope (fit)

Quoted from `aims_scope.txt`: "JSSE provides an authoritative source of information in the field of space safety
design, research and development. It serves applied scientists, engineers, policy makers and safety advocates with a
platform to develop, promote and coordinate the science, technology and practice of space safety. JSSE seeks to
establish channels of communication between industry, academy and government in the field of space safety, and also
covers related environmental issues."

The guide's "Types of Papers" paragraph is generic ("articles on space use, activities and developments in their
industrial, economic, political, legal and social contexts ... scholarly analysis and a forum for the discussion of
ideas and opinions"); it does not define separate article categories with different limits. The submission is
therefore a regular research article. JSSE has published debris-remediation evaluation, debris-environment and drag
de-orbit papers (e.g. McKnight 2016, Lewis 2020, Rhatigan and Lan 2020, Usovik 2023, Svotina 2024, Braun et al. 2020),
which the manuscript cites where they genuinely support a statement (see `docs/JSSE_CITATION_ECOLOGY_AUDIT.md`).

Fit assessment: **adequate**, provided the paper is framed as a space-safety screening question (non-target drag
exposure of an environment-directed remediation concept) and not as an atmospheric-physics novelty claim. Residual
risk: the physics content is heavier than most JSSE papers; an editor may judge it a better match for a geophysics
journal. This is a desk-decision risk, not a compliance issue.

## 2. Manuscript requirements (guide for authors) and how they are met

| Requirement (guide) | Implementation |
|---|---|
| Editable Word file, single column, simple layout, no justification/hyphenation | python-docx, single column, left-aligned, Times New Roman 12 pt |
| Clearly defined, numbered sections (1, 1.1, ...) | Sections 1–5 with numbered subsections |
| Essential title page: names, affiliations with full postal address, corresponding author with e-mail | Title page lines 2–4 (author metadata from the JSSE master prompt; ORCID record checked, see FINAL_HANDOFF) |
| Concise, factual, stand-alone abstract; no references; abbreviations defined | Abstract without citations; GITM defined |
| Keywords | 6 keywords |
| Abbreviations defined in a first-page footnote | "Abbreviations:" paragraph on the first page after the keywords (plain paragraph, not a Word footnote) |
| Highlights (where applicable) | `highlights.docx`, 5 bullets, ≤ 85 characters each (Elsevier convention) |
| Equations numbered consecutively, number in parentheses at right | Native OMML equations (1)–(3) with right-tab numbers |
| Figure captions supplied separately; figures as separate files; TIFF ≥ 300/500/1000 dpi | Captions listed after the references; `figures/Fig1–5.tif` at 600 dpi RGB; editable `figures.pptx` |
| Tables editable, numbered in order of appearance, notes below, no vertical rules or shading | Word tables with horizontal rules only (top, bottom, between rows), no shading, notes below |
| References: numbers in square brackets in order of appearance; list in the guide's style | `[n]` in order of first citation; "A.B. Author, Title, J. Abbrev. vol (year) pages. https://doi.org/..." |
| Journal names abbreviated per the List of Title Word Abbreviations | ISO 4 abbreviations applied in `scripts/build_jsse_manuscript.py` (`ISO4`) |
| Data references encouraged | Zenodo DOI and repository tag given in Data availability (not as a `[dataset]` list entry) |
| Declaration of competing interest (template upload in Editorial Manager) | Statement in manuscript; the Elsevier template must be completed at submission (author action) |
| Declaration of generative AI use | Section before the references |
| CRediT author statement | Present |
| Funding statement | Standard Elsevier "did not receive any specific grant" sentence |
| Peer review | Single-anonymized: author identity on the title page is expected |
| Word / abstract limits | **None stated** in the current guide; internal ceiling 13,000 words kept (current ≈ 8,300 incl. references and 300 per display item) |

## 3. Publication model and fees

Quoted from `open_access.txt`:

* Subscription option: "No open access publication fee."
* Open access option: "An open access publication fee is payable by authors, or their institution or funder."
  "The Article Publishing Charge for this journal is: USD 2930" (excl. taxes; a personalised APC may be offered at submission).
* Green route: "This journal has an embargo period of 12 months for self-archiving."

No submission fee or page charge appears on the captured guide or OA pages (searched for "fee", "charge", "page
charge", "submission fee"). On colour, the guide states that usable colour figures "will appear in color online ...
at no additional charge"; "For color reproduction in print, you will receive information regarding the costs" — i.e.
colour in print is an optional, chargeable choice. Selecting "online only" avoids it.

| Item | Status |
|---|---|
| Mandatory APC on the subscription route | **None** |
| Submission fee | None stated |
| Page charges | None stated |
| Colour | Free online; colour in print optional and charged — choose "online only" |
| Optional gold OA APC | USD 2930 (optional; do not select) |

**Fee gate: PASS — zero mandatory charges if the subscription route and online-only colour are chosen.** The author
must select the subscription option in the publishing agreement (open access would trigger the APC) and "online only"
for colour figures.

## 4. Journal metrics and the Q1 question

* ScienceDirect insights (captured 2026-11-23): CiteScore 3.5; Impact Factor 1.8; submission to acceptance 133 days;
  acceptance rate 51%.
* Scimago (Scopus) 2025: **Q2** in Aerospace Engineering and Q2 in Safety, Risk, Reliability and Quality.
* Clarivate JCR quartile: **not verified** (JCR requires a subscription not available in this session). With JIF 1.8,
  a JCR Q1 ranking is unlikely in the aerospace category.

The JSSE target was pre-selected in the JSSE master prompt, whose verdict criteria (fee route, scope, claims, data,
files) do not include a quartile requirement. The author's standing journal filter (JCR Q1 + no mandatory fee) is
therefore **not demonstrably met on the Q1 criterion**; this is reported as an author decision point, not as a
blocker under the master prompt.
