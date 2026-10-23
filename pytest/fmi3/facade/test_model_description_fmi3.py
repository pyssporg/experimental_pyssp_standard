"""ModelDescription facade tests for FMI3 (version 3.0) documents."""

from __future__ import annotations

from pathlib import Path

from pyssp_standard.md import ModelDescription


def test_create_fmi3_document_round_trip(tmp_path: Path):
    """Create FMI3 document, write, read back, verify version."""
    path = tmp_path / "test_fmi3.xml"

    with ModelDescription(path, "w", version="3.0") as md:
        assert md.xml.fmi_version == "3.0"

    xml_text = path.read_text(encoding="utf-8")
    assert 'fmiVersion="3.0"' in xml_text

    with ModelDescription(path) as md:
        assert md.xml.fmi_version == "3.0"

_FMI3_CS_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription fmiVersion="3.0" modelName="Test" instantiationToken="{token}">
  <CoSimulation modelIdentifier="Test"/>
  <ModelVariables>
    <Float64 name="y" valueReference="1" causality="output"/>
  </ModelVariables>
</fmiModelDescription>"""


def test_interface_types_reads_fmi3_interface_elements(tmp_path: Path):
    path = tmp_path / "model_description.xml"
    path.write_text(_FMI3_CS_XML, encoding="utf-8")
    with ModelDescription(path) as md:
        assert md.interface_types == {"CoSimulation"}
