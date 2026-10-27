"""Protocol conformance for the version-neutral SSD tree."""

from __future__ import annotations

from pyssp_standard import (
    Component,
    ParameterBinding,
    ParameterMappingReference,
    SSD,
    SSM,
    SSV,
    System,
)


def test_created_ssd_exposes_the_tree_protocols(tmp_path):
    path = tmp_path / "tree.ssd"

    with SSD(path, mode="w") as ssd:
        system = ssd.new_system("system")
        assert isinstance(system, System)
        assert not isinstance(system, Component)

        component = system.add_component(
            "component",
            source="resources/example.fmu",
            component_type="application/x-fmu-sharedlibrary",
            implementation="CoSimulation",
        )
        assert isinstance(component, Component)
        assert not isinstance(component, System)

        component.add_connector("x", "output", "Real")
        mapping = SSM.create_mapping([("gain", "component.x")])
        binding = component.add_parameter_binding(
            "resources/values.ssv",
            prefix="p",
            parameter_set=SSV.create_parameter_set("values"),
            mapping=mapping,
        )
        assert isinstance(binding, ParameterBinding)
        assert isinstance(binding.parameter_mapping, ParameterMappingReference)
        assert binding.parameter_mapping.mapping is mapping


def test_round_trip_preserves_tree_and_protocol_discrimination(tmp_path):
    path = tmp_path / "tree.ssd"

    with SSD(path, mode="w") as ssd:
        system = ssd.new_system("root")
        component = system.add_component(
            "component",
            source="resources/example.fmu",
            component_type="application/x-fmu-sharedlibrary",
            implementation="CoSimulation",
        )
        component.add_connector("x", "output", "Real")
        system.add_connector("y", "input", "Real")
        nested = system.add_subsystem("nested")
        nested.add_component("inner", source="resources/inner.fmu")
        system.add_connection(
            start_element="component",
            start_connector="x",
            end_connector="y",
        )
        ssd.set_default_experiment(start_time=0.0, stop_time=2.0)

    with SSD(path) as ssd:
        system = ssd.system
        assert isinstance(system, System)
        assert not isinstance(system, Component)
        assert [element.name for element in system.elements] == ["component", "nested"]

        component = system.find_component("component")
        assert isinstance(component, Component)
        assert not isinstance(component, System)
        assert [connector.name for connector in component.connectors] == ["x"]

        assert system.connections[0].start_element == "component"
        assert ssd.default_experiment.stop_time == 2.0


def test_parameter_construction_does_not_touch_the_filesystem(tmp_path):
    workdir = tmp_path / "in-memory"
    workdir.mkdir()

    SSV.create_parameter_set("set")
    SSM.create_mapping([("a", "b")])

    assert list(workdir.iterdir()) == []
