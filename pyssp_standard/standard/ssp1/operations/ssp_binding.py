"""Assembly of parameter bindings inside an SSP session.

Resolves the target element, places external resources, embeds in-memory
documents, attaches or resolves the parameter mapping, and returns the created
binding. The public facade (:meth:`pyssp_standard.ssp.SSP.bind_parameters`)
delegates here; policy such as one-root-binding rules stays with the caller.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pyssp_standard.parameters import (
    Parameter,
    ParameterMapping,
    ParameterSet,
    parameters_by_name,
    resolve_parameter_mapping,
)
from pyssp_standard.ssm import SSM
from pyssp_standard.ssv import SSV
from pyssp_standard.standard.ssp1.model.ssd_model import (
    Ssd1ParameterBinding,
    Ssd1ParameterMappingReference,
    Ssd1System,
)
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1ParameterSet
from pyssp_standard.standard.version_routing import (
    StandardVersion,
    get_codec_and_validator,
)
from pyssp_standard.tree import Element, ParameterBinding

if TYPE_CHECKING:
    from pyssp_standard.ssp import SSP

_PLACEMENTS = ("external", "inline")


def bind_parameters(
    ssp: SSP,
    parameter_set: str | Path | ParameterSet | Mapping[str, Parameter],
    *,
    mapping: str | Path | ParameterMapping | None = None,
    target: str | None = None,
    placement: Literal["external", "inline"] = "external",
    resolve_mapping: bool = False,
    name: str | None = None,
    prefix: str | None = None,
) -> ParameterBinding:
    """Bind one parameter set to a system or component and return the binding.

    Args:
        ssp: The open ``SSP`` session; only ``mode``, ``runtime``, and
            ``system_structure`` are used.
        parameter_set: An ``.ssv`` path, an in-memory parameter set, or
            already-resolved parameters keyed by name.
        mapping: An ``.ssm`` path or an in-memory mapping.
        target: Dotted path to the target element; ``None`` means the root
            system.
        placement: ``"external"`` copies or serializes the set under
            ``resources/``; ``"inline"`` embeds it in the SSD.
        resolve_mapping: Rename the parameters to their mapping targets and
            drop the mapping instead of referencing it.
        name: Parameter-set name; also names an external ``.ssv`` resource.
        prefix: Consumer-interpreted binding prefix, written verbatim.

    Returns:
        The created binding.

    Raises:
        RuntimeError: When the session was opened read-only.
        ValueError: On an invalid placement, ``resolve_mapping``, ``target``,
            or when the SSD has no system.
        KeyError: When a target segment is unknown or ambiguous.
        FileExistsError: When a resource name is taken by different bytes.
    """
    if ssp.mode == "r":
        raise RuntimeError("Cannot bind parameters in read mode")
    _validate_arguments(placement, resolve_mapping, target, name, prefix)

    parameter_path = (
        Path(parameter_set) if isinstance(parameter_set, (str, Path)) else None
    )
    mapping_path, mapping_document = _read_mapping(mapping, resolve_mapping)

    needs_document = placement == "inline" or resolve_mapping or parameter_path is None
    document = _read_parameter_set(
        parameter_set,
        parameter_path,
        needed=needs_document,
    )
    if name is not None and document is not None:
        document.name = name
    if resolve_mapping and mapping_document is not None:
        document = _resolved_document(document, mapping_document)

    mapping_source: str | None = None
    if mapping_path is not None and mapping_document is None:
        mapping_source = _place_mapping(ssp, mapping_path)
    inline_mapping = mapping_document if not resolve_mapping else None

    if placement == "external":
        resource_name = _external_resource_name(name, parameter_path, document)
        if parameter_path is not None and not resolve_mapping:
            _copy_resource(ssp, parameter_path, f"resources/{resource_name}")
        else:
            _write_parameter_set(ssp, document, f"resources/{resource_name}")
        with ssp.system_structure() as ssd:
            element = _select_target(ssd, target)
            return _append_binding(
                element,
                source=f"resources/{resource_name}",
                parameter_set=None,
                prefix=prefix,
                mapping=inline_mapping,
                mapping_source=mapping_source,
            )

    document = _require_document(document)
    with ssp.system_structure() as ssd:
        element = _select_target(ssd, target)
        return _append_binding(
            element,
            source=None,
            parameter_set=document,
            prefix=prefix,
            mapping=inline_mapping,
            mapping_source=mapping_source,
        )


def _validate_arguments(
    placement: object,
    resolve_mapping: object,
    target: object,
    name: object,
    prefix: object,
) -> None:
    if placement not in _PLACEMENTS:
        raise ValueError(
            f"Unsupported placement {placement!r}; expected one of {_PLACEMENTS}"
        )
    if not isinstance(resolve_mapping, bool):
        raise ValueError("resolve_mapping must be a bool")
    if target is not None and not isinstance(target, str):
        raise ValueError("target must be a string or None")
    if name is not None and not isinstance(name, str):
        raise ValueError("name must be a string or None")
    if prefix is not None and not isinstance(prefix, str):
        raise ValueError("prefix must be a string or None")


def _read_parameter_set(
    parameter_set: str | Path | ParameterSet | Mapping[str, Parameter],
    path: Path | None,
    *,
    needed: bool,
) -> ParameterSet | None:
    """Return an independent parameter set, or ``None`` when only a copy is needed."""
    if path is not None:
        if not needed:
            return None
        if not path.is_file():
            raise FileNotFoundError(f"Parameter set not found: {path}")
        with SSV(path, mode="r") as ssv:
            return copy.deepcopy(ssv.xml)
    if isinstance(parameter_set, Mapping):
        return Ssp1ParameterSet(
            name="parameters",
            version="1.0",
            parameters=list(parameter_set.values()),
        )
    if not isinstance(parameter_set, ParameterSet):
        raise TypeError(f"Unsupported parameter set input: {parameter_set!r}")
    return copy.deepcopy(parameter_set)


def _read_mapping(
    mapping: str | Path | ParameterMapping | None,
    resolve_mapping: bool,
) -> tuple[Path | None, ParameterMapping | None]:
    """Return the mapping path (when one was given) and its document when needed."""
    if mapping is None:
        return None, None
    if isinstance(mapping, (str, Path)):
        path = Path(mapping)
        if not path.is_file():
            raise FileNotFoundError(f"Parameter mapping not found: {path}")
        if not resolve_mapping:
            return path, None
        with SSM(path, mode="r") as ssm:
            return path, copy.deepcopy(ssm.xml)
    if isinstance(mapping, ParameterMapping):
        return None, copy.deepcopy(mapping)
    raise TypeError(f"Unsupported mapping input: {mapping!r}")


def _resolved_document(
    document: ParameterSet | None,
    mapping: ParameterMapping,
) -> ParameterSet:
    document = _require_document(document)
    resolved = resolve_parameter_mapping(
        parameters_by_name(document),
        mapping.mappings,
    )
    return replace(document, parameters=list(resolved.values()))


def _require_document(document: ParameterSet | None) -> ParameterSet:
    if document is None:
        raise RuntimeError("Parameter set document is not available")
    return document


def _external_resource_name(
    name: str | None,
    path: Path | None,
    document: ParameterSet | None,
) -> str:
    if name is not None:
        candidate = name
    elif path is not None:
        candidate = path.name
    elif document is not None:
        candidate = document.name
    else:
        candidate = "parameters"
    if Path(candidate).name != candidate:
        raise ValueError(
            f"Invalid resource name {candidate!r}: expected a bare file name"
        )
    return candidate if candidate.lower().endswith(".ssv") else f"{candidate}.ssv"


def _place_mapping(ssp: SSP, mapping_path: Path) -> str:
    """Copy the mapping resource and return its binding-relative source."""
    placed = _copy_resource(ssp, mapping_path, f"resources/{mapping_path.name}")
    return f"resources/{placed}"


def _copy_resource(ssp: SSP, source: Path, target_name: str) -> str:
    """Copy *source* through the session runtime, reusing identical bytes.

    Returns the resource name with the ``resources/`` prefix removed.
    """
    target = ssp.runtime.resolve(target_name)
    if target.exists():
        if target.is_file() and target.read_bytes() == source.read_bytes():
            return target_name.removeprefix("resources/")
        raise FileExistsError(
            f"Resource already exists with different content: {target_name}"
        )
    return ssp.runtime.add_file(source, target_name=target_name).removeprefix(
        "resources/"
    )


def _write_parameter_set(
    ssp: SSP,
    document: ParameterSet | None,
    target_name: str,
) -> str:
    """Serialize *document* into the session runtime, reusing identical bytes."""
    document = _require_document(document)
    codec_type, _ = get_codec_and_validator(
        StandardVersion(family="SSP", format="SSV", version=document.version)
    )
    data = codec_type().serialize(document).encode("utf-8")
    target = ssp.runtime.resolve(target_name)
    if target.exists():
        if target.is_file() and target.read_bytes() == data:
            return target_name
        raise FileExistsError(
            f"Resource already exists with different content: {target_name}"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target_name


def _select_target(ssd, target: str | None) -> Element:
    """Return the root system, or the element named by a dotted *target*."""
    if ssd.xml.system is None:
        raise ValueError("SSP system structure has no system")
    if target is None:
        return ssd.xml.system
    parts = target.split(".")
    if any(not part for part in parts):
        raise ValueError(f"Invalid target path {target!r}")
    element: Element = ssd.xml.system
    for index, part in enumerate(parts):
        final = index == len(parts) - 1
        matches = [child for child in element.elements if child.name == part]
        if not matches:
            raise KeyError(f"No element '{part}' under '{element.name}'")
        if len(matches) > 1:
            raise KeyError(f"Element '{part}' is ambiguous under '{element.name}'")
        match = matches[0]
        if not final and not isinstance(match, Ssd1System):
            raise KeyError(f"No system '{part}' under '{element.name}'")
        element = match
    return element


def _append_binding(
    element: Element,
    *,
    source: str | None,
    parameter_set: ParameterSet | None,
    prefix: str | None,
    mapping: ParameterMapping | None,
    mapping_source: str | None,
) -> ParameterBinding:
    """Append one binding to *element* without merging into an existing set."""
    binding = Ssd1ParameterBinding(
        source=source,
        prefix=prefix,
        parameter_set=parameter_set,
    )
    if mapping is not None or mapping_source is not None:
        binding.parameter_mapping = Ssd1ParameterMappingReference(
            source=mapping_source,
            mapping=mapping,
        )
    element.parameter_bindings.append(binding)
    return binding


__all__ = ["bind_parameters"]
