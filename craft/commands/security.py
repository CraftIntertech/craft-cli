import click

from craft.client import get, post
from craft.output import print_item, print_success


@click.command("status")
def twofa_status():
    """Check 2FA status."""
    data = get("/security/2fa")
    print_item(data)


@click.command("setup")
def twofa_setup():
    """Initialize 2FA setup. Returns TOTP secret and QR URL."""
    data = post("/security/2fa/setup")
    inner = data.get("data", data)
    secret = inner.get("secret", "")
    otpauth = inner.get("otpauthUrl", inner.get("url", ""))
    if secret:
        click.echo(f"Secret: {secret}")
    if otpauth:
        click.echo(f"OTP URL: {otpauth}")
    if not secret and not otpauth:
        print_item(data)
    click.echo("\nScan the QR code or enter the secret in your authenticator app.")
    click.echo("Then run: craft 2fa verify --code <6-digit-code>")


@click.command("verify")
@click.option("--code", required=True, help="6-digit TOTP code")
def twofa_verify(code):
    """Verify and activate 2FA."""
    post("/security/2fa/verify", {"code": code})
    print_success("2FA activated.")


@click.command("disable")
@click.option("--code", required=True, help="6-digit TOTP code")
def twofa_disable(code):
    """Disable 2FA."""
    post("/security/2fa/disable", {"code": code})
    print_success("2FA disabled.")
