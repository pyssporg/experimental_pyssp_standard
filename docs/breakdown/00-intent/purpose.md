---
id: INFO-001
type: info
title: Purpose
summary: "Why the library exists: scriptable, layered inspection and editing of SSP/FMI artifacts."
date: 2026-10-22
status: current
---

# Purpose


## Product Purpose

`pyssp_standard` exists to provide a Python library for inspecting, creating,
and editing SSP-related artifacts (`.ssp` archives, `.ssd` system structure
descriptions, `.ssv` parameter sets, `.ssm` parameter mappings) and FMI-related
artifacts (`.fmu` archives, `modelDescription.xml`).

The library is aimed at pre-processing, inspection, and controlled edits — not
at being a full SSP authoring environment or simulation runtime. See `README.md`.

## Problem Statement

SSP (System Structure & Parameterization) and FMI (Functional Mock-up Interface)
are open standards for co-simulation and model exchange. Tooling for these
standards has been fragmented and hard to script. Users who need to:

- validate parameter sets before a simulation run
- inspect FMU archive contents programmatically
- compose an SSP from an FMU and parameter files
- automate pre-processing in CI pipelines

have lacked a focused, layered Python library that separates archive I/O from
XML parsing from domain logic.

## Goals

1. **Read and validate** SSP/FMI artifacts without proprietary tooling.
2. **Edit and create** artifacts with round-trip preservation (element order,
   annotations, extensions).
3. **Resolve cross-document references** in archive-aware workflows.
4. **Stay layered** — archive, codec, model, validation, orchestration, and
   public API each own one concern.
5. **Keep the border standard, or public.** The interchange format is the SSP
   artifact; when a consumer needs an object, it receives a documented public
   facade (`SSP`, `SSD`, `SSV`, `SSM`, `FMU`, `ModelDescription`, and their
   model types). Internal codecs and schema bindings do not cross.

## Non-Goals (Current)

- Full SSP authoring environment (no GUI, no graphical system editor).
- FMU simulation or co-simulation runtime.
- SSP2 SSD and SSP2 SSM support (SSP2 SSV read/write is implemented).
- FMI3 support beyond `modelDescription.xml` (FMI3 model description read/write
  is implemented).
- End-user CLI (Python API only).
- Performance benchmarks or large-scale processing.

## Evidence

- `README.md`: "a Python package for inspecting and editing SSP-related files"
- `02-architecture/layer-rules.md`: layered XML-document workflow
- `pyssp_standard/__init__.py`: public facades, model types, and the
  parameter-set/mapping contract in the exported surface
- `04-verification/acceptance-criteria.md`: behavioral requirements baseline