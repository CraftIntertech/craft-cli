import click

from craft.client import get, patch, post
from craft.output import print_item, print_success


@click.command("show")
@click.argument("vm_id", required=False, default=None)
def billing_show(vm_id):
    """Get VM billing status."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    data = get(f"/vms/{vm_id}/billing")
    print_item(data)


@click.command("renew")
@click.argument("vm_id", required=False, default=None)
@click.option("--billing-type", default=None, type=click.Choice(["daily", "weekly", "monthly", "yearly"]))
def billing_renew(vm_id, billing_type):
    """Renew VM for another period."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    if not billing_type:
        from craft.interactive import select_billing_type
        billing_type = select_billing_type()
    data = post(f"/vms/{vm_id}/renew", {"billingType": billing_type})
    print_success("VM renewed.")
    print_item(data)


@click.command("auto-renew")
@click.argument("vm_id", required=False, default=None)
@click.option("--enable/--disable", default=None, help="Enable or disable auto-renew")
def billing_auto_renew(vm_id, enable):
    """Toggle VM auto-renewal."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    if enable is None:
        from craft.interactive import confirm
        enable = confirm("Enable auto-renew?")
    patch(f"/vms/{vm_id}/auto-renew", {"autoRenew": enable})
    state = "enabled" if enable else "disabled"
    print_success(f"Auto-renew {state}.")
