---
id: INFO-009
type: info
title: Layer Rules
summary: Per-layer responsibilities and the rules each layer must respect.
date: 2026-10-22
status: current
---

# Layer Rules


Each layer owns one concern. The rules below define what each layer may and may not do.

## Archive Layer

**Responsibility:** Open and save package containers (`.ssp`, `.fmu`), provide deterministic persistence, expose extracted paths and archive-relative resolution.

Rules:
- May handle directories, extraction, repacking, and file placement
- Must not parse schema-specific XML semantics
- Must not decide document meaning

## Schema and Binding Layer

**Responsibility:** Hold standard schemas and any generated/derived schema-shaped artifacts.

Rules:
- Schema-derived artifacts are internal
- Must not contain business logic
- Handwritten behavior belongs in codec, model, validation, or orchestration

## Codec Layer

**Responsibility:** Parse and serialize XML text. Isolate XML mechanics from workflow logic.

Rules:
- Codecs own document-shape translation
- Must not own archive I/O
- Must not own cross-file resolution

## Domain Model Layer

**Responsibility:** Define compact typed objects used by the rest of the system. Provide the canonical in-memory representation.

Rules:
- Models should reflect workflow concepts, not schema awkwardness
- Generated binding objects must not leak into model state
- Archive/session state must not leak into model state

## Validation Layer

**Responsibility:** Schema compliance checks and semantic validation.

Rules:
- Schema validation checks XML / document-shape compliance
- Semantic validation checks meaning, consistency, references, constraints
- Validation should stay representation-agnostic where possible

## Orchestration Layer

**Responsibility:** Coordinate multiple related artifacts in one session. Resolve cross-file references. Persist external artifacts in correct order.

Rules:
- Orchestration owns archive-relative resolution
- Orchestration owns multi-document persistence flow
- Must not re-implement XML parsing details already owned by codecs

## Public API Layer

**Responsibility:** Preserve the user-facing workflow. Keep file and session usage simple. Hide version-specific choices. Expose a small set of entry points.

Rules:
- Public facades should stay thin
- Editing helpers should delegate to the canonical model
- Persistence should delegate to document and orchestration layers
