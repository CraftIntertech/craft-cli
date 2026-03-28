import click

from craft.client import delete, get, post
from craft.output import print_item, print_json, print_success, print_table


@click.command("list")
def sshkey_list():
    """List saved SSH keys."""
    data = get("/ssh-keys")
    items = data.get("data", data)
    if isinstance(items, dict):
        items = items.get("items", items.get("keys", []))
    if isinstance(items, list) and items:
        rows = []
        for k in items:
            rows.append([
                k.get("id", ""),
                k.get("name", ""),
                k.get("fingerprint", k.get("publicKey", "")[:40]),
            ])
        print_table(rows, ["ID", "Name", "Fingerprint"])
    else:
        print_json(data)


@click.command("add")
@click.option("--name", required=True, help="Key name (1-100 chars)")
@click.option("--public-key", required=True, help="OpenSSH public key")
def sshkey_add(name, public_key):
    """Add an SSH public key."""
    data = post("/ssh-keys", {"name": name, "publicKey": public_key})
    print_success("SSH key added.")
    print_item(data)


@click.command("add-file")
@click.option("--name", required=True, help="Key name (1-100 chars)")
@click.option("--file", "key_file", required=True, type=click.Path(exists=True), help="Path to public key file")
def sshkey_add_file(name, key_file):
    """Add an SSH key from a file."""
    with open(key_file) as f:
        public_key = f.read().strip()
    data = post("/ssh-keys", {"name": name, "publicKey": public_key})
    print_success("SSH key added.")
    print_item(data)


@click.command("delete")
@click.argument("key_id")
def sshkey_delete(key_id):
    """Delete an SSH key."""
    delete(f"/ssh-keys/{key_id}")
    print_success(f"SSH key {key_id} deleted.")
