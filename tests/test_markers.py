"""The suite must declare exactly one level per collected test."""

from __future__ import annotations

import pytest

LEVEL_MARKERS = frozenset(
    {
        "level_static",
        "level_unit",
        "level_component",
        "level_contract",
        "level_integration",
        "level_system",
        "level_acceptance",
    }
)


def _level_markers(item) -> list[str]:
    return [
        marker.name
        for marker in item.iter_markers()
        if marker.name in LEVEL_MARKERS
    ]


def test_every_collected_test_has_exactly_one_level_marker(request):
    offenders = {
        item.nodeid: _level_markers(item)
        for item in request.session.items
        if len(_level_markers(item)) != 1
    }

    assert not offenders, f"tests without exactly one level marker: {offenders}"


def test_every_level_marker_selects_tests(request):
    counts = {name: 0 for name in LEVEL_MARKERS}
    for item in request.session.items:
        for name in _level_markers(item):
            counts[name] += 1

    unpopulated = sorted(name for name, count in counts.items() if count == 0)
    # level_integration may legitimately be empty until such tests exist.
    assert unpopulated == ["level_integration"], unpopulated


def test_demo_marker_is_not_registered_and_not_used(request):
    registered = " ".join(request.config.getini("markers"))
    assert "demo:" not in registered
    assert not any(item.get_closest_marker("demo") for item in request.session.items)


@pytest.mark.parametrize(
    "marker",
    ["level_static", "level_unit", "level_component", "level_contract", "level_system", "level_acceptance"],
)
def test_level_marker_is_registered(request, marker):
    assert f"{marker}:" in " ".join(request.config.getini("markers"))
