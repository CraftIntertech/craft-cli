import click

from craft.client import delete, get, patch, post
from craft.output import print_item, print_json, print_success, print_table


@click.command("plans")
def hosting_plans():
    """List available hosting plans."""
    data = get("/hosting/plans")
    print_json(data)


@click.command("nodes")
def hosting_nodes():
    """List available hosting nodes."""
    data = get("/hosting/nodes")
    print_json(data)


@click.command("list")
@click.option("--page", default=1, help="Page number")
@click.option("--limit", default=10, help="Items per page")
def hosting_list(page, limit):
    """List your hosting accounts."""
    data = get("/hosting", params={"page": page, "limit": limit})
    items = data.get("data", data)
    if isinstance(items, dict):
        items = items.get("items", items.get("accounts", []))
    if isinstance(items, list) and items:
        rows = []
        for h in items:
            rows.append([
                h.get("id", ""),
                h.get("name", ""),
                h.get("domain", ""),
                h.get("status", ""),
            ])
        print_table(rows, ["ID", "Name", "Domain", "Status"])
    else:
        print_json(data)


@click.command("get")
@click.argument("hosting_id")
def hosting_get(hosting_id):
    """Get hosting account details."""
    data = get(f"/hosting/{hosting_id}")
    print_item(data)


@click.command("create")
@click.option("--name", required=True, help="Account name (1-50 chars)")
@click.option("--domain", required=True, help="Domain name")
@click.option("--node-id", required=True, help="Node UUID")
@click.option("--plan-id", required=True, help="Plan UUID")
@click.option("--billing-type", type=click.Choice(["daily", "weekly", "monthly", "yearly"]), default="monthly")
def hosting_create(name, domain, node_id, plan_id, billing_type):
    """Create a hosting account."""
    body = {
        "name": name,
        "domain": domain,
        "nodeId": node_id,
        "planId": plan_id,
        "billingType": billing_type,
    }
    data = post("/hosting", body)
    print_success("Hosting account created.")
    print_item(data)


@click.command("delete")
@click.argument("hosting_id")
@click.confirmation_option(prompt="This will permanently delete the hosting account. Continue?")
def hosting_delete(hosting_id):
    """Delete a hosting account."""
    delete(f"/hosting/{hosting_id}")
    print_success(f"Hosting {hosting_id} deleted.")


@click.command("login-url")
@click.argument("hosting_id")
def hosting_login_url(hosting_id):
    """Get DirectAdmin SSO login URL (expires in 30 min)."""
    data = post(f"/hosting/{hosting_id}/login-url")
    inner = data.get("data", data)
    url = inner.get("loginUrl", inner.get("url", ""))
    if url:
        click.echo(url)
    else:
        print_json(data)


@click.command("billing")
@click.argument("hosting_id")
def hosting_billing(hosting_id):
    """Get hosting billing status."""
    data = get(f"/hosting/{hosting_id}/billing")
    print_item(data)


@click.command("renew")
@click.argument("hosting_id")
@click.option("--billing-type", required=True, type=click.Choice(["daily", "weekly", "monthly", "yearly"]))
def hosting_renew(hosting_id, billing_type):
    """Renew hosting account."""
    data = post(f"/hosting/{hosting_id}/renew", {"billingType": billing_type})
    print_success("Hosting renewed.")
    print_item(data)


@click.command("auto-renew")
@click.argument("hosting_id")
@click.option("--enable/--disable", required=True)
def hosting_auto_renew(hosting_id, enable):
    """Toggle hosting auto-renewal."""
    patch(f"/hosting/{hosting_id}/auto-renew", {"enabled": enable})
    state = "enabled" if enable else "disabled"
    print_success(f"Auto-renew {state}.")
