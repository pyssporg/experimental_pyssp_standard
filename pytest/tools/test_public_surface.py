"""Guard the public surface against SSP-version tokens and internal imports."""

from __future__ import annotations

import ast
from pathlib import Path

import pyssp_standard
import pyssp_standard.tree as tree

_VERSION_TOKENS = ("Ssp1", "Ssp2", "Ssd1", "Ssc1", "Ssm1")
_TREE_NAMES = (
    "Component",
    "Connection",
    "Connector",
    "DefaultExperiment",
    "ParameterBinding",
    "ParameterMappingReference",
    "System",
)
_PUBLIC_CONTRACT_MODULES = (
    Path(pyssp_standard.__file__).with_name("tree.py"),
    Path(pyssp_standard.__file__).with_name("parameters.py"),
)


def test_public_names_have_no_version_token():
    for name in pyssp_standard.__all__:
        assert not any(token in name for token in _VERSION_TOKENS), name


def test_every_public_name_resolves():
    for name in pyssp_standard.__all__:
        assert hasattr(pyssp_standard, name), name


def test_tree_names_come_from_the_protocol_module():
    for name in _TREE_NAMES:
        assert name in pyssp_standard.__all__, name
        assert getattr(pyssp_standard, name) is getattr(tree, name), name
    assert "validate_component_fmu" in pyssp_standard.__all__


def test_public_contract_modules_do_not_import_internal_modules():
    for path in _PUBLIC_CONTRACT_MODULES:
        module = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(module):
            if isinstance(node, ast.ImportFrom):
                source = node.module or ""
                if node.level:
                    source = "." * node.level + source
                assert not source.startswith("pyssp_standard.standard"), (
                    f"{path.name} imports {source}"
                )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("pyssp_standard.standard"), (
                        f"{path.name} imports {alias.name}"
                    )
