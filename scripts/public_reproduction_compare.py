"""Compare clean-clone regenerated outputs with the committed canonical versions (git HEAD of the clone)."""
import io, os, subprocess, sys, json
import numpy as np, pandas as pd
from PIL import Image
C = "/home/ubuntu/repro_final/clone"
def head(p): return subprocess.run(["git", "-C", C, "show", f"HEAD:{p}"], capture_output=True).stdout
st = subprocess.run(["git", "-C", C, "status", "--porcelain", "--untracked-files=all"], capture_output=True, text=True).stdout.splitlines()
tracked = subprocess.run(["git", "-C", C, "ls-files", "results", "manuscript/physical"], capture_output=True, text=True).stdout.split()
rows = []
for p in tracked:
    if not os.path.exists(os.path.join(C, p)): continue
    new = open(os.path.join(C, p), "rb").read(); old = head(p)
    r = dict(path=p, byte_identical=new == old)
    if not r["byte_identical"]:
        ext = os.path.splitext(p)[1]
        if ext == ".csv":
            a, b = pd.read_csv(io.BytesIO(old)), pd.read_csv(io.BytesIO(new))
            r["shape_same"] = a.shape == b.shape and list(a.columns) == list(b.columns)
            if r["shape_same"]:
                num = [c for c in a.columns if pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c])]
                key = [c for c in a.columns if c not in num]
                a2 = a.sort_values(list(a.columns)).reset_index(drop=True) if not key else a.sort_values(key + num).reset_index(drop=True)
                b2 = b.sort_values(list(b.columns)).reset_index(drop=True) if not key else b.sort_values(key + num).reset_index(drop=True)
                r["text_cols_same"] = bool((a2[key].astype(str).values == b2[key].astype(str).values).all()) if key else True
                if num:
                    x, y = a2[num].to_numpy(float), b2[num].to_numpy(float)
                    both = np.isnan(x) & np.isnan(y); d = np.where(both, 0, np.abs(x - y))
                    r["max_abs_diff"] = float(np.nanmax(d)); r["max_rel_diff"] = float(np.nanmax(np.where(both, 0, d / np.maximum(np.abs(x), 1e-300))))
                    r["nan_pattern_same"] = bool((np.isnan(x) == np.isnan(y)).all())
        elif ext in (".png", ".tif", ".tiff"):
            ia, ib = np.asarray(Image.open(io.BytesIO(old)).convert("RGB")), np.asarray(Image.open(io.BytesIO(new)).convert("RGB"))
            r["pixels_identical"] = ia.shape == ib.shape and bool((ia == ib).all())
        elif ext == ".docx":
            import docx
            ta = [q.text for q in docx.Document(io.BytesIO(old)).paragraphs]; tb = [q.text for q in docx.Document(io.BytesIO(new)).paragraphs]
            ca = [c.text for t in docx.Document(io.BytesIO(old)).tables for rr in t.rows for c in rr.cells]
            cb = [c.text for t in docx.Document(io.BytesIO(new)).tables for rr in t.rows for c in rr.cells]
            r["text_identical"] = ta == tb and ca == cb
        elif ext == ".pptx":
            from pptx import Presentation
            def sh(bt): return [(s.shape_type, s.name, getattr(s, "image", None) and s.image.sha1) for sl in Presentation(io.BytesIO(bt)).slides for s in sl.shapes]
            r["content_identical"] = sh(old) == sh(new)
        else:
            r["text_identical"] = new.decode(errors="replace").splitlines() == old.decode(errors="replace").splitlines()
    rows.append(r)
df = pd.DataFrame(rows); df.to_csv("/home/ubuntu/repro_final/compare_results.csv", index=False)
print("tracked outputs compared:", len(df), "byte-identical:", int(df.byte_identical.sum()))
print(df[~df.byte_identical].to_string())
print("untracked new files:", [l for l in st if l.startswith("??")][:20])
