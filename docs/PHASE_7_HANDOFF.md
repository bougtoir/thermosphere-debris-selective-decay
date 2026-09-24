# Phase 7 handoff

Optimized localized (case A): t0=614 s, dur=86397 s, objective=0.007444

| scenario            | pair   |   target_dv_ms |   protected_dv_ms |   selectivity_ratio |
|:--------------------|:-------|---------------:|------------------:|--------------------:|
| uniform             | A      |    0.00745497  |       0.00046574  |        16.0067      |
| uniform             | D      |    0.000159771 |       3.75864e-05 |         4.25078     |
| uniform             | E      |    0.002482    |       0.00053188  |         4.66647     |
| uniform             | G      |    0.0825827   |       0.0103087   |         8.01094     |
| localized_tracking  | A      |    0.00745494  |       4.99055e-09 |         1.49381e+06 |
| localized_tracking  | D      |    0.000159771 |       1.28704e-84 |         1.24139e+80 |
| localized_tracking  | E      |    0.002482    |       6.67895e-06 |       371.615       |
| localized_tracking  | G      |    0.0825338   |       3.41943e-82 |         2.41367e+80 |
| optimized_localized | A      |    0.00744401  |       4.9865e-09  |         1.49283e+06 |