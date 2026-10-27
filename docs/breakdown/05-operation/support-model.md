---
id: INFO-014
type: info
title: Support Model
summary: Support scope, versioning, and what is not supported.
date: 2026-05-20
status: current
---

# Support Model


## Support Scope

`pyssp_standard` is an experimental software project. There is no formal support
contract, SLA, or dedicated support team. The project is maintained on a
best-effort basis.

## What Is Supported

- Issues and feature requests via the repository's issue tracker (if enabled)
- Pull requests following the workflow defined in `AGENTS.md`
- Documentation at `docs/` for onboarding and reference

## What Is Not Supported

- Guaranteed response times for issues
- Backward compatibility across experimental API changes
- Production deployment or SLAs
- Training or consulting

## Versioning

- No formal versioning or changelog yet (see `docs/archive/README.md`)
- API stability is not guaranteed; interfaces may change
- `02-architecture/quality-attributes.md` tracks current implementation state
- `03-implementation/code-structure.md`: "Interfaces do not need to be stable"
- `AGENTS.md`: "This is an experimental software, this means: Interfaces do not need to be stable"