"""Parameter-binding editing for an SSD document.

Resolves the target element and appends one binding to it. The public facade
(:meth:`pyssp_standard.facades.ssd.SSD.bind_parameters`) delegates here; placing
external resources stays with the SSP archive layer.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping

from pyssp_standard.contracts.parameters import Parameter, ParameterMapping, ParameterSet
from pyssp_standard.standard.ssp1.model.ssd_model import Ssp1ParameterSet, Ssd1System
from pyssp_standard.contracts.tree import Component, Element, ParameterBinding, System


def resolve_target(system: System | None, target: str | None) -> System | Component:
    """Return *system*, or the element named by a dotted *target* path.

    Raises:
        ValueError: When the document has no system or a segment is empty.
        KeyError: When a segment is unknown, ambiguous, or not a system.
    """
    if system is None:
        raise ValueError("SSD document has no system")
    if target is None:
        return system
    parts = target.split(".")
    if any(not part for part in parts):
        raise ValueError(f"Invalid target path {target!r}")
    element: System = system
    for index, part in enumerate(parts):
        matches = [child for child in element.elements if child.name == part]
        if not matches:
            raise KeyError(f"No element '{part}' under '{element.name}'")
        if len(matches) > 1:
            raise KeyError(f"Element '{part}' is ambiguous under '{element.name}'")
        match = matches[0]
        if index == len(parts) - 1:
            return match
        if not isinstance(match, Ssd1System):
            raise KeyError(f"No system '{part}' under '{element.name}'")
        element = match
    raise ValueError(f"Invalid target path {target!r}")


def append_binding(
    element: Element,
    parameters: ParameterSet | Mapping[str, Parameter] | None,
    *,
    source: str | None,
    mapping: ParameterMapping | None,
    mapping_source: str | None,
    name: str | None,
    prefix: str | None,
) -> ParameterBinding:
    """Append one binding to *element* without merging into an existing set."""
    if mapping is not None and mapping_source is not None:
        raise ValueError("mapping and mapping_source are mutually exclusive")
    if source is not None:
        if parameters is not None:
            raise ValueError("source and parameters are mutually exclusive")
        if name is not None:
            raise ValueError("source and name are mutually exclusive")
        parameter_set = None
    else:
        if parameters is None:
            raise ValueError("parameters is required when source is absent")
        parameter_set = _parameter_set(parameters, name)
    return element.add_parameter_binding(
        source,
        prefix=prefix,
        parameter_set=parameter_set,
        mapping=mapping,
        mapping_source=mapping_source,
    )


def _parameter_set(
    parameters: ParameterSet | Mapping[str, Parameter],
    name: str | None,
) -> ParameterSet:
    """Return an independent embedded set named by *name* when given."""
    if isinstance(parameters, Mapping):
        return Ssp1ParameterSet(
            name=name or "parameters",
            version="1.0",
            parameters=list(parameters.values()),
        )
    document = copy.deepcopy(parameters)
    if name is not None:
        document.name = name
    return document


__all__ = ["append_binding", "resolve_target"]
