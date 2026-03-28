"""Interactive prompts with arrow-key selection."""
import sys

import click

from craft.client import get


def _extract_list(data, *keys):
    """Extract list from API response, trying common patterns."""
    inner = data.get("data", data)
    if isinstance(inner, list):
        return inner
    if isinstance(inner, dict):
        for key in keys:
            if key in inner and isinstance(inner[key], list):
                return inner[key]
        for key in ("items", "data"):
            if key in inner and isinstance(inner[key], list):
                return inner[key]
    return [inner] if isinstance(inner, dict) else []


def _extract_obj(data):
    """Extract single object from API response."""
    inner = data.get("data", data)
    return inner if isinstance(inner, dict) else data


def _require_inquirer():
    try:
        from InquirerPy import inquirer  # noqa: F401
    except ImportError:
        click.echo("Error: Interactive mode requires InquirerPy.", err=True)
        click.echo("Install with: pip install InquirerPy", err=True)
        sys.exit(1)


def _fetch_node_hardware(node_id):
    """Fetch hardware info for a node, return display string."""
    try:
        data = get(f"/nodes/{node_id}/hardware")
        hw = _extract_obj(data)
        cpu_model = hw.get("cpuModel", "")
        # Shorten CPU model name
        cpu_short = cpu_model.split("@")[0].strip() if "@" in cpu_model else cpu_model
        cpu_short = cpu_short.replace("Intel(R) Xeon(R) ", "Xeon ").replace("CPU ", "")
        cores = hw.get("cpuCores", "?")
        mem_gb = hw.get("memTotalGb", 0)
        if isinstance(mem_gb, (int, float)):
            mem_gb = f"{mem_gb:.0f}"
        return f"{cpu_short} / {cores} cores / {mem_gb} GB RAM"
    except SystemExit:
        return None


def select_node(label="Select node"):
    """Fetch nodes and let user pick one. Shows hardware info after selection."""
    _require_inquirer()
    from InquirerPy import inquirer

    data = get("/nodes")
    nodes = _extract_list(data, "nodes")
    if not nodes:
        click.echo("Error: No nodes available.", err=True)
        sys.exit(1)

    choices = []
    for n in nodes:
        name = n.get("name", n.get("hostname", ""))
        location = n.get("location", "")
        country = n.get("country", "")
        loc_parts = [x for x in [location, country] if x]
        loc_str = ", ".join(loc_parts)
        display = f"{name} ({loc_str})" if loc_str else name
        choices.append({"name": display, "value": n.get("id", "")})

    node_id = inquirer.fuzzy(
        message=label,
        choices=choices,
    ).execute()

    # Show hardware info for selected node
    click.echo("  Loading node hardware info...")
    hw_info = _fetch_node_hardware(node_id)
    if hw_info:
        click.echo(click.style(f"  Hardware: {hw_info}", fg="cyan"))

    return node_id


def select_os_template(label="Select OS template"):
    """Fetch OS templates and let user pick one."""
    _require_inquirer()
    from InquirerPy import inquirer

    data = get("/os-templates")
    templates = _extract_list(data, "templates", "osTemplates")
    if not templates:
        click.echo("Error: No OS templates available.", err=True)
        sys.exit(1)

    choices = []
    for t in templates:
        name = t.get("name", t.get("label", ""))
        version = t.get("version", "")
        min_disk = t.get("minDiskGb", t.get("minDisk", ""))
        display = f"{name} {version}".strip()
        if min_disk:
            display += f" (min {min_disk} GB)"
        choices.append({"name": display, "value": t.get("id", "")})

    return inquirer.fuzzy(
        message=label,
        choices=choices,
    ).execute()


def select_plan(node_id=None, label="Select plan"):
    """Fetch plans and let user pick one. Returns (plan_id, plan_data) or ('__custom__', None)."""
    _require_inquirer()
    from InquirerPy import inquirer

    params = {"nodeId": node_id} if node_id else None
    data = get("/plans", params=params)
    plans = _extract_list(data, "plans")

    # Store plan data keyed by id for later reference
    plan_map = {}
    choices = [{"name": "Custom specs (set CPU/RAM/Disk manually)", "value": "__custom__"}]
    for p in plans:
        pid = p.get("id", "")
        name = p.get("name", "")
        cpu = p.get("cpu", "?")
        ram = p.get("ramMb", p.get("ram", "?"))
        disk = p.get("diskGb", p.get("disk", "?"))

        # Collect all pricing
        prices = []
        for key, lbl in [("priceDaily", "d"), ("priceWeekly", "w"),
                          ("priceMonthly", "mo"), ("priceYearly", "yr")]:
            val = p.get(key)
            if val is not None:
                prices.append(f"฿{val}/{lbl}")
        # Fallback to generic price
        if not prices:
            price = p.get("price", "")
            if price:
                prices.append(f"฿{price}/mo")

        display = f"{name} — {cpu} vCPU / {ram} MB / {disk} GB"
        if prices:
            display += f"  [{', '.join(prices)}]"
        choices.append({"name": display, "value": pid})
        plan_map[pid] = p

    selected = inquirer.fuzzy(
        message=label,
        choices=choices,
    ).execute()

    if selected == "__custom__":
        return "__custom__", None
    return selected, plan_map.get(selected)


def select_billing_type_with_price(plan_data=None, label="Billing type"):
    """Let user pick billing cycle with price shown per option."""
    _require_inquirer()
    from InquirerPy import inquirer

    billing_options = [
        ("daily", "Daily", "priceDaily"),
        ("weekly", "Weekly", "priceWeekly"),
        ("monthly", "Monthly", "priceMonthly"),
        ("yearly", "Yearly", "priceYearly"),
    ]

    choices = []
    for value, name, price_key in billing_options:
        display = name
        if plan_data:
            price = plan_data.get(price_key)
            if price is not None:
                display = f"{name:<10} ฿{price}"
            else:
                display = f"{name:<10} (not available)"
        choices.append({"name": display, "value": value})

    return inquirer.select(
        message=label,
        choices=choices,
        default="monthly",
    ).execute()


def input_custom_specs():
    """Prompt for custom CPU, RAM, disk."""
    _require_inquirer()
    from InquirerPy import inquirer

    cpu = int(inquirer.number(
        message="CPU cores (1-32):",
        min_allowed=1,
        max_allowed=32,
        default=1,
    ).execute())

    ram = int(inquirer.number(
        message="RAM in MB (512-131072):",
        min_allowed=512,
        max_allowed=131072,
        default=1024,
    ).execute())

    disk = int(inquirer.number(
        message="Disk in GB (10-2000):",
        min_allowed=10,
        max_allowed=2000,
        default=20,
    ).execute())

    return cpu, ram, disk


def select_vm(label="Select VM"):
    """Fetch user's VMs and let them pick one."""
    _require_inquirer()
    from InquirerPy import inquirer

    data = get("/vms", params={"page": 1, "limit": 50})
    vms = _extract_list(data, "vms", "items")
    if not vms:
        click.echo("Error: No VMs found.", err=True)
        sys.exit(1)

    choices = []
    for vm in vms:
        name = vm.get("name", "")
        status = vm.get("status", "")
        ip = vm.get("ip", vm.get("ipAddress", ""))
        display = f"{name} ({status})"
        if ip:
            display += f" — {ip}"
        choices.append({"name": display, "value": vm.get("id", "")})

    return inquirer.fuzzy(
        message=label,
        choices=choices,
    ).execute()


def select_ssh_keys(label="Select SSH keys"):
    """Fetch SSH keys and let user select multiple."""
    _require_inquirer()
    from InquirerPy import inquirer

    data = get("/ssh-keys")
    keys = _extract_list(data, "keys", "sshKeys")
    if not keys:
        return None

    choices = []
    for k in keys:
        name = k.get("name", "")
        fp = k.get("fingerprint", "")
        display = f"{name} ({fp})" if fp else name
        choices.append({"name": display, "value": k.get("id", ""), "enabled": False})

    result = inquirer.checkbox(
        message=label,
        choices=choices,
        instruction="(Space to select, Enter to confirm, skip with Enter)",
    ).execute()
    return ",".join(result) if result else None


def select_billing_type(label="Billing type"):
    """Let user pick a billing cycle (no pricing info)."""
    _require_inquirer()
    from InquirerPy import inquirer

    return inquirer.select(
        message=label,
        choices=[
            {"name": "Daily", "value": "daily"},
            {"name": "Weekly", "value": "weekly"},
            {"name": "Monthly", "value": "monthly"},
            {"name": "Yearly", "value": "yearly"},
        ],
        default="monthly",
    ).execute()


def select_hosting(label="Select hosting account"):
    """Fetch hosting accounts and let user pick one."""
    _require_inquirer()
    from InquirerPy import inquirer

    data = get("/hosting", params={"page": 1, "limit": 50})
    accounts = _extract_list(data, "items", "accounts")
    if not accounts:
        click.echo("Error: No hosting accounts found.", err=True)
        sys.exit(1)

    choices = []
    for h in accounts:
        name = h.get("name", "")
        domain = h.get("domain", "")
        status = h.get("status", "")
        display = f"{name} — {domain} ({status})"
        choices.append({"name": display, "value": h.get("id", "")})

    return inquirer.fuzzy(
        message=label,
        choices=choices,
    ).execute()


def select_hosting_node(label="Select hosting node"):
    """Fetch hosting nodes and let user pick one."""
    _require_inquirer()
    from InquirerPy import inquirer

    data = get("/hosting/nodes")
    nodes = _extract_list(data, "nodes")
    if not nodes:
        click.echo("Error: No hosting nodes available.", err=True)
        sys.exit(1)

    choices = []
    for n in nodes:
        name = n.get("name", n.get("hostname", ""))
        choices.append({"name": name, "value": n.get("id", "")})

    return inquirer.fuzzy(
        message=label,
        choices=choices,
    ).execute()


def select_hosting_plan(label="Select hosting plan"):
    """Fetch hosting plans and let user pick one."""
    _require_inquirer()
    from InquirerPy import inquirer

    data = get("/hosting/plans")
    plans = _extract_list(data, "plans")
    if not plans:
        click.echo("Error: No hosting plans available.", err=True)
        sys.exit(1)

    choices = []
    for p in plans:
        name = p.get("name", "")
        price = p.get("price", p.get("priceMonthly", ""))
        display = f"{name} (฿{price}/mo)" if price else name
        choices.append({"name": display, "value": p.get("id", "")})

    return inquirer.fuzzy(
        message=label,
        choices=choices,
    ).execute()


def select_snapshot(vm_id, label="Select snapshot"):
    """Fetch snapshots for a VM and let user pick one."""
    _require_inquirer()
    from InquirerPy import inquirer

    data = get(f"/vms/{vm_id}/snapshots")
    snaps = _extract_list(data, "snapshots", "items")
    if not snaps:
        click.echo("Error: No snapshots found.", err=True)
        sys.exit(1)

    choices = []
    for s in snaps:
        sid = s.get("id", s.get("name", ""))
        desc = s.get("description", "")
        created = s.get("createdAt", s.get("snaptime", ""))
        display = f"{sid}"
        if desc:
            display += f" — {desc}"
        if created:
            display += f" ({created})"
        choices.append({"name": display, "value": sid})

    return inquirer.fuzzy(
        message=label,
        choices=choices,
    ).execute()


def select_firewall_action():
    """Select firewall rule parameters interactively."""
    _require_inquirer()
    from InquirerPy import inquirer

    rule_type = inquirer.select(
        message="Direction",
        choices=[
            {"name": "Inbound (in)", "value": "in"},
            {"name": "Outbound (out)", "value": "out"},
        ],
    ).execute()

    action = inquirer.select(
        message="Action",
        choices=["ACCEPT", "DROP", "REJECT"],
    ).execute()

    proto = inquirer.select(
        message="Protocol",
        choices=[
            {"name": "TCP", "value": "tcp"},
            {"name": "UDP", "value": "udp"},
            {"name": "ICMP", "value": "icmp"},
            {"name": "Any (skip)", "value": ""},
        ],
    ).execute()

    dport = inquirer.text(
        message="Destination port (e.g. 80, 443, 8000:9000 — leave empty for any):",
    ).execute().strip()

    source = inquirer.text(
        message="Source CIDR (e.g. 0.0.0.0/0 — leave empty for any):",
    ).execute().strip()

    comment = inquirer.text(
        message="Comment (optional):",
    ).execute().strip()

    return {
        "type": rule_type,
        "action": action,
        "proto": proto or None,
        "dport": dport or None,
        "source": source or None,
        "comment": comment or None,
    }


def confirm(message, default=False):
    """Confirm prompt."""
    _require_inquirer()
    from InquirerPy import inquirer

    return inquirer.confirm(
        message=message,
        default=default,
    ).execute()


def input_text(message, default="", password=False):
    """Text input prompt."""
    _require_inquirer()
    from InquirerPy import inquirer

    if password:
        return inquirer.secret(message=message).execute()
    return inquirer.text(message=message, default=default).execute()
