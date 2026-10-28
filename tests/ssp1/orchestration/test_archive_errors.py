"""Negative coverage for the archive helpers' documented error contracts."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from pyssp_standard.common.archive import (
    copy_resource_directory,
    package_archive,
    unpack_archive,
)


def _write_source_dir(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    (source / "resources").mkdir(parents=True)
    (source / "SystemStructure.ssd").write_text("<ssd:root />", encoding="utf-8")
    (source / "resources" / "data.txt").write_text("x\n", encoding="utf-8")
    return source


def test_unpack_rejects_other_suffixes(tmp_path):
    archive = tmp_path / "model.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("a.txt", "a")

    with pytest.raises(ValueError, match="Expected a .fmu or .ssp archive"):
        unpack_archive(archive)


def test_unpack_rejects_corrupt_zip(tmp_path):
    archive = tmp_path / "broken.ssp"
    archive.write_bytes(b"not a zip file")

    with pytest.raises(zipfile.BadZipFile):
        unpack_archive(archive)


def test_unpack_rejects_existing_destination_without_overwrite(tmp_path):
    source = _write_source_dir(tmp_path)
    archive = tmp_path / "model.ssp"
    package_archive(source, archive)
    existing = tmp_path / "existing"
    existing.mkdir()

    with pytest.raises(FileExistsError, match="Output path already exists"):
        unpack_archive(archive, existing)

    assert unpack_archive(archive, existing, overwrite=True) == existing
    assert (existing / "SystemStructure.ssd").is_file()


def test_package_rejects_other_suffixes(tmp_path):
    source = _write_source_dir(tmp_path)

    with pytest.raises(ValueError, match="extensionless output archive"):
        package_archive(source, tmp_path / "model.zip")


def test_package_rejects_missing_source_directory(tmp_path):
    with pytest.raises(FileNotFoundError, match="Source directory not found"):
        package_archive(tmp_path / "missing", tmp_path / "missing.ssp")


def test_package_rejects_existing_archive_without_overwrite(tmp_path):
    source = _write_source_dir(tmp_path)
    archive = tmp_path / "model.ssp"
    archive.write_bytes(b"existing")

    with pytest.raises(FileExistsError, match="Archive already exists"):
        package_archive(source, archive, overwrite=False)

    assert package_archive(source, archive) == archive
    with zipfile.ZipFile(archive) as z:
        assert "SystemStructure.ssd" in z.namelist()


def test_copy_resource_directory_rejects_missing_source(tmp_path):
    with pytest.raises(FileNotFoundError):
        copy_resource_directory(tmp_path / "missing", tmp_path, "target")


def test_copy_resource_directory_rejects_file_source(tmp_path):
    source_file = tmp_path / "file.txt"
    source_file.write_text("x", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        copy_resource_directory(source_file, tmp_path, "target")


def test_copy_resource_directory_rejects_existing_target(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "data.txt").write_text("x", encoding="utf-8")
    resource_root = tmp_path / "resources"
    (resource_root / "target").mkdir(parents=True)

    with pytest.raises(FileExistsError, match="Resource already exists: target"):
        copy_resource_directory(source, resource_root, "target")

    assert copy_resource_directory(source, resource_root, "other") == "other"
    assert (resource_root / "other" / "data.txt").is_file()
