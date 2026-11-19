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

Twelve-hour fine-grid continuation (`docs/SCIENTIFIC_CONTRIBUTION_GATE.md` §5): the frozen §3 rule (a) is met
over 0–12 h for every Gaussian fit-ingredient variant on both grids (`results/tables/physical_contribution_gate_checks.csv`);
PR8 bounds hold over 12 h. PR10 is confirmed at 500 km, outside range but not falsified at 400 km (×~1.5–1.7
instead of ≥ 3) and falsified at 300 km; the claim is calibrated to these magnitudes.

Decision: **CONDITIONAL GO, condition resolved — contribution gate satisfied for a calibrated single-model
claim** (STRONG GO excluded by the constraints in `docs/SCIENTIFIC_CONTRIBUTION_GATE.md` §2). Proceed to G6
manuscript reconstruction; journal selection follows from the calibrated claim set in §5 of that file.
