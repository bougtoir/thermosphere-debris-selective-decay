# Gate 1B — Predictions frozen before inspecting any perturbed GITM output

Frozen (UTC): 2026-11-07, committed to git before the first perturbed case
(`c4_p11_z300`) had started. State of inspection at freeze time:

* Inspected: GITM upstream reference test; a 30-min unperturbed timing pilot
  (2002-03-21 00:00–00:30); the first hours of the unperturbed 24-h spin-up
  (only log-file min/max temperature and time step). A plumbing self-test of
  the Gate 3/4 scripts used an *injected synthetic* Gaussian on the pilot
  output, not model output.
* Not inspected: any perturbed run, any control-minus-perturbed difference,
  any orbit-coupling result. No perturbed run existed at freeze time.

All predictions below are therefore prospective. Anything added after the
first perturbed output is inspected goes to `docs/CLAIM_EVIDENCE_MATRIX.md`
and is labelled retrospective.

Reference conditions (fixed in `physical/gitm/cases/*.json`): equinox
2002-03-21, F10.7 = F10.7A = 150, constant IMF Bz = −2 nT, SME = 150 nT;
source centred at 45°N, 0°E (local midnight at onset), σh = 1000 km,
z0 = 300 km (σz = 50 km) or 150 km (σz = 20 km), on at t = 1 h for 1 h
(10-min cosine ramps), P0 = 1e10 W or 1e11 W (3.6e13 J or 3.6e14 J). Grid
10°×5° (convergence case 5°×2.5°). Orbits: synthetic circular, 300/400/500 km,
B = 30 kg m^-2.

Main literature anchors: Liu et al. (2015, doi:10.1002/2014JA020962) — GITM
idealized substorm, 50 GW hemispheric-power pulse with Bz = −2 nT gives a
maximum mass-density perturbation of ~14 % about 50 min after onset (nightside
auroral zone); Sutton et al. (2009, doi:10.1029/2008JA013667) — CHAMP 400 km
density responds in < 2 h at mid/high latitudes and 3–4 h at low latitudes;
Deng et al. (2008, doi:10.1029/2007GL032182) — sudden intense heating drives
the vertical pressure-gradient force up to 25 % above gravity (non-hydrostatic),
and the disturbance is transported away; Bruinsma et al. (2006,
doi:10.1029/2005JA011284) — storm-time global density increases of 300–800 %
at 400–500 km with ~4 h delay at the equator; Gardner & Schunk (2010,
doi:10.1029/2009JA015129) — TADs carry energy from the auroral zone to mid/low
latitudes.

| ID | Quantity | Prediction (direction, range) | Basis | Falsified if | Genuinely new information would be |
|---|---|---|---|---|---|
| PR1 | Peak Δρ/ρ at 400 km, P0 = 1e11 W, z0 = 300 km | positive; 5–100 % (central ~30 %) | Liu 2015 (50 GW over a larger auroral area → 14 %); our source is 2× the power on a smaller area | < 5 % or > 100 % | the magnitude per joule for a *mid-latitude, compact, prescribed-energy* source, which the cited studies do not report |
| PR2 | Linearity, 1e10 vs 1e11 W | response ratio 0.05–0.2 (≈ linear) | small-perturbation regime; Liu 2015 reports only slight nonlinearity | ratio outside 0.05–0.2 | a measured nonlinearity coefficient |
| PR3 | Time of peak at 400 km after onset | 0.5–2 h | Liu 2015 (~50 min); Sutton 2009 (< 2 h at mid/high latitude) | outside 0.25–3 h | — (replication) |
| PR4 | Sign structure | enhancement above the source; weaker depletion regions (≤ 1/3 of peak magnitude) around/below it; O/N2 decreases at the source | upwelling/expansion physics; storm O/N2 depletion | no depletion anywhere, or depletion larger than enhancement at 400 km | — (replication), unless depletion dominates orbit-averaged drag |
| PR5 | Spread | |Δρ/ρ| > 1 % beyond 3000 km of the source within 3 h of onset (remote response non-zero) | TAD/gravity-wave propagation (Gardner & Schunk 2010; Deng 2008) | remote |Δρ/ρ| < 0.1 % at all times | the fraction of the drag anomaly carried outside the source footprint |
| PR6 | Persistence | e-folding of the local peak 1–4 h after switch-off; the globally integrated mass excess above 400 km decays more slowly (> 3 h) | storm recovery times; spreading plus conduction/NO cooling | local e-folding < 0.5 h or > 8 h | the persistence of a localized anomaly vs its spreading, quantified against the prescribed `tau_relax_s` (600–3600 s) and κh range used in the baseline |
| PR7 | Deposition altitude (150 vs 300 km, same energy) | 400-km response within a factor of 3 of each other; direction not predicted | competing effects: larger column expansion vs larger heat capacity and faster conduction loss at 150 km | ratio outside 1/3–3 | the deposition-altitude dependence of orbit-altitude density per joule |
| PR8 | Grid convergence (10°×5° vs 5°×2.5°) | peak Δρ/ρ at 400 km changes < 30 %; integrated mass excess changes < 20 % | σh = 1000 km spans ≥ 2 cells on the coarse grid | change > 50 % | — (method check) |
| PR9 | Orbit-integrated extra drag, targets (pass within σh of the centre while the source is on), 400 km, 1e11 W | extra Δv over 12 h = 0.1–3 % of the natural Δv | peak δ ~ 30 % encountered for a few minutes per pass, plus spread | outside 0.01–10 % | — |
| PR10 | Selectivity (target / non-target mean extra Δv) | GITM ratio at least 3× smaller than for the static Gaussian fitted to the GITM peak | spreading makes the non-target response non-zero, whereas the prescribed patch gives ~0 off-footprint | GITM ratio ≥ prescribed ratio | **candidate new coupled result**: by how much self-consistent transport erodes selectivity relative to the prescribed field |
| PR11 | GITM vs fitted prescribed patch, target-group extra Δv | same order (ratio 0.3–3); GITM larger because the anomaly persists and moves | | ratio outside 0.1–10 | how much of the drag is gained or lost by replacing a prescribed field with a self-consistent one |
| PR12 | Energy cost of the baseline's assumed anomalies | a δ ≳ 1 (doubling) over σh ~ 1000 km at 400 km would need ≳ 1e11–1e12 W for ≳ 1 h, i.e. storm-scale Joule heating; the baseline's δ ≥ 2 scenarios lie outside what a 1e11 W source produces | PR1 extrapolated linearly | a 1e11 W source gives δ ≥ 1 | a physically anchored energy cost per unit δ, replacing the baseline's hydrostatic lower bound (5.80e7 W) |

Priority for novelty: PR10–PR12 (coupled results) > PR6–PR7 (extensions) >
PR1–PR5, PR8 (replications/method checks).
