from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime
from pathlib import Path

from pyssp_standard.common.document.xml_document import XmlDocument
from pyssp_standard.contracts.parameters import (
    MappingEntry,
    Parameter,
    ParameterMapping,
    resolve_parameter_mapping,
)
from pyssp_standard.standard.ssp1.model.ssc_model import Ssp1Transformation
from pyssp_standard.standard.ssp1.model.ssm_model import Ssp1ParameterMapping


class SSM(XmlDocument[ParameterMapping]):
    """Public SSM facade following the same layered pattern as SSV."""

    def __init__(self, path: str | Path, mode: str = "r"):
        super().__init__(path, mode)
        self._codec, self._validator = self.get_codec_and_validator("SSP", "SSM", version="1.0")

    def _create_document(self) -> Ssp1ParameterMapping:
        return Ssp1ParameterMapping(version="1.0")

    @classmethod
    def create_mapping(
        cls,
        entries: Iterable[tuple[str, str]] = (),
        *,
        version: str | None = None,
    ) -> ParameterMapping:
        """Return an in-memory mapping with one entry per (source, target) pair."""
        selected = version or "1.0"
        if selected != "1.0":
            raise ValueError(
                f"Unsupported SSM version '{selected}'; supported versions: 1.0"
            )
        mapping = Ssp1ParameterMapping(version="1.0")
        for source, target in entries:
            mapping.add_mapping(source, target)
        return mapping

    def resolve(self, parameters: Mapping[str, Parameter]) -> dict[str, Parameter]:
        """Resolve this mapping's entries against parameters keyed by source name."""
        return resolve_parameter_mapping(parameters, self.xml.mappings)

    def add_mapping(
        self,
        source: str,
        target: str,
        *,
        suppress_unit_conversion: bool | None = None,
        transformation: object | None = None,
    ) -> MappingEntry:
        """Append a mapping entry from ``source`` to ``target``."""
        return self.xml.add_mapping(
            source,
            target,
            suppress_unit_conversion=suppress_unit_conversion,
            transformation=transformation,
        )

    def set_generation_date_and_time(self, dt: datetime | str | None = None) -> None:
        """Set the generation date and time on the XML document.

        Args:
            dt: A datetime, ISO 8601 string, or None.
                None defaults to "2000-01-01T00:00:00Z".
        """
        from pyssp_standard.common.datetime_utils import format_generation_datetime

        self.xml.metadata.generation_date_and_time = format_generation_datetime(dt)


