---
id: INFO-015
type: info
title: Improvement Backlog
summary: Open and done improvement candidates with priority and layer.
date: 2026-06-10
status: current
---

# Improvement Backlog

> architectural, documentation, and testing improvements identified during
> exploratory analysis.
>

---

## Overview

| Priority | Open | In Progress | Done | Total |
|----------|------|-------------|------|-------|
| High     | 1    | 0           | 7    | 8     |
| Medium   | 4    | 0           | 5    | 9     |
| Low      | 2    | 0           | 6    | 8     |
| **Total**| **7** | **0**       | **18**| **25**|

---

## Individual Candidates

| ID | Title | Priority | Layer | Status |
|----|-------|----------|-------|--------|
| IMP-001 | Consolidate DocumentRuntime subclasses | High | Orchestration | done |
| IMP-002 | Extract reference discovery from DocumentRuntime | High | Orchestration | done |
| IMP-003 | Unify EXTERNAL_REFERENCE_SPECS | High | Orchestration | done |
| IMP-004 | Route facades through version_routing | High | Public API / Versioning | done |
| IMP-005 | Implement SSP2 SSV stack | Medium | Version-Specific (SSP2) | done |
| IMP-006 | Reconcile generated-binding metadata | Medium | Versioning / Tools | done |
| IMP-007 | Add explicit test coverage for DocumentRuntime | Medium | Testing | done |
| IMP-008 | Remove empty layer_example directory | Low | Documentation | done |
| IMP-009 | Add SRMD and SSB to quick-start docs | Low | Documentation | done |
| IMP-010 | Fill FMI3 skeleton codec/model/validation | Low | Version-Specific (FMI3) | done |
| IMP-011 | Support nested `<System>` in SSD model and codec | High | Domain Model / Codec | done |
| IMP-012 | Add option to remove Model Exchange from ModelDescription | Low | Public API | done |
| IMP-013 | Flatten hierarchical SSD into single-level system structure | Low | Operations | done |
| IMP-014 | Version-aware SSV facade through version routing | High | Public API | proposed |
| IMP-015 | SSP2 SSV facade-level tests | Medium | Testing | proposed |
| IMP-016 | SSP2 SSV inline parameter set support in SSD facade | Low | Domain Model / Operations | proposed |
| IMP-017 | Automated standard version identification in XmlDocument | Medium | Public API / Versioning | proposed |
| IMP-018 | Bulk FMU import from directory via add_fmu_directory() | Low | Public API | proposed |
| IMP-019 | Lifecycle-safe FMU iteration over SSP components | Medium | Operations / Public API | proposed |
| IMP-020 | FMI2 model field type corrections (value_reference, start, unit, ModelStructure) | High | Domain Model / Codec (FMI2) | done |
| IMP-021 | FMI2 model metadata completeness (description, author, version, typed capabilities) | Medium | Domain Model / Codec (FMI2) | done |
| IMP-022 | Deterministic ZIP timestamps for reproducible archive builds | Low | Archive | done |
| IMP-028 | Formalize Reproducibility as a Non-Functional Requirement (NFR-001 / QA-001) | Medium | Archive (core), Quality Attributes (cross-cutting) | done |
| IMP-029 | Common layer structural review — Runtime, Archive, XML, Reference handling | Medium | Common | proposed |
| IMP-030 | Public parameter-set and parameter-mapping contract | High | Public API | done |

