"""Static gate on the package layout: root surface, packages, and module size.

Reads source text only; the package is not imported. The gate exists so the
root module list cannot grow again, every Python directory stays a real
package, only reviewed facades reach down from the lower layers, and no module
silently becomes an unreviewed monolith.
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src" / "pyssp_standard"

#: Modules allowed directly under ``src/pyssp_standard/``.
ROOT_MODULES = frozenset({"__init__.py"})

#: Directories allowed directly under ``src/pyssp_standard/``.
TOP_LEVEL_PACKAGES = frozenset(
    {"facades", "contracts", "common", "standard", "tools", "schema"}
)

#: Reviewed facade imports from lower layers, path -> facade -> reason.
#: ``common/`` and ``standard/`` reach a facade only through this registry, so
#: each edge is a deliberate, documented edit. ``reference_specs`` is the known
#: exception: document resolution opens external SSV/SSM documents through
#: their public facades.
FACADE_IMPORTS_FROM_BELOW = {
    "common/document/reference_specs.py": {
        "ssm": "opens external SSM documents through the public facade",
        "ssv": "opens external SSV documents through the public facade",
    },
    "standard/ssp1/operations/ssp_binding.py": {
        "ssm": "reads and writes parameter mappings through the public facade",
        "ssv": "reads and writes parameter sets through the public facade",
        "ssp": "annotates the archive session passed in by the caller",
    },
    "standard/ssp1/operations/ssd_fmu_iteration.py": {
        "fmu": "opens FMUs through the public facade",
    },
}

MAX_MODULE_LINES = 600

#: Modules allowed to exceed ``MAX_MODULE_LINES``, relative path -> reason.
LARGE_MODULES: dict[str, str] = {}

#: Vendored XSD payload: data, not an importable package.
DATA_DIRS = frozenset({"schema"})


def _is_data(path: Path) -> bool:
    return path.relative_to(SRC).parts[0] in DATA_DIRS


def _packages() -> list[Path]:
    return sorted(
        path
        for path in SRC.rglob("*")
        if path.is_dir() and "__pycache__" not in path.parts and not _is_data(path)
    )


def _modules() -> list[Path]:
    return sorted(
        path
        for path in SRC.rglob("*.py")
        if "__pycache__" not in path.parts and not _is_data(path)
    )


def _facade_names(
    module: str, names: list[str], package: list[str], level: int
) -> list[str]:
    """Return the facade modules a resolved import points at."""
    if level:
        base = package[: len(package) - (level - 1)]
        module = ".".join([*base, *filter(None, module.split("."))])
    else:
        prefix = "pyssp_standard."
        if not module.startswith(prefix):
            return []
        module = module[len(prefix) :]
    if module == "facades":
        return [name.split(".")[0] for name in names]
    if module.startswith("facades."):
        return [module.split(".", 1)[1]]
    return []


def _facade_imports_below_facades() -> set[tuple[str, str]]:
    edges: set[tuple[str, str]] = set()
    for path in _modules():
        relative = path.relative_to(SRC).as_posix()
        if not relative.startswith(("common/", "standard/")):
            continue
        package = relative.split("/")[:-1]
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom):
                names = [alias.name for alias in node.names]
                facades = _facade_names(node.module or "", names, package, node.level)
                edges.update((relative, facade) for facade in facades)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    facades = _facade_names(alias.name, [alias.name], package, 0)
                    edges.update((relative, facade) for facade in facades)
    return edges


def test_root_holds_only_the_package_init():
    on_disk = {path.name for path in SRC.glob("*.py")}

    assert on_disk == ROOT_MODULES, {
        "unexpected": sorted(on_disk - ROOT_MODULES),
        "missing": sorted(ROOT_MODULES - on_disk),
    }


def test_top_level_packages_are_allowlisted():
    on_disk = {
        path.name
        for path in SRC.iterdir()
        if path.is_dir() and path.name != "__pycache__"
    }

    assert on_disk == TOP_LEVEL_PACKAGES, {
        "unexpected": sorted(on_disk - TOP_LEVEL_PACKAGES),
        "missing": sorted(TOP_LEVEL_PACKAGES - on_disk),
    }


def test_every_directory_is_a_package():
    missing = sorted(
        path.relative_to(SRC).as_posix()
        for path in _packages()
        if not (path / "__init__.py").is_file()
    )

    assert not missing, f"directories without __init__.py: {missing}"


def test_lower_layers_import_only_reviewed_facades():
    found = _facade_imports_below_facades()
    reviewed = {
        (path, facade)
        for path, facades in FACADE_IMPORTS_FROM_BELOW.items()
        for facade in facades
    }

    assert not found - reviewed, (
        f"lower layer imports a facade outside the registry: {sorted(found - reviewed)}"
    )
    assert not reviewed - found, (
        f"FACADE_IMPORTS_FROM_BELOW entries without an import: {sorted(reviewed - found)}"
    )


def test_no_module_exceeds_the_size_limit():
    oversized = {
        path.relative_to(SRC).as_posix(): len(path.read_text(encoding="utf-8").splitlines())
        for path in _modules()
        if path.relative_to(SRC).as_posix() not in LARGE_MODULES
        and len(path.read_text(encoding="utf-8").splitlines()) > MAX_MODULE_LINES
    }

    assert not oversized, f"modules over {MAX_MODULE_LINES} lines: {oversized}"


def test_large_module_allowlist_names_real_files():
    unknown = sorted(name for name in LARGE_MODULES if not (SRC / name).is_file())

    assert not unknown, f"LARGE_MODULES entries without a module: {unknown}"
    assert not LARGE_MODULES, "no module currently needs a size exemption"
