"""Public, version-neutral contract for parameter sets and parameter mappings.

The concrete SSP1 and SSP2 dataclasses satisfy these protocols structurally;
they never import this module. Consumers can therefore work with parameter sets
and mappings without importing ``pyssp_standard.standard.*``.

The resolution helpers live here rather than in ``standard/common`` because they
are expressed entirely in contract terms, and putting them in the common layer
would make that layer import the public API.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Protocol, runtime_checkable


@runtime_checkable
class Parameter(Protocol):
    name: str
    type_name: str
    attributes: Mapping[str, str]
    id: str | None
    description: str | None

    def renamed(self, name: str) -> Parameter: ...


@runtime_checkable
class ParameterSet(Protocol):
    name: str
    version: str
    parameters: Sequence[Parameter]
    units: Sequence[object]
    enumerations: Sequence[object]

    def add_parameter(
        self,
        parname: str,
        ptype: str = "Real",
        *,
        value: object = None,
        name: str | None = None,
        mimetype: str | None = None,
        unit: str | None = None,
    ) -> Parameter: ...

    def extend_parameters(self, parameters) -> list[Parameter]: ...


@runtime_checkable
class MappingEntry(Protocol):
    source: str
    target: str
    suppress_unit_conversion: bool | None


@runtime_checkable
class ParameterMapping(Protocol):
    version: str
    mappings: Sequence[MappingEntry]

    def add_mapping(
        self,
        source: str,
        target: str,
        *,
        suppress_unit_conversion: bool | None = None,
        transformation: object | None = None,
    ) -> MappingEntry: ...


def parameters_by_name(parameter_set: ParameterSet) -> dict[str, Parameter]:
    """Parameters keyed by name; a later duplicate replaces an earlier one."""
    return {parameter.name: parameter for parameter in parameter_set.parameters}


def resolve_parameter_mapping(
    parameters: Mapping[str, Parameter],
    mappings: Iterable[MappingEntry],
) -> dict[str, Parameter]:
    """Parameters keyed by mapping target, in mapping order.

    Raises:
        KeyError: When a mapping source is not present in ``parameters``.

    Later entries targeting the same target replace earlier ones.
    ``transformation`` and ``suppress_unit_conversion`` are not applied: the
    source parameter is copied unchanged except for ``name``. ``attributes`` and
    ``annotations`` are copied so no two results share mutable state.
    """
    resolved: dict[str, Parameter] = {}
    for mapping in mappings:
        try:
            source = parameters[mapping.source]
        except KeyError:
            raise KeyError(
                f"Parameter mapping source '{mapping.source}' "
                "is not present in the parameter set"
            ) from None
        resolved[mapping.target] = source.renamed(mapping.target)
    return resolved


__all__ = [
    "MappingEntry",
    "Parameter",
    "ParameterMapping",
    "ParameterSet",
    "parameters_by_name",
    "resolve_parameter_mapping",
]
