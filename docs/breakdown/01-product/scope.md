---
id: INFO-004
type: info
title: Scope
summary: Artifact types in and out of scope, and the library boundary decision.
date: 2026-05-20
status: current
---

# Scope


## In Scope

| Artifact | Standards | Status |
|----------|-----------|--------|
| SSP (System Structure Package) — `.ssp` | SSP1 | Active |
| SSD (System Structure Description) — `.ssd` | SSP1 | Active |
| SSV (Parameter Set) — `.ssv` | SSP1, SSP2 | Active |
| SSM (Parameter Mapping) — `.ssm` | SSP1 | Active |
| SSB (Signal Dictionary) — `.ssb` | SSP1 | Active |
| SRMD (Simulation Resource MetaData) — `.srmd` | SSP1 | Active |
| FMU (Functional Mock-up Unit) — `.fmu` | FMI2 | Active |
| ModelDescription — `modelDescription.xml` | FMI2 | Active |
| LS-REF Manifest — `manifest.xml` | LS-REF (FMI3 layered std) | Active |
| LS-REF Experiments — `experiments.xml` | LS-REF (FMI3 layered std) | Active |

## Out of Scope (Current)

- SSP2 SSD and SSM document processing (SSP2 SSV read/write is active)
- FMI3 document processing beyond `modelDescription.xml` (FMI3 model description
  read/write is active)
- End-user CLI tool
- GUI or graphical editors
- FMU simulation or co-simulation runtime
- Performance benchmarking
- Cross-standard validation (e.g., FMI→SSP consistency)

## Boundary Decision

The library focuses on scriptable, layered artifact manipulation. It does not
aim to be a full SSP authoring environment. Archive I/O, XML parse/serialize,
in-memory models, validation, orchestration, and public API are separated into
distinct layers to support reuse and testability.

## Evidence

- `product-breakdown/index.md`: document types table with status
- `pyssp_standard/__init__.py`: exported public surface
- `02-architecture/quality-attributes.md`: layer status per standard family
- `04-verification/acceptance-criteria.md`: scope paragraph