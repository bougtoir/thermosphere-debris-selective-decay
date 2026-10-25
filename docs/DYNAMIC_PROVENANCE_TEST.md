# Dynamic provenance test evidence (Gate 3)

Date: 2026-10-17. Full log: logs/final_qc_commands.log.

## Suite run

`python3 -m pytest tests/test_numeric_provenance.py -v`
-> 6/6 PASS, exit=0:
- provenance coverage (>=60 keys, none unmapped)
- missing phase7_selectivity.csv -> build non-zero exit (fail-loud)
- missing phase11_scaling_fit.csv -> explicit abort message
- phase6_outcomes x1.5 perturbation -> rendered docx changes
- stale-literal guards ("0.12%", title-block "et al.")
- `{...}` placeholder scan across all three docx -> zero

## Input-level perturbation (NEW this pass)

Disposable copy at /tmp/perturb_repo (production results untouched):
- Input: `data/processed/cases.csv`, B of A_target_highAm_400 doubled 5->10.
- Rerun: `scripts/run_quick.py`, exit=0.
- Expected direction: doubling ballistic coefficient halves drag response.
- Observed: fixed_pulse 0.004015 -> 0.002005 m/s (~exactly half),
  tracking 3.530 -> 2.449, uniform 7.967 -> 3.681, baseline 0 -> 0.
- Should-change fields changed; should-not-change (baseline delta_v=0,
  protected object columns) unchanged. Linkage verified.
- Production tree unaffected (test ran in /tmp only; git status clean).

## Perturbation-to-text end-to-end

phase6 x1.5 test (in suite) proves CSV->docx propagation; this input test
proves config/data->CSV->docx. Combined: raw input -> code -> canonical
result -> manuscript linkage is live, not frozen.
