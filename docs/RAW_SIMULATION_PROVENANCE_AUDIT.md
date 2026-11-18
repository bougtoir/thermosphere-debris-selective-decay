# Raw GITM simulation provenance audit

Date: 2026-11-18 (UTC). Scope: log- and checksum-based audit of the retained GITM runs. **GITM was not rerun.**
This audit establishes execution provenance and the integrity of the raw → processed chain; it does not show that the
simulations are independently reproducible or that the model physics is valid.

Scripts: `scripts/raw_provenance_audit.py` → `results/provenance/raw_run_provenance.csv`,
`results/provenance/gitm_build_provenance.json`; `scripts/raw_to_processed_spotcheck.py` →
`results/provenance/raw_to_processed_spotcheck.csv`. Raw re-hash: `/home/ubuntu/qc_render/raw_rehash.csv` (VM).
Copies of the execution records (case manifests, `UAM.in`, `user_heating.in`, `run.log`, `run_information.txt`,
heating energy logs; 90 files, 2.0 MB, SHA-256 in `RUN_RECORDS_MANIFEST.csv`) are in `data/physical/run_records/`.
The originals stay in `/home/ubuntu/models/runs/` (not modified).

## Verdict: **PASS — LOG-VERIFIED**

All 17 items are supported by retained records. No contradiction affecting the results was found. Four minor record
gaps (§3) are documented; none touches a run used in the results in a way that changes a number.

## 1. Checklist

| # | Item | Evidence | Status |
|---|---|---|---|
| 1 | Run identifiers | 16 run directories in `GITM_RUN_MANIFEST.csv`; 11 used (spin4, c4_ctrl, c4_p11_z300r, c4_p10_z300, c4_p11_z150, c4_ctrl_rep, spin8b, c8b_ctrl, c8b_p11_z300, c8x_ctrl, c8x_p11_z300), 5 not used (c4_p11_z300, spin8, c8_ctrl, c8_p11_z300, spin8_np4test) | PASS |
| 2 | GITM source commit | `git -C ~/models/GITM rev-parse HEAD` = `c4fc3150aca274e0e0496ba415696a57d0703e00` (upstream merge 2026-09-04); only `src/user.f90` and `src/aurora.Earth.f90` modified | PASS |
| 3 | Heating-hook commit | `physical/gitm/user_perturbation_heating.f90` and `apply_patch.py` committed in `977e54f` (2026-11-07 11:02Z), unchanged since; the hook text is contained verbatim in the compiled `src/user.f90`; the block-allocation guard is present in `aurora.Earth.f90` | PASS (see §3a) |
| 4 | Build configuration | `Makefile.def`: OS=Linux, COMPILER=gfortran10; `Makefile.conf`: `mpif90` (Open MPI wrapper over gfortran), `-fallow-argument-mismatch -fno-automatic` | PASS |
| 5 | Compiler / MPI | GNU Fortran 11.4.0 (Ubuntu 22.04), Open MPI 4.1.2 — toolchain on the VM at audit time; the build-time version was not logged separately, but the packages were not changed and the executable is unchanged (item 2/10) | PASS (log gap §3b) |
| 6 | Input files | Every `case_manifest.json` lists SHA-256 of `UAM.in`, `static_imf.dat`, `static_sme.dat`, `user_heating.in`; all 4 × 15 hashes match the files in the run directories | PASS |
| 7 | Background initialization | Coarse: spin4 (24 h, from MSIS/IRI, no case manifest — §3c); fine: spin8b (6 h, 4 MPI ranks). Constant drivers in `UAM.in` / `static_*.dat` | PASS |
| 8 | Heating parameters | `heating_as_written` in each manifest equals the case JSON (power, 45°N, 0°E, z0, σh = 1000 km, σz, 3600 s, 600 s ramp) after the documented restart time offset; onset 2002-03-21 01:00 UT for every heated run; the processed NPZ `heating` arrays equal the `user_heating.in` of the heated run | PASS |
| 9 | Control/heated pairing | Same restart, executable, inputs (except `user_heating.in`), grid, ranks and output cadence within each pair: c4_ctrl ↔ c4_p11_z300r / c4_p10_z300 / c4_p11_z150; c8b_ctrl ↔ c8b_p11_z300; c8x_ctrl ↔ c8x_p11_z300 | PASS |
| 10 | Restart chronology | `restart_in_sha256` of every restarted run equals the SHA-256 of the `restartOUT` files of its parent: spin4 → c4_* (17 files each); spin8b → c8b_* (65); c8b_ctrl → c8x_ctrl and c8b_p11_z300 → c8x_p11_z300 (65 each) | PASS |
| 11 | Start / end times | Case JSON start/end match the first and last 3DALL time stamps (coarse 00–12 UT; fine 00–03 UT + 03–12 UT) | PASS |
| 12 | Completion status | Used runs: exit code 0, `GITM.DONE` present, `--> Finalize` in `run.log`. Unused: spin8 exit 253 (`CPCP is zero …`), c8_ctrl/c8_p11_z300 stopped at start (`restartIN/header.rst cannot be found`, recorded exit 0 — §3d), c4_p11_z300 zero heating power (superseded by c4_p11_z300r) | PASS |
| 13 | Output inventory | 3DALL files = (duration / 600 s) × blocks for every used run (1152 coarse 12 h; 1152 fine 3 h; 3456 fine 9 h); +1 output time where GITM also wrote the start time (spin8b, c8x_ctrl), which is not used | PASS |
| 14 | SHA-256 manifests | All 23 831 files of `GITM_RUN_MANIFEST.csv` (53.7 GB = 50.0 GiB) re-hashed on 2026-11-18: 23 831 match, 0 missing, 0 size or hash mismatch | PASS |
| 15 | Processing scripts | NPZ produced by `scripts/physical_g3_paired.py` (`PROCESSED_MANIFEST.csv`); invocations recorded in `post_fine.log` / `post_fine12.log`; the fine 0–12 h pair `c8f_*` is a symlink merge of c8b + c8x (`merge_fine12.sh`) | PASS |
| 16 | Raw → processed transformation | Independent reader (not `gitm_io.py`): density and three wind components at first, middle and last output time, control and heated, all five NPZ — 120/120 arrays **bit-identical** to the raw 3DALL values, altitude levels and heating parameters match | PASS |
| 17 | Consistency of principal outputs | Five NPZ SHA-256 = `PROCESSED_MANIFEST.csv` = public Zenodo files; results regenerated from them in a clean environment (`docs/PUBLIC_REPRODUCTION_FINAL_REPORT.md`) | PASS |

Chronology: predictions frozen in `c93bf8c` (2026-11-07 11:33Z); executable built 10:46Z; first heated run with
non-zero power (c4_p11_z300r) started 19:27Z. Heated output did not exist when the predictions were committed.

## 2. Distinction between log-verified and independently verified

- Independently verified on retained files: raw-file integrity (item 14), input and restart hashes (6, 10), output
  inventory (13), raw → NPZ values (16), NPZ → results (17).
- Log-supported only: that the executable was built from the stated source and patch (file times, contained hook
  text, constant executable hash), the toolchain version at build time (5), and run start/finish times.
- Not verified: a fresh GITM build and rerun reproducing the raw output.

## 3. Record gaps (not consequential)

a. The executable (built 2026-11-07 10:46Z) predates the git commit of the hook (11:02Z). The hook file has not changed
   since that commit and its text is contained verbatim in the compiled `user.f90` (mtime 10:45Z, before the build).
b. The compiler/MPI versions were not written to the run records; recorded here from the unchanged VM toolchain.
c. spin4 has no `case_manifest.json` (written before the manifest system); its files are in `GITM_RUN_MANIFEST.csv`,
   its `restartOUT` hashes match the `restart_in_sha256` of all c4 runs.
d. c8_ctrl / c8_p11_z300 record exit code 0 although GITM stopped at start (missing restart from the failed spin8);
   `run_case.py` records the `mpirun` return code. Neither run produced output or is used.

None of these gaps calls for a GITM rerun.
