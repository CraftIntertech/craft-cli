import click

from craft.client import delete, get, put
from craft.output import print_item, print_success


@click.command("get")
@click.argument("vm_id")
def rdns_get(vm_id):
    """Get reverse DNS record."""
    data = get(f"/vms/{vm_id}/rdns")
    print_item(data)


@click.command("set")
@click.argument("vm_id")
@click.option("--hostname", required=True, help="FQDN (max 253 chars)")
def rdns_set(vm_id, hostname):
    """Set reverse DNS hostname."""
    put(f"/vms/{vm_id}/rdns", {"hostname": hostname})
    print_success(f"rDNS set to {hostname}")


@click.command("delete")
@click.argument("vm_id")
def rdns_delete(vm_id):
    """Remove reverse DNS record."""
    delete(f"/vms/{vm_id}/rdns")
    print_success("rDNS record removed.")
