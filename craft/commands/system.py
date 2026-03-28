import click

from craft.client import get
from craft.output import print_item, print_json


@click.command("status")
def system_status():
    """Get system status and announcements."""
    data = get("/system/status", auth=False)
    print_item(data)


@click.command("plans")
def system_plans():
    """List public VPS plans."""
    data = get("/system/plans", auth=False)
    print_json(data)


@click.command("nodes")
def system_nodes():
    """List public nodes."""
    data = get("/system/nodes", auth=False)
    print_json(data)
