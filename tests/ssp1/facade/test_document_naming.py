"""Contract: document names come from the file stem, archive members do not.

Creating a document in write mode names it after ``Path.stem``; the same
content written to two file names yields two differently named documents.
Reading a file never renames the document. Archive member paths are relative
to the packaged directory and never embed the output archive file name.
"""

from __future__ import annotations

import zipfile

from pyssp_standard.common.archive.archive import package_archive
from pyssp_standard.facades.md import ModelDescription
from pyssp_standard.facades.srmd import SRMD
from pyssp_standard.facades.ssd import SSD
from pyssp_standard.facades.ssv import SSV


def _recorded_name(path):
    """Read the document name back from a file written by *path*."""
    suffix = path.suffix
    if suffix == ".ssd":
        with SSD(path) as document:
            return document.xml.name
    if suffix == ".ssv":
        with SSV(path) as document:
            return document.name
    if suffix == ".srmd":
        with SRMD(path) as document:
            return document.xml.name
    with ModelDescription(path) as document:
        return document.xml.model_name


def test_created_documents_are_named_after_the_file_stem(tmp_path):
    """Same content, two file names → two document names (pinned decision)."""
    first = tmp_path / "alpha.ssd"
    second = tmp_path / "beta.ssd"
    for path in (first, second):
        with SSD(path, mode="w") as document:
            document.new_system("system")
            document.check_compliance()

    assert _recorded_name(first) == "alpha"
    assert _recorded_name(second) == "beta"
    assert first.read_bytes() != second.read_bytes()


def test_created_documents_with_the_same_stem_are_byte_identical(tmp_path):
    """Same stem and content in different directories → identical bytes."""
    (tmp_path / "one").mkdir()
    (tmp_path / "two").mkdir()
    first = tmp_path / "one" / "model.ssv"
    second = tmp_path / "two" / "model.ssv"

    for path in (first, second):
        with SSV(path, mode="w") as document:
            document.add_parameter("gain", 1.5)
            document.check_compliance()

    assert first.read_bytes() == second.read_bytes()
    assert _recorded_name(first) == "model"


def test_reading_does_not_rename_a_document(tmp_path):
    """The stored name wins over the file name on read."""
    path = tmp_path / "file_name.ssd"
    with SSD(path, mode="w") as document:
        document.rename("Stored Name")
        document.new_system("system")
        document.check_compliance()

    renamed_copy = tmp_path / "other_name.ssd"
    renamed_copy.write_bytes(path.read_bytes())

    assert _recorded_name(path) == "Stored Name"
    assert _recorded_name(renamed_copy) == "Stored Name"


def test_md_srmd_names_are_file_stem_derived(tmp_path):
    md_two = tmp_path / "beta.xml"
    with ModelDescription(md_two, mode="w", version="3.0") as md:
        md.check_compliance()
    assert _recorded_name(md_two) == "beta"

    srmd_two = tmp_path / "gamma.srmd"
    with SRMD(srmd_two, mode="w") as srmd:
        srmd.check_compliance()
    assert _recorded_name(srmd_two) == "gamma"


def test_archive_member_paths_do_not_embed_the_output_filename(tmp_path):
    """Members are relative to the source dir, not to the archive name."""
    source = tmp_path / "content_dir"
    source.mkdir()
    (source / "SystemStructure.ssd").write_text("<ssd:root />", encoding="utf-8")
    (source / "resources").mkdir()
    (source / "resources" / "data.txt").write_text("x\n", encoding="utf-8")
    archive_path = tmp_path / "unrelated-output-name.ssp"

    package_archive(source, archive_path)

    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()

    assert sorted(names) == ["SystemStructure.ssd", "resources/data.txt"]
    assert all("unrelated-output-name" not in name for name in names)
