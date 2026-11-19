# PR merge-target audit

Checked 2026-11-19T01:17Z with the GitHub REST API (`repos`, `pulls`, `branches`, `rulesets`, `git/refs`, `git/tags`,
`commits/{sha}/status`, `check-runs`) and local git after `git fetch origin`.

## Verdict: **CONDITIONAL MERGE** — merge PR #9 alone into `main`

The merge sequence is verified and there is no merge conflict or dependency. The remaining issue is operational: the
"Devin Review" commit status reports `failure` with no findings and no log. It is not a required check (no branch
protection, no rulesets), so it does not block the merge mechanically, but its cause is unknown.

## Repository state

| Item | Value |
|---|---|
| Default branch | `main` (public repository) |
| `main` HEAD | `ac67802a0965661bb172285bc120b5ad5fe2a9bb` (= immutable scientific baseline) |
| Feature branch | `devin/1794047620-physical-model-rebuild`; HEAD before this audit `61478a11ab39b29c1abc33931149f5ec1bf2c65f`, plus the commit that adds this file (see `FINAL_HANDOFF.txt`) |
| Release tag | `gitm-orbit-selectivity-v1`, **annotated** (tag object `9040e4e2…`, tagger 2026-11-18T09:27:41Z) → commit `61478a11…` |
| Branch protection on `main` | `protected: false` (`GET /branches/main`); `GET /rulesets` → `[]`. (`GET /branches/main/protection` returns 403 to the integration token; `protected: false` is the authoritative flag.) |
| Merge methods allowed | merge commit, squash, rebase |

## PR inventory

| PR | Title (short) | State | Base ← head | Head SHA | In `main`? |
|---|---|---|---|---|---|
| **#9** | Physical-model rebuild (GITM, G0–G7) … Acta Astronautica manuscript | **open** | `main` ← `devin/1794047620-physical-model-rebuild` (same repository) | `61478a11` → new head after this commit | no (the PR to merge) |
| #8 | ASR editorial technical correction | merged 2026-11-05 | `main` | `a5bd28d7` | yes |
| #7 | Cover letter: single-author wording | merged 2026-11-02 | `devin/1790845369-reentry-flag-reset` | `9e30129f` | yes |
| #6 | ASR format/citation QC | merged 2026-10-25 | `devin/1790845369-reentry-flag-reset` | `8eb35e83` | yes |
| #5 | Hostile-review + hardcode-audit revision | merged 2026-10-25 | `devin/1790845369-reentry-flag-reset` | `b0376644` | yes |
| #4 | Reentry-altitude clamp fix | merged 2026-10-25 | `main` | `4c289833` | yes |
| #3, #2, #1 | earlier ASR revisions | merged 2026-09 | `main` | `bbd0e610`, `d09083ff`, `340c6bdd` | yes |

There is one open PR. All head SHAs of PRs #1–#8 are ancestors of `main`. The stale branch
`devin/1790845369-reentry-flag-reset` (HEAD `88aa0530`, the merge commit of #7) is not an ancestor of `main`, but its tree
has no content difference from `main` (`git diff origin/main...88aa0530` is empty); it has no open PR and needs no action.

**Dependency graph:** `main@ac67802` ← #9 (43 commits before this audit, 0 behind). No stack, no parent PR, no child PR.

## Recommended merge sequence

1. Merge **PR #9** into **`main`** (a merge commit keeps the commit referenced by tag `gitm-orbit-selectivity-v1` and the
   prediction-freeze commit `c93bf8c` reachable from `main`; squash or rebase would leave `main` without those SHAs).

No other PR needs to be merged before or after.

## Mergeability

`mergeable: true`, `mergeable_state: unstable` (= mergeable, but a non-required status is failing). PR #9 is
0 commits behind `main`, so the merge is conflict-free.

## Devin Review status

| Question | Finding |
|---|---|
| Required by branch protection? | No (no protection, no rulesets) |
| Associated commit | Reported as commit status context `Devin Review`, state `failure`, description "Completed analysis in 3s", on `61478a1`; the same status appeared on earlier heads. No check-run, no review comments, no inline comments, no job log available to the token |
| Can it be rerun? | No rerun API is available to Devin; each new push starts a new run (the push of this audit does) |
| Scientific/code defect? | Not determinable. A 3-second analysis of a 340-file PR with zero findings suggests a service-side failure (for example PR size or binary content), but this is an inference, not evidence |
| Other required checks | None configured (the repository has no CI workflows) |

Effect: the failure does not prevent merging, but no automated review of PR #9 exists. Its result on the new head is
recorded in `FINAL_HANDOFF.txt`.

## Release tag

- `gitm-orbit-selectivity-v1` → `61478a1`, annotated; message cites doi:10.5281/zenodo.24101202. Not moved or deleted.
- The tag contains the final data references (manuscript Data availability with the published DOI, README, manifests).
- The tag **predates** the 2026-11-19 literature-wording correction (`docs/FINAL_PRIOR_LITERATURE_CLAIM_DELTA.md`). Between
  the tag and the final head only prose strings in `scripts/build_physical_manuscript.py`, the three regenerated DOCX, the QC
  word count and documentation differ (plus the legacy `quick_summary.csv` restore); the analysis and figure code
  (`scripts/physical_*.py`, `physical/`), the processed-data manifests and the value ledger are identical. The tag therefore remains a valid
  reproducibility reference for the scientific outputs; regenerating the DOCX at the tag gives the pre-correction prose.
- The Zenodo record does not cite the tag: its related identifier is the repository URL (`isSupplementTo`), and its code
  snapshot is `git archive 8aa5205`.
- A new tag (for example `gitm-orbit-selectivity-v1.1` on the final head) is optional. It is needed only if the author wants
  the cited tag to regenerate the corrected prose; creating it and citing it in the Data availability requires the author's
  approval. Not done.

## Comparison of PR #9 with `main` (targeted semantic diff)

`git diff --name-status origin/main...HEAD`: 336 files added, 6 modified, **0 deleted**.

| Modified file | Change | Assessment |
|---|---|---|
| `.gitignore` | ignores `data/physical/processed/*.npz` | intended (npz on Zenodo) |
| `Makefile` | adds `physical-figures`, `physical-manuscript`, `physical-qc`; legacy targets unchanged | intended |
| `requirements.txt` | PyYAML 5.4.1 → 6.0.2 | intended (clean-venv install) |
| `README.md` | adds the GITM-study section; legacy text unchanged | intended |
| `FINAL_HANDOFF.txt` | replaced by the physical-study handoff; legacy version preserved byte-identically as `docs/FINAL_HANDOFF_LEGACY_GAUSSIAN.txt` | intended |
| `results/tables/quick_summary.csv` | legacy `make quick` output differed in the last floating-point digit (≈1e-16 relative) | **unrelated; restored to `main`'s version in this commit** |

Present on the branch after merge: GITM hook and patch (`physical/gitm/`), orbit coupling and analysis
(`scripts/physical_g3*`, `physical_g4*`, `physical_g5*`, `physical_g7*`), manuscript pipeline
(`scripts/physical_manuscript_figures.py`, `build_physical_manuscript.py`, `qc_physical_manuscript.py`), final artifacts
(`manuscript/physical/`), Data availability with DOI 10.5281/zenodo.24101202, reproduction instructions (README,
`scripts/public_reproduction_run.sh`), manifests (`data/physical/PROCESSED_MANIFEST.csv`, `GITM_RUN_MANIFEST.csv`,
`run_records/`) and audit reports (`docs/`). The legacy pipeline (`scripts/build_manuscript.py`, `manuscript/*.docx`) is not
modified.

## Blockers

| Type | Status |
|---|---|
| Required-check failure | none (no required checks) |
| Non-required check failure | Devin Review `failure`, cause unknown (above) |
| Merge conflicts | none |
| Missing dependencies | none |
| Tag inconsistency | tag predates the wording correction; documented, not moved |
| Unexpected changes | one (legacy `quick_summary.csv` float noise), reverted |
