# Independent Hostile Review — ASR submission (Gate 1)

Date: 2026-10-17. Base: PR #4 head `d2d2b12` (devin/1790845369-reentry-flag-reset), clean tree.
Scope: full manuscript text generator (`scripts/build_manuscript.py`), all result CSVs, propagator, perturbation, energy, classification, Sobol and QC code, supplement. Prior Devin audits were treated as claims to re-verify, not as evidence.

Severity scale: CRITICAL / MAJOR / MINOR / COSMETIC.

## Reviewer A — thermospheric physics / neutral-plasma transport

| ID | Severity | Location | Issue | Evidence | Falsification test | Remedy | Status |
|----|----------|----------|-------|----------|--------------------|--------|--------|
| A1 | MINOR | 2.1 | "~15%" density uncertainty is a typed literal | config/default.yaml `background_uncertainty: 0.15` matches, but text is not injected | change config -> text stays | inject from config | FIXED |
| A2 | MINOR | 3.5 | "460-730 m/s" TAD speeds typed | matches bruinsma2007tad note; CITED_EXTERNAL_VALUE, acceptable but brittle | — | keep (cited value) | JUSTIFIED |
| A3 | MINOR | 2.1 | lookup averages ln-rho over a 5x4x4 lat/lon/LST grid at a single June solstice epoch; regime = f107/ap labels | src/atmosphere/lookup.py | — | acceptable climatology; limitation already disclosed | JUSTIFIED |
| A4 | MINOR | models | amplitude-conserving diffusion `amp *= sigma0^2/sigma(t)^2` conserves horizontal integrated delta but ignores vertical dilution | models.py:75 | — | surrogate; disclosed as limitation | JUSTIFIED |

## Reviewer B — orbital mechanics / propagation

| ID | Severity | Location | Issue | Evidence | Falsification test | Remedy | Status |
|----|----------|----------|-------|----------|--------------------|--------|--------|
| B1 | MAJOR | 2.2, 5 | "0.12%" fast-vs-Cowell agreement is stale | phase2_validation.csv `fastprop_vs_cowell_250km` = 6.23e-4 = **0.062%** after the corotation fix; prose still says 0.12% | compare text vs CSV | inject from phase2_validation.csv | FIXED |
| B2 | MINOR | 4.3 | "29 encounters" for pair E is a typed literal | phase7_selectivity.csv localized_tracking/E protected_encounters = 29 (matches) | change CSV -> text stays | inject | FIXED |
| B3 | MINOR | fastprop | orbit-averaged drag uses single-radius evaluation for e<0.02; cases are near-circular | fastprop.py:97 | — | documented assumption | JUSTIFIED |
| B4 | MINOR | 2.2 | right-censored lifetimes handled correctly (n_censored injected, inf excluded) | build_manuscript.py:171 | — | none needed | VERIFIED |

## Reviewer C — numerics / uncertainty / sensitivity

| ID | Severity | Location | Issue | Evidence | Falsification test | Remedy | Status |
|----|----------|----------|-------|----------|--------------------|--------|--------|
| C1 | MAJOR | 3.8 | "slope of 1.01 and R^2 = 0.9995" are typed literals | phase11_scaling.py computes slope/R2 but writes them only to results/full_rebuild.log, not to any CSV | perturb input -> text stays | write phase11_scaling_fit.csv, inject | FIXED |
| C2 | MINOR | 3.8 | Pi mean 1.062 +- 0.260 inflated by 7 low-B (B<=10) outliers at 350-400 km (max 4.29); median is 1.022 | phase11_scaling.csv rows with Pi>1.5 | — | report median/IQR alongside mean, note outlier regime (induced-drift into/out of patch at very low B) | FIXED |
| C3 | MINOR | 2.4 | "six patch sigmas" typed literal | exposure_class.py N_SIGMA_NO_ENCOUNTER = 6.0 (matches) | — | inject constant | FIXED |
| C4 | MINOR | 2.4 | "2000-object factorial population" typed literal | phase04 n = 2000 (matches) | — | inject from population row count | FIXED |
| C5 | MINOR | Sobol | indices reported at converged rung with ordering-violation count injected — verified converged | sobol_convergence.csv ladder present | — | none needed | VERIFIED |
| C6 | MINOR | 3.7 | "all small compared with natural drag over the same window" is false for the 750 km control: natural 2h drag at 750 km ~1e-4 m/s << reported 9.6e-3 m/s extra | phase10_negative_controls.csv, density_lookup | recompute natural dv at 750 km | reword to "small in absolute terms" and drop the natural-drag comparison for that control | FIXED |

## Reviewer D — debris-remediation feasibility / safety

| ID | Severity | Location | Issue | Evidence | Falsification test | Remedy | Status |
|----|----------|----------|-------|----------|--------------------|--------|--------|
| D1 | MINOR | 4.4 | "464 GW"/"95 GW" typed literals | match knipp2004heating note (CITED_EXTERNAL_VALUE) | — | keep | JUSTIFIED |
| D2 | MINOR | energy audit | column-expansion bound uses isothermal-column exact eps=q/(1-q) and a mass/T-weighted integral; it is a stated thermodynamic lower bound, honest | audit_energy.py | — | none needed | VERIFIED |
| D3 | MINOR | 3.9 | "~7.7 km/s" transit speed literal | physically correct at ~400 km (v=7.67 km/s) | — | acceptable rounding, or compute; kept | JUSTIFIED |

## Reviewer E — ASR editor / presentation

| ID | Severity | Location | Issue | Evidence | Falsification test | Remedy | Status |
|----|----------|----------|-------|----------|--------------------|--------|--------|
| E1 | MAJOR | whole text | Table and figure numbers are not in citation order. Tables appear as 1,2,6,3,7,4,5,8 (Table 6 cited in 3.2 before Tables 3-5). Figures appear as 1,2,3,7,6,4,5 (Fig 7 cited in 3.4 before Figs 4-6). Supplement: Fig S4 cited (3.5) before S2,S3,S1 | content order in build_manuscript.py | read rendered docx | renumber by first-appearance order at render time and fix in-text citations | FIXED |
| E2 | MINOR | title block | "[Authors] T. Onishi et al." implies multiple authors; the paper is single-author, and "we" is used in the abstract | title paragraph + abstract | — | "T. Onishi"; first person singular where a pronoun is needed | FIXED |
| E3 | MINOR | Data/code availability | fine as is | — | — | none | VERIFIED |
| E4 | MINOR | references | 18 entries, DOIs recorded in references_verified.csv; only cited keys enter the list (Vancouver order) | build machinery | — | none needed | VERIFIED |

## Editorial verdict

MAJOR REVISION (mechanical, not scientific): the science and provenance machinery are sound; the defects are (i) one stale number vs current CSV, (ii) non-sequential figure/table numbering, (iii) several typed literals that should be injected, and (iv) one over-stated comparison in 3.7. All are fixable without new analysis. No fabricated content found.

No CRITICAL findings. Claims that survived scrutiny: corrected NRLMSISE-00 units (x1000 verified, magnitude test vs published values), gap decomposition closure, exposure classification with undefined ratios, column-expansion energy bound (exact eps=q/(1-q)), censored lifetimes, Sobol convergence ladder, dimensionless-collapse claim correctly labelled internal-consistency.
