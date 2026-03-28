import click

from craft.client import post
from craft.config import clear_tokens, load_config, save_tokens
from craft.output import print_success


@click.command()
@click.argument("token")
def login(token):
    """Authenticate with an API token or API key.

    \b
    TOKEN can be:
      - JWT access token (from web dashboard)
      - API key (cit_...)

    \b
    Examples:
      craft login eyJhbGciOi...
      craft login cit_xxxxxxxxxxxx
    """
    save_tokens(token)
    masked = token[:8] + "..." + token[-4:] if len(token) > 16 else "****"
    print_success(f"Token saved ({masked})")


@click.command()
def logout():
    """Clear saved token."""
    config = load_config()
    refresh_token = config.get("refresh_token", "")
    if refresh_token:
        try:
            post("/auth/logout", {"refreshToken": refresh_token})
        except SystemExit:
            pass
    clear_tokens()
    print_success("Logged out.")


@click.command()
def refresh():
    """Refresh access token."""
    config = load_config()
    refresh_token = config.get("refresh_token", "")
    if not refresh_token:
        click.echo("Error: No refresh token saved.", err=True)
        return

    data = post("/auth/refresh", {"refreshToken": refresh_token}, auth=False)
    inner = data.get("data", data)
    access_token = inner.get("accessToken", "")
    new_refresh = inner.get("refreshToken", refresh_token)
    if access_token:
        save_tokens(access_token, new_refresh)
        print_success("Token refreshed.")
    else:
        click.echo("Error: Could not refresh token.", err=True)
