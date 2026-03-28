import click

from craft.client import get, post
from craft.output import print_item, print_page_info, print_success, print_table


@click.command("balance")
def wallet_balance():
    """Get wallet balance."""
    data = get("/wallet")
    print_item(data)


@click.command("transactions")
@click.option("--page", default=1)
@click.option("--limit", default=20, help="Items per page (max 100)")
def wallet_transactions(page, limit):
    """List wallet transactions."""
    data = get("/wallet/transactions", params={"page": page, "limit": limit})
    items = data.get("data", data)
    if isinstance(items, dict):
        items = items.get("items", items.get("transactions", []))
    if isinstance(items, list) and items:
        rows = []
        for t in items:
            rows.append([
                t.get("id", ""),
                t.get("type", ""),
                t.get("amount", ""),
                t.get("description", t.get("note", "")),
                t.get("createdAt", ""),
            ])
        print_table(rows, ["ID", "Type", "Amount", "Description", "Date"])
        print_page_info(data, page, limit)
    else:
        print_item(data)


@click.command("topup")
@click.option("--amount", default=None, type=float, help="Amount in THB (max 100,000)")
@click.option("--reference", default=None, help="Bank transfer reference")
@click.option("--note", default=None, help="Optional note")
def wallet_topup(amount, reference, note):
    """Submit a top-up request.

    \b
    If --amount or --reference is omitted, you will be prompted.

    \b
    Examples:
      craft wallet topup --amount 500 --reference TRF123
      craft wallet topup                    # Interactive prompts
    """
    if amount is None:
        amount = click.prompt("Amount (THB)", type=float)
    if not reference:
        reference = click.prompt("Bank transfer reference")
    body = {"amount": amount, "reference": reference}
    if note:
        body["note"] = note
    data = post("/wallet/topup", body)
    print_success("Top-up submitted (pending admin approval).")
    print_item(data)
