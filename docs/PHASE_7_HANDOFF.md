# Phase 7 handoff

Optimized localized (case A): t0=573 s, dur=73573 s, objective=3.519

| scenario            | pair   |   target_dv_ms |   protected_dv_ms | protected_class   |   protected_n_sigma |   protected_encounters |   protected_rel_to_natural |   selectivity_ratio | ratio_status           | ratio_meaningful   |
|:--------------------|:-------|---------------:|------------------:|:------------------|--------------------:|-----------------------:|---------------------------:|--------------------:|:-----------------------|:-------------------|
| uniform             | A      |       7.9673   |       0.432726    | physical_exposure |           -0        |                      1 |                5           |        18.4119      | physical               | True               |
| uniform             | D      |       0.163036 |       0.0382756   | physical_exposure |           -0        |                      1 |                5           |         4.25954     | physical               | True               |
| uniform             | E      |       2.30707  |       0.494759    | physical_exposure |           -0        |                      1 |                5           |         4.66302     | physical               | True               |
| uniform             | G      |      64.1652   |      13.1878      | physical_exposure |           -0        |                      1 |                5           |         4.8655      | physical               | True               |
| localized_tracking  | A      |       3.53026  |       4.24627e-06 | gaussian_tail     |            4.77406  |                      1 |                5.35829e-05 |    831378           | tail_limited           | False              |
| localized_tracking  | D      |       0.162812 |       1.27374e-81 | no_encounter      |           19.0968   |                      0 |                1.71216e-79 |         1.27822e+80 | undefined_no_encounter | False              |
| localized_tracking  | E      |       1.85424  |       0.00617976  | physical_exposure |            0.165858 |                     29 |                0.0627865   |       300.05        | physical               | True               |
| localized_tracking  | G      |      12.6229   |       6.04907e-80 | no_encounter      |           19.0968   |                      0 |                1.67562e-79 |         2.08675e+80 | undefined_no_encounter | False              |
| optimized_localized | A      |       3.51923  |       3.69099e-06 | gaussian_tail     |            4.77406  |                      1 |                5.35692e-05 |    953465           | tail_limited           | False              |