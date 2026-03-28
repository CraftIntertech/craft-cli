"""Shared fixtures for craft-cli tests."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_config():
    """Mock config with valid token."""
    with patch("craft.config.load_config", return_value={
        "base_url": "https://craftintertech.co.th/api/v1",
        "access_token": "test-token-12345",
        "refresh_token": "test-refresh-token",
    }), patch("craft.config.get_token", return_value="test-token-12345"), \
         patch("craft.config.get_base_url", return_value="https://craftintertech.co.th/api/v1"):
        yield


@pytest.fixture
def mock_api(mock_config):
    """Mock HTTP requests for API calls."""
    with patch("craft.client.requests.request") as mock_req:
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"data": {}}
        mock_req.return_value = resp
        yield mock_req


def make_response(data, status_code=200):
    """Helper to create a mock API response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = data
    return resp
