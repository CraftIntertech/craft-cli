import click

from craft.client import delete, get, patch, post
from craft.output import print_item, print_json, print_page_info, print_success, print_table


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
        print_page_info(data, page, limit)
    else:
        print_json(data)


@click.command("get")
@click.argument("vm_id", required=False, default=None)
def vm_get(vm_id):
    """Get VM details."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    data = get(f"/vms/{vm_id}")
    print_item(data)


@click.command("create")
@click.option("--name", default=None, help="VM name (1-50 chars)")
@click.option("--hostname", default=None, help="Hostname (RFC-1123)")
@click.option("--node-id", default=None, help="Node UUID")
@click.option("--os-template-id", default=None, help="OS template UUID")
@click.option("--root-password", default=None, help="Root password (min 8 chars)")
@click.option("--plan-id", default=None, help="Plan UUID")
@click.option("--billing-type", type=click.Choice(["daily", "weekly", "monthly", "yearly"]), default=None)
@click.option("--cpu", default=None, type=int, help="Custom CPU cores (1-32)")
@click.option("--ram-mb", default=None, type=int, help="Custom RAM in MB (512-131072)")
@click.option("--disk-gb", default=None, type=int, help="Custom disk in GB (10-2000)")
@click.option("--ssh-keys", default=None, help="Comma-separated SSH key IDs")
@click.option("-i", "--interactive", is_flag=True, help="Interactive mode with menus")
def vm_create(name, hostname, node_id, os_template_id, root_password, plan_id,
              billing_type, cpu, ram_mb, disk_gb, ssh_keys, interactive):
    """Create a new VM.

    \b
    Two modes:
      craft vm create -i                    # Interactive wizard
      craft vm create --name x --hostname y # Direct flags
    """
    # Auto-enable interactive if required fields are missing
    if not all([name, hostname, node_id, os_template_id]):
        interactive = True

    if interactive:
        from craft.interactive import (
            confirm, input_custom_specs, input_text,
            select_billing_type, select_billing_type_with_price,
            select_node, select_os_template,
            select_plan, select_ssh_keys,
        )

        click.echo(click.style("── Create VM ──", fg="cyan", bold=True))
        click.echo()

        if not name:
            name = input_text("VM name:")
        if not hostname:
            hostname = input_text("Hostname:", default=f"{name}.example.com")
        if not node_id:
            node_id = select_node()
        if not os_template_id:
            os_template_id = select_os_template()

        plan_data = None
        if not plan_id and not cpu:
            selected, plan_data = select_plan(node_id)
            if selected == "__custom__":
                cpu, ram_mb, disk_gb = input_custom_specs()
            else:
                plan_id = selected

        if not billing_type:
            if plan_data:
                billing_type = select_billing_type_with_price(plan_data)
            else:
                billing_type = select_billing_type()

        if not ssh_keys:
            ssh_keys = select_ssh_keys()

        if not root_password:
            root_password = input_text("Root password (min 8 chars):", password=True)

        # Build summary
        click.echo()
        click.echo(click.style("── Summary ──", fg="cyan"))
        click.echo(f"  Name:     {name}")
        click.echo(f"  Hostname: {hostname}")
        if plan_data:
            plan_name = plan_data.get("name", plan_id)
            p_cpu = plan_data.get("cpu", "?")
            p_ram = plan_data.get("ramMb", "?")
            p_disk = plan_data.get("diskGb", "?")
            click.echo(f"  Plan:     {plan_name} ({p_cpu} vCPU / {p_ram} MB / {p_disk} GB)")
        elif plan_id:
            click.echo(f"  Plan:     {plan_id}")
        if cpu:
            click.echo(f"  Specs:    {cpu} vCPU / {ram_mb} MB / {disk_gb} GB")
        click.echo(f"  Billing:  {billing_type}")
        # Show price for selected billing type
        if plan_data:
            price_key = f"price{billing_type.capitalize()}"
            price = plan_data.get(price_key)
            if price is not None:
                click.echo(click.style(f"  Price:    ฿{price}/{billing_type}", fg="yellow"))
        click.echo()

        if not confirm("Create this VM?"):
            click.echo("Cancelled.")
            return
    else:
        if not root_password:
            root_password = click.prompt("Root password", hide_input=True)
        if not billing_type:
            billing_type = "daily"

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

    data = post("/vms", body, timeout=120)
    print_success("VM created.")
    print_item(data)


@click.command("delete")
@click.argument("vm_id", required=False, default=None)
def vm_delete(vm_id):
    """Delete a VM permanently."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm("Select VM to delete")
    if not click.confirm("This will permanently delete the VM and all data. Continue?"):
        click.echo("Cancelled.")
        return
    delete(f"/vms/{vm_id}")
    print_success(f"VM {vm_id} deleted.")


@click.command("status")
@click.argument("vm_id", required=False, default=None)
def vm_status(vm_id):
    """Get real-time VM status."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    data = get(f"/vms/{vm_id}/status")
    print_item(data)


@click.command("start")
@click.argument("vm_id", required=False, default=None)
def vm_start(vm_id):
    """Start a VM."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm("Select VM to start")
    post(f"/vms/{vm_id}/start", timeout=120)
    print_success(f"VM {vm_id} started.")


@click.command("stop")
@click.argument("vm_id", required=False, default=None)
def vm_stop(vm_id):
    """Stop a VM (graceful ACPI shutdown)."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm("Select VM to stop")
    post(f"/vms/{vm_id}/stop", timeout=120)
    print_success(f"VM {vm_id} stopped.")


@click.command("reboot")
@click.argument("vm_id", required=False, default=None)
def vm_reboot(vm_id):
    """Reboot a VM."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm("Select VM to reboot")
    post(f"/vms/{vm_id}/reboot", timeout=120)
    print_success(f"VM {vm_id} rebooted.")


@click.command("rename")
@click.argument("vm_id", required=False, default=None)
@click.option("--name", default=None, help="New name (1-50 chars)")
def vm_rename(vm_id, name):
    """Rename a VM."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    if not name:
        from craft.interactive import input_text
        name = input_text("New name:")
    patch(f"/vms/{vm_id}/rename", {"name": name})
    print_success(f"VM renamed to '{name}'.")


@click.command("reset-password")
@click.argument("vm_id", required=False, default=None)
@click.option("--username", default="root", help="Username (default: root)")
@click.option("--new-password", default=None)
def vm_reset_password(vm_id, username, new_password):
    """Reset VM user password via QEMU Guest Agent."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    if not new_password:
        new_password = click.prompt("New password", hide_input=True, confirmation_prompt=True)
    post(f"/vms/{vm_id}/reset-password", {"username": username, "newPassword": new_password})
    print_success(f"Password reset for '{username}'.")


@click.command("reset-network")
@click.argument("vm_id", required=False, default=None)
def vm_reset_network(vm_id):
    """Re-apply VM network configuration."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    post(f"/vms/{vm_id}/reset-network")
    print_success("Network reset. Reboot the VM to apply.")


@click.command("resize")
@click.argument("vm_id", required=False, default=None)
@click.option("--plan-id", default=None, help="Target plan UUID")
def vm_resize(vm_id, plan_id):
    """Resize VM to a new plan."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    if not plan_id:
        from craft.interactive import select_plan
        plan_id = select_plan(label="Select new plan")
    post(f"/vms/{vm_id}/resize", {"planId": plan_id})
    print_success("VM resized.")


@click.command("reinstall")
@click.argument("vm_id", required=False, default=None)
@click.option("--os-template-id", default=None, help="OS template UUID")
@click.option("--root-password", default=None)
@click.option("--ssh-keys", default=None, help="Comma-separated SSH key IDs")
def vm_reinstall(vm_id, os_template_id, root_password, ssh_keys):
    """Reinstall OS on a VM."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm("Select VM to reinstall")
    if not os_template_id:
        from craft.interactive import select_os_template
        os_template_id = select_os_template()
    if not root_password:
        root_password = click.prompt("Root password", hide_input=True)
    if not click.confirm("WARNING: All data will be destroyed. Continue?"):
        click.echo("Cancelled.")
        return
    body = {"osTemplateId": os_template_id, "rootPassword": root_password}
    if ssh_keys:
        body["sshKeys"] = ssh_keys
    post(f"/vms/{vm_id}/reinstall", body)
    print_success("OS reinstalled.")


@click.command("console")
@click.argument("vm_id", required=False, default=None)
def vm_console(vm_id):
    """Get noVNC console access."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    data = get(f"/vms/{vm_id}/console")
    print_item(data)


@click.command("network")
@click.argument("vm_id", required=False, default=None)
def vm_network(vm_id):
    """Get VM network info."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    data = get(f"/vms/{vm_id}/network")
    print_item(data)


@click.command("metrics")
@click.argument("vm_id", required=False, default=None)
@click.option("--hours", default=24, help="Hours of data (1-168, default: 24)")
def vm_metrics(vm_id, hours):
    """Get VM performance metrics."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    data = get(f"/vms/{vm_id}/metrics", params={"hours": hours})
    print_json(data)
