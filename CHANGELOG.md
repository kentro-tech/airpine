# Changelog

All notable changes to Airpine will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-XX

### Added
- Initial release
- ORM-like chained builder API for Alpine.js directives
- Event handlers namespace (`Alpine.at`) with full modifier support
- Directives namespace (`Alpine.x`) for all core Alpine.js directives
- Attribute binding (`Alpine.x.bind`) with common attributes
- Model modifiers (`Alpine.x.model`) with debounce/throttle support
- Pre-built patterns (`AlpinePatterns`) for common UI components:
  - Toggle
  - Dropdown with click-away
  - Tabs
  - Accordion
  - Modal with ESC key
- JavaScript object notation output (avoids HTML escaping issues)
- Full IDE autocomplete support
- Type-safe numeric modifiers (debounce, throttle)
- Comprehensive examples and documentation
- MIT license

### Features
- Zero dependencies (only Air needed for usage)
- Python 3.11+ support
- Dict composition via `|` operator
- Escape hatches for custom events and directives
- Complete docstrings and type hints

[0.1.0]: https://github.com/kentro-tech/airpine/releases/tag/v0.1.0
