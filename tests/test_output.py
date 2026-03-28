"""Tests for craft.output — formatting and display."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from craft.output import print_json, print_table, print_success, print_item, _label, _format_value, _flatten


class TestFormatValue:
    def test_none(self):
        result = _format_value(None)
        assert "-" in result

    def test_bool_true(self):
        result = _format_value(True)
        assert "Yes" in result

    def test_bool_false(self):
        result = _format_value(False)
        assert "No" in result

    def test_string(self):
        assert _format_value("hello") == "hello"

    def test_number(self):
        assert _format_value(42) == "42"

    def test_dict(self):
        result = _format_value({"key": "val"})
        assert "key" in result

    def test_list(self):
        result = _format_value(["a", "b"])
        assert "a, b" in result

    def test_empty_list(self):
        result = _format_value([])
        assert "-" in result


class TestLabel:
    def test_camel_case(self):
        assert _label("firstName") == "First Name"

    def test_snake_case(self):
        assert _label("first_name") == "First Name"

    def test_simple(self):
        assert _label("name") == "Name"

    def test_multi_caps(self):
        assert _label("ipAddress") == "Ip Address"


class TestFlatten:
    def test_simple(self):
        result = _flatten({"a": 1, "b": 2})
        assert result == {"a": 1, "b": 2}

    def test_nested(self):
        result = _flatten({"outer": "x", "inner": {"a": 1, "b": 2}})
        assert result["a"] == 1
        assert result["outer"] == "x"

    def test_conflict_top_level_wins(self):
        result = _flatten({"name": "top", "nested": {"name": "inner"}})
        assert result["name"] == "top"


class TestPrintItem:
    def test_simple_dict(self):
        # Just ensure no exceptions
        print_item({"data": {"id": "1", "name": "test"}})

    def test_nested_data(self):
        data = {"data": {"id": "1", "config": {"cpu": 2, "ram": 4096}}}
        # Just ensure no exceptions
        print_item(data)


class TestPrintTable:
    def test_with_tabulate(self):
        rows = [["1", "test", "active"]]
        headers = ["ID", "Name", "Status"]
        # Should not raise
        print_table(rows, headers)

    def test_empty_rows(self):
        print_table([], ["ID", "Name"])
