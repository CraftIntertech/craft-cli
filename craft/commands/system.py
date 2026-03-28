import click

from craft.client import get
from craft.output import print_item, print_json, print_table


@click.command("status")
def system_status():
    """Get system status and announcements (no auth required)."""
    data = get("/system/status", auth=False)
    print_item(data)


@click.command("plans")
def system_plans():
    """List public VPS plans (no auth required)."""
    data = get("/system/plans", auth=False)
    items = data.get("data", data)
    if isinstance(items, dict):
        items = items.get("items", items.get("plans", []))
    if isinstance(items, list) and items:
        rows = []
        for p in items:
            rows.append([
                p.get("name", ""),
                p.get("cpu", ""),
                f"{p.get('ramMb', '')} MB",
                f"{p.get('diskGb', '')} GB",
                p.get("priceMonthly", p.get("price", "-")),
            ])
        print_table(rows, ["Name", "CPU", "RAM", "Disk", "Monthly (฿)"])
    else:
        print_json(data)


@click.command("nodes")
def system_nodes():
    """List public nodes (no auth required)."""
    data = get("/system/nodes", auth=False)
    items = data.get("data", data)
    if isinstance(items, dict):
        items = items.get("items", items.get("nodes", []))
    if isinstance(items, list) and items:
        rows = []
        for n in items:
            rows.append([
                n.get("name", n.get("hostname", "")),
                n.get("location", ""),
                n.get("country", ""),
                n.get("status", ""),
            ])
        print_table(rows, ["Name", "Location", "Country", "Status"])
    else:
        print_json(data)
