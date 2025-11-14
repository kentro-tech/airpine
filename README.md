# Airpine 🏔️

**Alpine.js integration for the Air framework with excellent Python DX**

Airpine provides a Pythonic, ORM-like API for working with Alpine.js directives in [Air](https://github.com/feldroy/air) applications. Get excellent IDE autocomplete, natural chained syntax, and type-safe modifiers.

```python
from airpine import Alpine

# Clean event handling with modifiers
Button("Submit", **Alpine.at.submit.prevent("handleSubmit()"))

# Keyboard shortcuts
Input(**Alpine.at.keydown.ctrl.enter("save()"))

# Debounced input with type-safe milliseconds
Input(**Alpine.at.input.debounce(300)("search()"))

# Component state using JavaScript object notation
Div(**Alpine.x.data({"count": 0, "items": []}))
```

## Why Airpine?

### Current Approach (painful)
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

See `examples/demo.py` for examples.