import click

from craft.client import get
from craft.output import print_item, print_table


def _extract_items(data, *keys):
    """Extract list from API response."""
    inner = data.get("data", data)
    if isinstance(inner, list):
        return inner
    if isinstance(inner, dict):
        for key in keys:
            if key in inner and isinstance(inner[key], list):
                return inner[key]
        for key in ("items", "data"):
            if key in inner and isinstance(inner[key], list):
                return inner[key]
    return []


@click.command("vm")
@click.option("--node-id", default=None, help="Filter by node UUID")
def plans_vm(node_id):
    """List VM plans with pricing.

    \b
    Shows plan name, specs, and pricing for each billing period.
    Use --node-id to filter plans for a specific node.

    \b
    Examples:
      craft plan vm
      craft plan vm --node-id <NODE_ID>
    """
    params = {}
    if node_id:
        params["nodeId"] = node_id
    data = get("/plans", params=params or None)
    items = _extract_items(data, "plans")
    if items:
        rows = []
        for p in items:
            rows.append([
                p.get("id", "")[:12],
                p.get("name", ""),
                p.get("cpu", ""),
                f"{p.get('ramMb', '')} MB",
                f"{p.get('diskGb', '')} GB",
                p.get("priceDaily", "-"),
                p.get("priceMonthly", "-"),
            ])
        print_table(rows, ["ID", "Name", "CPU", "RAM", "Disk", "Daily (฿)", "Monthly (฿)"])
    else:
        print_item(data)


@click.command("os")
def plans_os():
    """List available OS templates.

    \b
    Shows OS name, type, and version for VM installation.
    """
    data = get("/os-templates")
    items = _extract_items(data, "templates", "osTemplates")
    if items:
        rows = []
        for t in items:
            rows.append([
                t.get("id", "")[:12],
                t.get("name", t.get("label", "")),
                t.get("type", t.get("osType", "")),
            ])
        print_table(rows, ["ID", "Name", "Type"])
    else:
        print_item(data)


@click.command("dedicated")
def plans_dedicated():
    """List dedicated server plans (public, no auth)."""
    data = get("/dedicated-plans", auth=False)
    items = _extract_items(data, "plans")
    if items:
        rows = []
        for p in items:
            rows.append([
                p.get("id", "")[:12],
                p.get("name", ""),
                p.get("cpu", ""),
                p.get("ram", p.get("ramGb", "")),
                p.get("disk", p.get("diskGb", "")),
                p.get("priceMonthly", p.get("price", "-")),
            ])
        print_table(rows, ["ID", "Name", "CPU", "RAM", "Disk", "Monthly (฿)"])
    else:
        print_item(data)


@click.command("colocation")
def plans_colocation():
    """List colocation plans (public, no auth)."""
    data = get("/colocation-plans", auth=False)
    items = _extract_items(data, "plans")
    if items:
        rows = []
        for p in items:
            rows.append([
                p.get("id", "")[:12],
                p.get("name", ""),
                p.get("rackSize", p.get("size", "")),
                p.get("power", ""),
                p.get("priceMonthly", p.get("price", "-")),
            ])
        print_table(rows, ["ID", "Name", "Rack", "Power", "Monthly (฿)"])
    else:
        print_item(data)
