"""G6: Acta Astronautica manuscript for the GITM localized-heating study.

Every number in the text, tables, highlights and captions is read from canonical outputs (results/, data/physical/)
at build time; scripts/physical_manuscript_figures.py draws the figures from the same files. Citations are numbered
in square brackets in order of first appearance (Acta Astronautica guide, archived in data/raw/journal/), formatted
from the archived Crossref records in data/physical/raw/crossref/.

Outputs (manuscript/physical/): manuscript.docx (tables after first citing paragraph, figure captions listed,
figures supplied separately), manuscript_review_inline.docx (figures also inline), tables.docx, figures.pptx,
highlights.docx, cover_letter.docx, figures/Fig{n}.tif; results/manuscript_physical_values.csv and
results/manuscript_physical_citations.csv record every injected value and citation.
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import os
import re
import shutil

import numpy as np
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from pptx import Presentation
from pptx.util import Inches as PInches
from pptx.util import Pt as PPt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "manuscript/physical")
FIG = os.path.join(ROOT, "results/figures/physical")
WORD_LIMIT = 13000
HL_MAX = 85


def rd(name):
    return pd.read_csv(os.path.join(ROOT, name))


# ---------------------------------------------------------------- values
def minus(x):
    return re.sub(r"(?<![\w.])-(?=\d)", "\u2212", x)


class Values:
    def __init__(self):
        self.rows = []

    def put(self, name, value, source, fmt):
        if fmt == "sci":
            mant, ex = f"{value:.1e}".split("e")
            out = f"{mant} × 10^{{{int(ex)}}}"
        else:
            out = minus(fmt.format(value))
        self.rows.append(dict(name=name, value=value, formatted=out, source=source))
        return out


V = Values()


def spinup_hours(run):
    m = rd("data/physical/GITM_RUN_MANIFEST.csv")
    t = m[m.run.str.endswith("/" + run)].relpath.str.extract(r"3DALL_t(\d{6}_\d{6})")[0].dropna()
    t = sorted(dt.datetime.strptime(x, "%y%m%d_%H%M%S") for x in t)
    return round((t[-1] - t[0]).total_seconds() / 3600.0)


def closure(label):
    t = rd(f"results/tables/physical_g3_{label}_timeseries.csv")
    t = t[(t.alt_km == 400) & (t.E_cum_J > 0)]
    q = t.iloc[0]
    return float(q.dH_total_J / q.E_cum_J), float(t.E_cum_J.max())


def collect():
    v = {}
    src_g2 = "results/tables/physical_g2_acceptance.csv"
    g2 = rd(src_g2).set_index("test")
    for k in ("V4@250", "V4@400", "V4@500"):
        lo = float(g2.loc[k, "value"].split("-")[0])
        v[k] = V.put(k, lo, src_g2, "{:.2f}")
    v["V5"] = V.put("Tn400_minus_MSIS_K", g2.loc["V5", "value"], src_g2, "{}")
    v["V2b_min"] = V.put("Tn_min_K", float(re.search(r"min ([\d.]+)", g2.loc["V2b", "value"]).group(1)), src_g2, "{:.0f}")
    v["spin_c"] = V.put("spinup_coarse_h", spinup_hours("spin4"), "data/physical/GITM_RUN_MANIFEST.csv", "{:d}")
    v["spin_f"] = V.put("spinup_fine_h", spinup_hours("spin8b"), "data/physical/GITM_RUN_MANIFEST.csv", "{:d}")

    s = "results/tables/physical_g3_summary.csv"
    g3 = rd(s)
    for lab in ("p11_z300", "p10_z300", "p11_z150"):
        for h in (300, 400, 500):
            r = g3[(g3.label == lab) & (g3.alt_km == h)].iloc[0]
            v[f"pk_{lab}_{h}"] = V.put(f"peak_drho_{lab}_{h}", 100 * r.peak_drho_rel, s, "{:.0f}")
            v[f"gm_{lab}_{h}"] = V.put(f"max_global_mean_drho_{lab}_{h}", 100 * r.max_global_mean_drho_rel, s, "{:.1f}")
            v[f"af_{lab}_{h}"] = V.put(f"max_area_frac_gt1pct_{lab}_{h}", 100 * r.max_area_frac_gt_1pct, s, "{:.0f}")
        r = g3[(g3.label == lab) & (g3.alt_km == 400)].iloc[0]
        v[f"dT_{lab}"] = V.put(f"max_dT_{lab}", r.max_dT_K, s, "{:.0f}")
        v[f"dOn2_{lab}"] = V.put(f"min_dOn2_{lab}", -100 * r.min_dOn2_rel, s, "{:.0f}")
        v[f"clf_{lab}"] = V.put(f"closure_final_{lab}", r.closure_final, s, "{:.2f}")
    v["ratio_pk_power"] = V.put("peak400_ratio_10GW_over_100GW", float(
        g3[(g3.label == "p10_z300") & (g3.alt_km == 400)].peak_drho_rel.iloc[0]
        / g3[(g3.label == "p11_z300") & (g3.alt_km == 400)].peak_drho_rel.iloc[0]), s, "{:.2f}")
    v["inv_pk_power"] = V.put("peak400_ratio_100GW_over_10GW", 1 / float(v["ratio_pk_power"]), s, "{:.1f}")
    v["gm_ratio"] = V.put("globalmean400_ratio_100GW_over_10GW", float(
        g3[(g3.label == "p11_z300") & (g3.alt_km == 400)].max_global_mean_drho_rel.iloc[0]
        / g3[(g3.label == "p10_z300") & (g3.alt_km == 400)].max_global_mean_drho_rel.iloc[0]), s, "{:.1f}")
    v["ratio_pk_z150"] = V.put("peak400_ratio_z150_over_z300", float(
        g3[(g3.label == "p11_z150") & (g3.alt_km == 400)].peak_drho_rel.iloc[0]
        / g3[(g3.label == "p11_z300") & (g3.alt_km == 400)].peak_drho_rel.iloc[0]), s, "{:.2f}")
    for lab in ("p11_z300", "p11_z300_fine12", "p10_z300", "p11_z150"):
        c, e = closure(lab)
        v[f"cl_{lab}"] = V.put(f"closure_first_{lab}", c, f"results/tables/physical_g3_{lab}_timeseries.csv", "{:.3f}")
        v[f"E_{lab}"] = V.put(f"E_total_{lab}", e, f"results/tables/physical_g3_{lab}_timeseries.csv", "sci")

    s = "results/tables/physical_g3r_realized_forcing.csv"
    f = rd(s).set_index("label")
    v["Preal"] = V.put("realized_power_coarse_GW", f.loc["c4_p11_z300", "realized_power_W"] / 1e9, s, "{:.1f}")
    v["sig_eff"] = V.put("sigma_h_eff_coarse_km", f.loc["c4_p11_z300", "sigma_h_eff_km"], s, "{:.0f}")
    v["sig_eff_f"] = V.put("sigma_h_eff_fine_km", f.loc["p11_z300_fine", "sigma_h_eff_km"], s, "{:.0f}")
    v["cps_c"] = V.put("cells_per_sigma_coarse", f.loc["c4_p11_z300", "cells_per_sigma_h_lat"], s, "{:.1f}")
    v["cps_f"] = V.put("cells_per_sigma_fine", f.loc["p11_z300_fine", "cells_per_sigma_h_lat"], s, "{:.1f}")

    s = "results/tables/physical_g4t_selectivity_evolution.csv"
    ev = rd(s)
    v["n_t400"] = V.put("n_target_400", int(ev[ev.alt_km == 400].n_target.iloc[0]), s, "{:d}")
    v["n_n400"] = V.put("n_nontarget_400", int(ev[ev.alt_km == 400].n_nontarget.iloc[0]), s, "{:d}")
    v["n_tot"] = V.put("n_objects_per_shell", int(ev.n_target.iloc[0] + ev.n_nontarget.iloc[0]), s, "{:d}")
    for lab, grid, tag in (("p11_z300", "36x36", "c"), ("p11_z300_fine12", "72x72", "f")):
        for h in (300, 400, 500):
            x = ev[(ev.label == lab) & (ev.grid == grid) & (ev.alt_km == h)]
            for th in (1, 3):
                q = x.iloc[int(np.argmin(np.abs(x.t_after_onset_s - 3600 * th)))]
                v[f"S{tag}_{h}_{th}h"] = V.put(f"S_{lab}_{grid}_{h}_{th}h", q.selectivity_mean, s, "{:.1f}")
            q = x.sort_values("t_after_onset_s").iloc[-1]
            v["t_end_h"] = V.put("t_end_after_onset_h", q.t_after_onset_s / 3600, s, "{:.0f}")
            v[f"S{tag}_{h}"] = V.put(f"S12_{lab}_{grid}_{h}", q.selectivity_mean, s, "{:.2f}")
            v[f"share{tag}_{h}"] = V.put(f"nontarget_share_{lab}_{grid}_{h}", 100 * q.nontarget_share_of_total_extra, s,
                                         "{:.0f}")
    s = "results/tables/physical_selectivity_bootstrap.csv"
    bs = rd(s)
    for _, q in bs[bs.label == "p11_z300"].iterrows():
        h = int(q.alt_km)
        v[f"ci_lo_{h}"] = V.put(f"S12_ci95_lo_p11_z300_{h}", q.ci95_lo, s, "{:.2f}")
        v[f"ci_hi_{h}"] = V.put(f"S12_ci95_hi_p11_z300_{h}", q.ci95_hi, s, "{:.2f}")
    v["n_boot"] = V.put("n_boot", int(bs.n_boot.iloc[0]), s, "{:,}")
    s = "results/tables/physical_g4t_selectivity_evolution.csv"
    for lab in ("p10_z300", "p11_z150"):
        x = ev[(ev.label == lab) & (ev.grid == "36x36")].sort_values("t_after_onset_s").groupby("alt_km").tail(1)
        for _, q in x.iterrows():
            v[f"S_{lab}_{int(q.alt_km)}"] = V.put(f"S12_{lab}_{int(q.alt_km)}", q.selectivity_mean, s, "{:.2f}")

    s = "results/physical_model_vs_prescribed_patch.csv"
    m = rd(s)
    m = m[(m.label == "p11_z300") & (m.group != "all")]
    var = {}
    for c in ("gitm_extra_dv_mean", "gitm_extra_dv_mean_no_winds", "gitm_extra_dv_mean_nearest_interp",
              "gitm_extra_dv_mean_alt_ref_6378km", "gitm_extra_dv_mean_dt_1200s"):
        p = m.pivot_table(index="alt_km", columns="group", values=c)
        var[c] = p.target / p.nontarget
    base = var.pop("gitm_extra_dv_mean")
    dev = max(float(np.max(np.abs(x.loc[[400.0, 500.0]] / base.loc[[400.0, 500.0]] - 1))) for x in var.values())
    v["orbit_sens"] = V.put("max_orbit_variant_selectivity_change_400_500", 100 * dev, s, "{:.0f}")
    t4 = m[(m.alt_km == 400) & (m.group == "target")].iloc[0]
    v["dv_t400"] = V.put("target_extra_dv_400", t4.gitm_extra_dv_mean * 1e3, s, "{:.1f}")
    v["dv_nat_frac"] = V.put("target_extra_over_natural_400", 100 * t4.gitm_extra_dv_mean / t4.natural_dv_12h_mean, s,
                             "{:.1f}")
    v["dlife400"] = V.put("delta_lifetime_target_400_d", -t4.delta_lifetime_d, s, "{:.3f}")
    v["life400"] = V.put("lifetime_base_400_d", t4.lifetime_base_d, s, "{:.0f}")

    s = "results/tables/physical_contribution_gate_checks.csv"
    gc = rd(s)
    gcr = gc[gc.run != "ALL"]
    for w in (3.0, 12.0):
        for h in (400.0, 500.0):
            x = gcr[(gcr.window_h == w) & (gcr.alt_km == h)]
            v[f"gr_lo_{int(w)}_{int(h)}"] = V.put(f"gitm_over_gauss_min_{w}h_{h}", x.gitm_over_gaussian_min.min(), s,
                                                  "{:.2f}")
            v[f"gr_hi_{int(w)}_{int(h)}"] = V.put(f"gitm_over_gauss_max_{w}h_{h}", x.gitm_over_gaussian_max.max(), s,
                                                  "{:.2f}")
            v[f"gf_lo_{int(w)}_{int(h)}"] = V.put(f"gauss_over_gitm_min_{w}h_{h}", 1 / x.gitm_over_gaussian_max.max(), s,
                                                  "{:.1f}")
            v[f"gf_hi_{int(w)}_{int(h)}"] = V.put(f"gauss_over_gitm_max_{w}h_{h}", 1 / x.gitm_over_gaussian_min.min(), s,
                                                  "{:.1f}")
    v["nvar"] = V.put("n_fit_variants_fine", int(gcr.n_variants.max()), s, "{:d}")
    v["gate12"] = gc[(gc.run == "ALL") & (gc.window_h == 12.0)].verdict_rule.iloc[0]

    x = gcr[(gcr.window_h == 3.0) & (gcr.alt_km == 400.0)].set_index("run").gitm_selectivity
    v["g3h_diff"] = V.put("gitm_sel_3h_400_fine_vs_coarse", 100 * abs(x["fine_native"] / x["coarse"] - 1), s, "{:.0f}")
    s = "results/tables/physical_g3r_spread_metrics.csv"
    sp = rd(s)
    c = sp[(sp.label == "p11_z300") & (sp.grid == "36x36") & (sp.alt_km == 400) & (sp.t_after_onset_s > 0)]
    fr = sp[(sp.label == "p11_z300_fine12") & (sp.grid == "remapped_2_36x36") & (sp.alt_km == 400)]
    v["rg_tmax"] = V.put("t_max_rg_400_h", c.loc[c.radius_of_gyration_km.idxmax(), "t_after_onset_s"] / 3600, s, "{:.0f}")
    q = c.iloc[int(np.argmin(np.abs(c.t_after_onset_s - 10800)))]
    v["pa3h"] = V.put("participation_area_400_3h", 100 * q.participation_area_frac, s, "{:.0f}")
    mm = pd.merge(c, fr, on="t_after_onset_s", suffixes=("_c", "_f"))
    v["pa_diff"] = V.put("max_participation_area_rel_diff_400", 100 * float(np.max(np.abs(
        mm.participation_area_frac_f / mm.participation_area_frac_c - 1))), s, "{:.0f}")

    s = "results/tables/physical_g4t_gaussian_matching.csv"
    gm = rd(s)
    sets = (("p11_z300", "36x36_tmax43200"), ("p11_z300_fine12", "72x72_tmax43200"),
            ("p11_z300_fine12", "remapped_2_36x36_tmax43200"))
    for h in (400.0, 500.0):
        r = []
        for lab, grid in sets:
            q = gm[(gm.label == lab) & (gm.grid == grid) & (gm.alt_km == h)
                   & (gm.comparator == "sigma_scan_1000km_source_centred")].iloc[0]
            r.append(q.selectivity_mean / q.gitm_selectivity_mean)
        v[f"src_lo_{int(h)}"] = V.put(f"src1000_over_gitm_min_{h}", min(r), s, "{:.1f}")
        v[f"src_hi_{int(h)}"] = V.put(f"src1000_over_gitm_max_{h}", max(r), s, "{:.1f}")
    s = "results/tables/physical_g4t_gaussian_decomposition.csv"
    gd = rd(s)
    v["gd_cols"] = list(gd.columns)

    s = "results/grid_sensitivity_metrics_12h.csv"
    gs = rd(s)
    gr = gs.dropna(subset=["A_model_discretization_rel"])
    big = gr[gr.A_model_discretization_rel.abs() > 0.2]
    ok = ~gr.metric.isin(big.metric) & ~gr.metric.str.startswith("centroid_lon")  # as physical_g3r_g4t_docs.py
    v["gs_ok"] = V.put("n_rows_absA_le_0.2", int(ok.sum()), s, "{:d}")
    v["gs_n"] = V.put("n_remappable_rows", int(len(gr)), s, "{:d}")
    v["gs_max_ok"] = V.put("max_absA_among_ok_rows", 100 * float(gr[ok].A_model_discretization_rel.abs().max()), s,
                           "{:.0f}")
    v["gs_B_max"] = V.put("max_absB_all_rows", 100 * float(gr.B_diagnostic_grid_rel.abs().max()), s, "{:.0f}")
    q = gs[(gs.metric == "peak_drho_rel_max") & (gs.alt_km == 400)].iloc[0]
    v["pk_fc"] = V.put("peak400_fine_vs_coarse", 100 * q.fine_native_vs_coarse_rel, s, "{:+.0f}")
    q = gs[(gs.metric == "int_drho_kg_m_max") & (gs.alt_km == 400)].iloc[0]
    v["int_fc"] = V.put("int400_fine_vs_coarse", 100 * q.fine_native_vs_coarse_rel, s, "{:+.1f}")
    q = gs[(gs.metric == "int_neg_drho_kg_m_min") & (gs.alt_km == 400)].iloc[0]
    v["neg_fc"] = V.put("neg_int400_fine_over_coarse", q.fine_native / q.coarse, s, "{:.1f}")
    v["gs"] = gs

    s = "results/tables/physical_prediction_outcomes.csv"
    po = rd(s)
    v["po"] = po
    for k in ("PR1", "PR12"):
        v[k] = V.put(k, 100 * float(po[po.prediction == k].value.iloc[0]), s, "{:.0f}")
    for k in ("PR2", "PR7", "PR10@400", "PR10@300"):
        v[k] = V.put(k, float(po[po.prediction == k].value.iloc[0]), s, "{:.2f}")
    for k in ("PR8a_12h", "PR8b_12h", "PR9"):
        v[k] = V.put(k, 100 * float(po[po.prediction == k].value.iloc[0]), s, "{:+.0f}" if k != "PR9" else "{:.1f}")
    core = po[~po.prediction.str.contains("_12h|fine12")]
    v["n_conf"] = V.put("n_confirmed_core", int((core.verdict == "CONFIRMED").sum()), s, "{:d}")
    v["n_fals"] = V.put("n_falsified_core", int((core.verdict == "FALSIFIED").sum()), s, "{:d}")
    v["n_out"] = V.put("n_outside_core", int(core.verdict.str.startswith("OUTSIDE").sum()), s, "{:d}")
    v["n_core"] = V.put("n_core_rows", int(len(core)), s, "{:d}")
    return v


# ---------------------------------------------------------------- references
class Refs:
    def __init__(self):
        self.tab = rd("references/PRIOR_KNOWLEDGE_VERIFIED.csv").set_index("citation_key")
        self.cr = {}
        for p in glob.glob(os.path.join(ROOT, "data/physical/raw/crossref/*.json")):
            d = json.load(open(p))
            msg = d.get("message", d)
            if msg.get("DOI"):
                self.cr[msg["DOI"].lower()] = msg
        self.order = []

    def num(self, key):
        if key not in self.tab.index:
            raise KeyError(f"citation {key} not in PRIOR_KNOWLEDGE_VERIFIED.csv")
        if key not in self.order:
            self.order.append(key)
        return self.order.index(key) + 1

    def render(self, text):
        def rep(mt):
            ns = sorted(self.num(k.strip()) for k in mt.group(1).split(","))
            out, i = [], 0
            while i < len(ns):
                j = i
                while j + 1 < len(ns) and ns[j + 1] == ns[j] + 1:
                    j += 1
                out.append(f"{ns[i]}–{ns[j]}" if j - i >= 2 else ",".join(str(x) for x in ns[i:j + 1]))
                i = j + 1
            return "[" + ",".join(out) + "]"
        return re.sub(r"\[@([^\]]+)\]", rep, text)

    def entry(self, key):
        r = self.tab.loc[key]
        m = self.cr.get(str(r.doi).lower(), {})
        au = m.get("author") or []
        names = []
        for a in au:
            g = a.get("given", "")
            words = g.replace(".", ". ").replace("\u2010", "-").split()
            ini = " ".join("-".join(q[0] + "." for q in w.split("-") if q) for w in words)
            ini = ini.replace(". ", ".")
            names.append(f"{ini} {a.get('family', '')}".strip() if "family" in a else a.get("name", ""))
        if not names:
            names = [x.strip() for x in str(r.authors).split(";")]
        auth = ", ".join(names[:6]) + (", et al." if len(names) > 6 else "")
        title = re.sub(r"<sub>(.*?)</sub>", r"_{\1}", (m.get("title") or [r.title])[0])
        title = re.sub(r"<sup>(.*?)</sup>", r"^{\1}", re.sub(r"<(?!/?su[bp]>)[^>]+>", "", title))
        cont = (m.get("container-title") or [r.journal])[0]
        vol, pg = m.get("volume"), m.get("page") or m.get("article-number")
        tail = f"{cont}"
        if vol:
            tail += f" {vol}"
        tail += f" ({int(r.year)})"
        if pg:
            tail += f" {pg.replace('-', '–')}"
        return f"{auth}, {title}, {tail}. https://doi.org/{r.doi}"

    def listing(self):
        return [(i + 1, k, self.entry(k)) for i, k in enumerate(self.order)]


# ---------------------------------------------------------------- docx helpers
def runs(par, text, size=None, bold=False):
    for part in re.split(r"(\^\{[^}]*\}|_\{[^}]*\}|\*[^*]+\*)", text):
        if not part:
            continue
        if part.startswith("^{"):
            r = par.add_run(part[2:-1])
            r.font.superscript = True
        elif part.startswith("_{"):
            r = par.add_run(part[2:-1])
            r.font.subscript = True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            r = par.add_run(part[1:-1])
            r.italic = True
        else:
            r = par.add_run(part)
        if size:
            r.font.size = Pt(size)
        if bold:
            r.bold = True
    return par


class Doc:
    def __init__(self, refs, inline_figs):
        self.d = Document()
        st = self.d.styles["Normal"]
        st.font.name = "Times New Roman"
        st.font.size = Pt(12)
        st.paragraph_format.line_spacing = 2.0
        self.refs = refs
        self.inline = inline_figs
        self.words = 0
        self.fig_seen, self.tab_seen = [], []

    def h(self, text, lvl=1):
        self.d.add_heading(text, level=lvl)
        self.words += len(text.split())

    def p(self, text, align=None, count=True):
        text = self.refs.render(text)
        for m in re.finditer(r"Fig\. (\d+)|Figs\. (\d+)[–-](\d+)|Table (\d+)", text):
            if m.group(1) or m.group(2):
                for n in range(int(m.group(1) or m.group(2)), int(m.group(1) or m.group(3)) + 1):
                    if n not in self.fig_seen:
                        self.fig_seen.append(n)
            else:
                n = int(m.group(4))
                if n not in self.tab_seen:
                    self.tab_seen.append(n)
        par = runs(self.d.add_paragraph(), text)
        if align:
            par.alignment = align
        if count:
            self.words += len(re.sub(r"[\^_]\{|\}", "", text).split())
        return par

    def table(self, n, caption, df, note=None):
        assert n in self.tab_seen, f"Table {n} placed before it is cited"
        self.p(f"Table {n}. {caption}", count=True).runs[0].bold = True
        t = self.d.add_table(rows=1, cols=len(df.columns))
        t.style = "Table Grid"
        for i, c in enumerate(df.columns):
            runs(t.rows[0].cells[i].paragraphs[0], str(c), size=9, bold=True)
        for _, r in df.iterrows():
            cells = t.add_row().cells
            for i, c in enumerate(df.columns):
                runs(cells[i].paragraphs[0], str(r[c]), size=9)
        for row in t.rows:
            for c in row.cells:
                c.paragraphs[0].paragraph_format.line_spacing = 1.0
        if note:
            self.p(note).runs[0].font.size = Pt(10)
        self.words += 300

    def figure(self, n, stem):
        assert n in self.fig_seen, f"Fig. {n} placed before it is cited"
        self.words += 300
        if self.inline:
            self.d.add_picture(os.path.join(FIG, stem + ".png"), width=Inches(6.3))
            self.p(f"Fig. {n}. {CAPTIONS[n][1]}", count=False)


CAPTIONS = {
    1: ("fig1_density_anomaly_maps_400km", ""),
    2: ("fig2_redistribution_400km", ""),
    3: ("fig3_selectivity_evolution", ""),
    4: ("fig4_gitm_vs_static_comparators", ""),
    5: ("fig5_power_altitude_dependence", ""),
}


def fill_captions(v):
    CAPTIONS[1] = (CAPTIONS[1][0], (
        "Relative neutral mass-density perturbation Δρ/ρ (heated minus control, divided by control) at 400 km in the "
        "fine-grid (5°×2.5°) GITM pair, at four times after the onset of the 100 GW, 1 h heat source centred at "
        "45°N, 0°E, 300 km (cross). Times are the nearest 10-min model outputs. The colour scale is non-linear."))
    CAPTIONS[2] = (CAPTIONS[2][0], (
        "Redistribution of the 400 km density perturbation for the 100 GW, 300 km case: (a) area-integrated excess "
        "∫Δρ dA over the 400 km shell, (b) participation area fraction, (c) anomaly-weighted radius of gyration about "
        "the anomaly centroid. Solid: coarse grid (10°×5°); dashed: fine grid (5°×2.5°); dotted: fine grid "
        "conservatively remapped (area-weighted 2×2 means of ρ) to the coarse grid before differencing."))
    CAPTIONS[3] = (CAPTIONS[3][0], (
        "Time evolution of the cumulative drag selectivity S(t) (mean extra Δv of target objects divided by that of "
        f"non-target objects; top) and the non-target share of the total extra Δv (bottom) for {v['n_tot']} synthetic "
        "circular orbits per shell at 300, 400 and 500 km (B = 30 kg m^{−2}). Line styles as in Fig. 2. At 300 km "
        "the ratio is ill-conditioned during the first ~30 min because both groups' extra Δv is close to zero."))
    CAPTIONS[4] = (CAPTIONS[4][0], (
        f"Selectivity over the 12 h case window ({v['t_end_h']} h after onset) from GITM and from two static "
        "Gaussian density patches imposed on the GITM control atmosphere: a peak-matched fit (amplitude, centre and "
        "e^{−1/2} width of the GITM perturbation at its peak, switched on while the GITM peak exceeds half its maximum) "
        "and a source-centred patch with σ = 1000 km and the same amplitude and window. Panels: coarse grid, fine grid "
        "on its native grid, and fine grid remapped to the coarse grid. Logarithmic ordinate."))
    CAPTIONS[5] = (CAPTIONS[5][0], (
        "Dependence of the 12 h GITM selectivity on heating power and deposition altitude (coarse grid only, two levels "
        "per factor): 10 GW and 100 GW deposited around 300 km (σ_{z} = 50 km), and 100 GW deposited around 150 km "
        "(σ_{z} = 20 km); same horizontal source shape, timing and orbit population in all cases."))


# ---------------------------------------------------------------- tables
def table1(v):
    rows = [
        ("Background spin-up", f"{v['spin_c']} h from MSIS", f"{v['spin_f']} h from MSIS"),
        ("Blocks × cells (lon × lat)", "4×4 × 9×9 → 36×36", "8×8 × 9×9 → 72×72"),
        ("Cell size", "10° × 5°", "5° × 2.5°"),
        ("Cells per σ_{h} (latitude)", v["cps_c"], v["cps_f"]),
        ("Realized σ_{h} of source (km)", v["sig_eff"], v["sig_eff_f"]),
        ("MPI ranks", "2", "4"),
        ("Heated cases (P_{0}, z_{0})", "100 GW, 300 km; 10 GW, 300 km; 100 GW, 150 km", "100 GW, 300 km"),
        ("Deposited energy, 100 GW 300 km (J)", v["E_p11_z300"], v["E_p11_z300_fine12"]),
        ("Energy closure, first output after onset", v["cl_p11_z300"], v["cl_p11_z300_fine12"]),
        ("Case window", "12 h (paired control)", "0–3 h, restarted 3–12 h (paired control)"),
    ]
    return pd.DataFrame(rows, columns=["Item", "Coarse grid", "Fine grid"])


def table2(v):
    gm = rd("results/tables/physical_g4t_gaussian_matching.csv")
    gc = rd("results/tables/physical_contribution_gate_checks.csv")
    gc = gc[(gc.run != "ALL") & (gc.window_h == 12.0)]
    ev = rd("results/tables/physical_g4t_selectivity_evolution.csv")
    rows = []
    for lab, grid, run, eg, name in (("p11_z300", "36x36_tmax43200", "coarse", "36x36", "Coarse"),
                                     ("p11_z300_fine12", "72x72_tmax43200", "fine_native", "72x72", "Fine, native"),
                                     ("p11_z300_fine12", "remapped_2_36x36_tmax43200", "fine_remapped",
                                      "remapped_2_36x36", "Fine, remapped")):
        for h in (300.0, 400.0, 500.0):
            x = gm[(gm.label == lab) & (gm.grid == grid) & (gm.alt_km == h)].set_index("comparator")
            e = ev[(ev.label == lab) & (ev.grid == eg) & (ev.alt_km == h)].sort_values("t_after_onset_s").iloc[-1]
            g = gc[(gc.run == run) & (gc.alt_km == h)]
            rng = (f"{g.gitm_over_gaussian_min.iloc[0]:.2f}–{g.gitm_over_gaussian_max.iloc[0]:.2f}"
                   if len(g) else "—")
            rows.append((name, f"{h:.0f}", f"{x.loc['peak_matched_fit', 'gitm_selectivity_mean']:.2f}",
                         f"{100 * e.nontarget_share_of_total_extra:.0f}",
                         f"{x.loc['peak_matched_fit', 'selectivity_mean']:.2f}", rng,
                         f"{x.loc['sigma_scan_1000km_source_centred', 'selectivity_mean']:.2f}"))
    return pd.DataFrame(rows, columns=["Grid", "Orbit altitude (km)", "S, GITM", "Non-target share of extra Δv (%)",
                                       "S, peak-matched Gaussian", "S_{GITM}/S_{Gauss}, all fit variants",
                                       "S, source-centred σ = 1000 km"])


GS_ROWS = (("orbit_selectivity_mean", "Selectivity S (12 h)"), ("orbit_target_dv_mean", "Target extra Δv"),
           ("orbit_nontarget_dv_mean", "Non-target extra Δv"), ("peak_drho_rel_max", "Peak Δρ/ρ"),
           ("int_drho_kg_m_max", "Max ∫Δρ dA"), ("area_frac_pos_gt_0.01_max", "Max area with Δρ/ρ > 1%"),
           ("radius_of_gyration_km_end", "Radius of gyration, end"),
           ("rg_growth_ms_mean_after_30min", "Mean spreading speed"),
           ("int_neg_drho_kg_m_min", "Min ∫Δρ^{−} dA (negative part)"),
           ("centroid_lat_deg_end", "Centroid latitude, end"))


def table3(v):
    gs = v["gs"]
    rows = []
    for met, name in GS_ROWS:
        for h in (400.0, 500.0):
            q = gs[(gs.metric == met) & (gs.alt_km == h)].iloc[0]
            rows.append((name, f"{h:.0f}", minus(f"{q.coarse:.4g}"), minus(f"{q.fine_native:.4g}"),
                         minus(f"{q.fine_remapped:.4g}"),
                         minus(f"{100 * q.A_model_discretization_rel:+.1f}"), minus(f"{100 * q.B_diagnostic_grid_rel:+.1f}")))
    return pd.DataFrame(rows, columns=["Metric", "Altitude (km)", "Coarse", "Fine, native", "Fine, remapped",
                                       "A: model (%)", "B: diagnostic (%)"])


PR_TEXT = {  # abridged from docs/PRIOR_PREDICTIONS_FROZEN.md (predicted range; falsification rule)
    "PR1": "Peak Δρ/ρ at 400 km, 100 GW: 5–100%",
    "PR2": "10 GW/100 GW peak ratio 0.05–0.2 (≈ linear)",
    "PR3": "400 km peak 0.5–2 h after onset (h)",
    "PR4": "Depletion ≤ 1/3 of peak; O/N_{2} decrease at source",
    "PR5": "|Δρ/ρ| > 1% beyond 3000 km within 3 h",
    "PR6a": "Local peak e-folding 1–4 h after switch-off (h)",
    "PR6b": "Global-mean excess e-folding > 3 h (h)",
    "PR7": "150 km/300 km ratio of 400 km peak within 1/3–3",
    "PR8a": "Fine vs coarse peak Δρ/ρ change < 30%",
    "PR8b": "Fine vs coarse integrated mass excess change < 20%",
    "PR9": "Target extra Δv 0.1–3% of natural Δv over 12 h",
    "PR10": "Gaussian/GITM selectivity ≥ 3",
    "PR11": "GITM/Gaussian target extra Δv 0.3–3",
    "PR12": "100 GW gives δ < 1 at 400 km",
}


def table4(v):
    po = v["po"]
    rows = []
    for _, r in po.iterrows():
        k = r.prediction
        base = k.split("@")[0].replace("_12h", "")
        alt = k.split("@")[1].split("_")[0] + " km" if "@" in k else "—"
        grid = ("fine, native" if "native" in k else "fine, remapped" if "remapped" in k
                else "coarse vs fine, 12 h" if "_12h" in k else "coarse vs fine, 3 h" if base.startswith("PR8")
                else "coarse")
        verdict = r.verdict.replace("OUTSIDE_RANGE_NOT_FALSIFIED", "outside range, not falsified").lower()
        rows.append((base, PR_TEXT.get(base, r.quantity), alt, grid, minus(f"{r.value:.3g}"), verdict))
    return pd.DataFrame(rows, columns=["ID", "Frozen prediction (abridged)", "Altitude", "Grid", "Value", "Outcome"])


# ---------------------------------------------------------------- manuscript text
TITLE = ("Transport limits the orbital-drag selectivity of a localized thermospheric heat source: "
         "a coupled GITM–orbit study")


def highlights(v):
    h = [
        "Coupled GITM–orbit runs test drag selectivity of compact thermospheric heating",
        f"After 12 h, target/non-target drag ratio is ~{float(v['Sc_400']):.1f} at 400 km, ~{float(v['Sc_500']):.0f} at 500 km",
        f"{v['sharec_400']}% of extra drag at 400 km falls on non-target objects",
        f"Static Gaussian patches overstate selectivity {v['gf_lo_12_400']}–{v['gf_hi_12_500']}×",
        "Coarse and fine grids agree on selectivity to within a few percent",
    ]
    for x in h:
        assert len(x) <= HL_MAX, (len(x), x)
    return h


def body(D, v):
    S = v
    D.p(TITLE, align=WD_ALIGN_PARAGRAPH.CENTER).runs[0].bold = True
    D.p("T. Onishi", align=WD_ALIGN_PARAGRAPH.CENTER)
    D.p("Affiliation: [to be entered by the author]. Corresponding author: T. Onishi, bougtoir@gmail.com",
        align=WD_ALIGN_PARAGRAPH.CENTER)

    D.h("Abstract")
    D.p(
        "Proposals to accelerate the decay of selected debris objects by locally heating the thermosphere assume that "
        "the resulting density enhancement stays where it was deposited. I test that assumption with a physically "
        "self-consistent model. A compact neutral heat source (100 GW for 1 h, centred at 300 km and 45°N) is inserted "
        "into the Global Ionosphere–Thermosphere Model (GITM) and paired with an unheated control, and the resulting "
        f"density and wind fields drive drag on {S['n_tot']} synthetic circular orbits per shell at 300, 400 and 500 km. "
        f"The perturbation reaches {S['pk_p11_z300_400']}% at 400 km but spreads over most of the globe within hours. "
        f"Over 12 h the ratio of mean extra Δv between objects that passed through the source and all others "
        f"(selectivity) is {S['Sc_400']} at 400 km, {S['Sc_500']} at 500 km and {S['Sc_300']} at 300 km; about "
        f"{S['sharec_400']}% of the extra drag at 400 km falls on non-target objects. Static Gaussian patches matched "
        f"to the GITM peak overstate selectivity by factors of {S['gf_lo_12_400']}–{S['gf_hi_12_400']} at 400 km and "
        f"{S['gf_lo_12_500']}–{S['gf_hi_12_500']} at 500 km, and a source-centred 1000 km patch by "
        f"{S['src_lo_400']}–{S['src_hi_500']}. A 5°×2.5° repeat changes the 12 h selectivity by less than 2% at 400 "
        "and 500 km. In two-level tests, selectivity is lower at 100 GW than at 10 GW and disappears for deposition "
        "at 150 km. Transport therefore bounds the selectivity attainable from localized heating well below what "
        "prescribed-patch models imply.")
    D.p("Keywords: thermosphere; orbital debris; atmospheric drag; GITM; localized heating; density perturbation",
        count=True)

    D.h("1. Introduction")
    D.p(
        "Most low-Earth-orbit debris removal concepts act on the object, either by adding drag area or by applying "
        "momentum directly, for example with ground- or space-based lasers [@serfontein2021dragaug,"
        "rhatigan2020deorbit,schall1991laser,rubenchik2010laser]. An alternative family acts on the medium: if the "
        "neutral density along a target's path could be raised, its drag and decay rate would increase without "
        "contact. Enhanced ionospheric drag has been discussed for this purpose [@smith2020ionodrag]. For neutral "
        "drag, the relevant question is whether a density enhancement can be made selective — larger for the "
        "objects one wants to remove than for the rest of the population sharing the shell.")
    D.p(
        "The thermosphere is known to respond strongly and quickly to energy input. Storm-time heating raises density "
        "globally within hours [@bruinsma2006storm,sutton2009rapid,emmert2015review], and localized auroral or cusp "
        "heating produces density enhancements that can approach a factor of two near 400 km [@luhr2004cusp,"
        "crowley2010cusp,carlson2012cusp]. Physics-based models reproduce these responses and show that sudden, "
        "intense heating launches travelling atmospheric disturbances and departures from hydrostatic balance that "
        "carry the perturbation away from the source [@deng2008nonhydro,gardner2010tad]. In GITM, an idealized "
        "50 GW substorm-like input raises the local density by about 14% [@liu2015substorm]. The drag consequences "
        "of storm-time density increases are also well documented, including the loss of newly launched satellites "
        "[@oliveira2019drag,fang2022starlink,baruah2024starlink].")
    D.p(
        "What has not been established is how the horizontal and vertical redistribution of a localized perturbation "
        "translates into the drag received by objects that did, and did not, pass through the heated region. "
        "Screening studies that prescribe a static Gaussian density patch around the source implicitly assume that "
        "the perturbation stays put, which maximises the apparent selectivity. Here I replace the prescribed patch "
        "with a self-consistent general circulation model, the Global Ionosphere–Thermosphere Model (GITM) "
        "[@ridley2006gitm], couple its paired heated and control fields directly to an orbit propagator, and ask "
        "three questions: (i) how selective the cumulative drag is over 12 h; (ii) by how much static patches "
        "overstate it; and (iii) whether the answer survives a change of model resolution. Predictions for the "
        "physical response and for selectivity were written down and committed before any heated output existed, "
        "and are scored against the results.")

    D.h("2. Methods")
    D.h("2.1. Thermosphere model and background state", 2)
    D.p(
        "GITM solves the non-hydrostatic Navier–Stokes equations for the neutral and ion species on a spherical grid "
        "with altitude as the vertical coordinate [@ridley2006gitm]. I used the public GITM source (commit "
        "c4fc315), compiled with GNU Fortran 11.4 and Open MPI 4.1.2, with 50 altitude levels starting at "
        "100 km. The background was a quiet equinox (2002-03-21) with constant drivers: F10.7 = F10.7A = 150, "
        "interplanetary magnetic field B_{z} = −2 nT, solar wind 400 km s^{−1}, and a constant SuperMAG "
        "electrojet index SME = 150 nT "
        "driving the FTA auroral model. High-latitude electrodynamics used the Weimer model [@weimer2005] "
        "and the lower boundary was set "
        "from NRLMSISE-00 [@picone2002msis]. Constant drivers ensure that heated and control runs differ only by "
        "the added heat source.")
    D.p(
        f"The coarse-grid background was spun up for {S['spin_c']} h from an MSIS initial state. Its global-mean "
        f"density at 250, 400 and 500 km was {S['V4@250']}, {S['V4@400']} and {S['V4@500']} times the NRLMSISE-00 "
        f"value for the same time, and the 400 km neutral temperature differed from MSIS by {S['V5']}; these and "
        "other acceptance criteria were set before the spin-up was inspected. One criterion failed: the minimum "
        f"neutral temperature was {S['V2b_min']} K, against a lower bound of 150 K, in a small high-latitude region "
        "near 100–107 km. I retain this failure as a limitation; it lies far below the heated layer and the orbit "
        "shells.")
    D.h("2.2. Localized heat source", 2)
    D.p(
        "A heating term was added to the GITM neutral energy equation through the model's user-perturbation hook. "
        "Its spatial shape is Gaussian in great-circle distance from the centre (σ_{h} = 1000 km) and in altitude "
        "(σ_{z} = 50 km around z_{0} = 300 km, or 20 km around 150 km), and its time profile is a 1 h cosine-tapered boxcar with "
        f"10 min ramps, which deposits {S['E_p11_z300']} J at 100 GW. The heating rate is normalised on the "
        "discrete grid with a global MPI sum of "
        "weight × cell volume, so the deposited power equals the requested P_{0} irrespective of grid or domain "
        f"decomposition; the realized power on the coarse grid was {S['Preal']} GW, and the realized horizontal width "
        f"was {S['sig_eff']} km on the coarse grid and {S['sig_eff_f']} km on the fine grid. The source is an abstract "
        "neutral energy input; no heating mechanism or hardware is implied.")
    D.h("2.3. Experiments", 2)
    D.p(
        "Each heated case was paired with a control started from the same restart file with zero source power, so "
        "that every reported perturbation is a heated-minus-control difference at identical times. On the coarse "
        "grid (10°×5°) I ran three heated cases: 100 GW and 10 GW centred at 300 km, and 100 GW centred at 150 km, "
        "each for 12 h with heating from 1 h to 2 h. The 100 GW, 300 km pair was repeated on a fine grid "
        "(5°×2.5°). The fine pair was run to 3 h and then continued from its 3 h restart files to 12 h, with the "
        "source timing corrected for the restart origin; the 3 h outputs were kept unchanged. Table 1 lists the two "
        "configurations. Energy closure — the change in total neutral internal energy over the deposited energy at "
        f"the first output after onset — was {S['cl_p11_z300']} and {S['cl_p11_z300_fine12']} for the coarse and "
        f"fine 100 GW pairs, {S['cl_p10_z300']} for 10 GW and {S['cl_p11_z150']} for 150 km deposition.")
    D.table(1, "Configuration of the coarse- and fine-grid GITM experiments.", table1(v),
            "Cells per σ_{h} and realized σ_{h} are computed from the source as evaluated on each grid. The fine grid "
            "used four MPI ranks because a decomposition-dependent sanity check in the GITM potential solver stopped "
            "the two-rank run; the executable and grid were otherwise identical.")
    D.h("2.4. Orbit coupling and selectivity", 2)
    D.p(
        f"For each of 300, 400 and 500 km, {S['n_tot']} synthetic circular orbits were generated at inclinations "
        "of 30°, 50°, 70° and 97° with random node and phase (fixed seed). Orbits were propagated with J2 secular "
        "rates at 10 s steps, and the GITM density (log-linear interpolation in space and time between 10 min "
        "outputs) and winds were sampled along each track. The extra drag velocity change of each object is the "
        "time integral of (ρ_{p}|v_{rel,p}|^{2} − ρ_{c}|v_{rel,c}|^{2})/(2B), where subscripts p and c denote the "
        "heated and control runs, v_{rel} is the velocity relative to the co-rotating atmosphere plus the GITM wind, "
        "and B = 30 kg m^{−2}. An object is a target if its ground track comes within σ_{h} of the source centre "
        f"while the source is on ({S['n_t400']} of {S['n_tot']} objects at 400 km). The selectivity S(t) is the mean "
        "cumulative extra Δv of targets divided by that of non-targets. Replacing linear by nearest-neighbour "
        "interpolation, removing winds, changing the Earth radius used for altitude, or doubling the output interval "
        f"changed the 12 h selectivity at 400 and 500 km by at most {S['orbit_sens']}%. Sampling uncertainty of S "
        f"was estimated by resampling targets and non-targets separately with replacement ({S['n_boot']} replicates, "
        "percentile 95% intervals).")
    D.h("2.5. Static comparators", 2)
    D.p(
        "To isolate the effect of transport, the same orbits were also flown through static Gaussian patches "
        "imposed on the GITM control atmosphere. The peak-matched patch takes the amplitude, centre and e^{−1/2} "
        "area-equivalent width of the GITM perturbation at the time of its peak at each orbit altitude, and is held "
        "fixed while the GITM peak exceeds half its maximum. The source-centred patch, the form used in earlier "
        "screening, has the same amplitude and window but is centred on the source with σ = 1000 km. Because the "
        "peak-matched fit depends on discrete choices, I also recomputed it with the centre, width and time window "
        "taken from the other grid.")
    D.h("2.6. Resolution test", 2)
    D.p(
        "For each diagnostic, the fine-grid result was compared with the coarse-grid result in two ways: on its native "
        "grid, and after conservative remapping of ρ (area-weighted 2×2 means) to the coarse grid before "
        "differencing. The remapped comparison (A) measures the change due to the model's discretization; the "
        "native-versus-remapped difference (B) measures the change due only to evaluating diagnostics on a finer "
        f"grid. The fine background was spun up for {S['spin_f']} h, against {S['spin_c']} h on the coarse grid, so "
        "A also contains any effect of the shorter spin-up. With two resolutions, these differences indicate "
        "sensitivity; they do not establish numerical convergence.")
    D.h("2.7. Frozen predictions", 2)
    D.p(
        "Before the first heated run, I recorded quantitative predictions (PR1–PR12) derived from published "
        "simulations and observations, together with falsification rules, and a decision rule for the scientific "
        "contribution that required the direction of the GITM-versus-patch difference to be preserved across grids. "
        "Thresholds were not changed after results were available; the outcomes are scored in Section 3.6.")

    D.h("3. Results")
    D.h("3.1. Physical response and redistribution", 2)
    D.p(
        f"The 100 GW source raised the 400 km density by up to {S['pk_p11_z300_400']}% and the 500 km density by up to "
        f"{S['pk_p11_z300_500']}%, with neutral temperature increases of up to {S['dT_p11_z300']} K and O/N_{{2}} "
        f"decreases of up to {S['dOn2_p11_z300']}% in the heated column. Fig. 1 shows that the perturbation, compact "
        f"at the end of heating, is carried equatorward and westward; at 3 h after onset it covers {S['pa3h']}% of the "
        "shell (participation area). By "
        f"the end of the window the residual 400 km perturbation is a few per cent and nearly global, with weak "
        "negative anomalies near the original source. The area-integrated excess at 400 km peaks just after "
        "switch-off and then decays, while the participation area and radius of gyration keep growing for about "
        f"{S['rg_tmax']} h (Fig. 2). The largest area with Δρ/ρ > 1% at 400 km was {S['af_p11_z300_400']}% of the shell, and the "
        f"global-mean density increase peaked at {S['gm_p11_z300_400']}%.")
    D.figure(1, CAPTIONS[1][0])
    D.figure(2, CAPTIONS[2][0])
    D.h("3.2. Evolution of drag selectivity", 2)
    D.p(
        "Because targets are defined by their passage through the source while it is on, they collect most of their "
        "extra drag early, whereas non-targets keep accumulating drag from the spreading perturbation. As a result "
        f"S(t) falls monotonically after the first hour at 400 and 500 km (Fig. 3): at 400 km from {S['Sc_400_1h']} at "
        f"1 h to {S['Sc_400_3h']} at 3 h and {S['Sc_400']} at {S['t_end_h']} h after onset; at 500 km from "
        f"{S['Sc_500_1h']} to {S['Sc_500_3h']} and {S['Sc_500']}. Resampling the objects gives 95% intervals of "
        f"{S['ci_lo_400']}–{S['ci_hi_400']} at 400 km and {S['ci_lo_500']}–{S['ci_hi_500']} at 500 km for the coarse "
        "12 h values, so the orbit sample is not the limiting uncertainty. At 300 km, where the perturbation is smaller and "
        f"broad, S settles near unity ({S['Sc_300']}). By the end of the window non-targets account for "
        f"{S['sharec_400']}% of the total extra Δv at 400 km and {S['sharec_500']}% at 500 km. Table 2 summarises "
        f"the 12 h values. The target extra Δv at 400 km was {S['dv_t400']} mm s^{{−1}}, {S['dv_nat_frac']}% of the "
        f"natural drag Δv over the same window, which shortens a {S['life400']} d orbital lifetime by about "
        f"{S['dlife400']} d.")
    D.h("3.3. Comparison with static patches", 2)
    D.p(
        "Static patches give substantially higher selectivity (Fig. 4). Over 12 h, the peak-matched Gaussian "
        f"overstates the GITM selectivity by factors of {S['gf_lo_12_400']}–{S['gf_hi_12_400']} at 400 km and "
        f"{S['gf_lo_12_500']}–{S['gf_hi_12_500']} at 500 km, across both grids and all fit variants (Table 2). The "
        f"source-centred σ = 1000 km patch overstates it by {S['src_lo_400']}–{S['src_hi_400']} at 400 km and "
        f"{S['src_lo_500']}–{S['src_hi_500']} at 500 km. At 300 km, where the perturbation is weak and broad, the "
        "peak-matched patch is close to GITM.")
    D.table(2, "Twelve-hour drag selectivity from GITM and from static comparators, 100 GW source at 300 km.",
            table2(v),
            "S is the ratio of mean extra Δv of target and non-target objects. The range in the sixth column covers "
            "the peak-matched fit with its own centre, width and window and with each of these taken from the other "
            "grid (two variants on the coarse grid, "
            f"{S['nvar']} on the fine grid); it was evaluated at 400 and 500 km only.")
    D.p(
        f"Over the first 3 h the comparison is different. At 400 km, the GITM selectivity is indistinguishable from "
        f"that of the peak-matched patch (ratio {S['gr_lo_3_400']}–{S['gr_hi_3_400']} across grids and fit variants), and the "
        "sign of the difference depends on the fit. The sign change between grids comes from the half-maximum time "
        "window, which starts one 10 min output earlier on the fine grid; using the coarse-grid window on the fine "
        f"grid restores agreement in sign, and the GITM selectivity itself differs between grids by {S['g3h_diff']}%. The "
        "transport-driven reduction relative to a static patch at 400 km is therefore a property of the post-heating "
        f"redistribution, not of the heating hour. At 500 km the reduction is already present at 3 h "
        f"(ratio {S['gr_lo_3_500']}–{S['gr_hi_3_500']}).")
    D.figure(3, CAPTIONS[3][0])
    D.figure(4, CAPTIONS[4][0])
    D.h("3.4. Sensitivity to model resolution", 2)
    D.p(
        f"Of {S['gs_n']} diagnostic-by-altitude comparisons that can be remapped, {S['gs_ok']} belong to diagnostics "
        f"that changed by 20% or less between grids at every altitude (largest change {S['gs_max_ok']}%), and "
        f"the diagnostic-grid effect B never exceeded {S['gs_B_max']}% "
        "(Table 3). The 12 h selectivity, the target and non-target extra Δv, the peak and integrated perturbation, "
        "the affected area and the spreading rate are all robust in this sense, and the fine-grid curves overlie "
        "the coarse-grid curves throughout the 12 h (Figs. 2–3). The participation area differs by up to "
        f"{S['pa_diff']}% in mid-window. The fine-vs-coarse change in peak Δρ/ρ at 400 km was {S['pk_fc']}% "
        "and in integrated excess "
        f"{S['int_fc']}%, so both frozen resolution criteria (PR8a: < 30%; PR8b: < 20%) were met over 3 h and 12 h. "
        "Two quantities are resolution-sensitive and are not used for any conclusion: the negative perturbation, "
        f"whose integral is {S['neg_fc']} times larger on the fine grid, and the end-of-window centroid, which is "
        "poorly defined once the perturbation is nearly global.")
    D.table(3, "Coarse- versus fine-grid sensitivity of the 100 GW, 300 km case over 12 h.", table3(v),
            "A: remapped fine minus coarse, relative to coarse (model discretization plus the shorter fine spin-up). "
            "B: native fine minus remapped fine, relative to remapped (diagnostic grid only). Δv in m s^{−1}; "
            "integrals in kg m^{−1}; radius in km; speed in m s^{−1}; latitude in degrees.")
    D.h("3.5. Power and deposition altitude", 2)
    D.p(
        "Two further coarse-grid pairs bracket the dependence on source parameters (Fig. 5). Reducing the power to "
        f"10 GW reduced the 400 km peak only to {S['ratio_pk_power']} of its 100 GW value, whereas the global-mean "
        f"density increase at 400 km fell from {S['gm_p11_z300_400']}% to {S['gm_p10_z300_400']}% and the maximum area "
        f"with Δρ/ρ > 1% from {S['af_p11_z300_400']}% to {S['af_p10_z300_400']}%. The 12 h selectivity was "
        f"correspondingly higher at 10 GW ({S['S_p10_z300_400']} at "
        f"400 km, {S['S_p10_z300_500']} at 500 km). Depositing 100 GW at 150 km produced a 400 km peak "
        f"{S['ratio_pk_z150']} times that of 300 km deposition and selectivities of {S['S_p11_z150_400']} and "
        f"{S['S_p11_z150_500']} at 400 and 500 km: lower-altitude heating raises density almost uniformly at orbit "
        "heights. These are two-level contrasts on one grid and do not define a scaling law.")
    D.figure(5, CAPTIONS[5][0])
    D.h("3.6. Scorecard of frozen predictions", 2)
    D.p(
        f"Of the {S['n_core']} pre-registered outcomes evaluated on the primary configuration, {S['n_conf']} were "
        f"confirmed, {S['n_fals']} falsified and {S['n_out']} fell outside the predicted range without being "
        "falsified (Table 4). The falsifications are informative. The 400 km peak response was "
        f"{S['PR1']}%, above the predicted 5–100% (PR1), so a 100 GW source does reach δ ≥ 1 (PR12). The response was "
        f"less than linear in power, with a 10 GW/100 GW peak ratio of {S['PR2']} (predicted 0.05–0.2; PR2). Deposition "
        f"at 150 km was much less effective at 400 km than predicted (ratio {S['PR7']}, PR7). The predicted ≥ 3-fold "
        "reduction of selectivity relative to the peak-matched patch (PR10) held at 500 km, was not reached at 400 km "
        f"(factor {S['PR10@400']}, outside the range but not falsified) and was falsified at 300 km "
        f"(factor {S['PR10@300']}), where the perturbation is broad and selectivity is close to unity in both "
        f"fields. The target extra Δv at 400 km ({S['PR9']}% of natural drag) slightly exceeded the predicted range "
        "(PR9). All fine-grid rows reproduce the coarse-grid outcomes.")
    D.table(4, "Outcomes of the predictions frozen before the first heated run.", table4(v),
            "Values are those of the quantity named in the scorecard file; 12 h and fine-grid rows were added after "
            "the fine-grid extension using the unchanged rules.")

    D.h("4. Discussion")
    D.p(
        "The central result is that the selectivity of drag from a localized heat source is limited by the "
        "thermosphere's own transport. Within a few hours of switch-off, the excess energy and mass are carried well "
        "beyond the source by the same wind and wave response known from auroral and cusp heating [@deng2008nonhydro,"
        "gardner2010tad,liu2015substorm], and objects that never passed the source then collect most of the extra "
        "drag. A static density patch cannot represent this, so it overstates selectivity by a factor that grows "
        "with altitude and with the time over which drag is accumulated. In this experiment the overstatement over "
        f"12 h is about {S['gf_lo_12_400']}–{S['gf_hi_12_400']}-fold at 400 km and {S['gf_lo_12_500']}–"
        f"{S['gf_hi_12_500']}-fold at 500 km relative to a patch fitted to GITM itself, and "
        f"{S['src_lo_400']}–{S['src_hi_500']}-fold relative to a source-sized patch. These factors, rather than the "
        "absolute selectivity, are the transferable result, because they compare a self-consistent and a prescribed "
        "density field under the same forcing, background and orbits.")
    D.p(
        f"The power dependence points the same way. Increasing the power tenfold increased the 400 km peak only "
        f"{S['inv_pk_power']}-fold but raised the global-mean increase {S['gm_ratio']}-fold, so selectivity fell. Lowering the "
        "deposition altitude removed selectivity altogether. Within the tested range, therefore, neither more power "
        "nor deeper deposition makes the effect more selective; the most selective configuration tested is the "
        "weakest one, where the absolute effect on any object is also smallest. The target drag increment at "
        f"400 km for 100 GW sustained for 1 h was {S['dv_nat_frac']}% of natural drag over 12 h, which changes the "
        "orbital lifetime by a negligible amount. The study does not address how such a source could be produced, "
        "and no engineering feasibility is claimed. Selectivity as defined here also depends on the target "
        "criterion (passage through the source footprint while it is on); other target definitions would "
        "give different values of S and were not tested.")
    D.p(
        "Several limitations bound these conclusions. Only one physical model was used; TIE-GCM [@richmond1992tiegcm,"
        "qian2014tiegcm] and WACCM-X [@liu2018waccmx] could not be run in this environment, so model-structural "
        "uncertainty is not sampled. The background is one quiet equinox state with constant drivers. Only two "
        "horizontal resolutions were compared, the fine-grid background had a shorter spin-up, and no transport "
        "budget was computed to separate physical from numerical diffusion; the agreement between grids is "
        "evidence of robustness to resolution, not of convergence. The source is an idealized neutral energy input "
        "of fixed shape and duration. The orbit population is synthetic, circular and uses a single ballistic "
        "coefficient, and power and deposition altitude were each sampled at two levels on the coarse grid only. "
        "Finally, the GITM response was checked against an empirical background and published model results, not "
        "against observations of an equivalent artificial perturbation, which do not exist.")

    D.h("5. Conclusions")
    D.p(
        "A compact 100 GW, 1 h neutral heat source in GITM produces a large local density increase that spreads "
        "over most of the globe within hours. Coupled to synthetic orbits, it gives 12 h target/non-target drag "
        f"selectivities of about {float(S['Sc_400']):.1f} at 400 km, {float(S['Sc_500']):.0f} at 500 km and "
        f"{float(S['Sc_300']):.0f} at 300 km, with most of the extra drag falling on non-target objects. Static "
        f"Gaussian patches overstate this selectivity by factors of {S['gf_lo_12_400']}–{S['gf_hi_12_400']} at 400 km "
        f"and {S['gf_lo_12_500']}–{S['gf_hi_12_500']} at 500 km when fitted to the model, and by "
        f"{S['src_lo_400']}–{S['src_hi_500']} when sized to the source. These results are robust to doubling the "
        "horizontal resolution. Any assessment of localized thermospheric heating for selective debris decay should "
        "therefore use self-consistent transport rather than prescribed density patches.")

    D.h("Declaration of competing interest")
    D.p("The author declares no known competing financial interests or personal relationships that could have "
        "appeared to influence the work reported in this paper.")
    D.h("Funding")
    D.p("This research did not receive any specific grant from funding agencies in the public, commercial, or "
        "not-for-profit sectors.")
    D.h("CRediT authorship contribution statement")
    D.p("T. Onishi: Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, "
        "Writing – original draft, Writing – review and editing, Visualization.")
    D.h("Data availability")
    D.p("Model configurations, the heating hook, analysis scripts, processed fields and all result tables are in "
        "https://github.com/bougtoir/thermosphere-debris-selective-decay. Raw GITM output (about 30 GB) is listed "
        "file-by-file with SHA-256 checksums in data/physical/GITM_RUN_MANIFEST.csv and is available from the "
        "author on request.")
    D.h("Declaration of generative AI and AI-assisted technologies in the manuscript preparation process")
    D.p("During the preparation of this work the author used an AI software assistant (Devin, Cognition AI) to "
        "implement and run the simulation and analysis code and to draft text. The author reviewed and edited the "
        "content as needed and takes full responsibility for the content of the published article.")

    D.h("References")
    for n, _, e in D.refs.listing():
        runs(D.d.add_paragraph(), f"[{n}] {e}")
        D.words += len(e.split()) + 1


# ---------------------------------------------------------------- outputs
def build(inline, v):
    refs = Refs()
    D = Doc(refs, inline)
    body(D, v)
    if not inline:
        D.h("Figure captions")
        for n in sorted(CAPTIONS):
            D.p(f"Fig. {n}. {CAPTIONS[n][1]}", count=False)
    assert D.fig_seen == sorted(D.fig_seen) == list(range(1, len(CAPTIONS) + 1)), D.fig_seen
    assert D.tab_seen == [1, 2, 3, 4], D.tab_seen
    return D


def tables_doc(v):
    d = Document()
    d.styles["Normal"].font.name = "Times New Roman"
    for n, (cap, df) in enumerate((("Configuration of the coarse- and fine-grid GITM experiments.", table1(v)),
                                   ("Twelve-hour drag selectivity from GITM and from static comparators.", table2(v)),
                                   ("Coarse- versus fine-grid sensitivity over 12 h.", table3(v)),
                                   ("Outcomes of the frozen predictions.", table4(v))), 1):
        runs(d.add_paragraph(), f"Table {n}. {cap}", bold=True)
        t = d.add_table(rows=1, cols=len(df.columns))
        t.style = "Table Grid"
        for i, c in enumerate(df.columns):
            runs(t.rows[0].cells[i].paragraphs[0], str(c), size=9, bold=True)
        for _, r in df.iterrows():
            cells = t.add_row().cells
            for i, c in enumerate(df.columns):
                runs(cells[i].paragraphs[0], str(r[c]), size=9)
        d.add_paragraph()
    d.save(os.path.join(OUT, "tables.docx"))


def figures_pptx():
    prs = Presentation()
    prs.slide_width, prs.slide_height = PInches(13.333), PInches(7.5)
    for n in sorted(CAPTIONS):
        s = prs.slides.add_slide(prs.slide_layouts[6])
        s.shapes.add_picture(os.path.join(FIG, CAPTIONS[n][0] + ".png"), PInches(0.4), PInches(0.3),
                             height=PInches(5.6))
        tb = s.shapes.add_textbox(PInches(0.4), PInches(6.0), PInches(12.5), PInches(1.4)).text_frame
        tb.word_wrap = True
        tb.text = f"Fig. {n}. " + re.sub(r"[\^_]\{([^}]*)\}", r"\1", CAPTIONS[n][1])
        for p in tb.paragraphs:
            for r in p.runs:
                r.font.size = PPt(11)
    prs.save(os.path.join(OUT, "figures.pptx"))


def cover_letter(v, words):
    d = Document()
    d.styles["Normal"].font.name = "Times New Roman"
    paras = (
        "Dear Editor,",
        f"Please consider the enclosed Research Paper, \"{TITLE}\", for publication in Acta Astronautica.",
        "Concepts that would accelerate the decay of selected debris objects by locally heating the thermosphere "
        "have so far been assessed with prescribed, static density patches. This paper tests that assumption with a "
        "physically self-consistent thermosphere model (GITM) coupled directly to an orbit propagator. It shows that "
        "post-heating transport limits the target/non-target drag selectivity to about "
        f"{float(v['Sc_400']):.1f} at 400 km and {float(v['Sc_500']):.0f} at 500 km over 12 h, that static patches "
        f"overstate it by factors of {v['gf_lo_12_400']} to {v['src_hi_500']} depending on altitude and patch "
        "definition, and that these results are "
        "robust to doubling the model resolution. Predictions were committed before the simulations were run and "
        "are scored in the paper, including those that failed.",
        "The results bear directly on the evaluation of non-contact debris remediation concepts and on the "
        "modelling standards such assessments should meet, which I believe makes Acta Astronautica the appropriate "
        "venue.",
        "An earlier, prescribed-patch version of this project was declined by Advances in Space Research "
        "(AISR-D-26-03405) for insufficient novelty and quantitative support. The present manuscript is a new study: "
        "the physical model, simulations, analysis and conclusions are all new, and the earlier patch model now "
        "serves only as a comparator.",
        f"The manuscript has about {words} words including references, five figures and four tables. It has not "
        "been published and is not under consideration elsewhere. The author declares no competing interests.",
        "Sincerely,", "T. Onishi", "bougtoir@gmail.com")
    for t in paras:
        d.add_paragraph(t)
    d.save(os.path.join(OUT, "cover_letter.docx"))


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
    v = collect()
    fill_captions(v)
    D = build(False, v)
    D.d.save(os.path.join(OUT, "manuscript.docx"))
    words = D.words
    assert words <= WORD_LIMIT, words
    build(True, v).d.save(os.path.join(OUT, "manuscript_review_inline.docx"))
    tables_doc(v)
    figures_pptx()
    hl = Document()
    hl.add_heading("Highlights", 1)
    for x in highlights(v):
        hl.add_paragraph(x, style="List Bullet")
    hl.save(os.path.join(OUT, "highlights.docx"))
    cover_letter(v, words)
    for n in sorted(CAPTIONS):
        shutil.copyfile(os.path.join(FIG, CAPTIONS[n][0] + ".tif"), os.path.join(OUT, "figures", f"Fig{n}.tif"))
    pd.DataFrame(V.rows).to_csv(os.path.join(ROOT, "results/manuscript_physical_values.csv"), index=False)
    pd.DataFrame([dict(number=n, citation_key=k, reference=e) for n, k, e in D.refs.listing()]).to_csv(
        os.path.join(ROOT, "results/manuscript_physical_citations.csv"), index=False)
    print(f"words (incl. refs, 300/figure-table): {words}; references: {len(D.refs.order)}; values: {len(V.rows)}")


if __name__ == "__main__":
    main()
