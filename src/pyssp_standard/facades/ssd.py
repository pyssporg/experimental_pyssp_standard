from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from pyssp_standard.common.document.xml_document import XmlDocument
from pyssp_standard.standard.ssp1.model.ssd_model import (
    Ssd1DefaultExperiment,
    Ssd1System,
    Ssd1SystemStructureDescription,
)
from pyssp_standard.standard.ssp1.operations.ssd_binding import (
    append_binding,
    resolve_target,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pyssp_standard.contracts.parameters import Parameter, ParameterMapping, ParameterSet
    from pyssp_standard.contracts.tree import (
        Component,
        DefaultExperiment,
        ParameterBinding,
        System,
    )


class SSD(XmlDocument[Ssd1SystemStructureDescription]):
    """Public SSD facade.

    This facade is intentionally limited to SSD file/model operations.
    Cross-file dependency resolution belongs to the SSP archive layer.

    A document created in write mode is named after ``Path.stem``; reading a
    file keeps the name stored in it.
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

    def target(self, path: str | None = None) -> System | Component:
        """Return the root system, or the element named by a dotted path.

        Args:
            path: ``None`` for the root system, otherwise dot-separated element
                names whose last segment is a system or a component.

        Raises:
            ValueError: When the document has no system or a segment is empty.
            KeyError: When a segment is unknown, ambiguous, or not a system.
        """
        return resolve_target(self.xml.system, path)

    def bind_parameters(
        self,
        parameters: ParameterSet | Mapping[str, Parameter] | None = None,
        *,
        target: str | None = None,
        source: str | None = None,
        mapping: ParameterMapping | None = None,
        mapping_source: str | None = None,
        name: str | None = None,
        prefix: str | None = None,
    ) -> ParameterBinding:
        """Add one parameter binding to a system or component.

        Args:
            parameters: A parameter set embedded as a deep copy, or parameters
                keyed by name embedded as a new set named ``name or
                "parameters"``. Required unless ``source`` is given.
            target: Dotted path to the target element; ``None`` selects the root
                system.
            source: External resource reference, written verbatim. Mutually
                exclusive with ``parameters`` and ``name``.
            mapping: Parameter mapping to embed.
            mapping_source: External mapping reference. Mutually exclusive with
                ``mapping``.
            name: Name for an embedded set.
            prefix: Binding prefix, written verbatim.

        Raises:
            RuntimeError: When the document was opened read-only.
            ValueError: On an invalid argument combination, a document without
                a system, or an empty target segment.
            KeyError: When a target segment is unknown or ambiguous.
        """
        if self.mode == "r":
            raise RuntimeError("Cannot bind parameters in read mode")
        return append_binding(
            self.target(target),
            parameters,
            source=source,
            mapping=mapping,
            mapping_source=mapping_source,
            name=name,
            prefix=prefix,
        )

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
