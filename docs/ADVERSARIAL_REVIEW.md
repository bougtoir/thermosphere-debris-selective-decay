# Final adversarial review (Phase 19)

Eight attack angles applied to the finished package. For each: the
criticism, and the concrete defense or fix implemented.

## 1. "Your propagator is too simple for lifetime claims"
Semi-analytic J2-secular + orbit-mean density is approximate. **Defense:**
Gate 2 validation against Cowell drag-only decay (<10% over 10 days at
250 km storm), energy conservation to 4e-15 under J2 (with U2 potential),
B-scaling check. Lifetime conclusions at 400+ km are orders-of-magnitude
statements, insensitive to the residual error.

## 2. "A tracking perturbation is physically impossible — results are vacuous"
Correct that it is not a mechanism — it is an *upper bound*, labeled as
such everywhere it appears. The contribution is showing that even the
upper bound is modest (mm/s per day) and that every realizable geometry
(static, advected, diffusing) sits orders of magnitude below it.

## 3. "MSIS climatology hides real density structure"
Lookup is orbit/LST/lat-averaged; the +15% background uncertainty is
Monte-Carlo propagated and appears as a small Sobol' index — i.e.,
results are robust to that approximation. Storm regime is represented
separately.

## 4. "Selectivity ratio is inflated by a denominator near zero"
Ratios are always reported beside absolute protected delta-v; the
near-identical-trajectory and diffuse-patch controls explicitly
demonstrate the ratio's failure modes (selectivity collapses to ~17 for
sigma_h=3000 km).

## 5. "Energy accounting is naive"
Deliberately so: it uses the *minimum* bound (heating fraction
delta/(1+delta), cp·dT over patch air mass). Any real deposition
mechanism is less efficient, so the bound strengthens — not weakens —
the transport-limited conclusion.

## 6. "Synthetic cases are cherry-picked"
Cases span B=5–200, 250–750 km, co-orbital and cross-track protected
objects, a 10-fragment cloud, and a negative-control altitude; the
2000-object factorial population underlies Phase 11's collapse. No
operational spacecraft appear anywhere.

## 7. "Optimization proves nothing with a 2-D search"
The optimizer explores (t0, duration) only to demonstrate that *timing*
is not the binding constraint — which the Phase 8 sweep confirms
independently. No claim of global optimality is made.

## 8. "Statistics are thin (MC n=256, Sobol' N=32)"
Justified by the near-linear response (Phase 11 collapse, R²=0.9999):
high-order structure is absent by construction evidence, so first-order
indices suffice for the boundary conclusions. Full-run config doubles
both if a reviewer insists.
