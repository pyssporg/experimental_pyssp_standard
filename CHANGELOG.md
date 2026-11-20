# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.9.4.dev0] - 2026-11-20

### Added

- Add `FMU.stage()` and `FMU.package()`: write a validated FMU directory tree
  and a deterministic `.fmu` archive from a model description plus binaries,
  sources, resources, and documentation. (`051c8c7`)
- Expose `ModelDescription.variable_names`, the declared scalar-variable names
  of an FMI 2 or FMI 3 model description. (`a287171`)

### Changed

- Convert the build to setuptools with the version read dynamically from
  `pyssp_standard.__version__`, and require Python >= 3.11. (`22442e2`)

## [0.9.3.dev0] - 2026-11-09

### Changed

- Harden the ecosystem CI workflows shared with the pyssp org.
- Add a `CHANGELOG.md` and ruff config; rename `requirements.txt` to
  `requirements-dev.txt`.
- Use HTTPS URLs for the nested Modelica Standard submodules so CI can clone
  recursively.

