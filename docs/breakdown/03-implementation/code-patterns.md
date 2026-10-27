---
id: INFO-017
type: info
title: Code Patterns
summary: Recurring implementation patterns and active code counts.
date: 2026-10-23
status: current
---

# Code Patterns

Recurring implementation patterns and active code counts.

The annotated package layout lives in INFO-011.

## Key Architectural Patterns

1. **XmlDocument base class** (`common/xml_document.py`): All document facades inherit
   from `XmlDocument[T]`, which provides context-managed lifecycle, load/save,
   compliance checking, and `_create_document()` creation.

2. **Version-routed codec selection**: facades resolve their codec and validator
   through `get_codec_and_validator()` in `standard/version_routing.py`:
   ```python
   class SSV(XmlDocument[Ssp1ParameterSet | Ssp2ParameterSet]):
       def __init__(self, path, mode="r", version=None):
           self._version = version or "1.0"
           self._codec, self._validator = self.get_codec_and_validator("SSP", "SSV")
   ```
   This pattern is consistent across `SSV`, `SSD`, `SSM`, `MD`, `SRMD`, `SSB`,
   and the LS-REF facades.

3. **Extracted reference discovery**: `discover_external_references()` in
   `common/reference_discovery.py` is a pure function extracted from
   `DocumentRuntime._iter_external_reference_targets`, making the tree-walking
   logic independently testable. `EXTERNAL_REFERENCE_SPECS` moved to
   `common/reference_specs.py`.

4. **Version routing registry**: `version_routing.py` registers `ParseStackSpec`s
   for 10 standard/format/version combinations and resolves each facade's codec
   and validator.

## Code Counts (Active Implementation)

| Layer | Files | Estimated LOC |
|-------|-------|---------------|
| Top-level facades | 9 | ~450 |
| Public contract (`parameters.py`) | 1 | ~120 |
| Common | 8 | ~500 |
| Standard/SSP1 | 22 | ~3,500 |
| Standard/FMI2 | 3 | ~500 |
| Standard/LS-REF | 6 | ~300 |
| Standard/other | 3 | ~200 |
| Tools | 1 | ~85 |
| **Total** | **~51** | **~5,600** |

## Evidence

- All modules listed above exist at the paths shown
- All facade `__init__` methods resolve codec/validator through `get_codec_and_validator`
- `parameters.py`: public parameter contract (IMD-002)
- `common/document_runtime.py`: reference discovery extracted to `reference_discovery.py` (IMP-002)