# ASR In-Text Citation Style Decision

## Decision: author–year (Harvard), parenthetical "(Surname, Year)"

## Evidence
1. Editorial request (verbatim): "Please remove numbering from the reference list. In Reference List, please do not use numbering and ensure that the reference list is consistent and in alphabetical order."
   → An unnumbered alphabetical list is only citable in-text by author–year.
2. Official style metadata: the CSL style registry maps Advances in Space Research (ISSN 0273-1177) to `elsevier-harvard`, citation-format "author-date" (citation-style-language/styles/dependent/advances-in-space-research.csl, accessed 2026-10-17).
3. ASR Guide for Authors (Elsevier, legacyfileshare JASRGuideforAuthorsDec2016.pdf): "References cited in the text must be listed in the reference list (and vice versa)" — no numbered-style prescription; Elsevier's ASR standard list is Harvard.
4. Recent ASR papers (e.g., Phipps et al. 2012 in the journal itself) use author–year.

## Implementation
- scripts/build_manuscript.py `Cites` now emits "Surname, Year" / "A and B, Year" / "Surname et al., Year" labels, "; "-joined and sorted alphabetically inside each parenthetical group.
- Bracket groups containing a 4-digit year are converted to parentheses at render time; non-citation brackets (exp[...], [Authors], figure placeholders) are untouched.
- Reference list: unnumbered, alphabetical by first-author surname (institutional authors by name), bibliography identity unchanged.
- Audit map: results/ASR_REFERENCE_MAPPING.csv.
