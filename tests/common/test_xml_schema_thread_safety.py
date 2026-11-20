"""A cached XSD validator must be safe to call from worker threads.

Parallel FMU builds validate one cached ``XMLSchema`` from several threads.
libxml2 schema objects are not re-entrant, so an unlocked ``validate`` corrupts
the heap instead of returning a result; this guards the lock in
``pyssp_standard.common.xml_schema_validation``.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from pyssp_standard.common.xml_schema_validation import resolve_schema_path
from pyssp_standard.standard.fmi2.validation.model_description_validation import (
    Fmi2ModelDescriptionSchemaValidator,
)

MODEL_DESCRIPTION = """<?xml version="1.0" encoding="UTF-8"?>
<fmiModelDescription fmiVersion="2.0" modelName="ThreadSafe" guid="{00000000-0000-0000-0000-000000000000}" generationTool="test">
  <CoSimulation modelIdentifier="ThreadSafe"/>
  <ModelVariables>
    <ScalarVariable name="x" valueReference="0" causality="input" variability="continuous">
      <Real start="0.0"/>
    </ScalarVariable>
  </ModelVariables>
  <ModelStructure/>
</fmiModelDescription>
"""


def test_shared_fmi2_schema_validates_from_many_threads():
    validator = Fmi2ModelDescriptionSchemaValidator()
    assert validator.schema_path == resolve_schema_path("FMI2", "fmi2ModelDescription.xsd")

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda _: validator.validate_xml(MODEL_DESCRIPTION), range(256)))


def test_invalid_document_still_raises():
    validator = Fmi2ModelDescriptionSchemaValidator()

    with pytest.raises(ValueError, match="failed XSD validation"):
        validator.validate_xml("<fmiModelDescription/>")
