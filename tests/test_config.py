"""Tests for craft.config — configuration management."""

import json
import pytest
from unittest.mock import patch, mock_open
from pathlib import Path

from craft.config import (
    load_config, save_config, get_token, save_tokens,
    clear_tokens, get_base_url, DEFAULT_CONFIG,
)


class TestLoadConfig:
    def test_default_config_when_no_file(self, tmp_path):
        with patch("craft.config.CONFIG_FILE", tmp_path / "nonexistent.json"), \
             patch("craft.config.CONFIG_DIR", tmp_path):
            cfg = load_config()
            assert cfg["base_url"] == DEFAULT_CONFIG["base_url"]
            assert cfg["access_token"] == ""

    def test_loads_existing_config(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"access_token": "my-token"}))
        with patch("craft.config.CONFIG_FILE", config_file), \
             patch("craft.config.CONFIG_DIR", tmp_path):
            cfg = load_config()
            assert cfg["access_token"] == "my-token"
            assert cfg["base_url"] == DEFAULT_CONFIG["base_url"]


class TestSaveConfig:
    def test_saves_config(self, tmp_path):
        config_file = tmp_path / "config.json"
        with patch("craft.config.CONFIG_FILE", config_file), \
             patch("craft.config.CONFIG_DIR", tmp_path):
            save_config({"access_token": "test", "base_url": "http://test.com"})
            data = json.loads(config_file.read_text())
            assert data["access_token"] == "test"


class TestTokens:
    def test_get_token(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"access_token": "my-token"}))
        with patch("craft.config.CONFIG_FILE", config_file), \
             patch("craft.config.CONFIG_DIR", tmp_path):
            assert get_token() == "my-token"

    def test_save_tokens(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(DEFAULT_CONFIG))
        with patch("craft.config.CONFIG_FILE", config_file), \
             patch("craft.config.CONFIG_DIR", tmp_path):
            save_tokens("new-access", "new-refresh")
            data = json.loads(config_file.read_text())
            assert data["access_token"] == "new-access"
            assert data["refresh_token"] == "new-refresh"

    def test_clear_tokens(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"access_token": "x", "refresh_token": "y"}))
        with patch("craft.config.CONFIG_FILE", config_file), \
             patch("craft.config.CONFIG_DIR", tmp_path):
            clear_tokens()
            data = json.loads(config_file.read_text())
            assert data["access_token"] == ""
            assert data["refresh_token"] == ""

    def test_get_base_url_default(self, tmp_path):
        config_file = tmp_path / "config.json"
        with patch("craft.config.CONFIG_FILE", config_file), \
             patch("craft.config.CONFIG_DIR", tmp_path):
            assert get_base_url() == DEFAULT_CONFIG["base_url"]
