import click

from craft.client import delete, get, patch, post
from craft.output import print_item, print_json, print_success, print_table


@click.command("list")
@click.option("--page", default=1, help="Page number")
@click.option("--limit", default=10, help="Items per page (max 50)")
def vm_list(page, limit):
    """List your VMs."""
    data = get("/vms", params={"page": page, "limit": limit})
    items = data.get("data", data) if not isinstance(data.get("data"), list) else data["data"]
    if isinstance(items, dict):
        items = items.get("items", items.get("vms", [items]))
    if isinstance(items, list) and items:
        rows = []
        for vm in items:
            rows.append([
                vm.get("id", ""),
                vm.get("name", ""),
                vm.get("status", ""),
                vm.get("ip", vm.get("ipAddress", "")),
                vm.get("os", vm.get("osTemplate", "")),
            ])
        print_table(rows, ["ID", "Name", "Status", "IP", "OS"])
    else:
        print_json(data)


@click.command("get")
@click.argument("vm_id")
def vm_get(vm_id):
    """Get VM details."""
    data = get(f"/vms/{vm_id}")
    print_item(data)


@click.command("create")
@click.option("--name", required=True, help="VM name (1-50 chars)")
@click.option("--hostname", required=True, help="Hostname (RFC-1123)")
@click.option("--node-id", required=True, help="Node UUID")
@click.option("--os-template-id", required=True, help="OS template UUID")
@click.option("--root-password", prompt=True, hide_input=True, help="Root password (min 8 chars)")
@click.option("--plan-id", default=None, help="Plan UUID")
@click.option("--billing-type", type=click.Choice(["daily", "weekly", "monthly", "yearly"]), default="daily")
@click.option("--cpu", default=None, type=int, help="Custom CPU cores (1-32)")
@click.option("--ram-mb", default=None, type=int, help="Custom RAM in MB (512-131072)")
@click.option("--disk-gb", default=None, type=int, help="Custom disk in GB (10-2000)")
@click.option("--ssh-keys", default=None, help="Comma-separated SSH key IDs")
def vm_create(name, hostname, node_id, os_template_id, root_password, plan_id,
              billing_type, cpu, ram_mb, disk_gb, ssh_keys):
    """Create a new VM."""
    body = {
        "name": name,
        "hostname": hostname,
        "nodeId": node_id,
        "osTemplateId": os_template_id,
        "rootPassword": root_password,
        "billingType": billing_type,
    }
    if plan_id:
        body["planId"] = plan_id
    if cpu:
        body["cpu"] = cpu
    if ram_mb:
        body["ramMb"] = ram_mb
    if disk_gb:
        body["diskGb"] = disk_gb
    if ssh_keys:
        body["sshKeys"] = ssh_keys

    data = post("/vms", body)
    print_success("VM created.")
    print_item(data)


@click.command("delete")
@click.argument("vm_id")
@click.confirmation_option(prompt="This will permanently delete the VM and all data. Continue?")
def vm_delete(vm_id):
    """Delete a VM permanently."""
    delete(f"/vms/{vm_id}")
    print_success(f"VM {vm_id} deleted.")


@click.command("status")
@click.argument("vm_id")
def vm_status(vm_id):
    """Get real-time VM status."""
    data = get(f"/vms/{vm_id}/status")
    print_item(data)


@click.command("start")
@click.argument("vm_id")
def vm_start(vm_id):
    """Start a VM."""
    post(f"/vms/{vm_id}/start")
    print_success(f"VM {vm_id} started.")


@click.command("stop")
@click.argument("vm_id")
def vm_stop(vm_id):
    """Stop a VM (graceful ACPI shutdown)."""
    post(f"/vms/{vm_id}/stop")
    print_success(f"VM {vm_id} stopped.")


@click.command("reboot")
@click.argument("vm_id")
def vm_reboot(vm_id):
    """Reboot a VM."""
    post(f"/vms/{vm_id}/reboot")
    print_success(f"VM {vm_id} rebooted.")


@click.command("rename")
@click.argument("vm_id")
@click.option("--name", required=True, help="New name (1-50 chars)")
def vm_rename(vm_id, name):
    """Rename a VM."""
    patch(f"/vms/{vm_id}/rename", {"name": name})
    print_success(f"VM renamed to '{name}'.")


@click.command("reset-password")
@click.argument("vm_id")
@click.option("--username", default="root", help="Username (default: root)")
@click.option("--new-password", prompt=True, hide_input=True, confirmation_prompt=True)
def vm_reset_password(vm_id, username, new_password):
    """Reset VM user password via QEMU Guest Agent."""
    post(f"/vms/{vm_id}/reset-password", {"username": username, "newPassword": new_password})
    print_success(f"Password reset for '{username}'.")


@click.command("reset-network")
@click.argument("vm_id")
def vm_reset_network(vm_id):
    """Re-apply VM network configuration."""
    post(f"/vms/{vm_id}/reset-network")
    print_success("Network reset. Reboot the VM to apply.")


@click.command("resize")
@click.argument("vm_id")
@click.option("--plan-id", required=True, help="Target plan UUID")
def vm_resize(vm_id, plan_id):
    """Resize VM to a new plan."""
    post(f"/vms/{vm_id}/resize", {"planId": plan_id})
    print_success("VM resized.")


@click.command("reinstall")
@click.argument("vm_id")
@click.option("--os-template-id", required=True, help="OS template UUID")
@click.option("--root-password", prompt=True, hide_input=True)
@click.option("--ssh-keys", default=None, help="Comma-separated SSH key IDs")
@click.confirmation_option(prompt="WARNING: All data will be destroyed. Continue?")
def vm_reinstall(vm_id, os_template_id, root_password, ssh_keys):
    """Reinstall OS on a VM."""
    body = {"osTemplateId": os_template_id, "rootPassword": root_password}
    if ssh_keys:
        body["sshKeys"] = ssh_keys
    post(f"/vms/{vm_id}/reinstall", body)
    print_success("OS reinstalled.")


@click.command("console")
@click.argument("vm_id")
def vm_console(vm_id):
    """Get noVNC console access."""
    data = get(f"/vms/{vm_id}/console")
    print_item(data)


@click.command("network")
@click.argument("vm_id")
def vm_network(vm_id):
    """Get VM network info."""
    data = get(f"/vms/{vm_id}/network")
    print_item(data)


@click.command("metrics")
@click.argument("vm_id")
@click.option("--hours", default=24, help="Hours of data (1-168, default: 24)")
def vm_metrics(vm_id, hours):
    """Get VM performance metrics."""
    data = get(f"/vms/{vm_id}/metrics", params={"hours": hours})
    print_json(data)
