---
id: INFO-022
type: info
title: Parameter Binding Interfaces
summary: SSD edits parameter bindings and resolves targets; SSP places archive resources and delegates.
date: 2026-10-27
status: current
---

# Parameter Binding Interfaces

Two entry points share one binding implementation, split by concern: `SSD`
edits the document, `SSP` handles the archive.

## SSD (document editing, no I/O)

`SSD.bind_parameters(parameters=None, *, target, source, mapping,
mapping_source, name, prefix)` appends one binding and returns it:

- `parameters=` embeds a set: a `ParameterSet` is deep-copied; a
  `Mapping[str, Parameter]` becomes a new set named `name or "parameters"`.
  `name` renames the embedded set.
- `source=` records an external reference verbatim and excludes `parameters=`
  and `name=` (`ValueError`).
- `mapping=` embeds an SSM; `mapping_source=` references one; the two are
  mutually exclusive (`ValueError`).
- `target=` selects the root system (`None`), a nested system, or a component
  by dotted name; `prefix=` is stored verbatim.
- Read mode raises `RuntimeError("Cannot bind parameters in read mode")`.
- An empty segment, a document without a system, or an invalid combination
  raises `ValueError`; an unknown or ambiguous segment raises `KeyError`.
- Node creation goes through `Element.add_parameter_binding(source=None, ...)`;
  the facade never builds binding objects.

`SSD.target(path=None)` resolves the same dotted path and returns the root
system, a nested system, or a component without editing. Both methods share one
walk in `standard/ssp1/operations/ssd_binding.py`.

## SSP (archive placement, unchanged surface)

`SSP.bind_parameters(parameter_set, *, mapping, target, placement,
resolve_mapping, name, prefix)` keeps every file concern:

| Input | `external` | `inline` |
|---|---|---|
| `.ssv` path | copy to `resources/<file>` | read and embed |
| `ParameterSet` | serialize to `resources/<name>.ssv` | embed |
| `Mapping[str, Parameter]` | serialize to `resources/parameters.ssv` | embed |

1. read-only check and argument validation;
2. read the SSV/SSM and deep-copy it;
3. resolve the mapping when `resolve_mapping=True`;
4. externally: derive the resource name, copy or serialize the set, reject a
   clashing name (`FileExistsError`), and compute `source="resources/<name>"`;
5. `with self.system_structure() as ssd: ssd.bind_parameters(...)`.

A mapping path is copied to `resources/`; an in-memory `ParameterMapping` is
embedded. `name` names the external resource and the embedded set, each where it
applies; `prefix` is stored verbatim.

## Ownership

`standard/ssp1/operations/ssp_binding.py` owns file placement;
`standard/ssp1/operations/ssd_binding.py` owns target resolution and node shape.
The facades only delegate, and neither duplicates the other's assembly.

## Evidence

- `src/pyssp_standard/ssd.py`: `target()`, `bind_parameters()`
- `src/pyssp_standard/ssp.py`: `bind_parameters()`
- `standard/ssp1/operations/ssp_binding.py`, `ssd_binding.py`
- `tests/ssp1/facade/test_ssd_bind.py`,
  `tests/ssp1/orchestration/test_ssp_bind.py`
