from __future__ import annotations

from pathlib import Path

import pytest
from pyssp_standard import SSD, SSM, SSV
from pyssp_standard.parameters import ParameterSet


def _ssd(tmp_path: Path) -> Path:
    path = tmp_path / "structure.ssd"
    with SSD(path, mode="w") as ssd:
        system = ssd.new_system("root")
        system.add_component("plant", source="resources/plant.fmu")
        subsystem = system.add_subsystem("sub")
        subsystem.add_component("gain")
    return path


def _parameter_set() -> ParameterSet:
    parameter_set = SSV.create_parameter_set("scenario")
    parameter_set.add_parameter("height", value=2.0)
    parameter_set.add_parameter("gain", value=3.0)
    return parameter_set


def _values(parameter_set) -> list[tuple[str, str]]:
    return [
        (parameter.name, parameter.attributes["value"])
        for parameter in parameter_set.parameters
    ]


def test_external_binding_uses_the_literal_source(tmp_path):
    path = _ssd(tmp_path)

    with SSD(path, mode="a") as ssd:
        binding = ssd.bind_parameters(source="resources/scenario.ssv")
        assert binding.source == "resources/scenario.ssv"
        assert binding.parameter_set is None
        assert binding.parameter_mapping is None

    with SSD(path, mode="r") as ssd:
        stored = ssd.system.parameter_bindings[0]
        assert stored.source == "resources/scenario.ssv"
    assert 'source="resources/scenario.ssv"' in path.read_text(encoding="utf-8")


def test_inline_binding_embeds_a_copy(tmp_path):
    path = _ssd(tmp_path)
    parameter_set = _parameter_set()

    with SSD(path, mode="a") as ssd:
        binding = ssd.bind_parameters(parameter_set)
        parameter_set.name = "mutated"
        assert binding.source is None
        assert binding.parameter_set.name == "scenario"

    with SSD(path, mode="r") as ssd:
        stored = ssd.system.parameter_bindings[0]
        assert stored.source is None
        assert stored.parameter_set.name == "scenario"
        assert _values(stored.parameter_set) == [("height", "2.0"), ("gain", "3.0")]


def test_binding_targets_a_nested_system(tmp_path):
    path = _ssd(tmp_path)

    with SSD(path, mode="a") as ssd:
        ssd.bind_parameters(_parameter_set(), target="sub")

    with SSD(path, mode="r") as ssd:
        assert len(ssd.system.parameter_bindings) == 0
        subsystem = next(
            element for element in ssd.system.elements if element.name == "sub"
        )
        assert len(subsystem.parameter_bindings) == 1


def test_binding_targets_a_component(tmp_path):
    path = _ssd(tmp_path)

    with SSD(path, mode="a") as ssd:
        ssd.bind_parameters(_parameter_set(), target="sub.gain")

    with SSD(path, mode="r") as ssd:
        subsystem = next(
            element for element in ssd.system.elements if element.name == "sub"
        )
        component = next(
            element for element in subsystem.elements if element.name == "gain"
        )
        assert len(component.parameter_bindings) == 1
        assert _values(component.parameter_bindings[0].parameter_set) == [
            ("height", "2.0"),
            ("gain", "3.0"),
        ]


def test_inline_mapping_is_embedded(tmp_path):
    path = _ssd(tmp_path)
    mapping = SSM.create_mapping([("height", "plant.height")])

    with SSD(path, mode="a") as ssd:
        binding = ssd.bind_parameters(_parameter_set(), mapping=mapping)
        assert binding.parameter_mapping.source is None
        assert binding.parameter_mapping.mapping is not None

    with SSD(path, mode="r") as ssd:
        stored = ssd.system.parameter_bindings[0]
        assert stored.parameter_mapping.source is None
        assert [
            (entry.source, entry.target)
            for entry in stored.parameter_mapping.mapping.mappings
        ] == [("height", "plant.height")]


def test_mapping_source_is_referenced_verbatim(tmp_path):
    path = _ssd(tmp_path)

    with SSD(path, mode="a") as ssd:
        binding = ssd.bind_parameters(
            _parameter_set(),
            mapping_source="resources/mapping.ssm",
        )
        assert binding.parameter_mapping.mapping is None

    with SSD(path, mode="r") as ssd:
        stored = ssd.system.parameter_bindings[0]
        assert stored.parameter_mapping.source == "resources/mapping.ssm"
        assert stored.parameter_mapping.mapping is None


def test_prefix_is_written_verbatim(tmp_path):
    path = _ssd(tmp_path)

    with SSD(path, mode="a") as ssd:
        binding = ssd.bind_parameters(_parameter_set(), prefix="run1")
        assert binding.prefix == "run1"

    with SSD(path, mode="r") as ssd:
        assert ssd.system.parameter_bindings[0].prefix == "run1"
    assert 'prefix="run1."' in path.read_text(encoding="utf-8")


def test_name_renames_the_embedded_set(tmp_path):
    path = _ssd(tmp_path)

    with SSD(path, mode="a") as ssd:
        binding = ssd.bind_parameters(_parameter_set(), name="plant_parameters")
        assert binding.parameter_set.name == "plant_parameters"

    with SSD(path, mode="r") as ssd:
        assert ssd.system.parameter_bindings[0].parameter_set.name == (
            "plant_parameters"
        )


def test_mapping_input_becomes_a_set_named_parameters(tmp_path):
    path = _ssd(tmp_path)
    parameters = {parameter.name: parameter for parameter in _parameter_set().parameters}

    with SSD(path, mode="a") as ssd:
        binding = ssd.bind_parameters(parameters)
        assert binding.parameter_set.name == "parameters"
        assert _values(binding.parameter_set) == [("height", "2.0"), ("gain", "3.0")]


def test_mapping_input_uses_the_given_name(tmp_path):
    path = _ssd(tmp_path)
    parameters = {parameter.name: parameter for parameter in _parameter_set().parameters}

    with SSD(path, mode="a") as ssd:
        binding = ssd.bind_parameters(parameters, name="from_memory")
        assert binding.parameter_set.name == "from_memory"


def test_read_mode_raises(tmp_path):
    path = _ssd(tmp_path)

    with SSD(path, mode="r") as ssd:
        with pytest.raises(RuntimeError, match="read mode"):
            ssd.bind_parameters(_parameter_set())


def test_parameters_are_required_without_a_source(tmp_path):
    path = _ssd(tmp_path)

    with SSD(path, mode="a") as ssd:
        with pytest.raises(ValueError, match="parameters"):
            ssd.bind_parameters()


def test_source_rejects_parameters(tmp_path):
    path = _ssd(tmp_path)

    with SSD(path, mode="a") as ssd:
        with pytest.raises(ValueError, match="source"):
            ssd.bind_parameters(_parameter_set(), source="resources/scenario.ssv")


def test_source_rejects_a_name(tmp_path):
    path = _ssd(tmp_path)

    with SSD(path, mode="a") as ssd:
        with pytest.raises(ValueError, match="source"):
            ssd.bind_parameters(source="resources/scenario.ssv", name="scenario")


def test_mapping_and_mapping_source_are_exclusive(tmp_path):
    path = _ssd(tmp_path)

    with SSD(path, mode="a") as ssd:
        with pytest.raises(ValueError, match="mutually exclusive"):
            ssd.bind_parameters(
                _parameter_set(),
                mapping=SSM.create_mapping([("height", "plant.height")]),
                mapping_source="resources/mapping.ssm",
            )


def test_unknown_target_raises_key_error(tmp_path):
    path = _ssd(tmp_path)

    with SSD(path, mode="a") as ssd:
        with pytest.raises(KeyError, match="missing"):
            ssd.bind_parameters(_parameter_set(), target="missing")
        with pytest.raises(KeyError, match="missing"):
            ssd.bind_parameters(_parameter_set(), target="sub.missing")


def test_ambiguous_target_raises_key_error(tmp_path):
    path = _ssd(tmp_path)

    with SSD(path, mode="a") as ssd:
        subsystem = ssd.target("sub")
        subsystem.add_component("gain")
        with pytest.raises(KeyError, match="ambiguous"):
            ssd.bind_parameters(_parameter_set(), target="sub.gain")


def test_empty_target_segment_raises(tmp_path):
    path = _ssd(tmp_path)

    with SSD(path, mode="a") as ssd:
        with pytest.raises(ValueError, match="Invalid target path"):
            ssd.bind_parameters(_parameter_set(), target="")
        with pytest.raises(ValueError, match="Invalid target path"):
            ssd.bind_parameters(_parameter_set(), target="sub.")


def test_target_returns_the_root_system(tmp_path):
    path = _ssd(tmp_path)

    with SSD(path, mode="r") as ssd:
        assert ssd.target() is ssd.system
        assert ssd.target("sub") is ssd.system.elements[1]
        assert ssd.target("sub.gain") is ssd.system.elements[1].elements[0]
