"""Tests for JavaScript serializer (_to_js)."""

# Import private functions for testing
import sys

from airpine import RawJS

sys.path.insert(0, 'airpine')
from airpine.airpine_builder import _to_js


class TestSerializerStrings:
    """Test string serialization with special characters."""
    
    def test_simple_string(self):
        """Simple strings should be quoted."""
        assert _to_js("hello") == "'hello'"
    
    def test_string_with_double_quotes(self):
        """Strings with double quotes should be escaped."""
        result = _to_js('He said "hello"')
        assert result == r'"He said 'hello'"'
    
    def test_string_with_single_quotes(self):
        """Strings with apostrophes should work."""
        result = _to_js("it's working")
        assert result == '"it\'s working"'
    
    def test_string_with_both_quotes(self):
        """Strings with both quote types should work."""
        result = _to_js("""He said "it's fine" """)
        # json.dumps escapes double quotes but not single quotes
        assert "it's" in result
        assert '\'' in result
    
    def test_string_with_html_entities(self):
        """HTML entities should be preserved (Air handles escaping)."""
        result = _to_js("<script>alert('xss')</script>")
        assert '<script>' in result
        assert "'xss'" in result
    
    def test_string_with_ampersand(self):
        """Ampersands should be preserved."""
        result = _to_js("Tom & Jerry")
        assert '"Tom & Jerry"' == result
    
    def test_string_with_backslash(self):
        """Backslashes should be escaped."""
        result = _to_js(r"C:\Users\test")
        assert r"C:\\Users\\test" in result
    
    def test_string_with_emoji(self):
        """Unicode emojis should work."""
        result = _to_js("Hello 👋 World")
        # json.dumps escapes unicode by default, which is fine for JS
        assert "Hello" in result
        assert "World" in result
    
    def test_empty_string(self):
        """Empty strings should be valid."""
        assert _to_js("") == '""'


class TestSerializerNumbers:
    """Test number serialization."""
    
    def test_integer(self):
        assert _to_js(42) == "42"
    
    def test_zero(self):
        assert _to_js(0) == "0"
    
    def test_negative_integer(self):
        assert _to_js(-10) == "-10"
    
    def test_float(self):
        assert _to_js(3.14) == "3.14"
    
    def test_negative_float(self):
        assert _to_js(-2.5) == "-2.5"


class TestSerializerBooleans:
    """Test boolean serialization."""
    
    def test_true(self):
        assert _to_js(True) == "true"
    
    def test_false(self):
        assert _to_js(False) == "false"


class TestSerializerNone:
    """Test None/null serialization."""
    
    def test_none(self):
        assert _to_js(None) == "null"


class TestSerializerLists:
    """Test list and tuple serialization."""
    
    def test_simple_list(self):
        result = _to_js([1, 2, 3])
        assert result == "[1, 2, 3]"
    
    def test_list_with_strings(self):
        result = _to_js(["a", "b", "c"])
        assert result == '["a", "b", "c"]'
    
    def test_list_with_apostrophes(self):
        """Lists with strings containing apostrophes should work."""
        result = _to_js(["it's", "test's"])
        # json.dumps doesn't escape single quotes
        assert "it's" in result
        assert "test's" in result
    
    def test_list_with_mixed_types(self):
        result = _to_js([1, "two", True, None])
        assert result == '[1, "two", true, null]'
    
    def test_nested_lists(self):
        result = _to_js([[1, 2], [3, 4]])
        assert result == "[[1, 2], [3, 4]]"
    
    def test_tuple(self):
        """Tuples should serialize like lists."""
        result = _to_js((1, 2, 3))
        assert result == "[1, 2, 3]"
    
    def test_empty_list(self):
        assert _to_js([]) == "[]"


class TestSerializerDicts:
    """Test dictionary serialization."""
    
    def test_simple_dict(self):
        result = _to_js({"count": 0})
        assert '"count": 0' in result
    
    def test_dict_with_string_values(self):
        result = _to_js({"name": "Alice"})
        assert '"name": "Alice"' in result
    
    def test_dict_with_multiple_keys(self):
        result = _to_js({"count": 0, "name": "test", "active": True})
        assert '"count": 0' in result
        assert '"name": "test"' in result
        assert '"active": true' in result
    
    def test_nested_dict(self):
        result = _to_js({"user": {"name": "Alice", "age": 30}})
        assert '"user": {' in result
        assert '"name": "Alice"' in result
        assert '"age": 30' in result
    
    def test_dict_with_list_values(self):
        result = _to_js({"items": [1, 2, 3]})
        assert '"items": [1, 2, 3]' in result
    
    def test_dict_with_hyphenated_keys(self):
        """Keys with hyphens should be quoted."""
        result = _to_js({"data-value": "test"})
        assert '"data-value": "test"' in result
    
    def test_dict_with_reserved_word_keys(self):
        """Reserved words as keys should be quoted."""
        result = _to_js({"class": "active", "for": "input1"})
        assert '"class": "active"' in result
        assert '"for": "input1"' in result
    
    def test_empty_dict(self):
        result = _to_js({})
        # Empty dict has two spaces between braces
        assert result == "{  }"


class TestSerializerRawJS:
    """Test RawJS handling."""
    
    def test_rawjs_simple(self):
        result = _to_js(RawJS("function() { return 42; }"))
        assert result == "function() { return 42; }"
    
    def test_rawjs_with_newlines(self):
        """RawJS should strip newlines for valid HTML attributes."""
        result = _to_js(RawJS("function() {\n  return 42;\n}"))
        assert "\n" not in result
        assert result == "function() {   return 42; }"
    
    def test_rawjs_in_dict(self):
        """RawJS values in dicts should not be quoted."""
        result = _to_js({"onClick": RawJS("() => alert('hi')")})
        assert '"onClick": () => alert(\'hi\')' in result
    
    def test_rawjs_in_nested_dict(self):
        """RawJS should work at any depth."""
        result = _to_js({"data": {"fn": RawJS("function() { return 42; }")}})
        assert '"fn": function() { return 42; }' in result
    
    def test_rawjs_in_list(self):
        """RawJS should work in lists."""
        result = _to_js([RawJS("1 + 1"), RawJS("2 + 2")])
        assert result == "[1 + 1, 2 + 2]"


class TestSerializerComplex:
    """Test complex nested structures."""
    
    def test_deeply_nested(self):
        """Deeply nested structures should work."""
        data = {
            "user": {
                "name": "Alice",
                "tags": ["admin", "user"],
                "settings": {
                    "theme": "dark",
                    "notifications": True
                }
            }
        }
        result = _to_js(data)
        assert '"name": "Alice"' in result
        assert '["admin", "user"]' in result
        assert '"theme": "dark"' in result
        assert '"notifications": true' in result
    
    def test_mixed_types_deeply_nested(self):
        """Complex structures with all types."""
        data = {
            "count": 0,
            "items": [
                {"id": 1, "name": "First"},
                {"id": 2, "name": "Second"}
            ],
            "active": True,
            "empty": None,
            "handler": RawJS("function() { console.log('test'); }")
        }
        result = _to_js(data)
        assert '"count": 0' in result
        assert '"id": 1' in result
        assert '"active": true' in result
        assert '"empty": null' in result
        assert 'function() { console.log(\'test\'); }' in result


class TestToJsWithDicts:
    """Test _to_js with dict values (used by x-data)."""
    
    def test_dict(self):
        """Should convert dicts to JS objects."""
        result = _to_js({"count": 0, "name": "test"})
        assert "count: 0" in result
        assert "name: 'test'" in result
    
    def test_non_dict(self):
        """Non-dicts should be converted properly."""
        assert _to_js("plain string") == "'plain string'"
        assert _to_js(42) == "42"
    
    def test_empty_dict(self):
        result = _to_js({})
        assert result == "{  }"
    
    def test_with_rawjs(self):
        """RawJS functions should work in x-data."""
        result = _to_js({
            "count": 0,
            "increment": RawJS("function() { this.count++; }")
        })
        assert "count: 0" in result
        assert 'function() { this.count++; }' in result


class TestSerializerEdgeCases:
    """Test edge cases and corner cases."""
    
    def test_string_with_newline(self):
        """Strings with literal newlines (not in RawJS) should be escaped."""
        result = _to_js("line1\nline2")
        # json.dumps escapes newlines as \n
        assert r"\n" in result
    
    def test_list_of_dicts_with_quotes(self):
        """Complex real-world scenario."""
        data = [
            {"name": "Item's name", "value": 'A "quoted" value'},
            {"name": "Other", "value": "simple"}
        ]
        result = _to_js(data)
        # Should not break on apostrophes or quotes
        assert "Item's name" in result
        assert '\'quoted\'' in result
    
    def test_dict_with_all_types(self):
        """Dict with every type."""
        data = {
            "str": "value",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "none": None,
            "list": [1, 2],
            "dict": {"nested": "value"},
            "rawjs": RawJS("() => 42")
        }
        result = _to_js(data)
        assert '"str": "value"' in result
        assert '"int": 42' in result
        assert '"float": 3.14' in result
        assert '"bool": true' in result
        assert '"none": null' in result
        assert '"list": [1, 2]' in result
        assert '"nested": "value"' in result
        assert '() => 42' in result
