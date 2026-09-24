# Phase 3 handoff

Intervention model checks: all pass

| model               | expected               |         got | passed   |
|:--------------------|:-----------------------|------------:|:---------|
| gaussian_peak       | 0.00038076210902182606 | 0.000380758 | True     |
| gaussian_vertical   | 3.032653298563167      | 3.03262     | True     |
| tophat_inside       | 2.0                    | 2           | True     |
| tophat_outside      | 0.0                    | 0           | True     |
| moving_static_equiv | 1.5                    | 1           | True     |
| encounter_detected  | mean_rho_delta>0       | 5.3225e-17  | True     |
| encounter_count     | >=1                    | 1           | True     |