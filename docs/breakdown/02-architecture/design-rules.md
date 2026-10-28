---
id: INFO-016
type: info
title: Design Rules
summary: Cross-cutting rules for library boundary, versioning, references, and placement.
date: 2026-10-22
status: current
---

# Design Rules

Cross-cutting rules that apply to every layer.

Layer-specific responsibilities live in INFO-009.

## Rules

### Library Boundary
- The preferred border is the SSP/FMI artifact itself.
- When a Python object must cross, expose only a documented public facade or
  model type from the package public surface.
- Internal codecs, schema bindings, and archive helpers stay internal unless a
  deliberate public API decision promotes them.
- Only `facades/*` and `contracts/*` are consumer-importable. `facades/` holds
  the context-managed entry points, `contracts/` the version-neutral protocols;
  `common/` is plumbing that facades and layers share, and `standard/` is the
  family/version stacks.

### Contract Independence
- `contracts/` must not import `pyssp_standard.standard`. The protocols are
  satisfied structurally by the versioned models; the dependency never runs the
  other way.

### Versioning
- Detect `(format, family, version)` once, route to the correct stack early
- Avoid scattered version checks in higher-level workflows
- Vary by version: XSD files, schema-target registrations, root codecs, validators, semantic handling
- Stay version-independent: archive/file runtime, orchestration flow, public editing workflow, shared utilities

### External References
- Keep one canonical model shape regardless of inline or external storage
- Codecs handle representation differences
- Standalone document facades remain file-local
- Orchestration resolves external files during archive-aware sessions

### Placement Guidance
- Archive mechanics → `common/archive/` helpers
- Version selection → `standard/version_routing.py`
- Standard-specific models → `standard/<family>/<version>/model/`
- Standard-specific codecs → `standard/<family>/<version>/codec/`
- Standard-specific validation → `standard/<family>/<version>/validation/`
- User-facing facades → `facades/` (`facades/ssv.py`, `facades/ssp.py`, etc.)
- Version-neutral protocols → `contracts/` (`contracts/tree.py`,
  `contracts/parameters.py`)
- Plumbing shared by facades and layers → `common/`

Before adding code, ask:
- Is this XML-shape logic, model logic, orchestration logic, or public facade logic?
- Does it belong to one standard version, or is it shared?
- Can it be pushed down into codec, model, or validation instead of growing the public facade?

## Practical Guidance

| Do | Don't |
|----|-------|
| Prefer extending the canonical model over adding parallel facade state | Put archive logic in codecs |
| Prefer orchestration for cross-file behavior | Put XML business logic in archive helpers |
| Prefer small registries for selecting version-specific stacks | Mix user-facing facade concerns with schema-specific parsing details |