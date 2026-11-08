# GITM run queue notes

* Queue 1 (launched before spin4 finished):
  `run_queue.sh c4_p11_z300 c4_ctrl c4_ctrl_rep c4_p10_z300 c4_p11_z150 spin8 c8_ctrl c8_p11_z300`
* Defect found 2026-11-07T14:53Z, after c4_p11_z300 had started: the heating
  hook times `t_on` from GITM `StartTime`, which a restarted run inherits from
  the spin-up (2002-03-20 00:00), not from the case start. `t_on = 3600 s` was
  therefore already in the past and **c4_p11_z300 deposits zero power**
  (`user_heating_log.dat` shows P = 0). Per instruction it was not stopped.
  It is kept as a zero-power, hook-active control (side-effect/determinism
  check against c4_ctrl) and is not used as a perturbed case.
* Fix: `run_case.py` now shifts `t_on` by (case start - restart StartTime)
  and records the offset in `case_manifest.json` (`heating_t_on_offset_s`).
  Applies to every case started after the fix.
* Because queue 1's argument list cannot change, `cases/c4_ctrl_rep.json`
  was overwritten with the corrected heated case (name/rundir
  `c4_p11_z300r`); the original 1-h repeat control is `cases/c4_ctrl_rep2.json`
  and runs in queue 2 after queue 1 exits (`~/models/runs/queue2.log`).
* 2026-11-07T21:45Z (before spin8 started): c8_ctrl and c8_p11_z300 shortened
  from 4 h to 3 h (end 03:00 UT). The 5°×2.5° grid has 4× the columns and a
  smaller CFL step; 3 h covers onset, the 400–500 km peak (~50 min after
  onset in the coarse run) and the first ~1 h of spreading, which is what the
  grid-convergence test (PR8) compares. Later decay is assessed on the coarse
  grid only.
* 2026-11-08T01:42Z: **spin8 failed at the first time step** (rc 253, 8 s wall):
  `CPCP is zero and model is not zero! Must Stop!` in `get_potential.f90`.
  Diagnosis (code reading + test): the stop check in `get_potential` is
  evaluated per block and reduced only across MPI ranks, i.e. it looks at the
  iBlock-th block of every rank at the same time. With 8×8 blocks on 2 ranks
  (32 blocks/rank, 22.5° latitude rows) some simultaneous block pairs contain
  no cell with |mlat| > 45° carrying non-zero Weimer potential, so the
  cross-rank CPCP is 0 and GITM stops; with 4×4 blocks every pair includes a
  polar row. This is a decomposition-dependent sanity check, not a physics
  failure. c8_ctrl / c8_p11_z300 then stopped immediately (no
  `restartIN/header.rst`). All three directories are preserved unchanged as
  failure records.
* Fix without modifying GITM: same executable (same SHA-256), same 8×8 grid,
  **4 MPI ranks** (`--oversubscribe` on 2 vCPU; 16 blocks/rank). Verified by
  `cases/spin8_np4test.json` (18:00–18:10 UT) which passes the step where
  the 2-rank run stopped. Replacement cases: `spin8b`, `c8b_ctrl`,
  `c8b_p11_z300` (otherwise identical to spin8/c8_*; queue log
  `~/models/runs/queue4.log`). MPI rank count changes only round-off-level
  domain decomposition, which is recorded as a fine/coarse difference.
