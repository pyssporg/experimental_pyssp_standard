from __future__ import annotations

import threading
from functools import lru_cache
from pathlib import Path

from lxml import etree


SCHEMA_ROOT = Path(__file__).resolve().parents[1] / "schema"

#: libxml2 schema objects are not safe for concurrent use. A single cached
#: ``XMLSchema`` is shared by every validator in the process, and callers do
#: validate from worker threads (parallel FMU builds), which corrupts the heap
#: ("double free or corruption") instead of failing cleanly. One process-wide
#: lock serialises compile and validate; both are cheap next to the work the
#: callers do between validations.
_SCHEMA_LOCK = threading.RLock()


def resolve_schema_path(*parts: str) -> Path:
    schema_path = SCHEMA_ROOT.joinpath(*parts)
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema does not exist: {schema_path}")
    return schema_path


@lru_cache(maxsize=None)
def _compile_schema(schema_path: Path) -> etree.XMLSchema:
    """Parse and compile an XSD schema, cached by path."""
    with _SCHEMA_LOCK:
        return etree.XMLSchema(etree.parse(str(schema_path)))


class XmlSchemaValidator:
    """Shared XSD-backed XML validator."""

    def __init__(self, schema_path: Path, *, error_prefix: str):
        self.schema_path = schema_path
        self.error_prefix = error_prefix
        self._schema = _compile_schema(schema_path)

    def validate_xml(self, xml_text: str) -> None:
        document = etree.fromstring(xml_text.encode("utf-8"))
        with _SCHEMA_LOCK:
            valid = self._schema.validate(document)
            error = None if valid else self._schema.error_log.last_error
        if valid:
            return

        if error is None:
            raise ValueError(self.error_prefix)
        raise ValueError(f"{self.error_prefix}: {error.message}")
