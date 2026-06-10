# Changelog

## [2.0.1] - 2026-06-10
### Fixed
- Move debounce lock into `do_toggle` so KDE path is protected too
- Close lock fd on `BlockingIOError` to prevent fd leak
- Pass explicit `mainloop=` to `BusConnection` in `session_bus`
- Validate config keys in `touchpad-key-listener` with actionable error messages

## [2.0.0] - 2026-06-10
### Added
- Python rewrite using evdev + dbus (replaces bash/xinput version)
