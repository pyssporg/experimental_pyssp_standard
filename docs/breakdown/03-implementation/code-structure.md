---
id: INFO-011
type: info
title: Code Structure
summary: Annotated package layout of the library.
date: 2026-10-23
status: current
---

# Code Structure

## Package Layout

Package sources live under `src/`; tests under `tests/` (see INFO-019).

```
src/pyssp_standard/
├── __init__.py              # Public API exports + get_repo_root()
├── ssp.py                   # SSP archive facade (context-managed)
├── ssd.py                   # SSD facade
├── ssv.py                   # SSV ParameterSet facade
├── ssm.py                   # SSM ParameterMapping facade
├── fmu.py                   # FMU archive facade + package_as_ssp()
├── md.py                    # ModelDescription facade
├── ls_ref.py                # LSRefManifest + LSRefExperiments
├── srmd.py                  # SRMD facade
├── ssb.py                   # SSB facade
├── parameters.py            # Public parameter-set/mapping contract + helpers
│
├── common/                  # Shared implementation
│   ├── archive.py           #   ZipFile unpack/repack
│   ├── archive_runtime.py   #   Context-managed archive runtime + create_runtime()
│   ├── directory_runtime.py #   Directory-based file runtime
│   ├── document_runtime.py  #   Cross-document reference resolution
│   ├── reference_specs.py   #   External reference specifications (SSV, SSM)
│   ├── reference_discovery.py #   Standalone external reference discovery
│   ├── xml_document.py      #   Base XmlDocument[T] facade (shared lifecycle)
│   └── xml_schema_validation.py  # XSD-backed validation
│
├── standard/                # Standard-specific logic
│   ├── version_routing.py   #   Document-root detection + ParseStackSpec registry
│   ├── unit_conversion.py   #   Base-unit definitions (minimal)
│   ├── common/              #   Shared standard helpers
│   │   └── utils.py
│   ├── operations/          #   Cross-standard composition
│   │   ├── fmi_interfaces.py
│   │   └── model_description_to_ssd.py
│   ├── ssp1/                #   [ACTIVE] Full SSP1
│   │   ├── codec/           #     6 codec modules
│   │   ├── model/           #     7 model modules
│   │   ├── operations/      #     5 operation modules
│   │   └── validation/      #     7 validation modules
│   ├── ssp2/                #   [PARTIAL] SSV only
│   │   ├── codec/           #     1 codec module
│   │   ├── model/           #     1 model module
│   │   └── validation/      #     1 validation module
│   ├── fmi2/                #   [ACTIVE] Full FMI2
│   │   ├── codec/           #     1 codec module
│   │   ├── model/           #     1 model module
│   │   └── validation/      #     1 validation module
│   ├── fmi3/                #   [PARTIAL] Model description only
│   │   ├── codec/           #     1 codec module
│   │   ├── model/           #     1 model module
│   │   └── validation/      #     1 validation module
│   └── ls_ref/              #   [ACTIVE] LS-REF
│       ├── codec/           #     2 codec modules
│       ├── model/           #     2 model modules
│       └── validation/      #     2 validation modules
│
├── tools/
│   └── schema_targets.py    #   Schema target registration (10 targets)
│
└── schema/                  # Vendored XSD files
    ├── SSP1/
    ├── SSP2/
    ├── FMI2/
    ├── FMI3/
    ├── SSP-LS-Traceability/
    └── _shared/
```
