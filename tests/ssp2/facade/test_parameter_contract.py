"""Public parameter contract tests for SSP2 models and the SSV facade."""

from __future__ import annotations

import pytest

from pyssp_standard import Parameter, ParameterSet
from pyssp_standard.facades.ssv import SSV
from pyssp_standard.standard.ssp2.model.ssv_model import (
    Ssp2Parameter,
    Ssp2ParameterSet,
)

pytestmark = pytest.mark.facade


def test_ssp2_models_satisfy_public_parameter_contract():
    parameter = Ssp2Parameter(name="gain", type_name="Real", attributes={"value": "1.0"})
    parameter_set = Ssp2ParameterSet(name="set", version="2.0")

    assert isinstance(parameter, Parameter)
    assert isinstance(parameter_set, ParameterSet)


def test_add_parameter_infers_type_name_for_ssp2(tmp_path):
    path = tmp_path / "inferred_ssp2.ssv"

    with SSV(path, "w", version="2.0") as ssv:
        parameter = ssv.add_parameter("gain", 1.5)

        assert parameter.type_name == "Real"

    with SSV(path) as ssv:
        assert isinstance(ssv.xml, Ssp2ParameterSet)
        assert ssv.xml.parameters[0].type_name == "Real"


def test_parameters_by_name_supports_ssp2_and_keeps_last_duplicate(tmp_path):
    path = tmp_path / "duplicates_ssp2.ssv"
    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<ssv:ParameterSet xmlns:ssv="http://ssp-standard.org/SSP1/SystemStructureParameterValues" version="2.0" name="Duplicates">
  <ssv:Parameters>
    <ssv:Parameter name="gain"><ssv:Real value="1.0" /></ssv:Parameter>
    <ssv:Parameter name="mode"><ssv:String value="demo" /></ssv:Parameter>
    <ssv:Parameter name="gain"><ssv:Integer value="2" /></ssv:Parameter>
  </ssv:Parameters>
</ssv:ParameterSet>
""",
        encoding="utf-8",
    )

    with SSV(path) as ssv:
        assert isinstance(ssv.xml, Ssp2ParameterSet)
        parameters = ssv.parameters_by_name()

    assert list(parameters) == ["gain", "mode"]
    assert parameters["gain"].type_name == "Integer"
    assert parameters["gain"].attributes == {"value": "2"}
    assert parameters["mode"].type_name == "String"
    assert parameters["mode"].attributes == {"value": "demo"}
