# Changelog

## 2026-04-17

### Modernization and setup improvements
- Ported the runnable scripts to Python 3-compatible syntax and behavior.
- Updated web server output handling to write bytes correctly via `http.server`.
- Replaced legacy `file(...)` calls with modern `open(...)`.
- Simplified POST form parsing for URL-encoded requests using `urllib.parse.parse_qs`.
- Fixed hash input encoding for generated game IDs.
- Updated CLI simulation stats to use Python's stdlib `statistics` instead of requiring `numpy`.
- Added a `--games` option to `hanabi.py` for fast/local smoke tests.

### Developer onboarding and install flow
- Added `requirements.txt`.
- Added `scripts/setup_env.sh` for one-command environment setup.
- Rewrote README with install/run instructions and a package tour.
- Added `AGENTS.md` with repository-specific maintenance guidance.
