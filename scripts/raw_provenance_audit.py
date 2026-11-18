"""Log-based provenance audit of the retained GITM runs (no rerun). Writes results/provenance/*.csv."""
import datetime as dt
import glob
import hashlib
import json
import os
import re

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.expanduser("~/models/runs")
GITM = os.path.expanduser("~/models/GITM")
OUT = os.path.join(ROOT, "results", "provenance")
USED = ["spin4", "c4_ctrl", "c4_p11_z300r", "c4_p10_z300", "c4_p11_z150", "c4_ctrl_rep",
        "spin8b", "c8b_ctrl", "c8b_p11_z300", "c8x_ctrl", "c8x_p11_z300"]
FAILED = ["c4_p11_z300", "spin8", "c8_ctrl", "c8_p11_z300", "spin8_np4test"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 22), b""):
            h.update(c)
    return h.hexdigest()


def t(s):
    return dt.datetime.fromisoformat(s)


def main():
    os.makedirs(OUT, exist_ok=True)
    exe = sha(os.path.join(GITM, "src", "GITM.exe"))
    hook = open(os.path.join(ROOT, "physical/gitm/user_perturbation_heating.f90")).read().strip()
    user = open(os.path.join(GITM, "src/user.f90")).read()
    aur = open(os.path.join(GITM, "src/aurora.Earth.f90")).read()
    rows = []
    for name in USED + FAILED:
        d = os.path.join(RUNS, name)
        case = {}
        for cj in sorted(glob.glob(os.path.join(ROOT, "physical/gitm/cases", "*.json"))):
            c = json.load(open(cj))
            if os.path.basename(c.get("rundir", "")) == name:
                case = dict(c, case_file=os.path.basename(cj))
        m = json.load(open(os.path.join(d, "case_manifest.json"))) if os.path.exists(
            os.path.join(d, "case_manifest.json")) else {}
        log = open(os.path.join(d, "run.log"), errors="replace").read() if os.path.exists(
            os.path.join(d, "run.log")) else ""
        r = dict(run=name, used_in_results=name in USED, manifest=bool(m), case_json=case.get("case_file", ""))
        r["exit_code_recorded"] = m.get("exit_code")
        r["gitm_done_marker"] = os.path.exists(os.path.join(d, "UA", "data", "..", "..", "GITM.DONE")) or \
            os.path.exists(os.path.join(d, "GITM.DONE"))
        r["log_finalize"] = "--> Finalize" in log
        r["log_error"] = "; ".join(sorted(set(re.findall(r"(CPCP is zero[^\n]*|cannot be found[^\n]*)", log))))[:120]
        r["exe_sha_match"] = m.get("gitm_exe_sha256") == exe if m else None
        if os.path.exists(os.path.join(d, "GITM.exe")):
            r["rundir_exe_sha_match"] = sha(os.path.join(d, "GITM.exe")) == exe
        ok = []
        for rel, h in (m.get("inputs") or {}).items():
            p = os.path.join(d, rel)
            ok.append(os.path.exists(p) and sha(p) == h)
        r["inputs_n"], r["inputs_match"] = len(ok), all(ok) if ok else None
        rin = m.get("restart_in_sha256")
        src = case.get("restart_from")
        if isinstance(rin, dict) and src:
            okr = [os.path.exists(os.path.join(src, "UA", "restartOUT", k))
                   and sha(os.path.join(src, "UA", "restartOUT", k)) == v for k, v in rin.items()]
            r["restart_files"], r["restart_chain_match"] = len(okr), all(okr)
        r["restart_from"] = os.path.basename(src) if src else ""
        if case:
            hs = case["heating"]
            r["start"], r["end"] = case["start"], case["end"]
            r["power_W"], r["lat"], r["lon"], r["z_km"], r["sigma_h_km"], r["sigma_z_km"] = hs[:6]
            r["duration_s"], r["ramp_s"] = hs[7], hs[8]
            hw = m.get("heating_as_written")
            off = m.get("heating_t_on_offset_s")
            if hw and off is not None:
                r["heating_written_matches_case"] = list(hw[:6]) == list(hs[:6]) and hw[6] == hs[6] + off \
                    and list(hw[7:]) == list(hs[7:])
                origin = t(case["start"]) - dt.timedelta(seconds=off)
                r["onset_utc"] = (origin + dt.timedelta(seconds=hw[6])).isoformat() if hs[0] else ""
            dur = (t(case["end"]) - t(case["start"])).total_seconds()
            nb = case["nblon"] * case["nblat"]
            files = glob.glob(os.path.join(d, "UA", "data", "3DALL_t*.b*"))
            r["blocks"], r["nproc"] = nb, case.get("nproc")
            r["outputs_expected"] = int(round(dur / case["dtplot"])) * nb
            r["outputs_found"] = len(files)
        rows.append(r)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "raw_run_provenance.csv"), index=False)
    src = dict(gitm_commit=os.popen(f"git -C {GITM} rev-parse HEAD").read().strip(),
               gitm_modified=os.popen(f"git -C {GITM} status --short").read().split("\n")[:-1],
               hook_in_user_f90=hook in user, fang_guard="if (allocated(Fang_Ci)) return" in aur,
               exe_sha256=exe, audited_utc=dt.datetime.utcnow().isoformat(timespec="seconds") + "Z")
    json.dump(src, open(os.path.join(OUT, "gitm_build_provenance.json"), "w"), indent=1)
    print(df.to_string())
    print(src)


if __name__ == "__main__":
    main()
