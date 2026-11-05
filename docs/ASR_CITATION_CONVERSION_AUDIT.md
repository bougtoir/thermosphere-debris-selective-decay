# ASR Citation Conversion Audit

- Conversion: Vancouver [n] → Harvard (Author, Year), implemented in the source generator (scripts/build_manuscript.py), not a DOCX patch.
- References: 17 listed, all from references_verified.csv (all DOI-verified or verified institutional/book sources; no invented DOIs/authors/years).
- In-text instances: 24 cited instances in 15 parenthetical groups; 0 dangling numeric [n] citations in body text.
- Bijectivity: every in-text label resolves to exactly one listed reference; every listed reference cited ≥1 time (verified programmatically, tests/test_editorial_format.py).
- No same-author same-year collisions → no a/b disambiguation needed.
- Multi-citation groups sorted alphabetically, separated by "; ".
- Institutional authors: IADC (2021), NRL Space Science Division (2024) render as institutional labels.
- Mapping table: results/ASR_REFERENCE_MAPPING.csv (old_id → label → alphabetical position → DOI/source → status → occurrences).
- Uncited verified source (NOAA SWPC) is absent from the list — bijectivity preserved; no dangling entry.
