# Baseline Freeze — Gate 0

Date (UTC): 2026-10-17T09:17:08Z
Branch: devin/1792228606-asr-hostile-hardcode-revision
Base: origin/devin/1790845369-reentry-flag-reset (PR #4 head)
HEAD commit: d2d2b12a5e19f78ea16687570e5770b9fc2c6b91
Dirty files: 1 (none expected; deps installed into env, not repo)

## Environment
Python 3.10.12
matplotlib          3.10.9
matplotlib-inline   0.1.3
nrlmsise00          0.1.2
numpy               2.2.6
pandas              2.3.3
pytest              9.1.1
python-docx         1.2.0
SALib               1.6.0
scipy               1.15.3

## Key artifact hashes (SHA-256)
- manuscript/manuscript.docx  0e9ede5f8ce63d7f27c3b3946874452763fc1e442508728ff5d5489b5047c46b
- manuscript/manuscript_inline.docx  a133443442d955c792609711327f4d566ee60ab88bda028e23e5b891b7e63765
- manuscript/manuscript_figures.pptx  539b389be68aa3252e679c5a6cd0527e13c4a375d5cba998394561ea56e69fbf
- supplement/supplement.docx  7c87f3eac29fe390c41571da40b6c11cde00f8b3075bdd6e42548207596f83ff
- results/tables/master_results.csv  e14a8c123c157900a98798872207c821dbb49a7a0da685ce37f4ff7319daae9f
- results/manuscript_value_provenance.csv  8a7bbbc9962114dd2013dcc4fb2bd7db6db35041bc19580095000159f3d15731
- results/manuscript_citations.csv  0f3ebac9fee9a2316a49217b7175b036e9ad56568bc8323ff46b73b9c50ff317
- config/default.yaml  37258ec4dbed4e6c8c608ce3b10f69e6c46587f4bd0ea8f4f7c5b76e4643c3f8

## Result table hashes
- results/tables/energy_bounds_audit.csv  358afbf67377f1b8d80b1a7844d643a532eaad018768c2a8cf1569b842772765
- results/tables/gap_decomposition.csv  1b7b61bd770ddca441fbfef99db0202b7e0629bb8ec7717cec430b2cf11cd35a
- results/tables/gap_decomposition_factors.csv  ef83aecbe530c6f519b34ad8f0ab641d75a0af96574bda4d9355101eedaf0f19
- results/tables/master_results.csv  e14a8c123c157900a98798872207c821dbb49a7a0da685ce37f4ff7319daae9f
- results/tables/matched_exposure.csv  1e1d7208dcd844e423f1a052497bae5f467c4e7db6ed978e4c8a2dac5e1dcbe5
- results/tables/numerical_zero_audit.csv  e6198ea3230b2a57e5b378cf79048ca418fc99e373b6bf22a8bed697978bb2a9
- results/tables/orbit_step_convergence.csv  481297c1dafe7affc26ccc00c1384415670365b5939a01de861a25bf25865d93
- results/tables/phase10_montecarlo.csv  a9df93af6d02410f964a377eb3b1dfd296d3ac5e89e84c3e47ffffe307aecc8c
- results/tables/phase10_negative_controls.csv  8242507ffe710a8deaa56b6cf26ad4d6dfd379b568967ca2193900e29b36f16b
- results/tables/phase10_sobol.csv  f616a8139320f575eadfa0f268750dd012b66a12379d33f8762fa81b1881cf73
- results/tables/phase11_scaling.csv  c049c99120a1b9e2f871433f9a6e765ebb5e72015bf4c279db82c88888fb73df
- results/tables/phase12_classification.csv  fe5b68f401eef3582d65285252da8569c89285108a02efe4adabebde22cb3d13
- results/tables/phase1_density_table.csv  adfaeffc1d930e7b8c9ce1fc45fd02de2060ed3fb5cf53504a8874c197fbcc8a
- results/tables/phase1_energy_bounds.csv  46dd7a0a4438e5144dcefdf356e6ae22e114a44da6d605d1d6322940fec6ec73
- results/tables/phase1_scale_calculations.csv  ee2619a2aa9deacd1063b5f1bfd5ff6dfe2fba371e49b3e34b159b2e41cd1e8a
- results/tables/phase2_validation.csv  ccf3f51bd239d6f4077698bb9e62b20713d4645d8ffc7e2c31de4bf5e270d505
- results/tables/phase3_intervention_checks.csv  3e64a1b65f9541b40333d5db56d35ccd950fe0ede2cacaf070978f9a5650b22d
- results/tables/phase5_spreading.csv  c6461aa26e18f597dc0eb3994641e6b508a50bb2de6ca6f1d76a81dc708f1c78
- results/tables/phase6_outcomes.csv  6abd87b5d1d67163bca0fa73a7c5eea53a29854a688668845e7d2fa06c374e83
- results/tables/phase7_controls.csv  30e52b0ce4453d562b08b35d4835610bee43ba0474dcb51aad38bdb3b5355522
- results/tables/phase7_selectivity.csv  b5b1e352f1bc748264734333909969366bff5bf459656bfea5140a0a19351c2d
- results/tables/phase8_timing.csv  a8fa265b095b5f69254a2e0a437f27094e4a0d4bc973aa6d6d287e9c61890f4f
- results/tables/phase9_pareto.csv  0195637a8ca4b1a46ebb3ca25d7126843edb20799c9a9cd155a92d6d891a3a13
- results/tables/quick_summary.csv  b2d85db2b2b322c404637bcc7a86a87215d3027c4b0829b4e7401c64e8b51314
- results/tables/selectivity_classified.csv  e3a2481b1f6a5c33c83a04696ede7e8890cae5542e9373f5e1d6c328edbd186c
- results/tables/sobol_convergence.csv  2ecc354319195eb656f5231849db7c8d79636ac406145c37e8b57e056fefbddc
- results/tables/sobol_reproduction_check.csv  55f484756c51acdc5cb6f8b3037c15f1a2018b57623f29cc9336d677f2c6edec
- results/tables/transport_boundary_sensitivity.csv  9e5ca2faeebefbf534f9d06914abd800656dc194733c29f2bed6108b11286f95

## Frozen claims (PR #4 state)
- Perfect co-location upper bound: 6.87 m/s/day target Δv at 400 km, high-B case; drift-aware tracking: 3.53 m/s (natural drag 1.37 m/s).
- Earth-fixed pulse per event: 3.986e-3 m/s. Ideal-vs-fixed gap ~1726x, decomposed into exposure-time (12x), in-patch fraction (22.5x), mean in-patch enhancement (6.3x), closure error -1.5%.
- Selectivity: localization buys collateral suppression, not effect; 3 matching conventions (equal target exposure / equal spacetime integral / equal energy lower bound). Equal spacetime-integral target effect drops to 2.99e-3 m/s.
- Exposure classification: physical / Gaussian-tail / below-resolution / non-encounter; extreme selectivity ratios (e.g. 1.2e80) declared non-physical. Co-orbital and orbit-crossing geometries break selectivity.
- Transport: 11/27 design-grid combinations survive 1 h at 100 m/s wind (grid fraction, not probability; varies 8-56% with grid). Column-expansion heating lower bound ~168x in-situ bound at 400 km (~3.6e7 W sustained).
- Scaling: Pi = Δv·B/(ρ·δ·v_rel²·T) = 1.062±0.260 (slope ~1.01, R²~0.9995); declared dimensional/internal-consistency check, not independent validation.
- 68 manuscript numbers injected from CSVs via manuscript_value_provenance.csv; build fails on missing values.
- MC n=256, Sobol converged; 20 tests pass; make clean/all/quick EXIT=0, QC PASS.

## Known limitations (carried from prior audits)
- Surrogate thermospheric dynamics (Gaussian patch diffusion/advection), not a full GCM.
- Right-censored lifetimes reported as censored, not measured infinity (see `inf` audit in Gate 3).
- PR #4 reentry fix affects only reentry-reaching cases (250 km band, one 350 km object); Pi mean 1.042 -> 1.062.

## Package vs working tree
Working tree = origin/devin/1790845369-reentry-flag-reset = source of latest ASR_final_submission.zip (2695748 B). No later commits exist on main beyond PR #3; PR #4 is open and is canonical.
