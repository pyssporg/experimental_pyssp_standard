---
id: INFO-019
type: info
title: Repository Map
summary: Navigational trees for the test suite and the documentation set.
date: 2026-06-10
status: current
---

# Repository Map

Navigational trees for tests and docs. The annotated package map lives in
INFO-011, the public surface in INFO-012, and the test strategy in TEST-001.

## Test Structure

```
pytest/
├── conftest.py                    # Shared fixtures
├── ssp1/
│   ├── codec/                     # XML round-trip tests
│   ├── facade/                    # Public API tests
│   └── orchestration/             # Archive-aware workflow tests
├── common/                       # Common layer tests (reference discovery, etc.)
├── fmi2/
│   ├── archive/                   # FMU workflow tests
│   ├── codec/                     # ModelDescription codec tests
│   └── facade/                    # ModelDescription facade tests
├── ls_ref/
│   ├── codec/                     # LS-REF codec tests
│   └── facade/                    # LS-REF facade tests
├── tools/                         # Schema target, validation, routing tests
└── legacy_unsupported/            # Out-of-maintenance tests
```

### Documentation Structure

```
docs/
├── index.md                    # Documentation router
├── getting_started.md          # Installation + first workflow
├── command_reference.md        # Dev commands (no CLI exists)
├── user/
│   └── python_api.md           # Python API examples
├── dev/
│   ├── repo_map.md             # Codebase orientation
│   ├── code_disposition.md     # Layer-to-file map
│   ├── architecture.md         # Internal layer boundaries
│   ├── repo_status.md          # Implementation reality
│   ├── guidelines.md           # Code/doc conventions
│   └── requirements.md         # Behavioral requirements
└── integrations/
    └── read_the_docs.md        # RTD publishing setup
```

