# Scientific Semantic Delta Report — AISR-S-26-05628 original vs editorially corrected

## Verdict: PASS (after one minimal repair)

Method: OOXML element-level extraction (paragraphs, table cells, OMML, media hashes), citation normalization via results/ASR_REFERENCE_MAPPING.csv (old_id → author_year_label), then ordered diff. Full row list: results/scientific_semantic_delta.csv.

## Differences found
- ~14 difference groups total: 9 AUTHORIZED_EDITORIAL, 2 METADATA_EXCEPTION, 2 SEMANTICALLY_EQUIVALENT, 1 SCIENTIFIC_CHANGE (fixed).
- SCIENTIFIC_CHANGE (the only one): the original's data-availability sentence asserted code/datasets/scripts at https://github.com/bougtoir/thermosphere-debris-selective-decay; the corrected "Data availability" paragraph dropped the URL when the Statements block was removed. Fixed in scripts/build_manuscript.py (URL restored); regenerated and re-verified.
- Scientific prose (title, abstract, methods, results, discussion, limitations, conclusions): 0 content diffs after authorized normalization. All numeric claims identical; tables 8/8 + 9/9 zero cell diffs; 12 OMML equations identical multiset/structure (glyph -→−, '→′ only); 8/8 main + 4/4 supplement figures byte-identical SHA256.
- METADATA_EXCEPTION: author name/affiliation placeholders — authorized (author completes locally); not restored.
- Declarations removed from manuscript per editor instruction — authorized disposition (kept in docs/DECLARATIONS.md).
