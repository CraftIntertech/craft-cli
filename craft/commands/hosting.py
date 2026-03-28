import click

from craft.client import delete, get, patch, post
from craft.output import print_item, print_json, print_page_info, print_success, print_table


@click.command("plans")
def hosting_plans():
    """List available hosting plans with pricing."""
    data = get("/hosting/plans")
    items = data.get("data", data)
    if isinstance(items, dict):
        items = items.get("items", items.get("plans", []))
    if isinstance(items, list) and items:
        rows = []
        for p in items:
            rows.append([
                p.get("id", "")[:12],
                p.get("name", ""),
                p.get("diskGb", p.get("disk", "")),
                p.get("bandwidth", ""),
                p.get("priceMonthly", p.get("price", "-")),
            ])
        print_table(rows, ["ID", "Name", "Disk (GB)", "Bandwidth", "Monthly (฿)"])
    else:
        print_json(data)


@click.command("nodes")
def hosting_nodes():
    """List available hosting nodes."""
    data = get("/hosting/nodes")
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
                n.get("status", ""),
            ])
        print_table(rows, ["ID", "Name", "Location", "Status"])
    else:
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
        print_page_info(data, page, limit)
    else:
        print_json(data)


@click.command("get")
@click.argument("hosting_id", required=False, default=None)
def hosting_get(hosting_id):
    """Get hosting account details."""
    if not hosting_id:
        from craft.interactive import select_hosting
        hosting_id = select_hosting()
    data = get(f"/hosting/{hosting_id}")
    print_item(data)


@click.command("create")
@click.option("--name", default=None, help="Account name (1-50 chars)")
@click.option("--domain", default=None, help="Domain name")
@click.option("--node-id", default=None, help="Node UUID")
@click.option("--plan-id", default=None, help="Plan UUID")
@click.option("--billing-type", type=click.Choice(["daily", "weekly", "monthly", "yearly"]), default=None)
@click.option("-i", "--interactive", is_flag=True, help="Interactive mode")
def hosting_create(name, domain, node_id, plan_id, billing_type, interactive):
    """Create a hosting account.

    \b
    Two modes:
      craft hosting create -i                     # Interactive wizard
      craft hosting create --name x --domain y    # Direct flags
    """
    if not all([name, domain, node_id, plan_id]):
        interactive = True

    if interactive:
        from craft.interactive import (
            confirm, input_text, select_billing_type,
            select_hosting_node, select_hosting_plan,
        )

        click.echo(click.style("── Create Hosting ──", fg="cyan", bold=True))
        click.echo()

        if not name:
            name = input_text("Account name:")
        if not domain:
            domain = input_text("Domain (e.g. example.com):")
        if not node_id:
            node_id = select_hosting_node()
        if not plan_id:
            plan_id = select_hosting_plan()
        if not billing_type:
            billing_type = select_billing_type()

        click.echo()
        click.echo(click.style("── Summary ──", fg="cyan"))
        click.echo(f"  Name:    {name}")
        click.echo(f"  Domain:  {domain}")
        click.echo(f"  Billing: {billing_type}")
        click.echo()

        if not confirm("Create this hosting account?"):
            click.echo("Cancelled.")
            return
    else:
        if not billing_type:
            billing_type = "monthly"

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
@click.argument("hosting_id", required=False, default=None)
def hosting_delete(hosting_id):
    """Delete a hosting account."""
    if not hosting_id:
        from craft.interactive import select_hosting
        hosting_id = select_hosting("Select hosting account to delete")
    if not click.confirm("This will permanently delete the hosting account. Continue?"):
        click.echo("Cancelled.")
        return
    delete(f"/hosting/{hosting_id}")
    print_success(f"Hosting {hosting_id} deleted.")


@click.command("login-url")
@click.argument("hosting_id", required=False, default=None)
def hosting_login_url(hosting_id):
    """Get DirectAdmin SSO login URL (expires in 30 min)."""
    if not hosting_id:
        from craft.interactive import select_hosting
        hosting_id = select_hosting()
    data = post(f"/hosting/{hosting_id}/login-url")
    inner = data.get("data", data)
    url = inner.get("loginUrl", inner.get("url", ""))
    if url:
        click.echo(url)
    else:
        print_json(data)


@click.command("billing")
@click.argument("hosting_id", required=False, default=None)
def hosting_billing(hosting_id):
    """Get hosting billing status."""
    if not hosting_id:
        from craft.interactive import select_hosting
        hosting_id = select_hosting()
    data = get(f"/hosting/{hosting_id}/billing")
    print_item(data)


@click.command("renew")
@click.argument("hosting_id", required=False, default=None)
@click.option("--billing-type", default=None, type=click.Choice(["daily", "weekly", "monthly", "yearly"]))
def hosting_renew(hosting_id, billing_type):
    """Renew hosting account."""
    if not hosting_id:
        from craft.interactive import select_hosting
        hosting_id = select_hosting()
    if not billing_type:
        from craft.interactive import select_billing_type
        billing_type = select_billing_type()
    data = post(f"/hosting/{hosting_id}/renew", {"billingType": billing_type})
    print_success("Hosting renewed.")
    print_item(data)


@click.command("auto-renew")
@click.argument("hosting_id", required=False, default=None)
@click.option("--enable/--disable", default=None)
def hosting_auto_renew(hosting_id, enable):
    """Toggle hosting auto-renewal."""
    if not hosting_id:
        from craft.interactive import select_hosting
        hosting_id = select_hosting()
    if enable is None:
        from craft.interactive import confirm
        enable = confirm("Enable auto-renew?")
    patch(f"/hosting/{hosting_id}/auto-renew", {"enabled": enable})
    state = "enabled" if enable else "disabled"
    print_success(f"Auto-renew {state}.")
