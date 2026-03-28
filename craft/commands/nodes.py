import click

from craft.client import get
from craft.output import print_item, print_table


@click.command("list")
def node_list():
    """List available infrastructure nodes.

    \b
    Shows node name, location, and status.
    Use 'craft node hardware <NODE_ID>' for detailed specs.
    """
    data = get("/nodes")
    items = data.get("data", data)
    if isinstance(items, dict):
        items = items.get("items", items.get("nodes", []))
    if isinstance(items, list) and items:
        rows = []
        for n in items:
            rows.append([
                n.get("id", ""),
                n.get("name", n.get("hostname", "")),
                n.get("location", ""),
                n.get("country", ""),
                n.get("status", ""),
            ])
        print_table(rows, ["ID", "Name", "Location", "Country", "Status"])
    else:
        print_item(data)


@click.command("hardware")
@click.argument("node_id", required=False, default=None)
def node_hardware(node_id):
    """Get node hardware info (CPU, RAM, storage).

    \b
    If NODE_ID is omitted, you can select interactively.
    """
    if not node_id:
        from craft.interactive import select_node
        node_id = select_node("Select node for hardware info")
    data = get(f"/nodes/{node_id}/hardware")
    print_item(data)
