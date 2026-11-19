"""Write a GITM UAM.in for the paired control/perturbed experiments.

Static, matched drivers (F10.7, hemispheric power, IMF) are used so that the
control and perturbed runs differ only by the user heat source.
"""
from __future__ import annotations

import argparse
import datetime as dt


def uam(start: dt.datetime, end: dt.datetime, nblon: int, nblat: int,
        dt_plot: float, restart: bool, perturb: bool, f107: float = 150.0,
        f107a: float = 150.0, dt_restart: float = 3600.0, cfl: float = 0.75) -> str:
    def t(x):
        return "\n".join(str(v) for v in (x.year, x.month, x.day, x.hour, x.minute, x.second))
    return f"""
#DEBUG
0
0
600.0
F

#RESTART
{'T' if restart else 'F'}

#TIMESTART
{t(start)}

#TIMEEND
{t(end)}

#GRID
{nblon}
{nblat}
-90.0
90.0
0.0
0.0

#SAVEPLOTS
{dt_restart}
1
3DALL
{dt_plot}

#LOGFILE
60.0

#F107
{f107}
{f107a}

#EUV_DATA
F
none

#SME_INDICES
UA/DataIn/static_sme.dat
none
T

#MHD_INDICES
UA/DataIn/static_imf.dat

#ELECTRODYNAMICS
FTA
60.0
weimer05
60.0

#APEX
F

#MSISOBC
T
0.0

#AUSMSOLVER
T

#CFL
{cfl}

#USEPERTURBATION
{'T' if perturb else 'F'}

#END
"""


def driver_files(start: dt.datetime, end: dt.datetime, sme: float = 150.0,
                 bz: float = -2.0, vx: float = 400.0, n_sw: float = 5.0,
                 t_sw: float = 1.0e5) -> tuple[str, str]:
    """Synthetic constant drivers (1-min cadence) covering [start-1h, end+1h]."""
    t0 = start - dt.timedelta(hours=1)
    n = int((end - t0).total_seconds() // 60) + 121
    imf = ["Synthetic constant IMF/solar wind for a controlled sensitivity study", "",
           "#TIMEDELAY", "0.0", "", "#START"]
    ae = ["File created synthetically: constant SME for a controlled sensitivity study", "",
          "=" * 60, "<year>  <month>  <day>  <hour>  <min>  <sec>  <SME (nT)>  <SML (nT)>  <SMU (nT)>"]
    for k in range(n):
        x = t0 + dt.timedelta(minutes=k)
        imf.append(f" {x.year:4d} {x.month:02d} {x.day:02d} {x.hour:02d} {x.minute:02d} 00 000"
                   f"    0.00     0.00 {bz:8.2f} {-vx:9.2f}      0.00      0.00 {n_sw:7.2f} {t_sw:10.1f}")
        ae.append(f"{x.year:4d}  {x.month:02d}  {x.day:02d}  {x.hour:02d}  {x.minute:02d}  00 "
                  f"{sme:8.2f} {-0.6 * sme:8.2f} {0.4 * sme:8.2f}")
    return "\n".join(imf) + "\n", "\n".join(ae) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--nblon", type=int, required=True)
    ap.add_argument("--nblat", type=int, required=True)
    ap.add_argument("--dtplot", type=float, default=600.0)
    ap.add_argument("--restart", action="store_true")
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    f = "%Y-%m-%dT%H:%M:%S"
    s = uam(dt.datetime.strptime(a.start, f), dt.datetime.strptime(a.end, f),
            a.nblon, a.nblat, a.dtplot, a.restart, a.perturb)
    open(a.out, "w").write(s.lstrip())
    imf, ae = driver_files(dt.datetime.strptime(a.start, f), dt.datetime.strptime(a.end, f))
    import os
    d = os.path.join(os.path.dirname(os.path.abspath(a.out)), "UA", "DataIn")
    open(os.path.join(d, "static_imf.dat"), "w").write(imf)
    open(os.path.join(d, "static_sme.dat"), "w").write(ae)
