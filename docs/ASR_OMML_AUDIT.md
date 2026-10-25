# OMML / Word-native equation audit

Inventory (all three docx at OOXML level):
- Before: m:oMath count = 0 in all docs. Substantive math existed as ASCII
  prose (v_rel, sigma_h, fractions, Π, Ω_E, ε).
- After: 12 m:oMath objects in manuscript.docx and
  manuscript_inline.docx; 0 in supplement (no formulas there — correct).

Converted (literal -> OMML with m:f/m:sSub/m:sSup/m:d):
1. −ρv_rel²/(2B)  2. B = m/(C_d A)  3. da/dt = −(aρv/B)(v_rel/v)²
4. v_rel/v = 1−Ω_E a cos(i)/v  5. ρ′ = ρ(1+δ)  6. σ_h² ← σ_h² + 2κt
7. Π = 2dvB/(ρδv_rel²T)  8. a = ρv_rel²/(2B)
9. exp[Lε/(H(1+ε))]  10. q = ln(1+δ)H/L  11. ε = q/(1−q)
12. Fig 5 caption predictor ρ·δ·v_rel²·T/(2B)

Not converted (by design, per scope): units (g/cm^3, kg/m^3), lone symbols
(delta, sigma_h, eps in prose), numeric results, and "(1+delta)" used as a
verbal factor. Implementation: scripts/build_manuscript.py builds OMML at
render time from literal->OMML map; reopen+PDF render verified (LibreOffice,
fractions/sub/superscripts/delimiters visible and editable in Word).
