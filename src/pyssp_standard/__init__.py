from pathlib import Path

from pyssp_standard.common.archive.archive import (
    copy_resource_directory,
    package_archive,
    unpack_archive,
)
from pyssp_standard.facades.fmu import FMU
from pyssp_standard.standard.ssp1.operations.ssd_fmu_iteration import FmuEntry
from pyssp_standard.facades.md import ModelDescription
from pyssp_standard.facades.ls_ref import LSRefExperiments, LSRefManifest, LS_REF_EXTRA_DIR
from pyssp_standard.standard.ls_ref.model import (
    LSRefExperiment,
    LSRefExperimentResource,
)
from pyssp_standard.facades.srmd import SRMD
from pyssp_standard.facades.ssb import SSB
from pyssp_standard.contracts.parameters import (
    MappingEntry,
    Parameter,
    ParameterMapping,
    ParameterSet,
    parameters_by_name,
    resolve_parameter_mapping,
)
from pyssp_standard.contracts.tree import (
    Component,
    Connection,
    Connector,
    DefaultExperiment,
    ParameterBinding,
    ParameterMappingReference,
    System,
)
from pyssp_standard.facades.ssd import SSD
from pyssp_standard.facades.ssm import SSM
from pyssp_standard.facades.ssp import SSP
from pyssp_standard.facades.ssv import SSV
from pyssp_standard.standard.ssp1.validation.ssd_fmu_validation import (
    validate_component_fmu,
)


def get_repo_root(*, file: str = "__SSP_REF_ROOT__") -> Path:
    current = Path(__file__).resolve()
    for candidate in (current.parent, *current.parents):
        marker = candidate / file
        if marker.exists():
            return candidate
    raise FileNotFoundError(f"Could not locate repository root marker '{file}' from {current}")


__all__ = [
    "Component",
    "Connection",
    "Connector",
    "DefaultExperiment",
    "FMU",
    "FmuEntry",
    "LSRefExperiment",
    "LSRefExperimentResource",
    "LSRefExperiments",
    "LSRefManifest",
    "MappingEntry",
    "ModelDescription",
    "Parameter",
    "ParameterBinding",
    "ParameterMapping",
    "ParameterMappingReference",
    "ParameterSet",
    "SRMD",
    "SSB",
    "SSD",
    "SSM",
    "SSP",
    "SSV",
    "System",
    "get_repo_root",
    "LS_REF_EXTRA_DIR",
    "copy_resource_directory",
    "package_archive",
    "parameters_by_name",
    "resolve_parameter_mapping",
    "unpack_archive",
    "validate_component_fmu",
]
