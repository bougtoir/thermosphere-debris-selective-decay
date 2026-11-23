# JSSE hostile pre-submission review

Reviewer stance: a sceptical JSSE handling editor plus two referees (space-safety engineer; thermosphere modeller),
reading `manuscript/JSSE/manuscript.docx` as built at the head of the JSSE branch. Each finding states the problem,
the evidence, and the disposition in this branch. Priorities: **P0** mandatory before submission; **P1** high;
**P2** medium; **P3** optional.

## 1. Novelty, focus, logic, methods, consistency of results and conclusions

| # | Finding | Priority | Disposition |
|---|---|---|---|
| 1.1 | "It is obvious that heat spreads; what is new?" The thermospheric response is established physics. | P1 | Addressed in text: response "is established physics and is not claimed as new"; contribution is the quantified division of extra drag between targets and non-targets and the static-vs-self-consistent factor, framed as a screening requirement (§1 ¶4, §4.3). Residual desk risk accepted. |
| 1.2 | Physics-heavy for JSSE; editor may redirect to a geophysics journal. | P1 | Framing rebuilt around non-target exposure (title, abstract, §1 ¶1–2, §4.1–4.4, cover letter). Cannot be removed entirely without deleting the evidence. |
| 1.3 | Environment-directed remediation is speculative; is the question worth asking? | P2 | Stated as "speculative" (§1 ¶1); the point is that if such concepts are screened, non-target exposure must be part of the screen. No feasibility claim. |
| 1.4 | Results vs conclusions: conclusions generalise beyond one configuration? | P1 | §4.3 now says "in this experiment the static representation overstated ..."; requirements are "on the assessment, not conclusions about any particular concept"; conclusions keep "for space-safety screening ... should be assessed" as a recommendation, with limits stated in §4.5. |
| 1.5 | "Selectivity" vs "exposure" vocabulary could confuse safety readers. | P2 | S and the aggregate share are defined separately (Eqs. (2)–(3)), and §2.4 explains that the share depends on the sample. |
| 1.6 | The 12 h window is 11 h after onset; text says "12 h" and "11 h after onset" in places. | P3 | Consistent with Methods ("each for 12 h with heating from 1 h to 2 h") and Fig. 4 caption; left as is. |

## 2. Statistical design and independence

| # | Finding | Priority | Disposition |
|---|---|---|---|
| 2.1 | One simulation per configuration; bootstrap over objects treats objects as independent although they share one atmosphere. | P1 | Added: intervals "are conditional on the single simulated atmosphere and exclude model, background and forcing uncertainty" (§3.2). No claim of population-level inference. |
| 2.2 | 28 of 256 objects are targets at 400 km; S for targets rests on a small group. | P2 | Bootstrap CI 1.43–1.59 reported; target count stated in §2.4. |
| 2.3 | Aggregate share depends on target fraction; easy to misread. | P0 (resolved) | Eq. (3) and explicit statements in §2.4, §3.2, §4.4, abstract, highlights, cover letter; QC enforces "synthetic sample" qualifier on every share percentage. |
| 2.4 | Power/altitude dependence from two levels each, coarse grid only. | P1 | Stated as "two-level contrasts ... do not define a scaling law" (§3.5) and in §4.5. |
| 2.5 | Frozen predictions: were thresholds moved? | P2 | Committed before heated output; scorecard includes 5 falsified and 2 outside-range outcomes; "not registered with an external registry" stated. |

## 3. Figure and table support; over-selection

| # | Finding | Priority | Disposition |
|---|---|---|---|
| 3.1 | Selective display? | P2 | All five figures and four tables of the Acta-final version retained; fine-grid curves shown with coarse in Figs. 2–4; resolution-sensitive diagnostics (negative perturbation, late centroid) are reported as such (§3.4). |
| 3.2 | Fig. 3 bottom panel (non-target share) could be read as a population statistic. | P0 (resolved) | Caption now says "non-target share of the total extra Δv of the synthetic sample (bottom; Eq. (3))". |
| 3.3 | Fig. 1 colour scale saturation. | P3 | Caption reports plotted range inside colour range (no saturation). |
| 3.4 | Static patches could be read as upper bounds or alternative physics. | P1 | Fig. 4 caption: "diagnostic comparators ... not alternative physical solutions or upper bounds"; §4.2 heading "Static patches as a modelling representation". |
| 3.5 | Tables use vertical rules (JSSE guide asks to avoid them). | P0 (resolved) | Horizontal rules only in manuscript and tables.docx; QC check added. |
| 3.6 | TIFF resolution / format. | P2 | 600 dpi RGB LZW TIFF with opaque white background (QC). |
| 3.7 | Standalone `tables.docx` lacked the table notes (units, % baselines); `figures.pptx` cut off the right panels of Figs. 2 and 4 (found by Devin Review). | P0 (resolved) | JSSE builder now writes captions and notes into `tables.docx` and scales each figure to fit the slide; two QC checks added. |

## 4. Reproducibility, provenance, checksums, environment

| # | Finding | Priority | Disposition |
|---|---|---|---|
| 4.1 | Can a reader regenerate numbers, figures and text from public material? | P0 (resolved) | Fresh clone of the pushed JSSE branch from GitHub + the five Zenodo NPZ files only → `make jsse-qc PY=python` → 91/91 PASS on the final head 7fba0c6; value ledger and citations byte-identical; manuscript text identical. Regenerated TIFF/PNG differ from the committed files only by anti-aliasing (0.27% of pixels in Fig. 3, visually identical). |
| 4.2 | Processed data integrity. | P0 (resolved) | Five NPZ files re-downloaded from Zenodo 10.5281/zenodo.24101202: SHA-256 = `PROCESSED_MANIFEST.csv` and MD5 = Zenodo checksums (`data/physical/zenodo_retrieval/ZENODO_RETRIEVAL_LEDGER.csv`). |
| 4.3 | Raw GITM provenance. | P1 (resolved) | Private release restored; 22/22 parts SHA-256 OK; 23,945 run files, 1,587 build-tree files and 9,567 symlinks verified with 0 mismatches (`data/physical/raw_restore_20261123/RAW_RESTORE_LEDGER.json`). This is log/checksum verification of existing execution, **not** an independent re-simulation (no GITM rerun, by instruction). |
| 4.4 | Data statement cites tag `gitm-orbit-selectivity-v1.1`, which predates the JSSE builder. | P2 | Statement names the builder file; analysis code and values are unchanged since v1.1. After merge, the author may add a new tag (do not move existing tags). |
| 4.5 | Environment: `python-docx`/`python-pptx` were missing on the VM until `pip install -r requirements.txt`. | P3 | Pinned in `requirements.txt`; blueprint already runs it. |

## 5. Claim strength vs evidence

| # | Finding | Priority | Disposition |
|---|---|---|---|
| 5.1 | Any collision/conjunction/operational-risk claim? | P0 (resolved) | None; every mention negated or framed as not assessed (§4.4 "Exposure is not hazard"); QC lexicon check. |
| 5.2 | "These factors ... are the more transferable result" overstated generality. | P1 (resolved) | Reverted to "more informative result". |
| 5.3 | Priority / novelty words. | P0 (resolved) | No "first", "novel", "unprecedented" (QC). |
| 5.4 | Static-patch literature. | P0 (resolved) | No claim of established practice; targeted search reported; comparator "not a representation of prior work". |
| 5.5 | Feasibility. | P0 (resolved) | "no engineering feasibility is claimed"; source is an abstract energy input; 100 GW described as "very large power". |
| 5.6 | Added JSSE citations used for venue signalling? | P2 | Each supports a specific sentence; abstracts read and archived (`docs/JSSE_CITATION_ECOLOGY_AUDIT.md`). |

## Remaining items

**P0 (author/administrative, cannot be done by the pipeline):**
1. Confirm author name order and address romanisation on the title page and in Editorial Manager (manuscript uses
   "Tatsuki Onishi" and "1-1-1 Bamba, Hikone" as given in the JSSE master prompt; ORCID public name is "Onishi Tatsuki").
2. Complete and upload Elsevier's declaration-of-competing-interest template at submission.
3. At acceptance choose the subscription route (no APC) and "online only" for colour figures.

**P1 (accepted residual risks):** journal-fit desk risk (1.2); single-model, single-background scope (§4.5).

**P3 (optional):** convert the first-page "Abbreviations" paragraph into a Word footnote if the editorial office asks.
