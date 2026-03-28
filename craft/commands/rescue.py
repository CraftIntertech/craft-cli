import click

from craft.client import post
from craft.output import print_success


@click.command("enable")
@click.argument("vm_id")
def rescue_enable(vm_id):
    """Enable rescue mode (boots on next start)."""
    post(f"/vms/{vm_id}/rescue/enable")
    print_success("Rescue mode enabled. Start/reboot to enter rescue OS.")


@click.command("disable")
@click.argument("vm_id")
def rescue_disable(vm_id):
    """Disable rescue mode."""
    post(f"/vms/{vm_id}/rescue/disable")
    print_success("Rescue mode disabled. VM will boot normally.")
