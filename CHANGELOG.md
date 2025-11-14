# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-11-14

### 🚀 Production Ready Release

This release makes Airpine production-ready with critical bug fixes, comprehensive testing, and full Alpine.js 3.x directive coverage.

### Added
- ✨ Comprehensive unit test suite (107 tests covering serializer and builders)
- 📚 Production-ready documentation with examples and API reference
- 🔧 `justfile` for common development commands
- 🎯 Missing Alpine.js directives:
  - `x-key` for efficient x-for list updates
  - `x-id` for scoped ID generation (accessibility)
  - `x-modelable` for custom component model binding
  - `x-ignore.self` to ignore only element, not children
- 🎨 `x-transition` namespace with typed variants:
  - `Alpine.x.transition.enter()`, `.leave()`, `.enter_start()`, `.enter_end()`, `.leave_start()`, `.leave_end()`
- ⌨️ Additional keyboard modifiers:
  - Navigation keys: `backspace`, `delete`, `home`, `end`, `page_up`, `page_down`
  - Generic `.key(name)` helper for custom keys (e.g., `.key("f1")`)
- ⏱️ Optional milliseconds for debounce/throttle (defaults to 250ms)
  - `Alpine.at.input.debounce()` - uses default
  - `Alpine.at.input.debounce(500)` - custom ms
- 📝 x-model modifiers: `.boolean` and `.fill`
- 🔌 Alpine.js plugin directive stubs:
  - `x-intersect`, `x-mask`, `x-trap`, `x-collapse`
- 🛠️ Development tooling:
  - Ruff configuration for linting and formatting
  - Mypy configuration for type checking
  - GitHub Actions CI workflow
  - pytest configuration

### Fixed
- 🐛 **CRITICAL**: JavaScript serializer rewritten to fix multiple bugs:
  - Lists with apostrophes no longer break (`["it's", "test's"]` now works)
  - Nested structures properly escaped
  - Object keys always quoted for safety (hyphens, reserved words, etc.)
  - HTML escaping moved to Air's layer (proper separation of concerns)
  - Consistent handling of all Python types
- 🔧 Trailing underscores now properly removed (`class_` → `class`, not `class-`)
- 🎯 `__call__` now accepts `Any` type (more ergonomic API)
- ✅ `x-cloak` and `x-ignore` now render as boolean attributes (`""` instead of `True`)

### Changed
- ⚠️ **BREAKING**: JavaScript object serialization now uses double-quoted keys and proper JSON escaping
  - Old: `{ count: 0, name: 'test' }`
  - New: `{ "count": 0, "name": "test" }`
  - This is more robust and handles edge cases correctly
- 📦 Updated dependencies to stable versions
- 📖 README rewritten for production use (removed "brainstorming" disclaimer)

### Security
- 🔒 Improved escaping prevents XSS vulnerabilities in edge cases
- 🛡️ RawJS usage documented with security warnings

## [0.1.0] - 2024-11-13

### Added
- Initial release
- Basic Alpine.js directive support
- Event handlers with modifiers
- x-data, x-show, x-if, x-for, x-model
- x-bind namespace
- Chained modifier syntax
- Dict merging with `|` operator
- RawJS for JavaScript functions

---

[0.2.0]: https://github.com/kentro-tech/airpine/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/kentro-tech/airpine/releases/tag/v0.1.0
