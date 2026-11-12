# Acta final delta — figure export audit (Gate 11)

Source: `scripts/physical_manuscript_figures.py` (`make physical-figures`). Each figure is drawn by matplotlib from
canonical CSV/NPZ data at 600 dpi, saved as PNG preview (`results/figures/physical/*.png`) and TIFF, then re-saved as
8-bit RGB (alpha flattened onto white) with lossless LZW compression. `build_physical_manuscript.py` copies the TIFFs
to `manuscript/physical/figures/Fig1–5.tif` and places the PNGs in the editable `figures.pptx`. No screenshots.

Acta guide (archived 2026-11-10, `data/raw/journal/acta_astronautica_guide_20261110.txt`): TIFF ≥ 300 dpi for
halftones, ≥ 500 dpi for combined line/halftone, ≥ 1000 dpi for pure line art; fonts Arial, Courier, Times New Roman,
Symbol or similar. The figures are line/colour-fill combinations; 600 dpi meets the 500 dpi combination requirement.
Text uses Liberation Sans (metric-compatible with Arial; Arial is not installed in the build environment) and
DejaVu Sans for mathtext symbols, rasterized into the TIFF.

| File | Pixels | dpi | Print size (mm) | MB | Mode | Compression | SHA-256 |
|---|---|---:|---|---:|---|---|---|
| Fig1.tif | 4381×2829 | 600 | 185×120 | 0.84 | RGB | tiff_lzw | `b30d0b10c755976c19bf295229a4e34173ada5462e4e9918109d8402e3c58e23` |
| Fig2.tif | 4509×1629 | 600 | 191×69 | 0.49 | RGB | tiff_lzw | `89944dcdb8b643305a80dae5359c127630685f7b4117ab725de8f97c3fdc7191` |
| Fig3.tif | 4509×2829 | 600 | 191×120 | 0.79 | RGB | tiff_lzw | `0cc0d2585aff5aaefd51055dfb088c5000666999f002ed212e13fbf59c901af6` |
| Fig4.tif | 4509×1749 | 600 | 191×74 | 0.47 | RGB | tiff_lzw | `fd1254419b7368a98e2cd78e105419710384c90cf05a5b4f915a44454e77d610` |
| Fig5.tif | 2229×1749 | 600 | 94×74 | 0.24 | RGB | tiff_lzw | `a264d3b11bc8a5d1f2b2a030d8b4f2f22d9e40467846f53d684cf3a40eece6cd` |

Fig. 1–4 are double-column width, Fig. 5 single-column. Smallest text at print size is the legend (6.5 pt).

## Visual QC (PNG previews inspected)

- Fig. 1: PASS — common BoundaryNorm on all panels; neutral |Δρ/ρ| ≤ 0.01 white, negative bin blue, six positive red bins; source cross at 45°N 0°E; lon −180…180, lat −90…90; titles t − t_on with mathtext subscript; colour-bar label 'Δρ/ρ at 400 km (dimensionless)'; no text clipped
- Fig. 2: PASS — three panels with units (kg m⁻¹, fraction, km); solid/dashed/dotted = coarse/fine/remapped; legend readable; no clipping (unchanged except font/RGB/mathtext label)
- Fig. 3: PASS — full 0–12 h range retained; grey shading only in the two 300 km panels (first 30 min); log ordinate top row; 400/500 km panels unobstructed
- Fig. 4: PASS — log ordinate; 3 panels × 3 altitudes × (GITM, peak-matched, source-centred); values identical to physical_g4t_gaussian_matching.csv 12 h rows
- Fig. 5: PASS — markers only at 300/400/500 km (distinct shapes), dotted lines labelled 'visual guide only', x ticks at the three altitudes; y = coarse-grid 12 h S

## Changes relative to baseline 23add38

| Fig. | Change | Data changed? |
|---|---|---|
| 1 | Map now at exactly 400 km (log-linear altitude interpolation, the same `alt_interp` used by G3R and the manuscript's 400 km numbers) instead of the nearest native level (390.6 km, maximum 1.60) | No — same NPZ, same normalization ρ_p/ρ_c − 1 |
| 1 | Colour map corrected: baseline `RdBu_r` with 8 bins drew the neutral −0.01…0.01 bin in mid-blue, so undisturbed regions read as negative anomalies; now neutral = white, the single negative bin blue, positive bins red | No |
| 1 | Saturation check: maximum 1.94 < upper bound 2.0; minimum −0.030 > lower bound −0.05; 0 of 4 × 5184 cells out of range. Caption states that no cell is saturated (the suggested "values exceeding its upper bound are saturated" would be false). Ranges in `results/tables/physical_fig1_panel_ranges.csv`. The manuscript's 204% peak is the coarse-grid G3 value; the fine-grid G3 time series (linear-in-altitude interpolation of ρ from the raw output) peaks at 189%, and the log-linear interpolation used by Fig. 1/G3R gives 194% at 50 min — a 2.5% interpolation-method difference, below the 7% grid difference reported for PR8a | — |
| 3 | Grey shading of the sign-undefined interval at 300 km; caption states the rule | No |
| 5 | `o-` replaced by markers + dotted guides labelled "visual guide only" | No |
| all | RGBA → RGB TIFF; Arial-compatible font; mathtext for Δ, ρ, subscripts | No |

Fig. 3 rule: no formal criterion had been defined before (the baseline caption said "~30 min" without a rule). The
shading marks where the ratio of group means has no defined sign — either group mean ≤ 0 in any plotted run. This
is a property of the definition, not a tuned threshold; it gives 30 min at 300 km and only the first output (3 s) at
400/500 km (`results/tables/physical_fig3_illconditioned_interval.csv`). Data inside and outside the interval are
plotted unchanged; non-positive ratios cannot appear on the log axis, as the caption says.
