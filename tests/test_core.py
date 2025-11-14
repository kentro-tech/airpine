"""Core functionality tests for Airpine with Alpine.js-compatible output."""

from airpine import Alpine, RawJS
from airpine.airpine_builder import _to_js, _dict_to_alpine_obj


def test_serializer_alpine_format():
    """Verify serializer produces Alpine.js-compatible JavaScript."""
    # Strings use single quotes
    assert _to_js("hello") == "'hello'"
    assert _to_js("it's") == "'it\\'s'"
    
    # Numbers and booleans
    assert _to_js(42) == "42"
    assert _to_js(True) == "true"
    assert _to_js(False) == "false"
    assert _to_js(None) == "null"
    
    # Dicts use unquoted keys
    result = _to_js({"count": 0})
    assert result == "{ count: 0 }"
    
    result = _to_js({"count": 0, "name": "test"})
    assert "count: 0" in result
    assert "name: 'test'" in result
    
    # Lists
    assert _to_js([1, 2, 3]) == "[1, 2, 3]"
    assert _to_js(["a", "b"]) == "['a', 'b']"
    
    # RawJS
    assert _to_js(RawJS("() => 42")) == "() => 42"


def test_alpine_x_data():
    """Test x-data generation."""
    attrs = Alpine.x.data({"count": 0})
    assert "x-data" in attrs
    assert attrs["x-data"] == "{ count: 0 }"
    
    attrs = Alpine.x.data({"count": 0, "name": "test"})
    result = attrs["x-data"]
    assert "count: 0" in result
    assert "name: 'test'" in result


def test_alpine_events():
    """Test event handlers."""
    assert Alpine.at.click("count++") == {"@click": "count++"}
    assert Alpine.at.click.prevent("save()") == {"@click.prevent": "save()"}
    assert Alpine.at.keydown.enter("submit()") == {"@keydown.enter": "submit()"}


def test_real_world_counter():
    """Test realistic counter component."""
    data_attrs = Alpine.x.data({"count": 0})
    click_attrs = Alpine.at.click("count++")
    text_attrs = Alpine.x.text("count")
    
    assert data_attrs["x-data"] == "{ count: 0 }"
    assert click_attrs["@click"] == "count++"
    assert text_attrs["x-text"] == "count"


def test_rawjs_in_data():
    """Test RawJS functions in x-data."""
    attrs = Alpine.x.data({
        "count": 0,
        "increment": RawJS("function() { this.count++; }")
    })
    result = attrs["x-data"]
    assert "count: 0" in result
    assert "function() { this.count++; }" in result
    # RawJS should not be quoted
    assert "'function()" not in result


def test_escaping_apostrophes():
    """Test that apostrophes in strings are escaped."""
    result = _to_js("it's working")
    assert result == "'it\\'s working'"
    
    result = _to_js({"msg": "it's fine"})
    assert "msg: 'it\\'s fine'" in result


if __name__ == "__main__":
    # Run quick smoke test
    test_serializer_alpine_format()
    test_alpine_x_data()
    test_alpine_events()
    test_real_world_counter()
    test_rawjs_in_data()
    test_escaping_apostrophes()
    print("✓ All core tests passed!")
