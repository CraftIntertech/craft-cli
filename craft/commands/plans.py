import click

from craft.client import get
from craft.output import print_json


@click.command("vm")
@click.option("--node-id", default=None, help="Filter by node UUID")
def plans_vm(node_id):
    """List VM plans."""
    params = {}
    if node_id:
        params["nodeId"] = node_id
    data = get("/plans", params=params or None)
    print_json(data)


@click.command("os")
def plans_os():
    """List OS templates."""
    data = get("/os-templates")
    print_json(data)


@click.command("dedicated")
def plans_dedicated():
    """List dedicated server plans (public)."""
    data = get("/dedicated-plans", auth=False)
    print_json(data)


@click.command("colocation")
def plans_colocation():
    """List colocation plans (public)."""
    data = get("/colocation-plans", auth=False)
    print_json(data)
