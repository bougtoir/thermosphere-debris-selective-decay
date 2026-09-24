# Decision log

Autonomous-study choices that a reader might reasonably have made
differently, with the rationale actually used.

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 1 | Density model | NRLMSISE-00 via `nrlmsise00`, orbit/attitude-averaged lookup table | Community standard; JB2008 kept as model-form citation; lookup cached once (3204 rows) to keep grids affordable |
| 2 | Propagator for grids | J2-secular semi-analytic + orbit-mean density; Cowell+DOP853 reserved for validation | Cowell too slow on 2 CPUs for population/MC grids; validated to <10% on drag-only decay (Gate 2) |
| 3 | Regimes | 4 fixed solar/geomagnetic regimes (low/moderate/high/storm), F10.7+ap from config | Covers climatological range used in storm-drag literature |
| 4 | Perturbation | Abstract fractional enhancement delta(r,t); Gaussian patch + an idealized on-target *tracking bound* | The prompt forbids hardware blueprints; the tracking bound is an upper limit, not a mechanism |
| 5 | Selectivity metric | Always reported beside absolute protected-object delta-v | Ratios alone hide collateral; mandated by protocol |
| 6 | Intervention comparison | Matched integrated exposure (uniform vs localized vs optimized) | Required to test whether localization itself adds value |
| 7 | Negative controls | All six mandatory controls simulated, not asserted | High-altitude, high-B, twin trajectory, diffuse, short, mistimed |
| 8 | Optimization | scipy differential_evolution, small budget (maxiter 12, popsize 6) | Sufficient for 2-D (t0, duration); documented as such |
| 9 | MC size | 256 (quick) / Sobol' Saltelli N=32 | Cost constraint on 2 CPUs; Sobol' used because the scaling collapse showed near-linear response |
| 10 | Journal | Advances in Space Research | See JOURNAL_AUDIT.md |
| 11 | Manuscript numbers | All injected from results CSVs by build_manuscript.py | No hard-coded scientific numbers |
