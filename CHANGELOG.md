# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

### Added

- Added option to logistics algorithm to optimise to minimise start delay. This
  is utilised for the corrective maintenance strategy.

### Changed

- Changed module name from dtocean-operations to dtocean-maintenance.
- Renamed modules.
- Always read failure rate from dtocean-reliability.
- Always read ports and weather windows from dtocean-logistics.

### Fixed

- Debugged conditional, calendar and corrective maintenance strategies.

## [1.0.0] - 2017-01-05

### Added

- Initial import of dtocean-operations from SETIS.
