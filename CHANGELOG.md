# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet

## [0.1.0] - 2025-11-26

### Added
- Initial release
- `Controller` class for low-level USB communication
- `HighLevelController` class with blocking moves and convenience methods
- `ControllerConsole` for interactive command-line control
- Auto-discovery of connected controllers via `discover_controllers()`
- Standalone PyQt5 GUI with:
  - Auto-discovery on startup
  - Optional `--config` JSON file for custom channel labels
  - `--list` flag to show discovered controllers
  - Position polling and display
  - Relative and absolute positioning
  - Set home (zero) functionality
- Support for all 4 motor channels
- Timeout protection for motion operations
- Comprehensive error handling with custom exceptions

### Fixed
- Motor initialization now covers all 4 channels (was only 2)
- `wait()` method now checks all 4 motors with timeout protection
- Fixed `time.delay` typo (now `time.sleep`)

### Documentation
- README with installation, usage, and API reference
- Example scripts in `examples/` directory
- PDF manuals in `docs/manuals/`

[Unreleased]: https://github.com/OWNER/newport-8742-picomotor/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/OWNER/newport-8742-picomotor/releases/tag/v0.1.0
