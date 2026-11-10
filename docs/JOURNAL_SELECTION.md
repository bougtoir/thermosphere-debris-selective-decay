# Journal selection after the G5 contribution gate

Inputs archived under `data/raw/journal/` (ledger `LEDGER.jsonl`). The first Scimago fetch (2026-11-09) used
source ids that resolve to unrelated journals; those files are kept but marked in the ledger and were not used.
The corrected pages are `scimago_*_sid<id>_20261110.txt`.

Filter (standing author preference): Q1, no mandatory author charge (hybrid subscription route acceptable),
scope covering both thermospheric physics and orbital-debris drag.

| Journal | Scope fit | Scimago 2025 | Mandatory charge | Reference style | Decision |
|---|---|---|---|---|---|
| Acta Astronautica (Elsevier, IAA) | space technology and operations incl. debris remediation; prior debris-drag and laser-removal papers cited here appeared there | Q1 Aerospace Engineering (SJR 1.078) | none (hybrid; OA optional) | numbered, square brackets, order of appearance | **selected** |
| JGR Space Physics (AGU) | strongest physics fit | — | base publication fee for subscription route (`agu_publication_fees_20261109.txt`) | author–year | excluded (mandatory fee) |
| J. Atmos. Sol.-Terr. Phys. (Elsevier) | thermosphere physics; debris angle peripheral | Q2 | none | author–year, alphabetical | not selected (Q2) |
| J. Space Safety Engineering (Elsevier) | debris/safety | Q2 | none | — | not selected (Q2) |
| Advances in Space Research | — | Q1 | — | — | excluded: rejecting journal (AISR-D-26-03405) |

Acta Astronautica requirements applied in G6 (`acta_astronautica_guide_20261109.txt`): Research Paper ≤ 13,000
words including references (figure/table ≈ 300–400 words each); concise stand-alone abstract without references;
≤ 6 keywords; 3–5 highlights ≤ 85 characters each in a separate file; numbered sections; figure captions supplied
separately; numbered references in square brackets in order of appearance; competing-interest declaration;
declaration of generative-AI use placed before the references; data statement.
