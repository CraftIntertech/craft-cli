import click

from craft.client import delete, get, post
from craft.output import print_item, print_json, print_success, print_table


@click.command("list")
@click.argument("vm_id")
def snap_list(vm_id):
    """List snapshots for a VM."""
    data = get(f"/vms/{vm_id}/snapshots")
    items = data.get("data", data)
    if isinstance(items, dict):
        items = items.get("snapshots", items.get("items", []))
    if isinstance(items, list) and items:
        rows = []
        for s in items:
            rows.append([
                s.get("id", s.get("name", "")),
                s.get("description", ""),
                s.get("createdAt", s.get("snaptime", "")),
            ])
        print_table(rows, ["ID", "Description", "Created"])
    else:
        print_json(data)


@click.command("create")
@click.argument("vm_id")
@click.option("--description", default="", help="Snapshot description (max 200 chars)")
def snap_create(vm_id, description):
    """Create a snapshot (max 5 per VM)."""
    body = {}
    if description:
        body["description"] = description
    data = post(f"/vms/{vm_id}/snapshots", body)
    print_success("Snapshot created.")
    print_item(data)


@click.command("delete")
@click.argument("vm_id")
@click.argument("snap_id")
@click.confirmation_option(prompt="Delete this snapshot?")
def snap_delete(vm_id, snap_id):
    """Delete a snapshot."""
    delete(f"/vms/{vm_id}/snapshots/{snap_id}")
    print_success(f"Snapshot {snap_id} deleted.")


@click.command("rollback")
@click.argument("vm_id")
@click.argument("snap_id")
@click.confirmation_option(prompt="WARNING: Current VM state will be lost. Continue?")
def snap_rollback(vm_id, snap_id):
    """Rollback VM to a snapshot."""
    post(f"/vms/{vm_id}/snapshots/{snap_id}/rollback")
    print_success("Rollback complete.")


@click.command("sync")
@click.argument("vm_id")
def snap_sync(vm_id):
    """Sync snapshot records with hypervisor."""
    post(f"/vms/{vm_id}/snapshots/sync")
    print_success("Snapshots synced.")
