"""SRMD validation: structural (no loadable XSD) plus semantic checks."""

from __future__ import annotations

import pytest

from pyssp_standard.standard.ssp1.codec.srmd_codec import Ssp1SrmdCodec
from pyssp_standard.standard.ssp1.validation.srmd_validation import (
    Ssp1SrmdSchemaValidator,
    Ssp1SrmdValidator,
)
from support.fixtures import SRMD

NS_DECLS = (
    'xmlns:srmd="http://ssp-standard.org/SSPTraceability1/SimulationResourceMetaData" '
    'xmlns:stc="http://ssp-standard.org/SSPTraceability1/SSPTraceabilityCommon"'
)


def _document(body: str = "", attributes: str = 'version="1.0.0" name="doc"') -> str:
    return f"<srmd:SimulationResourceMetaData {NS_DECLS} {attributes}>{body}</srmd:SimulationResourceMetaData>"


def test_structural_validator_accepts_reference_fixture():
    xml_text = SRMD.read_text(encoding="utf-8")
    model = Ssp1SrmdCodec().parse(xml_text)

    assert Ssp1SrmdValidator().validate(model, xml_text) is None


def test_structural_validator_accepts_minimal_document():
    assert Ssp1SrmdSchemaValidator().validate_xml(_document()) is None


def test_structural_validator_accepts_classification_with_keyword():
    body = (
        '<stc:Classification type="t">'
        '<stc:ClassificationEntry keyword="part">value</stc:ClassificationEntry>'
        "</stc:Classification>"
    )
    assert Ssp1SrmdSchemaValidator().validate_xml(_document(body)) is None


@pytest.mark.parametrize(
    ("xml_text", "message"),
    [
        (
            '<srmd:SimulationResourceMetaData xmlns:srmd="urn:wrong" version="1.0" name="d" />',
            "root element must be srmd:SimulationResourceMetaData",
        ),
        (_document(attributes='name="doc"'), "missing required attribute 'version'"),
        (_document(attributes='version="1.0.0"'), "missing required attribute 'name'"),
        (_document("<stc:Unknown />"), "unsupported child"),
        (
            _document('<stc:Classification><stc:Unknown /></stc:Classification>'),
            "unsupported child",
        ),
        (
            _document('<stc:Classification><stc:ClassificationEntry /></stc:Classification>'),
            "missing required attribute 'keyword'",
        ),
    ],
)
def test_structural_validator_rejects_invalid_documents(xml_text, message):
    with pytest.raises(ValueError, match=message):
        Ssp1SrmdSchemaValidator().validate_xml(xml_text)


def test_semantic_validator_rejects_duplicate_classification_type():
    xml_text = _document(
        '<stc:Classification type="dup" /><stc:Classification type="dup" />'
    )
    model = Ssp1SrmdCodec().parse(xml_text)

    with pytest.raises(ValueError, match="Duplicate classification type 'dup'"):
        Ssp1SrmdValidator().validate(model, xml_text)


def test_semantic_validation_runs_before_structural_validation():
    model = Ssp1SrmdCodec().parse(_document())
    model.add_classification("dup")
    model.add_classification("dup")

    with pytest.raises(ValueError, match="Duplicate classification type"):
        Ssp1SrmdValidator().validate(model, "<not-the-model />")
