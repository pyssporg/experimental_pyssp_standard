# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Expose `ModelDescription.variable_names`, the declared scalar-variable names
  of an FMI 2 or FMI 3 model description.

## [0.9.3.dev0] - 2026-11-09

### Changed

- Harden the ecosystem CI workflows shared with the pyssp org.
- Add a `CHANGELOG.md` and ruff config; rename `requirements.txt` to
  `requirements-dev.txt`.
- Use HTTPS URLs for the nested Modelica Standard submodules so CI can clone
  recursively.

