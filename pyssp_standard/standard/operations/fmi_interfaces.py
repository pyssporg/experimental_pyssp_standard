"""FMI interface types offered by a model description."""

from __future__ import annotations

_FMI3_INTERFACES = (
    ("model_exchange", "ModelExchange"),
    ("co_simulation", "CoSimulation"),
    ("scheduled_execution", "ScheduledExecution"),
)


def interface_types(model_description) -> set[str]:
    """Return the FMI interface types a model description offers.

    FMI 2 declares one ``interfaceType`` attribute; FMI 3 declares the offered
    interfaces as child elements.
    """
    declared = getattr(model_description, "interface_type", None)
    if declared:
        return {str(declared)}

    offered: set[str] = set()
    for field_name, interface in _FMI3_INTERFACES:
        if getattr(model_description, field_name, None) is not None:
            offered.add(interface)
    return offered
