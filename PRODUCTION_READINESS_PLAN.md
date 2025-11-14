# Airpine Production Readiness Plan

**Goal**: Make Airpine production-ready for commercial applications by fixing critical bugs, filling feature gaps, hardening edge cases, and establishing comprehensive testing.

**Status**: Early development → Production-ready v0.2.0

---

## Executive Summary

Airpine needs work in 4 critical areas:

1. **Serializer bugs** (CRITICAL) - Current JS object generation breaks with apostrophes, nested data, and has escaping issues
2. **Missing Alpine.js features** (HIGH) - Key directives and modifiers missing (x-transition variants, x-key, x-id, etc.)
3. **API warts** (MEDIUM) - Inconsistent value handling, trailing underscore issues, strict typing
4. **Testing gap** (HIGH) - No unit or integration tests; escaping bugs invisible without browser tests

**Estimated effort**: 2-4 days total
- Serializer + Tests: 1-2 days
- Directive coverage + Docs: 0.5-1 day  
- Packaging/CI: 0.5 day

---

## 1. CRITICAL: Fix JavaScript Object Serializer

### Problem
Current `_dict_to_alpine_obj()` has multiple bugs:
- Breaks on lists with apostrophes (replaces `"` with `'` unsafely)
- Inconsistent escaping (strings escaped, lists not)
- Unquoted object keys fail on hyphens/reserved words
- HTML escaping in wrong layer (should be Air's job)
- Single-quote strategy conflicts with Alpine.js expectations

### Solution: Rewrite Serializer

**New implementation**:
```python
def _to_js(value):
    """Convert Python value to valid JavaScript expression."""
    if isinstance(value, RawJS):
        return value.code
    if isinstance(value, str):
        return json.dumps(value)  # Safe, proper escaping
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_to_js(v) for v in value) + "]"
    if isinstance(value, dict):
        items = []
        for k, v in value.items():
            key = json.dumps(str(k))  # Always quote keys
            items.append(f"{key}: {_to_js(v)}")
        return "{ " + ", ".join(items) + " }"
    if value is None:
        return 'null'
    return json.dumps(str(value))  # Fallback

def _dict_to_alpine_obj(d: dict) -> str:
    """Convert Python dict to Alpine.js object notation."""
    if not isinstance(d, dict):
        return str(d)
    return _to_js(d)
```

**Key improvements**:
- Uses `json.dumps()` for strings (proper escaping)
- Always quotes object keys (safer parsing)
- Consistent handling of nested structures
- No HTML escaping (let Air handle at render time)
- RawJS works at any depth

### Test Cases Needed
```python
# Strings with special characters
{"msg": "He said 'hello' & \"goodbye\""}  # Apostrophes and quotes
{"html": "<script>alert('xss')</script>"}  # HTML entities
{"emoji": "Hello 👋 World"}                # Unicode
{"backslash": "C:\\Users\\test"}           # Backslashes

# Nested structures
{"user": {"name": "Alice", "tags": ["admin", "user"]}}
{"items": [{"id": 1}, {"id": 2}]}

# RawJS at various depths
{"onClick": RawJS("() => alert('hi')")}
{"data": {"fn": RawJS("function() { return 42; }")}}

# Edge cases
{"empty": ""}
{"zero": 0}
{"false": False}
{"null": None}
{"hyphen-key": "value"}
{"reserved": "class"}

# Lists
["item's", 'with "quotes"', "and & symbols"]
```

---

## 2. HIGH: Missing Alpine.js Features

### 2.1 Directives

#### x-key (for x-for tracking)
```python
class _DirectiveNamespace:
    def key(self, expr: str) -> Dict[str, str]:
        """Unique key for x-for items."""
        return {"x-key": expr}

# Usage:
Template(**Alpine.x.for_("item in items"), **Alpine.x.key("item.id"))
```

#### x-id (scoped ID generation)
```python
def id(self, expr: str | list[str]) -> Dict[str, str]:
    """Generate scoped IDs for accessibility."""
    value = expr if isinstance(expr, str) else _to_js(expr)
    return {"x-id": value}

# Usage:
Div(**Alpine.x.id(["input", "label"]))
```

#### x-modelable (custom model bindings)
```python
def modelable(self, expr: str) -> Dict[str, str]:
    """Make component property bindable with x-model."""
    return {"x-modelable": expr}

# Usage:
Div(**Alpine.x.data({"value": ""}), **Alpine.x.modelable("value"))
```

#### x-ignore.self (ignore only self, not children)
```python
def ignore_self(self) -> Dict[str, str]:
    """Ignore this element but not children."""
    return {"x-ignore.self": ""}

# Keep existing:
def ignore(self) -> Dict[str, str]:
    """Ignore this element and children."""
    return {"x-ignore": ""}
```

#### x-transition namespace (typed variants)
```python
class _TransitionNamespace:
    """Namespace for x-transition variants."""
    
    def __call__(self, expr: str = "") -> Dict[str, str]:
        """Generic transition."""
        return {"x-transition": expr}
    
    @property
    def enter(self) -> _AlpineAttr:
        return _AlpineAttr("x-transition:", "enter")
    
    @property
    def enter_start(self) -> _AlpineAttr:
        return _AlpineAttr("x-transition:", "enter-start")
    
    @property
    def enter_end(self) -> _AlpineAttr:
        return _AlpineAttr("x-transition:", "enter-end")
    
    @property
    def leave(self) -> _AlpineAttr:
        return _AlpineAttr("x-transition:", "leave")
    
    @property
    def leave_start(self) -> _AlpineAttr:
        return _AlpineAttr("x-transition:", "leave-start")
    
    @property
    def leave_end(self) -> _AlpineAttr:
        return _AlpineAttr("x-transition:", "leave-end")

class _DirectiveNamespace:
    @property
    def transition(self) -> _TransitionNamespace:
        return _TransitionNamespace()

# Usage:
Div(**Alpine.x.transition.enter()("transition ease-out duration-300"))
Div(**Alpine.x.transition.enter_start()("opacity-0 scale-90"))
Div(**Alpine.x.transition.leave_end()("opacity-0"))
```

#### Plugin directive stubs (optional)
```python
def intersect(self, expr: str) -> Dict[str, str]:
    """Intersection observer (requires Alpine intersect plugin)."""
    return {"x-intersect": expr}

def mask(self, expr: str) -> Dict[str, str]:
    """Input masking (requires Alpine mask plugin)."""
    return {"x-mask": expr}

def trap(self, expr: str) -> Dict[str, str]:
    """Focus trapping (requires Alpine focus plugin)."""
    return {"x-trap": expr}

def collapse(self) -> Dict[str, str]:
    """Collapse animation (requires Alpine collapse plugin)."""
    return {"x-collapse": ""}
```

### 2.2 Event Modifiers

#### Additional key modifiers
```python
class _AlpineAttr:
    # Navigation keys
    @property
    def backspace(self) -> _AlpineAttr:
        return self.mod("backspace")
    
    @property
    def delete(self) -> _AlpineAttr:
        return self.mod("delete")
    
    @property
    def home(self) -> _AlpineAttr:
        return self.mod("home")
    
    @property
    def end(self) -> _AlpineAttr:
        return self.mod("end")
    
    @property
    def page_up(self) -> _AlpineAttr:
        return self.mod("page-up")
    
    @property
    def page_down(self) -> _AlpineAttr:
        return self.mod("page-down")
    
    # Generic key helper
    def key(self, name: str) -> _AlpineAttr:
        """Arbitrary key name."""
        return self.mod(name.lower())

# Usage:
Input(**Alpine.at.keydown.ctrl.backspace("deleteWord()"))
Input(**Alpine.at.keydown.key("f1")("showHelp()"))
```

#### Debounce/throttle with optional ms
```python
def debounce(self, ms: int | None = None) -> _AlpineAttr:
    """Add debounce modifier (default 250ms if no ms provided)."""
    if ms is None:
        return self.mod("debounce")
    return self.mod("debounce", f"{ms}ms")

def throttle(self, ms: int | None = None) -> _AlpineAttr:
    """Add throttle modifier (default 250ms if no ms provided)."""
    if ms is None:
        return self.mod("throttle")
    return self.mod("throttle", f"{ms}ms")

# Usage:
Input(**Alpine.at.input.debounce()("search()"))      # Uses default
Input(**Alpine.at.input.debounce(500)("search()"))   # Custom ms
```

#### Camel modifier for x-bind
```python
class _BindNamespace:
    # Add to existing methods:
    @property
    def camel(self) -> _AlpineAttr:
        """Convert attribute name to camelCase."""
        return self.mod("camel")

# Usage:
Div(**Alpine.x.bind.some_prop.camel("value"))  # -> :someProp.camel
```

### 2.3 x-model modifiers

#### Missing modifiers
```python
class _ModelNamespace:
    @property
    def boolean(self) -> _AlpineAttr:
        """Convert to boolean."""
        return _AlpineAttr("x-model", "", ("boolean",))
    
    @property
    def fill(self) -> _AlpineAttr:
        """Use input's value attribute to initialize."""
        return _AlpineAttr("x-model", "", ("fill",))

# Usage:
Input(**Alpine.x.model.boolean("agreed"))
Input(**Alpine.x.model.fill("name"), value="Default")
```

---

## 3. MEDIUM: API Improvements

### 3.1 Trailing underscore cleanup
```python
def _hyphenate(name: str) -> str:
    """Convert Python snake_case to HTML hyphen-case."""
    return name.rstrip("_").replace("_", "-")
```

Prevents `class_` → `class-` and aligns with Air's attribute behavior.

### 3.2 Accept Any in __call__
```python
from typing import Any

class _AlpineAttr:
    def __call__(self, value: Any) -> Dict[str, str]:
        """Generate the final attribute dict."""
        mod_path = "".join(f".{m}" for m in self.mods)
        if self.base:
            key = f"{self.prefix}{self.base}{mod_path}"
        else:
            key = f"{self.prefix.rstrip(':')}{mod_path}"
        return {key: str(value)}
```

Allows ergonomic use: `Alpine.x.show(True)`, `Alpine.at.click(42)`, etc.

### 3.3 Fix x-cloak and x-ignore rendering
```python
def cloak(self) -> Dict[str, str]:
    """Hide until Alpine loads."""
    return {"x-cloak": ""}  # Empty string for boolean attribute

def ignore(self) -> Dict[str, str]:
    """Ignore this element."""
    return {"x-ignore": ""}
```

Ensures Air renders them as boolean attributes correctly.

---

## 4. HIGH: Testing Strategy

### 4.1 Unit Tests (pytest)

**Test file**: `tests/test_serializer.py`
```python
def test_strings_with_quotes():
    result = _dict_to_alpine_obj({"msg": "He said 'hello'"})
    assert '"msg": "He said \'hello\'"' in result

def test_nested_structures():
    result = _dict_to_alpine_obj({"user": {"name": "Alice", "age": 30}})
    assert '"user": { "name": "Alice", "age": 30 }' in result

def test_rawjs_at_any_depth():
    result = _dict_to_alpine_obj({"fn": RawJS("() => 42")})
    assert '() => 42' in result

def test_lists_with_apostrophes():
    result = _dict_to_alpine_obj({"items": ["it's", "test's"]})
    # Should not break
```

**Test file**: `tests/test_builders.py`
```python
def test_event_with_modifiers():
    attrs = Alpine.at.click.prevent.once("save()")
    assert attrs == {"@click.prevent.once": "save()"}

def test_x_data_dict():
    attrs = Alpine.x.data({"count": 0, "name": "test"})
    assert '"count": 0' in attrs["x-data"]
    assert '"name": "test"' in attrs["x-data"]

def test_x_model_modifiers():
    assert Alpine.x.model.number("age") == {"x-model.number": "age"}
    assert Alpine.x.model.lazy("email") == {"x-model.lazy": "email"}

def test_x_transition_variants():
    attrs = Alpine.x.transition.enter()("transition ease-out")
    assert attrs == {"x-transition:enter": "transition ease-out"}

def test_key_modifiers():
    attrs = Alpine.at.keydown.ctrl.enter("submit()")
    assert attrs == {"@keydown.ctrl.enter": "submit()"}

def test_trailing_underscore_cleanup():
    # Should handle class_ correctly
    attrs = Alpine.x.bind.class_("active")
    assert attrs == {"x-bind:class": "active"}
```

### 4.2 Integration Tests (Playwright + Air)

**Setup**: Create test Air apps, render in headless browser, verify behavior

**Test file**: `tests/integration/test_alpine_integration.py`
```python
import pytest
from playwright.sync_api import Page, expect
import uvicorn
from multiprocessing import Process

def test_x_data_initializes(page: Page):
    """Verify x-data creates reactive state."""
    page.goto("http://localhost:8002/test-data")
    expect(page.locator('[data-test="counter"]')).to_have_text("0")

def test_click_event_works(page: Page):
    """Verify @click modifiers work."""
    page.goto("http://localhost:8002/test-click")
    page.click('[data-test="increment"]')
    expect(page.locator('[data-test="counter"]')).to_have_text("1")

def test_x_model_two_way_binding(page: Page):
    """Verify x-model creates two-way binding."""
    page.goto("http://localhost:8002/test-model")
    page.fill('input[name="username"]', "Alice")
    expect(page.locator('[data-test="display"]')).to_have_text("Alice")

def test_escaping_with_quotes(page: Page):
    """Verify data with quotes doesn't break."""
    page.goto("http://localhost:8002/test-escaping")
    # Page should render without JS errors
    assert page.evaluate("() => !window.hasErrors")
    
def test_x_key_reactivity(page: Page):
    """Verify x-for with x-key maintains element identity."""
    page.goto("http://localhost:8002/test-for-key")
    # Add test for DOM element reuse when reordering

def test_keyboard_shortcuts(page: Page):
    """Verify key modifiers work."""
    page.goto("http://localhost:8002/test-keys")
    page.keyboard.press("Control+Enter")
    expect(page.locator('[data-test="result"]')).to_have_text("submitted")

def test_x_transition_animations(page: Page):
    """Smoke test for transitions."""
    page.goto("http://localhost:8002/test-transition")
    page.click('[data-test="toggle"]')
    # Just verify no errors; detailed animation testing is overkill
```

**Test apps**: `tests/integration/test_app.py`
```python
from air import Air, Div, Button, Span, Input, Template
from airpine import Alpine

app = Air()

@app.get("/test-data")
def test_data():
    return Div(
        Span(**Alpine.x.text("count"), **{"data-test": "counter"}),
        **Alpine.x.data({"count": 0})
    )

@app.get("/test-click")
def test_click():
    return Div(
        Button("Increment", **Alpine.at.click("count++"), **{"data-test": "increment"}),
        Span(**Alpine.x.text("count"), **{"data-test": "counter"}),
        **Alpine.x.data({"count": 0})
    )

# ... more test routes
```

**CI Configuration**: GitHub Actions
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]" pytest playwright
      - run: playwright install chromium
      - run: pytest tests/
```

---

## 5. Documentation Gaps

### 5.1 Update README.md

**Remove**: "This is brainstorming" disclaimer

**Add**:
1. **Installation**: `pip install airpine`
2. **Supported versions**: Python ≥3.11, Alpine.js 3.x
3. **Quick start** with Alpine CDN script
4. **Mapping cheat sheet**: Python → Alpine
5. **Escaping rules**: When to use RawJS vs strings
6. **Plugin usage**: How to include and use Alpine plugins
7. **API reference**: All directives and modifiers

### 5.2 Create API_REFERENCE.md

Complete reference of all:
- Events (`Alpine.at.*`)
- Directives (`Alpine.x.*`)
- Modifiers (all variants)
- Special cases (`RawJS`, merging dicts)

### 5.3 Create EXAMPLES.md

**Real-world patterns**:
- Form validation
- Modals with ESC handling
- Dropdowns with click-away
- Search with debounce
- Lists with x-key
- Transitions
- Keyboard shortcuts
- Nested components

### 5.4 Document Escaping Rules

**Critical for users**:
```markdown
## Escaping Rules

### JavaScript Object Generation
- Airpine converts Python dicts to valid JavaScript
- Air handles HTML attribute escaping at render time
- **Don't pre-escape** values; let the framework handle it

### Using RawJS
Use `RawJS()` for JavaScript functions/expressions:
```python
Alpine.x.data({
    "count": 0,
    "increment": RawJS("function() { this.count++ }")
})
```

**Warning**: Never use `RawJS()` with user input (XSS risk)

### Merging Dicts
Last value wins when merging:
```python
Alpine.at.click("first()") | Alpine.at.click("second()")
# Result: @click="second()"
```

Use separate events or chain in one expression instead.
```

---

## 6. Edge Cases & Warts

### 6.1 Known Issues (to fix)

**CRITICAL**:
- ❌ Lists with apostrophes break serializer
- ❌ Nested structures not consistently escaped
- ❌ Unquoted keys fail on hyphens/reserved words

**HIGH**:
- ❌ Missing x-key (common for x-for)
- ❌ Missing x-transition variants (common for animations)
- ❌ Missing x-id (needed for accessibility)
- ❌ No integration tests (escaping bugs invisible)

**MEDIUM**:
- ❌ Trailing underscores produce spurious hyphens
- ❌ __call__ too strict (str only)
- ❌ x-cloak/x-ignore might render incorrectly as booleans

### 6.2 Unexpected Behaviors

**Dict merging with `|`**:
- Last value wins for duplicate keys
- Can silently override earlier attributes
- **Mitigation**: Document clearly; consider warning in tests

**RawJS whitespace stripping**:
- Newlines/carriage returns removed
- Needed for valid HTML attributes
- **Mitigation**: Document; users should write compact functions

**Air attribute processing**:
- Air converts `_` to `-` and strips trailing `_`
- Airpine must align with this
- **Mitigation**: Use same `_hyphenate` strategy

**Alpine.js version differences**:
- Directives/modifiers change between Alpine versions
- Current focus: Alpine 3.x
- **Mitigation**: Document supported version; link to Alpine 3.x docs

---

## 7. Testing Matrix

### Unit Tests Coverage

| Category | Test Cases |
|----------|-----------|
| Serializer - Strings | Quotes, apostrophes, HTML entities, backslashes, Unicode |
| Serializer - Nested | Dicts in dicts, lists in dicts, mixed |
| Serializer - RawJS | Top-level, nested, in lists |
| Serializer - Edge cases | Empty strings, None, zero, false, hyphenated keys |
| Events | All modifiers (prevent, stop, once, keys, etc.) |
| Directives | x-data, x-show, x-if, x-bind.*, x-model.*, x-transition.* |
| Modifiers | Debounce/throttle (with/without ms), key combos |
| API | Trailing underscore, Any values, dict merging |

### Integration Tests Coverage

| Feature | Browser Test |
|---------|--------------|
| State initialization | x-data creates reactive state |
| Event handlers | @click increments counter |
| Modifiers | prevent/stop work correctly |
| Two-way binding | x-model syncs input ↔ state |
| Conditional rendering | x-show/x-if toggle visibility |
| Lists | x-for renders items, x-key maintains identity |
| Keys | Class binding switches on state change |
| Keyboard | Ctrl+Enter, Escape work |
| Transitions | Enter/leave toggle (smoke test) |
| Escaping | Data with quotes/HTML doesn't break |

### Browser Matrix
- **Primary**: Chromium (headless)
- **Optional**: Firefox, WebKit (for extra confidence)

---

## 8. Packaging & Quality

### 8.1 Type Hints
```python
from typing import Any, Dict, Tuple

def _to_js(value: Any) -> str: ...
def _dict_to_alpine_obj(d: dict) -> str: ...

class _AlpineAttr:
    def __call__(self, value: Any) -> Dict[str, str]: ...
    def mod(self, *modifiers: str) -> _AlpineAttr: ...
```

Add `py.typed` for PEP 561 compliance.

### 8.2 Linting & Formatting
- **ruff**: Fast linter
- **black**: Code formatter
- **mypy**: Type checking

**pyproject.toml**:
```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "UP", "RUF"]

[tool.black]
line-length = 100

[tool.mypy]
strict = true
```

### 8.3 Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
```

### 8.4 Version Strategy
- **Current**: 0.1.0 (early dev)
- **After fixes**: 0.2.0 (breaking serializer change)
- **Future**: SemVer for public API stability

---

## 9. Implementation Checklist

### Phase 1: Critical Fixes (1-2 days)
- [x] Rewrite `_dict_to_alpine_obj()` with new serializer
- [x] Add comprehensive serializer unit tests
- [x] Fix trailing underscore in `_hyphenate()`
- [x] Update `__call__` to accept `Any`
- [x] Fix x-cloak/x-ignore to render as boolean attributes
- [ ] Add integration test harness (Playwright + test Air app)
- [ ] Write 10+ integration tests covering escaping, events, binding

### Phase 2: Feature Completeness (0.5-1 day)
- [x] Add x-key directive
- [x] Add x-id directive  
- [x] Add x-modelable directive
- [x] Add x-ignore.self variant
- [x] Add x-transition namespace with variants (enter, leave, start, end)
- [ ] Add transition modifiers (opacity, scale, duration, delay, origin)
- [x] Add missing key modifiers (backspace, delete, home, end, page_up, page_down)
- [x] Add generic `key(name)` helper
- [x] Add optional ms for debounce/throttle
- [x] Add x-model.boolean and x-model.fill modifiers
- [x] Add plugin stubs (intersect, mask, trap, collapse)

### Phase 3: Documentation (0.5 day)
- [x] Rewrite README (remove brainstorming, add installation, quick start)
- [x] Add mapping cheat sheet (Python → Alpine)
- [x] Document escaping rules
- [x] Document RawJS usage and warnings
- [x] Document merging behavior
- [x] API reference integrated into README
- [x] Real-world patterns included in README
- [x] Add plugin usage guide
- [x] Link to Alpine 3.x documentation

### Phase 4: Packaging & CI (0.5 day)
- [x] Add type hints to all public APIs
- [ ] Add py.typed marker
- [x] Configure ruff, mypy
- [ ] Add pre-commit hooks
- [x] Set up GitHub Actions CI (unit tests)
- [x] Update pyproject.toml metadata
- [x] Add supported versions (Python ≥3.11, Alpine 3.x)
- [x] Version to 0.2.0
- [x] Add CHANGELOG.md

---

## 10. Success Criteria

✅ **Production-ready when**:
1. All serializer unit tests pass (strings, nested, RawJS, edge cases)
2. All integration tests pass in headless Chromium
3. No JavaScript console errors in test apps
4. All Alpine 3.x core directives and common modifiers supported
5. Documentation complete (README, API, examples, escaping rules)
6. Type hints complete and mypy passes
7. CI runs on all PRs/pushes
8. Version 0.2.0 published

---

## 11. Future Enhancements (Post v0.2.0)

**Not blocking production use, but nice to have**:

### Advanced Transition DSL
```python
Alpine.x.transition.enter().opacity().scale().duration(200).origin("top")
```
More ergonomic than string-based classes.

### Expression Helpers
```python
Alpine.expr.var("count").inc()  # -> "count++"
Alpine.expr.toggle("open")      # -> "open = !open"
```
Type-safe expression building (likely overkill).

### Server-side Validation
Validate Alpine expressions at build time to catch typos.

### Large Data Optimization
For huge x-data objects, consider:
```html
<script type="application/json" id="data">
  { "items": [...1000 items...] }
</script>
<div x-data x-init="$data = JSON.parse($el.previousElementSibling.textContent)">
```

### Alpine 4.x Support
When Alpine 4.x is released, add compatibility testing.

---

## 12. Risk Mitigation

### Double-Escaping Risk
**Issue**: Removing `html.escape()` assumes Air handles attribute escaping.
**Mitigation**: Integration tests verify HTML attributes are escaped correctly and Alpine receives decoded values.

### Alpine Version Drift
**Issue**: Directives/modifiers may change between Alpine versions.
**Mitigation**: Document supported range (3.x); link to versioned docs; test against pinned CDN.

### Dict Merge Confusion
**Issue**: `|` operator silently overwrites duplicate keys.
**Mitigation**: Document clearly; consider test that warns on duplicate keys in demo/examples.

### Plugin Missing at Runtime
**Issue**: Using plugin directives without including plugin scripts fails silently.
**Mitigation**: Document requirement; optionally add runtime warning (but likely overkill).

---

## 13. Questions to Resolve

1. **Should we support Alpine 2.x?** 
   - **Recommendation**: No, focus on 3.x (latest stable)

2. **Should we validate Alpine expressions?**
   - **Recommendation**: No, too complex; let browser report errors

3. **Should we warn when merging duplicate keys?**
   - **Recommendation**: Yes, add warning in tests; document in README

4. **Should plugin stubs include runtime checks?**
   - **Recommendation**: No, keep simple; document plugin requirements

5. **Should we support Python 3.9/3.10?**
   - **Recommendation**: Yes, drop only `|` operator docs for 3.8; use `Alpine.merge()` instead

---

## Summary of Warts & Edges

### Current Warts
1. **Serializer breaks on apostrophes in lists** → FIXED in Phase 1
2. **Inconsistent escaping** → FIXED in Phase 1
3. **Unquoted keys fail** → FIXED in Phase 1  
4. **Missing x-key, x-id, x-transition variants** → FIXED in Phase 2
5. **Trailing underscore produces spurious hyphens** → FIXED in Phase 1
6. **No tests = bugs invisible** → FIXED in Phase 1
7. **Type hints incomplete** → FIXED in Phase 4

### Remaining Edges (by design)
1. **Dict merge with `|` overwrites duplicates** → Documented
2. **RawJS strips newlines** → Documented
3. **Alpine version-specific features** → Documented
4. **Plugins require external scripts** → Documented

---

## Conclusion

Airpine can become production-ready with **2-4 days of focused work**:
- Fix critical serializer bugs (highest impact)
- Fill obvious feature gaps (x-key, x-transition, etc.)
- Add comprehensive tests (unit + integration)
- Polish docs and packaging

After these changes, Airpine will be a robust, predictable library suitable for commercial applications.
