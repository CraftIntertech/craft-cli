import click

from craft.client import delete, get, post
from craft.output import print_item, print_success, print_table


@click.command("list")
def apikey_list():
    """List API keys (full key value is never shown)."""
    data = get("/api-keys")
    items = data.get("data", data)
    if isinstance(items, dict):
        items = items.get("items", items.get("keys", []))
    if isinstance(items, list) and items:
        rows = []
        for k in items:
            rows.append([
                k.get("id", ""),
                k.get("name", ""),
                k.get("prefix", ""),
                k.get("createdAt", ""),
            ])
        print_table(rows, ["ID", "Name", "Prefix", "Created"])
    else:
        print_item(data)


@click.command("create")
@click.option("--name", required=True, help="Key name (1-100 chars)")
def apikey_create(name):
    """Create an API key. The full key is shown ONCE."""
    data = post("/api-keys", {"name": name})
    inner = data.get("data", data)
    key = inner.get("key", inner.get("apiKey", ""))
    if key:
        click.echo(f"API Key: {key}")
        click.echo("Save this key now - it will not be shown again.")
    else:
        print_item(data)


@click.command("revoke")
@click.argument("key_id")
@click.confirmation_option(prompt="Revoke this API key?")
def apikey_revoke(key_id):
    """Revoke an API key permanently."""
    delete(f"/api-keys/{key_id}")
    print_success(f"API key {key_id} revoked.")
