import click

from craft.client import get
from craft.output import print_item


@click.command("code")
def referral_code():
    """Get your referral code."""
    data = get("/referral")
    print_item(data)


@click.command("stats")
def referral_stats():
    """Get referral statistics and earnings."""
    data = get("/referral/stats")
    print_item(data)


@click.command("check")
@click.argument("code")
def referral_check(code):
    """Validate a referral code (no auth required)."""
    data = get(f"/referral/check/{code}", auth=False)
    print_item(data)
