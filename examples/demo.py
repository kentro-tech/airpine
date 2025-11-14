"""Airpine Demo - Alpine.js integration examples

Demonstrates Airpine capabilities using MVP.css for clean, semantic HTML.

Run with:
    python demo.py
    # Then visit http://localhost:8001
"""

import sys
from pathlib import Path

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

from airpine import Alpine, RawJS

import air
from air import Div, Button, Input, Textarea, Form, A, Span, H2, H3, P, Label, Script

# Create Air app
app = air.Air()


def simple_counter():
    """Simple counter - demonstrates basic x-data and @click."""
    return Div(
        H3("Counter", class_="text-xl font-semibold mb-3"),
        Div(
            Button("-", **Alpine.at.click("count--"), class_="px-4 py-2 bg-blue-500 text-white rounded"),
            Span(**Alpine.x.text("count"), class_="mx-4 text-2xl font-bold"),
            Button("+", **Alpine.at.click("count++"), class_="px-4 py-2 bg-blue-500 text-white rounded")
        ),
        **Alpine.x.data({"count": 0}),
        class_="p-6 border rounded-lg bg-white shadow-sm"
    )


def simple_toggle():
    """Toggle visibility."""
    return Div(
        H3("Toggle", class_="text-xl font-semibold mb-3"),
        Button("Toggle Content", **Alpine.at.click("visible = !visible"), class_="px-4 py-2 bg-blue-500 text-white rounded mb-2"),
        P("This content can be toggled!", **Alpine.x.show("visible"), class_="mt-2 p-3 bg-blue-50 rounded"),
        **Alpine.x.data({"visible": True}),
        class_="p-6 border rounded-lg bg-white shadow-sm"
    )


def simple_input():
    """Two-way data binding."""
    return Div(
        H3("Input Binding", class_="text-xl font-semibold mb-3"),
        Input(type="text", placeholder="Type something...", **Alpine.x.model("message"), class_="w-full border p-2 rounded mb-2"),
        P(**Alpine.x.text("message || 'Nothing typed yet...'"), class_="text-gray-600"),
        **Alpine.x.data({"message": ""}),
        class_="p-6 border rounded-lg bg-white shadow-sm"
    )


def tabs_component():
    """Tabs with dynamic styling."""
    return Div(
        H3("Tabs", class_="text-xl font-semibold mb-3"),
        Div(
            Button("Profile", **(
                Alpine.at.click("tab = 0") |
                Alpine.x.bind.class_("{ 'bg-blue-500 text-white': tab === 0, 'bg-gray-200': tab !== 0 }")
            ), class_="px-4 py-2 rounded-t"),
            Button("Settings", **(
                Alpine.at.click("tab = 1") |
                Alpine.x.bind.class_("{ 'bg-blue-500 text-white': tab === 1, 'bg-gray-200': tab !== 1 }")
            ), class_="px-4 py-2 rounded-t"),
            class_="flex gap-1"
        ),
        Div(
            P("Profile content", **Alpine.x.show("tab === 0"), class_="p-4"),
            P("Settings content", **Alpine.x.show("tab === 1"), class_="p-4"),
            class_="border border-t-0 rounded-b"
        ),
        **Alpine.x.data({"tab": 0}),
        class_="p-6 border rounded-lg bg-white shadow-sm"
    )


def dropdown_menu():
    """Dropdown with click-away."""
    return Div(
        H3("Dropdown", class_="text-xl font-semibold mb-3"),
        Div(
            Button("Menu", **Alpine.at.click("open = !open"), class_="px-4 py-2 bg-blue-500 text-white rounded"),
            Div(
                A("Profile", href="#", class_="block px-4 py-2 hover:bg-gray-100"),
                A("Settings", href="#", class_="block px-4 py-2 hover:bg-gray-100"),
                A("Logout", href="#", class_="block px-4 py-2 hover:bg-gray-100"),
                **Alpine.x.show("open"),
                class_="absolute mt-1 bg-white border rounded shadow-lg min-w-[150px]"
            ),
            **(Alpine.x.data({"open": False}) | Alpine.at.click.away("open = false")),
            class_="relative inline-block"
        ),
        class_="p-6 border rounded-lg bg-white shadow-sm"
    )

def form_validation():
    """Form with validation."""
    return Div(
        H3("Form Validation", class_="text-xl font-semibold mb-3"),
        Form(
            Label("Email:", class_="block mb-1 font-medium"),
            Input(
                type="email",
                placeholder="you@example.com",
                **(
                    Alpine.x.model("email") |
                    Alpine.at.input("emailError = email.includes('@') ? '' : 'Invalid email'")
                ),
                class_="w-full border p-2 rounded mb-1"
            ),
            Span(**Alpine.x.text("emailError"), **Alpine.x.show("emailError"), class_="text-red-500 text-sm block mb-2"),
            Button(
                "Submit",
                type="submit",
                **(
                    Alpine.at.submit.prevent("alert('Submitted!')") |
                    Alpine.x.bind.disabled("emailError !== '' || email === ''")
                ),
                class_="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
            )
        ),
        **Alpine.x.data({"email": "", "emailError": ""}),
        class_="p-6 border rounded-lg bg-white shadow-sm"
    )


def search_filter():
    """Search with debounce."""
    items = ["Apple", "Banana", "Cherry", "Date", "Elderberry", "Fig", "Grape"]
    
    return Div(
        H3("Search & Filter", class_="text-xl font-semibold mb-3"),
        P(air.Small("Debounced input (300ms)"), class_="text-gray-600 text-sm mb-2"),
        Input(
            type="text",
            placeholder="Search fruits...",
            **(
                Alpine.x.model("search") |
                Alpine.at.input.debounce(300)("updateResults()")
            ),
            class_="w-full border p-2 rounded mb-2"
        ),
        Div(
            P(**Alpine.x.text("'Found: ' + filteredItems.length + ' items'"), class_="text-sm text-gray-600 mb-2"),
            Div(**Alpine.x.html(
                "filteredItems.map(item => `<div class='p-2 border-b'>${item}</div>`).join('')"
            ), class_="border rounded"),
            **Alpine.x.show("search !== ''")
        ),
        **Alpine.x.data({
            "search": "",
            "items": items,
            "filteredItems": items,
            "updateResults": RawJS("function() { this.filteredItems = this.items.filter(item => item.toLowerCase().includes(this.search.toLowerCase())); }")
        }),
        class_="p-6 border rounded-lg bg-white shadow-sm"
    )


def modal_dialog():
    """Modal with ESC key handling."""
    return Div(
        H3("Modal", class_="text-xl font-semibold mb-3"),
        Button("Open Modal", **Alpine.at.click("isOpen = true"), class_="px-4 py-2 bg-blue-500 text-white rounded"),
        Div(
            Div(**Alpine.at.click("isOpen = false"), class_="fixed inset-0 bg-black bg-opacity-50"),
            Div(
                H3("Modal Title", class_="text-xl font-bold mb-2"),
                P("Press ESC to close", class_="mb-4"),
                Button("Close", **Alpine.at.click("isOpen = false"), class_="px-4 py-2 bg-gray-500 text-white rounded"),
                **Alpine.at.click.stop(""),
                class_="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white p-6 rounded-lg shadow-xl max-w-md z-10"
            ),
            **Alpine.x.show("isOpen"),
            class_="fixed inset-0 z-50",
        ),
        **(Alpine.x.data({"isOpen": False}) | Alpine.at.keydown.escape.window("isOpen = false")),
        class_="p-6 border rounded-lg bg-white shadow-sm"
    )


@app.page
def index():
    """Airpine examples with Tailwind CSS."""
    return air.Html(
        air.Head(
            air.Meta(charset="UTF-8"),
            air.Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            air.Title("Airpine Examples"),
            Script(src="https://cdn.tailwindcss.com"),
            Script(
                src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js",
                defer=True
            )
        ),
        air.Body(
            Div(
                air.Header(
                    H2("Airpine Examples", class_="text-3xl font-bold mb-2"),
                    P("Alpine.js integration for Air framework", class_="text-gray-600 mb-2"),
                    P(
                        air.Code("Alpine.at.click.prevent()"), " • ",
                        air.Code("Alpine.x.bind.class_()"), " • ",
                        air.Code("Alpine.at.keydown.ctrl.enter()"),
                        class_="text-sm"
                    ),
                    class_="mb-8 pb-6 border-b"
                ),
                
                H2("Simple Examples", class_="text-2xl font-bold mb-4"),
                Div(
                    simple_counter(),
                    simple_toggle(),
                    simple_input(),
                    class_="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mb-8"
                ),
                
                H2("Interactive Components", class_="text-2xl font-bold mb-4"),
                Div(
                    tabs_component(),
                    dropdown_menu(),
                    form_validation(),
                    class_="grid gap-4 md:grid-cols-2 mb-8"
                ),
                
                H2("Advanced Features", class_="text-2xl font-bold mb-4"),
                Div(
                    search_filter(),
                    modal_dialog(),
                    class_="grid gap-4 md:grid-cols-2 mb-8"
                ),
                
                air.Footer(
                    P(
                        "Built with ",
                        A("Air", href="https://github.com/feldroy/air", class_="text-blue-500 hover:underline"),
                        " and ",
                        A("Alpine.js", href="https://alpinejs.dev", class_="text-blue-500 hover:underline"),
                        class_="text-center text-gray-600"
                    ),
                    class_="mt-12 pt-6 border-t"
                ),
                
                class_="container mx-auto px-8 py-8 max-w-6xl"
            ),
            class_="bg-gray-50 min-h-screen"
        )
    )


if __name__ == "__main__":
    import uvicorn
    
    print("🏔️  Airpine Demo")
    print("Visit: http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
