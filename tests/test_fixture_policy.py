"""Static contract for the fixture tree: cases, size, allowlist, paths."""

from __future__ import annotations

from pathlib import Path

from support.fixtures import (
    EMBRACE,
    EMBRACE_FMU_DIR,
    EMBRACE_MODEL_DESCRIPTION,
    EMBRACE_SSD,
    EMBRACE_SSM,
    EXTERNAL_SSV,
    FIXTURES,
    MIXED_SSD,
    SRMD,
    SSV2,
    TEXT_PAYLOAD,
)

TESTS_DIR = Path(__file__).resolve().parent
MAX_FIXTURE_BYTES = 512 * 1024

REQUIRED_HEADINGS = (
    "## Requirement or fault",
    "## Level",
    "## Input provenance",
    "## Independent oracle",
    "## Comparison",
    "## Update policy",
    "## What this case proves",
)

#: Vendored FMI binaries that must stay byte-identical.
LARGE_FIXTURES = {
    "embrace/resources/0002_ECS_SW.fmu": "vendored FMI binary, copied verbatim",
    "embrace/resources/0003_Consumer.fmu": "vendored FMI binary, copied verbatim",
    "embrace/resources/0004_Atmos.fmu": "vendored FMI binary, copied verbatim",
    "embrace/resources/0005_AdaptionUnit.fmu": "vendored FMI binary, copied verbatim",
}


def _cases() -> list[Path]:
    return sorted(path for path in FIXTURES.iterdir() if path.is_dir())


def _fixture_files() -> list[Path]:
    return sorted(path for path in FIXTURES.rglob("*") if path.is_file())


def test_every_fixture_case_has_a_case_document():
    missing = [path.name for path in _cases() if not (path / "case.md").is_file()]

    assert not missing, f"fixture cases without case.md: {missing}"


def test_every_case_document_has_required_headings():
    offenders = {}
    for case in _cases():
        text = (case / "case.md").read_text(encoding="utf-8")
        absent = [heading for heading in REQUIRED_HEADINGS if heading not in text]
        if not text.startswith("# Case: ") or absent:
            offenders[case.name] = absent or ["# Case: <name>"]

    assert not offenders, f"case.md files missing required headings: {offenders}"


def test_large_fixture_allowlist_entries_exist():
    missing = sorted(name for name in LARGE_FIXTURES if not (FIXTURES / name).is_file())

    assert not missing, f"LARGE_FIXTURES entries without a file: {missing}"


def test_no_fixture_exceeds_the_size_limit_unless_allowlisted():
    oversized = sorted(
        path.relative_to(FIXTURES).as_posix()
        for path in _fixture_files()
        if path.stat().st_size > MAX_FIXTURE_BYTES
        and path.relative_to(FIXTURES).as_posix() not in LARGE_FIXTURES
    )

    assert not oversized, f"fixture files over 512 KB without a reason: {oversized}"


def test_no_test_source_uses_a_cwd_relative_fixture_path():
    offenders = {}
    for path in sorted(TESTS_DIR.rglob("*.py")):
        if "__pycache__" in path.parts or path.resolve() == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8")
        hits = [
            marker
            for marker in ('Path("tests/', "Path('tests/", "__fixture__")
            if marker in text
        ]
        if hits:
            offenders[path.relative_to(TESTS_DIR).as_posix()] = hits

    assert not offenders, f"cwd-relative or legacy fixture paths: {offenders}"


def test_fixture_constants_resolve_under_the_fixture_tree():
    constants = {
        "EMBRACE": EMBRACE,
        "EMBRACE_SSD": EMBRACE_SSD,
        "EMBRACE_SSM": EMBRACE_SSM,
        "EMBRACE_FMU_DIR": EMBRACE_FMU_DIR,
        "EMBRACE_MODEL_DESCRIPTION": EMBRACE_MODEL_DESCRIPTION,
        "MIXED_SSD": MIXED_SSD,
        "EXTERNAL_SSV": EXTERNAL_SSV,
        "SSV2": SSV2,
        "SRMD": SRMD,
        "TEXT_PAYLOAD": TEXT_PAYLOAD,
    }
    root = FIXTURES.resolve()
    offenders = {
        name: str(path)
        for name, path in constants.items()
        if root not in path.resolve().parents or not path.exists()
    }

    assert not offenders, f"fixture constants outside {root}: {offenders}"
