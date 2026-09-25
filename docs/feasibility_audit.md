# Phase 1 — Feasibility Audit

## 1. Thermospheric densities 200-800 km (NRLMSISE-00, climatological mean)

Density varies by orders of magnitude with altitude and space weather; representative values (kg/m^3, moderate regime F10.7=140, ap=15):

- 200 km: rho = 2.46e-10 kg/m^3, H = 34 km
- 400 km: rho = 2.92e-12 kg/m^3, H = 61 km
- 600 km: rho = 1.24e-13 kg/m^3, H = 72 km
- 800 km: rho = 1.19e-14 kg/m^3, H = 94 km

## 2. Solar/geomagnetic variability

At 400 km the climatological-mean density ratio between storm (F10.7=200, ap=300) and quiet (F10.7=70, ap=4) regimes is 24.4x in this model. Observed storm-time enhancements of 300-800% at 400-500 km are documented (Bruinsma et al. 2006; Parker & Linares 2024; Berger et al. 2023).

## 3-5. Ballistic coefficients, natural drag, lifetimes

Representative B = m/(CdA): high-A/m debris ~3-10 kg/m^2, typical debris ~30-80, compact objects ~100-300 (cf. Moe & Moe 2005 for Cd ~2.0-2.4). Baseline circular-orbit lifetimes (moderate regime, exponential integration):

- 300 km, B=5: 2.3 d
- 300 km, B=30: 13.8 d
- 300 km, B=120: 55.4 d
- 400 km, B=5: 19.7 d
- 400 km, B=30: 118.2 d
- 400 km, B=120: 472.7 d
- 500 km, B=5: 119.0 d
- 500 km, B=30: 714.0 d
- 500 km, B=120: 2856.2 d
- 600 km, B=5: 585.7 d
- 600 km, B=30: 3514.0 d
- 600 km, B=120: 14056.0 d
- 800 km, B=5: 8168.6 d
- 800 km, B=30: 49011.4 d
- 800 km, B=120: >200 yr

## 6-7. Perturbation timescales and energy lower bound

Storm observations show global redistribution on ~hours timescales with regional anomalies 1000-2000 km (Bruinsma et al. 2006), implying a localized enhancement is eroded within hours at best. The thermodynamic lower bound E_min = m_air cp dT (with dT set by the isobaric density change) is tabulated in phase1_energy_bounds.csv; expansion work, conduction, advection, radiation and coupling inefficiency all act to increase the true energy requirement well above this optimistic bound.

Example: 300-km-radius-equivalent Gaussian patch at 400 km, delta=2 -> air mass 2.61e+05 kg, dT ~ 667 K, E_min = 1.75e+11 J per activation.

## 8-9. Differential drag and storm precedent

Density multipliers required for sustained uniform lifetime reductions are in phase1_scale_calculations.csv. Geomagnetic storms demonstrate that factors of several over days already cause operationally significant drag (Starlink Feb 2022 loss of ~38-40 satellites; Berger et al. 2023).

## 10. Existing approaches

Active debris removal reviews (Shan et al. 2016), laser nudging (Phipps et al. 2012), and drag-augmentation devices set the comparative baseline.

## GATE 1

**Classification: worth simulation (restricted regime: low altitude, low B).** Drag responds linearly to density, so uniform multipliers of order 2-10 already yield large lifetime changes at <=500 km for low-B objects; the open questions are localization survival under spreading, collateral drag, and energetics — exactly what later phases quantify.
