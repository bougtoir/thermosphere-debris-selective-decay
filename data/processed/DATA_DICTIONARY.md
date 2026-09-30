# Data dictionary

Auto-generated column descriptions for results/tables CSVs.


## phase1_density

- `altitude_km`: (phase-specific column)
- `regime`: (phase-specific column)
- `rho_kgm3`: (phase-specific column)
- `H_km`: (phase-specific column)
- `v_circ_ms`: (phase-specific column)
- `period_min`: (phase-specific column)

## phase1_scale

- `regime`: (phase-specific column)
- `altitude_km`: (phase-specific column)
- `B_kgm2`: (phase-specific column)
- `lifetime0_days`: (phase-specific column)
- `mult_for_1pct_reduction`: (phase-specific column)
- `mult_for_10pct_reduction`: (phase-specific column)
- `mult_for_50pct_reduction`: (phase-specific column)
- `mult_for_90pct_reduction`: (phase-specific column)

## phase1_energy

- `altitude_km`: (phase-specific column)
- `sigma_h_km`: (phase-specific column)
- `sigma_v_km`: (phase-specific column)
- `delta`: (phase-specific column)
- `dT_assumed_K`: (phase-specific column)
- `air_mass_kg`: (phase-specific column)
- `E_min_J`: (phase-specific column)
- `orbital_energy_removal_W_per_kg`: (phase-specific column)
- `E_min_over_orbital_per_day`: (phase-specific column)

## phase5_spreading

- `model`: (phase-specific column)
- `target_exposure`: (phase-specific column)
- `protected_exposure`: (phase-specific column)
- `selectivity_ratio`: target extra dv / protected extra dv
- `target_enc`: (phase-specific column)
- `protected_enc`: (phase-specific column)
- `target_tfrac`: (phase-specific column)
- `exposure_retention`: (phase-specific column)

## phase6_outcomes

- `regime`: (phase-specific column)
- `scenario`: (phase-specific column)
- `case`: (phase-specific column)
- `obj_type`: (phase-specific column)
- `alt_km`: (phase-specific column)
- `inc_deg`: (phase-specific column)
- `B`: (phase-specific column)
- `lifetime_d`: simulated decay lifetime, days
- `delta_lifetime_d`: baseline minus intervention lifetime, days
- `delta_a_km`: baseline minus intervention final semimajor axis, km
- `encounter_count`: number of contiguous in-patch crossings
- `extra_impulse_ms`: integrated extra drag impulse, m/s
- `extra_deltav_ms`: equivalent extra delta-v from the perturbation, m/s
- `orbital_energy_removed_J_perkg`: (phase-specific column)
- `reentry`: (phase-specific column)

## phase7_controls

- `scenario`: (phase-specific column)
- `case`: (phase-specific column)
- `obj_type`: (phase-specific column)
- `pair`: (phase-specific column)
- `delta_a_km`: baseline minus intervention final semimajor axis, km
- `a_drop_km`: start minus final semimajor axis over horizon, km
- `extra_deltav_ms`: equivalent extra delta-v from the perturbation, m/s
- `encounter_count`: number of contiguous in-patch crossings
- `delta_lifetime_d`: baseline minus intervention lifetime, days

## phase7_selectivity

- `scenario`: (phase-specific column)
- `pair`: (phase-specific column)
- `target_dv_ms`: (phase-specific column)
- `protected_dv_ms`: (phase-specific column)
- `protected_class`: (phase-specific column)
- `protected_n_sigma`: (phase-specific column)
- `protected_encounters`: (phase-specific column)
- `protected_rel_to_natural`: (phase-specific column)
- `selectivity_ratio`: target extra dv / protected extra dv
- `ratio_status`: (phase-specific column)
- `ratio_meaningful`: (phase-specific column)

## phase8_timing

- `experiment`: (phase-specific column)
- `t_s`: (phase-specific column)
- `case`: (phase-specific column)
- `obj_type`: (phase-specific column)
- `extra_deltav_ms`: equivalent extra delta-v from the perturbation, m/s
- `encounter_count`: number of contiguous in-patch crossings
- `a_drop_km`: start minus final semimajor axis over horizon, km

## phase9_pareto

- `delta_max`: (phase-specific column)
- `sigma_h_km`: (phase-specific column)
- `duration_s`: (phase-specific column)
- `target_dv_ms`: (phase-specific column)
- `target_a_drop_km`: (phase-specific column)
- `protected_dv_ms`: (phase-specific column)
- `protected_a_drop_km`: (phase-specific column)
- `selectivity`: (phase-specific column)
- `on_pareto_front`: (phase-specific column)

## phase10_mc

- `delta_max`: (phase-specific column)
- `sigma_h_km`: (phase-specific column)
- `sigma_v_km`: (phase-specific column)
- `rho_scale`: (phase-specific column)
- `B_scale`: (phase-specific column)
- `duration_h`: (phase-specific column)
- `target_dv_ms`: (phase-specific column)
- `protected_dv_ms`: (phase-specific column)

## phase10_sobol

- `param`: (phase-specific column)
- `S1`: (phase-specific column)
- `ST`: (phase-specific column)
- `S1_conf`: (phase-specific column)
- `ST_conf`: (phase-specific column)
- `n_base`: (phase-specific column)
- `n_model_evals`: (phase-specific column)

## phase10_negative

- `control`: (phase-specific column)
- `case`: (phase-specific column)
- `extra_deltav_ms`: equivalent extra delta-v from the perturbation, m/s
- `a_drop_km`: start minus final semimajor axis over horizon, km
- `encounter_count`: number of contiguous in-patch crossings

## phase11_scaling

- `regime`: (phase-specific column)
- `obj_id`: (phase-specific column)
- `alt_km`: (phase-specific column)
- `B`: (phase-specific column)
- `delta`: (phase-specific column)
- `rho`: (phase-specific column)
- `v_ms`: (phase-specific column)
- `v_rel_ms`: (phase-specific column)
- `T_s`: (phase-specific column)
- `extra_dv_sim`: (phase-specific column)
- `extra_dv_pred`: (phase-specific column)
- `Pi_benefit`: dv*B/(rho*delta*v^2*T), collapses to 1

## phase12_classification

- `regime`: (phase-specific column)
- `alt_km`: (phase-specific column)
- `delta`: (phase-specific column)
- `sigma_h_km`: (phase-specific column)
- `sigma_v_km`: (phase-specific column)
- `kappa_h`: (phase-specific column)
- `advection_ms`: (phase-specific column)
- `patch_air_mass_kg`: (phase-specific column)
- `heating_fraction`: delta/(1+delta), fraction of patch air heated
- `E_thermal_min_J`: minimum thermal energy for required heating fraction
- `tau_diff_s`: sigma_h^2/(2*kappa_h) horizontal diffusion lifetime
- `tau_adv_s`: sigma_h/u advection flushing time
- `transport_survivable_1h`: (phase-specific column)
- `classification`: (phase-specific column)

## audit_exposure_class

- `scenario`: (phase-specific column)
- `pair`: (phase-specific column)
- `case`: (phase-specific column)
- `obj_type`: (phase-specific column)
- `alt_km`: (phase-specific column)
- `inc_deg`: (phase-specific column)
- `B_kgm2`: (phase-specific column)
- `peak_delta`: (phase-specific column)
- `n_sigma_closest`: (phase-specific column)
- `encounter_count`: number of contiguous in-patch crossings
- `time_fraction_in_patch`: (phase-specific column)
- `extra_dv_ms`: (phase-specific column)
- `natural_dv_ms`: (phase-specific column)
- `rel_to_natural`: (phase-specific column)
- `exposure_class`: (phase-specific column)

## audit_transport

- `sigma_set`: (phase-specific column)
- `kappa_set`: (phase-specific column)
- `wind_set`: (phase-specific column)
- `criterion_h`: (phase-specific column)
- `n_combinations`: (phase-specific column)
- `frac_surviving`: (phase-specific column)
- `n_selective`: (phase-specific column)
- `frac_surviving_selective_sigma`: (phase-specific column)
- `n_selective_windy`: (phase-specific column)
- `frac_surviving_selective_windy`: (phase-specific column)
- `n_selective_wind100`: (phase-specific column)
- `frac_surviving_selective_wind100`: (phase-specific column)

## audit_gap

- `scenario`: (phase-specific column)
- `ephemeris`: (phase-specific column)
- `window_s`: (phase-specific column)
- `time_fraction_in_patch`: (phase-specific column)
- `time_in_patch_s`: (phase-specific column)
- `peak_delta`: (phase-specific column)
- `delta_eff_in_patch`: (phase-specific column)
- `encounter_count`: number of contiguous in-patch crossings
- `extra_dv_ms`: (phase-specific column)
- `natural_dv_ms`: (phase-specific column)

## audit_gap_factors

- `factor`: (phase-specific column)
- `ratio`: (phase-specific column)

## audit_matched_exposure

- `pair`: (phase-specific column)
- `matching`: (phase-specific column)
- `case`: (phase-specific column)
- `obj_type`: (phase-specific column)
- `alt_km`: (phase-specific column)
- `ephemeris`: (phase-specific column)
- `volume_ratio`: (phase-specific column)
- `delta_uniform`: (phase-specific column)
- `extra_dv_ms`: (phase-specific column)
- `natural_dv_ms`: (phase-specific column)
- `rel_to_natural`: (phase-specific column)
- `exposure_class`: (phase-specific column)

## audit_energy

- `altitude_km`: (phase-specific column)
- `sigma_h_km`: (phase-specific column)
- `sigma_v_km`: (phase-specific column)
- `delta`: (phase-specific column)
- `rho_top_kgm3`: (phase-specific column)
- `T_top_K`: (phase-specific column)
- `H_km`: (phase-specific column)
- `patch_air_mass_kg`: (phase-specific column)
- `column_mass_kg`: (phase-specific column)
- `dT_insitu_K`: (phase-specific column)
- `E_insitu_J`: (phase-specific column)
- `q_column`: (phase-specific column)
- `column_attainable`: (phase-specific column)
- `eps_column`: (phase-specific column)
- `dT_column_at_top_K`: (phase-specific column)
- `E_column_expansion_J`: (phase-specific column)
- `ratio_column_to_insitu`: (phase-specific column)
- `E_column_per_day_W`: (phase-specific column)
- `orbital_removal_W_per_kg`: (phase-specific column)