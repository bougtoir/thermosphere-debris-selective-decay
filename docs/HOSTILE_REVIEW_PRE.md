# Pre-revision hostile review

Five independent adversarial reviews of the frozen state
(`pre-revision-checkpoint`, commit `67f6a72`) conducted before any manuscript
editing. Each reviewer was instructed to assume the manuscript is wrong until
the code and CSVs prove otherwise.

Severity: **CRITICAL** = invalidates a stated conclusion; **MAJOR** = a claim
is unsupported as written and requires reanalysis or substantial rewording;
**MINOR** = correct but imprecise or incomplete; **COSMETIC** = presentation.

## Issue register

| ID | Sev | Reviewer | Issue | Evidence | Files | Reanalysis? | Correction | Downstream |
|---|---|---|---|---|---|---|---|---|
| C1 | CRITICAL | R3 | Sobol' indices violate `S1 <= ST` (`delta_max`: S1 0.830 > ST 0.548) and every CI is wider than the index. The reported sensitivity ranking is sampling noise. | `results/tables/phase10_sobol.csv`; N=32 base = 256 evaluations for 6 factors | `scripts/phase10_uncertainty.py` | yes | converge the estimator over N = 256..2048, report CIs, never clip indices | Fig. UQ panel, Results 6, Abstract sensitivity sentence |
| C2 | CRITICAL | R3/R4 | Headline selectivity 1.2e80 (pair D) is the ratio of a target dv to a Gaussian tail evaluated ~50 sigma away, i.e. 1.3e-84 m/s. Presenting it as selectivity is a numerical artefact, not physics. | `results/tables/phase7_selectivity.csv` | `scripts/phase07_controls.py`, figures | yes | classify outcomes (true no-encounter / below numerical resolution / tail-nonzero / physical); lead with absolute dv and encounter status; ratio demoted to secondary | Fig. Pareto, Table selectivity, Abstract, Conclusion |
| C3 | CRITICAL | R1 | Lifetimes are reported as if physical, but `inf` comes from a 200-year integrator cap and 1826.5 d is simply the 5-year simulation horizon with no reentry. The manuscript states both "exceeds 200 years" and "under the 5-year horizon used" in the same sentence. | `scripts/phase01_feasibility_audit.py` (`return np.inf` at 200 yr); `phase6_outcomes.csv` lifetime 1826.5 d for all non-reentering objects | `scripts/build_manuscript.py`, Table 1 | no (relabel + re-render) | report right-censored / lower-bounded lifetimes explicitly; mark censored cells in Table 1 | Table 1, Results 1, Abstract |
| M1 | MAJOR | R2 | "41% of plausible (kappa, u) combinations" is stated as though a probability was computed. The grid is a uniform sweep of hand-chosen values; no distribution was sampled, and the value moves with grid choice. | `scripts/phase12_classification.py` uses `.mean()` over a fixed product grid | `scripts/phase12_classification.py`, `build_manuscript.py` | yes (sensitivity) | wording -> "41% of the surveyed parameter combinations"; add a grid-choice sensitivity table | Abstract, Results 5, Discussion transport |
| M2 | MAJOR | R2 | Horizontal eddy diffusivity range 1e3-1e6 m^2/s and winds 0-300 m/s are asserted without per-value provenance, yet they set the transport boundary that drives the paper's main negative conclusion. | `config`/script literals; references list lacks per-value mapping | `scripts/phase05_spreading.py`, `phase12_classification.py`, references | partly | cite each bound to thermospheric literature; show the boundary's sensitivity to the bounds | Results 5, Discussion, references |
| M3 | MAJOR | R1/R4 | The tracking bound dominates every favourable number in the paper (7.45e-3 vs 4.32e-6 m/s, a factor 1.7e3), but the text does not consistently mark it as an unrealizable upper bound, and the abstract quotes it alongside physical results. | `phase6_outcomes.csv`; `build_manuscript.py` mentions "upper bound" in one place only | manuscript, figures, abstract | no | uniform "idealized tracking upper bound" framing at every occurrence; decompose the 1.7e3 gap into exposure-time vs amplitude | Abstract, Results 2-3, Discussion, Conclusion |
| M4 | MAJOR | R3 | Pi collapse (R^2 = 0.9999) is presented as confirmation of the response law, but the predictor and the simulator evaluate the same drag equation; the collapse is dimensional bookkeeping, not validation. The prose group `dv*B/(rho*delta*v*T)` is also dimensionally wrong (missing `v`). | `scripts/phase11_scaling.py` (`pred = rho*d*v**2*T/(2B)`) vs `docs/PHASE_11_HANDOFF.md` prose | `scripts/phase11_scaling.py`, manuscript | no (re-derive + reword) | derive Pi from first principles, fix the group, state it as internal consistency / dimensional reduction | Results 8, Discussion |
| M5 | MAJOR | R4 | Uniform-vs-localized comparison uses the same `delta_max`, not matched exposure or matched energy, so "localization buys selectivity" partly reflects the matching convention. | `scripts/phase07_controls.py` (uniform delta=5 vs localized delta=5) | `scripts/phase07_controls.py` | yes | add matched target-exposure and matched-energy variants; report all three | Results 4, Discussion selectivity |
| M6 | MAJOR | R5 | Novelty as stated ("localized density enhancement accelerates decay") is textbook drag physics; ASR reviewers will reject on novelty unless the contribution is framed as a quantitative feasibility/exclusion boundary distinguished from storm-drag and drag-augmentation literature. | `docs/JOURNAL_AUDIT.md`, abstract | manuscript, `JOURNAL_AUDIT.md` | no | reframe around the five-axis exclusion framework; explicit comparison with differential drag, storm-drag studies, drag augmentation, ADR | Abstract, Intro, Discussion |
| M7 | MAJOR | R2 | `E_min` is computed as `m c_p dT` with no expansion work, conduction, radiation or coupling efficiency, but is discussed as an energy requirement. | `scripts/phase01_feasibility_audit.py` energy block | manuscript energy section | no | label as a strict thermodynamic lower bound; state that delivered engineering energy cannot be inferred | Results/Discussion energetics |
| m1 | MINOR | R1 | Relative-velocity treatment (co-rotating atmosphere) and the B convention `B = m/(Cd A)` are used consistently in code but never stated in the manuscript, so a reviewer cannot check the factor of 2 or the 1.0-1.1 rotation correction. | `src/orbits/fastprop.py` | manuscript Methods | no | state conventions and the rotation assumption explicitly | Methods |
| m2 | MINOR | R3 | The exposure integral uses a fixed 10 s fine step with no stated convergence check. | `fastprop.exposure_metrics` | Methods, Supplement | no | report the step-refinement check | Methods |
| m3 | MINOR | R2 | Patch diffusion uses amplitude ~ sigma0^2/sigma(t)^2 (2-D area dilution) while the patch is 3-D; vertical spreading/stratification is ignored. | `src/intervention/models.py` | Methods, Limitations | no | state the 2-D dilution assumption as a limitation | Methods, Limitations |
| m4 | MINOR | R4 | Negative controls exist but the co-orbital twin - the most damaging failure mode - is buried in a table rather than shown. | `phase10_negative_controls.csv` | figures | no | promote the co-orbital control to a figure panel | Figures, Results 7 |
| m5 | MINOR | R5 | Figure captions are not self-contained; several rely on body text for units and regime. | figures | `scripts/make_figures.py` | no | rewrite captions | Figures |
| x1 | COSMETIC | R5 | Mixed notation `delta` / `δ` / `delta_max` across text, tables and code. | manuscript | manuscript | no | unify | - |
| x2 | COSMETIC | R3 | CSVs carry full float64 repr (17 digits) into rendered tables. | tables | `build_manuscript.py` | no | round at render time | Tables |

## Reviewer summaries

**R1 - orbital mechanics.** The propagation itself is defensible: J2 secular
elements, orbit-averaged density with 72 samples per revolution, a Cowell/DOP853
cross-check, and a drag law consistent with `a = rho v^2 / (2B)`. Two things
would stop me recommending acceptance: lifetimes presented without censoring
(C3), and an upper bound reported next to physical results without a
consistent label (M3). The physical per-pass result - a micrometre-per-second
impulse from a single transit of a 200 km patch - is the honest headline, and
the paper should say so first.

**R2 - thermosphere / space weather.** The enhancement is imposed as a
prescribed multiplicative field; there is no neutral-gas energy equation, no
pressure response, no wind feedback. That is acceptable *as a surrogate* only
if the paper says so and does not quote transport numbers with implied
precision. The 41% figure (M1) and the diffusivity/wind provenance (M2) are the
weakest links, because the paper's central negative claim rests on them.
`E_min` (M7) must be labelled a lower bound.

**R3 - numerics / UQ.** The Sobol' analysis as submitted would be desk-rejected
by any UQ referee (C1): 256 evaluations for six factors, CIs larger than the
indices, and an impossible ordering. The 1e80 selectivity (C2) is the same
class of error in the opposite direction - reporting float arithmetic below any
physical resolution as a result. The Pi collapse (M4) is arithmetic, not
evidence. Fix these three and the numerical story is sound.

**R4 - skeptical debris remediation.** My question is simple: how much does a
real object actually lose? The answer in this dataset is ~4 micrometre/s per
event, against orbital velocities of 7.6 km/s - about ten orders of magnitude
below what remediation needs, and the paper should lead with that ratio. The
co-orbital control (m4) shows the selectivity premise fails exactly where
debris clouds live. Matched-exposure fairness (M5) must be settled before any
selectivity claim survives.

**R5 - ASR scope / novelty.** In scope for ASR (space debris, thermosphere,
orbital dynamics), but the novelty claim must change (M6). "Higher density -->
more drag" is not publishable; "here is the quantitative boundary, on five
independent axes, beyond which selective drag is excluded even under idealized
assumptions" is. The paper must position itself against differential drag,
geomagnetic-storm drag studies, drag augmentation devices and active debris
removal, and must not imply technological feasibility anywhere.

## Disposition

CRITICAL: C1 -> Phase 2, C2 -> Phase 3, C3 -> Phase 7.
MAJOR: M1/M2 -> Phase 4/6, M3 -> Phase 5/8, M4 -> Phase 11, M5 -> Phase 9,
M6 -> Phase 13, M7 -> Phase 10.
MINOR/COSMETIC are resolved in the Phase 15-17 manuscript synchronization.
