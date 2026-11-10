# Acta final delta — data availability audit (Gate 8)

## Inventory

| Item | Location | Public? | Size | Integrity record |
|---|---|---|---|---|
| Analysis code, GITM case files, heating hook, patch script, Makefile, tests | GitHub `bougtoir/thermosphere-debris-selective-decay` (branch of PR #9) | yes (public repo) | ~10 MB | git |
| Result tables (`results/`, `results/tables/`), value ledger, QC outputs | GitHub | yes | small | git |
| Processed GITM fields, 5 NPZ (paired heated/control slices, 150–500 km) | `data/physical/processed/` (git-ignored); deposition package | **draft only** | 0.40 GB | `data/physical/PROCESSED_MANIFEST.csv` (SHA-256) |
| Raw GITM output, 16 run directories, 23831 files | `/home/ubuntu/models/runs` (session VM) | no | 53.7 GB | `data/physical/GITM_RUN_MANIFEST.csv` (per-file SHA-256) |
| GITM source | upstream GitHub, commit `c4fc3150aca274e0e0496ba415696a57d0703e00` | yes | — | `physical/gitm/` patch + build notes |

The minimum dataset needed to regenerate every figure and every G3/G4 table from the public code is the five NPZ
files (verified in `docs/ACTA_PUBLIC_REPRODUCTION_CHECK.md`, section B). Raw output is needed only to regenerate the
NPZ files. It was not deposited: it is ~54 GB, mostly restart and 3DALL files reproducible from the
public configuration, and includes failed/test runs (2-rank fine-grid CPCP failures, the zero-power `c4_p11_z300`,
1 h replicate, pre-runs) that do not enter any reported result. They remain on the VM, listed with SHA-256.

Raw output by run (GB):

| Run | GB |
|---|---:|
| /home/ubuntu/models/runs/c8x_ctrl | 11.08 |
| /home/ubuntu/models/runs/c8x_p11_z300 | 10.89 |
| /home/ubuntu/models/runs/c8b_p11_z300 | 3.99 |
| /home/ubuntu/models/runs/c8b_ctrl | 3.99 |
| /home/ubuntu/models/runs/c4_p11_z300r | 3.73 |
| /home/ubuntu/models/runs/c4_p10_z300 | 3.73 |
| /home/ubuntu/models/runs/c4_p11_z150 | 3.73 |
| /home/ubuntu/models/runs/c4_p11_z300 | 3.73 |
| /home/ubuntu/models/runs/c4_ctrl | 3.73 |
| /home/ubuntu/models/runs/spin8b | 1.71 |
| /home/ubuntu/models/runs/spin4 | 1.24 |
| /home/ubuntu/models/runs/spin8_np4test | 0.75 |
| /home/ubuntu/models/runs/c4_ctrl_rep | 0.57 |
| /home/ubuntu/models/runs/spin8 | 0.39 |
| /home/ubuntu/models/runs/c8_p11_z300 | 0.20 |
| /home/ubuntu/models/runs/c8_ctrl | 0.20 |

Note: the G6 handoff and an earlier data statement said "~30 GB"; the manifest total is 53.7 GB. The
manuscript now injects the manifest total.

## Zenodo deposition (verified via API 2026-11-10T08:21:21Z)

| Field | Value |
|---|---|
| Deposition ID | 24101202 |
| State | `unsubmitted` (draft, **not published**) |
| Reserved DOI | 10.5281/zenodo.24101202 — `https://doi.org/` returns HTTP 404 (does not resolve yet) |
| Anonymous record page | https://zenodo.org/records/24101202 → HTTP 404 |
| Title | Processed GITM fields and analysis code for a coupled GITM–orbit study of orbital-drag selectivity from localized thermospheric heating |
| Creator | Onishi, Tatsuki (Shiga University) |
| License / access | cc-by-4.0 / open (data CC BY 4.0; code in the snapshot under MIT per its LICENSE) |
| Related identifier | GitHub repository, `isSupplementTo` |
| Files | 9, 413.8 MB |

Processed-file integrity (deposit copy vs manifest SHA-256; Zenodo MD5/size vs local):

| File | Bytes | Manifest SHA-256 | SHA-256 | Zenodo MD5/size |
|---|---:|---|---|---|
| p10_z300_slices.npz | 47635582 | `0e30ab6f7f675ad8…` | match | match |
| p11_z150_slices.npz | 36723640 | `99aa68628c8ae625…` | match | match |
| p11_z300_fine12_slices.npz | 209642932 | `85d999e2c9bf31f7…` | match | match |
| p11_z300_fine_slices.npz | 73926012 | `2727b352eee46ee3…` | match | match |
| p11_z300_slices.npz | 35734353 | `d834d7bd58aa1cf1…` | match | match |

Other deposited files: `PROCESSED_MANIFEST.csv`, `GITM_RUN_MANIFEST.csv`, `README.md` (reproduction steps, license,
exclusions) and `code/repository_snapshot.zip` (`git archive` of the final branch commit; see FINAL_HANDOFF).
Full record JSON: `data/physical/ZENODO_DRAFT_RECORD.json`. The upload script (`zenodo_draft.py`) reads the token
only from the environment.

## Manuscript statement

The Data availability section is generated from `docs/ZENODO_DEPOSIT.json`. With `published: false` it says the
fields "have been uploaded to a Zenodo record with the reserved DOI …, which resolves once the record is published".
It does not claim a public archive. After the author publishes the record, set `published: true` and rebuild
(`make physical-qc`); the sentence then reads "are archived at Zenodo, https://doi.org/10.5281/zenodo.24101202".

## Status

Not complete for submission: the processed fields are not publicly accessible until the author reviews and publishes
the draft. Publishing is irreversible (DOI minted, files frozen) and was left to the author.
