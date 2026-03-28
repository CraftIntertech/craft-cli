import click

from craft.client import delete, get, put
from craft.output import print_item, print_success


@click.command("get")
@click.argument("vm_id", required=False, default=None)
def rdns_get(vm_id):
    """Get reverse DNS record."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    data = get(f"/vms/{vm_id}/rdns")
    print_item(data)


@click.command("set")
@click.argument("vm_id", required=False, default=None)
@click.option("--hostname", default=None, help="FQDN (max 253 chars)")
def rdns_set(vm_id, hostname):
    """Set reverse DNS hostname."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    if not hostname:
        from craft.interactive import input_text
        hostname = input_text("Hostname (FQDN):")
    put(f"/vms/{vm_id}/rdns", {"hostname": hostname})
    print_success(f"rDNS set to {hostname}")


@click.command("delete")
@click.argument("vm_id", required=False, default=None)
def rdns_delete(vm_id):
    """Remove reverse DNS record."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    delete(f"/vms/{vm_id}/rdns")
    print_success("rDNS record removed.")
