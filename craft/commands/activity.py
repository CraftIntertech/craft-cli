import click

from craft.client import get
from craft.output import print_json, print_page_info, print_table


@click.command("list")
@click.option("--page", default=1)
@click.option("--limit", default=20, help="Items per page (max 50)")
def activity_list(page, limit):
    """Get account activity log."""
    data = get("/activity", params={"page": page, "limit": limit})
    items = data.get("data", data)
    if isinstance(items, dict):
        items = items.get("items", items.get("logs", []))
    if isinstance(items, list) and items:
        rows = []
        for log in items:
            rows.append([
                log.get("action", ""),
                log.get("description", log.get("detail", "")),
                log.get("ip", ""),
                log.get("createdAt", ""),
            ])
        print_table(rows, ["Action", "Description", "IP", "Date"])
        print_page_info(data, page, limit)
    else:
        print_json(data)
