import sys

import click
import requests

from craft.config import get_base_url, get_token


def api_request(method, path, json_data=None, params=None, auth_required=True, timeout=30):
    """Make an API request and return the JSON response."""
    base_url = get_base_url()
    url = f"{base_url}{path}"
    headers = {"Content-Type": "application/json"}

    if auth_required:
        token = get_token()
        if not token:
            click.echo("Error: Not authenticated. Run 'craft login' first.", err=True)
            sys.exit(1)
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.request(
            method, url, json=json_data, params=params, headers=headers, timeout=timeout
        )
    except requests.ConnectionError:
        click.echo("Error: Could not connect to API server.", err=True)
        sys.exit(1)
    except requests.Timeout:
        click.echo("Error: Request timed out.", err=True)
        sys.exit(1)

    try:
        data = resp.json()
    except ValueError:
        data = {}

    if resp.status_code >= 400:
        # Try to extract message from response
        msg = ""
        if isinstance(data, dict):
            msg = (
                data.get("message")
                or data.get("error")
                or data.get("detail")
                or data.get("msg")
                or ""
            )
            # Some APIs nest errors
            if not msg and "error" in data and isinstance(data["error"], dict):
                msg = data["error"].get("message", "")
            # Show validation errors
            errors = data.get("errors")
            if isinstance(errors, list):
                details = [e.get("message", e.get("msg", str(e))) for e in errors]
                msg = msg + " — " + "; ".join(details) if msg else "; ".join(details)
            elif isinstance(errors, dict):
                details = [f"{k}: {v}" for k, v in errors.items()]
                msg = msg + " — " + "; ".join(details) if msg else "; ".join(details)

        if not msg:
            status_hints = {
                400: "Bad request — check your input",
                401: "Unauthorized — run 'craft login' to authenticate",
                403: "Forbidden — you don't have permission",
                404: "Not found — resource doesn't exist",
                409: "Conflict — resource state doesn't allow this action",
                422: "Validation error — check your input",
                429: "Rate limited — try again later",
                500: "Internal server error",
                502: "Server temporarily unavailable — try again later",
                503: "Service unavailable — try again later",
                504: "Gateway timeout — try again later",
            }
            msg = status_hints.get(resp.status_code, f"HTTP {resp.status_code}")

        click.echo(f"Error [{resp.status_code}]: {msg}", err=True)
        sys.exit(1)

    return data


def get(path, params=None, auth=True):
    return api_request("GET", path, params=params, auth_required=auth)


def post(path, data=None, auth=True, timeout=30):
    return api_request("POST", path, json_data=data, auth_required=auth, timeout=timeout)


def put(path, data=None, auth=True):
    return api_request("PUT", path, json_data=data, auth_required=auth)


def patch(path, data=None, auth=True):
    return api_request("PATCH", path, json_data=data, auth_required=auth)


def delete(path, auth=True):
    return api_request("DELETE", path, auth_required=auth)
