---
id: INFO-020
type: info
title: Round-Trip Preservation
summary: What read-modify-write preserves, and what stays outside the guarantee.
date: 2026-10-23
status: current
---

# Round-Trip Preservation

What read-modify-write preserves, and what stays outside the guarantee.

Acceptance criteria live in REQ-016.

## Round-Trip Preservation Detail

### Supported Now

- Read-modify-write preserves supported metadata across SSD, SSM, SSV, and FMI model description content
- Preserves annotation and extension content rather than discarding it
- Preserves input order of supported repeated child elements (parameters, connections, mappings, variables)
- Output preserves logical collection order so diff tools remain effective
- SSD preserves: connectors, connections, component attributes, default experiment data
- SSM preserves: mapping entries, transformation definitions
- SSV preserves: parameters, units, enumerations

Examples of preserved ordering:
- Input SSV with parameters `beta`, `alpha`, `gamma` → output preserves that logical parameter order
- Input SSD connections `B -> bus` before `A -> bus` → output preserves that connection order
- Input FMI `modelDescription.xml` variable/output ordering → output preserves that order

### Not Guaranteed Now

- XML lexical details not represented as ordered model data: attribute order, namespace prefix choice, indentation, line wrapping, serializer-chosen section ordering
- Example: attribute order `target="x" source="y"` may serialize as `source="y" target="x"`
- Example: namespace prefix spelling may differ
- Example: non-canonical section ordering may be normalized

### Future Compatibility Target

- Deterministic serializer-originated ordering for emitted tags and attributes
- Newly created/edited files should remain stable and reviewable across releases
- Once defined per document type, treated as explicit compatibility target with dedicated tests

## Scope Limitations (Not Currently Guaranteed)

- XML lexical details: attribute order, namespace prefix spelling, indentation
- Full byte-for-byte round trips
- Serializer-originated tag and attribute ordering (future compatibility target)

## Evidence

- `04-verification/traceability-matrix.md`: requirement-to-test mapping
- `tests/` test files: each test exercises one or more acceptance criteria
- `common/xml_document.py`: lifecycle implementation