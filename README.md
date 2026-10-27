# pyssp_standard

`pyssp_standard` is a Python package for inspecting and editing SSP-related files.

The current public entry points are:
- `SSP` for archive and directory workflows
- `SSD` for standalone system structure documents
- `SSM` for parameter mappings
- `SSV` for parameter sets
- `SRMD` for simulation resource meta data (compute resources, tool versions, licenses)
- `SSB` for signal dictionaries
- `FMU` and `ModelDescription` for FMI model archives and `modelDescription.xml`
- `LSRefExperiments`, `LSRefExperiment`, and `LSRefExperimentResource` for LS-REF experiments
- `package_archive` and `unpack_archive` for deterministic SSP/FMU archive I/O

The package is aimed at pre-processing, inspection, and controlled edits of SSP artifacts.

**Library boundary:** the preferred interchange is the SSP/FMI artifact itself.
When a Python object must cross, use only the public entry points and model
types listed above; internal codecs, schema bindings, and archive helpers are
not part of the public API.

## Install

```bash
pip install .
```

## Quick Start

Read and validate a standalone parameter set:

```python
from pyssp_standard import SSV

with SSV("parameters.ssv") as ssv:
    assert ssv.check_compliance() is True
    print(ssv.xml.parameters[0].name)
```

Open an SSP archive and work on `SystemStructure.ssd` in archive context:

```python
from pyssp_standard import SSP

with SSP("system.ssp", mode="r") as ssp:
    with ssp.system_structure() as ssd:
        print(ssd.xml.name)
```

## Documentation

- [Docs index](docs/index.md)
- [Getting started](docs/getting_started.md)
- [Python API workflows](docs/user/python_api.md)
- [Command reference](docs/command_reference.md)
- [Product breakdown](docs/breakdown/README.md) — architecture, capabilities, traceability
- [Code structure](docs/breakdown/03-implementation/code-structure.md)
- [Quick code lookup](docs/breakdown/03-implementation/interfaces.md)

## Notes

- Use `SSD(path)` for file-local SSD work.
- Use `SSP(path).system_structure()` when edits need archive-aware resolution of external `.ssv` and `.ssm` references.
- For SSD structure edits, prefer `ssd.system` as the canonical model entry point.
- Use `SSD.flatten()` for the public flatten operation; do not import the SSP1 codec or operation modules directly.
- Legacy and unsupported material is kept outside the main docs flow and should not be treated as the primary API surface.
