# Acta Astronautica final delta — baseline (Gate 1)

Recorded before any delta edit. Branch `devin/1794047620-physical-model-rebuild`; baseline HEAD `23add38e72a7950816baf6d92aa3531ec13d5c30`
(the previously reported `1aa34f1` is an ancestor, not HEAD). Immutable pre-rebuild baseline: `main@ac67802`.
PR: https://github.com/bougtoir/thermosphere-debris-selective-decay/pull/9 (open, not merged).

## Canonical submission artifacts at baseline HEAD

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `manuscript/physical/manuscript.docx` | 52,686 | `00f33094f1a1c5ebf951d60c00b3c6a6598bdbfd15dde54025a5573db8e6739b` |
| `manuscript/physical/manuscript_review_inline.docx` | 1,241,265 | `856871d5499d620b69c30cf48b7bde7c5a226c83791e60cfd405b77eee0a9b49` |
| `manuscript/physical/tables.docx` | 39,630 | `28244bbba274e52b2b4fa5b4cd069ebd2f4854334565fd4078e2046255de7390` |
| `manuscript/physical/figures.pptx` | 1,221,814 | `8b0252da714595c7aba8d3f6a9ab9448a5e40e132a3f79658fc55330abf3bc36` |
| `manuscript/physical/figures/Fig1.tif` | 1,485,950 | `d8f25ce329162457dbbdfb533ef3c4942bc0b8f3cc513bf27b8d9a0010baa0a5` |
| `manuscript/physical/figures/Fig2.tif` | 652,540 | `7e5ab3e1742e8db78d2b26fbcf607f2a56e7f6f21b4eb1c3266867a70cce9e3d` |
| `manuscript/physical/figures/Fig3.tif` | 1,017,594 | `f3c542195ba43640991b60af13eae967d281fed79024ba79d6a82c4d73ca8cdb` |
| `manuscript/physical/figures/Fig4.tif` | 668,686 | `dc63b2abee86dd53e13e6a4e3718540d5ba9123477680de3412fa12bf900874e` |
| `manuscript/physical/figures/Fig5.tif` | 335,410 | `89bd50c2abd207887e8007985967fea0cd5c50be22a00cb1dff25dd56df39adf` |
| `manuscript/physical/highlights.docx` | 36,843 | `720e3d9a5631b88270f3c352034cd7828c023c86ef727b50c4fefccdf2bba50d` |
| `manuscript/physical/cover_letter.docx` | 37,524 | `23813ca8d60ce92c6da610dd3d9f07ef08576b912560a53953da8b118b9205ad` |
| `FINAL_HANDOFF.txt` | 4,243 | `e8ace02be9e17111a19a0913728c621e82f3b1001db24a528821e817900e1b1a` |
| `results/manuscript_physical_values.csv` | 14,439 | `b849cff13f16adc48848a75f3f7d9ecbbbf1b287acfb366ef47e42ab958d7fd6` |
| `results/manuscript_physical_citations.csv` | 5,540 | `a2d90f9f268e9407dd1f6f2f2d7d82afe8369fc3862504da739fc959c19ed2e4` |
| `results/qc_physical_manuscript.csv` | 1,315 | `5d1651e918e2bad2d234d55ef3ad93d374f3d0fee2394c422a64024e360b1860` |
| `docs/SCIENTIFIC_CONTRIBUTION_GATE.md` | 12,986 | `888673bd90a7a72f7e87385d052b9f05c7257cee78999e84e3a87466de4d0f4a` |
| `docs/NOVELTY_AND_EVIDENCE_GATE.md` | 2,202 | `e40a1a018de04e779be3834b93698fa8386dc28fb600a881e751aa4f07aae39c` |
| `docs/G7_HOSTILE_REVIEW_PHYSICAL.md` | 7,053 | `8616615caebf1b41b786a020bf957aeb185d797de5f4d7124bd990524529ca1d` |

## Figure and document sources

| Output | Source |
|---|---|
| Fig. 1–5 (PNG/TIFF in `results/figures/physical/`, copied to `manuscript/physical/figures/`) | `scripts/physical_manuscript_figures.py` |
| Fig. 1 data | `data/physical/processed/p11_z300_fine12_slices.npz` (git-ignored) |
| Fig. 2 data | `results/tables/physical_g3r_spread_metrics.csv` |
| Fig. 3 data | `results/tables/physical_g4t_selectivity_evolution.csv` |
| Fig. 4 data | `results/tables/physical_g4t_gaussian_matching.csv` |
| Fig. 5 data | `results/tables/physical_g4t_selectivity_evolution.csv` (12 h rows, coarse) |
| All DOCX/PPTX, value and citation ledgers | `scripts/build_physical_manuscript.py` |
| Mechanical QC | `scripts/qc_physical_manuscript.py` → `results/qc_physical_manuscript.csv` |
| Pipeline | `make physical-qc` (bootstrap → figures → manuscript → QC) |

## QC status at baseline

22 PASS / 0 FAIL of 22 mechanical checks; `python3 -m pytest -q` 34 passed.

## Files requiring revision (identified at baseline)

| File | Reason |
|---|---|
| `scripts/physical_manuscript_figures.py` | Fig. 1 shows the nearest native level (390.6 km), not 400 km, and its colour map draws the neutral ±0.01 bin in blue; Fig. 5 joins three discrete altitudes with solid lines; Fig. 3 has no marker of the sign-undefined 300 km interval; TIFFs are RGBA; non-math Unicode labels |
| `scripts/build_physical_manuscript.py` | causal "transport" wording (title, abstract, 2.5, 3.3, 4, 5, cover letter); "pre-registered" in 3.6; Data availability claims processed fields are on GitHub (they are git-ignored) and states raw size 30 GB (manifest total 54 GB); cover letter cites the ASR decision; equations as plain runs, not OMML; Heading styles use theme fonts (Calibri Light, blue); captions 12 pt; affiliation placeholder |
| `scripts/qc_physical_manuscript.py` | no checks for terminology, fonts, colour, caption size, OMML, grid, tracked changes, placeholders, data statement |
| `FINAL_HANDOFF.txt`, new `docs/ACTA_*.md` | to be rewritten / created |

Canonical scientific CSVs (`results/tables/physical_g*.csv`, `results/physical_model_vs_prescribed_patch.csv`,
`results/grid_sensitivity_metrics*.csv`), raw runs and processed NPZ files are not to be modified.
