"""Test API connectivity and endpoint health."""

import sys
import time

import click
import requests

from craft.config import get_base_url, get_token


def _check(label, method, path, auth=True, expect_list=False):
    """Test a single API endpoint. Returns (ok, status_code, elapsed_ms)."""
    base_url = get_base_url()
    url = f"{base_url}{path}"
    headers = {"Content-Type": "application/json"}

    if auth:
        token = get_token()
        if not token:
            return False, 0, 0, "No token"
        headers["Authorization"] = f"Bearer {token}"

    try:
        start = time.time()
        resp = requests.request(method, url, headers=headers, timeout=15)
        elapsed = int((time.time() - start) * 1000)

        if resp.status_code < 400:
            return True, resp.status_code, elapsed, "OK"
        else:
            try:
                data = resp.json()
                msg = data.get("message", data.get("error", f"HTTP {resp.status_code}"))
            except ValueError:
                msg = f"HTTP {resp.status_code}"
            return False, resp.status_code, elapsed, str(msg)

    except requests.ConnectionError:
        return False, 0, 0, "Connection refused"
    except requests.Timeout:
        return False, 0, 0, "Timeout (>15s)"


@click.command("test-api")
@click.option("--all", "test_all", is_flag=True, help="Test all endpoints (including authenticated)")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed results")
def test_api(test_all, verbose):
    """Test API connectivity and endpoint health.

    \b
    By default, tests only public (no-auth) endpoints.
    Use --all to include authenticated endpoints (requires login).

    \b
    Examples:
      craft test-api             # Test public endpoints
      craft test-api --all       # Test all endpoints
      craft test-api --all -v    # Verbose output
    """
    public_endpoints = [
        ("System Status", "GET", "/system/status"),
        ("System Plans", "GET", "/system/plans"),
        ("System Nodes", "GET", "/system/nodes"),
        ("Dedicated Plans", "GET", "/dedicated-plans"),
        ("Colocation Plans", "GET", "/colocation-plans"),
    ]

    auth_endpoints = [
        ("Profile", "GET", "/me"),
        ("VM List", "GET", "/vms"),
        ("Wallet Balance", "GET", "/wallet"),
        ("SSH Keys", "GET", "/ssh-keys"),
        ("API Keys", "GET", "/api-keys"),
        ("Tickets", "GET", "/tickets"),
        ("Nodes", "GET", "/nodes"),
        ("Plans", "GET", "/plans"),
        ("OS Templates", "GET", "/os-templates"),
        ("Hosting List", "GET", "/hosting"),
        ("Hosting Plans", "GET", "/hosting/plans"),
        ("Hosting Nodes", "GET", "/hosting/nodes"),
        ("2FA Status", "GET", "/security/2fa"),
        ("Referral Code", "GET", "/referral"),
        ("Referral Stats", "GET", "/referral/stats"),
        ("Activity Log", "GET", "/activity"),
        ("Wallet Transactions", "GET", "/wallet/transactions"),
    ]

    click.echo(click.style("── API Connectivity Test ──", fg="cyan", bold=True))
    click.echo(f"  Base URL: {get_base_url()}")
    click.echo()

    passed = 0
    failed = 0
    total = 0

    def run_group(label, endpoints, auth=False):
        nonlocal passed, failed, total
        click.echo(click.style(f"  {label}:", bold=True))
        for name, method, path in endpoints:
            total += 1
            ok, status, elapsed, msg = _check(name, method, path, auth=auth)
            if ok:
                passed += 1
                icon = click.style("PASS", fg="green")
                detail = f"{elapsed}ms" if verbose else ""
            else:
                failed += 1
                icon = click.style("FAIL", fg="red")
                detail = msg

            line = f"    {icon}  {name:<22}"
            if detail:
                line += click.style(f"  ({detail})", dim=True)
            click.echo(line)

    # Always test public endpoints
    run_group("Public endpoints (no auth)", public_endpoints, auth=False)

    if test_all:
        token = get_token()
        if not token:
            click.echo()
            click.echo(click.style("  Skipping auth endpoints — not logged in.", fg="yellow"))
            click.echo("  Run 'craft login <token>' first.")
        else:
            click.echo()
            run_group("Authenticated endpoints", auth_endpoints, auth=True)

    # Summary
    click.echo()
    color = "green" if failed == 0 else "red" if failed > passed else "yellow"
    click.echo(click.style(f"  Results: {passed}/{total} passed", fg=color))

    if failed > 0:
        sys.exit(1)
