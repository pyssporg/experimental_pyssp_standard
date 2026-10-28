"""SSV (ParameterSet) facade — version-aware through version routing."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pyssp_standard.common.document.xml_document import XmlDocument
from pyssp_standard.contracts.parameters import Parameter, ParameterSet, parameters_by_name
from pyssp_standard.standard.common.utils import infer_parameter_type_name
from pyssp_standard.standard.ssp1.model.ssv_model import Ssp1ParameterSet
from pyssp_standard.standard.ssp2.model.ssv_model import Ssp2ParameterSet
from pyssp_standard.standard.version_routing import get_codec_and_validator


class SSV(XmlDocument[ParameterSet]):
    """SSV (ParameterSet) facade — version-aware through version routing.

    A document created in write mode is named after ``Path.stem`` (default
    ``"parameters"``); reading a file keeps the name stored in it.
    """

    def __init__(self, path: str | Path, mode: str = "r", version: str | None = None) -> None:
        super().__init__(path, mode)
        self._version = version or "1.0"

        self._codec, self._validator = self.get_codec_and_validator("SSP", "SSV")


    def _create_document(self) -> Ssp1ParameterSet | Ssp2ParameterSet:
        if self._version == "2.0":
            return Ssp2ParameterSet(name=self.path.stem or "parameters", version="2.0")
        return Ssp1ParameterSet(name=self.path.stem or "parameters", version="1.0")

    @property
    def name(self) -> str:
        """Document name of the parameter set."""
        return self.xml.name

    @classmethod
    def create_parameter_set(
        cls, name: str, *, version: str | None = None
    ) -> ParameterSet:
        """Return an in-memory parameter set; version None means the default SSP version."""
        selected = version or "1.0"
        if selected == "1.0":
            return Ssp1ParameterSet(name=name, version="1.0")
        if selected == "2.0":
            return Ssp2ParameterSet(name=name, version="2.0")
        raise ValueError(
            f"Unsupported SSV version '{selected}'; supported versions: 1.0, 2.0"
        )

    def parameters_by_name(self) -> dict[str, Parameter]:
        """Return the parameter set's parameters keyed by name; last duplicate wins."""
        return parameters_by_name(self.xml)

    def add_parameter(
        self,
        name: str,
        value: object,
        *,
        type_name: str | None = None,
        unit: str | None = None,
        mimetype: str | None = None,
    ) -> Parameter:
        """Append a parameter, inferring the SSP type from ``value`` by default.

        ``value`` is required because every SSP1 parameter type requires a value
        attribute; omitting it would produce a document that fails compliance on
        close.
        """
        ptype = type_name or ("Real" if value is None else infer_parameter_type_name(value))
        return self.xml.add_parameter(
            name,
            ptype,
            value=value,
            unit=unit,
            mimetype=mimetype,
        )

    def extend_parameters(self, parameters) -> list[Parameter]:
        """Append parameters from compact values or explicit parameters."""
        return self.xml.extend_parameters(parameters)

    def set_generation_date_and_time(self, dt: datetime | str | None = None) -> None:
        """Set the generation date and time on the XML document.

        Args:
            dt: A datetime, ISO 8601 string, or None.
                None defaults to "2000-01-01T00:00:00Z".
        """
        from pyssp_standard.common.datetime_utils import format_generation_datetime

        self.xml.metadata.generation_date_and_time = format_generation_datetime(dt)