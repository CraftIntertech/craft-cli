import sys

import click
import requests

from craft.config import get_base_url, get_token


def api_request(method, path, json_data=None, params=None, auth_required=True):
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
            method, url, json=json_data, params=params, headers=headers, timeout=30
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
        if resp.status_code >= 400:
            click.echo(f"Error: HTTP {resp.status_code}", err=True)
            sys.exit(1)
        return {}

    if resp.status_code >= 400:
        msg = data.get("message") or data.get("error") or f"HTTP {resp.status_code}"
        click.echo(f"Error: {msg}", err=True)
        sys.exit(1)

    return data


def get(path, params=None, auth=True):
    return api_request("GET", path, params=params, auth_required=auth)


def post(path, data=None, auth=True):
    return api_request("POST", path, json_data=data, auth_required=auth)


def put(path, data=None, auth=True):
    return api_request("PUT", path, json_data=data, auth_required=auth)


def patch(path, data=None, auth=True):
    return api_request("PATCH", path, json_data=data, auth_required=auth)


def delete(path, auth=True):
    return api_request("DELETE", path, auth_required=auth)
