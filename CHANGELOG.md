## [0.3.0] - 
### Added
### Changed
- API configuration has changed to match the data models of ORC-OS. This prepares LiveORC and ORC-OS to work
  together operationally. This also prepares cloud processing using ORC-OS API as backend.
- New naming convention `crosssection` and "Cross section" (in admin interface) for end points and database models
  for cross sections, used to estimate discharge and water levels.
### Deprecated
- NodeORC has been entirely removed. Cloud processing will be replaced in a future release by the ORC-OS API.
  Currently temporarily, cloud processing is not possible. Only edge processing with ORC-OS is supported.
### Removed
- All references to `profile`. Has been deprecated in favour of `crosssection` which resembles better the naming
  convention throughout the ORC ecosystem.
### Fixed
- Video POST without any files was not possible. This is now fixed. Only metadata can be posted now.
### Security


## [0.2.3] - 2025-11-17
### Added
- Camera config admin view now also displays a 3D view of the camera configuration.
### Changed
### Deprecated
### Removed
### Fixed
- Camera config admin view checks if CRS is provided. If not, the map view is not displayed.
- PATCH /api/site/<site_pk>/cameraconfig/<pk> was not working, now properly functions.
### Security


## [0.2.2] - 2025-10-02
### Added
### Changed
### Deprecated
### Removed
### Fixed
- PATCH /api/site/<site_pk>/timeseries/<pk> was not working, now properly functions.
### Security


## [0.2.1] - 2025-07-01
### Added
### Changed
- New fields `q_raw`, `v_av`, `v_bulk` in `api.models.time_series.py` for storing raw
  optical discharge, average surface velocity and bulk velocity.
- Added new time series fields to admin and API views.
### Deprecated
### Removed
### Fixed
- Recipe serialization now includes "id"
- fixed test assertions by using `assertEqual` instead of deprecated `assertEquals`
- fixed wrongly preferred HTML serializer for API POST/GET request to time series objects. This now
  is JSON by default.
- storage port mapping for internal storage set to correct port.
### Security


## [0.2.0] - 2024-09-27
### Added
- Style and logos
### Changed
- Bump nodeorc version to 0.2.1
### Deprecated
### Removed
### Fixed
- Improvements in README.md
### Security


## [0.1.1] - 2024-06-14
### Added
- Tabular downloads
### Changed
- Bump nodeorc version
### Deprecated
### Removed
### Fixed
### Security
- Freeze of package versions
- Docker image so that a frozen version is used by end users


## [0.1.0] - 2024-05-31
### Added
- First pre-release of LiveOpenRiverCam
### Changed
### Deprecated
### Removed
### Fixed
### Security

