# ASR Section-Order Audit (Conclusions → References)

Editorial constraint: only Appendix / Acknowledgements / Data availability may appear between Conclusion and References.

Result: the only heading in that interval is "Data availability" (renamed from "Data and code availability" to the exact editorial category name; content unchanged — still covers code via repository pointer).
- No Appendix (none exists; not manufactured).
- No Acknowledgements (none required; not manufactured).
- No funding/declarations/competing-interests/code-availability subsections in the interval — disclosures live in docs/DECLARATIONS.md in the submission docs (declared disposition: submission-system fields, not manuscript text).
- "Figure captions" section remains after References per Elsevier end-matter layout — outside the constrained interval.
- Test: tests/test_editorial_format.py::test_section_order_conclusion_to_references.
