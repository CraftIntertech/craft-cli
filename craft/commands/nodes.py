import click

from craft.client import get
from craft.output import print_item, print_json


@click.command("list")
def node_list():
    """List available nodes."""
    data = get("/nodes")
    print_json(data)


@click.command("hardware")
@click.argument("node_id")
def node_hardware(node_id):
    """Get node hardware info."""
    data = get(f"/nodes/{node_id}/hardware")
    print_item(data)
