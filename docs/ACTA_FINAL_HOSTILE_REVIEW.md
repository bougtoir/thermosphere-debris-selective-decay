# Acta final delta — hostile review (Gate 13)

Reviewer stance: find reasons to reject. Reviewed: `manuscript/physical/manuscript.docx` after the delta edits,
Tables 1–4, Fig. 1–5, highlights, cover letter, and the canonical CSVs. Severity: **major** = would justify rejection
if unaddressed; **minor** = revision; **noted** = acceptable as stated.

## 1. Thermosphere physics

| Issue | Severity | Assessment |
|---|---|---|
| 100 GW for 1 h is far beyond any natural localized input or plausible artificial source; is the regime meaningful? | noted | The manuscript states it is an idealized source, compares it with storm and substorm inputs (Liu 2015: 50 GW), adds a 10 GW case, and claims no feasibility. The 400 km response (+204%) is extreme; the paper says so. Results are explicitly conditional on this regime. |
| Single quiet equinox background, constant drivers, minimum Tn 118 K failing the 150 K criterion near 100–107 km | minor | Disclosed in §2.2 and limitations. Impact on 300–500 km not quantified beyond the MSIS comparison; a reviewer may ask for a second background. Cannot be fixed without new runs; acceptable as limitation. |
| "Spreading" is attributed to winds and waves | noted | Now stated as consistent with known dynamics, not demonstrated by a budget; §4 says no transport budget was computed. |
| Neutral heating only; no ion-neutral or composition-specific deposition | noted | Stated as idealized neutral energy input. |

## 2. Numerical simulation and discretization

| Issue | Severity | Assessment |
|---|---|---|
| Two resolutions cannot establish convergence; fine grid had 6 h spin-up vs 24 h | minor | Wording now "robustness to resolution, not formal convergence"; spin-up confounder stated in §2.6 and limitations. The 12 h S agree within 1.1%, but this could partly reflect the shared source width (σh ≈ 1000 km is resolved by 1.7 vs 3.4 cells). A third grid would strengthen it; not required for the calibrated claim. |
| Source barely resolved on the coarse grid | noted | Realized power and width (996 km) identical on both grids (Table 1). |
| Negative anomalies and late centroid change with resolution | noted | Reported, not used for any claim. |
| Interpolation method for 400 km (linear vs log-linear) differs by ≈ 2.5% at the fine-grid peak | minor | Below the grid difference; each number's source is traceable. Not a claim-level issue. |

## 3. Orbital dynamics

| Issue | Severity | Assessment |
|---|---|---|
| Synthetic circular orbits, single B, J2 secular propagation without feedback of drag on the orbit | noted | Δv is first-order and tiny (3.7% of natural drag over 12 h); neglecting feedback is justified at this magnitude. Stated. |
| Target definition (pass within σh while on) drives S; other definitions would change S | minor | Stated in §4. A reviewer may ask for a sensitivity; it is post-processing only but was not requested in this delta and would add a new estimand. Left as limitation. |
| Bootstrap intervals resample objects only | noted | Text says the orbit sample is not the limiting uncertainty; intervals are not presented as model uncertainty. |
| Selectivity vs non-target share | noted | Defined separately (Eq. 2 and §3.2); highlights use the share for "84% of extra drag" and S for the ratio. Correct. |
| Static comparator omits winds while GITM includes them | noted | Effect on S ≤ 0.33% (semantic audit); irrelevant to 1.5–8.5× factors. |

## 4. Novelty and citation ecology

| Issue | Severity | Assessment |
|---|---|---|
| Density response to localized heating is well known (Deng, Gardner, Liu, Lühr, Carlson) | noted | Introduction now states explicitly that this physics is established and not claimed; the contribution is the target/non-target drag division and the quantified overstatement by static patches. |
| Is the static-patch assumption a straw man? | minor | The patch form is the one used in earlier screening (including this author's own prior work, not cited as a publication). A reviewer could ask for published examples of static-patch screening; the manuscript cites ionospheric-drag and laser concepts [1–5] but no published static-patch selectivity study, because none was found in the 38-study Crossref search. Phrase "Screening studies that prescribe …" could be challenged; acceptable but exposed. |
| Single model | noted | Stated; TIE-GCM/WACCM-X could not be run. |

## 5. Acta Astronautica fit and presentation

| Issue | Severity | Assessment |
|---|---|---|
| Fit | noted | Debris remediation and space-environment modelling are within scope; cover letter connects to that readership without claiming feasibility. |
| Format | noted | TNR 12 pt body, 10 pt captions, black text, OMML Eq. (1)–(2), no grid snapping, numbered citations in order, 23 references, 5 TIFFs at 600 dpi, highlights ≤ 85 characters, word count 7232 incl. 300 per display item. |
| Data availability | **major until resolved** | Processed fields are not on GitHub. The statement now says so truthfully and points to the Zenodo record; the record must be **published** (DOI active) before submission, otherwise the statement promises an inaccessible archive. |
| Affiliation detail, ORCID | author action | Not a scientific issue. |

## Verdict

No remaining scientific or numerical defect invalidates the calibrated conclusions: (i) 12 h selectivity ≈ 1.5 at
400 km, ≈ 2 at 500 km, ≈ 1 at 300 km; (ii) most extra drag reaches non-targets; (iii) static patches overstate S by
1.5–1.7× (400 km) and 2.8–3.6× (500 km) when fitted to GITM, 4.7–8.5× when source-sized; (iv) power/altitude
contrasts are two-level, coarse-grid observations. Expected reviewer requests (second background, third grid,
alternative target definitions, published static-patch precedent) are limitations, not errors. The one blocking item is
public activation of the processed-data archive.
