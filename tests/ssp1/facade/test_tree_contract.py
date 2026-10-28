"""Behavioural contract for the public SSD tree protocol."""

from __future__ import annotations

from pyssp_standard import (
    Connection,
    Connector,
    DefaultExperiment,
    ParameterBinding,
    ParameterMappingReference,
    SSD,
    SSM,
    SSV,
    System,
)


def _create_nested_tree(path):
    with SSD(path, mode="w") as ssd:
        root = ssd.new_system("root")
        root.add_component("first", source="first.fmu")
        outer = root.add_subsystem("outer")
        outer.add_component("second", source="second.fmu")
        inner = outer.add_subsystem("inner")
        inner.add_component("third", source="third.fmu")
        root.add_component("fourth", source="fourth.fmu")
    return path


def test_iter_components_yields_direct_children_in_document_order(tmp_path):
    with SSD(_create_nested_tree(tmp_path / "tree.ssd")) as ssd:
        assert isinstance(ssd.system, System)
        assert [element.name for element in ssd.system.elements] == [
            "first",
            "outer",
            "fourth",
        ]
        assert [component.name for component in ssd.system.iter_components()] == [
            "first",
            "fourth",
        ]


def test_iter_components_recursive_yields_parents_before_children(tmp_path):
    with SSD(_create_nested_tree(tmp_path / "tree.ssd")) as ssd:
        assert [component.name for component in ssd.system.iter_components(recursive=True)] == [
            "first",
            "second",
            "third",
            "fourth",
        ]


def test_public_tree_value_types_satisfy_their_protocols(tmp_path):
    path = tmp_path / "protocols.ssd"

    with SSD(path, mode="w") as ssd:
        system = ssd.new_system("root")
        connector = system.add_connector("u", "input", "Real")
        component = system.add_component("plant", source="plant.fmu")
        component.add_connector("y", "output", "Real")
        connection = system.add_connection(
            start_element="plant",
            start_connector="y",
            end_connector="u",
        )
        ssd.set_default_experiment(start_time=1.0, stop_time=3.0)

        assert isinstance(connector, Connector)
        assert connector.element is None
        assert connector.name == "u"
        assert connector.kind == "input"
        assert connector.type_name == "Real"
        assert connector.type_attributes == {}

        assert isinstance(connection, Connection)
        assert connection.start_element == "plant"
        assert connection.start_connector == "y"
        assert connection.end_element is None
        assert connection.end_connector == "u"

        assert isinstance(ssd.default_experiment, DefaultExperiment)
        assert ssd.default_experiment.start_time == 1.0
        assert ssd.default_experiment.stop_time == 3.0

    with SSD(path) as ssd:
        assert isinstance(ssd.system.connectors[0], Connector)
        assert isinstance(ssd.system.connections[0], Connection)
        assert isinstance(ssd.default_experiment, DefaultExperiment)


def test_parameter_binding_exposes_second_level_mapping_reference(tmp_path):
    path = tmp_path / "binding.ssd"
    mapping = SSM.create_mapping([("gain", "plant.gain")])

    with SSD(path, mode="w") as ssd:
        system = ssd.new_system("root")
        binding = system.add_parameter_binding(
            "values.ssv",
            prefix="p",
            parameter_set=SSV.create_parameter_set("values"),
            mapping=mapping,
        )

        assert isinstance(binding, ParameterBinding)
        assert isinstance(binding.parameter_mapping, ParameterMappingReference)
        assert binding.parameter_mapping.mapping is mapping

    with SSD(path) as ssd:
        parsed = ssd.system.get_parameter_bindings()[0]

        assert isinstance(parsed, ParameterBinding)
        assert isinstance(parsed.parameter_mapping, ParameterMappingReference)
        assert parsed.parameter_mapping.source is None
        assert parsed.parameter_mapping.mapping is not None
        assert parsed.parameter_mapping.mapping.mappings[0].target == "plant.gain"
