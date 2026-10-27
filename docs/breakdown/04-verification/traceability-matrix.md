---
id: TR-001
type: trace
title: Traceability Matrix
summary: Requirement-to-test mapping and coverage gaps.
date: 2026-05-20
status: current
---

# Traceability Matrix


> **Note:** This matrix is currently inferred from the codebase structure.
> Explicit requirement-to-test mapping does not yet exist as formal metadata.
> This file should be refined as requirements gain formal IDs.

| Req ID | Description | Test Location(s) | Coverage |
|--------|-------------|------------------|----------|
| REQ-001 | Read SSP archives | `tests/ssp1/orchestration/test_ssp.py`, `test_archive_tools.py` | Full |
| REQ-002 | Read-modify-write preserves order | `tests/ssp1/codec/*.py` | Full |
| REQ-003 | External .ssv/.ssm resolved in archive | `tests/ssp1/orchestration/test_ssp.py` | Partial (indirect) |
| REQ-004 | FMU exposes binaries, docs, modelDescription | `tests/fmi2/archive/test_fmu.py` | Full |
| REQ-005 | Compliance check explicit | All facade tests call `check_compliance()` | Full |
| REQ-006 | SSV read/create/edit | `tests/ssp1/facade/test_ssv.py`, `tests/ssp1/codec/test_ssv_xml_codec.py` | Full |
| REQ-007 | SSM read/create/edit | `tests/ssp1/facade/test_ssm.py`, `tests/ssp1/codec/test_ssm_xml_codec.py` | Full |
| REQ-008 | SSD read/create/edit | `tests/ssp1/facade/test_ssd.py`, `tests/ssp1/codec/test_ssd_xml_codec.py` | Full |
| REQ-009 | SSB read/create/edit | `tests/ssp1/facade/test_ssb.py`, `tests/ssp1/codec/test_ssb_xml_codec.py` | Full |
| REQ-010 | SRMD read/create/edit | `tests/ssp1/facade/test_srmd.py`, `tests/ssp1/codec/test_srmd_xml_codec.py` | Full |
| REQ-011 | FMI2 ModelDescription read/create/edit | `tests/fmi2/facade/test_model_description.py`, `tests/fmi2/codec/test_model_description_xml_codec.py` | Full |
| REQ-012 | LS-REF manifest and experiments | `tests/ls_ref/codec/test_ls_ref_xml_codec.py`, `tests/ls_ref/facade/test_ls_ref.py` | Full |
| REQ-013 | FMU-to-SSP packaging | `tests/ssp1/orchestration/test_ssp_add_fmu.py` | Full |
| REQ-014 | Version routing detection | `tests/tools/test_version_routing.py` | Full |
| REQ-015 | Schema target registration | `tests/tools/test_schema_targets.py` | Full |

## Coverage Gaps

| Missing Test Area | Related Requirements | Impact |
|-------------------|---------------------|--------|
| DocumentRuntime external reference discovery | REQ-003 | Resolved via integration tests only |
| Cross-standard validation (FMI→SSP) | Implicit | Risk of silent inconsistency |
| SSP2/FMI3 standards | None (no impl) | Dead routes in version_routing |
| Performance/benchmarks | None | Regression risk for large archives |

## Evidence

- All test files under `tests/`
- `04-verification/acceptance-criteria.md`: requirements baseline
- `tests/conftest.py`: fixture configuration for each test category