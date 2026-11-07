"""Replace user_perturbation in GITM src/user.f90 with the localized heat source."""
import pathlib
import sys

src = pathlib.Path(sys.argv[1]) / "src" / "user.f90"
new = (pathlib.Path(__file__).parent / "user_perturbation_heating.f90").read_text()
text = src.read_text()
i = text.index("subroutine user_perturbation\n")
j = text.index("end subroutine user_perturbation") + len("end subroutine user_perturbation")
if "Abstract, synthetic localized heat source" in text[i:j]:
    print("already patched")
else:
    src.write_text(text[:i] + new.strip() + text[j:])
    print("patched", src)

# Upstream bug (c4fc315): initialize_fang_arrays runs once per block, so a
# second block on the same MPI rank re-allocates allocated arrays and aborts.
# Guard keeps physics unchanged and is required for nBlocks > 1 per rank.
aur = pathlib.Path(sys.argv[1]) / "src" / "aurora.Earth.f90"
t = aur.read_text()
key = "  use ModSources\n\n  allocate(Fang_Ci(ED_N_Energies, 8), stat=iErr)"
if key in t:
    guard = "  use ModSources\n\n  if (allocated(Fang_Ci)) return\n  allocate(Fang_Ci(ED_N_Energies, 8), stat=iErr)"
    aur.write_text(t.replace(key, guard))
    print("patched", aur)
elif "if (allocated(Fang_Ci)) return" in t:
    print("fang guard already present")
else:
    raise SystemExit("fang allocation block not found")
