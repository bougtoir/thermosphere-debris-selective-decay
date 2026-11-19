# Final prior-literature claim delta

Date: 2026-11-19 (UTC). Scope: wording that described static Gaussian density patches as an established
practice in published selective-debris-decay studies. No new simulation, analysis or literature search was run.

## Verdict: corrected

The verified literature base does not support the claim. The static patch is now described as an idealized
screening comparator; the GITM-versus-static-patch numbers are unchanged.

## Evidence

| Approach | Published, verified example in `references/PRIOR_KNOWLEDGE_VERIFIED.csv` (38 Crossref records) | Use for selective debris decay |
|---|---|---|
| 1. Prescribed static Gaussian density patch | none | none found. Only this author's own unpublished, rejected study (repository baseline `main@ac67802`) used it (`docs/PRIOR_KNOWLEDGE_MATRIX.md` row 6: "the baseline asserted this only for prescribed fields") |
| 2. Other prescribed stationary perturbations | none | none found |
| 3. Empirical density fields (NRLMSISE-00 [picone2002msis]; storm-time drag studies [oliveira2019drag, fang2022starlink, baruah2024starlink]) | yes | natural storms and orbit decay; no target/non-target selectivity |
| 4. Physics-based dynamic models (GITM [ridley2006gitm, deng2008nonhydro, liu2015substorm]; TIE-GCM [richmond1992tiegcm]; WACCM-X [liu2018waccmx]; TAD studies [gardner2010tad]) | yes | thermospheric response only; no debris selectivity |

Debris-removal literature cited [serfontein2021dragaug, rhatigan2020deorbit, schall1991laser, rubenchik2010laser,
smith2020ionodrag] acts on the object or uses ionospheric drag; `PRIOR_KNOWLEDGE_MATRIX.md` row 13 notes "none uses
atmospheric heating", and row 14 classes debris removal by modifying the thermosphere as UNKNOWN ("no peer-reviewed
predecessor found … absence in 40-hit pages is not proof of absence"). Hence:

- "Proposals … assume" (abstract) and "Proposals … are usually screened with prescribed, static density patches" (cover
  letter) assert a body of published proposals and a screening practice that the verified record does not contain.
- "Screening studies that prescribe a static Gaussian density patch" (introduction) and "the form used in earlier
  screening" (§2.5) refer to published screening studies that were not found.
- The absence statements added below are qualified as the result of a targeted search, matching the matrix caveat.

## Original → revised wording

**Manuscript — Abstract**

Original:

> Proposals to accelerate the decay of selected debris objects by locally heating the thermosphere assume that the resulting density enhancement stays where it was deposited.
> I test that assumption with a physically self-consistent model.
> Under the tested conditions, the dynamically evolving GITM density field therefore yields much lower cumulative drag selectivity than prescribed static density patches imply.

Revised:

> Accelerating the decay of selected debris objects by locally heating the thermosphere would require the resulting density enhancement to stay near where it was deposited.
> I test whether it does with a physically self-consistent model.
> Under the tested conditions, the dynamically evolving GITM density field therefore yields much lower cumulative drag selectivity than idealized, prescribed static density patches imply.

**Manuscript — Introduction, 3rd paragraph**

Original:

> Screening studies that prescribe a static Gaussian density patch around the source implicitly assume that the perturbation stays put, which can inflate the apparent selectivity.
> Here I replace the prescribed patch with a self-consistent general circulation model, the Global Ionosphere–Thermosphere Model (GITM) [18], couple its paired heated and control fields directly to an orbit propagator, and ask three questions: (i) how selective the cumulative drag is over 12 h; (ii) by how much static patches overstate it; and (iii) whether the answer survives a change of model resolution.

Revised:

> An idealized screening approach that prescribes a static Gaussian density patch around the source assumes that the perturbation stays localized, which can inflate the apparent selectivity.
> A targeted literature search found no published study that evaluates selective debris decay in this way, so the static patch is used here as an idealized comparator, not as a representation of prior work.
> Here I compare such patches with a self-consistent general circulation model, the Global Ionosphere–Thermosphere Model (GITM) [18], couple its paired heated and control fields directly to an orbit propagator, and ask three questions: (i) how selective the cumulative drag is over 12 h; (ii) by how much static patches overstate it; and (iii) whether the answer survives a change of model resolution.

**Manuscript — Methods §2.5 Static comparators**

Original:

> To compare the evolving GITM perturbation with the prescribed-field assumption, the same orbits were also flown through static Gaussian patches imposed on the GITM control atmosphere.
> The source-centred patch, the form used in earlier screening, has the same amplitude and window but is centred on the source with σ = 1000 km.

Revised:

> To compare the evolving GITM perturbation with a prescribed static field, the same orbits were also flown through static Gaussian patches imposed on the GITM control atmosphere.
> The source-centred patch, the simplest idealized screening form, has the same amplitude and window but is centred on the source with σ = 1000 km.

**Cover letter — 2nd paragraph**

Original:

> Proposals to accelerate the decay of selected debris objects by locally heating the thermosphere are usually screened with prescribed, static density patches.

Revised:

> The simplest way to screen the idea of accelerating the decay of selected debris objects by locally heating the thermosphere is to prescribe a static density patch around the source.
> A targeted literature search found no published study that evaluates selective debris decay with a physics-based thermosphere model.

Also changed: the cover-letter word count (7260 → 7296), which is computed by the builder.

Not changed: highlights ("Static Gaussian patches overstate selectivity 1.5–3.6×" states a model contrast, not a literature
claim); Discussion and Conclusions (they compare self-consistent and prescribed fields under the same forcing and recommend
self-consistent fields for future assessment; no claim about published practice); "What has not been established …"
(supported by matrix row 6). No sentence claims a first study.

## Novelty claim after the change

The contribution remains a newly quantified model-based contrast: target/non-target cumulative drag selectivity from a
dynamically evolving GITM response versus prescribed static density fields under matched orbits. The manuscript does not
claim to demonstrate an error in a published method.

## Files modified

- `scripts/build_physical_manuscript.py` (`body()` abstract, introduction and §2.5; `cover_letter()`)
- `manuscript/physical/manuscript.docx`, `manuscript_review_inline.docx`, `cover_letter.docx` (regenerated)
- `results/qc_physical_manuscript.csv` (word count)
- `docs/ACTA_FINAL_HOSTILE_REVIEW.md` (straw-man row updated)

Not regenerated: figures, TIFFs, tables, highlights, PPTX (byte-identical to the previous commit).

## Numerical results

`results/manuscript_physical_values.csv` (164 values) is byte-identical before and after. Manuscript QC 34/34, semantic
checks 325/325, pytest 34 passed. Data availability text and DOI unchanged.
