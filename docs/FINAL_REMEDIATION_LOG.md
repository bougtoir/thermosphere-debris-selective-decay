# Final remediation log (Gate 3, second pass)

Date: 2026-10-17.

## Issues substantiated in this pass and actions

| Issue | Severity | Root cause | Action | Downstream impact |
|-------|----------|------------|--------|-------------------|
| `{len(p11)}` literal placeholder rendered in §3.8 of both manuscript docx | MAJOR (render) | a non-f-string segment inside the f-string paragraph (line ~742) | replaced by injected `n['n_pi_total']` (480, from phase11_scaling_fit.csv); added provenance mapping | regenerated all four artifacts; new regression test `test_no_unsubstituted_placeholders_in_rendered_docx` scans all three docx for `{...}` leftovers |

## Items checked and closed WITHOUT change (independence evidence)

- "2000-object" and "~15%" appearing in rendered docx: verified injected
  (`n['n_pop']`=2000 from population.csv; `n['rho_unc_pct']`≈15 from
  config), not literals. Closed.
- "0.12" substring hits in rendered tables: legitimate data values
  (0.1215, -0.1295, …), not the retired 0.12% claim. Closed.
- "et al." hits: only in reference-list entries (legitimate citation
  style) and substring false positives ("relative", "set al"). Title
  block clean. Closed.
- Density unit path: single g/cm3->kg/m3 conversion at
  msis.py boundary; magnitude tests anchor values. No double-correction.
- Pi formula factor 2 now present and consistent with code.

## No science changed

No analysis was rerun in this pass — the defect was presentational.
All canonical result CSVs preserved byte-for-byte.
