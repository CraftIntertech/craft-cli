import click

from craft.client import get, patch, post
from craft.output import print_item, print_success


@click.command("show")
@click.argument("vm_id")
def billing_show(vm_id):
    """Get VM billing status."""
    data = get(f"/vms/{vm_id}/billing")
    print_item(data)


@click.command("renew")
@click.argument("vm_id")
@click.option("--billing-type", required=True, type=click.Choice(["daily", "weekly", "monthly", "yearly"]))
def billing_renew(vm_id, billing_type):
    """Renew VM for another period."""
    data = post(f"/vms/{vm_id}/renew", {"billingType": billing_type})
    print_success("VM renewed.")
    print_item(data)


@click.command("auto-renew")
@click.argument("vm_id")
@click.option("--enable/--disable", required=True, help="Enable or disable auto-renew")
def billing_auto_renew(vm_id, enable):
    """Toggle VM auto-renewal."""
    patch(f"/vms/{vm_id}/auto-renew", {"autoRenew": enable})
    state = "enabled" if enable else "disabled"
    print_success(f"Auto-renew {state}.")
