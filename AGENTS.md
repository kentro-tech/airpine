# Airpine for Alpine.js

## Core Concept

Airpine maps Alpine.js directives to Python with full autocomplete. Two namespaces:
- `Alpine.at.*` → `@event` (shorthand)
- `Alpine.x.*` → `x-directive`

For reserved words (`if`, `class`, `for`) use trailing underscore (like `x.for_` or `x.bind.class_`)

## Quick Examples

```python
from airpine import Alpine, RawJS
from air import Div, Button, Input

**Alpine.x.data({"count": 0, "message": ""})
# → x-data="{ count: 0, message: '' }"

**Alpine.at.click("count++")
# → @click="count++"

**Alpine.at.keydown.ctrl.enter("save()")
# → @keydown.ctrl.enter="save()"

**Alpine.x.model("email")
# → x-model="email"

**Alpine.x.show("open")
# → x-show="open"

**Alpine.x.if_("visible")
# → x-if="visible"

# Binding attributes
**Alpine.x.bind.class_("{ 'active': isActive }")
# → x-bind:class="{ 'active': isActive }"

**Alpine.x.bind.disabled("!valid")
# → x-bind:disabled="!valid"

# Loops
**Alpine.x.for_("item in items")
# → x-for="item in items"

**Alpine.x.key("item.id")
# → x-key="item.id"
```

## Merging Attributes

Use `|` to combine:

```python
Button(
    "Submit",
    **(
        Alpine.x.data({"loading": False}) |
        Alpine.at.click.prevent("submit()") |
        Alpine.x.bind.disabled("loading")
    )
)
```

## JavaScript Functions

Use `RawJS` for functions in x-data:

```python
**Alpine.x.data({
    "count": 0,
    "increment": RawJS("function() { this.count++; }"),
    "reset": RawJS("() => { this.count = 0; }")
})
# → x-data="{ count: 0, increment: function() { this.count++; }, reset: () => { this.count = 0; } }"
```