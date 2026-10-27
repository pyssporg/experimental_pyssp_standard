---
id: INFO-012
type: info
title: Interfaces
summary: Public API surface, facade pattern, mode semantics, and interface decisions.
date: 2026-10-22
status: current
---

# Interfaces


## Public API Surface

All public exports from `pyssp_standard/__init__.py`:

```python
__all__ = [
    "Component", "Connection", "Connector", "DefaultExperiment",
    "FMU", "FmuEntry", "LSRefExperiment", "LSRefExperimentResource",
    "LSRefExperiments", "LSRefManifest", "MappingEntry", "ModelDescription",
    "Parameter", "ParameterBinding", "ParameterMapping",
    "ParameterMappingReference", "ParameterSet",
    "SRMD", "SSB", "SSD", "SSM", "SSP", "SSV", "System",
    "get_repo_root", "LS_REF_EXTRA_DIR", "copy_resource_directory",
    "package_archive", "parameters_by_name", "resolve_parameter_mapping",
    "unpack_archive", "validate_component_fmu",
]
```

## Tree Protocol

`pyssp_standard/tree.py` publishes the version-neutral SSD tree: `Connector`,
`Connection`, `ParameterMappingReference`, `ParameterBinding`,
`DefaultExperiment`, `Element`, `Component`, and `System`. They are
`@runtime_checkable` protocols, so consumers annotate and `isinstance`-check
against them; `Component` and `System` are mutually exclusive. Tree classes are
never instantiated by consumers. Documents are built through facade methods:
`SSD.new_system`, `System.add_component`, `System.add_subsystem`,
`System.add_connection`, `Element.add_connector`,
`Element.add_parameter_binding`, `SSV.create_parameter_set`, and
`SSM.create_mapping`. `SSD` owns the SSP version. `add_parameter_binding`
carries either an inline `mapping=` or an external `mapping_source=` reference,
never a hand-built reference object.

`SSD.flatten()` is the public facade for replacing nested systems with one
flattened system; callers do not import the SSP1 codec or flatten operation.

## Parameter Contract

`pyssp_standard/parameters.py` is the public, version-neutral surface for
parameter sets and parameter mappings:

- Protocols: `Parameter`, `ParameterSet`, `MappingEntry`, `ParameterMapping`.
  They are `typing.Protocol` types, so SSP1 and SSP2 models satisfy them
  structurally and never import the contract.
- Functions: `parameters_by_name(parameter_set)` keys a set's parameters by
  name; `resolve_parameter_mapping(parameters, mappings)` keys the source
  parameters by mapping target. They live in `parameters.py` and are exported
  from the package surface.
- Facade construction: `SSV.create_parameter_set()` and `SSM.create_mapping()`
  build in-memory documents at the library default version, or an explicitly
  supported one, without touching the filesystem.
- Facade mutators: `SSV.add_parameter()`, `SSV.extend_parameters()`,
  `SSM.add_mapping()`. They delegate to the versioned model, and `SSV.xml` is
  typed as `ParameterSet`.
- `SSV.parameters_by_name()` works for SSP1 and SSP2 documents.
- `ParameterMapping` is the protocol; `SSM.create_mapping()` returns the
  concrete SSP1 dataclass, which stays internal.

Models do not import `parameters.py`; only the facades, the package
`__init__.py`, and consumers do.

## Parameter Binding Assembly

`SSP.bind_parameters()` composes one binding in an open session and returns it:

| Input | `external` | `inline` |
|---|---|---|
| `.ssv` path | copy to `resources/<file>` | read and embed |
| `ParameterSet` | serialize to `resources/<name>.ssv` | embed |
| `Mapping[str, Parameter]` | serialize to `resources/parameters.ssv` | embed |

`mapping=` attaches an SSM: a path is copied to `resources/`, an in-memory
`ParameterMapping` becomes an inline reference. `resolve_mapping=True` instead
renames the parameters to their mapping targets and drops the mapping. `target`
selects the root system, a nested system, or a component by dotted name.
`name` overrides the parameter-set name and the external file name; `prefix` is
stored verbatim for consumers. A resource name holding different bytes raises
`FileExistsError`; a read-mode session raises `RuntimeError`.

Assembly lives in `standard/ssp1/operations/ssp_binding.py`; the facade only
delegates. `SSP.add_external_parameterset()` is the compatibility entry point
and delegates to the same implementation. `SSD.extend_system_parameterset` and
`SSD.extend_component_parameterset` remain low-level helpers that extend an
existing inline set.

## Facade Interface Pattern

All document facades follow a common pattern via `XmlDocument[T]` base class:

```python
class XmlDocument(Generic[DocumentT]):
    def __init__(self, path, mode="r"):     # path + mode
    def __enter__(self) -> "XmlDocument":    # context manager
    def __exit__(self, exc_type, exc, tb):   # auto-save on success
    @property
    def xml(self) -> DocumentT:              # access canonical model
    def check_compliance(self) -> bool:      # explicit validation
    def load_document(self) -> DocumentT:    # parse from file
    def save_document(self):                 # serialize to file
    def from_xml(self, text):               # parse from string
```

## Mode Semantics

| Mode | Read | Edit | Create | Auto-save on exit |
|------|------|------|--------|-------------------|
| `r` | Yes | No | No | No |
| `a` | Yes | Yes | No | Yes (if no exception) |
| `w` | No | Yes | Yes | Yes (if no exception) |

## Key Implementation Decisions

| Decision | Location | Rationale |
|----------|----------|-----------|
| Direct `xml.etree.ElementTree` | All codec modules | Standard library, no external dependency |
| Dataclass models | `model/` modules per standard | Simple, testable, immutable-like |
| `XmlDocument[T]` generics | `common/xml_document.py` | Reusable lifecycle for all facades |
| `check_compliance()` explicit | `XmlDocument.__exit__` calls it | Never auto-validate without user knowledge |
| `DocumentRuntime` for cross-file | `common/document_runtime.py` | Keeps codecs simple, orchestration separate |
| Facades route through `get_codec_and_validator` | Each facade `__init__` | Codec and validator chosen by `standard/version_routing.py` |

## Evidence

- `pyssp_standard/__init__.py`: exports
- Each facade module: constructor, `_create_document()`, `xml` property
- `common/xml_document.py`: base class
- `common/document_runtime.py`: generic orchestration
- `common/archive_runtime.py`: `create_runtime()` dispatch
