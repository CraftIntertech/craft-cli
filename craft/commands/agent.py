import click

from craft.client import get, post
from craft.output import print_item, print_success


@click.command("enable")
@click.argument("vm_id", required=False, default=None)
def agent_enable(vm_id):
    """Enable QEMU Guest Agent. Reboot VM afterwards."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    post(f"/vms/{vm_id}/agent/enable")
    print_success("Guest agent enabled. Reboot VM to activate.")


@click.command("info")
@click.argument("vm_id", required=False, default=None)
def agent_info(vm_id):
    """Get guest agent info (hostname, OS, network, etc.)."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    data = get(f"/vms/{vm_id}/agent/info")
    print_item(data)


@click.command("fstrim")
@click.argument("vm_id", required=False, default=None)
def agent_fstrim(vm_id):
    """Trigger filesystem TRIM."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    post(f"/vms/{vm_id}/agent/fstrim")
    print_success("FS TRIM completed.")
