# Physical-model rebuild — Gate 0 baseline freeze

Date (UTC): 2026-11-07T10:36:05Z
Baseline: `main` @ `ac67802a0965661bb172285bc120b5ad5fe2a9bb` (merge of PR #8, 2026-11-05).
Working branch: `devin/1794047620-physical-model-rebuild`.
Authoritative editorial decision: AISR-D-26-03405 (desk rejection). AISR-S-26-05628 is the same project
(the earlier submission number that went through the editorial technical correction).

## Immutability rule
Nothing that exists at the baseline commit is modified or deleted by this branch. The old pipeline
(`src/`, `scripts/phase*.py`, `results/`, `manuscript/`, `supplement/`, `ASR_*.zip`) is the frozen
idealized-Gaussian comparator. All new work lives in new paths:

- `physical/` — new code (GITM user-heating hook, run configs, post-processing, orbit coupling)
- `results/physical/` — new canonical CSVs/figures derived from physical-model runs
- `data/physical/` — retained run inputs, logs, compact model-output extracts and the acquisition ledger
- `docs/` — new gate documents (names listed in the mission brief)

## Frozen headline numbers (values from the baseline CSVs, not re-run)
| quantity | value | source |
|---|---|---|
| idealized on-target tracking bound, 1 d, 400 km, B=5 | 6.87 m/s | gap_decomposition.csv |
| natural drag over the same window | 1.37 m/s | gap_decomposition.csv |
| drift-aware simulated tracking arm | 3.53 m/s | phase6_outcomes.csv |
| Earth-fixed pulse (delta=5, sigma_h=200 km, 2 h) | 3.98e-3 m/s | phase6_outcomes.csv |
| transport persistence (1 h) | 11/27 combinations | transport_boundary_sensitivity.csv |
| hydrostatic column-expansion lower bound | ~5.80e7 W | energy_bounds_audit.csv |
| Cowell vs fast propagator (10 d) | 0.062% | phase2_validation.csv |

## Frozen citation set
`references/references_verified.csv` (18 entries) at the baseline commit.

## Environment at freeze
Python 3.10.12, numpy 2.2.6, scipy 1.15.3, pandas 2.3.3, nrlmsise00 0.1.2 (requirements.txt pins).
VM: 2 vCPU (Intel Xeon, KVM), 7 GiB RAM, no swap, 86 GB free disk.

## Artifact hashes (SHA-256) at baseline
- 164749a90b5fdc9b64869744df6986ba198fd1b6a39b10444f4b60fe7529701d  manuscript/manuscript.docx
- 837c831daa6c7b8fa325243a87aaba50b7307469e45c3949095f24c5902e5ced  manuscript/manuscript_inline.docx
- 55e55b422d2f9b2895c54c99f6e78e3fe462578c0edf344ed9b57c40050ac5a4  manuscript/manuscript_figures.pptx
- 813ba5fd262638f0ff2f8003c38a9e1a930073a89654ddc161bc6dee5dfd644b  supplement/supplement.docx
- 37258ec4dbed4e6c8c608ce3b10f69e6c46587f4bd0ea8f4f7c5b76e4643c3f8  config/default.yaml
- 358afbf67377f1b8d80b1a7844d643a532eaad018768c2a8cf1569b842772765  results/tables/energy_bounds_audit.csv
- 1b7b61bd770ddca441fbfef99db0202b7e0629bb8ec7717cec430b2cf11cd35a  results/tables/gap_decomposition.csv
- ef83aecbe530c6f519b34ad8f0ab641d75a0af96574bda4d9355101eedaf0f19  results/tables/gap_decomposition_factors.csv
- e620fa81a537d38dfb7fd1fa7bd70e270cc0808f89f9efcb2c274bba10d9ef2e  results/tables/master_results.csv
- 1e1d7208dcd844e423f1a052497bae5f467c4e7db6ed978e4c8a2dac5e1dcbe5  results/tables/matched_exposure.csv
- e6198ea3230b2a57e5b378cf79048ca418fc99e373b6bf22a8bed697978bb2a9  results/tables/numerical_zero_audit.csv
- 481297c1dafe7affc26ccc00c1384415670365b5939a01de861a25bf25865d93  results/tables/orbit_step_convergence.csv
- a9df93af6d02410f964a377eb3b1dfd296d3ac5e89e84c3e47ffffe307aecc8c  results/tables/phase10_montecarlo.csv
- 8242507ffe710a8deaa56b6cf26ad4d6dfd379b568967ca2193900e29b36f16b  results/tables/phase10_negative_controls.csv
- 34da93220de8560821b2eca8a5dbc26f4f0e2402736061abd24d4b52c4372d90  results/tables/phase10_sobol.csv
- c049c99120a1b9e2f871433f9a6e765ebb5e72015bf4c279db82c88888fb73df  results/tables/phase11_scaling.csv
- abed35f3a9cac656d31c4551b4b62454b0239824b2fbd67b5f6c4adfe98c659d  results/tables/phase11_scaling_fit.csv
- fe5b68f401eef3582d65285252da8569c89285108a02efe4adabebde22cb3d13  results/tables/phase12_classification.csv
- b72e4bf86c3eb5d5314204d8afbc0913a9841745025acc004e7dd997a62e7f34  results/tables/phase1_density_table.csv
- 3caaad39187dd41302ad5b2449ef4182dae3db1eb31932fefbae9909f084b4e0  results/tables/phase1_energy_bounds.csv
- 7244ff6996a96b5764a5b4f6a09b365cbf07a51d0b183c75a683a34e9ad01ce9  results/tables/phase1_scale_calculations.csv
- ccf3f51bd239d6f4077698bb9e62b20713d4645d8ffc7e2c31de4bf5e270d505  results/tables/phase2_validation.csv
- 3e64a1b65f9541b40333d5db56d35ccd950fe0ede2cacaf070978f9a5650b22d  results/tables/phase3_intervention_checks.csv
- c6461aa26e18f597dc0eb3994641e6b508a50bb2de6ca6f1d76a81dc708f1c78  results/tables/phase5_spreading.csv
- 6abd87b5d1d67163bca0fa73a7c5eea53a29854a688668845e7d2fa06c374e83  results/tables/phase6_outcomes.csv
- 30e52b0ce4453d562b08b35d4835610bee43ba0474dcb51aad38bdb3b5355522  results/tables/phase7_controls.csv
- b5b1e352f1bc748264734333909969366bff5bf459656bfea5140a0a19351c2d  results/tables/phase7_selectivity.csv
- a8fa265b095b5f69254a2e0a437f27094e4a0d4bc973aa6d6d287e9c61890f4f  results/tables/phase8_timing.csv
- 0195637a8ca4b1a46ebb3ca25d7126843edb20799c9a9cd155a92d6d891a3a13  results/tables/phase9_pareto.csv
- b2d85db2b2b322c404637bcc7a86a87215d3027c4b0829b4e7401c64e8b51314  results/tables/quick_summary.csv
- e3a2481b1f6a5c33c83a04696ede7e8890cae5542e9373f5e1d6c328edbd186c  results/tables/selectivity_classified.csv
- 33da193b2d29fb0e4edd14fed1a918fdeeda043c0a965e3da2fe05133ad7e0c6  results/tables/sobol_convergence.csv
- b39709222daa7fa4478478ae79db58d3e8c1a083cef25c43826e1d6f70f96d11  results/tables/sobol_reproduction_check.csv
- 9e5ca2faeebefbf534f9d06914abd800656dc194733c29f2bed6108b11286f95  results/tables/transport_boundary_sensitivity.csv
- 63f6836e27390542663ed2b3688888b646cbaa82a732ebefd3d865eec50fc08e  results/ASR_FINAL_NUMERIC_CLAIM_MAP.csv
- c4d770c4784bc0069f5aaa2f4a7b7406fc455fe5f5c6abd3f38de81ae50b33be  results/ASR_REFERENCE_MAPPING.csv
- 533bac4a0f0b6a0535bac850bfd973f3a5b4e6702b93e730c7cb99e06e7dbe81  results/evidence_inventory.csv
- d3640578677f88ce837213cc4d8af95216b50b9c9d853b4c82961bdcb8a0b944  results/hardcode_findings.csv
- bb6faa7bbbce8e0f8f15c60287e433b01133c5fffcc9892b56f2100dac1528cd  results/manuscript_citations.csv
- b909989bb7543d9667f5ee6d91ece98670551cf3cd712e71c0485a81748bdc7a  results/manuscript_value_provenance.csv
- dad972882f861029927549b9de682d25edeec06ee7493d0b75527c5217e83177  results/numeric_claim_traceability.csv
- 9e3e2f3aef9cb20863461a2d2753af805fc51ed0e26c9d2c0bbe66a034d0a343  results/numeric_equation_figure_delta.csv
- ae42551b80c00f98024d839e91401c28826d6d8232f900afb02d173695f4ee8f  results/scientific_semantic_delta.csv
- 7f7ff7fef42dd24972f63b2c2082eaab64c6ed910d60977eb1c8e89937648aab  references/ASR_REFERENCE_QC.csv
- 85f565f70a6f2a4d8fe25a4c9f22b1d3200a12819faeb381b22fb44bf8453342  references/references_verified.csv
- f53163b29c08b365a3b96c811f67cfff0c332b2eac33e335031ff7d5d7a9a5c2  ASR_EDITORIAL_SEMANTIC_VERIFIED.zip
- 9b54bf31195eb8479701cc049462d72332b3709d5947bbd48315d5d885c576b8  ASR_EDITORIAL_TECHNICAL_CORRECTION_FINAL.zip
- 661c4ddc3a8679d4f7f74705285a0b3d84bf2a53a90f96b47df3e954435724a8  ASR_FORMAT_CITATION_QC_FINAL.zip
- a11fb518b0cdb0d511a7b1ddbbf2c19d02748580c67faa17c7cd04507d3ee4b5  ASR_SUBMISSION_EVIDENCE_VERIFIED.zip
- ac8b45919ab9f098387c38f151e4d23d92701c2fdfd52fcf52392e941ec66997  ASR_SUBMISSION_EVIDENCE_VERIFIED_FINAL.zip
- 52a198d8f64bfc8230defb0bfb90237f715f11362fe246bc17de6b8740d4dea7  ASR_SUBMISSION_FINAL_LOCK.zip
- 7fea6aa713fbd7e1c7c9c138524c79b830f0e5fda27ad8d7e5e7b52bf1232218  ASR_submission_FINAL_AUDITED.zip
