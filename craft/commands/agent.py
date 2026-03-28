import click

from craft.client import get, post
from craft.output import print_item, print_success


@click.command("enable")
@click.argument("vm_id")
def agent_enable(vm_id):
    """Enable QEMU Guest Agent. Reboot VM afterwards."""
    post(f"/vms/{vm_id}/agent/enable")
    print_success("Guest agent enabled. Reboot VM to activate.")


@click.command("info")
@click.argument("vm_id")
def agent_info(vm_id):
    """Get guest agent info (hostname, OS, network, etc.)."""
    data = get(f"/vms/{vm_id}/agent/info")
    print_item(data)


@click.command("fstrim")
@click.argument("vm_id")
def agent_fstrim(vm_id):
    """Trigger filesystem TRIM."""
    post(f"/vms/{vm_id}/agent/fstrim")
    print_success("FS TRIM completed.")
