# Zenodo publication audit — record 24101202

Date: 2026-11-18 (UTC). Checked without authentication through the public REST API and landing page, plus the
authenticated deposition API (owner account) for the metadata correction. Evidence (VM):
`/home/ubuntu/repro_final/zenodo/record_api.json`, `record_api_after_edit.json`, `download_manifest.json`;
`/home/ubuntu/deposit/gitm-selectivity-processed-v1/metadata_edit_20261118/` (before/after metadata, no token).

## Verdict: **PASS** — publicly accessible, files complete and intact

The record was published by the author on 2026-11-12 (record created 2026-11-12T05:12:40Z). No new or duplicate
record was created. On 2026-11-18 the description, publication date and version were corrected through the owner
account (metadata-only edit, revision 4); files, DOI and creators were not changed.

## 1. Checklist

| # | Item | Finding | Status |
|---|---|---|---|
| 1 | Account | Deposition 24101202 is listed under the authenticated owner account (same token as used to create the draft) | PASS |
| 2 | Record | id 24101202, status `published`, DOI 10.5281/zenodo.24101202 | PASS |
| 3 | Title | "Processed GITM fields and analysis code for a coupled GITM–orbit study of orbital-drag selectivity from localized thermospheric heating" | PASS |
| 4 | Creators / affiliation | Onishi, Tatsuki — Shiga University (confirmed by the author 2026-11-12); no ORCID in the record (author item) | PASS |
| 5 | Type | Dataset | PASS |
| 6 | Description | Corrected 2026-11-18: it stated that the npz contain temperature and O/N2 at all model altitudes; they contain mass density and three neutral-wind components at native levels 200–700 km. A dated correction note also records the snapshot file name and the PyYAML pin (§3) | PASS after correction |
| 7 | Licence | CC BY 4.0 (data); code in the snapshot under MIT (`LICENSE`) | PASS |
| 8 | Access | `open`; landing page https://zenodo.org/records/24101202 HTTP 200 without login; https://doi.org/10.5281/zenodo.24101202 → 302 → record | PASS |
| 9 | Version | was empty; set to `1.0` | PASS after correction |
| 10 | Files | 9 files, 439 489 239 bytes in total: 5 npz, `PROCESSED_MANIFEST.csv`, `GITM_RUN_MANIFEST.csv`, `README.md`, `repository_snapshot.zip` | PASS |
| 11 | Sizes | downloaded size = API size for all 9 | PASS |
| 12 | Checksums | downloaded MD5 = Zenodo MD5 for all 9; SHA-256 of the 5 npz = `data/physical/PROCESSED_MANIFEST.csv`; both manifests byte-identical to the repository copies; files unchanged after the metadata edit | PASS |
| 13 | Link to source repository | related identifier `isSupplementTo` https://github.com/bougtoir/thermosphere-debris-selective-decay; snapshot = `git archive 8aa5205` (436 files, 0 differences) | PASS |
| 14 | Relation to the manuscript | The manuscript Data availability cites the DOI; the record cites the repository. No journal name in the record | PASS |
| 15 | Credentials / sensitive material | Snapshot scanned for tokens, keys and password patterns: none. 24 text files contain `/home/ubuntu` paths (VM paths, not personal). E-mail addresses: the author's (also in git history) and journal/editor contact addresses inside saved public journal pages (`data/raw/journal/`) | PASS |

Publication date: the metadata field showed 2026-11-10 (pre-filled when the draft was created); set to
2026-11-12, the day the author published the record.

## 2. Third-party material

- GITM (Apache-2.0) is **not** redistributed. The snapshot contains only the author-written heating hook
  (`physical/gitm/user_perturbation_heating.f90`), the patch script and case definitions; the upstream source is
  referenced by URL and commit `c4fc3150aca274e0e0496ba415696a57d0703e00`.
- Saved journal guide pages and SCImago pages in `data/raw/journal/` are saved public web pages from the journal-selection step; they
  are not part of the scientific data.
- Earlier ASR submission ZIPs of the superseded prescribed-Gaussian study are in the snapshot because they are in the
  repository; they are unrelated to the processed fields and contain no credentials.

## 3. Known limitations of the deposited files (not fixed by a new version)

- The deposited `README.md` predates the description correction (temperature/O/N2 wording; `code/` prefix of the
  snapshot path). The record description carries the correction.
- `requirements.txt` in the snapshot pins PyYAML 5.4.1, which does not build in a clean Python 3.10 venv
  (`cython_sources` error with setuptools/Cython 3). PyYAML is not used by the physical-model scripts; the repository
  (tag `gitm-orbit-selectivity-v1`) pins 6.0.2, with which the clean reproduction passes.

A new Zenodo version (new DOI) was judged unnecessary: the data files are correct, and both points are documented in
the record itself.
