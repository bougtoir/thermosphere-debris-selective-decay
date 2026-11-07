"""Create and run one GITM case (control or perturbed) from a spun-up restart.

usage: python3 run_case.py <case.json>
case.json: {"name", "rundir", "restart_from" (dir or null), "start", "end",
            "nblon", "nblat", "dtplot", "heating": [P0_W, lat0, lon0, z0_km,
            sigma_h_km, sigma_z_km, t_on_s, duration_s, ramp_s], "nproc"}
Writes <rundir>/case_manifest.json with input hashes, wall time and exit code.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_uam import driver_files, uam  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
F = "%Y-%m-%dT%H:%M:%S"


def sha(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main() -> None:
    c = json.load(open(sys.argv[1]))
    r = c["rundir"]
    if os.path.exists(os.path.join(r, "GITM.DONE")):
        print("already done", r)
        return
    args = [os.path.join(HERE, "setup_run.sh"), r]
    if c.get("restart_from"):
        args.append(c["restart_from"])
    subprocess.run(args, check=True)
    s, e = dt.datetime.strptime(c["start"], F), dt.datetime.strptime(c["end"], F)
    open(os.path.join(r, "UAM.in"), "w").write(
        uam(s, e, c["nblon"], c["nblat"], c["dtplot"], bool(c.get("restart_from")), True,
            dt_restart=c.get("dt_restart", 21600.0)).lstrip())
    imf, ae = driver_files(dt.datetime(2002, 3, 20), dt.datetime(2002, 3, 23))
    open(os.path.join(r, "UA/DataIn/static_imf.dat"), "w").write(imf)
    open(os.path.join(r, "UA/DataIn/static_sme.dat"), "w").write(ae)
    open(os.path.join(r, "UA/DataIn/user_heating.in"), "w").write(
        " ".join(repr(float(x)) for x in c["heating"]) + "\n")
    man = dict(case=c, gitm_exe_sha256=sha(os.path.realpath(os.path.join(r, "GITM.exe"))),
               inputs={p: sha(os.path.join(r, p)) for p in
                       ("UAM.in", "UA/DataIn/static_imf.dat", "UA/DataIn/static_sme.dat",
                        "UA/DataIn/user_heating.in")},
               started_utc=dt.datetime.utcnow().isoformat())
    if c.get("restart_from"):
        man["restart_in_sha256"] = {f: sha(os.path.join(r, "UA/restartIN", f))
                                    for f in sorted(os.listdir(os.path.join(r, "UA/restartIN")))}
    env = dict(os.environ, HWLOC_COMPONENTS="no_os,stop")
    t0 = time.time()
    with open(os.path.join(r, "run.log"), "w") as log:
        rc = subprocess.run(["mpirun", "--oversubscribe", "-np", str(c.get("nproc", 2)), "./GITM.exe"],
                            cwd=r, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
    man.update(exit_code=rc, wall_s=time.time() - t0, finished_utc=dt.datetime.utcnow().isoformat())
    json.dump(man, open(os.path.join(r, "case_manifest.json"), "w"), indent=1)
    print(c["name"], "rc", rc, "wall", round(man["wall_s"]))


if __name__ == "__main__":
    main()
