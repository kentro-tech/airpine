"""Airpine - Alpine.js integration for Air framework

Provides an ORM-like chained builder API for Alpine.js directives with excellent
IDE autocomplete support and natural Python syntax.

This is the recommended API for EidosUI and general Air + Alpine.js usage.

Features:
    - Natural chained syntax: Alpine.at.click.prevent.once()
    - Excellent IDE autocomplete on events, directives, and modifiers
    - Type-safe numeric modifiers (debounce, throttle)
    - JavaScript object notation output (avoids HTML escaping issues)
    - Pre-built patterns for common UI components

Example:
    from airpine import Alpine
    
    # Event handling with modifiers
    Button("Submit", **Alpine.at.submit.prevent("handleSubmit()"))
    
    # Keyboard shortcuts
    Input(**Alpine.at.keydown.ctrl.enter("save()"))
    
    # Debounced input
    Input(**Alpine.at.input.debounce(300)("search()"))
    
    # Component state
    Div(**Alpine.x.data({"count": 0, "items": []}))
    
    # Composition
    Form(**(
        Alpine.x.data({"email": ""}) |
        Alpine.at.submit.prevent("send()") |
        Alpine.at.keydown.escape("cancel()")
    ))
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple
import json
import html


class RawJS:
    """Wrapper for raw JavaScript expressions that should not be quoted.
    
    Use this when you need to pass JavaScript functions or expressions
    as values in Alpine.js x-data.
    
    Example:
        Alpine.x.data({
            "count": 0,
            "increment": RawJS("function() { this.count++ }")
        })
    """
    def __init__(self, code: str):
        self.code = code
    
    def __str__(self) -> str:
        return self.code


def _hyphenate(name: str) -> str:
    """Convert Python snake_case to HTML hyphen-case."""
    return name.replace("_", "-")


def _dict_to_alpine_obj(d: dict) -> str:
    """Convert Python dict to Alpine.js object notation (JavaScript, not JSON).
    
    Alpine accepts JavaScript object notation which doesn't require quotes around keys
    and uses single quotes for strings, avoiding HTML attribute escaping issues.
    
    Example: {"count": 0, "name": "test"} -> "{ count: 0, name: 'test' }"
    """
    if not isinstance(d, dict):
        return str(d)
    
    pairs = []
    for key, value in d.items():
        if isinstance(value, dict):
            val_str = _dict_to_alpine_obj(value)
        elif isinstance(value, RawJS):
            # Raw JavaScript - don't quote, just clean up whitespace
            val_str = str(value).replace("\n", " ").replace("\r", "")
        elif isinstance(value, str):
            # Escape HTML entities, remove newlines, and use single quotes for Alpine.js compatibility
            escaped = html.escape(value, quote=False).replace("'", "&apos;").replace("\n", " ").replace("\r", "")
            val_str = f"'{escaped}'"
        elif isinstance(value, bool):
            val_str = 'true' if value else 'false'
        elif isinstance(value, (int, float)):
            val_str = str(value)
        elif isinstance(value, list):
            # Convert to JSON and replace double quotes with single quotes
            # JavaScript/Alpine.js accepts both, but single quotes avoid HTML escaping
            val_str = json.dumps(value).replace('"', "'")
        else:
            val_str = str(value)
        
        pairs.append(f"{key}: {val_str}")
    
    return "{ " + ", ".join(pairs) + " }"


@dataclass(frozen=True)
class _AlpineAttr:
    """Immutable builder for a single Alpine directive with modifiers."""
    
    prefix: str  # "@", "x-", or "x-bind:"
    base: str    # "click", "text", "href", etc.
    mods: Tuple[str, ...] = ()
    
    def __call__(self, value: str) -> Dict[str, str]:
        """Generate the final attribute dict."""
        mod_path = "".join(f".{m}" for m in self.mods)
        if self.base:
            key = f"{self.prefix}{self.base}{mod_path}"
        else:
            # For x-model modifiers where base is empty
            key = f"{self.prefix.rstrip(':')}{mod_path}"
        return {key: value}
    
    def mod(self, *modifiers: str) -> _AlpineAttr:
        """Add custom modifiers."""
        return _AlpineAttr(self.prefix, self.base, self.mods + tuple(_hyphenate(m) for m in modifiers))
    
    # Time-based modifiers
    def debounce(self, ms: int) -> _AlpineAttr:
        """Add debounce modifier with milliseconds."""
        return self.mod("debounce", f"{ms}ms")
    
    def throttle(self, ms: int) -> _AlpineAttr:
        """Add throttle modifier with milliseconds."""
        return self.mod("throttle", f"{ms}ms")
    
    # Common event modifiers (typed for IDE completion)
    @property
    def prevent(self) -> _AlpineAttr:
        """preventDefault() modifier."""
        return self.mod("prevent")
    
    @property
    def stop(self) -> _AlpineAttr:
        """stopPropagation() modifier."""
        return self.mod("stop")
    
    @property
    def once(self) -> _AlpineAttr:
        """Run handler only once."""
        return self.mod("once")
    
    @property
    def self(self) -> _AlpineAttr:
        """Only trigger if event.target is the element itself."""
        return self.mod("self")
    
    @property
    def window(self) -> _AlpineAttr:
        """Attach listener to window."""
        return self.mod("window")
    
    @property
    def document(self) -> _AlpineAttr:
        """Attach listener to document."""
        return self.mod("document")
    
    @property
    def outside(self) -> _AlpineAttr:
        """Trigger when click is outside element."""
        return self.mod("outside")
    
    @property
    def away(self) -> _AlpineAttr:
        """Alias for outside."""
        return self.mod("away")
    
    @property
    def passive(self) -> _AlpineAttr:
        """Use passive event listener."""
        return self.mod("passive")
    
    @property
    def capture(self) -> _AlpineAttr:
        """Use capture phase."""
        return self.mod("capture")
    
    # Key modifiers
    @property
    def enter(self) -> _AlpineAttr:
        """Enter key."""
        return self.mod("enter")
    
    @property
    def escape(self) -> _AlpineAttr:
        """Escape key."""
        return self.mod("escape")
    
    @property
    def space(self) -> _AlpineAttr:
        """Space key."""
        return self.mod("space")
    
    @property
    def tab(self) -> _AlpineAttr:
        """Tab key."""
        return self.mod("tab")
    
    @property
    def up(self) -> _AlpineAttr:
        """Arrow up key."""
        return self.mod("up")
    
    @property
    def down(self) -> _AlpineAttr:
        """Arrow down key."""
        return self.mod("down")
    
    @property
    def left(self) -> _AlpineAttr:
        """Arrow left key."""
        return self.mod("left")
    
    @property
    def right(self) -> _AlpineAttr:
        """Arrow right key."""
        return self.mod("right")
    
    @property
    def shift(self) -> _AlpineAttr:
        """Shift key modifier."""
        return self.mod("shift")
    
    @property
    def ctrl(self) -> _AlpineAttr:
        """Control key modifier."""
        return self.mod("ctrl")
    
    @property
    def alt(self) -> _AlpineAttr:
        """Alt key modifier."""
        return self.mod("alt")
    
    @property
    def meta(self) -> _AlpineAttr:
        """Meta/Command key modifier."""
        return self.mod("meta")
    
    @property
    def cmd(self) -> _AlpineAttr:
        """Alias for meta."""
        return self.mod("cmd")


class _EventNamespace:
    """Namespace for @event handlers with tab completion."""
    
    # Common DOM events (typed properties for IDE completion)
    @property
    def click(self) -> _AlpineAttr:
        """Click event."""
        return _AlpineAttr("@", "click")
    
    @property
    def dblclick(self) -> _AlpineAttr:
        """Double click event."""
        return _AlpineAttr("@", "dblclick")
    
    @property
    def input(self) -> _AlpineAttr:
        """Input event."""
        return _AlpineAttr("@", "input")
    
    @property
    def change(self) -> _AlpineAttr:
        """Change event."""
        return _AlpineAttr("@", "change")
    
    @property
    def submit(self) -> _AlpineAttr:
        """Submit event."""
        return _AlpineAttr("@", "submit")
    
    @property
    def keydown(self) -> _AlpineAttr:
        """Keydown event."""
        return _AlpineAttr("@", "keydown")
    
    @property
    def keyup(self) -> _AlpineAttr:
        """Keyup event."""
        return _AlpineAttr("@", "keyup")
    
    @property
    def keypress(self) -> _AlpineAttr:
        """Keypress event."""
        return _AlpineAttr("@", "keypress")
    
    @property
    def focus(self) -> _AlpineAttr:
        """Focus event."""
        return _AlpineAttr("@", "focus")
    
    @property
    def blur(self) -> _AlpineAttr:
        """Blur event."""
        return _AlpineAttr("@", "blur")
    
    @property
    def mouseenter(self) -> _AlpineAttr:
        """Mouse enter event."""
        return _AlpineAttr("@", "mouseenter")
    
    @property
    def mouseleave(self) -> _AlpineAttr:
        """Mouse leave event."""
        return _AlpineAttr("@", "mouseleave")
    
    @property
    def mouseover(self) -> _AlpineAttr:
        """Mouse over event."""
        return _AlpineAttr("@", "mouseover")
    
    @property
    def mouseout(self) -> _AlpineAttr:
        """Mouse out event."""
        return _AlpineAttr("@", "mouseout")
    
    @property
    def scroll(self) -> _AlpineAttr:
        """Scroll event."""
        return _AlpineAttr("@", "scroll")
    
    @property
    def resize(self) -> _AlpineAttr:
        """Resize event."""
        return _AlpineAttr("@", "resize")
    
    @property
    def load(self) -> _AlpineAttr:
        """Load event."""
        return _AlpineAttr("@", "load")
    
    # Fallback for custom events
    def __getattr__(self, name: str) -> _AlpineAttr:
        """Support custom events via attribute access."""
        return _AlpineAttr("@", _hyphenate(name))
    
    def __getitem__(self, event_name: str) -> _AlpineAttr:
        """Support exact event names with special characters."""
        return _AlpineAttr("@", event_name)


class _BindNamespace:
    """Namespace for x-bind:* attributes."""
    
    # Common bound attributes
    @property
    def class_(self) -> _AlpineAttr:
        """Bind class attribute."""
        return _AlpineAttr("x-bind:", "class")
    
    @property
    def style(self) -> _AlpineAttr:
        """Bind style attribute."""
        return _AlpineAttr("x-bind:", "style")
    
    @property
    def href(self) -> _AlpineAttr:
        """Bind href attribute."""
        return _AlpineAttr("x-bind:", "href")
    
    @property
    def src(self) -> _AlpineAttr:
        """Bind src attribute."""
        return _AlpineAttr("x-bind:", "src")
    
    @property
    def value(self) -> _AlpineAttr:
        """Bind value attribute."""
        return _AlpineAttr("x-bind:", "value")
    
    @property
    def disabled(self) -> _AlpineAttr:
        """Bind disabled attribute."""
        return _AlpineAttr("x-bind:", "disabled")
    
    @property
    def checked(self) -> _AlpineAttr:
        """Bind checked attribute."""
        return _AlpineAttr("x-bind:", "checked")
    
    @property
    def selected(self) -> _AlpineAttr:
        """Bind selected attribute."""
        return _AlpineAttr("x-bind:", "selected")
    
    @property
    def readonly(self) -> _AlpineAttr:
        """Bind readonly attribute."""
        return _AlpineAttr("x-bind:", "readonly")
    
    # Fallback for any attribute
    def __getattr__(self, name: str) -> _AlpineAttr:
        return _AlpineAttr("x-bind:", _hyphenate(name))
    
    def __getitem__(self, attr_name: str) -> _AlpineAttr:
        """Support exact attribute names."""
        return _AlpineAttr("x-bind:", attr_name)


class _ModelNamespace:
    """Namespace for x-model with modifiers."""
    
    def __call__(self, expr: str) -> Dict[str, str]:
        """Plain x-model."""
        return {"x-model": expr}
    
    @property
    def number(self) -> _AlpineAttr:
        """Convert to number."""
        return _AlpineAttr("x-model", "", ("number",))
    
    @property
    def lazy(self) -> _AlpineAttr:
        """Update on change instead of input."""
        return _AlpineAttr("x-model", "", ("lazy",))
    
    @property
    def trim(self) -> _AlpineAttr:
        """Trim whitespace."""
        return _AlpineAttr("x-model", "", ("trim",))
    
    def debounce(self, ms: int) -> _AlpineAttr:
        """Debounce updates."""
        return _AlpineAttr("x-model", "", ("debounce", f"{ms}ms"))
    
    def throttle(self, ms: int) -> _AlpineAttr:
        """Throttle updates."""
        return _AlpineAttr("x-model", "", ("throttle", f"{ms}ms"))


class _DirectiveNamespace:
    """Namespace for x-* directives."""
    
    # Common directives as callable methods
    def text(self, expr: str) -> Dict[str, str]:
        """Set text content."""
        return {"x-text": expr}
    
    def html(self, expr: str) -> Dict[str, str]:
        """Set HTML content."""
        return {"x-html": expr}
    
    def show(self, expr: str) -> Dict[str, str]:
        """Conditionally show element (CSS)."""
        return {"x-show": expr}
    
    def if_(self, expr: str) -> Dict[str, str]:
        """Conditionally render element (DOM)."""
        return {"x-if": expr}
    
    def for_(self, expr: str) -> Dict[str, str]:
        """Loop over items."""
        return {"x-for": expr}
    
    def data(self, expr: str | dict) -> Dict[str, str]:
        """Component state."""
        value = expr if isinstance(expr, str) else _dict_to_alpine_obj(expr)
        return {"x-data": value}
    
    def ref(self, name: str) -> Dict[str, str]:
        """Reference to element."""
        return {"x-ref": name}
    
    def init(self, expr: str) -> Dict[str, str]:
        """Initialize component."""
        return {"x-init": expr}
    
    def cloak(self) -> Dict[str, bool]:
        """Hide until Alpine loads."""
        return {"x-cloak": True}
    
    def ignore(self) -> Dict[str, bool]:
        """Ignore this element."""
        return {"x-ignore": True}
    
    def transition(self, expr: str = "") -> Dict[str, str]:
        """Transition directive."""
        return {"x-transition": expr}
    
    def effect(self, expr: str) -> Dict[str, str]:
        """Side effect that re-runs."""
        return {"x-effect": expr}
    
    def teleport(self, target: str) -> Dict[str, str]:
        """Teleport to selector."""
        return {"x-teleport": target}
    
    # Sub-namespaces
    @property
    def bind(self) -> _BindNamespace:
        """Bind attributes namespace."""
        return _BindNamespace()
    
    @property
    def model(self) -> _ModelNamespace:
        """Two-way binding namespace."""
        return _ModelNamespace()
    
    # Fallback for custom directives
    def __getattr__(self, name: str) -> callable:
        directive = f"x-{_hyphenate(name)}"
        def _setter(expr: str) -> Dict[str, str]:
            return {directive: expr}
        return _setter


class AlpineBuilder:
    """ORM-like builder for Alpine.js attributes with excellent IDE support."""
    
    at = _EventNamespace()
    x = _DirectiveNamespace()
    
    @staticmethod
    def merge(*dicts: Dict[str, str]) -> Dict[str, str]:
        """Merge multiple attribute dicts."""
        result = {}
        for d in dicts:
            result |= d
        return result


# Export singleton instance as Alpine
Alpine = AlpineBuilder()
