from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import pytest
from pyssp_standard.ssm import SSM
from pyssp_standard.ssp import SSP
from pyssp_standard.ssv import SSV
from pyssp_standard.tree import ParameterBinding


def _new_ssp(root: Path) -> Path:
    with SSP(root, mode="w") as ssp:
        with ssp.system_structure() as ssd:
            system = ssd.system
            system.add_component("plant")
            subsystem = system.add_subsystem("sub")
            subsystem.add_component("gain")
    return root


def _write_ssv(
    path: Path,
    *,
    name: str = "scenario",
    values: tuple[tuple[str, float], ...] = (("height", 2.0), ("gain", 3.0)),
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with SSV(path, mode="w") as ssv:
        ssv.xml.name = name
        for parameter_name, value in values:
            ssv.xml.add_parameter(parname=parameter_name, value=value)
    return path


def _write_ssm(path: Path, entries: tuple[tuple[str, str], ...]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with SSM(path, mode="w") as ssm:
        for source, target in entries:
            ssm.xml.add_mapping(source, target)
    return path


@contextmanager
def _opened(root: Path):
    with SSP(root, mode="r") as ssp:
        with ssp.system_structure() as ssd:
            yield ssp, ssd


def _root_binding(ssd):
    bindings = ssd.system.get_parameter_bindings()
    assert len(bindings) == 1
    return bindings[0]


def _values(parameter_set) -> list[tuple[str, str]]:
    return [
        (parameter.name, parameter.attributes["value"])
        for parameter in parameter_set.parameters
    ]


def _mapping_entries(binding) -> list[tuple[str, str]]:
    return [
        (entry.source, entry.target)
        for entry in binding.parameter_mapping.mapping.mappings
    ]


def test_external_attach_at_root(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    ssv_path = _write_ssv(tmp_path / "scenario.ssv")
    ssm_path = _write_ssm(
        tmp_path / "mapping.ssm",
        (("height", "plant.height"), ("gain", "plant.gain")),
    )

    with SSP(root, mode="a") as ssp:
        binding = ssp.bind_parameters(ssv_path, mapping=ssm_path)
        assert isinstance(binding, ParameterBinding)
        assert binding.source == "resources/scenario.ssv"
        assert binding.parameter_mapping.source == "resources/mapping.ssm"

    assert (root / "resources" / "scenario.ssv").is_file()
    assert (root / "resources" / "mapping.ssm").is_file()
    xml = (root / "SystemStructure.ssd").read_text(encoding="utf-8")
    assert '<ssd:ParameterBinding source="resources/scenario.ssv"' in xml
    assert '<ssd:ParameterMapping source="resources/mapping.ssm"' in xml

    with _opened(root) as (_, ssd):
        binding = _root_binding(ssd)
        assert binding.source == "resources/scenario.ssv"
        assert _values(binding.parameter_set) == [("height", "2.0"), ("gain", "3.0")]
        assert _mapping_entries(binding) == [
            ("height", "plant.height"),
            ("gain", "plant.gain"),
        ]


def test_external_resolved_at_root(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    ssv_path = _write_ssv(tmp_path / "scenario.ssv")
    ssm_path = _write_ssm(
        tmp_path / "mapping.ssm",
        (("height", "plant.height"), ("gain", "plant.gain")),
    )

    with SSP(root, mode="a") as ssp:
        binding = ssp.bind_parameters(ssv_path, mapping=ssm_path, resolve_mapping=True)
        assert binding.source == "resources/scenario.ssv"
        assert binding.parameter_mapping is None

    assert not (root / "resources" / "mapping.ssm").exists()

    with _opened(root) as (_, ssd):
        binding = _root_binding(ssd)
        assert binding.parameter_mapping is None
        assert _values(binding.parameter_set) == [("plant.height", "2.0"), ("plant.gain", "3.0")]


def test_inline_attach_at_root(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    ssv_path = _write_ssv(tmp_path / "scenario.ssv")
    ssm_path = _write_ssm(tmp_path / "mapping.ssm", (("height", "plant.height"),))

    with SSP(root, mode="a") as ssp:
        binding = ssp.bind_parameters(ssv_path, mapping=ssm_path, placement="inline")
        assert isinstance(binding, ParameterBinding)
        assert binding.source is None
        assert binding.parameter_mapping.source == "resources/mapping.ssm"

    assert (root / "resources" / "mapping.ssm").is_file()
    assert not (root / "resources" / "scenario.ssv").exists()
    xml = (root / "SystemStructure.ssd").read_text(encoding="utf-8")
    assert "<ssd:ParameterValues>" in xml
    assert '<ssd:ParameterMapping source="resources/mapping.ssm"' in xml

    with _opened(root) as (_, ssd):
        binding = _root_binding(ssd)
        assert binding.source is None
        assert _values(binding.parameter_set) == [("height", "2.0"), ("gain", "3.0")]
        assert binding.parameter_mapping.source == "resources/mapping.ssm"


def test_inline_resolved_at_root(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    ssv_path = _write_ssv(tmp_path / "scenario.ssv")
    ssm_path = _write_ssm(
        tmp_path / "mapping.ssm",
        (("height", "plant.height"), ("gain", "plant.gain")),
    )

    with SSP(root, mode="a") as ssp:
        ssp.bind_parameters(
            ssv_path,
            mapping=ssm_path,
            placement="inline",
            resolve_mapping=True,
        )

    resources = root / "resources"
    assert not resources.exists() or list(resources.iterdir()) == []

    with _opened(root) as (_, ssd):
        binding = _root_binding(ssd)
        assert binding.parameter_mapping is None
        assert _values(binding.parameter_set) == [("plant.height", "2.0"), ("plant.gain", "3.0")]


def test_inline_binding_at_component(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    ssv_path = _write_ssv(tmp_path / "scenario.ssv")

    with SSP(root, mode="a") as ssp:
        binding = ssp.bind_parameters(
            ssv_path,
            placement="inline",
            target="plant",
            name="plant_parameters",
        )
        assert binding.parameter_set.name == "plant_parameters"

    with _opened(root) as (_, ssd):
        component = next(
            element for element in ssd.system.elements if element.name == "plant"
        )
        binding = component.parameter_bindings[0]
        assert binding.parameter_set.name == "plant_parameters"
        assert _values(binding.parameter_set) == [("height", "2.0"), ("gain", "3.0")]


def test_inline_binding_at_nested_system_and_component(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    ssv_path = _write_ssv(tmp_path / "scenario.ssv")

    with SSP(root, mode="a") as ssp:
        ssp.bind_parameters(ssv_path, placement="inline", target="sub")
        ssp.bind_parameters(ssv_path, placement="inline", target="sub.gain")

    with _opened(root) as (_, ssd):
        subsystem = next(
            element for element in ssd.system.elements if element.name == "sub"
        )
        assert len(subsystem.parameter_bindings) == 1
        component = next(
            element for element in subsystem.elements if element.name == "gain"
        )
        assert len(component.parameter_bindings) == 1
        assert _values(component.parameter_bindings[0].parameter_set) == [
            ("height", "2.0"),
            ("gain", "3.0"),
        ]


def test_in_memory_parameter_set_is_serialized(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    parameter_set = SSV.create_parameter_set("from_memory")
    parameter_set.add_parameter("height", value=2.0)
    parameter_set.add_parameter("gain", value=3.0)

    with SSP(root, mode="a") as ssp:
        binding = ssp.bind_parameters(parameter_set)
        assert binding.source == "resources/from_memory.ssv"

    assert (root / "resources" / "from_memory.ssv").is_file()
    with _opened(root) as (_, ssd):
        binding = _root_binding(ssd)
        assert binding.parameter_set.name == "from_memory"
        assert _values(binding.parameter_set) == [("height", "2.0"), ("gain", "3.0")]


def test_parameter_mapping_input_is_embedded_inline(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    ssv_path = _write_ssv(tmp_path / "scenario.ssv")
    with SSV(ssv_path, mode="r") as ssv:
        parameters = ssv.parameters_by_name()

    with SSP(root, mode="a") as ssp:
        binding = ssp.bind_parameters(parameters, placement="inline")
        assert binding.parameter_set.name == "parameters"

    assert not (root / "resources").exists()
    with _opened(root) as (_, ssd):
        binding = _root_binding(ssd)
        assert binding.parameter_set.name == "parameters"
        assert _values(binding.parameter_set) == [("height", "2.0"), ("gain", "3.0")]


def test_external_mapping_is_copied_next_to_in_memory_set(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    mapping_path = _write_ssm(tmp_path / "mapping.ssm", (("height", "plant.height"),))
    parameter_set = SSV.create_parameter_set("memory")
    parameter_set.add_parameter("height", value=2.0)

    with SSP(root, mode="a") as ssp:
        ssp.bind_parameters(parameter_set, mapping=mapping_path)

    assert (root / "resources" / "memory.ssv").is_file()
    assert (root / "resources" / "mapping.ssm").read_bytes() == mapping_path.read_bytes()

    with _opened(root) as (_, ssd):
        binding = _root_binding(ssd)
        assert binding.parameter_mapping.source == "resources/mapping.ssm"


def test_in_memory_mapping_is_embedded_inline(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    ssv_path = _write_ssv(tmp_path / "scenario.ssv")
    mapping = SSM.create_mapping([("height", "plant.height")])

    with SSP(root, mode="a") as ssp:
        binding = ssp.bind_parameters(ssv_path, mapping=mapping, placement="inline")
        assert binding.parameter_mapping.source is None
        assert binding.parameter_mapping.mapping is not None

    xml = (root / "SystemStructure.ssd").read_text(encoding="utf-8")
    assert "<ssd:ParameterMapping>" in xml
    assert "<ssm:ParameterMapping" in xml

    with _opened(root) as (_, ssd):
        binding = _root_binding(ssd)
        assert binding.parameter_mapping.source is None
        assert _mapping_entries(binding) == [("height", "plant.height")]


def test_conflicting_resource_with_same_name_raises(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    first = _write_ssv(tmp_path / "a" / "scenario.ssv", values=(("height", 2.0),))
    second = _write_ssv(tmp_path / "b" / "scenario.ssv", values=(("height", 9.0),))

    with SSP(root, mode="a") as ssp:
        ssp.bind_parameters(first)
        with pytest.raises(FileExistsError, match="resources/scenario.ssv"):
            ssp.bind_parameters(second)


def test_identical_bytes_reuse_the_resource(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    ssv_path = _write_ssv(tmp_path / "scenario.ssv")

    with SSP(root, mode="a") as ssp:
        ssp.bind_parameters(ssv_path)
        ssp.bind_parameters(ssv_path)
        assert ssp.resources.count("scenario.ssv") == 1

    with _opened(root) as (_, ssd):
        assert len(ssd.system.get_parameter_bindings()) == 2


def test_read_mode_raises(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    ssv_path = _write_ssv(tmp_path / "scenario.ssv")

    with SSP(root, mode="r") as ssp:
        with pytest.raises(RuntimeError, match="read mode"):
            ssp.bind_parameters(ssv_path)


def test_unknown_target_segment_raises(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    ssv_path = _write_ssv(tmp_path / "scenario.ssv")

    with SSP(root, mode="a") as ssp:
        with pytest.raises(KeyError, match="missing"):
            ssp.bind_parameters(ssv_path, placement="inline", target="missing")
        with pytest.raises(KeyError, match="missing"):
            ssp.bind_parameters(ssv_path, placement="inline", target="sub.missing")


def test_invalid_placement_raises(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    ssv_path = _write_ssv(tmp_path / "scenario.ssv")

    with SSP(root, mode="a") as ssp:
        with pytest.raises(ValueError, match="placement"):
            ssp.bind_parameters(ssv_path, placement="bogus")
        with pytest.raises(ValueError, match="resolve_mapping"):
            ssp.bind_parameters(ssv_path, resolve_mapping="yes")


def test_prefix_is_written_verbatim(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    ssv_path = _write_ssv(tmp_path / "scenario.ssv")

    with SSP(root, mode="a") as ssp:
        binding = ssp.bind_parameters(ssv_path, placement="inline", prefix="run1")
        assert binding.prefix == "run1"

    xml = (root / "SystemStructure.ssd").read_text(encoding="utf-8")
    assert 'prefix="run1."' in xml
    with _opened(root) as (_, ssd):
        assert _root_binding(ssd).prefix == "run1"


def test_ssv_name_returns_document_name(tmp_path):
    ssv_path = _write_ssv(tmp_path / "scenario.ssv", name="named_set")
    with SSV(ssv_path, mode="r") as ssv:
        assert ssv.name == "named_set"
        assert ssv.xml.name == "named_set"


def test_bind_parameters_renames_the_external_resource(tmp_path):
    root = _new_ssp(tmp_path / "ssp")
    ssv_path = _write_ssv(tmp_path / "scenario.ssv")

    with SSP(root, mode="a") as ssp:
        binding = ssp.bind_parameters(ssv_path, name="custom.ssv")
        assert binding.source == "resources/custom.ssv"

    with _opened(root) as (_, ssd):
        assert _root_binding(ssd).source == "resources/custom.ssv"
