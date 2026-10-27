from __future__ import annotations

import pytest
import shutil
from xml.etree import ElementTree as ET

from pyssp_standard import SSD
from pyssp_standard.standard.ssp1.model import Ssp1Annotation, Ssp1Parameter


def test_check_compliance_accepts_reference_fixture(embrace_ssd_fixture):
    with SSD(embrace_ssd_fixture) as ssd:
        assert ssd.check_compliance() is True


def test_create_round_trip(tmp_path):
    path = tmp_path / "test.ssd"

    with SSD(path, mode="w") as ssd:
        system = ssd.new_system("system")
        ssd.rename("Test SSD")
        ssd.set_default_experiment(start_time=0.0, stop_time=1.0)

        component = system.add_component(
            "component",
            source="resources/example.fmu",
            component_type="application/x-fmu-sharedlibrary",
            implementation="CoSimulation",
        )
        component.add_connector("x", "output", "Real")
        system.add_connector("x", "output", "Real")
        system.add_connection(
            start_element="component",
            start_connector="x",
            end_connector="x",
        )

    with SSD(path, mode="r") as ssd:
        assert ssd.xml.name == "Test SSD"
        assert ssd.xml.version == "1.0"
        assert ssd.default_experiment is not None
        assert ssd.default_experiment.start_time == 0.0
        assert ssd.default_experiment.stop_time == 1.0
        assert ssd.system is not None
        assert len(ssd.system.elements) == 1
        assert len(ssd.system.connectors) == 1
        assert len(ssd.system.get_connections()) == 1
        assert ssd.system.elements[0].component_type == "application/x-fmu-sharedlibrary"


def test_context_exit_validates_before_saving_invalid_document(tmp_path):
    path = tmp_path / "invalid.ssd"

    with pytest.raises(ValueError, match="SSD XML failed XSD validation"):
        with SSD(path, mode="w") as ssd:
            ssd.rename("Invalid SSD")
            system = ssd.new_system("system")
            system.add_connector(
                "x", "output", "Real", type_attributes={"start": "0.0"}
            )

    assert not path.exists()


def test_editing_connections_preserves_compliance(tmp_path, embrace_ssd_fixture):
    path = tmp_path / "fixture.ssd"
    shutil.copy(embrace_ssd_fixture, path)

    with SSD(path, "a") as ssd:
        system = ssd.system
        system.add_connection(
            start_element="house",
            start_connector="garage",
            end_element="work",
            end_connector="parking",
        )
        removed = next(
            connection
            for connection in system.connections
            if connection.start_element == "Atmos"
            and connection.start_connector == "Tamb"
            and connection.end_element == "Consumer"
            and connection.end_connector == "Tamb"
        )
        system.remove_connection(removed)
        assert ssd.check_compliance() is True

    with SSD(path) as ssd:
        assert len(ssd.system.list_connectors(parent="Consumer")) == 76
        assert any(
            connection.start_element == "house"
            for connection in ssd.system.get_connections()
        )


def test_standalone_facade_preserves_external_binding_reference_without_resolution(mixed_ssd_fixture):
    with SSD(mixed_ssd_fixture) as ssd:
        assert len(ssd.system.get_parameter_bindings()) == 2
        external_binding = next(
            binding
            for binding in ssd.system.get_parameter_bindings()
            if binding.source is not None
        )
        assert external_binding.prefix == "Controller"
        assert external_binding.source == "external_values.ssv"
        assert external_binding.parameter_set is None
        assert external_binding.parameter_mapping is None


def test_list_connectors_returns_component_connectors(embrace_ssd_fixture):
    with SSD(embrace_ssd_fixture) as ssd:
        found = ssd.system.list_connectors(parent="Consumer")

    assert len(found) == 76


def test_round_trip_preserves_metadata_and_connector_annotations(tmp_path):
    path = tmp_path / "annotations.ssd"

    with SSD(path, mode="w") as ssd:
        system = ssd.new_system("system")
        ssd.rename("Annotated SSD")
        ssd.xml.metadata.annotations.append(
            Ssp1Annotation(
                type_name="com.example.doc",
                elements=[ET.fromstring('<doc xmlns="urn:test">ssd</doc>')],
            )
        )
        connector = system.add_connector("x", "output", "Real")
        connector.annotations.append(
            Ssp1Annotation(
                type_name="com.example.connector",
                elements=[ET.fromstring('<connectorNote xmlns="urn:test">signal</connectorNote>')],
            )
        )

    with SSD(path, mode="r") as ssd:
        assert ssd.xml.metadata.annotations[0].elements[0].text == "ssd"
        assert ssd.system is not None
        assert ssd.system.connectors[0].annotations[0].type_name == "com.example.connector"
        assert ssd.system.connectors[0].annotations[0].elements[0].text == "signal"


def test_component_can_extend_first_inline_parameterset_from_mapping(tmp_path):
    path = tmp_path / "inline_parameters.ssd"

    with SSD(path, mode="w") as ssd:
        system = ssd.new_system("system")
        component = system.add_component("component", source="resources/example.fmu")
        component.extend_inline_parameterset(
            [
                ("gain", 2.5),
                Ssp1Parameter(name="enabled", type_name="Boolean", attributes={"value": "true"}),
            ]
        )
        component.extend_inline_parameterset({"offset": -1})

    with SSD(path, mode="r") as ssd:
        component = ssd.system.elements[0]
        binding = component.parameter_bindings[0]

        assert binding.parameter_set is not None
        assert binding.parameter_set.name == "component_parameters"
        assert len(component.parameter_bindings) == 1
        assert [(parameter.name, parameter.attributes["value"]) for parameter in binding.parameter_set.parameters] == [
            ("gain", "2.5"),
            ("enabled", "true"),
            ("offset", "-1"),
        ]


def test_components_can_extend_their_inline_parametersets(tmp_path):
    path = tmp_path / "facade_parameters.ssd"

    with SSD(path, mode="w") as ssd:
        system = ssd.new_system("system")
        step = system.add_component("step", source="resources/step.fmu")
        gain = system.add_component("gain", source="resources/gain.fmu")

        step.extend_inline_parameterset({"height": 2.0, "offset": 1.0})
        gain.extend_inline_parameterset({"k": 3.0})

    with SSD(path, mode="r") as ssd:
        step = next(element for element in ssd.system.elements if element.name == "step")
        gain = next(element for element in ssd.system.elements if element.name == "gain")

        assert step.parameter_bindings[0].parameter_set is not None
        assert gain.parameter_bindings[0].parameter_set is not None
        assert [(parameter.name, parameter.attributes["value"]) for parameter in step.parameter_bindings[0].parameter_set.parameters] == [
            ("height", "2.0"),
            ("offset", "1.0"),
        ]
        assert [(parameter.name, parameter.attributes["value"]) for parameter in gain.parameter_bindings[0].parameter_set.parameters] == [
            ("k", "3.0"),
        ]


def test_ssd_can_extend_system_inline_parameterset(tmp_path):
    path = tmp_path / "system_parameters.ssd"

    with SSD(path, mode="w") as ssd:
        ssd.new_system("system")

        ssd.system.extend_inline_parameterset(
            {
                "step.height": 2.0,
                "gain.k": 3.0,
            },
            binding_name="simulation_parameters",
        )
        ssd.system.extend_inline_parameterset({"step.offset": -1.0})

    with SSD(path, mode="r") as ssd:
        assert ssd.system is not None
        binding = ssd.system.get_parameter_bindings()[0]

        assert len(ssd.system.get_parameter_bindings()) == 1
        assert binding.parameter_set is not None
        assert binding.parameter_set.name == "simulation_parameters"
        assert [(parameter.name, parameter.attributes["value"]) for parameter in binding.parameter_set.parameters] == [
            ("step.height", "2.0"),
            ("gain.k", "3.0"),
            ("step.offset", "-1.0"),
        ]


def test_extend_inline_parameterset_attaches_and_overwrites_mapping_source(tmp_path):
    path = tmp_path / "mapping_source.ssd"

    with SSD(path, mode="w") as ssd:
        ssd.new_system("system")

        ssd.system.extend_inline_parameterset(
            {"step.height": 2.0}, mapping_source="resources/x.ssm"
        )
        binding = ssd.system.get_parameter_bindings()[0]
        assert binding.parameter_mapping is not None
        assert binding.parameter_mapping.source == "resources/x.ssm"

        ssd.system.extend_inline_parameterset(
            {"step.offset": -1.0}, mapping_source="resources/y.ssm"
        )
        assert binding.parameter_mapping.source == "resources/y.ssm"

    with SSD(path, mode="r") as ssd:
        binding = ssd.system.get_parameter_bindings()[0]

        assert len(ssd.system.get_parameter_bindings()) == 1
        assert binding.parameter_mapping is not None
        assert binding.parameter_mapping.source == "resources/y.ssm"


def test_round_trip_preserves_structural_order_in_serialized_xml(tmp_path):
    path = tmp_path / "ordered.ssd"
    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<ssd:SystemStructureDescription xmlns:ssc="http://ssp-standard.org/SSP1/SystemStructureCommon" xmlns:ssd="http://ssp-standard.org/SSP1/SystemStructureDescription" version="1.0" name="Ordered SSD">
  <ssd:System name="system">
    <ssd:Connectors>
      <ssd:Connector kind="output" name="beta_bus"><ssc:Real /></ssd:Connector>
      <ssd:Connector kind="output" name="alpha_bus"><ssc:Real /></ssd:Connector>
    </ssd:Connectors>
    <ssd:Elements>
      <ssd:Component source="resources/beta.fmu" name="beta_component" type="application/x-fmu-sharedlibrary"><ssd:Connectors><ssd:Connector kind="output" name="beta_out"><ssc:Real /></ssd:Connector></ssd:Connectors></ssd:Component>
      <ssd:Component name="alpha_component" source="resources/alpha.fmu" type="application/x-fmu-sharedlibrary"><ssd:Connectors><ssd:Connector name="alpha_out" kind="output"><ssc:Real /></ssd:Connector></ssd:Connectors></ssd:Component>
    </ssd:Elements>
    <ssd:Connections>
      <ssd:Connection endConnector="beta_bus" startConnector="beta_out" startElement="beta_component" />
      <ssd:Connection startElement="alpha_component" startConnector="alpha_out" endConnector="alpha_bus" />
    </ssd:Connections>
  </ssd:System>
</ssd:SystemStructureDescription>
""",
        encoding="utf-8",
    )

    with SSD(path, mode="a"):
        pass

    with SSD(path, mode="r") as ssd:
        assert [element.name for element in ssd.system.elements] == ["beta_component", "alpha_component"]
        assert [connector.name for connector in ssd.system.connectors] == ["beta_bus", "alpha_bus"]
        assert [connection.start_element for connection in ssd.system.get_connections()] == [
            "beta_component",
            "alpha_component",
        ]

    xml_text = path.read_text(encoding="utf-8")
    assert xml_text.index('name="beta_component"') < xml_text.index('name="alpha_component"')
    assert xml_text.index('name="beta_bus"') < xml_text.index('name="alpha_bus"')
    assert xml_text.index('startElement="beta_component"') < xml_text.index('startElement="alpha_component"')


def test_new_system_keeps_the_document_name(tmp_path):
    path = tmp_path / "named.ssd"

    with SSD(path, mode="w") as ssd:
        ssd.rename("Document name")
        system = ssd.new_system("root")
        system.add_component("component", source="resources/example.fmu")

    with SSD(path, mode="r") as ssd:
        assert ssd.xml.name == "Document name"
        assert ssd.system.name == "root"


def test_add_parameter_binding_records_an_external_mapping_source(tmp_path):
    path = tmp_path / "external_mapping.ssd"

    with SSD(path, mode="w") as ssd:
        system = ssd.new_system("root")
        binding = system.add_parameter_binding(
            "set.ssv",
            mapping_source="resources/mapping.ssm",
        )

    with SSD(path, mode="r") as ssd:
        stored = ssd.system.parameter_bindings[0]

    assert binding.parameter_mapping.source == "resources/mapping.ssm"
    assert stored.parameter_mapping.source == "resources/mapping.ssm"
    assert stored.parameter_mapping.mapping is None
