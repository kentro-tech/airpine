"""Tests for Alpine builder API."""

from airpine import Alpine, RawJS


class TestEventNamespace:
    """Test @event handlers."""
    
    def test_simple_click(self):
        attrs = Alpine.at.click("count++")
        assert attrs == {"@click": "count++"}
    
    def test_click_with_prevent(self):
        attrs = Alpine.at.click.prevent("save()")
        assert attrs == {"@click.prevent": "save()"}
    
    def test_click_with_multiple_modifiers(self):
        attrs = Alpine.at.click.prevent.once("save()")
        assert attrs == {"@click.prevent.once": "save()"}
    
    def test_submit_prevent(self):
        attrs = Alpine.at.submit.prevent("handleSubmit()")
        assert attrs == {"@submit.prevent": "handleSubmit()"}
    
    def test_keydown_modifiers(self):
        attrs = Alpine.at.keydown.ctrl.enter("submit()")
        assert attrs == {"@keydown.ctrl.enter": "submit()"}
    
    def test_keydown_escape(self):
        attrs = Alpine.at.keydown.escape("close()")
        assert attrs == {"@keydown.escape": "close()"}
    
    def test_click_window(self):
        attrs = Alpine.at.click.window("handleClick()")
        assert attrs == {"@click.window": "handleClick()"}
    
    def test_click_outside(self):
        attrs = Alpine.at.click.outside("close()")
        assert attrs == {"@click.outside": "close()"}
    
    def test_click_away(self):
        attrs = Alpine.at.click.away("close()")
        assert attrs == {"@click.away": "close()"}
    
    def test_click_stop(self):
        attrs = Alpine.at.click.stop("stopPropagation()")
        assert attrs == {"@click.stop": "stopPropagation()"}
    
    def test_click_self(self):
        attrs = Alpine.at.click.self("handleSelf()")
        assert attrs == {"@click.self": "handleSelf()"}
    
    def test_debounce(self):
        attrs = Alpine.at.input.debounce(300)("search()")
        assert attrs == {"@input.debounce.300ms": "search()"}
    
    def test_throttle(self):
        attrs = Alpine.at.scroll.throttle(100)("onScroll()")
        assert attrs == {"@scroll.throttle.100ms": "onScroll()"}
    
    def test_custom_event(self):
        """Custom events via attribute access."""
        attrs = Alpine.at.custom_event("handler()")
        assert attrs == {"@custom-event": "handler()"}


class TestDirectiveNamespace:
    """Test x-* directives."""
    
    def test_x_data_string(self):
        attrs = Alpine.x.data("{ count: 0 }")
        assert attrs == {"x-data": "{ count: 0 }"}
    
    def test_x_data_dict(self):
        attrs = Alpine.x.data({"count": 0})
        assert "x-data" in attrs
        assert '"count": 0' in attrs["x-data"]
    
    def test_x_data_complex_dict(self):
        attrs = Alpine.x.data({"count": 0, "name": "test", "active": True})
        result = attrs["x-data"]
        assert '"count": 0' in result
        assert '"name": "test"' in result
        assert '"active": true' in result
    
    def test_x_show(self):
        attrs = Alpine.x.show("isVisible")
        assert attrs == {"x-show": "isVisible"}
    
    def test_x_if(self):
        attrs = Alpine.x.if_("condition")
        assert attrs == {"x-if": "condition"}
    
    def test_x_for(self):
        attrs = Alpine.x.for_("item in items")
        assert attrs == {"x-for": "item in items"}
    
    def test_x_text(self):
        attrs = Alpine.x.text("message")
        assert attrs == {"x-text": "message"}
    
    def test_x_html(self):
        attrs = Alpine.x.html("htmlContent")
        assert attrs == {"x-html": "htmlContent"}
    
    def test_x_ref(self):
        attrs = Alpine.x.ref("myInput")
        assert attrs == {"x-ref": "myInput"}
    
    def test_x_init(self):
        attrs = Alpine.x.init("console.log('initialized')")
        assert attrs == {"x-init": "console.log('initialized')"}
    
    def test_x_cloak(self):
        attrs = Alpine.x.cloak()
        assert attrs == {"x-cloak": ""}
    
    def test_x_ignore(self):
        attrs = Alpine.x.ignore()
        assert attrs == {"x-ignore": ""}
    
    def test_x_transition(self):
        attrs = Alpine.x.transition()
        assert attrs == {"x-transition": ""}
    
    def test_x_transition_with_value(self):
        attrs = Alpine.x.transition("opacity")
        assert attrs == {"x-transition": "opacity"}
    
    def test_x_effect(self):
        attrs = Alpine.x.effect("console.log(count)")
        assert attrs == {"x-effect": "console.log(count)"}
    
    def test_x_teleport(self):
        attrs = Alpine.x.teleport("body")
        assert attrs == {"x-teleport": "body"}


class TestBindNamespace:
    """Test x-bind:* attributes."""
    
    def test_bind_class(self):
        attrs = Alpine.x.bind.class_("{ 'active': isActive }")
        assert attrs == {"x-bind:class": "{ 'active': isActive }"}
    
    def test_bind_style(self):
        attrs = Alpine.x.bind.style("{ color: textColor }")
        assert attrs == {"x-bind:style": "{ color: textColor }"}
    
    def test_bind_href(self):
        attrs = Alpine.x.bind.href("linkUrl")
        assert attrs == {"x-bind:href": "linkUrl"}
    
    def test_bind_src(self):
        attrs = Alpine.x.bind.src("imageUrl")
        assert attrs == {"x-bind:src": "imageUrl"}
    
    def test_bind_value(self):
        attrs = Alpine.x.bind.value("inputValue")
        assert attrs == {"x-bind:value": "inputValue"}
    
    def test_bind_disabled(self):
        attrs = Alpine.x.bind.disabled("isDisabled")
        assert attrs == {"x-bind:disabled": "isDisabled"}
    
    def test_bind_checked(self):
        attrs = Alpine.x.bind.checked("isChecked")
        assert attrs == {"x-bind:checked": "isChecked"}
    
    def test_bind_custom_attribute(self):
        """Custom attributes via __getattr__."""
        attrs = Alpine.x.bind.data_value("someValue")
        assert attrs == {"x-bind:data-value": "someValue"}


class TestModelNamespace:
    """Test x-model and modifiers."""
    
    def test_x_model_plain(self):
        attrs = Alpine.x.model("email")
        assert attrs == {"x-model": "email"}
    
    def test_x_model_number(self):
        attrs = Alpine.x.model.number("age")
        assert attrs == {"x-model.number": "age"}
    
    def test_x_model_lazy(self):
        attrs = Alpine.x.model.lazy("message")
        assert attrs == {"x-model.lazy": "message"}
    
    def test_x_model_trim(self):
        attrs = Alpine.x.model.trim("input")
        assert attrs == {"x-model.trim": "input"}
    
    def test_x_model_debounce(self):
        attrs = Alpine.x.model.debounce(500)("search")
        assert attrs == {"x-model.debounce.500ms": "search"}
    
    def test_x_model_throttle(self):
        attrs = Alpine.x.model.throttle(100)("input")
        assert attrs == {"x-model.throttle.100ms": "input"}


class TestDictMerging:
    """Test merging attribute dicts with | operator."""
    
    def test_merge_two_dicts(self):
        result = Alpine.x.data({"count": 0}) | Alpine.at.click("increment()")
        assert "x-data" in result
        assert "@click" in result
        assert '"count": 0' in result["x-data"]
        assert result["@click"] == "increment()"
    
    def test_merge_multiple(self):
        result = (
            Alpine.x.data({"open": False}) |
            Alpine.at.click("toggle()") |
            Alpine.at.keydown.escape("close()")
        )
        assert "x-data" in result
        assert "@click" in result
        assert "@keydown.escape" in result
    
    def test_merge_last_wins(self):
        """When merging duplicate keys, last value wins."""
        result = Alpine.at.click("first()") | Alpine.at.click("second()")
        assert result == {"@click": "second()"}


class TestCleanHtmlAttrKey:
    """Test clean_html_attr_key utility from Air."""
    
    def test_trailing_underscore_removal(self):
        """Trailing underscores should be handled via special cases."""
        from air.tags.utils import clean_html_attr_key
        
        assert clean_html_attr_key("class_") == "class"
        assert clean_html_attr_key("for_") == "for"
        assert clean_html_attr_key("id_") == "id"
        assert clean_html_attr_key("as_") == "as"
        assert clean_html_attr_key("async_") == "async"
    
    def test_internal_underscores(self):
        """Internal underscores should become hyphens."""
        from air.tags.utils import clean_html_attr_key
        
        assert clean_html_attr_key("data_value") == "data-value"
        assert clean_html_attr_key("hx_post") == "hx-post"
    
    def test_leading_underscores(self):
        """Leading underscores should be removed."""
        from air.tags.utils import clean_html_attr_key
        
        assert clean_html_attr_key("_private") == "private"
        assert clean_html_attr_key("__dunder") == "dunder"


class TestAnyValueSupport:
    """Test that __call__ accepts Any type."""
    
    def test_string_value(self):
        attrs = Alpine.x.text("message")
        assert attrs == {"x-text": "message"}
    
    def test_number_value(self):
        """Numbers can be passed directly (Air handles conversion)."""
        attrs = Alpine.x.text(42)
        assert attrs == {"x-text": 42}
    
    def test_boolean_value(self):
        """Booleans can be passed directly (Air handles conversion)."""
        attrs = Alpine.x.show(True)
        assert attrs == {"x-show": True}
    
    def test_expression_value(self):
        """Complex expressions as strings still work."""
        attrs = Alpine.at.click("count++")
        assert attrs == {"@click": "count++"}


class TestRawJSIntegration:
    """Test RawJS with x-data."""
    
    def test_rawjs_function(self):
        attrs = Alpine.x.data({
            "count": 0,
            "increment": RawJS("function() { this.count++; }")
        })
        result = attrs["x-data"]
        assert '"count": 0' in result
        assert 'function() { this.count++; }' in result
        # RawJS should not be quoted
        assert '"function()' not in result
    
    def test_rawjs_arrow_function(self):
        attrs = Alpine.x.data({
            "onClick": RawJS("() => alert('hi')")
        })
        result = attrs["x-data"]
        assert '() => alert(\'hi\')' in result


class TestRealWorldScenarios:
    """Test realistic use cases."""
    
    def test_counter_component(self):
        """Simple counter."""
        attrs = Alpine.x.data({"count": 0})
        increment_attrs = Alpine.at.click("count++")
        
        assert '"count": 0' in attrs["x-data"]
        assert increment_attrs == {"@click": "count++"}
    
    def test_modal_component(self):
        """Modal with ESC key."""
        attrs = (
            Alpine.x.data({"open": False}) |
            Alpine.at.keydown.escape.window("open = false") |
            Alpine.at.click.outside("open = false")
        )
        
        assert '"open": false' in attrs["x-data"]
        assert attrs["@keydown.escape.window"] == "open = false"
        assert attrs["@click.outside"] == "open = false"
    
    def test_form_with_validation(self):
        """Form with debounced validation."""
        data_attrs = Alpine.x.data({"email": "", "valid": False})
        input_attrs = (
            Alpine.x.model("email") |
            Alpine.at.input.debounce(300)("validateEmail()")
        )
        
        assert '"email": ""' in data_attrs["x-data"]
        assert '"valid": false' in data_attrs["x-data"]
        assert input_attrs["x-model"] == "email"
        assert input_attrs["@input.debounce.300ms"] == "validateEmail()"
    
    def test_dropdown_menu(self):
        """Dropdown with click away."""
        attrs = Alpine.x.data({"open": False}) | Alpine.at.click.away("open = false")
        button_attrs = Alpine.at.click("open = !open")
        content_attrs = Alpine.x.show("open")
        
        assert '"open": false' in attrs["x-data"]
        assert attrs["@click.away"] == "open = false"
        assert button_attrs == {"@click": "open = !open"}
        assert content_attrs == {"x-show": "open"}
    
    def test_search_with_debounce(self):
        """Search with debounced input."""
        data_attrs = Alpine.x.data({
            "search": "",
            "results": []
        })
        input_attrs = (
            Alpine.x.model("search") |
            Alpine.at.input.debounce(300)("performSearch()")
        )
        
        assert '"search": ""' in data_attrs["x-data"]
        assert '"results": []' in data_attrs["x-data"]
        assert input_attrs["x-model"] == "search"
        assert input_attrs["@input.debounce.300ms"] == "performSearch()"
