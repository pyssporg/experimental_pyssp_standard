---
id: INFO-021
type: info
title: Backlog Gaps
summary: Known gaps and architectural tensions behind the improvement backlog.
date: 2026-06-10
status: current
---

# Backlog Gaps

Known gaps and architectural tensions behind the improvement backlog.

Candidates live in INFO-015; the package map lives in INFO-011.

## Gap Summary

| # | Gap | Category | Impact |
|---|-----|----------|--------|
| G1 | SSP2 codec/model/validation are empty | Missing impl | Cannot parse SSP2 documents |
| G2 | FMI3 codec/model/validation are empty | Missing impl | Cannot parse FMI3 documents |
| G3 | Generated binding paths referenced but absent | Dead metadata | Risk of ImportError |
| G4 | Facades hardcode codecs instead of version routing | Architecture | Adding version requires facade change |
| G5 | No end-user CLI | Missing feature | Python API only |
| G6 | No cross-standard integration tests | Test gap | Risk of regression |
| G7 | DocumentRuntime reference discovery untestable | Code quality | (resolved - IMP-002) |
| G8 | Specialized runtimes should be inlined | Code quality | (resolved - IMP-001) |
| G9 | EXTERNAL_REFERENCE_SPECS duplicated | Code quality | (resolved - IMP-003) |
| G10 | Loose coupling between facade and codec/validator | Architecture | Bypasses routing abstraction |
| G11 | SSP2 SSV registered but not implemented | Missing impl | Dead registration |
| G12 | ls_ref.py and ssd.py define near-identical runtimes | Code quality | (resolved - G12 merged into IMP-001) |
| G13 | No SSP2/FMI3 user docs | Doc gap | Unclear version support |
| G14 | Empty layer_example directory | Doc gap | (directory already removed) |
| G15 | SRMD/SSB not in quick-start | Doc gap | Hidden capability |
| G16 | No CLI docs | Doc gap | No discoverable CLI path |
| G17 | No SSP2/FMI3 tests | Test gap | No coverage |
| G18 | No dedicated document_runtime tests | Test gap | (resolved - IMP-007) |
| G19 | No benchmarks | Test gap | Performance regression risk |
| G20 | FMI2 ScalarVariable.value_reference typed as str instead of int | Type fidelity | Forces manual XML parsing for int access |
| G21 | FMI2 ScalarVariable.start typed as str only, not str\|float | Type fidelity | Loses numeric semantic for Real/Integer types |
| G22 | FMI2 interface capabilities untyped (dict[str,str] with string booleans) | Model completeness | Fragile string comparisons, no type safety |
| G23 | FMI2 metadata description/author/version not parsed or exposed | Model completeness | Information loss during parse-serialize round-trip |
| G24 | FMI2 ModelStructure dependencies typed as str rather than list[int] | Type fidelity | Every project must manually parse space-separated strings |
| G25 | Non-deterministic ZIP timestamps in archive packing | Missing feature | Non-reproducible builds in CI |

---

## Architectural Tensions (Key Insights)

1. **Version routing bypassed** — Facades import codec/validator classes
   directly instead of querying `version_routing.py`. The routing layer
   exists but is not the universal dispatch mechanism.

2. **DocumentRuntime subclass sprawl** — Resolved (IMP-001): `SsdRuntime` and
   `LSRefExperimentsRuntime` have been removed. Both are now direct uses of
   `DocumentRuntime[...]`.

3. **Reference specs duplicated** — Resolved (IMP-003): `EXTERNAL_REFERENCE_SPECS`
   moved to `common/reference_specs.py`.

4. **SSP2/FMI3 skeletons** — Directory structure exists for SSP2 and FMI3
   but has no implementation. The version routing already references SSP2 SSV.

---

*This backlog was initialized by the Improvement Workflow (iteration 1) on
2026-05-20. No files were modified during the analysis; all proposed changes
require explicit approval.*