# Python API Workflows

This page is for users who want practical Python entry points without reading the full codebase.

## Public Entry Points

The main user-facing entry points are:
- `SSP` for archive-level or directory-level SSP workflows
- `SSD` for standalone `SystemStructure.ssd` files
- `SSM` for `.ssm` parameter mappings
- `SSV` for `.ssv` parameter sets
- `SRMD` for `.srmd` simulation resource meta data
- `SSB` for `.ssb` signal dictionaries
- `FMU` for `.fmu` archives or unpacked FMU directories
- `ModelDescription` for direct work on `modelDescription.xml`

## Common Facade Pattern

The document and archive facades are designed to be used as context managers.

Typical mode usage is:
- `mode="r"` to inspect existing content without writing changes
- `mode="a"` to edit existing content and persist changes on normal exit
- `mode="w"` to create new content and persist it on normal exit

## SSV

Use `SSV` for standalone parameter sets.

```python
from pyssp_standard import SSV

with SSV("parameters.ssv", "w") as ssv:
    ssv.xml.metadata.author = "tester"
    ssv.xml.add_parameter(parname="Weight", ptype="Real", value=20.4, unit="kg")
    ssv.xml.add_unit("kg", {"kg": 1})
```

## SSM

Use `SSM` for parameter mappings.

```python
from pyssp_standard.ssm import SSM, Ssp1Transformation

with SSM("mapping.ssm", "w") as ssm:
    ssm.xml.add_mapping("source", "target")
    ssm.xml.add_mapping(
        "scaled_source",
        "scaled_target",
        transformation=Ssp1Transformation("LinearTransformation", {"factor": 2, "offset": 0}),
    )
```

## SRMD

Use `SRMD` for simulation resource meta data.

```python
from pyssp_standard import SRMD
with SRMD("resources.srmd", mode="r") as srmd:
    print(srmd.xml)
```

## SSB

Use `SSB` for signal dictionaries.

```python
from pyssp_standard import SSB
with SSB("dictionary.ssb", mode="r") as ssb:
    print(ssb.xml)
```

## SSD

Use `SSD` for standalone system structure files.

```python
from pyssp_standard import SSD

with SSD("SystemStructure.ssd", mode="w") as ssd:
    system = ssd.new_system("system")
    ssd.rename("Demo")
    ssd.set_default_experiment(start_time=0.0, stop_time=1.0)

    component = system.add_component(
        "component",
        source="resources/example.fmu",
        component_type="application/x-fmu-sharedlibrary",
        implementation="CoSimulation",
    )
    component.add_connector("x", "output", "Real")
    system.add_connector("x", "output", "Real")
    system.add_connection(
        start_element="component", start_connector="x", end_connector="x"
    )
```

## SSP

Use `SSP` when the workflow is archive-aware or directory-aware.

```python
from pyssp_standard import SSP

with SSP("system.ssp", mode="a") as ssp:
    print(ssp.resources)

    with ssp.system_structure() as ssd:
        print(ssd.xml.name)
```

When you open `SystemStructure.ssd` through `SSP`, external parameter bindings and mappings can be resolved and written back in the same session.

### Populating a design-first SSP

`add_fmu()` creates a component. When the composition already exists — for
example because it was exported from SysML before the FMUs were built —
`attach_fmu()` pairs an FMU with an existing component instead.

```python
from pyssp_standard import SSP

with SSP("design.ssp", mode="a") as ssp:
    ssp.attach_fmu("source", "build/CsvSource.fmu")
    ssp.validate_fmu_interfaces()
```

`attach_fmu()` copies the FMU into `resources/`, points the component's
`source` at it, and by default checks that the component's connector names,
connector kinds, and implementation match the FMU. `validate_fmu_interfaces()`
runs the same check for every component whose resource is present; components
without a resource are skipped.

## FMU

Use `FMU` for `.fmu` archives or unpacked FMU directories.

### Reading an FMU

```python
from pyssp_standard import FMU

with FMU("component.fmu", mode="r") as fmu:
    print(fmu.binaries)

    with fmu.model_description as md:
        print(md.xml.model_name)
        print(len(md.xml.inputs))
```

### Creating an FMU from scratch

```python
from pathlib import Path
from pyssp_standard import FMU

binary = Path("my_controller.so")
binary.write_text("(shared library)")

with FMU("controller.fmu", mode="w") as fmu:
    fmu.add_binary(binary, platform="linux64")
    fmu.add_resource(Path("config.json"))
```

## ModelDescription

`md.interface_types` returns the FMI interfaces the model description offers
(`ModelExchange`, `CoSimulation`, `ScheduledExecution`), across FMI 2 and 3.

Use `ModelDescription` when you already have a direct path to `modelDescription.xml` and do not need FMU archive handling.

```python
from pyssp_standard import ModelDescription

with ModelDescription("modelDescription.xml", mode="r") as md:
    print(md.xml.model_name)
```

## Validation

Standalone document facades support compliance checks:

```python
with SSV("parameters.ssv") as ssv:
    assert ssv.check_compliance() is True
```

The same pattern applies to `SSM`, `SSD`, and model description workflows where supported by the facade.
