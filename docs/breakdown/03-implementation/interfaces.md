---
id: INFO-012
type: info
title: Interfaces
summary: Public API surface, tree protocol, parameter contract, facade pattern, and mode semantics.
date: 2026-10-22
status: current
---

# Interfaces

## Public API Surface

`src/pyssp_standard/__init__.py` exports:

```python
__all__ = [
    "Component", "Connection", "Connector", "DefaultExperiment", "FMU",
    "FmuEntry", "LSRefExperiment", "LSRefExperimentResource", "LSRefExperiments",
    "LSRefManifest", "MappingEntry", "ModelDescription", "Parameter",
    "ParameterBinding", "ParameterMapping", "ParameterMappingReference",
    "ParameterSet", "SRMD", "SSB", "SSD", "SSM", "SSP", "SSV", "System",
    "get_repo_root", "LS_REF_EXTRA_DIR", "copy_resource_directory",
    "package_archive", "parameters_by_name", "resolve_parameter_mapping",
    "unpack_archive", "validate_component_fmu",
]
```

## Tree Protocol

`tree.py` publishes the version-neutral SSD tree as `@runtime_checkable`
protocols: `Connector`, `Connection`, `ParameterMappingReference`,
`ParameterBinding`, `DefaultExperiment`, `Element`, `Component`, `System`;
`Component` and `System` are mutually exclusive. Consumers annotate and
`isinstance`-check against them, never instantiate them. Documents are built
through facade methods: `SSD.new_system`, `System.add_component`,
`System.add_subsystem`, `System.add_connection`, `Element.add_connector`,
`Element.add_parameter_binding`, `SSV.create_parameter_set`,
`SSM.create_mapping`; `SSD` owns the SSP version. `add_parameter_binding` takes
an inline `mapping=` or an external `mapping_source=`, never a hand-built
reference. `SSD.flatten()` is the public flatten entry point; callers do not
import the codec or the operation.

## Parameter Contract

`parameters.py` is the version-neutral parameter surface:

- Protocols `Parameter`, `ParameterSet`, `MappingEntry`, `ParameterMapping`,
  satisfied structurally by the SSP1 and SSP2 models, which never import it.
- `parameters_by_name(set)` keys parameters by name;
  `resolve_parameter_mapping(parameters, mappings)` keys them by mapping
  target. Both are exported.
- `SSV.create_parameter_set()` and `SSM.create_mapping()` build in-memory
  documents at the default or an explicit version without file I/O.
- `SSV.add_parameter()`, `SSV.extend_parameters()`, `SSM.add_mapping()`
  delegate to the versioned model; `SSV.xml` is typed `ParameterSet`;
  `SSV.parameters_by_name()` works for SSP1 and SSP2.

Models do not import `parameters.py`; only facades, `__init__.py`, and
consumers do.

## Parameter Binding

`INFO-022` (Parameter Binding Interfaces) defines the split:
`SSD.bind_parameters()` and `SSD.target()` edit a document, while
`SSP.bind_parameters()` places archive resources and delegates.

## Facade Interface Pattern

All document facades share `XmlDocument[T]`:

```python
class XmlDocument(Generic[DocumentT]):
    def __init__(self, path, mode="r"):     # path + mode
    def __enter__(self) -> "XmlDocument":   # context manager
    def __exit__(self, exc_type, exc, tb):  # auto-save on success
    @property
    def xml(self) -> DocumentT:             # canonical model
    def check_compliance(self) -> bool:     # explicit validation
    def load_document(self) -> DocumentT:   # parse from file
    def save_document(self):                # serialize to file
    def from_xml(self, text):               # parse from string
```

## Mode Semantics

| Mode | Read | Edit | Create | Auto-save on exit |
|------|------|------|--------|-------------------|
| `r` | Yes | No | No | No |
| `a` | Yes | Yes | No | Yes (if no exception) |
| `w` | No | Yes | Yes | Yes (if no exception) |

## Evidence

- `src/pyssp_standard/__init__.py`: exports
- Each facade module: constructor, `_create_document()`, `xml` property
- `common/xml_document.py`: base class
- `common/document_runtime.py`: generic orchestration
- `common/archive_runtime.py`: `create_runtime()` dispatch
