# Airpine 🏔️

**Alpine.js integration for the Air framework with excellent Python DX**

Airpine provides a Pythonic, type-safe API for working with Alpine.js directives in [Air](https://github.com/feldroy/air) applications. Get excellent IDE autocomplete, natural chained syntax, and type-safe modifiers.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install airpine
```

Or with uv:
```bash
uv pip install airpine
```

## Quick Start

```python
from air import Air, Div, Button, Input, Span
from airpine import Alpine

app = Air()

@app.page
def index():
    return Div(
        # Counter with reactive state
        Button("-", **Alpine.at.click("count--")),
        Span(**Alpine.x.text("count")),
        Button("+", **Alpine.at.click("count++")),
        
        **Alpine.x.data({"count": 0}),
    )
```

Don't forget to include Alpine.js in your HTML:

```python
from air import Html, Head, Body, Script

def layout(content):
    return Html(
        Head(
            Script(
                src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js",
                defer=True
            )
        ),
        Body(content)
    )
```

## Why Airpine?

###  Before (painful)
```python
# No autocomplete, easy typos, ugly syntax
Button(**{"@click.prevent.once": "save()"})
Form(**{"x-data": '{"email": "", "valid": false}', "@submit.prevent": "send()"})
```

### With Airpine (delightful)
```python
# Full IDE autocomplete, natural syntax, composable
Button(**Alpine.at.click.prevent.once("save()"))
Form(**(
    Alpine.x.data({"email": "", "valid": False}) |
    Alpine.at.submit.prevent("send()")
))
```

## Features

- ✨ **Excellent IDE autocomplete** - All Alpine.js directives and modifiers typed
- 🔗 **Natural chained syntax** - `Alpine.at.click.prevent.once("handler()")`
- 🎯 **Type-safe** - Catch errors at dev time, not runtime
- 🐍 **Pythonic** - Use Python dicts for x-data, no manual JSON
- 🧩 **Composable** - Merge attributes with `|` operator
- 🚀 **Production-ready** - Comprehensive tests, proper escaping

## Python → Alpine Cheat Sheet

| Python | Alpine HTML | Description |
|--------|-------------|-------------|
| `Alpine.x.data({"count": 0})` | `x-data='{ "count": 0 }'` | Component state |
| `Alpine.x.text("message")` | `x-text="message"` | Set text content |
| `Alpine.x.show("visible")` | `x-show="visible"` | Toggle visibility (CSS) |
| `Alpine.x.if_("condition")` | `x-if="condition"` | Conditional rendering (DOM) |
| `Alpine.x.for_("item in items")` | `x-for="item in items"` | Loop rendering |
| `Alpine.x.model("email")` | `x-model="email"` | Two-way binding |
| `Alpine.x.bind.class_("active")` | `x-bind:class="active"` | Bind class |
| `Alpine.x.ref("myInput")` | `x-ref="myInput"` | Element reference |
| `Alpine.at.click("handler()")` | `@click="handler()"` | Click event |
| `Alpine.at.submit.prevent("send()")` | `@submit.prevent="send()"` | Submit with preventDefault |
| `Alpine.at.keydown.enter("submit()")` | `@keydown.enter="submit()"` | Enter key |
| `Alpine.at.click.outside("close()")` | `@click.outside="close()"` | Click outside |
| `Alpine.at.input.debounce(300)("search()")` | `@input.debounce.300ms="search()"` | Debounced input |

## Common Patterns

### Modal with ESC key

```python
Div(
    Button("Open", **Alpine.at.click("open = true")),
    Div(
        # Modal content
        **Alpine.x.show("open"),
    ),
    **(
        Alpine.x.data({"open": False}) |
        Alpine.at.keydown.escape.window("open = false") |
        Alpine.at.click.outside("open = false")
    )
)
```

### Form Validation

```python
Form(
    Input(
        type="email",
        **(
            Alpine.x.model("email") |
            Alpine.at.input.debounce(300)("validate()")
        )
    ),
    Button(
        "Submit",
        **Alpine.x.bind.disabled("!valid")
    ),
    **Alpine.x.data({
        "email": "",
        "valid": False,
        "validate": RawJS("function() { this.valid = this.email.includes('@'); }")
    })
)
```

### Tabs

```python
from airpine import Alpine

Div(
    # Tab buttons
    Div(
        Button("Tab 1", **( 
            Alpine.at.click("tab = 0") |
            Alpine.x.bind.class_("{ 'active': tab === 0 }")
        )),
        Button("Tab 2", **(
            Alpine.at.click("tab = 1") |
            Alpine.x.bind.class_("{ 'active': tab === 1 }")
        )),
    ),
    # Tab content
    Div("Content 1", **Alpine.x.show("tab === 0")),
    Div("Content 2", **Alpine.x.show("tab === 1")),
    
    **Alpine.x.data({"tab": 0})
)
```

### Search with Debounce

```python
Div(
    Input(
        placeholder="Search...",
        **(
            Alpine.x.model("query") |
            Alpine.at.input.debounce(300)("search()")
        )
    ),
    Div(**Alpine.x.html("results")),
    
    **Alpine.x.data({
        "query": "",
        "results": "",
        "search": RawJS("""function() {
            fetch('/search?q=' + this.query)
                .then(r => r.text())
                .then(html => { this.results = html; });
        }""")
    })
)
```

## API Reference

### Events (`Alpine.at.*`)

#### Common Events
- `click`, `dblclick` - Mouse clicks
- `input`, `change` - Form input
- `submit` - Form submission
- `keydown`, `keyup`, `keypress` - Keyboard
- `focus`, `blur` - Focus events
- `mouseenter`, `mouseleave` - Mouse movement
- `scroll`, `resize` - Window events

#### Event Modifiers
- `.prevent` - preventDefault()
- `.stop` - stopPropagation()
- `.once` - Run only once
- `.self` - Only if event.target is element itself
- `.window` - Listen on window
- `.document` - Listen on document
- `.outside` / `.away` - Click outside element
- `.passive` - Passive event listener
- `.capture` - Use capture phase
- `.debounce(ms)` - Debounce handler (default 250ms)
- `.throttle(ms)` - Throttle handler (default 250ms)

#### Keyboard Modifiers
- `.enter`, `.space`, `.escape`, `.tab`
- `.up`, `.down`, `.left`, `.right`
- `.backspace`, `.delete`, `.home`, `.end`
- `.page_up`, `.page_down`
- `.shift`, `.ctrl`, `.alt`, `.meta`, `.cmd`
- `.key(name)` - Custom key (e.g., `.key("f1")`)

Chain modifiers: `Alpine.at.keydown.ctrl.enter("submit()")`

### Directives (`Alpine.x.*`)

#### State & Rendering
- `data(dict | str)` - Component state
- `text(expr)` - Set text content
- `html(expr)` - Set innerHTML (⚠️ XSS risk with user input)
- `show(expr)` - Toggle visibility (CSS)
- `if_(expr)` - Conditional rendering (DOM)
- `for_(expr)` - Loop rendering

#### Binding
- `model(expr)` - Two-way data binding
- `bind.class_(expr)` - Bind class
- `bind.style(expr)` - Bind style
- `bind.href(expr)` - Bind href
- `bind.{attribute}(expr)` - Bind any attribute

#### Lifecycle & Utils
- `init(expr)` - Run on initialization
- `effect(expr)` - Re-run when dependencies change
- `ref(name)` - Element reference (access via `$refs.name`)
- `cloak()` - Hide until Alpine loads
- `ignore()` - Ignore element and children
- `ignore_self()` - Ignore only element, not children
- `key(expr)` - Unique key for x-for items
- `id(list)` - Generate scoped IDs for accessibility
- `teleport(selector)` - Move content to selector
- `modelable(prop)` - Make property bindable with x-model

#### Transitions
- `transition()` - Simple transition
- `transition.enter(classes)` - Enter transition
- `transition.enter_start(classes)` - Enter start state
- `transition.enter_end(classes)` - Enter end state
- `transition.leave(classes)` - Leave transition
- `transition.leave_start(classes)` - Leave start state
- `transition.leave_end(classes)` - Leave end state

#### Plugins (require Alpine.js plugins)
- `intersect(expr)` - Intersection observer
- `mask(expr)` - Input masking
- `trap(expr)` - Focus trapping
- `collapse()` - Collapse animation

### Model Modifiers

- `Alpine.x.model(expr)` - Basic two-way binding
- `Alpine.x.model.lazy(expr)` - Update on change instead of input
- `Alpine.x.model.number(expr)` - Convert to number
- `Alpine.x.model.boolean(expr)` - Convert to boolean
- `Alpine.x.model.trim(expr)` - Trim whitespace
- `Alpine.x.model.fill(expr)` - Use input's value attribute to initialize
- `Alpine.x.model.debounce(ms)(expr)` - Debounce updates
- `Alpine.x.model.throttle(ms)(expr)` - Throttle updates

## Using RawJS

For JavaScript functions/expressions in x-data, use `RawJS`:

```python
from airpine import Alpine, RawJS

Alpine.x.data({
    "count": 0,
    "increment": RawJS("function() { this.count++; }"),
    "reset": RawJS("() => { this.count = 0; }")
})
```

**⚠️ Security Warning**: Never use `RawJS` with user input - it can lead to XSS vulnerabilities.

## Escaping & Security

### How Escaping Works
1. Airpine converts Python values to valid JavaScript
2. Air (the framework) handles HTML attribute escaping at render time
3. You don't need to pre-escape values

### Safe by Default
```python
# Safe - strings are automatically escaped
Alpine.x.data({"message": "User's <script>alert('xss')</script> input"})
# Generates: x-data='{ "message": "User\'s <script>alert(\'xss\')</script> input" }'
# Air escapes this when rendering to HTML
```

### Only Use Raw JS for Functions
```python
# Safe - RawJS for JavaScript code only
Alpine.x.data({
    "userInput": user_provided_data,  # ✅ Safe - escaped
    "handler": RawJS("function() { ... }")  # ✅ Safe - your code
})

# NEVER do this:
Alpine.x.data({
    "handler": RawJS(f"function() {{ alert('{user_input}'); }}")  # ❌ XSS!
})
```

## Merging Attributes

Use Python's `|` operator to merge attributes:

```python
attrs = (
    Alpine.x.data({"count": 0}) |
    Alpine.at.click("count++") |
    Alpine.x.bind.class_("'active'")
)

Button("Click me", **attrs)
```

**Note**: When merging, the last value wins for duplicate keys.

## Supported Versions

- Python: ≥ 3.11
- Alpine.js: 3.x
- Air: ≥ 0.30.0

## Examples

See `examples/demo.py` for a complete demo application with:
- Counter
- Toggle visibility
- Form validation
- Dropdowns
- Modals
- Search with debounce
- Tabs
- And more!

Run the demo:
```bash
python examples/demo.py
# Visit http://localhost:8001
```

## Development

### Setup

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Install playwright browsers (for integration tests)
playwright install chromium
```

### Commands (using just)

```bash
# Run tests
just test

# Run specific tests
just test-serializer
just test-builders

# Lint and format
just lint
just format
just fix

# Type check
just typecheck

# Run all checks
just check

# Run demo
just demo
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please:
1. Add tests for new features
2. Run `just check` before submitting
3. Follow existing code style

## Links

- [Air Framework](https://github.com/feldroy/air)
- [Alpine.js](https://alpinejs.dev/)
- [Documentation](https://github.com/kentro-tech/airpine#readme)
