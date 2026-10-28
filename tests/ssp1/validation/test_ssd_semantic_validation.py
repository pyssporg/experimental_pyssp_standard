"""Current behaviour of the SSD semantic validator (documented, not expanded)."""

from __future__ import annotations

import pytest

from pyssp_standard.standard.ssp1.codec.ssd_codec import Ssp1SsdCodec
from pyssp_standard.standard.ssp1.validation.ssd_validation import (
    Ssp1SsdSemanticValidator,
)


def _model(system_xml: str):
    xml_text = (
        '<ssd:SystemStructureDescription xmlns:ssd="http://ssp-standard.org/SSP1/SystemStructureDescription"'
        ' xmlns:ssc="http://ssp-standard.org/SSP1/SystemStructureCommon"'
        ' name="doc" version="1.0">'
        f"{system_xml}"
        "</ssd:SystemStructureDescription>"
    )
    return Ssp1SsdCodec().parse(xml_text)


def test_duplicate_sibling_components_are_rejected():
    model = _model(
        '<ssd:System name="root"><ssd:Elements>'
        '<ssd:Component name="dup" source="a.fmu" />'
        '<ssd:Component name="dup" source="b.fmu" />'
        "</ssd:Elements></ssd:System>"
    )

    with pytest.raises(ValueError, match="Duplicate component 'dup'"):
        Ssp1SsdSemanticValidator().validate(model)


def test_duplicate_nested_components_are_not_detected():
    """Known gap (ssd_validation.py TODO): nested systems are not checked."""
    model = _model(
        '<ssd:System name="root"><ssd:Elements>'
        '<ssd:System name="nested"><ssd:Elements>'
        '<ssd:Component name="dup" source="a.fmu" />'
        '<ssd:Component name="dup" source="b.fmu" />'
        "</ssd:Elements></ssd:System>"
        "</ssd:Elements></ssd:System>"
    )

    Ssp1SsdSemanticValidator().validate(model)

    nested = model.system.elements[0]
    assert [element.name for element in nested.elements] == ["dup", "dup"]
