# Hardcode / single-source-of-truth audit (Gate 2)

Date: 2026-10-17. Base: PR #4 head `d2d2b12` + this revision's edits.

## Method

1. Static scan of `scripts/build_manuscript.py` (AST + literal review): every
   numeric literal in prose was classified as PHYSICAL_CONSTANT /
   CONFIGURATION / CITED_EXTERNAL_VALUE / COMPUTED_RESULT / DISPLAY_FORMAT /
   SUSPICIOUS / UNRESOLVED (results/hardcode_findings.csv, 16 items).
2. Provenance trace: every injected manuscript value maps to a canonical CSV,
   config entry, or code constant via `manuscript_value_provenance.csv` /
   `numeric_claim_traceability.csv` (84 claims). Any unmapped key aborts the
   build (`raise SystemExit`).
3. Dynamic tests (`tests/test_numeric_provenance.py`, 5 tests):
   - removing `phase7_selectivity.csv` -> build exits non-zero (no substitution);
   - removing `phase11_scaling_fit.csv` -> build aborts with an explicit
     "missing canonical result" message;
   - perturbing `phase6_outcomes.csv` x1.5 in a disposable copy -> rendered
     docx text changes (numbers are computed, not frozen);
   - provenance table covers all injected keys, no "unmapped";
   - stale-literal regression guards ("0.12%", "et al." on title block).

## Findings and dispositions

- H01 STALE RESULT: "0.12%" propagator agreement vs current 0.062% -> injected.
- H02 STALE RESULT: "slope 1.01 / R^2 0.9995" vs recomputed 1.016 / 0.9984
  (changed by the PR #4 reentry fix; phase11 previously wrote the fit only to
  a log file) -> new canonical `phase11_scaling_fit.csv`, injected, plus
  median/IQR and outlier count.
- H03/H04/H05/H06 typed literals matching current sources -> injected anyway
  so they cannot silently drift.
- H07 formula text missed the factor of 2 that the code's Pi_benefit carries
  -> corrected.
- H08/H09/H10 cited/derived constants verified -> kept.
- H11 "et al." single-author placeholder -> fixed.
- H12 table/figure numbering not in citation order -> renumbered.
- H13 "small compared with natural drag" false for the 750 km control ->
  reworded.
- No hidden fallback code paths found: `load()` returns None and downstream
  code then fails; there is no default-number substitution anywhere.

## Verdict

Audit complete: every manuscript number is either injected from a current
canonical file or an explicitly justified constant/cited value. Dynamic
perturbation proves the text reflects the current computation.

## Addendum — lock-pass sweep (2026-10-17)

Commands/evidence added this pass:

- Rendered-docx sweep for unsubstituted placeholders:
  `re.findall(r"\{[a-zA-Z_][^}]*\}", docx_text)` -> found `{len(p11)}` in
  both manuscript docx (root cause: non-f-string line inside f-string
  paragraph). Fixed by injecting `n_pi_total`; new test
  `test_no_unsubstituted_placeholders_in_rendered_docx`.
- Full literal sweep of rendered docx incl. tables: all "0.12", "et al",
  "2000-object", "~15%" hits classified as injected values, legitimate
  reference strings, or numeric table data — no residual stale claims.
- finding H17 added to results/hardcode_findings.csv;
  claim C085 added to results/numeric_claim_traceability.csv.

## Addendum 2 — evidence pass AST scan (2026-10-17)

- AST scan of all scripts/*.py + src/**: zero `or <literal>` fallback
  defaults; zero `except: return <literal>` paths.
- AST extraction of every digit-bearing non-f-string passed to
  P/TBL/FIG/H in build_manuscript.py: 49 items, all headings, captions
  or figure filenames — no numeric results in static prose.
- `make all` regeneration surfaced schema drift (n_outlier vs
  n_outlier_gt_1p5): committed CSV had masked it; fixed by aligning the
  builder to the script's emitted schema.
