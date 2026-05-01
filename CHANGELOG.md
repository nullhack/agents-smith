# Changelog

All notable changes to agents-smith will be documented in this file.

## [0.3.0] - 20260501

### Fixed

- Fix package build configuration: add missing `[build-system]` section and use `setuptools.packages.find` to include all subpackages (delivery, domain, application, infrastructure, data). Previously only `smith/__init__.py` and `smith/__main__.py` were included in the wheel, causing `ModuleNotFoundError: No module named 'smith.delivery'` when installed as a dependency in another project.

## [0.2.0] - 20260501

### Changed

- Minor version bump.

## [0.1.0] - 20260501

### Added

- Initial release.