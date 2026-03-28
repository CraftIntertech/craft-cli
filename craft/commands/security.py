import click

from craft.client import get, post
from craft.output import print_item, print_success


def _print_qr(data_str):
    """Print QR code in terminal using block characters."""
    try:
        import qrcode

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=1,
        )
        qr.add_data(data_str)
        qr.make(fit=True)
        click.echo()
        qr.print_ascii(invert=True)
        click.echo()
        return True
    except ImportError:
        return False


@click.command("status")
def twofa_status():
    """Check 2FA status."""
    data = get("/security/2fa")
    print_item(data)


@click.command("setup")
def twofa_setup():
    """Initialize 2FA setup. Shows QR code in terminal."""
    data = post("/security/2fa/setup")
    inner = data.get("data", data)
    secret = inner.get("secret", "")
    otpauth = inner.get("otpauthUrl", inner.get("url", ""))

    if otpauth:
        click.echo(click.style("── 2FA Setup ──", fg="cyan", bold=True))
        click.echo()
        click.echo("Scan this QR code with your authenticator app:")
        if not _print_qr(otpauth):
            click.echo()
            click.echo("  (Install 'qrcode' for QR display: pip install qrcode)")
            click.echo()
    if secret:
        click.echo(f"  Secret: {click.style(secret, fg='yellow', bold=True)}")
    if otpauth:
        click.echo(f"  OTP URL: {otpauth}")
    if not secret and not otpauth:
        print_item(data)

    click.echo()
    click.echo("Then verify with:")
    click.echo(click.style("  craft 2fa verify --code <6-digit-code>", fg="cyan"))


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
