# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [2.0.0] - 2019-03-12

### Added

- Added option to logistics algorithm to optimise to minimum start delay. This
  is utilised for the corrective maintenance strategy.
- Added post calculation analysis classes and methods to the static module for
  energy, availability, logistics and financials. 
- Added statistical method for generating multiple data points calculated with 
  varying random seeds for sub-system failures. The results of all data points 
  are now returned for external analysis.
- The OPEX component of LCOE is now calculated and returned.
- Vessel names are now included in output events tables.
- Added startProjectDate input to collect the actual start date of the project 
  so energy and OPEX tables start from year 0.
- Added curtailDevices input to trigger option for devices to be shut down 
  indefinitely on failure (not tested).
- Added numberOfSimulations input to collect the number of data points to be
  used for statistics.
- Added NumberOfParallelActions input to set how many maintenance actions 
  can be completed by one vessel (default to 10).
- Added correctivePrepTime input to allow the amount of time required for
  preparation of a corrective maintenance event to be set (defaults to 48
  hours).
- Allowed exclusion of sub-systems from calendar or corrective maintenance if
  they are given maintenance intervals or health thresholds of zero or less.

### Changed

- Changed package name from dtocean-operations to dtocean-maintenance.
- Renamed modules.
- Ensured failure rate is always read from the dtocean-reliability module.
- Ensured ports and weather windows are always read from the dtocean-logistics
  module.
- Refactored LCOE_Calculator.__postCalculation using new static post-analysis 
  functions and improved outputs.
- The power_prod_perD input is now a dictionary, containing the device names as
  keys, rather than a numpy array.
- A RuntimeError is now raised if no weather windows can be found for an
  operation.

### Removed

- Removed whichOptim, checkNoSolutionWP6Files and integrateSelectPort inputs
  as no longer functional.

### Fixed

- Fixed bug in distinguishing between reliability data of moorings and
  umbilical cables.
- Fixed bug in retrieving reliability data for multi-hub layouts.
- Fixed bug which occurred if no corrective maintenance events where simulated.
- Fixed bug with port selection if no operations are requested.
- Fixed bug which occurred if the number of operations was divisible by the
  number of parallel ship operations.
- Fixed start delay from corrective maintenance operations when previous
  operation not completed before the scheduled start date.
- Fixed labour costs not being shared when undertaking parallel operations.
- The corrective maintenance table is now correctly sorted after addition of
  downtime (which extends sub-system lifetime).
- Fixed scheduling of calendar based maintenance to respect the allowed months
  of operations and ensure that the first operation occurs within the given
  range.
- The sub-system MTTF is now used to determine how long a sub-system with 
  calendar maintenance will exhibit perfect reliability from deployment and 
  after maintenance.
- Added waiting time to operation duration calculations, which was missing.
- Reorder check on the impact of calendar maintenance on corrective maintenance
  events and the shift  their operation request dates.
- Fixed check for day after which failures can occur for sub-systems with
  calendar based maintenance, when no maintenance actions are scheduled.
- Fixed double counting of umbilical cable reliability data if both electrical 
  and moorings modules inputs are given.

## [1.0.0] - 2017-01-05

### Added

- Initial import of dtocean-operations from SETIS.
