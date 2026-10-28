"""Every collected test file owns exactly one explicit level in FILE_LEVELS."""

from __future__ import annotations

from pathlib import Path

from conftest import FILE_LEVELS, TESTS_DIR
from test_markers import LEVEL_MARKERS


def _relative(item) -> str:
    return Path(str(item.path)).resolve().relative_to(TESTS_DIR).as_posix()


def _collected_files(request) -> set[str]:
    return {_relative(item) for item in request.session.items}


def _level_markers(item) -> list[str]:
    return [marker.name for marker in item.iter_markers() if marker.name in LEVEL_MARKERS]


def test_every_collected_test_file_is_in_the_level_table(request):
    missing = sorted(_collected_files(request) - FILE_LEVELS.keys())

    assert not missing, f"test files missing from FILE_LEVELS: {missing}"


def test_no_level_table_entry_is_stale(request):
    on_disk = {
        path.resolve().relative_to(TESTS_DIR).as_posix()
        for path in TESTS_DIR.rglob("test_*.py")
    }
    stale = sorted(FILE_LEVELS.keys() - on_disk)

    assert not stale, f"FILE_LEVELS entries without a test file: {stale}"


def test_every_collected_test_has_exactly_one_level_marker(request):
    offenders = {
        item.nodeid: _level_markers(item)
        for item in request.session.items
        if len(_level_markers(item)) != 1
    }

    assert not offenders, f"tests without exactly one level marker: {offenders}"
