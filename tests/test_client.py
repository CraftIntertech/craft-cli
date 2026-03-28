"""Tests for craft.client — HTTP client layer."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from craft.client import api_request, get, post, put, patch as client_patch, delete


@pytest.fixture
def mock_config():
    with patch("craft.client.get_token", return_value="test-token"), \
         patch("craft.client.get_base_url", return_value="https://api.test.com"):
        yield


class TestApiRequest:
    def test_get_request(self, mock_config):
        with patch("craft.client.requests.request") as mock_req:
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {"data": {"id": 1}}
            mock_req.return_value = resp

            result = api_request("GET", "/vms")
            assert result == {"data": {"id": 1}}
            mock_req.assert_called_once()
            args, kwargs = mock_req.call_args
            assert args[0] == "GET"
            assert "https://api.test.com/vms" in args[1]
            assert kwargs["headers"]["Authorization"] == "Bearer test-token"

    def test_post_request_with_json(self, mock_config):
        with patch("craft.client.requests.request") as mock_req:
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {"success": True}
            mock_req.return_value = resp

            result = api_request("POST", "/vms", json_data={"name": "test"})
            _, kwargs = mock_req.call_args
            assert kwargs["json"] == {"name": "test"}

    def test_no_auth_when_not_required(self):
        with patch("craft.client.get_base_url", return_value="https://api.test.com"), \
             patch("craft.client.requests.request") as mock_req:
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {}
            mock_req.return_value = resp

            api_request("GET", "/system/status", auth_required=False)
            _, kwargs = mock_req.call_args
            assert "Authorization" not in kwargs["headers"]

    def test_missing_token_exits(self):
        with patch("craft.client.get_token", return_value=""), \
             patch("craft.client.get_base_url", return_value="https://api.test.com"):
            with pytest.raises(SystemExit):
                api_request("GET", "/vms")

    def test_connection_error_exits(self, mock_config):
        import requests as req_lib
        with patch("craft.client.requests.request", side_effect=req_lib.ConnectionError):
            with pytest.raises(SystemExit):
                api_request("GET", "/vms")

    def test_timeout_error_exits(self, mock_config):
        import requests as req_lib
        with patch("craft.client.requests.request", side_effect=req_lib.Timeout):
            with pytest.raises(SystemExit):
                api_request("GET", "/vms")

    def test_http_400_exits_with_message(self, mock_config):
        with patch("craft.client.requests.request") as mock_req:
            resp = MagicMock()
            resp.status_code = 400
            resp.json.return_value = {"message": "Invalid input"}
            mock_req.return_value = resp

            with pytest.raises(SystemExit):
                api_request("GET", "/vms")

    def test_http_401_exits(self, mock_config):
        with patch("craft.client.requests.request") as mock_req:
            resp = MagicMock()
            resp.status_code = 401
            resp.json.return_value = {}
            mock_req.return_value = resp

            with pytest.raises(SystemExit):
                api_request("GET", "/vms")

    def test_http_404_exits(self, mock_config):
        with patch("craft.client.requests.request") as mock_req:
            resp = MagicMock()
            resp.status_code = 404
            resp.json.return_value = {"error": "Not found"}
            mock_req.return_value = resp

            with pytest.raises(SystemExit):
                api_request("GET", "/vms/999")

    def test_http_422_validation_errors(self, mock_config):
        with patch("craft.client.requests.request") as mock_req:
            resp = MagicMock()
            resp.status_code = 422
            resp.json.return_value = {
                "message": "Validation failed",
                "errors": [{"message": "name is required"}]
            }
            mock_req.return_value = resp

            with pytest.raises(SystemExit):
                api_request("POST", "/vms")

    def test_http_429_rate_limit(self, mock_config):
        with patch("craft.client.requests.request") as mock_req:
            resp = MagicMock()
            resp.status_code = 429
            resp.json.return_value = {}
            mock_req.return_value = resp

            with pytest.raises(SystemExit):
                api_request("GET", "/vms")

    def test_http_500_server_error(self, mock_config):
        with patch("craft.client.requests.request") as mock_req:
            resp = MagicMock()
            resp.status_code = 500
            resp.json.return_value = {}
            mock_req.return_value = resp

            with pytest.raises(SystemExit):
                api_request("GET", "/vms")

    def test_nested_error_message(self, mock_config):
        with patch("craft.client.requests.request") as mock_req:
            resp = MagicMock()
            resp.status_code = 400
            resp.json.return_value = {"error": {"message": "nested error"}}
            mock_req.return_value = resp

            with pytest.raises(SystemExit):
                api_request("GET", "/vms")

    def test_dict_errors_format(self, mock_config):
        with patch("craft.client.requests.request") as mock_req:
            resp = MagicMock()
            resp.status_code = 422
            resp.json.return_value = {
                "errors": {"name": "required", "email": "invalid"}
            }
            mock_req.return_value = resp

            with pytest.raises(SystemExit):
                api_request("POST", "/me")

    def test_params_passed_through(self, mock_config):
        with patch("craft.client.requests.request") as mock_req:
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {}
            mock_req.return_value = resp

            api_request("GET", "/vms", params={"page": 1, "limit": 10})
            _, kwargs = mock_req.call_args
            assert kwargs["params"] == {"page": 1, "limit": 10}

    def test_custom_timeout(self, mock_config):
        with patch("craft.client.requests.request") as mock_req:
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {}
            mock_req.return_value = resp

            api_request("POST", "/vms", timeout=120)
            _, kwargs = mock_req.call_args
            assert kwargs["timeout"] == 120


class TestShortcuts:
    def test_get(self, mock_config):
        with patch("craft.client.api_request") as mock:
            mock.return_value = {}
            get("/vms", params={"page": 1})
            mock.assert_called_once_with("GET", "/vms", params={"page": 1}, auth_required=True)

    def test_post(self, mock_config):
        with patch("craft.client.api_request") as mock:
            mock.return_value = {}
            post("/vms", data={"name": "x"}, timeout=60)
            mock.assert_called_once_with("POST", "/vms", json_data={"name": "x"}, auth_required=True, timeout=60)

    def test_put(self, mock_config):
        with patch("craft.client.api_request") as mock:
            mock.return_value = {}
            put("/me", data={"name": "x"})
            mock.assert_called_once_with("PUT", "/me", json_data={"name": "x"}, auth_required=True)

    def test_patch(self, mock_config):
        with patch("craft.client.api_request") as mock:
            mock.return_value = {}
            client_patch("/vms/1/rename", data={"name": "x"})
            mock.assert_called_once_with("PATCH", "/vms/1/rename", json_data={"name": "x"}, auth_required=True)

    def test_delete(self, mock_config):
        with patch("craft.client.api_request") as mock:
            mock.return_value = {}
            delete("/vms/1")
            mock.assert_called_once_with("DELETE", "/vms/1", auth_required=True)

    def test_get_no_auth(self, mock_config):
        with patch("craft.client.api_request") as mock:
            mock.return_value = {}
            get("/system/status", auth=False)
            mock.assert_called_once_with("GET", "/system/status", params=None, auth_required=False)
