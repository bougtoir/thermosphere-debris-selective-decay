# JSSE claim–evidence audit

Every quantitative statement in `manuscript/JSSE/*` is injected at build time from the value ledger
`results/manuscript_jsse_values.csv` (164 values, each with its source file), which is byte-identical to the Acta-final
ledger `results/manuscript_physical_values.csv` (QC check "JSSE value ledger identical"). The QC check "every body
number injected or a declared design constant" scans the abstract, body and captions for any other number. This audit
covers the claims that carry the space-safety argument and the claims introduced or reworded for JSSE.

Status: **S** supported by the cited evidence; **S-q** supported with the stated qualifier (the qualifier is in the
text); **L** stated as a limitation, not a claim.

## A. Quantitative claims (unchanged from the Acta-final results)

| Claim (manuscript wording) | Ledger value(s) | Source | Status |
|---|---|---|---|
| 12 h selectivity 1.51 / 2.03 / 1.02 at 400 / 500 / 300 km (coarse); fine 1.49 / 2.04 | `S12_p11_z300_36x36_*`, `S12_p11_z300_fine12_72x72_*` | `results/tables/physical_g4t_selectivity_evolution.csv` | S |
| Non-targets receive 84% (fine 85%) at 400 km and 77% at 500 km **of the synthetic sample** | `nontarget_share_*` | same | S-q |
| S falls 5.3 → 2.1 → 1.51 (400 km) and 10.9 → 3.1 → 2.03 (500 km) at 1 h, 3 h, end of window | `S_p11_z300_36x36_*_1h/_3h` | same | S |
| 95% intervals 1.43–1.59 (400 km), 1.84–2.21 (500 km); conditional on one simulated atmosphere | `S12_ci95_*` | `results/tables/physical_selectivity_bootstrap.csv` | S-q (added qualifier) |
| Peak-matched static patch overstates S 1.5–1.7× (400 km), 2.8–3.6× (500 km) over 12 h | `gauss_over_gitm_*_12.0h_*` | `results/tables/physical_contribution_gate_checks.csv` | S |
| Source-centred 1000 km patch overstates S 4.7–5.8× (400 km), 8.0–8.5× (500 km) | `src1000_over_gitm_*` | `results/tables/physical_g4t_gaussian_matching.csv` | S |
| At 3 h the 400 km GITM/patch ratio is 0.98–1.12 (no reduction yet); 500 km 0.52–0.67 | `gitm_over_gauss_*_3.0h_*` | `results/tables/physical_contribution_gate_checks.csv` | S |
| Coarse/fine 12 h S differ by ≤ 1.1% at 400/500 km | `S12_fine_vs_coarse_max_diff_400_500_pct` | `physical_g4t_selectivity_evolution.csv` | S |
| Peak Δρ/ρ 204% (400 km), 983% (500 km); global-mean peak 11.6% | `peak_drho_*`, `max_global_mean_drho_*` | `results/tables/physical_g3_summary.csv` | S |
| Target extra Δv 6.6 mm/s = 3.7% of natural drag; lifetime 129 d shortened by ≈ 0.010 d | `target_extra_dv_400`, `target_extra_over_natural_400`, `lifetime_base_400_d`, `delta_lifetime_target_400_d` | `results/physical_model_vs_prescribed_patch.csv` | S |
| 10/100 GW peak ratio 0.31; 150/300 km deposition peak ratio 0.16; S at 10 GW 1.93/2.27; at 150 km 0.97/0.95 | `peak400_ratio_*`, `S12_p10_*`, `S12_p11_z150_*` | `physical_g3_summary.csv`, `physical_g4t_selectivity_evolution.csv` | S-q ("two-level contrasts ... do not define a scaling law") |
| Prediction scorecard 11 confirmed, 5 falsified, 2 outside range (primary configuration) | `n_confirmed_core` etc. | `results/tables/physical_prediction_outcomes.csv` | S |

Independent recomputation of the principal estimands from lower-level outputs: `scripts/acta_semantic_checks.py`,
325/325 PASS this session (`results/tables/acta_semantic_checks.csv`).

## B. Framing claims added or reworded for JSSE

| Claim | Evidence / reasoning | Status |
|---|---|---|
| Collisions can sustain debris growth even without new launches [1–3] | Kessler & Cour-Palais 1978; Liou & Johnson 2006; Lewis 2020 (abstract read) | S |
| Most remediation methods act on individual objects [4–10] | ADR reviews and drag-device/laser papers | S |
| An environment-directed method modifies a shared medium, so non-targets receive part of the effect | Definition; demonstrated quantitatively for one configuration in §3.2 | S |
| Remediation should be assessed by its effect on environment and operations [12,13] | McKnight 2016 (operational success framework), Usovik 2023 (assessing measures' effect on the environment) — abstracts read | S |
| Density/drag uncertainties propagate into orbit prediction and estimation [14] | Vallado & Finkleman 2014 highlights | S |
| Aggregate share depends on the number of targets, the population and the target criterion | Follows from Eq. (3); stated in §2.4 and §4.4 | S |
| "Static patches as a modelling representation ... not two physical outcomes"; difference attributed to the time-evolving field as a whole, not to transport alone | No mechanism/transport budget computed — stated | S (calibrated) |
| Three minimum requirements for screening (§4.3) | Each tied to a result of this experiment (static overstatement; share dependence; S(t) decline, Fig. 3); explicitly "requirements on the assessment, not conclusions about any particular concept" | S-q |
| Extra drag is an exposure metric; collision probability, conjunction rates, manoeuvre burden and mission safety not quantified (§4.4, abstract, cover letter) | No catalogue, conjunction screening or risk tool was used — stated | S |
| "A small drag increment on non-target objects is not evidence of safety" | Logical caution; magnitude depends on forcing/population/target definition | S |
| No engineering feasibility claimed; source is an abstract energy input | Methods §2.2 | S |
| Limitations: one model, one quiet background, two grids, 6 h vs 24 h spin-up, no convergence, idealized 100 GW source, synthetic circular orbits, one ballistic coefficient, one target definition, two-level contrasts, no observational validation | §4.5 | L |

## C. Claims deliberately not made

* No "first", "novel" or priority claim (QC lexicon check).
* No statement that static Gaussian patches are established practice; the static patch is "an idealized comparator,
  not ... a representation of prior work", after a targeted search that found no such study.
* No collision-risk, conjunction-risk, manoeuvre-burden or operational-hazard estimate; every mention of these terms is
  negated or framed as not assessed (QC check).
* No interpretation of 84–85% / 77% as a fraction of real satellites, debris burden or risk; every share percentage is
  qualified by "synthetic sample" (QC check).
* No "unsafe", "catastrophic" or deployment-validation language (QC lexicon check).
