import click

from craft.client import delete, get, post
from craft.output import print_item, print_json, print_success, print_table


@click.command("list")
@click.argument("vm_id", required=False, default=None)
def snap_list(vm_id):
    """List snapshots for a VM."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
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
@click.argument("vm_id", required=False, default=None)
@click.option("--description", default="", help="Snapshot description (max 200 chars)")
def snap_create(vm_id, description):
    """Create a snapshot (max 5 per VM)."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    if not description:
        from craft.interactive import input_text
        description = input_text("Description (optional):")
    body = {}
    if description:
        body["description"] = description
    data = post(f"/vms/{vm_id}/snapshots", body)
    print_success("Snapshot created.")
    print_item(data)


@click.command("delete")
@click.argument("vm_id", required=False, default=None)
@click.argument("snap_id", required=False, default=None)
def snap_delete(vm_id, snap_id):
    """Delete a snapshot."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    if not snap_id:
        from craft.interactive import select_snapshot
        snap_id = select_snapshot(vm_id, "Select snapshot to delete")
    if not click.confirm("Delete this snapshot?"):
        click.echo("Cancelled.")
        return
    delete(f"/vms/{vm_id}/snapshots/{snap_id}")
    print_success(f"Snapshot {snap_id} deleted.")


@click.command("rollback")
@click.argument("vm_id", required=False, default=None)
@click.argument("snap_id", required=False, default=None)
def snap_rollback(vm_id, snap_id):
    """Rollback VM to a snapshot."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    if not snap_id:
        from craft.interactive import select_snapshot
        snap_id = select_snapshot(vm_id, "Select snapshot to rollback to")
    if not click.confirm("WARNING: Current VM state will be lost. Continue?"):
        click.echo("Cancelled.")
        return
    post(f"/vms/{vm_id}/snapshots/{snap_id}/rollback")
    print_success("Rollback complete.")


@click.command("sync")
@click.argument("vm_id", required=False, default=None)
def snap_sync(vm_id):
    """Sync snapshot records with hypervisor."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    post(f"/vms/{vm_id}/snapshots/sync")
    print_success("Snapshots synced.")
