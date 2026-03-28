import click

from craft.client import post
from craft.config import clear_tokens, load_config, save_tokens
from craft.output import print_item, print_success


@click.command()
@click.option("--email", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--first-name", prompt="First name")
@click.option("--last-name", prompt="Last name")
@click.option("--phone", prompt=True)
@click.option("--address", default="", help="Address (optional)")
@click.option("--company", default="", help="Company (optional)")
@click.option("--referral-code", default="", help="Referral code (optional)")
def register(email, password, first_name, last_name, phone, address, company, referral_code):
    """Create a new account."""
    body = {
        "email": email,
        "password": password,
        "firstName": first_name,
        "lastName": last_name,
        "phone": phone,
    }
    if address:
        body["address"] = address
    if company:
        body["company"] = company
    if referral_code:
        body["referralCode"] = referral_code

    data = post("/auth/register", body, auth=False)
    print_success("Account created successfully.")
    print_item(data)


@click.command()
@click.option("--email", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
def login(email, password):
    """Log in and save access token."""
    data = post("/auth/login", {"email": email, "password": password}, auth=False)

    inner = data.get("data", data)

    if inner.get("requires2FA"):
        temp_token = inner.get("tempToken", "")
        click.echo("2FA is enabled. Enter your authenticator code.")
        code = click.prompt("Code", type=str)
        data = post("/auth/verify-2fa", {"tempToken": temp_token, "code": code}, auth=False)
        inner = data.get("data", data)

    access_token = inner.get("accessToken", "")
    refresh_token = inner.get("refreshToken", "")

    if access_token:
        save_tokens(access_token, refresh_token)
        user = inner.get("user", {})
        name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
        print_success(f"Logged in as {name or email}")
    else:
        click.echo("Login response did not contain a token.")


@click.command()
def logout():
    """Log out and clear saved tokens."""
    config = load_config()
    refresh_token = config.get("refresh_token", "")
    if refresh_token:
        post("/auth/logout", {"refreshToken": refresh_token})
    clear_tokens()
    print_success("Logged out.")


@click.command()
def refresh():
    """Refresh access token."""
    config = load_config()
    refresh_token = config.get("refresh_token", "")
    if not refresh_token:
        click.echo("Error: No refresh token saved. Run 'craft login' first.", err=True)
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
