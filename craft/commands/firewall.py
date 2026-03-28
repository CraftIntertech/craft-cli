import click

from craft.client import delete, get, post, put
from craft.output import print_item, print_json, print_success, print_table


@click.command("list")
@click.argument("vm_id", required=False, default=None)
def fw_list(vm_id):
    """List firewall rules for a VM."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    data = get(f"/vms/{vm_id}/firewall")
    inner = data.get("data", data)
    rules = inner.get("rules", inner) if isinstance(inner, dict) else inner
    if isinstance(rules, list) and rules:
        rows = []
        for i, r in enumerate(rules):
            rows.append([
                i,
                r.get("type", ""),
                r.get("action", ""),
                r.get("proto", "*"),
                r.get("dport", "*"),
                r.get("source", "*"),
                r.get("enable", 1),
                r.get("comment", ""),
            ])
        print_table(rows, ["#", "Type", "Action", "Proto", "DPort", "Source", "Enabled", "Comment"])
    else:
        print_json(data)


@click.command("add")
@click.argument("vm_id", required=False, default=None)
@click.option("--type", "rule_type", default=None, type=click.Choice(["in", "out"]))
@click.option("--action", default=None, type=click.Choice(["ACCEPT", "DROP", "REJECT"]))
@click.option("--proto", default=None, type=click.Choice(["tcp", "udp", "icmp"]))
@click.option("--dport", default=None, help="Destination port (e.g. 80 or 8000:9000)")
@click.option("--sport", default=None, help="Source port")
@click.option("--source", default=None, help="Source CIDR (e.g. 10.0.0.0/8)")
@click.option("--dest", default=None, help="Destination CIDR")
@click.option("--comment", default=None, help="Comment (max 255 chars)")
@click.option("--enable/--disable", default=True, help="Enable rule (default: enabled)")
def fw_add(vm_id, rule_type, action, proto, dport, sport, source, dest, comment, enable):
    """Add a firewall rule."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()

    # Interactive mode if required fields missing
    if not rule_type or not action:
        from craft.interactive import select_firewall_action
        fw = select_firewall_action()
        rule_type = rule_type or fw["type"]
        action = action or fw["action"]
        proto = proto or fw.get("proto")
        dport = dport or fw.get("dport")
        source = source or fw.get("source")
        comment = comment or fw.get("comment")

    body = {"type": rule_type, "action": action, "enable": 1 if enable else 0}
    if proto:
        body["proto"] = proto
    if dport:
        body["dport"] = dport
    if sport:
        body["sport"] = sport
    if source:
        body["source"] = source
    if dest:
        body["dest"] = dest
    if comment:
        body["comment"] = comment

    data = post(f"/vms/{vm_id}/firewall", body)
    print_success("Firewall rule added.")
    print_item(data)


@click.command("delete")
@click.argument("vm_id", required=False, default=None)
@click.argument("position", required=False, default=None, type=int)
def fw_delete(vm_id, position):
    """Delete a firewall rule by position (0-based)."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    if position is None:
        position = click.prompt("Rule position (0-based)", type=int)
    delete(f"/vms/{vm_id}/firewall/{position}")
    print_success(f"Firewall rule {position} deleted.")


@click.command("options")
@click.argument("vm_id", required=False, default=None)
@click.option("--enable/--disable", default=None, help="Enable or disable firewall")
@click.option("--policy-in", type=click.Choice(["ACCEPT", "DROP", "REJECT"]), default=None)
@click.option("--policy-out", type=click.Choice(["ACCEPT", "DROP", "REJECT"]), default=None)
def fw_options(vm_id, enable, policy_in, policy_out):
    """Update firewall options."""
    if not vm_id:
        from craft.interactive import select_vm
        vm_id = select_vm()
    body = {}
    if enable is not None:
        body["enable"] = 1 if enable else 0
    if policy_in:
        body["policy_in"] = policy_in
    if policy_out:
        body["policy_out"] = policy_out

    if not body:
        click.echo("No options to update. Use --help.")
        return

    put(f"/vms/{vm_id}/firewall/options", body)
    print_success("Firewall options updated.")
