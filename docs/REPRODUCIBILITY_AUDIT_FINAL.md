# Reproducibility audit — final (Gate 6)

Date: 2026-10-17.

## Environment

- Python 3.10 (venv), deps per requirements.txt.
- Entry points: `make all` (full ~40 min), `make quick`, `pytest tests/ -x -q`.

## Results of final verification run

- `make quick`: PASS, 7.1 s. quick_summary.csv values match canonical
  numbers used in the text (tracking 3.530 m/s, fixed_pulse 4.0e-3 m/s,
  protected-column drag 0.433 m/s).
- `pytest tests/ -x -q`: 25 passed — original 20 QC/physics tests + 5 new
  provenance/hardcode tests.
- `scripts/build_manuscript.py`: rebuilds all four artifacts; aborts
  loudly if any canonical CSV is missing; provenance coverage complete.
- Fresh-checkout independence: results/ CSVs are committed; the build only
  needs the repo + deps, no external data fetch. `make all` regenerates
  from src/ + config/ and was validated in the baseline session.
- No perturbation contamination: all perturbation tests run on disposable
  copies (tests use tmp paths / in-memory string mutation only).

## Known limitations

- Long-horizon `make all` not rerun in this revision — only phase11 was
  re-executed because only its prose values were stale; the PR #4 branch
  already validated the rest end-to-end (BASELINE_FREEZE.md).
- flake8 debt pre-existing, untouched.

## Lock-pass verification (2026-10-17)

- `pytest tests/ -x -q`: 26 passed (added placeholder regression test).
- `make quick`: PASS previously this session; quick_summary reproduced.
- `python3 scripts/build_manuscript.py`: clean rebuild after F1/F2 fixes.
- Render: manuscript 14p, inline 20p, supplement 34p (landscape).
- `make all` still not rerun (no scientific change; see BASELINE_FREEZE).
