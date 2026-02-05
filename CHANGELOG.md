## [0.2.X] - 
### Added
### Changed
### Deprecated
### Removed
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

