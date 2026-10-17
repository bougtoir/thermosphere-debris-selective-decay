# Reproducibility audit — FINAL with execution evidence (Gate 4)

Date: 2026-10-17. Command log: logs/final_qc_commands.log +
logs/make_all.log.

## Executed commands (all actually run, exit codes recorded)

| Command | Cwd | Exit | Duration | Evidence |
|---|---|---|---|---|
| `make all` | repo root | 0 (initial manuscript step failed once, see below) | 39m09s | logs/make_all.log |
| `python3 scripts/build_manuscript.py` | repo root | 0 | ~8s | rebuild after fix |
| `python3 -m pytest tests/ -x -q` | repo root | 0 | 4s | 26/26 pass |
| `python3 -m pytest tests/test_numeric_provenance.py -v` | repo root | 0 | 3.2s | 6/6 pass |
| `make quick` | repo root | 0 | 7.1s | quick_summary.csv regenerated |
| input-perturbation (B×2) | /tmp/perturb_repo | 0 | ~7s | expected-direction deltas |
| `python3 scripts/build_submission_package.py` | repo root | 0 | ~20s | 130-file zip |

## make all — what a full rerun revealed (real finding)

- Phases 1–12 all regenerated from public inputs (NRLMSISE-00 via
  nrlmsise00 package, committed processed data).
- Regenerated CSV diffs are: (a) last-ulp FP noise in phase1
  (~1e-16 relative — BLAS/version noise), (b) bootstrap confidence
  intervals in phase10 Sobol tables (resample-level nondeterminism;
  S1/ST point estimates byte-identical), (c) diagnostic columns in
  sobol_reproduction_check. No substantive value drift.
- One REAL defect surfaced: `phase11_scaling_fit.csv` schema drift —
  the script writes `n_outlier`, the builder read `n_outlier_gt_1p5`,
  so a fresh `make all` aborted at the manuscript step (fail-loud,
  no substitution). Fixed by aligning the builder to the script schema;
  rebuild then succeeded. This is exactly the failure mode the audit
  exists to catch: the committed CSV masked the schema mismatch.

## External dependencies

- `nrlmsise00` Python package (public PyPI) — required for MSIS calls;
  already in requirements.txt. No other network/data fetch needed;
  data/processed/ is committed.
- Monte Carlo and Sobol use seeded sampling but bootstrap CI estimation
  is resample-level nondeterministic between runs — documented, and only
  CI columns (not injected text claims) vary.

## Verdict

Public-input reproduction confirmed end-to-end. The only manuscript
numbers that move under regeneration are Table 6 bootstrap CIs at the
third significant figure — now regenerated and internally consistent.
