from __future__ import annotations

import shutil
import tempfile
import zipfile
from collections.abc import Callable, Iterable, Iterator
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

from pyssp_standard.common.archive.archive import FMI_EPOCH, package_archive
from pyssp_standard.common.archive.archive_runtime import create_runtime
from pyssp_standard.common.archive.fmu_layout import platform_component
from pyssp_standard.facades.md import ModelDescription
from pyssp_standard.facades.ssp import SSP
from pyssp_standard.standard.fmi2.validation.model_description_validation import (
    Fmi2ModelDescriptionSemanticValidator,
)
from pyssp_standard.standard.fmi3.validation.model_description_validation import (
    Fmi3ModelDescriptionSemanticValidator,
)
from pyssp_standard.standard.version_routing import (
    StandardVersion,
    get_parse_stack,
    get_parse_stack_from_file,
)


def _prepare_root(directory: Path, overwrite: bool) -> None:
    """Clear *directory* for a fresh tree, refusing to merge with stale files."""
    if directory.exists():
        if not directory.is_dir():
            raise NotADirectoryError(
                f"staging path {directory} exists and is not a directory"
            )
        if any(directory.iterdir()) and not overwrite:
            raise FileExistsError(
                f"staging directory {directory} is not empty; pass "
                "overwrite=True to replace its contents"
            )
        if overwrite:
            shutil.rmtree(directory)


def _load_description(path: Path, fmi_version: str | None):
    """Parse and version-gate the model description before anything is written."""
    if not path.is_file():
        raise ValueError(f"modelDescription {path} does not exist or is not a file")
    try:
        spec = (
            get_parse_stack_from_file(path)
            if fmi_version is None
            else get_parse_stack(StandardVersion("FMI", "MD", fmi_version))
        )
        if spec.codec_type is None:
            raise ValueError(f"no model description codec for FMI {fmi_version or 'version'}")
        document = spec.codec_type().parse(path.read_text(encoding="utf-8"))
    except (ET.ParseError, KeyError, UnicodeDecodeError, ValueError) as exc:
        label = f"FMI {fmi_version} " if fmi_version else ""
        raise ValueError(
            f"modelDescription {path} is not a valid {label}model description: {exc}"
        ) from exc
    if fmi_version is not None and document.fmi_version != fmi_version:
        raise ValueError(
            f"fmiVersion {document.fmi_version!r} is not a valid FMI {fmi_version} version"
        )
    return document


def _require_entry(path: Path, role: str) -> None:
    if not path.exists():
        raise ValueError(f"{role} {path} does not exist")


def _entries(entry: Path) -> Iterator[tuple[Path, str]]:
    """Yield *(file, name below the entry)* for a file or a whole tree."""
    if entry.is_dir():
        for path in sorted(entry.rglob("*")):
            if path.is_file():
                yield path, f"{entry.name}/{path.relative_to(entry).as_posix()}"
    else:
        yield entry, entry.name


def _add_entry(
    fmu: "FMU", entry: Path, role: str, group: str, add: Callable[..., str]
) -> None:
    """Add a file or tree under *group*, refusing a duplicate entry name."""
    if (fmu.path / group / entry.name).exists():
        raise ValueError(f"duplicate {role} name {entry.name!r} under {group}/")
    for source, name in _entries(entry):
        add(source, target_name=name)


class FMU:
    def __init__(
        self,
        path: str | Path,
        mode: str = "r",
        fixed_timestamp: tuple[int, int, int, int, int, int] = FMI_EPOCH,
    ):
        self.path = Path(path)
        self.mode = mode
        self.fixed_timestamp = fixed_timestamp
        self.runtime = create_runtime(self.path, mode, fixed_timestamp=fixed_timestamp)
        self._model_description: "ModelDescription" | None = None

    def __enter__(self) -> "FMU":
        self.runtime.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.runtime.__exit__(exc_type, exc, tb)
        return False

    @property
    def binaries(self) -> list[str]:
        return self.runtime.list_prefix("binaries/")

    @property
    def documentation(self) -> list[str]:
        return self.runtime.list_prefix("documentation/")

    def add_model_description(self, source: str | Path) -> str:
        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(f"modelDescription file not found: {source_path}")
        return self.runtime.add_file(source_path, target_name="modelDescription.xml")

    @classmethod
    def create(
        cls,
        path: str | Path,
        model_description: str | Path,
        binaries: dict[str, str | Path] | None = None,
        resources: list[str | Path] | None = None,
        fixed_timestamp: tuple[int, int, int, int, int, int] = FMI_EPOCH,
        *,
        sources: Iterable[str | Path] | None = None,
        documentation: Iterable[str | Path] | None = None,
    ) -> Path:
        path = Path(path)
        with cls(path, mode="w", fixed_timestamp=fixed_timestamp) as fmu:
            fmu.add_model_description(model_description)
            for platform, binary in (binaries or {}).items():
                fmu.add_binary(binary, platform=platform)
            for resource in (resources or []):
                fmu.add_resource(resource)
            for source in (sources or []):
                fmu.add_sources(source)
            for document in (documentation or []):
                fmu.add_documentation(document)
        return path

    @classmethod
    def stage(
        cls,
        directory: str | Path,
        *,
        model_description: str | Path,
        binaries: dict[str, str | Path] | None = None,
        sources: Iterable[str | Path] | None = None,
        resources: Iterable[str | Path] | None = None,
        documentation: Iterable[str | Path] | None = None,
        fmi_version: str | None = None,
        overwrite: bool = False,
    ) -> Path:
        """Write a clean FMU tree at *directory* and return it.

        The model description is validated first (parsed for *fmi_version*, or
        routed from its content when that is ``None``), then copied verbatim to
        the archive root. Binaries go to ``binaries/<platform>/``; source,
        resource, and documentation entries go to ``sources/``, ``resources/``,
        and ``documentation/``. Directory entries expand recursively with their
        path below the entry preserved. Empty optional groups create no
        directory.

        Raises:
            ValueError: The model description, version, binary name, or an
                input entry does not satisfy the FMU contract, or two entries
                would land on the same name.
            FileExistsError: *directory* is non-empty and *overwrite* is false.
            NotADirectoryError: *directory* exists and is not a directory.
        """
        directory = Path(directory)
        description_path = Path(model_description)
        binary_items = tuple(
            (platform, Path(binary)) for platform, binary in (binaries or {}).items()
        )
        source_entries = tuple(Path(entry) for entry in (sources or ()))
        resource_entries = tuple(Path(entry) for entry in (resources or ()))
        documentation_entries = tuple(Path(entry) for entry in (documentation or ()))

        document = _load_description(description_path, fmi_version)
        for _, binary_path in binary_items:
            if not binary_path.is_file():
                raise ValueError(
                    f"binary {binary_path} does not exist or is not a file"
                )
        if document.fmi_version == "2.0":
            validator = Fmi2ModelDescriptionSemanticValidator()
            for _, binary_path in binary_items:
                validator.validate_binary(document, binary_path.name)
        elif document.fmi_version.startswith("3."):
            Fmi3ModelDescriptionSemanticValidator().validate(document)
        else:
            raise ValueError(f"Unsupported FMI version {document.fmi_version!r}")
        for header in source_entries:
            _require_entry(header, "header")
        for resource in resource_entries:
            _require_entry(resource, "resource")
        for entry in documentation_entries:
            _require_entry(entry, "documentation entry")

        _prepare_root(directory, overwrite)
        with cls(directory, mode="w") as fmu:
            fmu.add_model_description(description_path)
            for platform, binary_path in binary_items:
                fmu.add_binary(binary_path, platform=platform)
            for header in source_entries:
                _add_entry(fmu, header, "header", "sources", fmu.add_sources)
            for resource in resource_entries:
                _add_entry(fmu, resource, "resource", "resources", fmu.add_resource)
            for entry in documentation_entries:
                _add_entry(
                    fmu,
                    entry,
                    "documentation entry",
                    "documentation",
                    fmu.add_documentation,
                )

        return directory

    @classmethod
    def package(
        cls,
        path: str | Path,
        *,
        model_description: str | Path,
        binaries: dict[str, str | Path] | None = None,
        sources: Iterable[str | Path] | None = None,
        resources: Iterable[str | Path] | None = None,
        documentation: Iterable[str | Path] | None = None,
        fmi_version: str | None = None,
        stage_dir: str | Path | None = None,
    ) -> Path:
        """Stage an FMU tree and write it as a deterministic ``.fmu`` archive.

        A temporary staging directory is used unless *stage_dir* is given; both
        are cleared first. ``package_archive`` sorts the entries and stamps the
        FMI epoch. The produced archive is verified to contain the description
        at the root and every binary under ``binaries/<platform>/``.
        """
        path = Path(path)
        binary_items = tuple(
            (platform, Path(binary)) for platform, binary in (binaries or {}).items()
        )
        inputs = {
            "model_description": model_description,
            "binaries": binaries,
            "sources": sources,
            "resources": resources,
            "documentation": documentation,
            "fmi_version": fmi_version,
        }

        if stage_dir is None:
            with tempfile.TemporaryDirectory(prefix="pyssp-standard-fmu-") as tmp:
                stage = cls.stage(Path(tmp) / "fmu", overwrite=True, **inputs)
                archive = package_archive(stage, path)
        else:
            stage = cls.stage(Path(stage_dir), overwrite=True, **inputs)
            archive = package_archive(stage, path)

        required = {"modelDescription.xml"} | {
            f"binaries/{platform_component(platform)}/{binary.name}"
            for platform, binary in binary_items
        }
        with zipfile.ZipFile(archive) as bundle:
            present = set(bundle.namelist())
        missing = sorted(required - present)
        if missing:
            raise ValueError(
                f"packaged archive {archive} is missing {', '.join(missing)}; "
                "modelDescription.xml must be at the root and the binary under "
                "binaries/<platform>/"
            )
        return archive

    def add_binary(self, source: str | Path, *, platform: str | None = None) -> str:
        source_path = Path(source)
        if platform:
            target_path = f"binaries/{platform_component(platform)}/{source_path.name}"
        else:
            target_path = f"binaries/{source_path.name}"
        return self.runtime.add_file(source_path, target_name=target_path)

    def add_resource(self, source: str | Path, *, target_name: str | None = None) -> str:
        source_path = Path(source)
        name = target_name or source_path.name
        target_path = f"resources/{name}"
        return self.runtime.add_file(source_path, target_name=target_path)

    def add_sources(self, source: str | Path, *, target_name: str | None = None) -> str:
        source_path = Path(source)
        name = target_name or source_path.name
        return self.runtime.add_file(source_path, target_name=f"sources/{name}")

    def add_documentation(self, source: str | Path, *, target_name: str | None = None) -> str:
        source_path = Path(source)
        name = target_name or source_path.name
        return self.runtime.add_file(source_path, target_name=f"documentation/{name}")

    @property
    def model_description(self) -> ModelDescription:
        return ModelDescription(self.runtime.root / "modelDescription.xml", mode=self.mode)

    def set_generation_date_and_time(self, dt: datetime | str | None = None) -> None:
        """Set the generation date and time on the modelDescription.xml document.

        Args:
            dt: A datetime, ISO 8601 string, or None.
                None defaults to "2000-01-01T00:00:00Z".
        """
        with ModelDescription(self.runtime.root / "modelDescription.xml", mode=self.mode) as md:
            md.set_generation_date_and_time(dt)

    def package_as_ssp(
        self,
        path: str | Path,
        *,
        system_name: str | None = None,
        component_name: str | None = None,
        resource_name: str | None = None,
        implementation: str | None = None,
        expose_system_connectors: bool = False,
    ) -> Path:
        path = Path(path)
        component_name = component_name or self.path.stem
        system_name = system_name or path.stem

        with self.model_description as md:
            resolved_implementation = implementation or md.xml.interface_type or "ModelExchange"

        with SSP(path, mode="w", fixed_timestamp=self.fixed_timestamp) as ssp:
            ssp.add_fmu(
                component_name=component_name,
                fmu_path=self.path,
                resource_name=resource_name,
                implementation=resolved_implementation,
                expose_system_connectors=expose_system_connectors,
            )
            with ssp.system_structure() as ssd:
                ssd.rename(system_name)
                if ssd.system is not None:
                    ssd.system.name = system_name

        return path
