# Post-merge and tag record (final submission state)

Recorded 2026-11-19 (UTC) after the author authorized merging PR #9 and creating tag `gitm-orbit-selectivity-v1.1`.
This file is added after the tag, so it is not part of the tagged tree.

## Merge

| Item | Value |
|---|---|
| PR | #9, base `main`, head `devin/1794047620-physical-model-rebuild` |
| Validated head before merge | `95e531963e842be39b66a23511751b5f2703f552` (44 commits ahead of `main`, 0 behind, no conflict) |
| Merge method | merge commit (not squash or rebase), guarded by head SHA |
| Merge commit | `d6817a18682cb7a58a7325cd6c15d13e4df7444e`, parents `ac67802a0965661bb172285bc120b5ad5fe2a9bb` and `95e531963e842be39b66a23511751b5f2703f552` |
| Tree | identical to `95e5319` |
| Ancestry | frozen-prediction commit `c93bf8c` and tag `gitm-orbit-selectivity-v1` target `61478a1` are reachable from `main` |
| Other open PRs | none |
| Branch protection / rulesets | `protected: false`; rulesets `[]` |

## Checks at merge time

The only reported status on `95e5319` was the commit-status context `Devin Review`: state `failure`, description "Completed analysis in 5s", no check-run, no review comments, no log.
The cause is unexplained. It was not a required check. It is not a successful review and must not be reported as one.

## Tags

| Tag | Tag object | Target commit | Role |
|---|---|---|---|
| `gitm-orbit-selectivity-v1` | `9040e4e26fefea1f3cc32e265bc42f5712857d33` | `61478a11ab39b29c1abc33931149f5ec1bf2c65f` | initial public reproducibility release (unchanged, not moved) |
| `gitm-orbit-selectivity-v1.1` | `c58f0476e8c8d50ea55af55fc94116bfa0c3092f` | `d6817a18682cb7a58a7325cd6c15d13e4df7444e` | final submission state |

Both tags resolve to these commits through unauthenticated `git ls-remote` on `https://github.com/bougtoir/thermosphere-debris-selective-decay.git`, and both release-tag pages return HTTP 200.

v1 to v1.1 differs only in the prior-literature wording of the manuscript and cover letter, plus audit documents. Scientific numerical results, figures, tables and data manifests are unchanged.

## Zenodo

No new record, version or DOI was created. The processed data remain record 24101202, DOI 10.5281/zenodo.24101202. The manuscript on `main` cites `https://doi.org/10.5281/zenodo.24101202`.

## Reconstruction from v1.1

- Fresh unauthenticated clone at `gitm-orbit-selectivity-v1.1` (`d6817a1`).
- The five processed NPZ files previously downloaded without login from Zenodo record 24101202 were used. All five SHA-256 values match `data/physical/PROCESSED_MANIFEST.csv`.
- Python environment: the clean reproduction venv (NumPy 2.2.6, pandas 2.3.3, Matplotlib 3.10.9, PyYAML 6.0.2).
- Commands: `make physical-qc PY=python` (bootstrap, figures, manuscript, QC), `scripts/acta_semantic_checks.py`, `pytest -q`. All exited 0.
- Results:
  - manuscript QC 34/34 PASS;
  - semantic checks PASS;
  - pytest 34 passed;
  - `results/manuscript_physical_values.csv` and `results/qc_physical_manuscript.csv` byte-identical;
  - figure TIFFs byte-identical;
  - manuscript, review manuscript, cover letter, highlights and tables DOCX text-identical;
  - `figures.pptx` content-identical. The DOCX/PPTX files differ only in package metadata.
- GITM was not rerun. The raw GITM simulations were not independently reproduced.

## Remaining author-only actions

- Department, postal address and ORCID.
- Final reading of the manuscript and cover letter.
- Manual submission to the journal.
