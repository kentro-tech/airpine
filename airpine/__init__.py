"""Airpine - Alpine.js integration for Air framework

Airpine provides a Pythonic API for working with Alpine.js directives in the Air framework.
Features excellent IDE autocomplete and natural chained syntax.

Example:
    from airpine import Alpine
    
    # Clean event handling with modifiers
    Button("Save", **Alpine.at.click.prevent.once("save()"))
    
    # Keyboard shortcuts
    Input(**Alpine.at.keydown.ctrl.enter("submit()"))
    
    # Debounced input
    Input(**Alpine.at.input.debounce(300)("search()"))
    
    # Component state
    Div(**Alpine.x.data({"count": 0}))
"""

from .airpine_builder import Alpine, RawJS

__version__ = "0.2.0"
__all__ = ["Alpine", "RawJS"]
