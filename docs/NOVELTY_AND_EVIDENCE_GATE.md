# Gate 5 — Novelty and evidence gate

This gate combines the Gate 1B literature baseline with the Gate 3/4 physical-model evidence. It does not
restate numbers; each item points to the generated source.

| Input | File |
|---|---|
| Verified prior literature (Crossref) | `references/PRIOR_KNOWLEDGE_VERIFIED.csv`, `docs/PRIOR_KNOWLEDGE_MATRIX.md` |
| Pre-results novelty map | `docs/INCREMENTAL_NOVELTY_MAP.md` |
| Frozen predictions and scoring | `docs/PRIOR_PREDICTIONS_FROZEN.md`, `results/tables/physical_prediction_outcomes.csv` |
| Physical response audit | `docs/PERTURBATION_PHYSICS_AUDIT.md` |
| Resolution / discretization (G3R) | `docs/G3R_RESOLUTION_DISCRETIZATION_AUDIT.md`, `results/grid_sensitivity_metrics.csv`, `results/threshold_sensitivity.csv`, `results/orbit_interpolation_sensitivity.csv` |
| Power–effect–selectivity (G4T) | `docs/G4T_POWER_EFFECT_SELECTIVITY_TRADEOFF.md`, `results/power_effect_selectivity.csv` |
| Claim-by-claim evidence | `docs/CLAIM_EVIDENCE_MATRIX.md` |
| Decision | `docs/SCIENTIFIC_CONTRIBUTION_GATE.md` |

Prediction scorecard: 4 of 12 frozen predictions were falsified in at least one tested case (PR1, PR2, PR7,
PR12 — all on the side of a larger or more non-linear response than the literature-based expectation) and
PR10 was falsified at 300 km only; the remaining predictions were confirmed or outside range but not
falsified. The falsifications are reported, not re-fitted.

Decision: **CONDITIONAL GO** (see `docs/SCIENTIFIC_CONTRIBUTION_GATE.md` §4 for the condition and the
single analysis that would resolve it). No manuscript reconstruction or journal selection has started.
