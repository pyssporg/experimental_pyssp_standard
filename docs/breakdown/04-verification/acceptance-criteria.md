---
id: REQ-016
type: requirement
title: Acceptance Criteria
summary: Behavioural acceptance criteria and their verification.
date: 2026-10-23
status: current
---

# Acceptance Criteria


## Criteria (Inferred from Requirements and Tests)

### Document Lifecycle

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-001 | Reading an existing XML document shall produce a populated in-memory model | Codec tests: parse fixture → model != None |
| AC-002 | Creating a new document in `w` mode shall produce a minimal valid skeleton | Facade tests: create → serialize → validate |
| AC-003 | Editing a document in `a` mode and exiting normally shall persist changes | Facade + orchestration tests |
| AC-004 | Editing and exiting with an exception shall not persist changes | Implicit in `XmlDocument.__exit__` logic |
| AC-005 | `check_compliance()` shall not be called automatically on read | `XmlDocument.__enter__` does not validate |

### Round-Trip Preservation

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-006 | Element order shall be preserved for supported collections (parameters, connections, mappings, variables) | Codec tests compare element order before/after |
| AC-007 | Annotations and extensions shall be preserved in read-modify-write | Codec tests parsing same fixture |
| AC-008 | Line-oriented diff tools shall remain effective on serialized output | Element order guaranteed by codec design |

### File and Archive Handling

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-009 | `.ssp` archives and directories shall produce equivalent API behavior | `SSP` facade tests with both fixture types |
| AC-010 | Archive-backed SSPs shall use a temporary directory cleaned up on context exit | Archive runtime tests |
| AC-011 | Adding and removing resources in an SSP shall work in both archive and directory modes | `pytest/ssp1/orchestration/test_ssp.py` |

### Cross-Document Resolution

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-012 | External `.ssv`/`.ssm` references shall be resolved when referenced files exist and are parseable | Orchestration tests (indirect) |
| AC-013 | External references shall be preserved even when not resolved | Orphan references survive round-trip |
| AC-014 | Changes to resolved external documents shall persist to source files on save | Orchestration tests |

### Validation

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-015 | Valid reference documents shall pass compliance checks | Facade tests: `check_compliance()` returns True |
| AC-016 | SSV validation shall reject unknown custom units | `Ssp1SsvValidator` unit validation |
| AC-017 | SSV validation shall accept built-in bracketed unit syntax `[m]` | Unit tests in validator |
| AC-018 | SSP1 documents created or edited through the API shall remain compliant | Facade tests validate output |

### FMU Access

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-019 | FMU access shall expose binaries, documentation, and modelDescription | FMU archive tests |
| AC-020 | Archive-backed and directory-backed FMU access shall be equivalent | Both fixture types tested |
| AC-021 | Attaching an FMU to an existing component shall validate connectors, connector kinds, and implementation, then update the component source | `pytest/ssp1/orchestration/test_ssp_attach_fmu.py` |

### Deterministic Builds {#nfr-001}

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-DET-001 | Two `FMU.create()` calls with identical model description, binaries, and resources, using `fixed_timestamp=FMI_EPOCH`, produce identical SHA256 hashes | `pytest/fmi2/archive/test_fmu.py::test_fmu_create_deterministic` |
| AC-DET-002 | Two `SSP.__init__(path, mode="w")` contexts with identical FMU additions produce identical SHA256 hashes | `pytest/ssp1/archive/test_ssp_deterministic.py::test_ssp_create_deterministic` |
| AC-DET-003 | Two `FMU.package_as_ssp()` calls with the same FMU produce identical SHA256 hashes | `pytest/fmi2/archive/test_fmu_package_deterministic.py::test_fmu_package_as_ssp_deterministic` |
| AC-DET-004 | Two SSP archives adding the same resource file produce identical SHA256 hashes | `pytest/ssp1/archive/test_ssp_deterministic.py::test_ssp_add_resource_deterministic` |
| AC-DET-005 | XML documents created without calling `set_generation_date_and_time()` do not include a varying `generationDateAndTime` attribute; calling `set_generation_date_and_time(None)` always serializes `"2000-01-01T00:00:00Z"` | `pytest/common/test_generation_datetime_stability.py` (guardrail); `pytest/common/test_generation_date_time.py` (setter) |
