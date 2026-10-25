# ASR FINAL numeric hardcode audit (this pass)

Method: reuse of the static provenance map (scripts/build_manuscript.py
injects every number from results/tables/*.csv; missing canonical data
aborts the build) + pytest tests/ (26 pass incl. fail-loud, perturbation-
propagation, stale-literal, and unsubstituted-placeholder tests, newly
executed this pass). AST inspection of build/analysis scripts: scientific
results are never typed as immutable constants; the only literals added in
this QC pass are OMML equation *structure* (symbols/fractions), not values
— every number inside/around the equations still comes from the n[...]
injection (e.g. Π = … = n['pi_mean'] ± n['pi_std']).

No fallback-to-fabricated-number logic anywhere (verified HARDCODE_AUDIT.md
+ new sweep of build_manuscript.py diff: only formatting/table-numbering
code added). Scientific values unchanged: spot-check of 47 frozen literals
in the regenerated docx (6.87, 3.53, 3.98e-3, 1726, 887, 41%, 11/27,
1.06±0.26, 1.016/0.9984, 7/480, 0.06%, 5.8e7, …) all match canonical CSVs.

Unresolved: none. results/ASR_FINAL_NUMERIC_CLAIM_MAP.csv (90 rows).
