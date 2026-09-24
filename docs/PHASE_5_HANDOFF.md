# Phase 5 handoff

| model               |   target_exposure |   protected_exposure |   selectivity_ratio |   target_enc |   protected_enc |   target_tfrac |   exposure_retention |
|:--------------------|------------------:|---------------------:|--------------------:|-------------:|----------------:|---------------:|---------------------:|
| M0_static           |       6.65294e-17 |          5.01372e-17 |            3.53852  |            1 |               1 |      0.0222222 |           1          |
| M1_diffusion_weak   |       6.65161e-17 |          5.01336e-17 |            3.53807  |            1 |               1 |      0.0222222 |           0.9998     |
| M1_diffusion_mod    |       6.52374e-17 |          4.97758e-17 |            3.495    |            1 |               1 |      0.0222222 |           0.980581   |
| M1_diffusion_strong |       5.62276e-17 |          4.66097e-17 |            3.21693  |            1 |               1 |      0.025     |           0.845154   |
| M2_adv_diff         |       4.04029e-17 |          6.57942e-17 |            1.63755  |            1 |               1 |      0.0222222 |           0.607293   |
| M2_adv_strong       |       6.08866e-19 |          1.36356e-17 |            0.119074 |            1 |               1 |      0.0194444 |           0.00915183 |
| M2_relax_1h         |       2.3077e-17  |          4.11217e-17 |            1.4965   |            1 |               1 |      0.0222222 |           0.34687    |
| M2_relax_10m        |       1.40324e-18 |          3.92284e-18 |            0.953894 |            1 |               1 |      0.0208333 |           0.021092   |

Note: amplitude under diffusion is rescaled by sigma0^2/sigma(t)^2 so integrated column enhancement is roughly conserved; selectivity loss is therefore driven by footprint growth plus protected-object encounters and by relaxation/advection, not by artificial dilution alone. Published storm redistribution (Bruinsma et al. 2006) shows hours-scale equatorward transport, consistent with the tau/kappa range used here.
