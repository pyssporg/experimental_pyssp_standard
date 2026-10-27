"""Public, version-neutral protocols for the SSD model tree."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Protocol, runtime_checkable

from pyssp_standard.parameters import ParameterMapping, ParameterSet


@runtime_checkable
class Connector(Protocol):
    element: str | None
    name: str
    kind: str
    type_name: str | None
    type_attributes: dict[str, str]


@runtime_checkable
class Connection(Protocol):
    start_element: str | None
    start_connector: str
    end_element: str | None
    end_connector: str


@runtime_checkable
class ParameterMappingReference(Protocol):
    source: str | None
    mapping: ParameterMapping | None


@runtime_checkable
class ParameterBinding(Protocol):
    source: str | None
    prefix: str | None
    parameter_set: ParameterSet | None
    parameter_mapping: ParameterMappingReference | None


@runtime_checkable
class DefaultExperiment(Protocol):
    start_time: float | None
    stop_time: float | None


@runtime_checkable
class Element(Protocol):
    name: str
    connectors: list[Connector]
    parameter_bindings: list[ParameterBinding]

    def add_connector(
        self,
        name: str,
        kind: str,
        type_name: str | None = None,
        *,
        type_attributes: Mapping[str, str] | None = None,
    ) -> Connector: ...

    def add_parameter_binding(
        self,
        source: str,
        *,
        prefix: str | None = None,
        parameter_set: ParameterSet | None = None,
        mapping: ParameterMapping | None = None,
        mapping_source: str | None = None,
    ) -> ParameterBinding: ...

    def extend_inline_parameterset(
        self,
        parameters,
        *,
        binding_name: str | None = None,
        prefix: str | None = None,
        mapping_source: str | None = None,
    ) -> ParameterBinding: ...


@runtime_checkable
class Component(Element, Protocol):
    source: str
    component_type: str | None
    implementation: str | None


@runtime_checkable
class System(Element, Protocol):
    elements: list[Component | System]
    connections: list[Connection]

    def add_component(
        self,
        name: str,
        *,
        source: str = "",
        component_type: str | None = None,
        implementation: str | None = None,
    ) -> Component: ...

    def add_subsystem(self, name: str) -> System: ...

    def add_connection(
        self,
        *,
        start_element: str | None = None,
        start_connector: str = "",
        end_element: str | None = None,
        end_connector: str = "",
    ) -> Connection: ...

    def iter_components(self, *, recursive: bool = False) -> Iterator[Component]: ...

    def find_component(self, name: str) -> Component: ...
