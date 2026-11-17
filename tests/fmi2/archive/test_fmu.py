from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path

import pytest

from pyssp_standard.common.archive.archive import FMI_EPOCH
from pyssp_standard.facades.fmu import FMU
from pyssp_standard.facades.ssp import SSP
from pyssp_standard.standard.fmi2.codec.model_description_xml_codec import (
    Fmi2ModelDescriptionXmlCodec,
)
from pyssp_standard.standard.fmi2.validation.model_description_validation import (
    Fmi2ModelDescriptionSemanticValidator,
)


def test_archive_lists_binary_and_documentation_entries(fmu_with_binary_archive_fixture, tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(fmu_with_binary_archive_fixture, test_fmu_file)

    with FMU(test_fmu_file) as fmu:
        assert fmu.binaries == ["binaries/linux64/plant.so"]
        assert fmu.documentation == []


def test_archive_lists_no_binaries_when_absent(fmu_archive_fixture, tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(fmu_archive_fixture, test_fmu_file)

    with FMU(test_fmu_file) as fmu:
        assert fmu.binaries == []
        assert fmu.documentation == []


def test_archive_uses_temp_workdir_and_cleans_up_after_exit(fmu_archive_fixture, tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(fmu_archive_fixture, test_fmu_file)

    archive = FMU(test_fmu_file)
    with archive as fmu:
        root = fmu.runtime.root
        assert root.exists()
        assert (root / "modelDescription.xml").exists()

    assert not root.exists()


def test_model_description_facade_reads_from_archive_contents(fmu_archive_fixture, tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(fmu_archive_fixture, test_fmu_file)

    with FMU(test_fmu_file) as fmu:
        archive_xml = fmu.runtime.read_text("modelDescription.xml")
        with fmu.model_description as md:
            assert len(md.xml.inputs) > 0
            assert md.path.read_text(encoding="utf-8") == archive_xml
            assert md.check_compliance() is True


def test_strip_model_exchange_preserves_archive_model_description_guid(fmu_archive_fixture, tmp_path):
    test_fmu_file = tmp_path / "ecs.fmu"
    shutil.copy(fmu_archive_fixture, test_fmu_file)

    with FMU(test_fmu_file, mode="r") as fmu:
        with fmu.model_description as md:
            original_guid = md.xml.guid

    with FMU(test_fmu_file, mode="a") as fmu:
        with fmu.model_description as md:
            md.strip_model_exchange()

    with FMU(test_fmu_file, mode="r") as fmu:
        with fmu.model_description as md:
            assert md.xml.guid == original_guid


def test_directory_mode_reads_fmu_contents_from_persistent_root(fmu_directory_fixture):
    archive = FMU(fmu_directory_fixture, mode="r")
    with archive as fmu:
        root = fmu.runtime.root
        assert root == fmu_directory_fixture
        assert "modelDescription.xml" in fmu.runtime.namelist()
        assert all(entry.startswith("binaries/") for entry in fmu.binaries)
        assert len(fmu.documentation) == 0

    assert root.exists()


def test_directory_mode_exposes_model_description(fmu_directory_fixture):
    with FMU(fmu_directory_fixture, mode="r") as fmu:
        with fmu.model_description as md:
            assert len(md.xml.inputs) > 0
            assert md.path == fmu_directory_fixture / "modelDescription.xml"


def test_archive_and_directory_modes_expose_same_model_name(fmu_archive_fixture, fmu_directory_fixture):
    with FMU(fmu_archive_fixture, mode="r") as archive_fmu:
        with archive_fmu.model_description as archive_md:
            archive_name = archive_md.xml.model_name

    with FMU(fmu_directory_fixture, mode="r") as directory_fmu:
        with directory_fmu.model_description as directory_md:
            directory_name = directory_md.xml.model_name

    assert archive_name == directory_name


def test_fmu_create_empty_in_directory_mode(tmp_path):
    fmu_dir = tmp_path / "empty_fmu"
    with FMU(fmu_dir, mode="w") as fmu:
        assert fmu.runtime.root == fmu_dir
        assert fmu_dir.is_dir()
        assert fmu.binaries == []

    assert fmu_dir.is_dir()


def test_fmu_create_empty_archive(tmp_path):
    fmu_path = tmp_path / "empty.fmu"
    with FMU(fmu_path, mode="w") as fmu:
        assert fmu.runtime.root.is_dir()
        assert fmu.binaries == []

    assert fmu_path.is_file()
    assert fmu_path.stat().st_size > 0


def test_add_binary(tmp_path):
    source_file = tmp_path / "mylib.so"
    source_file.write_text("fake binary content")

    fmu_path = tmp_path / "test.fmu"
    with FMU(fmu_path, mode="w") as fmu:
        result = fmu.add_binary(source_file)
        assert result == "binaries/mylib.so"
        assert "binaries/mylib.so" in fmu.runtime.namelist()


def test_add_binary_with_platform(tmp_path):
    source_file = tmp_path / "mylib.so"
    source_file.write_text("fake binary content")

    fmu_path = tmp_path / "test.fmu"
    with FMU(fmu_path, mode="w") as fmu:
        result = fmu.add_binary(source_file, platform="linux64")
        assert result == "binaries/linux64/mylib.so"
        assert "binaries/linux64/mylib.so" in fmu.runtime.namelist()


def test_add_resource_to_fmu(tmp_path):
    source_file = tmp_path / "data.csv"
    source_file.write_text("a,b,c\n1,2,3")

    fmu_path = tmp_path / "test.fmu"
    with FMU(fmu_path, mode="w") as fmu:
        result = fmu.add_resource(source_file)
        assert result == "resources/data.csv"
        assert "resources/data.csv" in fmu.runtime.namelist()
        assert fmu.runtime.read_text("resources/data.csv") == "a,b,c\n1,2,3"


def test_add_resource_with_target_name(tmp_path):
    source_file = tmp_path / "data.csv"
    source_file.write_text("a,b,c\n1,2,3")

    fmu_path = tmp_path / "test.fmu"
    with FMU(fmu_path, mode="w") as fmu:
        result = fmu.add_resource(source_file, target_name="my_data.csv")
        assert result == "resources/my_data.csv"
        assert "resources/my_data.csv" in fmu.runtime.namelist()


def test_fmu_builder_contents_survive_commit(tmp_path):
    binary_file = tmp_path / "engine.so"
    binary_file.write_text("binary content")
    resource_file = tmp_path / "config.json"
    resource_file.write_text('{"key": "value"}')

    fmu_path = tmp_path / "built.fmu"
    with FMU(fmu_path, mode="w") as fmu:
        fmu.add_binary(binary_file, platform="linux64")
        fmu.add_resource(resource_file)

    # Re-open in read mode
    with FMU(fmu_path, mode="r") as fmu:
        assert "binaries/linux64/engine.so" in fmu.runtime.namelist()
        assert "resources/config.json" in fmu.runtime.namelist()
        assert fmu.runtime.read_text("resources/config.json") == '{"key": "value"}'


def test_package_as_ssp_creates_single_component_ssp(fmu_archive_fixture, tmp_path):
    ssp_path = tmp_path / "packaged.ssp"

    with FMU(fmu_archive_fixture, mode="r") as fmu:
        returned_path = fmu.package_as_ssp(
            ssp_path,
            system_name="custom_system",
            component_name="controller",
            expose_system_connectors=True,
        )

    assert returned_path == ssp_path

    with SSP(ssp_path, mode="r") as ssp:
        assert "0001_ECS_HW.fmu" in ssp.resources
        with ssp.system_structure() as ssd:
            assert ssd.xml.name == "custom_system"
            assert ssd.xml.system is not None
            assert ssd.xml.system.name == "custom_system"
            component = next(element for element in ssd.xml.system.elements if element.name == "controller")
            assert component.source == "resources/0001_ECS_HW.fmu"
            assert any(connector.kind == "input" for connector in ssd.xml.system.connectors)
            assert any(connector.kind == "output" for connector in ssd.xml.system.connectors)


# --- add_model_description tests ---

_MINIMAL_MD_XML = """<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription
  fmiVersion="2.0"
  modelName="TestModel"
  guid="{test-guid-0000-0000-0000-000000000000}"
  generationDateAndTime="2024-01-01T00:00:00Z"
  variableNamingConvention="structured"
  numberOfEventIndicators="0">
  <ModelExchange modelIdentifier="TestModel"/>
</fmiModelDescription>"""


def test_add_model_description_from_file(tmp_path):
    md_file = tmp_path / "modelDescription.xml"
    md_file.write_text(_MINIMAL_MD_XML)

    fmu_path = tmp_path / "test.fmu"
    with FMU(fmu_path, mode="w") as fmu:
        result = fmu.add_model_description(md_file)
        assert result == "modelDescription.xml"
        assert "modelDescription.xml" in fmu.runtime.namelist()


def test_add_model_description_survives_commit(tmp_path):
    md_file = tmp_path / "modelDescription.xml"
    md_file.write_text(_MINIMAL_MD_XML)

    fmu_path = tmp_path / "test.fmu"
    with FMU(fmu_path, mode="w") as fmu:
        fmu.add_model_description(md_file)

    with FMU(fmu_path, mode="r") as fmu:
        assert "modelDescription.xml" in fmu.runtime.namelist()
        with fmu.model_description as md:
            assert md.xml.model_name == "TestModel"


def test_add_model_description_invalid_path(tmp_path):
    fmu_path = tmp_path / "test.fmu"
    with FMU(fmu_path, mode="w") as fmu:
        with pytest.raises(FileNotFoundError):
            fmu.add_model_description(tmp_path / "nonexistent.xml")


# --- FMU.create tests ---


def test_fmu_create_with_minimal(tmp_path):
    md_file = tmp_path / "modelDescription.xml"
    md_file.write_text(_MINIMAL_MD_XML)

    fmu_path = tmp_path / "created.fmu"
    result = FMU.create(fmu_path, md_file)

    assert result == fmu_path
    assert fmu_path.is_file()
    assert fmu_path.stat().st_size > 0

    with FMU(fmu_path, mode="r") as fmu:
        assert "modelDescription.xml" in fmu.runtime.namelist()


def test_fmu_create_with_all_components(tmp_path):
    md_file = tmp_path / "modelDescription.xml"
    md_file.write_text(_MINIMAL_MD_XML)

    binary_file = tmp_path / "engine.so"
    binary_file.write_text("binary content")
    resource_file = tmp_path / "config.json"
    resource_file.write_text('{"key": "value"}')

    binaries = {"linux64": binary_file}
    resources = [resource_file]

    fmu_path = tmp_path / "full.fmu"
    result = FMU.create(fmu_path, md_file, binaries=binaries, resources=resources)

    assert result == fmu_path

    with FMU(fmu_path, mode="r") as fmu:
        assert "modelDescription.xml" in fmu.runtime.namelist()
        assert "binaries/linux64/engine.so" in fmu.runtime.namelist()
        assert "resources/config.json" in fmu.runtime.namelist()


def test_fmu_create_returns_path(tmp_path):
    md_file = tmp_path / "modelDescription.xml"
    md_file.write_text(_MINIMAL_MD_XML)

    fmu_path = tmp_path / "created.fmu"
    result = FMU.create(fmu_path, md_file)

    assert isinstance(result, Path)
    assert result == fmu_path


def test_fmu_create_deterministic(tmp_path):
    """Two FMU.create() calls with identical inputs produce identical SHA256 hashes."""
    md_file = tmp_path / "modelDescription.xml"
    md_file.write_text(_MINIMAL_MD_XML)
    binary_file = tmp_path / "engine.so"
    binary_file.write_text("binary content")
    resource_file = tmp_path / "config.json"
    resource_file.write_text('{"key": "value"}')
    binaries = {"linux64": binary_file}
    resources = [resource_file]

    fmu_path1 = tmp_path / "deterministic_1.fmu"
    fmu_path2 = tmp_path / "deterministic_2.fmu"

    FMU.create(
        fmu_path1,
        md_file,
        binaries=binaries,
        resources=resources,
        fixed_timestamp=FMI_EPOCH,
    )
    FMU.create(
        fmu_path2,
        md_file,
        binaries=binaries,
        resources=resources,
        fixed_timestamp=FMI_EPOCH,
    )

    hash1 = hashlib.sha256(fmu_path1.read_bytes()).hexdigest()
    hash2 = hashlib.sha256(fmu_path2.read_bytes()).hexdigest()

    assert hash1 == hash2


# --- add_sources / add_documentation tests ---


def test_add_sources(tmp_path):
    source_file = tmp_path / "model.c"
    source_file.write_text("int main(void) { return 0; }\n")

    fmu_path = tmp_path / "test.fmu"
    with FMU(fmu_path, mode="w") as fmu:
        result = fmu.add_sources(source_file)
        assert result == "sources/model.c"
        assert "sources/model.c" in fmu.runtime.namelist()


def test_add_documentation_with_target_name(tmp_path):
    doc_file = tmp_path / "readme.txt"
    doc_file.write_text("documentation")

    fmu_path = tmp_path / "test.fmu"
    with FMU(fmu_path, mode="w") as fmu:
        result = fmu.add_documentation(doc_file, target_name="guide.txt")
        assert result == "documentation/guide.txt"
        assert "documentation/guide.txt" in fmu.runtime.namelist()


def test_fmu_create_with_sources_and_documentation(tmp_path):
    md_file = tmp_path / "modelDescription.xml"
    md_file.write_text(_MINIMAL_MD_XML)
    source_file = tmp_path / "model.c"
    source_file.write_text("int main(void) { return 0; }\n")
    doc_file = tmp_path / "readme.txt"
    doc_file.write_text("documentation")

    fmu_path = tmp_path / "with_sources.fmu"
    FMU.create(fmu_path, md_file, sources=[source_file], documentation=[doc_file])

    with FMU(fmu_path, mode="r") as fmu:
        assert "sources/model.c" in fmu.runtime.namelist()
        assert "documentation/readme.txt" in fmu.runtime.namelist()


def test_staged_directory_binary_has_executable_bit(tmp_path):
    binary_file = tmp_path / "engine.so"
    binary_file.write_text("binary content")

    fmu_dir = tmp_path / "staged_fmu"
    with FMU(fmu_dir, mode="w") as fmu:
        fmu.add_binary(binary_file, platform="linux64")

    staged_binary = fmu_dir / "binaries/linux64/engine.so"
    assert staged_binary.stat().st_mode & 0o111


def test_add_binary_rejects_unsafe_platform(tmp_path):
    binary_file = tmp_path / "engine.so"
    binary_file.write_text("binary content")

    fmu_path = tmp_path / "test.fmu"
    with FMU(fmu_path, mode="w") as fmu:
        for platform in ("../evil", "linux/64"):
            with pytest.raises(ValueError, match="platform") as excinfo:
                fmu.add_binary(binary_file, platform=platform)
            assert platform in str(excinfo.value)


# --- validate_binary tests ---


def _parse_minimal_model():
    return Fmi2ModelDescriptionXmlCodec().parse(_MINIMAL_MD_XML)


def test_validate_binary_accepts_matching_identifier():
    Fmi2ModelDescriptionSemanticValidator().validate_binary(_parse_minimal_model(), "TestModel.so")


def test_validate_binary_rejects_model_identifier_mismatch():
    with pytest.raises(ValueError) as excinfo:
        Fmi2ModelDescriptionSemanticValidator().validate_binary(_parse_minimal_model(), "Other.dll")
    message = str(excinfo.value)
    assert "modelIdentifier" in message
    assert "Other.dll" in message


def test_validate_binary_rejects_non_fmi2_version():
    model = _parse_minimal_model()
    model.fmi_version = "3.0"

    with pytest.raises(ValueError) as excinfo:
        Fmi2ModelDescriptionSemanticValidator().validate_binary(model, "TestModel")
    message = str(excinfo.value)
    assert "fmiVersion" in message
    assert "valid FMI 2.0" in message


def test_validate_binary_rejects_missing_interface():
    model = _parse_minimal_model()
    model.interface_type = None

    with pytest.raises(ValueError, match="valid FMI 2.0"):
        Fmi2ModelDescriptionSemanticValidator().validate_binary(model, "TestModel")


# --- FMU.stage / FMU.package tests ---


def _minimal_description(tmp_path, *, fmi_version="2.0", model_identifier="TestModel"):
    xml = _MINIMAL_MD_XML.replace('fmiVersion="2.0"', f'fmiVersion="{fmi_version}"')
    xml = xml.replace('modelIdentifier="TestModel"', f'modelIdentifier="{model_identifier}"')
    path = tmp_path / "modelDescription.xml"
    path.write_text(xml)
    return path


def _minimal_binary(tmp_path, name="TestModel.so"):
    path = tmp_path / "build" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("binary content")
    return path


def test_stage_writes_full_tree(tmp_path):
    description = _minimal_description(tmp_path)
    binary = _minimal_binary(tmp_path)

    sources = tmp_path / "src"
    sources.mkdir()
    (sources / "model.c").write_text("int main(void) { return 0; }\n")

    resources = tmp_path / "data"
    (resources / "nested").mkdir(parents=True)
    (resources / "a.csv").write_text("a,b\n1,2\n")
    (resources / "nested" / "b.csv").write_text("b,c\n3,4\n")

    documentation = tmp_path / "docs"
    documentation.mkdir()
    (documentation / "guide.txt").write_text("guide\n")

    staged = FMU.stage(
        tmp_path / "staged",
        model_description=description,
        binaries={"linux64": binary},
        sources=[sources],
        resources=[resources],
        documentation=[documentation],
        fmi_version="2.0",
    )

    assert staged == tmp_path / "staged"
    assert (staged / "modelDescription.xml").is_file()
    assert (staged / "binaries/linux64/TestModel.so").is_file()
    assert (staged / "binaries/linux64/TestModel.so").stat().st_mode & 0o111
    assert (staged / "sources/src/model.c").is_file()
    assert (staged / "resources/data/a.csv").is_file()
    assert (staged / "resources/data/nested/b.csv").is_file()
    assert (staged / "documentation/docs/guide.txt").is_file()


def test_stage_creates_no_optional_directories(tmp_path):
    description = _minimal_description(tmp_path)

    staged = FMU.stage(tmp_path / "staged", model_description=description)

    for group in ("sources", "resources", "documentation"):
        assert not (staged / group).exists()


def test_stage_refuses_non_empty_directory_and_overwrite_clears_it(tmp_path):
    description = _minimal_description(tmp_path)
    staged = tmp_path / "staged"
    staged.mkdir()
    (staged / "stale.txt").write_text("stale")

    with pytest.raises(FileExistsError) as excinfo:
        FMU.stage(staged, model_description=description)

    assert "overwrite=True" in str(excinfo.value)

    result = FMU.stage(staged, model_description=description, overwrite=True)

    assert result == staged
    assert not (staged / "stale.txt").exists()
    assert (staged / "modelDescription.xml").is_file()


def test_stage_rejects_duplicate_resource_names(tmp_path):
    description = _minimal_description(tmp_path)
    first = tmp_path / "one" / "same.csv"
    second = tmp_path / "two" / "same.csv"
    first.parent.mkdir()
    second.parent.mkdir()
    first.write_text("first")
    second.write_text("second")

    with pytest.raises(ValueError) as excinfo:
        FMU.stage(
            tmp_path / "staged",
            model_description=description,
            resources=[first, second],
        )

    message = str(excinfo.value)
    assert "duplicate resource name" in message
    assert "resources/" in message


def test_stage_rejects_identifier_mismatch(tmp_path):
    description = _minimal_description(tmp_path)
    binary = _minimal_binary(tmp_path, name="Other.so")

    with pytest.raises(ValueError) as excinfo:
        FMU.stage(
            tmp_path / "staged",
            model_description=description,
            binaries={"linux64": binary},
        )

    assert "modelIdentifier" in str(excinfo.value)


def test_stage_rejects_wrong_requested_version(tmp_path):
    description = _minimal_description(tmp_path, fmi_version="1.0")

    with pytest.raises(ValueError) as excinfo:
        FMU.stage(tmp_path / "staged", model_description=description, fmi_version="2.0")

    message = str(excinfo.value)
    assert "fmiVersion" in message
    assert "valid FMI 2.0" in message


def test_stage_rejects_missing_description(tmp_path):
    with pytest.raises(ValueError) as excinfo:
        FMU.stage(tmp_path / "staged", model_description=tmp_path / "missing.xml")

    assert "modelDescription" in str(excinfo.value)


def test_package_writes_exact_staged_entries(tmp_path):
    description = _minimal_description(tmp_path)
    binary = _minimal_binary(tmp_path)
    resource = tmp_path / "config.json"
    resource.write_text('{"key": "value"}')

    staged = FMU.stage(
        tmp_path / "staged",
        model_description=description,
        binaries={"linux64": binary},
        resources=[resource],
    )
    expected = sorted(
        path.relative_to(staged).as_posix()
        for path in staged.rglob("*")
        if path.is_file()
    )

    archive = FMU.package(
        tmp_path / "packaged.fmu",
        model_description=description,
        binaries={"linux64": binary},
        resources=[resource],
        stage_dir=tmp_path / "stage",
    )

    assert archive == tmp_path / "packaged.fmu"
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.namelist() == expected


def test_package_is_deterministic(tmp_path):
    description = _minimal_description(tmp_path)
    binary = _minimal_binary(tmp_path)
    resource = tmp_path / "config.json"
    resource.write_text('{"key": "value"}')
    inputs = {
        "model_description": description,
        "binaries": {"linux64": binary},
        "resources": [resource],
    }

    first = FMU.package(tmp_path / "first.fmu", **inputs)
    second = FMU.package(tmp_path / "second.fmu", **inputs)

    hash_first = hashlib.sha256(first.read_bytes()).hexdigest()
    hash_second = hashlib.sha256(second.read_bytes()).hexdigest()
    assert hash_first == hash_second
