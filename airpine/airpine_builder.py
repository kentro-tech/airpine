"""Airpine - Alpine.js integration for Air framework

Provides an ORM-like chained builder API for Alpine.js directives with excellent
IDE autocomplete support and natural Python syntax.

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
from typing import Any

from air.tags.utils import clean_html_attr_key


class RawJS(str):
    """Wrapper for raw JavaScript expressions that should not be quoted.
    
    Use this when you need to pass JavaScript functions or expressions
    as values in Alpine.js x-data.
    
    Example:
        Alpine.x.data({
            "count": 0,
            "increment": RawJS("function() { this.count++ }")
        })
    """
    pass


def _to_js(value: Any) -> str:
    """Convert Python value to Alpine.js-compatible JavaScript.
    
    Uses unquoted object keys and single-quoted strings to avoid HTML escaping issues.
    Alpine.js evaluates x-data as JavaScript, not JSON, so this is valid and avoids
    double-escaping when Air renders to HTML attributes.
    
    Args:
        value: Any Python value to convert
        
    Returns:
        Valid JavaScript expression as string (Alpine.js compatible)
    """
    if isinstance(value, RawJS):
        # Raw JavaScript - strip newlines for valid HTML attributes
        return value.replace("\n", " ").replace("\r", "")
    if isinstance(value, str):
        # Use single quotes and escape them
        escaped = (
            value.replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace("\n", "\\n")
            .replace("\r", "")
        )
        return f"'{escaped}'"
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, (int, float)):
        return str(value)
    if value is None:
        return 'null'
    if isinstance(value, (list, tuple)):
        items = [_to_js(item) for item in value]
        return "[" + ", ".join(items) + "]"
    if isinstance(value, dict):
        pairs = []
        for k, v in value.items():
            # Unquoted keys (valid JS, avoids HTML escaping)
            # Convert hyphens and special chars in keys to underscores for valid identifiers
            key_str = str(k).replace("-", "_").replace(" ", "_")
            pairs.append(f"{key_str}: {_to_js(v)}")
        return "{ " + ", ".join(pairs) + " }"
    # Fallback: convert to string with single quotes
    escaped = str(value).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


@dataclass(frozen=True)
class _AlpineAttr:
    """Immutable builder for a single Alpine directive with modifiers."""
    
    prefix: str  # "@", "x-", or "x-bind:"
    base: str    # "click", "text", "href", etc.
    mods: tuple[str, ...] = ()
    
    def __call__(self, value: Any) -> dict[str, str]:
        """Generate the final attribute dict.
        
        Args:
            value: Any value to convert to string for the attribute
        """
        mod_path = "".join(f".{m}" for m in self.mods)
        key = f"{self.prefix}{self.base}{mod_path}"
        return {key: str(value)}
    
    def mod(self, *modifiers: str) -> _AlpineAttr:
        """Add custom modifiers."""
        new_mods = self.mods + tuple(clean_html_attr_key(m) for m in modifiers)
        return _AlpineAttr(self.prefix, self.base, new_mods)
    
    # Time-based modifiers
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
    
    # Navigation keys
    @property
    def backspace(self) -> _AlpineAttr:
        """Backspace key."""
        return self.mod("backspace")
    
    @property
    def delete(self) -> _AlpineAttr:
        """Delete key."""
        return self.mod("delete")
    
    @property
    def home(self) -> _AlpineAttr:
        """Home key."""
        return self.mod("home")
    
    @property
    def end(self) -> _AlpineAttr:
        """End key."""
        return self.mod("end")
    
    @property
    def page_up(self) -> _AlpineAttr:
        """Page up key."""
        return self.mod("page-up")
    
    @property
    def page_down(self) -> _AlpineAttr:
        """Page down key."""
        return self.mod("page-down")
    
    def key(self, name: str) -> _AlpineAttr:
        """Arbitrary key name (e.g., 'f1', 'f12')."""
        return self.mod(name.lower())


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
        return _AlpineAttr("@", clean_html_attr_key(name))
    
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
        return _AlpineAttr("x-bind:", clean_html_attr_key(name))
    
    def __getitem__(self, attr_name: str) -> _AlpineAttr:
        """Support exact attribute names."""
        return _AlpineAttr("x-bind:", attr_name)


class _ModelNamespace:
    """Namespace for x-model with modifiers."""
    
    def __call__(self, expr: str) -> dict[str, str]:
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
    
    @property
    def boolean(self) -> _AlpineAttr:
        """Convert to boolean."""
        return _AlpineAttr("x-model", "", ("boolean",))
    
    @property
    def fill(self) -> _AlpineAttr:
        """Use input's value attribute to initialize empty data."""
        return _AlpineAttr("x-model", "", ("fill",))
    
    def debounce(self, ms: int | None = None) -> _AlpineAttr:
        """Debounce updates (default 250ms if no ms provided)."""
        if ms is None:
            return _AlpineAttr("x-model", "", ("debounce",))
        return _AlpineAttr("x-model", "", ("debounce", f"{ms}ms"))
    
    def throttle(self, ms: int | None = None) -> _AlpineAttr:
        """Throttle updates (default 250ms if no ms provided)."""
        if ms is None:
            return _AlpineAttr("x-model", "", ("throttle",))
        return _AlpineAttr("x-model", "", ("throttle", f"{ms}ms"))


class _TransitionNamespace:
    """Namespace for x-transition variants."""
    
    def __call__(self, expr: str = "") -> dict[str, str]:
        """Generic transition."""
        return {"x-transition": expr}
    
    @property
    def enter(self) -> _AlpineAttr:
        """Transition enter phase."""
        return _AlpineAttr("x-transition:", "enter")
    
    @property
    def enter_start(self) -> _AlpineAttr:
        """Transition enter start state."""
        return _AlpineAttr("x-transition:", "enter-start")
    
    @property
    def enter_end(self) -> _AlpineAttr:
        """Transition enter end state."""
        return _AlpineAttr("x-transition:", "enter-end")
    
    @property
    def leave(self) -> _AlpineAttr:
        """Transition leave phase."""
        return _AlpineAttr("x-transition:", "leave")
    
    @property
    def leave_start(self) -> _AlpineAttr:
        """Transition leave start state."""
        return _AlpineAttr("x-transition:", "leave-start")
    
    @property
    def leave_end(self) -> _AlpineAttr:
        """Transition leave end state."""
        return _AlpineAttr("x-transition:", "leave-end")


class _DirectiveNamespace:
    """Namespace for x-* directives."""
    
    # Common directives as callable methods
    def text(self, expr: str) -> dict[str, str]:
        """Set text content."""
        return {"x-text": expr}
    
    def html(self, expr: str) -> dict[str, str]:
        """Set HTML content."""
        return {"x-html": expr}
    
    def show(self, expr: str) -> dict[str, str]:
        """Conditionally show element (CSS)."""
        return {"x-show": expr}
    
    def if_(self, expr: str) -> dict[str, str]:
        """Conditionally render element (DOM)."""
        return {"x-if": expr}
    
    def for_(self, expr: str) -> dict[str, str]:
        """Loop over items."""
        return {"x-for": expr}
    
    def data(self, expr: str | dict) -> dict[str, str]:
        """Component state."""
        value = expr if isinstance(expr, str) else _to_js(expr)
        return {"x-data": value}
    
    def ref(self, name: str) -> dict[str, str]:
        """Reference to element."""
        return {"x-ref": name}
    
    def init(self, expr: str) -> dict[str, str]:
        """Initialize component."""
        return {"x-init": expr}
    
    def cloak(self) -> dict[str, str]:
        """Hide until Alpine loads."""
        return {"x-cloak": ""}
    
    def ignore(self) -> dict[str, str]:
        """Ignore this element and children."""
        return {"x-ignore": ""}
    
    def ignore_self(self) -> dict[str, str]:
        """Ignore only this element, not children."""
        return {"x-ignore.self": ""}
    
    def key(self, expr: str) -> dict[str, str]:
        """Unique key for x-for items (for efficient DOM updates)."""
        return {"x-key": expr}
    
    def id(self, expr: str | list[str]) -> dict[str, str]:
        """Generate scoped IDs for accessibility."""
        value = expr if isinstance(expr, str) else _to_js(expr)
        return {"x-id": value}
    
    def modelable(self, expr: str) -> dict[str, str]:
        """Make component property bindable with x-model."""
        return {"x-modelable": expr}
    
    def effect(self, expr: str) -> dict[str, str]:
        """Side effect that re-runs when dependencies change."""
        return {"x-effect": expr}
    
    def teleport(self, target: str) -> dict[str, str]:
        """Teleport content to selector."""
        return {"x-teleport": target}
    
    # Plugin directives (require corresponding Alpine plugins)
    def intersect(self, expr: str) -> dict[str, str]:
        """Intersection observer (requires Alpine intersect plugin)."""
        return {"x-intersect": expr}
    
    def mask(self, expr: str) -> dict[str, str]:
        """Input masking (requires Alpine mask plugin)."""
        return {"x-mask": expr}
    
    def trap(self, expr: str) -> dict[str, str]:
        """Focus trapping (requires Alpine focus plugin)."""
        return {"x-trap": expr}
    
    def collapse(self) -> dict[str, str]:
        """Collapse animation (requires Alpine collapse plugin)."""
        return {"x-collapse": ""}
    
    # Sub-namespaces
    @property
    def bind(self) -> _BindNamespace:
        """Bind attributes namespace."""
        return _BindNamespace()
    
    @property
    def model(self) -> _ModelNamespace:
        """Two-way binding namespace."""
        return _ModelNamespace()
    
    @property
    def transition(self) -> _TransitionNamespace:
        """Transition namespace."""
        return _TransitionNamespace()
    
    # Fallback for custom directives
    def __getattr__(self, name: str) -> callable:
        directive = f"x-{clean_html_attr_key(name)}"
        def _setter(expr: str) -> dict[str, str]:
            return {directive: expr}
        return _setter


class AlpineBuilder:
    """ORM-like builder for Alpine.js attributes with excellent IDE support."""
    
    at = _EventNamespace()
    x = _DirectiveNamespace()
    
    @staticmethod
    def merge(*dicts: dict[str, str]) -> dict[str, str]:
        """Merge multiple attribute dicts."""
        result = {}
        for d in dicts:
            result |= d
        return result


# Export singleton instance as Alpine
Alpine = AlpineBuilder()
