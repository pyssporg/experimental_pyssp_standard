"""Parameter value resolution over SSV parameter sets and SSM mappings."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import replace

from pyssp_standard.standard.ssp1.model.ssm_model import Ssp1MappingEntry
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1Parameter, Ssp1ParameterSet


def parameters_by_name(parameter_set: Ssp1ParameterSet) -> dict[str, Ssp1Parameter]:
    """Parameters keyed by name; a later duplicate replaces an earlier one."""
    return {parameter.name: parameter for parameter in parameter_set.parameters}


def resolve_parameter_mapping(
    parameters: Mapping[str, Ssp1Parameter],
    mappings: Iterable[Ssp1MappingEntry],
) -> dict[str, Ssp1Parameter]:
    """Parameters keyed by mapping target, in mapping order.

    Raises:
        KeyError: When a mapping source is not present in ``parameters``.

    Later entries targeting the same target replace earlier ones.
    ``transformation`` and ``suppress_unit_conversion`` are not applied: the
    source parameter is copied unchanged except for ``name``. ``attributes`` and
    ``annotations`` are copied so no two results share mutable state.
    """
    resolved: dict[str, Ssp1Parameter] = {}
    for mapping in mappings:
        try:
            source = parameters[mapping.source]
        except KeyError:
            raise KeyError(
                f"Parameter mapping source '{mapping.source}' "
                "is not present in the parameter set"
            ) from None
        resolved[mapping.target] = replace(
            source,
            name=mapping.target,
            attributes=dict(source.attributes),
            annotations=list(source.annotations),
        )
    return resolved
