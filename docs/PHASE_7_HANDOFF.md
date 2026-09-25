# Phase 7 handoff

Optimized localized (case A): t0=211 s, dur=74729 s, objective=2.905

| scenario            | pair   |   target_dv_ms |   protected_dv_ms | protected_class   |   protected_n_sigma |   protected_encounters |   protected_rel_to_natural |   selectivity_ratio | ratio_status           | ratio_meaningful   |
|:--------------------|:-------|---------------:|------------------:|:------------------|--------------------:|-----------------------:|---------------------------:|--------------------:|:-----------------------|:-------------------|
| uniform             | A      |       7.3596   |       0.430979    | physical_exposure |           -0        |                      1 |                5           |        17.0765      | physical               | True               |
| uniform             | D      |       0.162819 |       0.0382635   | physical_exposure |           -0        |                      1 |                5           |         4.25521     | physical               | True               |
| uniform             | E      |       2.25683  |       0.492468    | physical_exposure |           -0        |                      1 |                5           |         4.5827      | physical               | True               |
| uniform             | G      |     471.652    |      10.8814      | physical_exposure |           -0        |                      1 |                5           |        43.3448      | physical               | True               |
| localized_tracking  | A      |       3.44732  |       4.1641e-06  | gaussian_tail     |            4.77406  |                      1 |                5.35829e-05 |    827867           | tail_limited           | False              |
| localized_tracking  | D      |       0.162493 |       1.26984e-81 | no_encounter      |           19.0968   |                      0 |                1.71216e-79 |         1.27963e+80 | undefined_no_encounter | False              |
| localized_tracking  | E      |       1.64552  |       0.00615817  | physical_exposure |            0.165858 |                     29 |                0.0627865   |       267.209       | physical               | True               |
| localized_tracking  | G      |      38.1177   |       1.59571e-79 | no_encounter      |           19.0968   |                      0 |                1.67562e-79 |         2.38877e+80 | undefined_no_encounter | False              |
| optimized_localized | A      |       3.4292   |       3.68362e-06 | gaussian_tail     |            4.77406  |                      1 |                5.35808e-05 |    930933           | tail_limited           | False              |