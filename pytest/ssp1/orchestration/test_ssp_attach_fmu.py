from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from pyssp_standard import Component, FMU, SSP, System, unpack_archive

_MODEL_DESCRIPTION = """\
<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription fmiVersion="2.0" modelName="CsvSource" guid="{00000000-0000-0000-0000-000000000001}" variableNamingConvention="structured">
  <CoSimulation modelIdentifier="CsvSource" canHandleVariableCommunicationStepSize="true"/>
  <ModelVariables>
    <ScalarVariable name="csv_path" valueReference="0" causality="parameter" variability="tunable"><String/></ScalarVariable>
    <ScalarVariable name="y" valueReference="1" causality="output" variability="continuous"><Real/></ScalarVariable>
  </ModelVariables>
  <ModelStructure><Outputs><Unknown index="2"/></Outputs></ModelStructure>
</fmiModelDescription>
"""


def _write_fmu(root: Path) -> Path:
    model_description = root / "modelDescription.xml"
    model_description.write_text(_MODEL_DESCRIPTION, encoding="utf-8")
    return FMU.create(root / "CsvSource.fmu", model_description)


def _add_component(
    system: System,
    name: str,
    connectors: list[tuple[str, str, str]],
    *,
    source: str | None = None,
    implementation: str | None = "CoSimulation",
) -> Component:
    component = system.add_component(
        name,
        source=source or f"resources/{name}.fmu",
        implementation=implementation,
    )
    for connector_name, kind, type_name in connectors:
        component.add_connector(connector_name, kind, type_name)
    return component


def _add_source_component(system: System, **overrides) -> Component:
    return _add_component(
        system,
        "source",
        [("csv_path", "parameter", "String"), ("y", "output", "Real")],
        source="resources/CsvSource.fmu",
        **overrides,
    )


def _add_sink_component(system: System) -> Component:
    return _add_component(
        system,
        "sink",
        [("k", "parameter", "Real"), ("u", "input", "Real"), ("y", "output", "Real")],
    )


def _write_ssp(path: Path, populate: Callable[[System], object]) -> Path:
    with SSP(path, mode="w") as ssp:
        with ssp.system_structure() as ssd:
            populate(ssd.new_system("System"))
    return path


def _component_source(path: Path, name: str) -> tuple[str, str | None]:
    with SSP(path, mode="r") as ssp:
        with ssp.system_structure() as ssd:
            assert ssd.system is not None
            component = ssd.system.find_component(name)
            return component.source, component.implementation


def test_attach_fmu_populates_design_first_component(tmp_path: Path) -> None:
    ssp_path = _write_ssp(tmp_path / "design.ssp", _add_source_component)
    fmu_path = _write_fmu(tmp_path)

    with SSP(ssp_path, mode="a") as ssp:
        assert ssp.resources == []
        resource_name = ssp.attach_fmu("source", fmu_path)
        assert resource_name == "CsvSource.fmu"
        assert ssp.resources == ["CsvSource.fmu"]

    assert _component_source(ssp_path, "source") == (
        "resources/CsvSource.fmu",
        "CoSimulation",
    )


def test_attach_fmu_supports_directory_ssp(tmp_path: Path) -> None:
    ssp_root = tmp_path / "design_dir"
    _write_ssp(ssp_root, _add_source_component)
    fmu_path = _write_fmu(tmp_path)

    with SSP(ssp_root, mode="a") as ssp:
        ssp.attach_fmu("source", fmu_path)

    assert (ssp_root / "resources" / "CsvSource.fmu").is_file()


def test_attach_fmu_accepts_extracted_fmu_directory(tmp_path: Path) -> None:
    ssp_path = _write_ssp(tmp_path / "design.ssp", _add_source_component)
    fmu_dir = unpack_archive(_write_fmu(tmp_path), tmp_path / "extracted")

    with SSP(ssp_path, mode="a") as ssp:
        ssp.attach_fmu("source", fmu_dir)

    with SSP(ssp_path, mode="r") as ssp:
        assert "CsvSource.fmu" in ssp.resources


def test_attach_fmu_sets_explicit_resource_name(tmp_path: Path) -> None:
    ssp_path = _write_ssp(tmp_path / "design.ssp", _add_source_component)
    fmu_path = _write_fmu(tmp_path)

    with SSP(ssp_path, mode="a") as ssp:
        resource_name = ssp.attach_fmu(
            "source", fmu_path, resource_name="sources/csv"
        )

    assert resource_name == "sources/csv.fmu"
    assert _component_source(ssp_path, "source")[0] == "resources/sources/csv.fmu"


def test_attach_fmu_rejects_unknown_component(tmp_path: Path) -> None:
    ssp_path = _write_ssp(tmp_path / "design.ssp", _add_source_component)

    with SSP(ssp_path, mode="a") as ssp:
        with pytest.raises(ValueError, match="No component named 'missing'"):
            ssp.attach_fmu("missing", _write_fmu(tmp_path))


def test_attach_fmu_rejects_ambiguous_component(tmp_path: Path) -> None:
    def populate(system: System) -> None:
        _add_source_component(system)
        nested = system.add_subsystem("nested")
        _add_source_component(nested)

    _write_ssp(tmp_path / "design.ssp", populate)

    with SSP(tmp_path / "design.ssp", mode="a") as ssp:
        with pytest.raises(ValueError, match="ambiguous"):
            ssp.attach_fmu("source", _write_fmu(tmp_path))


def test_attach_fmu_rejects_missing_variable(tmp_path: Path) -> None:
    def populate(system: System) -> Component:
        return _add_component(
            system,
            "source",
            [
                ("csv_path", "parameter", "String"),
                ("y", "output", "Real"),
                ("extra", "output", "Real"),
            ],
        )

    ssp_path = _write_ssp(tmp_path / "design.ssp", populate)

    with SSP(ssp_path, mode="a") as ssp:
        with pytest.raises(ValueError, match="missing variable"):
            ssp.attach_fmu("source", _write_fmu(tmp_path))


def test_attach_fmu_rejects_connector_kind_mismatch(tmp_path: Path) -> None:
    def populate(system: System) -> Component:
        return _add_component(
            system,
            "source",
            [("csv_path", "input", "String"), ("y", "output", "Real")],
        )

    ssp_path = _write_ssp(tmp_path / "design.ssp", populate)

    with SSP(ssp_path, mode="a") as ssp:
        with pytest.raises(ValueError, match="'input' in the SSD but 'parameter'"):
            ssp.attach_fmu("source", _write_fmu(tmp_path))


def test_attach_fmu_rejects_implementation_mismatch(tmp_path: Path) -> None:
    ssp_path = _write_ssp(
        tmp_path / "design.ssp",
        lambda system: _add_source_component(system, implementation="ModelExchange"),
    )

    with SSP(ssp_path, mode="a") as ssp:
        with pytest.raises(ValueError, match="component implementation"):
            ssp.attach_fmu("source", _write_fmu(tmp_path))


def test_attach_fmu_can_skip_validation(tmp_path: Path) -> None:
    def populate(system: System) -> Component:
        return _add_component(
            system,
            "source",
            [("csv_path", "input", "String"), ("y", "output", "Real")],
            source="resources/CsvSource.fmu",
        )

    ssp_path = _write_ssp(tmp_path / "design.ssp", populate)

    with SSP(ssp_path, mode="a") as ssp:
        ssp.attach_fmu("source", _write_fmu(tmp_path), validate=False)

    with SSP(ssp_path, mode="r") as ssp:
        assert "CsvSource.fmu" in ssp.resources


def test_validate_fmu_interfaces_skips_unpopulated_components(tmp_path: Path) -> None:
    ssp_path = _write_ssp(
        tmp_path / "design.ssp",
        lambda system: [_add_source_component(system), _add_sink_component(system)],
    )
    fmu_path = _write_fmu(tmp_path)

    with SSP(ssp_path, mode="a") as ssp:
        ssp.attach_fmu("source", fmu_path)
        ssp.validate_fmu_interfaces()


def test_validate_fmu_interfaces_rejects_mismatched_component(tmp_path: Path) -> None:
    ssp_path = _write_ssp(
        tmp_path / "design.ssp",
        lambda system: [_add_source_component(system), _add_sink_component(system)],
    )
    fmu_path = _write_fmu(tmp_path)

    with SSP(ssp_path, mode="a") as ssp:
        ssp.attach_fmu("source", fmu_path)
        ssp.attach_fmu("sink", fmu_path, validate=False)
        with pytest.raises(ValueError, match="missing variable"):
            ssp.validate_fmu_interfaces()
