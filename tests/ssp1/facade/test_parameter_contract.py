"""Public parameter contract tests for SSP1 models and facades."""

from __future__ import annotations

import pytest

import pyssp_standard
import pyssp_standard.facades.ssd
from pyssp_standard import (
    MappingEntry,
    Parameter,
    ParameterBinding,
    ParameterMapping,
    ParameterSet,
)
from pyssp_standard.facades.ssm import SSM
from pyssp_standard.facades.ssv import SSV
from pyssp_standard.standard.ssp1.model.ssc_model import Ssp1Annotation
from pyssp_standard.standard.ssp1.model.ssm_model import (
    Ssp1MappingEntry,
    Ssp1ParameterMapping,
)
from pyssp_standard.standard.ssp1.model.ssv_model import (
    Ssp1Parameter,
    Ssp1ParameterSet,
)

pytestmark = pytest.mark.facade


def test_ssp1_models_satisfy_public_parameter_contract():
    parameter = Ssp1Parameter(name="gain", type_name="Real", attributes={"value": "1.0"})
    parameter_set = Ssp1ParameterSet(name="set", version="1.0")
    mapping_entry = Ssp1MappingEntry(source="gain", target="controller.gain")
    mapping = Ssp1ParameterMapping(version="1.0")

    assert isinstance(parameter, Parameter)
    assert isinstance(parameter_set, ParameterSet)
    assert isinstance(mapping_entry, MappingEntry)
    assert isinstance(mapping, ParameterMapping)


@pytest.mark.parametrize(
    ("value", "expected_type", "expected_value"),
    [
        (1.5, "Real", "1.5"),
        (7, "Integer", "7"),
        (True, "Boolean", "True"),
        ("demo", "String", "demo"),
    ],
)
def test_add_parameter_infers_type_name_from_value(
    tmp_path, value, expected_type, expected_value
):
    path = tmp_path / "inferred.ssv"

    with SSV(path, "w") as ssv:
        parameter = ssv.add_parameter("p", value)

        assert parameter.type_name == expected_type
        assert parameter.attributes.get("value") == expected_value

    with SSV(path) as ssv:
        assert ssv.xml.parameters[0].type_name == expected_type


def test_add_parameter_delegates_unit_and_explicit_type(tmp_path):
    path = tmp_path / "explicit.ssv"

    with SSV(path, "w") as ssv:
        ssv.xml.add_unit("kg", {"kg": 1})
        parameter = ssv.add_parameter("gain", 2.0, type_name="Real", unit="kg")

        assert parameter.type_name == "Real"
        assert parameter.attributes == {"value": "2.0", "unit": "kg"}

    with SSV(path) as ssv:
        assert ssv.xml.parameters[0].attributes["unit"] == "kg"


def test_add_parameter_delegates_mimetype(tmp_path):
    path = tmp_path / "binary.ssv"

    with SSV(path, "w") as ssv:
        parameter = ssv.add_parameter(
            "blob",
            "cafe",
            type_name="Binary",
            mimetype="application/octet-stream",
        )

        assert parameter.attributes == {
            "value": "cafe",
            "mime-type": "application/octet-stream",
        }


def test_extend_parameters_delegates_to_model(tmp_path):
    path = tmp_path / "extended.ssv"

    with SSV(path, "w") as ssv:
        created = ssv.extend_parameters({"offset": -2, "label": "demo"})

        assert [parameter.name for parameter in created] == ["offset", "label"]
        assert [parameter.type_name for parameter in created] == ["Integer", "String"]


def test_add_mapping_and_resolve_returns_independent_parameters(tmp_path):
    path = tmp_path / "mapping.ssm"

    with SSM(path, "w") as ssm:
        entry = ssm.add_mapping("gain", "controller.gain", suppress_unit_conversion=True)

        assert isinstance(entry, MappingEntry)
        assert entry.source == "gain"
        assert entry.target == "controller.gain"
        assert entry.suppress_unit_conversion is True

    source = Ssp1Parameter(
        name="gain",
        type_name="Integer",
        attributes={"value": "2"},
        annotations=[Ssp1Annotation(type_name="com.example.note")],
    )

    with SSM(path) as ssm:
        resolved = ssm.resolve({"gain": source})

    assert list(resolved) == ["controller.gain"]
    result = resolved["controller.gain"]
    assert result.name == "controller.gain"
    assert result.type_name == "Integer"
    assert result.attributes == {"value": "2"}
    assert result.attributes is not source.attributes
    assert result.annotations is not source.annotations


def test_public_imports_expose_version_neutral_contract():
    assert pyssp_standard.ParameterMapping is ParameterMapping
    assert pyssp_standard.ParameterMapping is not Ssp1ParameterMapping
    assert pyssp_standard.ParameterBinding is ParameterBinding
    assert not hasattr(pyssp_standard.facades.ssd, "ParameterBinding")
    assert not hasattr(pyssp_standard.facades.ssd, "Component")
    assert not hasattr(pyssp_standard.facades.ssd, "ParameterMapping")

    public_names = {"Parameter", "ParameterSet", "ParameterMapping", "MappingEntry", "ParameterBinding"}
    assert public_names <= set(pyssp_standard.__all__)
