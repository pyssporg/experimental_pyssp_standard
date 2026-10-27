"""Semantic validation of an SSD component against an FMU model description."""

from __future__ import annotations

from pyssp_standard.standard.fmi2.model.model_description import (
    Fmi2ModelDescriptionDocument,
)
from pyssp_standard.standard.fmi3.model.model_description import (
    Fmi3ModelDescriptionDocument,
)
from pyssp_standard.standard.operations.fmi_interfaces import interface_types
from pyssp_standard.standard.ssp1.model.ssd_model import Ssd1Component

FmiModelDescription = Fmi2ModelDescriptionDocument | Fmi3ModelDescriptionDocument


def validate_component_fmu(
    component: Ssd1Component,
    model_description: FmiModelDescription,
    *,
    source: str,
    implementation: str | None = None,
) -> None:
    """Check that *component*'s interface is served by *model_description*.

    Connector names must be FMU variables, connector kinds must match the FMU
    causality, and the component implementation (or *implementation* when
    given) must be an interface the FMU offers. *source* labels the FMU in
    error messages.

    Raises:
        ValueError: On the first interface mismatch.
    """
    variables = {variable.name: variable for variable in model_description.variables}

    missing = sorted(
        {connector.name for connector in component.connectors} - set(variables)
    )
    if missing:
        preview = ", ".join(missing[:8])
        if len(missing) > 8:
            preview = f"{preview}, ..."
        raise ValueError(
            f"{component.name}: FMU {source} is missing variable(s) used by "
            f"the SSD: {preview}. SSD connector names must match the FMU "
            "modelDescription; rename the SysML ports/parameters or the FMU "
            "variables, or skip FMU validation."
        )

    declared = (
        implementation if implementation is not None else component.implementation
    )
    offered = interface_types(model_description)
    if declared and offered and declared.lower() not in {
        item.lower() for item in offered
    }:
        exposed = ", ".join(sorted(offered))
        raise ValueError(
            f"{component.name}: component implementation is '{declared}', "
            f"but {source} exposes '{exposed}'"
        )

    for connector in component.connectors:
        causality = getattr(variables[connector.name], "causality", None)
        if connector.kind and causality and connector.kind != causality:
            raise ValueError(
                f"{component.name}: connector '{connector.name}' is "
                f"'{connector.kind}' in the SSD but '{causality}' in {source}"
            )
