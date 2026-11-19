# Data availability — final audit

Date: 2026-11-18 (UTC). **Verdict: PASS.** Supersedes `docs/ACTA_DATA_AVAILABILITY_AUDIT.md` (kept as history).

## Statement in the manuscript

> The analysis code, GITM case configurations, the heating hook and the figure- and manuscript-generation scripts are
> publicly available at https://github.com/bougtoir/thermosphere-debris-selective-decay (tag gitm-orbit-selectivity-v1).
> The processed GITM fields required to reproduce the figures, tables and principal numerical results (about 0.4 GB,
> five paired heated/control files with SHA-256 checksums) and a snapshot of the code are archived at Zenodo,
> https://doi.org/10.5281/zenodo.24101202. The GITM run configurations, execution records and file-level SHA-256
> checksums of the raw output are documented in the repository (data/physical/run_records/ and
> data/physical/GITM_RUN_MANIFEST.csv). Reproducing the results from the processed fields does not require GITM;
> regenerating the processed fields requires rerunning GITM. The full raw GITM output (about 54 GB, including failed
> and test runs) is not deposited and is available from the author on reasonable request.

## Checks

| Element | Evidence | Status |
|---|---|---|
| Public code repository | GitHub API HTTP 200 without token; anonymous clone works | PASS |
| Tag `gitm-orbit-selectivity-v1` | pushed with the final commit; resolution checked anonymously (FINAL_HANDOFF) | PASS |
| Processed-data archive | Zenodo 24101202 public, DOI resolves, 9 files intact (`docs/ZENODO_PUBLICATION_AUDIT.md`) | PASS |
| Processed vs full reproduction distinguished | sentences 3–4 of the statement | PASS |
| Raw output status | "not deposited … available on reasonable request"; size from the manifest (53.7 GB = 50.0 GiB); the task brief's "about 51 GB" is not used | PASS |
| Execution records in repository | `data/physical/run_records/` (90 files, SHA-256 manifest); `GITM_RUN_MANIFEST.csv` | PASS |
| No placeholder URL or unpublished DOI | only published DOI and live URLs; manuscript QC 34/34 | PASS |
| Consistency | README (new section), `data/physical/ZENODO_README.md`, Zenodo description, FINAL_HANDOFF give the same split (code on GitHub, processed fields on Zenodo, raw on request). The cover letter does not discuss data | PASS |
| Numbers unchanged | value ledger, figures and table cells unchanged by this revision; manuscript text change = data statement only (+37 words; cover-letter word count 7223 → 7260) | PASS |
| Author metadata | not changed (affiliation placeholder for department/address; ORCID absent) | PASS |
