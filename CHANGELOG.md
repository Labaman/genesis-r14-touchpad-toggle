# Changelog

## [2.0.2] - 2026-06-11
### Fixed
- Fix fd leak in `do_toggle`: single `try/finally` now guarantees `lock.close()` on any exception
- Catch exceptions from `do_toggle` in event loop to prevent crash-restart cycle on transient errors
- Wrap `load_conf` in `try/except` for actionable error message on missing config file
- Validate `KEYBOARD_EVENT` path is under `/dev/input/` before opening device
- Guard against root active session (uid=0) in `get_active_session` with explicit error
- Isolate notification dbus call so its failure does not affect touchpad toggle state
- Add 2s timeout to dbus calls to cap blocking time under held lock
### Added
- systemd sandbox: `ProtectSystem=full`, `ProtectHome=read-only`, `PrivateTmp`, `NoNewPrivileges`, `ProtectKernelModules`, `ProtectKernelTunables`, `RestrictNamespaces`, `RestrictSUIDSGID`

## [2.0.1] - 2026-06-10
### Fixed
- Move debounce lock into `do_toggle` so KDE path is protected too
- Close lock fd on `BlockingIOError` to prevent fd leak
- Pass explicit `mainloop=` to `BusConnection` in `session_bus`
- Validate config keys in `touchpad-key-listener` with actionable error messages

## [2.0.0] - 2026-06-10
### Added
- Python rewrite using evdev + dbus (replaces bash/xinput version)
