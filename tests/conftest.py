from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path

import pytest
from support import fixture_guard
from support.fixtures import (
    EMBRACE,
    EMBRACE_FMU_DIR,
    EMBRACE_MODEL_DESCRIPTION,
    EMBRACE_SSD,
    EMBRACE_SSM,
    EXTERNAL_SSV,
    MIXED_SSD,
    SSV2,
)

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent

#: One explicit level per test file, keyed by path relative to ``tests/``.
FILE_LEVELS = {
    "common/test_archive_determinism.py": "acceptance",
    "common/test_document_runtime.py": "unit",
    "common/test_generation_date_time.py": "unit",
    "common/test_generation_datetime_stability.py": "acceptance",
    "common/test_reference_discovery.py": "unit",
    "common/test_reference_specs.py": "unit",
    "common/test_runtime_layer.py": "unit",
    "fmi2/archive/test_fmu.py": "acceptance",
    "fmi2/archive/test_fmu_package_deterministic.py": "acceptance",
    "fmi2/codec/test_default_experiment_stepsize.py": "component",
    "fmi2/codec/test_model_description_xml_codec.py": "component",
    "fmi2/facade/test_model_description_fmi2.py": "component",
    "fmi2/operations/test_unit_converter.py": "unit",
    "fmi3/facade/test_model_description_fmi3.py": "component",
    "ls_ref/codec/test_ls_ref_xml_codec.py": "component",
    "ls_ref/facade/test_ls_ref.py": "component",
    "operations/test_connection_graph.py": "unit",
    "ssp1/archive/test_ssp_deterministic.py": "acceptance",
    "ssp1/codec/test_missing_typed_value.py": "component",
    "ssp1/codec/test_srmd_xml_codec.py": "component",
    "ssp1/codec/test_ssb_xml_codec.py": "component",
    "ssp1/codec/test_ssd_xml_codec.py": "component",
    "ssp1/codec/test_ssm_xml_codec.py": "component",
    "ssp1/codec/test_xml_utils.py": "component",
    "ssp1/facade/test_document_naming.py": "component",
    "ssp1/facade/test_parameter_contract.py": "contract",
    "ssp1/facade/test_srmd_ssp1.py": "component",
    "ssp1/facade/test_ssb.py": "component",
    "ssp1/facade/test_ssd.py": "component",
    "ssp1/facade/test_ssd_bind.py": "component",
    "ssp1/facade/test_ssm.py": "component",
    "ssp1/facade/test_ssv_ssp1.py": "component",
    "ssp1/facade/test_tree_contract.py": "contract",
    "ssp1/facade/test_tree_protocol.py": "component",
    "ssp1/operations/test_ssd_flatten.py": "unit",
    "ssp1/operations/test_ssd_fmu_iteration.py": "unit",
    "ssp1/orchestration/test_archive_errors.py": "system",
    "ssp1/orchestration/test_archive_tools.py": "system",
    "ssp1/orchestration/test_ssp.py": "system",
    "ssp1/orchestration/test_ssp_add_fmu.py": "system",
    "ssp1/orchestration/test_ssp_attach_fmu.py": "system",
    "ssp1/orchestration/test_ssp_bind.py": "system",
    "ssp1/validation/test_srmd_validation.py": "unit",
    "ssp1/validation/test_ssd_semantic_validation.py": "unit",
    "ssp2/facade/test_parameter_contract.py": "contract",
    "ssp2/facade/test_ssv_ssp2.py": "component",
    "test_fixture_policy.py": "static",
    "test_level_table.py": "static",
    "test_markers.py": "static",
    "test_module_layout.py": "static",
    "tools/test_public_surface.py": "static",
    "tools/test_schema_targets.py": "static",
    "tools/test_schema_validation.py": "static",
    "tools/test_version_routing.py": "static",
}


def _write_zip_from_tree(source_dir: Path, target_file: Path) -> Path:
    with zipfile.ZipFile(target_file, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                archive.write(path, arcname=path.relative_to(source_dir).as_posix())
    return target_file


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def embrace_ssd_fixture() -> Path:
    return EMBRACE_SSD


@pytest.fixture
def embrace_ssm_fixture() -> Path:
    return EMBRACE_SSM


@pytest.fixture
def embrace_ssp_dir_fixture() -> Path:
    return EMBRACE


@pytest.fixture
def embrace_ssp_fixture(tmp_path: Path, embrace_ssp_dir_fixture: Path) -> Path:
    ssp_dir = tmp_path / "embrace_dir"
    shutil.copytree(embrace_ssp_dir_fixture, ssp_dir)

    fmu_dir = ssp_dir / "resources" / "0001_ECS_HW"
    fmu_path = ssp_dir / "resources" / "0001_ECS_HW.fmu"
    _write_zip_from_tree(fmu_dir, fmu_path)
    shutil.rmtree(fmu_dir)

    ssp_path = tmp_path / "embrace.ssp"
    return _write_zip_from_tree(ssp_dir, ssp_path)


@pytest.fixture
def embrace_ssp_archive_fixture(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return _write_zip_from_tree(EMBRACE, tmp_path_factory.mktemp("ssp_archive") / "embrace.ssp")


@pytest.fixture
def mixed_ssd_fixture() -> Path:
    return MIXED_SSD


@pytest.fixture
def external_ssv_fixture() -> Path:
    return EXTERNAL_SSV


@pytest.fixture
def ssv2_fixture() -> Path:
    return SSV2


@pytest.fixture
def model_description_fixture() -> Path:
    return EMBRACE_MODEL_DESCRIPTION


@pytest.fixture
def fmu_directory_fixture() -> Path:
    return EMBRACE_FMU_DIR


@pytest.fixture
def fmu_archive_fixture(tmp_path_factory: pytest.TempPathFactory, fmu_directory_fixture: Path) -> Path:
    return _write_zip_from_tree(fmu_directory_fixture, tmp_path_factory.mktemp("fmu_archive") / "0001_ECS_HW.fmu")


@pytest.fixture
def fmu_with_binary_archive_fixture(
    tmp_path_factory: pytest.TempPathFactory, fmu_directory_fixture: Path
) -> Path:
    root = tmp_path_factory.mktemp("fmu_binary") / "0001_ECS_HW"
    shutil.copytree(fmu_directory_fixture, root)
    binary = root / "binaries" / "linux64" / "plant.so"
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"\x00\x00\x00\x00")
    return _write_zip_from_tree(root, root.parent / "0001_ECS_HW.fmu")


def _relative_test_path(item) -> str:
    return Path(str(item.path)).resolve().relative_to(TESTS_DIR).as_posix()


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    if os.environ.get("UPDATE_GOLDENS") or os.environ.get("UPDATE_REF"):
        return
    session.fixture_snapshot = fixture_guard.snapshot()


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    before = getattr(session, "fixture_snapshot", None)
    if before is None:
        return
    changed = fixture_guard.changes(before)
    if not changed:
        return

    session.exitstatus = pytest.ExitCode.TESTS_FAILED
    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    lines = ["fixtures changed during the run:"] + [f"  {path}" for path in changed]
    if reporter is not None:
        for line in lines:
            reporter.write_line(line)
    else:
        print("\n".join(lines))


def pytest_collection_modifyitems(config, items):
    path_markers = {
        "codec": pytest.mark.codec,
        "facade": pytest.mark.facade,
        "archive": pytest.mark.archive,
        "orchestration": pytest.mark.archive,
        "tools": pytest.mark.tooling,
    }
    level_markers = {
        f"level_{name}": getattr(pytest.mark, f"level_{name}")
        for name in (
            "static",
            "unit",
            "component",
            "contract",
            "integration",
            "system",
            "acceptance",
        )
    }

    for item in items:
        parts = Path(str(item.fspath)).parts
        for path_part, marker in path_markers.items():
            if path_part in parts:
                item.add_marker(marker)
        level = FILE_LEVELS.get(_relative_test_path(item))
        if level is not None:
            item.add_marker(level_markers[f"level_{level}"])
