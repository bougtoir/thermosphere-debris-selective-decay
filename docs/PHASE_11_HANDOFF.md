# Phase 11 handoff

Dimensionless collapse of simulated extra delta-v onto Pi_benefit = 2*dv*B/(rho*delta*v_rel^2*T) = 1 (uniform enhancement, T_eff = T). See docs/SCALING_LAW_AUDIT.md: the collapse is an internal-consistency check, not an independent physical validation.

| regime   |    mean |       std |   count |
|:---------|--------:|----------:|--------:|
| high     | 1.0887  | 0.360508  |     120 |
| low      | 1.02931 | 0.0361013 |     120 |
| moderate | 1.05099 | 0.235389  |     120 |
| storm    | 1.07169 | 0.201937  |     120 |

log-log fit: slope=1.016, intercept=0.041, R2=0.9985
