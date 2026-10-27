from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pyssp_standard.tree import DefaultExperiment, System
from pyssp_standard.standard.ssp1.model.ssd_model import (
    Ssd1DefaultExperiment,
    Ssd1SystemStructureDescription,
    Ssd1System,
)
from pyssp_standard.common.xml_document import XmlDocument


class SSD(XmlDocument[Ssd1SystemStructureDescription]):
    """Public SSD facade.

    This facade is intentionally limited to SSD file/model operations.
    Cross-file dependency resolution belongs to the SSP archive layer.
    """

    def __init__(self, path: str | Path, mode: str = "r"):
        super().__init__(path, mode)
        self._codec, self._validator = self.get_codec_and_validator("SSP", "SSD", version="1.0")

    def _create_document(self) -> Ssd1SystemStructureDescription:
        return Ssd1SystemStructureDescription(name=self.path.stem or "system", version="1.0", system=Ssd1System(name="system"))

    @property
    def system(self) -> System | None:
        """Top-level system, or ``None`` when the document has none."""
        return self.xml.system

    @property
    def default_experiment(self) -> DefaultExperiment | None:
        return self.xml.default_experiment

    def new_system(self, name: str) -> System:
        """Replace the top-level system with a new empty one.

        The document name is left unchanged; call :meth:`rename` to set it.
        """
        self.xml.system = Ssd1System(name=name)
        return self.xml.system

    def rename(self, name: str) -> None:
        """Set the document name, leaving the system tree untouched."""
        self.xml.name = name

    def set_default_experiment(
        self,
        *,
        start_time: float | None = None,
        stop_time: float | None = None,
    ) -> None:
        """Replace the default experiment with the given values."""
        self.xml.default_experiment = Ssd1DefaultExperiment(
            start_time=start_time,
            stop_time=stop_time,
        )

    def set_generation_date_and_time(self, dt: datetime | str | None = None) -> None:
        """Set the generation date and time on the XML document.

        Args:
            dt: A datetime, ISO 8601 string, or None.
                None defaults to "2000-01-01T00:00:00Z".
        """
        from pyssp_standard.common.datetime_utils import format_generation_datetime

        self.xml.metadata.generation_date_and_time = format_generation_datetime(dt)

    def flatten(self) -> None:
        """Flatten nested systems into one system in place."""
        from pyssp_standard.standard.ssp1.codec.ssd_codec import Ssp1SsdCodec
        from pyssp_standard.standard.ssp1.operations.ssd_flatten import flatten_ssd

        flattened = flatten_ssd(self.xml)
        flattened.version = "1.0"
        self.from_xml(Ssp1SsdCodec().serialize(flattened))
