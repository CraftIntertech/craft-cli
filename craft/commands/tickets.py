import click

from craft.client import get, patch, post
from craft.output import print_item, print_json, print_success, print_table


def _select_ticket(label="Select ticket"):
    """Fetch tickets and let user pick one."""
    from craft.interactive import _require_inquirer, _extract_list
    _require_inquirer()
    from InquirerPy import inquirer

    data = get("/tickets")
    items = _extract_list(data, "tickets")
    if not items:
        click.echo("No tickets found.", err=True)
        raise SystemExit(1)

    choices = []
    for t in items:
        tid = t.get("id", "")
        subject = t.get("subject", "")
        status = t.get("status", "")
        choices.append({"name": f"[{status}] {subject}  ({tid[:8]}...)", "value": tid})

    return inquirer.fuzzy(message=label, choices=choices).execute()


def _print_ticket_detail(data):
    """Print ticket info with formatted message thread."""
    obj = data.get("data", data) if isinstance(data, dict) else data
    if not isinstance(obj, dict):
        print_json(data)
        return

    # Print ticket header
    click.echo(click.style("── Ticket ──", fg="cyan", bold=True))
    click.echo()

    status = obj.get("status", "")
    status_colors = {"open": "green", "pending": "yellow", "closed": "red"}
    status_styled = click.style(status, fg=status_colors.get(status, None))

    priority = obj.get("priority", "")
    prio_colors = {"urgent": "red", "high": "yellow", "medium": "cyan", "low": "green"}
    prio_styled = click.style(priority, fg=prio_colors.get(priority, None)) if priority else "-"

    fields = [
        ("ID", obj.get("id", "")),
        ("Subject", obj.get("subject", "")),
        ("Status", status_styled),
        ("Priority", prio_styled),
        ("Created", obj.get("createdAt", "")),
        ("Updated", obj.get("updatedAt", "")),
    ]
    if obj.get("closedAt"):
        fields.append(("Closed", obj.get("closedAt")))
    if obj.get("vmId"):
        fields.append(("VM ID", obj.get("vmId")))

    max_label = max(len(f[0]) for f in fields)
    for label, val in fields:
        click.echo(f"  {label:<{max_label}}  {val}")

    # Print messages
    messages = obj.get("messages", [])
    if isinstance(messages, list) and messages:
        click.echo()
        click.echo(click.style(f"── Messages ({len(messages)}) ──", fg="cyan", bold=True))
        click.echo()

        for msg in messages:
            author = msg.get("authorName", "Unknown")
            is_staff = msg.get("isStaff", False)
            body = msg.get("body", "")
            created = msg.get("createdAt", "")

            # Format timestamp (show date + time only)
            if "T" in created:
                created = created.replace("T", " ").split(".")[0]

            if is_staff:
                tag = click.style("[Staff]", fg="yellow", bold=True)
            else:
                tag = click.style("[You]", fg="cyan")

            click.echo(f"  {tag} {author}  {click.style(created, dim=True)}")
            # Indent message body
            for line in body.split("\n"):
                click.echo(f"    {line}")
            click.echo()


@click.command("list")
def ticket_list():
    """List support tickets."""
    data = get("/tickets")
    items = data.get("data", data)
    if isinstance(items, dict):
        items = items.get("items", items.get("tickets", []))
    if isinstance(items, list) and items:
        rows = []
        for t in items:
            rows.append([
                t.get("id", ""),
                t.get("subject", ""),
                t.get("status", ""),
                t.get("createdAt", ""),
            ])
        print_table(rows, ["ID", "Subject", "Status", "Created"])
    else:
        print_item(data)


@click.command("get")
@click.argument("ticket_id", required=False, default=None)
def ticket_get(ticket_id):
    """Get ticket with message history.

    \b
    If TICKET_ID is omitted, select from a list interactively.
    """
    if not ticket_id:
        ticket_id = _select_ticket()
    data = get(f"/tickets/{ticket_id}")
    _print_ticket_detail(data)


@click.command("create")
@click.option("--subject", default=None, help="Subject (1-255 chars)")
@click.option("--body", "body_text", default=None, help="Message (1-10,000 chars)")
@click.option("--vm-id", default=None, help="Link to a VM (optional)")
def ticket_create(subject, body_text, vm_id):
    """Create a support ticket.

    \b
    If --subject or --body is omitted, you will be prompted interactively.

    \b
    Examples:
      craft ticket create --subject "Help" --body "Details..."
      craft ticket create                    # Interactive prompts
    """
    if not subject:
        subject = click.prompt("Subject")
    if not body_text:
        body_text = click.prompt("Message")
    body = {"subject": subject, "body": body_text}
    if vm_id:
        body["vmId"] = vm_id
    data = post("/tickets", body)
    print_success("Ticket created.")
    print_item(data)


@click.command("reply")
@click.argument("ticket_id", required=False, default=None)
@click.option("--body", "body_text", default=None, help="Reply message")
def ticket_reply(ticket_id, body_text):
    """Reply to a ticket.

    \b
    If TICKET_ID is omitted, select from a list interactively.
    """
    if not ticket_id:
        ticket_id = _select_ticket("Select ticket to reply")
    if not body_text:
        body_text = click.prompt("Message")
    post(f"/tickets/{ticket_id}/messages", {"body": body_text})
    print_success("Reply sent.")


@click.command("close")
@click.argument("ticket_id", required=False, default=None)
def ticket_close(ticket_id):
    """Close a ticket.

    \b
    If TICKET_ID is omitted, select from a list interactively.
    """
    if not ticket_id:
        ticket_id = _select_ticket("Select ticket to close")
    if not click.confirm(f"Close ticket {ticket_id[:8]}...?"):
        click.echo("Cancelled.")
        return
    patch(f"/tickets/{ticket_id}/close")
    print_success(f"Ticket {ticket_id[:8]}... closed.")
