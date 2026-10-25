# Evidence inventory (Phase 1-2)

Date: 2026-10-17. Machine-readable copy: results/evidence_inventory.csv.

## Classification summary

All 19 required audit artifacts: **FOUND_CURRENT** in the canonical
working tree (commit a28aed3 and ancestors 0ece949/ef02a98) and
**MISSING_FROM_ZIP** in ASR_SUBMISSION_EVIDENCE_VERIFIED.zip.

## Root cause of repeated zip exclusion

`scripts/build_submission_package.py` uses an explicit `ITEMS`
allowlist of doc paths under `03_submission_docs/`. Every audit file
produced by the three review/lock passes lived outside that list
(`docs/*.md` not enumerated, plus root `FINAL_HANDOFF.txt`, `logs/`,
`results/*audit*.csv`). The builder never failed because files it
doesn't know about are silently skipped — there is no
completeness check on audit evidence.

Fix applied: added every required artifact to `ITEMS` under
`08_audit_evidence/` (docs + CSVs + logs + FINAL_HANDOFF.txt), so a
missing audit file now aborts the package build loudly.

## Execution-evidence truth check

- Hostile review: 3 written sweeps exist (INDEPENDENT, FINAL); newest
  documents defects actually found ({len(p11)}, schema drift) —
  genuine, not repackaged.
- Static hardcode audit: AST scan logged (zero fallback literals,
  49 digit strings all headings/captions).
- Dynamic provenance: pytest 6/6 PASS, exit=0 in
  logs/final_qc_commands.log; input-perturbation Bx2 halved drag.
- make all: 39m09s, logs/make_all.log, phases 1-12 regenerated.
- Render: 3 docx rendered to PDF and inspected (14/20/34 pp).
