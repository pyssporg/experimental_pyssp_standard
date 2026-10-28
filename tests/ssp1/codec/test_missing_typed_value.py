"""A parameter/entry without a typed child element is a hard parse error."""

from __future__ import annotations

import pytest

from pyssp_standard.facades.ssv import SSV
from pyssp_standard.standard.ssp1.codec import Ssp1SsbCodec, Ssp1SsvCodec


SSV_MISSING_TYPE = """\
<ssv:ParameterSet xmlns:ssv="http://ssp-standard.org/SSP1/SystemStructureParameterValues" version="1.0" name="Set">
  <ssv:Parameters>
    <ssv:Parameter name="gain" />
  </ssv:Parameters>
</ssv:ParameterSet>
"""

SSB_MISSING_TYPE = """\
<ssb:SignalDictionary
    xmlns:ssb="http://ssp-standard.org/SSP1/SystemStructureSignalDictionary"
    xmlns:ssc="http://ssp-standard.org/SSP1/SystemStructureCommon"
    version="1.0">
  <ssb:DictionaryEntry name="gain" />
</ssb:SignalDictionary>
"""


def test_ssv_codec_rejects_parameter_without_typed_element():
    with pytest.raises(ValueError, match="Parameter 'gain' is missing a typed value element"):
        Ssp1SsvCodec().parse(SSV_MISSING_TYPE)


def test_ssb_codec_rejects_entry_without_typed_element():
    with pytest.raises(ValueError, match="DictionaryEntry 'gain' is missing a typed value element"):
        Ssp1SsbCodec().parse(SSB_MISSING_TYPE)


def test_ssv_facade_surfaces_the_parse_error(tmp_path):
    path = tmp_path / "broken.ssv"
    path.write_text(SSV_MISSING_TYPE, encoding="utf-8")

    with pytest.raises(ValueError, match="missing a typed value element"):
        with SSV(path):
            pass


def test_ssv_annotation_only_parameter_is_also_rejected():
    """Annotations are not a typed value; an otherwise empty parameter fails."""
    xml_text = SSV_MISSING_TYPE.replace(
        '<ssv:Parameter name="gain" />',
        '<ssv:Parameter name="gain"><ssv:Annotations /></ssv:Parameter>',
    )

    with pytest.raises(ValueError, match="missing a typed value element"):
        Ssp1SsvCodec().parse(xml_text)
